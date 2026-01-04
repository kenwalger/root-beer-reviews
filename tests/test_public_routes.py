"""Tests for public routes."""
import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.integration
@pytest.mark.public
class TestHomepage:
    """Tests for homepage route."""
    
    @pytest.mark.asyncio
    async def test_homepage_loads(self, client: AsyncClient):
        """Test that homepage loads successfully."""
        response = await client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_homepage_with_reviews(self, client: AsyncClient, sample_rootbeer: dict, sample_review: dict):
        """Test homepage displays root beers with reviews."""
        response = await client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        # Should show root beers that have reviews
        assert "root beer" in response.text.lower() or "review" in response.text.lower()
    
    @pytest.mark.asyncio
    async def test_homepage_pagination(self, client: AsyncClient):
        """Test homepage pagination parameters."""
        response = await client.get("/?page=1&per_page=20")
        
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_homepage_filtering(self, client: AsyncClient, sample_rootbeer: dict):
        """Test homepage filtering by brand."""
        response = await client.get(f"/?brand={sample_rootbeer['brand']}")
        
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.integration
@pytest.mark.public
class TestRootBeerPublicView:
    """Tests for public root beer view."""
    
    @pytest.mark.asyncio
    async def test_view_rootbeer_public(self, client: AsyncClient, sample_rootbeer: dict):
        """Test viewing a root beer publicly."""
        rootbeer_id = str(sample_rootbeer["_id"])
        response = await client.get(f"/rootbeers/{rootbeer_id}")
        
        assert response.status_code == status.HTTP_200_OK
        assert sample_rootbeer["name"].lower() in response.text.lower()
    
    @pytest.mark.asyncio
    async def test_view_nonexistent_rootbeer_public(self, client: AsyncClient):
        """Test viewing a nonexistent root beer."""
        from bson import ObjectId
        fake_id = str(ObjectId())
        response = await client.get(f"/rootbeers/{fake_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_view_rootbeer_with_reviews(
        self, 
        client: AsyncClient, 
        sample_rootbeer: dict, 
        sample_review: dict
    ):
        """Test viewing root beer with reviews."""
        rootbeer_id = str(sample_rootbeer["_id"])
        response = await client.get(f"/rootbeers/{rootbeer_id}")
        
        assert response.status_code == status.HTTP_200_OK
        # Should display review information
        assert "review" in response.text.lower() or "rating" in response.text.lower()


@pytest.mark.integration
@pytest.mark.public
class TestReviewPublicView:
    """Tests for public review view."""
    
    @pytest.mark.asyncio
    async def test_view_review_public(self, client: AsyncClient, sample_review: dict):
        """Test viewing a review publicly."""
        review_id = str(sample_review["_id"])
        response = await client.get(f"/reviews/{review_id}")
        
        assert response.status_code == status.HTTP_200_OK
    
    @pytest.mark.asyncio
    async def test_view_nonexistent_review_public(self, client: AsyncClient):
        """Test viewing a nonexistent review."""
        from bson import ObjectId
        fake_id = str(ObjectId())
        response = await client.get(f"/reviews/{fake_id}")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
@pytest.mark.public
class TestPublicRoutesNoAuth:
    """Tests that public routes don't require authentication."""
    
    @pytest.mark.asyncio
    async def test_homepage_no_auth_required(self, client: AsyncClient):
        """Test homepage doesn't require authentication."""
        response = await client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        # Should not redirect to login
        assert "/admin/login" not in str(response.url)
    
    @pytest.mark.asyncio
    async def test_rootbeer_view_no_auth_required(self, client: AsyncClient, sample_rootbeer: dict):
        """Test root beer view doesn't require authentication."""
        rootbeer_id = str(sample_rootbeer["_id"])
        response = await client.get(f"/rootbeers/{rootbeer_id}")
        
        assert response.status_code == status.HTTP_200_OK
        assert "/admin/login" not in str(response.url)

