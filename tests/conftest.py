"""Pytest configuration and shared fixtures.

This module provides fixtures for testing the Root Beer Review App,
including test database setup, FastAPI test client, and authentication helpers.
"""
import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient
from typing import AsyncGenerator, Generator
import os
from unittest.mock import Mock, patch
from dotenv import load_dotenv

# Load .env file before tests run
load_dotenv()

from app.main import app
from app.database import db, get_database
from app.config import Settings


# Test database configuration
# Uses the same MongoDB connection (Atlas or local) but a separate test database
# Set TEST_DATABASE_NAME environment variable to override, or it defaults to "rootbeer_reviews_test"
def get_test_database_name() -> str:
    """Get test database name from environment or use default.
    
    :returns: Test database name
    :rtype: str
    """
    return os.environ.get("TEST_DATABASE_NAME", "rootbeer_reviews_test")


@pytest.fixture(scope="function")
def test_settings() -> Settings:
    """Create test settings with test database.
    
    :returns: Settings instance configured for testing
    :rtype: Settings
    """
    # Use test database
    original_db_name = os.environ.get("DATABASE_NAME", "rootbeer_reviews")
    os.environ["DATABASE_NAME"] = get_test_database_name()
    
    # Create test settings
    settings = Settings(
        mongodb_uri=os.environ.get("MONGODB_URI", "mongodb://localhost:27017"),
        database_name=get_test_database_name(),
        secret_key=os.environ.get("SECRET_KEY", "test-secret-key-for-testing-only"),
        algorithm="HS256",
        environment="test",
    )
    
    yield settings
    
    # Restore original
    os.environ["DATABASE_NAME"] = original_db_name


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[None, None]:
    """Set up and tear down test database.
    
    Creates a test database connection and cleans up after each test.
    Uses the same MongoDB connection string as the application (from MONGODB_URI env var),
    but connects to a separate test database to avoid affecting production data.
    Uses collection clearing instead of database dropping for better performance.
    
    Note: Motor clients are event-loop bound, so we create the client in the same
    event loop that will be used by all async fixtures in the test.
    
    :yields: None
    :rtype: AsyncGenerator[None, None]
    """
    # Get MongoDB URI from environment (should be set in .env file)
    # Falls back to localhost only if not set (for local development)
    mongodb_uri = os.environ.get("MONGODB_URI")
    if not mongodb_uri:
        mongodb_uri = "mongodb://localhost:27017"
        pytest.skip(
            "MONGODB_URI not set. Set it in your .env file to use MongoDB Atlas for testing, "
            "or start a local MongoDB instance."
        )
    
    # Store original database reference
    original_db = db.database
    original_client = db.client
    
    # Connect to test database using the same connection string but different database name
    # IMPORTANT: Create client in the current event loop (pytest-asyncio manages this)
    # Motor clients are event-loop bound, so we must create them in the same loop that will use them
    # In newer Motor versions, the client automatically uses the current event loop
    test_client = AsyncIOMotorClient(
        mongodb_uri,
        serverSelectionTimeoutMS=5000,  # Fail fast if MongoDB unavailable
    )
    test_database = test_client[get_test_database_name()]
    
    # Replace with test database
    db.client = test_client
    db.database = test_database
    
    # Verify connection by pinging the database
    try:
        await test_client.admin.command('ping')
    except Exception as e:
        pytest.skip(f"Could not connect to MongoDB: {e}")
    
    yield
    
    # Clean up: clear all collections (faster than dropping database)
    collections_to_clear = [
        "rootbeers",
        "reviews",
        "flavor_notes",
        "admin_users",
        "colors",
        "serving_contexts",
    ]
    for collection_name in collections_to_clear:
        try:
            await test_database[collection_name].delete_many({})
        except Exception:
            pass  # Collection might not exist, ignore
    
    # Close test client
    test_client.close()
    
    # Restore original database reference
    db.database = original_db
    db.client = original_client


@pytest_asyncio.fixture(scope="function")
async def async_client(test_db: None) -> AsyncGenerator[AsyncClient, None]:
    """Create async FastAPI test client.
    
    Uses httpx.AsyncClient which works properly with pytest-asyncio's event loop.
    The database is set up by test_db before this fixture runs.
    We patch the lifespan functions to prevent them from overwriting the test database.
    
    :param test_db: Test database fixture (ensures database is set up)
    :type test_db: None
    :yields: Async FastAPI test client
    :rtype: AsyncGenerator[AsyncClient, None]
    """
    # Patch lifespan functions to no-ops since test_db already sets up the database
    from app.database import connect_to_mongo, close_mongo_connection
    from app.auth import initialize_admin_user
    from app.seed_data import seed_default_data
    from unittest.mock import patch
    
    async def noop():
        pass
    
    with patch('app.database.connect_to_mongo', noop), \
         patch('app.database.close_mongo_connection', noop), \
         patch('app.auth.initialize_admin_user', noop), \
         patch('app.seed_data.seed_default_data', noop):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client


@pytest_asyncio.fixture(scope="function")
async def client(test_db: None) -> AsyncGenerator[AsyncClient, None]:
    """Create async FastAPI test client.
    
    Uses httpx.AsyncClient which works properly with pytest-asyncio's event loop.
    This ensures the Motor client created in test_db is in the same event loop.
    The database is set up by test_db before this fixture runs.
    We patch the lifespan functions to prevent them from overwriting the test database.
    
    :param test_db: Test database fixture (ensures database is set up)
    :type test_db: None
    :yields: Async FastAPI test client
    :rtype: AsyncGenerator[AsyncClient, None]
    """
    # Patch lifespan functions to no-ops since test_db already sets up the database
    from app.database import connect_to_mongo, close_mongo_connection
    from app.auth import initialize_admin_user
    from app.seed_data import seed_default_data
    from unittest.mock import patch
    
    async def noop():
        pass
    
    with patch('app.database.connect_to_mongo', noop), \
         patch('app.database.close_mongo_connection', noop), \
         patch('app.auth.initialize_admin_user', noop), \
         patch('app.seed_data.seed_default_data', noop):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client


@pytest_asyncio.fixture
async def admin_user(test_db: None) -> AsyncGenerator[dict[str, str], None]:
    """Create a test admin user in the database.
    
    :param test_db: Test database fixture
    :type test_db: None
    :returns: Dictionary with admin user email and password
    :rtype: dict[str, str]
    """
    from app.auth import get_password_hash
    from datetime import datetime, UTC
    
    database = get_database()
    if database is None:
        pytest.skip("Database not available")
    
    admin_email = "test@example.com"
    admin_password = "testpassword123"
    
    admin_user = {
        "email": admin_email,
        "hashed_password": get_password_hash(admin_password),
        "is_active": True,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "created_by": "test",
        "updated_by": "test",
    }
    
    await database.admin_users.insert_one(admin_user)
    
    yield {"email": admin_email, "password": admin_password}
    
    # Cleanup
    await database.admin_users.delete_one({"email": admin_email})


@pytest_asyncio.fixture
async def authenticated_client(test_db: None, client: AsyncClient, admin_user: dict[str, str]) -> AsyncClient:
    """Create an authenticated test client.
    
    :param test_db: Test database fixture (ensures database is set up)
    :type test_db: None
    :param client: FastAPI test client
    :type client: AsyncClient
    :param admin_user: Test admin user fixture
    :type admin_user: dict[str, str]
    :returns: Authenticated test client
    :rtype: AsyncClient
    """
    # Login to get authentication cookie
    response = await client.post(
        "/admin/login",
        data={
            "email": admin_user["email"],
            "password": admin_user["password"],
        },
        follow_redirects=False,
    )
    
    # Check if login was successful (should redirect or return 200)
    assert response.status_code in [200, 303, 307], f"Login failed: {response.status_code}"
    
    return client


@pytest.fixture
def mock_s3_client():
    """Mock S3 client for testing image uploads.
    
    :yields: Mock S3 client
    :rtype: Generator[Mock, None, None]
    """
    with patch("app.utils.images.s3_client") as mock_client:
        # Mock S3 operations
        mock_client.put_object = Mock()
        mock_client.delete_object = Mock()
        yield mock_client


@pytest.fixture
def sample_rootbeer_data() -> dict:
    """Sample root beer data for testing.
    
    :returns: Dictionary with sample root beer data
    :rtype: dict
    """
    return {
        "name": "Test Root Beer",
        "brand": "Test Brand",
        "region": "Test Region",
        "country": "USA",
        "ingredients": "Water, sugar, natural flavors",
        "sweetener_type": "cane sugar",
        "sugar_grams_per_serving": 40.0,
        "caffeine_mg": 0.0,
        "alcohol_content": 0.0,
        "color": "Brown",
        "carbonation_level": "medium",
        "estimated_co2_volumes": 2.5,
        "notes": "A test root beer",
    }


@pytest_asyncio.fixture
async def sample_rootbeer(test_db: None, sample_rootbeer_data: dict) -> AsyncGenerator[dict, None]:
    """Create a sample root beer in the test database.
    
    :param test_db: Test database fixture
    :type test_db: None
    :param sample_rootbeer_data: Sample root beer data
    :type sample_rootbeer_data: dict
    :returns: Created root beer document with _id
    :rtype: dict
    """
    from datetime import datetime, UTC
    
    database = get_database()
    if database is None:
        pytest.skip("Database not available")
    
    rootbeer = {
        **sample_rootbeer_data,
        "images": [],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "created_by": "test",
        "updated_by": "test",
    }
    
    result = await database.rootbeers.insert_one(rootbeer)
    rootbeer["_id"] = result.inserted_id
    
    yield rootbeer
    
    # Cleanup
    await database.rootbeers.delete_one({"_id": result.inserted_id})


@pytest.fixture
def sample_review_data(sample_rootbeer: dict) -> dict:
    """Sample review data for testing.
    
    :param sample_rootbeer: Sample root beer fixture
    :type sample_rootbeer: dict
    :returns: Dictionary with sample review data
    :rtype: dict
    """
    return {
        "root_beer_id": str(sample_rootbeer["_id"]),
        "sweetness": 3,
        "carbonation_bite": 4,
        "creaminess": 2,
        "acidity": 3,
        "aftertaste_length": 4,
        "overall_score": 7,
        "would_drink_again": True,
        "uniqueness_score": 6,
        "tasting_notes": "A good test root beer",
        "flavor_notes": [],
    }


@pytest_asyncio.fixture
async def sample_review(test_db: None, sample_review_data: dict) -> AsyncGenerator[dict, None]:
    """Create a sample review in the test database.
    
    :param test_db: Test database fixture
    :type test_db: None
    :param sample_review_data: Sample review data
    :type sample_review_data: dict
    :yields: Created review document with _id
    :rtype: AsyncGenerator[dict, None]
    """
    from datetime import datetime, UTC
    
    database = get_database()
    if database is None:
        pytest.skip("Database not available")
    
    review = {
        **sample_review_data,
        "review_date": datetime.now(UTC),
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "created_by": "test",
        "updated_by": "test",
    }
    
    result = await database.reviews.insert_one(review)
    review["_id"] = result.inserted_id
    
    yield review
    
    # Cleanup (not strictly necessary since test_db clears collections, but good practice)
    try:
        await database.reviews.delete_one({"_id": result.inserted_id})
    except Exception:
        pass

