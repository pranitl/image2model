"""
Edge case tests for parameter validation and missing fields.
"""

import pytest
from unittest.mock import patch
import asyncio

from app.workers.fal_client import (
    get_model_client,
    TripoClient,
    TrellisClient
)
from tests.mocks.fal_responses import INVALID_PARAMS


class TestEdgeCaseValidation:
    """Test edge cases for parameter validation and missing fields."""
    
    @pytest.fixture
    def tripo_client(self):
        """Create a TripoClient instance."""
        with patch("app.core.config.settings.FAL_API_KEY", "test-key"):
            return TripoClient()
    
    @pytest.fixture
    def trellis_client(self):
        """Create a TrellisClient instance."""
        with patch("app.core.config.settings.FAL_API_KEY", "test-key"):
            return TrellisClient()
    
    # Invalid Parameter Combinations
    
    def test_tripo_with_trellis_params(self, tripo_client):
        """Test that Tripo client ignores Trellis-specific parameters."""
        image_url = "https://fal.ai/uploads/test.png"
        params = {
            "texture_enabled": True,  # Valid Tripo param
            "ss_guidance_strength": 7.5,  # Invalid - Trellis param
            "mesh_simplify": 0.95,  # Invalid - Trellis param
            "texture_size": "1024"  # Invalid - Trellis param
        }
        
        # Should not raise during validation (unknown params ignored)
        tripo_client.validate_params(params)
        
        # Prepare input should only include valid Tripo params
        result = tripo_client.prepare_input(image_url, params)
        assert "texture" in result
        assert "ss_guidance_strength" not in result
        assert "mesh_simplify" not in result
        assert "texture_size" not in result
    
    def test_trellis_with_tripo_params(self, trellis_client):
        """Test that Trellis client ignores Tripo-specific parameters."""
        image_url = "https://fal.ai/uploads/test.png"
        params = {
            "texture_enabled": False,  # Invalid - Tripo param
            "face_limit": 1000,  # Invalid - Tripo param
            "ss_guidance_strength": 5.0,  # Valid Trellis param
            "texture_size": "2048"  # Valid Trellis param
        }
        
        # Should not raise during validation (unknown params ignored)
        trellis_client.validate_params(params)
        
        # Prepare input should only include valid Trellis params
        result = trellis_client.prepare_input(image_url, params)
        assert result["ss_guidance_strength"] == 5.0
        assert result["texture_size"] == "2048"
        assert "texture" not in result
        assert "face_limit" not in result
    
    def test_empty_params_dict(self, tripo_client, trellis_client):
        """Test both clients handle empty params dict."""
        image_url = "https://fal.ai/uploads/test.png"
        params = {}
        
        # Tripo should use defaults
        tripo_result = tripo_client.prepare_input(image_url, params)
        assert tripo_result["texture"] == "standard"
        assert "face_limit" not in tripo_result
        
        # Trellis should use all defaults
        trellis_result = trellis_client.prepare_input(image_url, params)
        assert trellis_result["ss_guidance_strength"] == 7.5
        assert trellis_result["texture_size"] == "1024"
    
    def test_none_params(self, tripo_client, trellis_client, mock_fal_subscribe):
        """Test both clients handle None params."""
        mock_fal_subscribe.response_type = "success"
        
        # Test with async process_single_image
        async def test_async():
            # Tripo
            tripo_result = await tripo_client.process_single_image(
                "test.png", 
                params=None
            )
            assert tripo_result["status"] == "success"
            
            # Trellis
            trellis_result = await trellis_client.process_single_image(
                "test.png",
                params=None
            )
            assert trellis_result["status"] == "success"
        
        # Run async test
        asyncio.run(test_async())
    
    def test_params_with_extra_fields(self, tripo_client, trellis_client):
        """Test handling of unknown parameters."""
        image_url = "https://fal.ai/uploads/test.png"
        
        # Extra params for Tripo
        tripo_params = {
            "texture_enabled": True,
            "face_limit": 5000,
            "unknown_param": "value",
            "another_unknown": 123
        }
        
        # Should not raise
        tripo_client.validate_params(tripo_params)
        result = tripo_client.prepare_input(image_url, tripo_params)
        assert "unknown_param" not in result
        assert "another_unknown" not in result
        
        # Extra params for Trellis
        trellis_params = {
            "ss_guidance_strength": 5.0,
            "texture_size": "1024",
            "future_param": True,
            "legacy_param": "old"
        }
        
        # Should not raise
        trellis_client.validate_params(trellis_params)
        result = trellis_client.prepare_input(image_url, trellis_params)
        assert "future_param" not in result
        assert "legacy_param" not in result
    
    # Missing Required Fields
    
    def test_process_image_no_file_path(self, tripo_client):
        """Test process_single_image without file_path raises error."""
        async def test_async():
            with pytest.raises(TypeError) as exc_info:
                await tripo_client.process_single_image(params={})
            assert "missing 1 required positional argument: 'file_path'" in str(exc_info.value)
        
        asyncio.run(test_async())
    
    def test_prepare_input_no_image_url(self, tripo_client):
        """Test prepare_input without image_url raises error."""
        with pytest.raises(TypeError) as exc_info:
            tripo_client.prepare_input(params={})
        assert "missing 1 required positional argument: 'image_url'" in str(exc_info.value)
    
    def test_submit_job_no_input_data(self, tripo_client):
        """Test submit_job without input_data raises error."""
        with pytest.raises(TypeError) as exc_info:
            tripo_client.submit_job()
        assert "missing 1 required positional argument: 'input_data'" in str(exc_info.value)
    
    # Mixed valid and invalid parameters
    
    def test_mixed_valid_invalid_params_tripo(self, tripo_client):
        """Test Tripo with mix of valid and invalid parameter values."""
        params = {
            "texture_enabled": True,  # Valid
            "face_limit": -100,  # Invalid value
        }
        
        with pytest.raises(ValueError) as exc_info:
            tripo_client.validate_params(params)
        assert "face_limit must be a positive integer" in str(exc_info.value)
    
    def test_mixed_valid_invalid_params_trellis(self, trellis_client):
        """Test Trellis with mix of valid and invalid parameter values."""
        params = {
            "ss_guidance_strength": 5.0,  # Valid
            "texture_size": "4096",  # Invalid value
            "mesh_simplify": 0.95,  # Valid
        }
        
        with pytest.raises(ValueError) as exc_info:
            trellis_client.validate_params(params)
        assert 'texture_size must be one of ["512", "1024", "2048"]' in str(exc_info.value)
    
    # Parameter type coercion attempts
    
    def test_numeric_string_params_tripo(self, tripo_client):
        """Test Tripo doesn't coerce string numbers to integers."""
        params = {"face_limit": "1000"}  # String instead of int
        
        with pytest.raises(ValueError) as exc_info:
            tripo_client.validate_params(params)
        assert "face_limit must be a positive integer" in str(exc_info.value)
    
    def test_numeric_params_trellis(self, trellis_client):
        """Test Trellis parameter type validation."""
        # String for float
        params = {"ss_guidance_strength": "7.5"}
        with pytest.raises(ValueError):
            trellis_client.validate_params(params)
        
        # Float for integer  
        params = {"ss_sampling_steps": 12.5}
        with pytest.raises(ValueError):
            trellis_client.validate_params(params)
        
        # Integer for string enum
        params = {"texture_size": 1024}
        with pytest.raises(ValueError):
            trellis_client.validate_params(params)
    
    # Null and undefined handling
    
    def test_null_param_values_tripo(self, tripo_client):
        """Test Tripo handles null parameter values."""
        image_url = "https://fal.ai/uploads/test.png"
        params = {
            "texture_enabled": None,  # Should cause validation error
            "face_limit": None  # Allowed - None is valid
        }
        
        # texture_enabled None should fail validation
        with pytest.raises(ValueError):
            tripo_client.validate_params({"texture_enabled": None})
        
        # face_limit None is allowed
        tripo_client.validate_params({"face_limit": None})
        result = tripo_client.prepare_input(image_url, {"face_limit": None})
        assert "face_limit" not in result
    
    def test_special_values_trellis(self, trellis_client):
        """Test Trellis handles special values."""
        # Test extreme but valid values
        params = {
            "ss_guidance_strength": 0.0,  # Min value
            "ss_sampling_steps": 50,  # Max value
            "mesh_simplify": 0.9,  # Min value
        }
        
        # Should pass validation
        trellis_client.validate_params(params)
        
        # Test slightly out of range
        params = {"mesh_simplify": 0.8999999}
        with pytest.raises(ValueError):
            trellis_client.validate_params(params)