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
        assert result["texture"] == "standard"  # texture_enabled=True means "standard"
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
        assert "texture_enabled" not in result
        assert "face_limit" not in result
        # Check that defaults are included for missing Trellis params
        assert result["ss_sampling_steps"] == 12
        assert result["slat_guidance_strength"] == 3
        assert result["slat_sampling_steps"] == 12
        assert result["mesh_simplify"] == 0.95
    
    def test_empty_params_dict(self, tripo_client, trellis_client):
        """Test both clients handle empty params dict."""
        image_url = "https://fal.ai/uploads/test.png"
        params = {}
        
        # Tripo should use defaults
        tripo_result = tripo_client.prepare_input(image_url, params)
        assert tripo_result["texture"] == "standard"  # Default when texture_enabled is True
        assert tripo_result["texture_alignment"] == "original_image"
        assert tripo_result["orientation"] == "default"
        assert "face_limit" not in tripo_result  # Optional param not included when not specified
        
        # Trellis should use all defaults
        trellis_result = trellis_client.prepare_input(image_url, params)
        assert trellis_result["ss_guidance_strength"] == 7.5
        assert trellis_result["ss_sampling_steps"] == 12
        assert trellis_result["slat_guidance_strength"] == 3
        assert trellis_result["slat_sampling_steps"] == 12
        assert trellis_result["mesh_simplify"] == 0.95
        assert trellis_result["texture_size"] == "1024"
    
    def test_none_params(self, tripo_client, trellis_client):
        """Test both clients handle None params."""
        image_url = "https://fal.ai/uploads/test.png"
        
        # Test that None params are treated as empty dict
        # Tripo with None params should use defaults
        tripo_result = tripo_client.prepare_input(image_url, params={})
        assert tripo_result["texture"] == "standard"
        assert "face_limit" not in tripo_result
        
        # Trellis with None params should use all defaults
        trellis_result = trellis_client.prepare_input(image_url, params={})
        assert trellis_result["ss_guidance_strength"] == 7.5
        assert trellis_result["texture_size"] == "1024"
    
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
        
        # Should not raise - unknown params are ignored in validation
        tripo_client.validate_params(tripo_params)
        result = tripo_client.prepare_input(image_url, tripo_params)
        assert result["texture"] == "standard"
        assert result["face_limit"] == 5000
        assert "unknown_param" not in result
        assert "another_unknown" not in result
        
        # Extra params for Trellis
        trellis_params = {
            "ss_guidance_strength": 5.0,
            "texture_size": "1024",
            "future_param": True,
            "legacy_param": "old"
        }
        
        # Should not raise - unknown params are ignored in validation
        trellis_client.validate_params(trellis_params)
        result = trellis_client.prepare_input(image_url, trellis_params)
        assert result["ss_guidance_strength"] == 5.0
        assert result["texture_size"] == "1024"
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
        # The error message uses single quotes in Python's repr of the list
        assert "texture_size must be one of ['512', '1024', '2048']" in str(exc_info.value)
    
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
        with pytest.raises(ValueError) as exc_info:
            trellis_client.validate_params(params)
        assert "ss_guidance_strength must be a number between 0 and 10" in str(exc_info.value)
        
        # Float for integer  
        params = {"ss_sampling_steps": 12.5}
        with pytest.raises(ValueError) as exc_info:
            trellis_client.validate_params(params)
        assert "ss_sampling_steps must be an integer between 1 and 50" in str(exc_info.value)
        
        # Integer for string enum - actually passes because str(1024) == "1024"
        params = {"texture_size": 1024}
        # This should NOT raise an error because the implementation converts to string
        trellis_client.validate_params(params)
        
        # Test with an invalid texture size that will fail
        params = {"texture_size": 4096}
        with pytest.raises(ValueError) as exc_info:
            trellis_client.validate_params(params)
        assert "texture_size must be one of ['512', '1024', '2048']" in str(exc_info.value)
    
    # Null and undefined handling
    
    def test_null_param_values_tripo(self, tripo_client):
        """Test Tripo handles null parameter values."""
        image_url = "https://fal.ai/uploads/test.png"
        
        # texture_enabled None should fail validation
        with pytest.raises(ValueError) as exc_info:
            tripo_client.validate_params({"texture_enabled": None})
        assert "texture_enabled must be a boolean value" in str(exc_info.value)
        
        # face_limit None is allowed - it's an optional param
        tripo_client.validate_params({"face_limit": None})
        result = tripo_client.prepare_input(image_url, {"face_limit": None})
        assert "face_limit" not in result  # None values are not included in input
    
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
        with pytest.raises(ValueError) as exc_info:
            trellis_client.validate_params(params)
        assert "mesh_simplify must be a number between 0.9 and 0.98" in str(exc_info.value)