"""Tests for utility functions."""
import pytest
from fastapi import Request
from unittest.mock import Mock
from app.utils.pagination import (
    get_pagination_params,
    calculate_pagination_info,
    build_pagination_url,
)


@pytest.mark.unit
class TestPagination:
    """Tests for pagination utilities."""
    
    def test_get_pagination_params_default(self):
        """Test getting pagination params with defaults."""
        request = Mock(spec=Request)
        request.query_params = {}
        
        params = get_pagination_params(request)
        
        assert params["page"] == 1
        assert params["per_page"] == 20
        assert params["skip"] == 0
        assert params["limit"] == 20
    
    def test_get_pagination_params_custom(self):
        """Test getting pagination params with custom values."""
        request = Mock(spec=Request)
        request.query_params = {"page": "3", "per_page": "50"}
        
        params = get_pagination_params(request, default_per_page=20)
        
        assert params["page"] == 3
        assert params["per_page"] == 50
        assert params["skip"] == 100  # (3-1) * 50
        assert params["limit"] == 50
    
    def test_get_pagination_params_invalid_page(self):
        """Test pagination params with invalid page number."""
        request = Mock(spec=Request)
        request.query_params = {"page": "invalid", "per_page": "20"}
        
        params = get_pagination_params(request)
        
        assert params["page"] == 1  # Defaults to 1
    
    def test_get_pagination_params_invalid_per_page(self):
        """Test pagination params with invalid per_page value."""
        request = Mock(spec=Request)
        request.query_params = {"page": "1", "per_page": "999"}  # Not in allowed list
        
        params = get_pagination_params(request, default_per_page=20)
        
        assert params["per_page"] == 20  # Defaults to default_per_page
    
    def test_calculate_pagination_info(self):
        """Test pagination info calculation."""
        info = calculate_pagination_info(total_items=100, page=2, per_page=20)
        
        assert info["total_items"] == 100
        assert info["total_pages"] == 5
        assert info["page"] == 2
        assert info["per_page"] == 20
        assert info["has_prev"] is True
        assert info["has_next"] is True
        assert info["prev_page"] == 1
        assert info["next_page"] == 3
        assert info["start_item"] == 21
        assert info["end_item"] == 40
    
    def test_calculate_pagination_info_first_page(self):
        """Test pagination info for first page."""
        info = calculate_pagination_info(total_items=100, page=1, per_page=20)
        
        assert info["has_prev"] is False
        assert info["has_next"] is True
        assert info["prev_page"] is None
        assert info["next_page"] == 2
    
    def test_calculate_pagination_info_last_page(self):
        """Test pagination info for last page."""
        info = calculate_pagination_info(total_items=100, page=5, per_page=20)
        
        assert info["has_prev"] is True
        assert info["has_next"] is False
        assert info["prev_page"] == 4
        assert info["next_page"] is None
    
    def test_calculate_pagination_info_zero_items(self):
        """Test pagination info with zero items."""
        info = calculate_pagination_info(total_items=0, page=1, per_page=20)
        
        assert info["total_items"] == 0
        assert info["total_pages"] == 1
        assert info["start_item"] == 0
        assert info["end_item"] == 0
    
    def test_build_pagination_url(self):
        """Test building pagination URL."""
        base_url = "/admin/rootbeers"
        params = {"brand": "test", "sort": "name"}
        
        url = build_pagination_url(base_url, params, page=2, per_page=50)
        
        assert base_url in url
        assert "page=2" in url
        assert "per_page=50" in url
        assert "brand=test" in url
        assert "sort=name" in url
    
    def test_build_pagination_url_no_params(self):
        """Test building pagination URL with no existing params."""
        base_url = "/admin/rootbeers"
        params = {}
        
        url = build_pagination_url(base_url, params, page=1)
        
        assert url == "/admin/rootbeers?page=1"
    
    def test_build_pagination_url_preserves_existing(self):
        """Test that build_pagination_url preserves existing params."""
        base_url = "/admin/rootbeers"
        params = {"filter": "active", "sort": "name"}
        
        url = build_pagination_url(base_url, params, page=2)
        
        assert "filter=active" in url
        assert "sort=name" in url
        assert "page=2" in url

