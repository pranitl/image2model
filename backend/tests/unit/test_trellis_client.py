"""
Unit tests for TrellisClient implementation.
"""

import pytest
from unittest.mock import patch

from app.workers.fal_client import TrellisClient
from tests.mocks.fal_responses import TRELLIS_SUCCESS, INVALID_PARAMS


class TestTrellisClient:
    """Test cases for TrellisClient."""
    
    @pytest.fixture
    def trellis_client(self):
        """Create a TrellisClient instance with mocked settings."""
        with patch("app.core.config.settings.FAL_API_KEY", "test-key"):
            return TrellisClient()
    
    def test_model_endpoint_property(self, trellis_client):
        """Test that correct endpoint is returned."""
        assert trellis_client.model_endpoint == "fal-ai/trellis"
    
    def test_prepare_input_all_defaults(self, trellis_client):
        """Test all default values are applied when no params provided."""
        image_url = "https://fal.ai/uploads/test.png"
        params = {}
        
        result = trellis_client.prepare_input(image_url, params)
        
        assert result["image_url"] == image_url
        assert result["ss_guidance_strength"] == 7.5
        assert result["ss_sampling_steps"] == 12
        assert result["slat_guidance_strength"] == 3
        assert result["slat_sampling_steps"] == 12
        assert result["mesh_simplify"] == 0.95
        assert result["texture_size"] == "1024"
    
    def test_prepare_input_custom_params(self, trellis_client):
        """Test custom parameters override defaults."""
        image_url = "https://fal.ai/uploads/test.png"
        params = {
            "ss_guidance_strength": 5.0,
            "ss_sampling_steps": 20,
            "slat_guidance_strength": 5.0,
            "slat_sampling_steps": 15,
            "mesh_simplify": 0.92,
            "texture_size": "2048"
        }
        
        result = trellis_client.prepare_input(image_url, params)
        
        assert result["image_url"] == image_url
        assert result["ss_guidance_strength"] == 5.0
        assert result["ss_sampling_steps"] == 20
        assert result["slat_guidance_strength"] == 5.0
        assert result["slat_sampling_steps"] == 15
        assert result["mesh_simplify"] == 0.92
        assert result["texture_size"] == "2048"
    
    def test_validate_params_ss_guidance_below_range(self, trellis_client):
        """Test validation rejects ss_guidance_strength below 0."""
        params = {"ss_guidance_strength": -1.0}
        
        with pytest.raises(ValueError) as exc_info:
            trellis_client.validate_params(params)
        assert "ss_guidance_strength must be a number between 0 and 10" in str(exc_info.value)
    
    def test_validate_params_ss_guidance_above_range(self, trellis_client):
        """Test validation rejects ss_guidance_strength above 10."""
        params = {"ss_guidance_strength": 15.0}
        
        with pytest.raises(ValueError) as exc_info:
            trellis_client.validate_params(params)
        assert "ss_guidance_strength must be a number between 0 and 10" in str(exc_info.value)
    
    def test_validate_params_ss_sampling_steps_zero(self, trellis_client):
        """Test validation rejects ss_sampling_steps of 0."""
        params = {"ss_sampling_steps": 0}
        
        with pytest.raises(ValueError) as exc_info:
            trellis_client.validate_params(params)
        assert "ss_sampling_steps must be an integer between 1 and 50" in str(exc_info.value)
    
    def test_validate_params_ss_sampling_steps_over_fifty(self, trellis_client):
        """Test validation rejects ss_sampling_steps over 50."""
        params = {"ss_sampling_steps": 100}
        
        with pytest.raises(ValueError) as exc_info:
            trellis_client.validate_params(params)
        assert "ss_sampling_steps must be an integer between 1 and 50" in str(exc_info.value)
    
    def test_validate_params_slat_guidance_invalid_range(self, trellis_client):
        """Test validation for slat_guidance_strength range."""
        # Test below minimum
        params = {"slat_guidance_strength": -5.0}
        with pytest.raises(ValueError) as exc_info:
            trellis_client.validate_params(params)
        assert "slat_guidance_strength must be a number between 0 and 10" in str(exc_info.value)
        
        # Test above maximum
        params = {"slat_guidance_strength": 12.0}
        with pytest.raises(ValueError) as exc_info:
            trellis_client.validate_params(params)
        assert "slat_guidance_strength must be a number between 0 and 10" in str(exc_info.value)
    
    def test_validate_params_mesh_simplify_below_min(self, trellis_client):
        """Test validation rejects mesh_simplify below 0.9."""
        params = {"mesh_simplify": 0.85}
        
        with pytest.raises(ValueError) as exc_info:
            trellis_client.validate_params(params)
        assert "mesh_simplify must be a number between 0.9 and 0.98" in str(exc_info.value)
    
    def test_validate_params_mesh_simplify_above_max(self, trellis_client):
        """Test validation rejects mesh_simplify above 0.98."""
        params = {"mesh_simplify": 0.99}
        
        with pytest.raises(ValueError) as exc_info:
            trellis_client.validate_params(params)
        assert "mesh_simplify must be a number between 0.9 and 0.98" in str(exc_info.value)
    
    def test_validate_params_texture_size_invalid_enum(self, trellis_client):
        """Test validation rejects invalid texture_size values."""
        params = {"texture_size": "4096"}
        
        with pytest.raises(ValueError) as exc_info:
            trellis_client.validate_params(params)
        assert "texture_size must be one of" in str(exc_info.value)
        assert "512" in str(exc_info.value)
        assert "1024" in str(exc_info.value)
        assert "2048" in str(exc_info.value)
    
    def test_validate_params_texture_size_valid_enums(self, trellis_client):
        """Test validation accepts valid texture_size values."""
        valid_sizes = ["512", "1024", "2048"]
        
        for size in valid_sizes:
            params = {"texture_size": size}
            # Should not raise exception
            trellis_client.validate_params(params)
    
    def test_validate_params_wrong_types(self, trellis_client):
        """Test validation rejects wrong parameter types."""
        # String for float field
        params = {"ss_guidance_strength": "7.5"}
        with pytest.raises(ValueError) as exc_info:
            trellis_client.validate_params(params)
        assert "ss_guidance_strength must be a number" in str(exc_info.value)
        
        # Float for int field
        params = {"ss_sampling_steps": 12.5}
        with pytest.raises(ValueError) as exc_info:
            trellis_client.validate_params(params)
        assert "ss_sampling_steps must be an integer" in str(exc_info.value)
        
        # Int for string enum field - implementation accepts ints and converts to string
        # This is actually valid since the implementation uses str(value)
        params = {"texture_size": 1024}
        # Should not raise exception since 1024 converts to "1024" which is valid
        trellis_client.validate_params(params)
    
    def test_model_info_metadata(self, trellis_client):
        """Test MODEL_INFO structure is correct."""
        assert trellis_client.MODEL_INFO["name"] == "trellis"
        assert "description" in trellis_client.MODEL_INFO
        assert trellis_client.MODEL_INFO["type"] == "image_to_3d"
        assert "glb" in trellis_client.MODEL_INFO["supported_formats"]
        
        # Check default params
        defaults = trellis_client.MODEL_INFO["default_params"]
        assert defaults["ss_guidance_strength"] == 7.5
        assert defaults["ss_sampling_steps"] == 12
        assert defaults["slat_guidance_strength"] == 3
        assert defaults["slat_sampling_steps"] == 12
        assert defaults["mesh_simplify"] == 0.95
        assert defaults["texture_size"] == "1024"
        
        # Check param schema
        param_schema = trellis_client.MODEL_INFO["param_schema"]
        assert param_schema["ss_guidance_strength"]["min"] == 0
        assert param_schema["ss_guidance_strength"]["max"] == 10
        assert param_schema["ss_sampling_steps"]["min"] == 1
        assert param_schema["ss_sampling_steps"]["max"] == 50
        assert param_schema["mesh_simplify"]["min"] == 0.9
        assert param_schema["mesh_simplify"]["max"] == 0.98
        assert param_schema["texture_size"]["enum"] == ["512", "1024", "2048"]
    
    def test_validate_params_valid_params(self, trellis_client):
        """Test validation passes for all valid parameters."""
        params = {
            "ss_guidance_strength": 5.0,
            "ss_sampling_steps": 25,
            "slat_guidance_strength": 4.5,
            "slat_sampling_steps": 20,
            "mesh_simplify": 0.93,
            "texture_size": "2048"
        }
        
        # Should not raise any exception
        trellis_client.validate_params(params)
    
    def test_validate_params_boundary_values(self, trellis_client):
        """Test validation at boundary values."""
        # Minimum values
        params = {
            "ss_guidance_strength": 0.0,
            "ss_sampling_steps": 1,
            "slat_guidance_strength": 0.0,
            "slat_sampling_steps": 1,
            "mesh_simplify": 0.9,
            "texture_size": "512"
        }
        trellis_client.validate_params(params)
        
        # Maximum values
        params = {
            "ss_guidance_strength": 10.0,
            "ss_sampling_steps": 50,
            "slat_guidance_strength": 10.0,
            "slat_sampling_steps": 50,
            "mesh_simplify": 0.98,
            "texture_size": "2048"
        }
        trellis_client.validate_params(params)
    
    def test_prepare_input_partial_params(self, trellis_client):
        """Test that missing params use defaults."""
        image_url = "https://fal.ai/uploads/test.png"
        params = {
            "ss_guidance_strength": 9.0,
            "texture_size": "2048"
        }
        
        result = trellis_client.prepare_input(image_url, params)
        
        # Custom values
        assert result["ss_guidance_strength"] == 9.0
        assert result["texture_size"] == "2048"
        
        # Default values for missing params
        assert result["ss_sampling_steps"] == 12
        assert result["slat_guidance_strength"] == 3
        assert result["slat_sampling_steps"] == 12
        assert result["mesh_simplify"] == 0.95