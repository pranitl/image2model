"""
Unit tests for TripoClient implementation.
"""

import pytest
from unittest.mock import patch

from app.workers.fal_client import TripoClient
from tests.mocks.fal_responses import TRIPO_SUCCESS, INVALID_PARAMS


class TestTripoClient:
    """Test cases for TripoClient."""
    
    @pytest.fixture
    def tripo_client(self):
        """Create a TripoClient instance with mocked settings."""
        with patch("app.core.config.settings.FAL_API_KEY", "test-key"):
            return TripoClient()
    
    def test_model_endpoint_property(self, tripo_client):
        """Test that correct endpoint is returned."""
        assert tripo_client.model_endpoint == "tripo3d/tripo/v2.5/image-to-3d"
    
    def test_prepare_input_basic(self, tripo_client):
        """Test basic parameter preparation."""
        image_url = "https://fal.ai/uploads/test.png"
        params = {}
        
        result = tripo_client.prepare_input(image_url, params)
        
        assert result["image_url"] == image_url
        assert result["texture"] == "standard"  # Default to enabled
        assert result["texture_alignment"] == "original_image"
        assert result["orientation"] == "default"
        assert "face_limit" not in result  # Not included when not specified
    
    def test_prepare_input_texture_enabled_true(self, tripo_client):
        """Test texture parameter when enabled."""
        image_url = "https://fal.ai/uploads/test.png"
        params = {"texture_enabled": True}
        
        result = tripo_client.prepare_input(image_url, params)
        
        assert result["texture"] == "standard"
    
    def test_prepare_input_texture_enabled_false(self, tripo_client):
        """Test texture parameter when disabled."""
        image_url = "https://fal.ai/uploads/test.png"
        params = {"texture_enabled": False}
        
        result = tripo_client.prepare_input(image_url, params)
        
        assert result["texture"] == "no"
    
    def test_prepare_input_with_face_limit(self, tripo_client):
        """Test face limit parameter inclusion."""
        image_url = "https://fal.ai/uploads/test.png"
        params = {"face_limit": 10000}
        
        result = tripo_client.prepare_input(image_url, params)
        
        assert result["face_limit"] == 10000
        assert "quad" not in result  # Should not set quad=True
    
    def test_prepare_input_without_face_limit(self, tripo_client):
        """Test that face_limit is not included when not specified."""
        image_url = "https://fal.ai/uploads/test.png"
        params = {"texture_enabled": True}
        
        result = tripo_client.prepare_input(image_url, params)
        
        assert "face_limit" not in result
    
    def test_prepare_input_face_limit_none_not_included(self, tripo_client):
        """Test that face_limit of None is not included in input."""
        image_url = "https://fal.ai/uploads/test.png"
        params = {"face_limit": None}
        
        result = tripo_client.prepare_input(image_url, params)
        
        assert "face_limit" not in result
    
    def test_validate_params_texture_enabled_invalid(self, tripo_client):
        """Test validation rejects non-boolean texture_enabled."""
        params = {"texture_enabled": "yes"}
        
        with pytest.raises(ValueError) as exc_info:
            tripo_client.validate_params(params)
        assert "texture_enabled must be a boolean value" in str(exc_info.value)
    
    def test_validate_params_face_limit_negative(self, tripo_client):
        """Test validation rejects negative face_limit."""
        params = {"face_limit": -100}
        
        with pytest.raises(ValueError) as exc_info:
            tripo_client.validate_params(params)
        assert "face_limit must be a positive integer" in str(exc_info.value)
    
    def test_validate_params_face_limit_zero(self, tripo_client):
        """Test validation rejects zero face_limit."""
        params = {"face_limit": 0}
        
        with pytest.raises(ValueError) as exc_info:
            tripo_client.validate_params(params)
        assert "face_limit must be a positive integer" in str(exc_info.value)
    
    def test_validate_params_face_limit_string(self, tripo_client):
        """Test validation rejects string face_limit."""
        params = {"face_limit": "1000"}
        
        with pytest.raises(ValueError) as exc_info:
            tripo_client.validate_params(params)
        assert "face_limit must be a positive integer" in str(exc_info.value)
    
    def test_model_info_metadata(self, tripo_client):
        """Test MODEL_INFO structure is correct."""
        assert tripo_client.MODEL_INFO["name"] == "tripo3d"
        assert "description" in tripo_client.MODEL_INFO
        assert tripo_client.MODEL_INFO["type"] == "image_to_3d"
        assert "glb" in tripo_client.MODEL_INFO["supported_formats"]
        assert tripo_client.MODEL_INFO["default_params"]["texture_enabled"] is True
        
        # Check param schema
        param_schema = tripo_client.MODEL_INFO["param_schema"]
        assert "texture_enabled" in param_schema
        assert param_schema["texture_enabled"]["type"] == "boolean"
        assert "face_limit" in param_schema
        assert param_schema["face_limit"]["type"] == "integer"
    
    def test_validate_params_valid_params(self, tripo_client):
        """Test validation passes for valid parameters."""
        params = {
            "texture_enabled": True,
            "face_limit": 5000
        }
        
        # Should not raise any exception
        tripo_client.validate_params(params)
    
    def test_validate_params_empty(self, tripo_client):
        """Test validation passes for empty parameters."""
        params = {}
        
        # Should not raise any exception
        tripo_client.validate_params(params)
    
    def test_validate_params_none_face_limit(self, tripo_client):
        """Test validation handles None face_limit."""
        params = {"face_limit": None}
        
        # Should not raise any exception (None is allowed)
        tripo_client.validate_params(params)
    
    def test_prepare_input_face_limit_zero_not_included(self, tripo_client):
        """Test that face_limit of 0 is not included in input."""
        image_url = "https://fal.ai/uploads/test.png"
        params = {"face_limit": 0}
        
        # prepare_input checks > 0, so zero is not included
        result = tripo_client.prepare_input(image_url, params)
        
        assert "face_limit" not in result
    
    def test_prepare_input_preserves_defaults(self, tripo_client):
        """Test that default values are properly set."""
        image_url = "https://fal.ai/uploads/test.png"
        params = {"face_limit": 1000}
        
        result = tripo_client.prepare_input(image_url, params)
        
        # Check all default values are present
        assert result["texture"] == "standard"
        assert result["texture_alignment"] == "original_image"
        assert result["orientation"] == "default"
        assert result["face_limit"] == 1000