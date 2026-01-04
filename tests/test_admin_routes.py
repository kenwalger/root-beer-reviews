"""Tests for admin routes."""
import pytest
from fastapi import status
from httpx import AsyncClient
from bson import ObjectId


@pytest.mark.integration
@pytest.mark.admin
class TestAdminDashboard:
    """Tests for admin dashboard route."""
    
    @pytest.mark.asyncio
    async def test_dashboard_requires_auth(self, client: AsyncClient):
        """Test that dashboard requires authentication."""
        response = await client.get("/admin", follow_redirects=False)
        
        # Should redirect to login
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_401_UNAUTHORIZED]
    
    @pytest.mark.asyncio
    async def test_dashboard_accessible_when_authenticated(self, authenticated_client: AsyncClient):
        """Test that dashboard is accessible when authenticated."""
        response = await authenticated_client.get("/admin")
        
        assert response.status_code == status.HTTP_200_OK
        assert "dashboard" in response.text.lower() or "root beer" in response.text.lower()


@pytest.mark.integration
@pytest.mark.admin
class TestRootBeerCRUD:
    """Tests for root beer CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_list_rootbeers_requires_auth(self, client: AsyncClient):
        """Test that listing root beers requires authentication."""
        response = await client.get("/admin/rootbeers", follow_redirects=False)
        
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_401_UNAUTHORIZED]
    
    @pytest.mark.asyncio
    async def test_list_rootbeers_when_authenticated(self, authenticated_client: AsyncClient):
        """Test listing root beers when authenticated."""
        response = await authenticated_client.get("/admin/rootbeers")
        
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_new_rootbeer_form_requires_auth(self, client: AsyncClient):
        """Test that new root beer form requires authentication."""
        response = await client.get("/admin/rootbeers/new", follow_redirects=False)
        
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_401_UNAUTHORIZED]
    
    @pytest.mark.asyncio
    async def test_new_rootbeer_form_accessible(self, authenticated_client: AsyncClient):
        """Test that new root beer form is accessible when authenticated."""
        response = await authenticated_client.get("/admin/rootbeers/new")
        
        assert response.status_code == status.HTTP_200_OK
        assert "form" in response.text.lower() or "root beer" in response.text.lower()
    
    @pytest.mark.asyncio
    async def test_create_rootbeer_requires_auth(self, client: AsyncClient):
        """Test that creating root beer requires authentication."""
        response = await client.post(
            "/admin/rootbeers",
            data={"name": "Test", "brand": "Test Brand"},
            follow_redirects=False,
        )
        
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_401_UNAUTHORIZED]
    
    @pytest.mark.asyncio
    async def test_create_rootbeer_success(
        self, 
        authenticated_client: AsyncClient, 
        test_db: None
    ):
        """Test successful root beer creation."""
        response = await authenticated_client.post(
            "/admin/rootbeers",
            data={
                "name": "Test Root Beer",
                "brand": "Test Brand",
                "region": "Test Region",
                "country": "USA",
            },
            follow_redirects=False,
        )
        
        assert response.status_code == status.HTTP_303_SEE_OTHER
        
        # Verify root beer was created in database
        from app.database import get_database
        database = get_database()
        if database is not None:
            rootbeer = await database.rootbeers.find_one({"name": "Test Root Beer"})
            assert rootbeer is not None
            assert rootbeer["brand"] == "Test Brand"
    
    @pytest.mark.asyncio
    async def test_view_rootbeer_requires_auth(self, client: AsyncClient, sample_rootbeer: dict):
        """Test that viewing root beer requires authentication."""
        rootbeer_id = str(sample_rootbeer["_id"])
        response = await client.get(
            f"/admin/rootbeers/{rootbeer_id}",
            follow_redirects=False,
        )
        
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_401_UNAUTHORIZED]
    
    @pytest.mark.asyncio
    async def test_view_rootbeer_when_authenticated(
        self, 
        authenticated_client: AsyncClient, 
        sample_rootbeer: dict
    ):
        """Test viewing root beer when authenticated."""
        rootbeer_id = str(sample_rootbeer["_id"])
        response = await authenticated_client.get(f"/admin/rootbeers/{rootbeer_id}")
        
        assert response.status_code == status.HTTP_200_OK
        assert sample_rootbeer["name"].lower() in response.text.lower()
    
    @pytest.mark.asyncio
    async def test_view_nonexistent_rootbeer(self, authenticated_client: AsyncClient):
        """Test viewing a nonexistent root beer."""
        fake_id = str(ObjectId())
        response = await authenticated_client.get(f"/admin/rootbeers/{fake_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_update_rootbeer_success(
        self,
        authenticated_client: AsyncClient,
        sample_rootbeer: dict,
    ):
        """Test successful root beer update."""
        rootbeer_id = str(sample_rootbeer["_id"])
        # Use JSON since route expects RootBeerUpdate Pydantic model
        response = await authenticated_client.post(
            f"/admin/rootbeers/{rootbeer_id}",
            json={
                "name": "Updated Root Beer Name",
                "brand": "Updated Brand",
            },
            follow_redirects=False,
        )
        
        assert response.status_code == status.HTTP_303_SEE_OTHER
        
        # Verify root beer was updated in database
        from app.database import get_database
        database = get_database()
        if database is not None:
            rootbeer = await database.rootbeers.find_one({"_id": ObjectId(rootbeer_id)})
            assert rootbeer is not None
            assert rootbeer["name"] == "Updated Root Beer Name"
            assert rootbeer["brand"] == "Updated Brand"
    
    @pytest.mark.asyncio
    async def test_update_nonexistent_rootbeer(self, authenticated_client: AsyncClient):
        """Test updating a nonexistent root beer."""
        fake_id = str(ObjectId())
        response = await authenticated_client.post(
            f"/admin/rootbeers/{fake_id}",
            json={"name": "Test"},
            follow_redirects=False,
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_delete_rootbeer_success(
        self,
        authenticated_client: AsyncClient,
        test_db: None,
    ):
        """Test successful root beer deletion."""
        from app.database import get_database
        from datetime import datetime, UTC
        
        database = get_database()
        if database is None:
            pytest.skip("Database not available")
        
        # Create a root beer without reviews
        rootbeer = {
            "name": "To Be Deleted",
            "brand": "Test Brand",
            "region": "Test Region",
            "country": "USA",
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
        result = await database.rootbeers.insert_one(rootbeer)
        rootbeer_id = str(result.inserted_id)
        
        response = await authenticated_client.post(
            f"/admin/rootbeers/{rootbeer_id}/delete",
            follow_redirects=False,
        )
        
        assert response.status_code == status.HTTP_303_SEE_OTHER
        
        # Verify root beer was deleted
        deleted = await database.rootbeers.find_one({"_id": ObjectId(rootbeer_id)})
        assert deleted is None
    
    @pytest.mark.asyncio
    async def test_delete_rootbeer_with_reviews(
        self,
        authenticated_client: AsyncClient,
        sample_rootbeer: dict,
        sample_review: dict,
    ):
        """Test that root beer with reviews cannot be deleted."""
        rootbeer_id = str(sample_rootbeer["_id"])
        response = await authenticated_client.post(
            f"/admin/rootbeers/{rootbeer_id}/delete",
            follow_redirects=False,
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_rootbeer(self, authenticated_client: AsyncClient):
        """Test deleting a nonexistent root beer."""
        fake_id = str(ObjectId())
        response = await authenticated_client.post(
            f"/admin/rootbeers/{fake_id}/delete",
            follow_redirects=False,
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
@pytest.mark.admin
class TestReviewCRUD:
    """Tests for review CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_list_reviews_requires_auth(self, client: AsyncClient):
        """Test that listing reviews requires authentication."""
        response = await client.get("/admin/reviews", follow_redirects=False)
        
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_401_UNAUTHORIZED]
    
    @pytest.mark.asyncio
    async def test_list_reviews_when_authenticated(self, authenticated_client: AsyncClient):
        """Test listing reviews when authenticated."""
        response = await authenticated_client.get("/admin/reviews")
        
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_new_review_form_requires_auth(self, client: AsyncClient):
        """Test that new review form requires authentication."""
        response = await client.get("/admin/reviews/new", follow_redirects=False)
        
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_401_UNAUTHORIZED]
    
    @pytest.mark.asyncio
    async def test_new_review_form_accessible(self, authenticated_client: AsyncClient):
        """Test that new review form is accessible when authenticated."""
        response = await authenticated_client.get("/admin/reviews/new")
        
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_create_review_success(
        self,
        authenticated_client: AsyncClient,
        test_db: None,
        sample_rootbeer: dict,
    ):
        """Test successful review creation."""
        from datetime import datetime, UTC
        
        response = await authenticated_client.post(
            "/admin/reviews",
            data={
                "root_beer_id": str(sample_rootbeer["_id"]),
                "review_date": datetime.now(UTC).isoformat(),
                "sweetness": "3",
                "carbonation_bite": "4",
                "creaminess": "2",
                "acidity": "3",
                "aftertaste_length": "4",
                "overall_score": "7",
                "would_drink_again": "true",
            },
            follow_redirects=False,
        )
        
        assert response.status_code == status.HTTP_303_SEE_OTHER
        
        # Verify review was created
        from app.database import get_database
        database = get_database()
        if database is not None:
            review = await database.reviews.find_one({"root_beer_id": str(sample_rootbeer["_id"])})
            assert review is not None
            assert review["overall_score"] == 7
    
    @pytest.mark.asyncio
    async def test_view_review_requires_auth(self, client: AsyncClient, sample_review: dict):
        """Test that viewing review requires authentication."""
        review_id = str(sample_review["_id"])
        response = await client.get(
            f"/admin/reviews/{review_id}",
            follow_redirects=False,
        )
        
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_401_UNAUTHORIZED]
    
    @pytest.mark.asyncio
    async def test_view_review_when_authenticated(
        self,
        authenticated_client: AsyncClient,
        sample_review: dict,
    ):
        """Test viewing review when authenticated."""
        review_id = str(sample_review["_id"])
        response = await authenticated_client.get(f"/admin/reviews/{review_id}")
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.integration
@pytest.mark.admin
class TestFlavorNoteManagement:
    """Tests for flavor note management."""
    
    @pytest.mark.asyncio
    async def test_list_flavor_notes_requires_auth(self, client: AsyncClient):
        """Test that listing flavor notes requires authentication."""
        response = await client.get("/admin/flavor-notes", follow_redirects=False)
        
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_401_UNAUTHORIZED]
    
    @pytest.mark.asyncio
    async def test_list_flavor_notes_when_authenticated(self, authenticated_client: AsyncClient):
        """Test listing flavor notes when authenticated."""
        response = await authenticated_client.get("/admin/flavor-notes")
        
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_create_flavor_note_success(
        self,
        authenticated_client: AsyncClient,
        test_db: None,
    ):
        """Test successful flavor note creation."""
        response = await authenticated_client.post(
            "/admin/flavor-notes",
            data={
                "name": "Test Flavor Note",
                "category": "Test Category",
            },
            follow_redirects=False,
        )
        
        assert response.status_code == status.HTTP_303_SEE_OTHER
        
        # Verify flavor note was created
        from app.database import get_database
        database = get_database()
        if database is not None:
            flavor_note = await database.flavor_notes.find_one({"name": "Test Flavor Note"})
            assert flavor_note is not None
            assert flavor_note["category"] == "Test Category"
    
    @pytest.mark.asyncio
    async def test_delete_flavor_note_success(
        self,
        authenticated_client: AsyncClient,
        test_db: None,
    ):
        """Test successful flavor note deletion."""
        from app.database import get_database
        from datetime import datetime, UTC
        
        database = get_database()
        if database is None:
            pytest.skip("Database not available")
        
        # Create a flavor note
        flavor_note = {
            "name": "To Be Deleted",
            "category": "Test",
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
        result = await database.flavor_notes.insert_one(flavor_note)
        flavor_note_id = str(result.inserted_id)
        
        response = await authenticated_client.post(
            f"/admin/flavor-notes/{flavor_note_id}/delete",
            follow_redirects=False,
        )
        
        assert response.status_code == status.HTTP_303_SEE_OTHER
        
        # Verify flavor note was deleted
        deleted = await database.flavor_notes.find_one({"_id": ObjectId(flavor_note_id)})
        assert deleted is None


@pytest.mark.integration
@pytest.mark.admin
class TestMetadataManagement:
    """Tests for metadata management."""
    
    @pytest.mark.asyncio
    async def test_metadata_management_requires_auth(self, client: AsyncClient):
        """Test that metadata management requires authentication."""
        response = await client.get("/admin/metadata", follow_redirects=False)
        
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_401_UNAUTHORIZED]
    
    @pytest.mark.asyncio
    async def test_metadata_management_when_authenticated(self, authenticated_client: AsyncClient):
        """Test metadata management page when authenticated."""
        response = await authenticated_client.get("/admin/metadata")
        
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_create_color_success(
        self,
        authenticated_client: AsyncClient,
        test_db: None,
    ):
        """Test successful color creation."""
        response = await authenticated_client.post(
            "/admin/metadata/colors",
            data={"name": "Test Color"},
            follow_redirects=False,
        )
        
        assert response.status_code == status.HTTP_303_SEE_OTHER
        
        # Verify color was created
        from app.database import get_database
        database = get_database()
        if database is not None:
            color = await database.colors.find_one({"name": "Test Color"})
            assert color is not None
    
    @pytest.mark.asyncio
    async def test_delete_color_success(
        self,
        authenticated_client: AsyncClient,
        test_db: None,
    ):
        """Test successful color deletion."""
        from app.database import get_database
        from datetime import datetime, UTC
        
        database = get_database()
        if database is None:
            pytest.skip("Database not available")
        
        # Create a color
        color = {
            "name": "To Be Deleted",
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
        result = await database.colors.insert_one(color)
        color_id = str(result.inserted_id)
        
        response = await authenticated_client.post(
            f"/admin/metadata/colors/{color_id}/delete",
            follow_redirects=False,
        )
        
        assert response.status_code == status.HTTP_303_SEE_OTHER
        
        # Verify color was deleted
        deleted = await database.colors.find_one({"_id": ObjectId(color_id)})
        assert deleted is None
    
    @pytest.mark.asyncio
    async def test_create_serving_context_success(
        self,
        authenticated_client: AsyncClient,
        test_db: None,
    ):
        """Test successful serving context creation."""
        response = await authenticated_client.post(
            "/admin/metadata/serving-contexts",
            data={"name": "Test Context"},
            follow_redirects=False,
        )
        
        assert response.status_code == status.HTTP_303_SEE_OTHER
        
        # Verify serving context was created
        from app.database import get_database
        database = get_database()
        if database is not None:
            context = await database.serving_contexts.find_one({"name": "Test Context"})
            assert context is not None
    
    @pytest.mark.asyncio
    async def test_delete_serving_context_success(
        self,
        authenticated_client: AsyncClient,
        test_db: None,
    ):
        """Test successful serving context deletion."""
        from app.database import get_database
        from datetime import datetime, UTC
        
        database = get_database()
        if database is None:
            pytest.skip("Database not available")
        
        # Create a serving context
        context = {
            "name": "To Be Deleted",
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
        result = await database.serving_contexts.insert_one(context)
        context_id = str(result.inserted_id)
        
        response = await authenticated_client.post(
            f"/admin/metadata/serving-contexts/{context_id}/delete",
            follow_redirects=False,
        )
        
        assert response.status_code == status.HTTP_303_SEE_OTHER
        
        # Verify serving context was deleted
        deleted = await database.serving_contexts.find_one({"_id": ObjectId(context_id)})
        assert deleted is None


@pytest.mark.integration
@pytest.mark.admin
class TestAdminAccount:
    """Tests for admin account management."""
    
    @pytest.mark.asyncio
    async def test_admin_account_requires_auth(self, client: AsyncClient):
        """Test that admin account page requires authentication."""
        response = await client.get("/admin/account", follow_redirects=False)
        
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_401_UNAUTHORIZED]
    
    @pytest.mark.asyncio
    async def test_admin_account_when_authenticated(self, authenticated_client: AsyncClient):
        """Test admin account page when authenticated."""
        response = await authenticated_client.get("/admin/account")
        
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_change_password_success(
        self,
        authenticated_client: AsyncClient,
        admin_user: dict[str, str],
    ):
        """Test successful password change."""
        response = await authenticated_client.post(
            "/admin/account/change-password",
            data={
                "current_password": admin_user["password"],
                "new_password": "newpassword123",
                "confirm_password": "newpassword123",
            },
            follow_redirects=False,
        )
        
        assert response.status_code == status.HTTP_303_SEE_OTHER
        
        # Verify password was changed by trying to login with new password
        from app.auth import authenticate_admin
        user = await authenticate_admin(admin_user["email"], "newpassword123")
        assert user is not None
    
    @pytest.mark.asyncio
    async def test_change_password_wrong_current(
        self,
        authenticated_client: AsyncClient,
        admin_user: dict[str, str],
    ):
        """Test password change with wrong current password."""
        response = await authenticated_client.post(
            "/admin/account/change-password",
            data={
                "current_password": "wrongpassword",
                "new_password": "newpassword123",
                "confirm_password": "newpassword123",
            },
            follow_redirects=False,
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "incorrect" in response.text.lower()
    
    @pytest.mark.asyncio
    async def test_change_password_mismatch(
        self,
        authenticated_client: AsyncClient,
        admin_user: dict[str, str],
    ):
        """Test password change with mismatched new passwords."""
        response = await authenticated_client.post(
            "/admin/account/change-password",
            data={
                "current_password": admin_user["password"],
                "new_password": "newpassword123",
                "confirm_password": "differentpassword",
            },
            follow_redirects=False,
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "match" in response.text.lower()
    
    @pytest.mark.asyncio
    async def test_change_password_too_short(
        self,
        authenticated_client: AsyncClient,
        admin_user: dict[str, str],
    ):
        """Test password change with password that's too short."""
        response = await authenticated_client.post(
            "/admin/account/change-password",
            data={
                "current_password": admin_user["password"],
                "new_password": "short",
                "confirm_password": "short",
            },
            follow_redirects=False,
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "8" in response.text or "characters" in response.text.lower()


@pytest.mark.integration
@pytest.mark.admin
@pytest.mark.s3
class TestImageManagement:
    """Tests for image management operations."""
    
    @pytest.mark.asyncio
    async def test_upload_rootbeer_image_requires_auth(
        self,
        client: AsyncClient,
        sample_rootbeer: dict,
    ):
        """Test that uploading image requires authentication."""
        rootbeer_id = str(sample_rootbeer["_id"])
        response = await client.post(
            f"/admin/rootbeers/{rootbeer_id}/images",
            files={"file": ("test.jpg", b"fake image data", "image/jpeg")},
            follow_redirects=False,
        )
        
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_401_UNAUTHORIZED]
    
    @pytest.mark.asyncio
    async def test_upload_rootbeer_image_success(
        self,
        authenticated_client: AsyncClient,
        sample_rootbeer: dict,
        mocker,
    ):
        """Test successful image upload."""
        from unittest.mock import AsyncMock, patch
        
        rootbeer_id = str(sample_rootbeer["_id"])
        
        # Mock S3 upload to return a URL
        mock_upload = AsyncMock(return_value="https://s3.amazonaws.com/bucket/test.jpg")
        
        with patch("app.routes.admin.upload_image", mock_upload):
            response = await authenticated_client.post(
                f"/admin/rootbeers/{rootbeer_id}/images",
                files={"file": ("test.jpg", b"fake image data", "image/jpeg")},
                follow_redirects=False,
            )
            
            assert response.status_code == status.HTTP_303_SEE_OTHER
            mock_upload.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_rootbeer_image_requires_auth(
        self,
        client: AsyncClient,
        sample_rootbeer: dict,
    ):
        """Test that deleting image requires authentication."""
        rootbeer_id = str(sample_rootbeer["_id"])
        response = await client.post(
            f"/admin/rootbeers/{rootbeer_id}/images/delete",
            data={"image_url": "https://example.com/image.jpg"},
            follow_redirects=False,
        )
        
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_401_UNAUTHORIZED]
    
    @pytest.mark.asyncio
    async def test_delete_rootbeer_image_success(
        self,
        authenticated_client: AsyncClient,
        test_db: None,
        mocker,
    ):
        """Test successful image deletion."""
        from app.database import get_database
        from datetime import datetime, UTC
        from unittest.mock import AsyncMock, patch
        
        database = get_database()
        if database is None:
            pytest.skip("Database not available")
        
        # Create a root beer with an image
        rootbeer = {
            "name": "Test Root Beer",
            "brand": "Test Brand",
            "images": ["https://example.com/image.jpg"],
            "primary_image": "https://example.com/image.jpg",
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
        result = await database.rootbeers.insert_one(rootbeer)
        rootbeer_id = str(result.inserted_id)
        
        # Mock S3 delete
        mock_delete = AsyncMock(return_value=True)
        
        with patch("app.routes.admin.delete_image", mock_delete):
            response = await authenticated_client.post(
                f"/admin/rootbeers/{rootbeer_id}/images/delete",
                data={"image_url": "https://example.com/image.jpg"},
                follow_redirects=False,
            )
            
            assert response.status_code == status.HTTP_303_SEE_OTHER
            mock_delete.assert_called_once()
            
            # Verify image was removed from database
            updated = await database.rootbeers.find_one({"_id": result.inserted_id})
            assert updated is not None
            assert "https://example.com/image.jpg" not in updated.get("images", [])
    
    @pytest.mark.asyncio
    async def test_set_primary_image_requires_auth(
        self,
        client: AsyncClient,
        sample_rootbeer: dict,
    ):
        """Test that setting primary image requires authentication."""
        rootbeer_id = str(sample_rootbeer["_id"])
        response = await client.post(
            f"/admin/rootbeers/{rootbeer_id}/images/set-primary",
            data={"image_url": "https://example.com/image.jpg"},
            follow_redirects=False,
        )
        
        assert response.status_code in [status.HTTP_303_SEE_OTHER, status.HTTP_401_UNAUTHORIZED]
    
    @pytest.mark.asyncio
    async def test_set_primary_image_success(
        self,
        authenticated_client: AsyncClient,
        test_db: None,
    ):
        """Test successful primary image setting."""
        from app.database import get_database
        from datetime import datetime, UTC
        
        database = get_database()
        if database is None:
            pytest.skip("Database not available")
        
        # Create a root beer with images
        rootbeer = {
            "name": "Test Root Beer",
            "brand": "Test Brand",
            "images": [
                "https://example.com/image1.jpg",
                "https://example.com/image2.jpg",
            ],
            "primary_image": "https://example.com/image1.jpg",
            "created_at": datetime.now(UTC),
            "updated_at": datetime.now(UTC),
        }
        result = await database.rootbeers.insert_one(rootbeer)
        rootbeer_id = str(result.inserted_id)
        
        response = await authenticated_client.post(
            f"/admin/rootbeers/{rootbeer_id}/images/set-primary",
            data={"image_url": "https://example.com/image2.jpg"},
            follow_redirects=False,
        )
        
        assert response.status_code == status.HTTP_303_SEE_OTHER
        
        # Verify primary image was updated
        updated = await database.rootbeers.find_one({"_id": result.inserted_id})
        assert updated is not None
        assert updated["primary_image"] == "https://example.com/image2.jpg"
    
    @pytest.mark.asyncio
    async def test_update_review_success(
        self,
        authenticated_client: AsyncClient,
        sample_review: dict,
    ):
        """Test successful review update."""
        review_id = str(sample_review["_id"])
        from datetime import datetime, UTC
        
        response = await authenticated_client.post(
            f"/admin/reviews/{review_id}",
            data={
                "overall_score": "9",
                "sweetness": "4",
                "tasting_notes": "Updated tasting notes",
            },
            follow_redirects=False,
        )
        
        assert response.status_code == status.HTTP_303_SEE_OTHER
        
        # Verify review was updated in database
        from app.database import get_database
        database = get_database()
        if database is not None:
            review = await database.reviews.find_one({"_id": ObjectId(review_id)})
            assert review is not None
            assert review["overall_score"] == 9
            assert review["sweetness"] == 4
            assert review["tasting_notes"] == "Updated tasting notes"
    
    @pytest.mark.asyncio
    async def test_update_nonexistent_review(self, authenticated_client: AsyncClient):
        """Test updating a nonexistent review."""
        fake_id = str(ObjectId())
        response = await authenticated_client.post(
            f"/admin/reviews/{fake_id}",
            data={"overall_score": "5"},
            follow_redirects=False,
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_delete_review_success(
        self,
        authenticated_client: AsyncClient,
        sample_review: dict,
    ):
        """Test successful review deletion."""
        review_id = str(sample_review["_id"])
        response = await authenticated_client.post(
            f"/admin/reviews/{review_id}/delete",
            follow_redirects=False,
        )
        
        assert response.status_code == status.HTTP_303_SEE_OTHER
        
        # Verify review was deleted
        from app.database import get_database
        database = get_database()
        if database is not None:
            deleted = await database.reviews.find_one({"_id": ObjectId(review_id)})
            assert deleted is None
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_review(self, authenticated_client: AsyncClient):
        """Test deleting a nonexistent review."""
        fake_id = str(ObjectId())
        response = await authenticated_client.post(
            f"/admin/reviews/{fake_id}/delete",
            follow_redirects=False,
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

