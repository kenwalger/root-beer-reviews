"""Tests for Pydantic models."""
import pytest
from datetime import datetime
from pydantic import ValidationError

from app.models.rootbeer import RootBeerCreate, RootBeerUpdate, RootBeer
from app.models.review import ReviewCreate, ReviewUpdate, Review
from app.models.flavor_note import FlavorNoteCreate, FlavorNote
from app.models.admin_user import AdminUserCreate, AdminUser


@pytest.mark.unit
class TestRootBeerModels:
    """Tests for root beer models."""
    
    def test_rootbeer_create_valid(self):
        """Test creating a valid root beer."""
        rootbeer = RootBeerCreate(
            name="Test Root Beer",
            brand="Test Brand",
            region="Test Region",
            country="USA",
        )
        
        assert rootbeer.name == "Test Root Beer"
        assert rootbeer.brand == "Test Brand"
        assert rootbeer.region == "Test Region"
        assert rootbeer.country == "USA"
    
    def test_rootbeer_create_missing_required(self):
        """Test that required fields are enforced."""
        with pytest.raises(ValidationError):
            RootBeerCreate(brand="Test Brand")  # Missing name
    
    def test_rootbeer_create_optional_fields(self):
        """Test that optional fields work correctly."""
        rootbeer = RootBeerCreate(
            name="Test",
            brand="Test Brand",
            sugar_grams_per_serving=40.0,
            caffeine_mg=0.0,
        )
        
        assert rootbeer.sugar_grams_per_serving == 40.0
        assert rootbeer.caffeine_mg == 0.0
    
    def test_rootbeer_update_all_optional(self):
        """Test that update model allows all fields to be optional."""
        update = RootBeerUpdate()
        
        # Should not raise validation error
        assert update.name is None
    
    def test_rootbeer_update_partial(self):
        """Test partial update with only some fields."""
        update = RootBeerUpdate(name="Updated Name")
        
        assert update.name == "Updated Name"
        assert update.brand is None


@pytest.mark.unit
class TestReviewModels:
    """Tests for review models."""
    
    def test_review_create_valid(self):
        """Test creating a valid review."""
        review = ReviewCreate(
            root_beer_id="test_id",
            sweetness=3,
            carbonation_bite=4,
            creaminess=2,
            acidity=3,
            aftertaste_length=4,
            overall_score=7,
        )
        
        assert review.sweetness == 3
        assert review.overall_score == 7
        assert review.would_drink_again is True  # Default value
    
    def test_review_create_missing_required(self):
        """Test that required fields are enforced."""
        with pytest.raises(ValidationError):
            ReviewCreate(
                root_beer_id="test_id",
                sweetness=3,
                # Missing other required fields
            )
    
    def test_review_create_rating_bounds(self):
        """Test that ratings are within valid bounds."""
        # Test lower bound
        with pytest.raises(ValidationError):
            ReviewCreate(
                root_beer_id="test_id",
                sweetness=0,  # Below minimum
                carbonation_bite=4,
                creaminess=2,
                acidity=3,
                aftertaste_length=4,
                overall_score=7,
            )
        
        # Test upper bound
        with pytest.raises(ValidationError):
            ReviewCreate(
                root_beer_id="test_id",
                sweetness=6,  # Above maximum
                carbonation_bite=4,
                creaminess=2,
                acidity=3,
                aftertaste_length=4,
                overall_score=7,
            )
    
    def test_review_create_flavor_notes(self):
        """Test flavor notes list handling."""
        review = ReviewCreate(
            root_beer_id="test_id",
            sweetness=3,
            carbonation_bite=4,
            creaminess=2,
            acidity=3,
            aftertaste_length=4,
            overall_score=7,
            flavor_notes=["note1", "note2"],
        )
        
        assert len(review.flavor_notes) == 2
        assert "note1" in review.flavor_notes
    
    def test_review_update_partial(self):
        """Test partial review update."""
        update = ReviewUpdate(overall_score=8)
        
        assert update.overall_score == 8
        assert update.sweetness is None


@pytest.mark.unit
class TestFlavorNoteModels:
    """Tests for flavor note models."""
    
    def test_flavor_note_create_valid(self):
        """Test creating a valid flavor note."""
        note = FlavorNoteCreate(
            name="Vanilla",
            category="Sweet & Creamy",
        )
        
        assert note.name == "Vanilla"
        assert note.category == "Sweet & Creamy"
    
    def test_flavor_note_create_missing_required(self):
        """Test that required fields are enforced."""
        with pytest.raises(ValidationError):
            FlavorNoteCreate(category="Sweet")  # Missing name
    
    def test_flavor_note_create_optional_category(self):
        """Test that category is optional."""
        note = FlavorNoteCreate(name="Vanilla")
        
        assert note.name == "Vanilla"
        assert note.category is None


@pytest.mark.unit
class TestAdminUserModels:
    """Tests for admin user models."""
    
    def test_admin_user_create_valid(self):
        """Test creating a valid admin user."""
        user = AdminUserCreate(
            email="test@example.com",
            password="password123",
        )
        
        assert user.email == "test@example.com"
        assert user.password == "password123"
        assert user.is_active is True  # Default value
    
    def test_admin_user_create_missing_required(self):
        """Test that required fields are enforced."""
        with pytest.raises(ValidationError):
            AdminUserCreate(email="test@example.com")  # Missing password
    
    def test_admin_user_create_password_min_length(self):
        """Test that password has minimum length requirement."""
        with pytest.raises(ValidationError):
            AdminUserCreate(
                email="test@example.com",
                password="short",  # Less than 8 characters
            )
    
    def test_admin_user_create_invalid_email(self):
        """Test that email validation works."""
        with pytest.raises(ValidationError):
            AdminUserCreate(
                email="not-an-email",
                password="password123",
            )

