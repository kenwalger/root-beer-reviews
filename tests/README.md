# Test Suite

This directory contains the comprehensive test suite for the Root Beer Review App.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures and test configuration
├── test_auth.py         # Authentication tests (unit + integration)
├── test_utils.py        # Utility function tests (unit)
├── test_models.py       # Pydantic model validation tests (unit)
├── test_admin_routes.py # Admin route tests (integration)
└── test_public_routes.py # Public route tests (integration)
```

## Running Tests

### Install Test Dependencies

```bash
uv sync --extra test
# or
uv pip install -e ".[test]"
```

### Run All Tests

```bash
uv run pytest
# or
pytest
```

### Run Specific Test Categories

```bash
# Unit tests only
uv run pytest -m unit

# Integration tests only
uv run pytest -m integration

# Authentication tests
uv run pytest -m auth

# Admin route tests
uv run pytest -m admin

# Public route tests
uv run pytest -m public
```

### Run Specific Test Files

```bash
# Run only authentication tests
uv run pytest tests/test_auth.py

# Run only model tests
uv run pytest tests/test_models.py
```

### Run with Coverage

```bash
uv run pytest --cov=app --cov-report=html --cov-report=term
```

This will:
- Generate a coverage report in the terminal
- Create an HTML coverage report in `htmlcov/` directory
- Open `htmlcov/index.html` in a browser to see detailed coverage

### Verbose Output

```bash
uv run pytest -v
```

## Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit` - Unit tests (no database/external services)
- `@pytest.mark.integration` - Integration tests (require database)
- `@pytest.mark.auth` - Authentication-related tests
- `@pytest.mark.admin` - Admin route tests
- `@pytest.mark.public` - Public route tests

## Test Fixtures

### Database Fixtures

- `test_db` - Sets up and tears down a test MongoDB database
- `test_settings` - Test configuration settings

### Authentication Fixtures

- `admin_user` - Creates a test admin user in the database
- `authenticated_client` - Test client with authenticated session

### Data Fixtures

- `sample_rootbeer_data` - Sample root beer data dictionary
- `sample_rootbeer` - Creates a root beer in test database
- `sample_review_data` - Sample review data dictionary
- `sample_review` - Creates a review in test database

### Mock Fixtures

- `mock_s3_client` - Mock S3 client for image upload tests

## Test Database

Tests use a separate test database (`rootbeer_reviews_test` by default) that is:
- Created automatically before each test
- Cleared (not dropped) after each test for better performance
- Isolated from the development/production database

### Using MongoDB Atlas for Testing

**Tests automatically use the same MongoDB connection as your application** (from `MONGODB_URI` in your `.env` file), but connect to a separate test database. This means:

- ✅ **MongoDB Atlas**: If you're using MongoDB Atlas, tests will use the same Atlas cluster but a different database name (`rootbeer_reviews_test`)
- ✅ **Local MongoDB**: If you have local MongoDB running, tests will use that
- ⚠️ **No MongoDB**: Tests will skip if `MONGODB_URI` is not set and local MongoDB is not available

**Recommended Setup:**
1. Use the same `MONGODB_URI` from your `.env` file (your Atlas connection string)
2. Tests will automatically use a separate database (`rootbeer_reviews_test` by default)
3. Override the test database name by setting `TEST_DATABASE_NAME` environment variable if needed
4. The test database is cleared between test runs, so it's safe to use your production Atlas cluster

**Example `.env` for testing with Atlas:**
```env
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/rootbeer_reviews?retryWrites=true&w=majority
DATABASE_NAME=rootbeer_reviews
TEST_DATABASE_NAME=rootbeer_reviews_test  # Optional: override test database name
SECRET_KEY=your-secret-key
```

**Note**: The test database is automatically cleared between test runs, so your production data in `rootbeer_reviews` is never affected.

## Writing New Tests

### Unit Test Example

```python
@pytest.mark.unit
def test_my_function():
    """Test description."""
    result = my_function(input)
    assert result == expected
```

### Integration Test Example

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_my_route(test_db: None, authenticated_client: TestClient):
    """Test description."""
    response = authenticated_client.get("/my/route")
    assert response.status_code == 200
```

### Using Fixtures

```python
def test_with_fixture(sample_rootbeer: dict):
    """Test using a fixture."""
    assert sample_rootbeer["name"] == "Test Root Beer"
```

## Continuous Integration

Tests are designed to run in CI/CD pipelines. Make sure to:

1. Set `MONGODB_URI` environment variable
2. Install test dependencies: `uv sync --extra test`
3. Run tests: `pytest`

## Coverage Goals

- Target: 70%+ code coverage
- Focus areas:
  - All route handlers
  - Authentication logic
  - Utility functions
  - Model validation
  - Error handling

## Troubleshooting

### Tests Fail with Database Connection Error

- Ensure `MONGODB_URI` environment variable is set in your `.env` file
- For MongoDB Atlas: Verify your connection string is correct and your IP is whitelisted
- For local MongoDB: Ensure MongoDB is running (`mongod` or `brew services start mongodb-community`)
- Verify network connectivity to MongoDB instance
- Check that the test database name doesn't conflict with your production database

### Tests Fail with Import Errors

- Ensure test dependencies are installed: `uv sync --extra test`
- Verify you're running tests from the project root directory

### Async Test Warnings

- All async tests should use `@pytest.mark.asyncio`
- Ensure `pytest-asyncio` is installed

