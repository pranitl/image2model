"""
Unit tests for FAL client factory functions.
"""

import pytest
from unittest.mock import patch

from app.workers.fal_client import (
    get_model_client,
    get_available_models,
    TripoClient,
    TrellisClient,
    FalAIClient
)


class TestFalClientFactory:
    """Test cases for factory functions and model discovery."""
    
    def test_get_model_client_tripo(self):
        """Test factory returns TripoClient for tripo3d."""
        with patch("app.core.config.settings.FAL_API_KEY", "test-key"):
            client = get_model_client("tripo3d")
            assert isinstance(client, TripoClient)
            assert client.model_endpoint == "tripo3d/tripo/v2.5/image-to-3d"
    
    def test_get_model_client_trellis(self):
        """Test factory returns TrellisClient for trellis."""
        with patch("app.core.config.settings.FAL_API_KEY", "test-key"):
            client = get_model_client("trellis")
            assert isinstance(client, TrellisClient)
            assert client.model_endpoint == "fal-ai/trellis"
    
    def test_get_model_client_invalid(self):
        """Test factory raises ValueError for unknown model."""
        with pytest.raises(ValueError) as exc_info:
            get_model_client("unknown_model")
        assert "Unsupported model type: unknown_model" in str(exc_info.value)
    
    def test_get_available_models_structure(self):
        """Test get_available_models returns correct structure."""
        models = get_available_models()
        
        assert isinstance(models, list)
        assert len(models) >= 2  # At least Tripo and Trellis
        
        # Check structure of each model
        for model in models:
            assert isinstance(model, dict)
            assert "name" in model
            assert "description" in model
            assert "type" in model
            assert "supported_formats" in model
            assert "default_params" in model
            assert "param_schema" in model
    
    def test_get_available_models_content(self):
        """Test get_available_models contains expected models."""
        models = get_available_models()
        model_names = [m["name"] for m in models]
        
        assert "tripo3d" in model_names
        assert "trellis" in model_names
        
        # Find specific models and verify content
        tripo_model = next(m for m in models if m["name"] == "tripo3d")
        assert tripo_model["type"] == "image_to_3d"
        assert "glb" in tripo_model["supported_formats"]
        assert tripo_model["default_params"]["texture_enabled"] is True
        
        trellis_model = next(m for m in models if m["name"] == "trellis")
        assert trellis_model["type"] == "image_to_3d"
        assert "glb" in trellis_model["supported_formats"]
        assert trellis_model["default_params"]["ss_guidance_strength"] == 7.5
    
    def test_legacy_fal_ai_client_compatibility(self):
        """Test that FalAIClient is aliased to TripoClient for backward compatibility."""
        with patch("app.core.config.settings.FAL_API_KEY", "test-key"):
            client = FalAIClient()
            assert isinstance(client, TripoClient)
            assert client.model_endpoint == "tripo3d/tripo/v2.5/image-to-3d"
    
    def test_model_info_completeness(self):
        """Test that all models have complete MODEL_INFO."""
        models = get_available_models()
        
        for model in models:
            # Check required fields
            assert model["name"]
            assert model["description"]
            assert model["type"]
            assert isinstance(model["supported_formats"], list)
            assert len(model["supported_formats"]) > 0
            assert isinstance(model["default_params"], dict)
            assert isinstance(model["param_schema"], dict)
            
            # Check param schema structure
            for param_name, param_info in model["param_schema"].items():
                assert "type" in param_info
                assert "description" in param_info
                # Some params should have default values
                if param_name in model["default_params"]:
                    if "default" in param_info:
                        assert param_info["default"] == model["default_params"][param_name]
    
    def test_factory_creates_independent_instances(self):
        """Test that factory creates new instances each time."""
        with patch("app.core.config.settings.FAL_API_KEY", "test-key"):
            client1 = get_model_client("tripo3d")
            client2 = get_model_client("tripo3d")
            
            assert client1 is not client2
            assert client1._processed_log_timestamps is not client2._processed_log_timestamps
    
    def test_get_available_models_returns_copy(self):
        """Test that get_available_models returns copies, not references."""
        models1 = get_available_models()
        models2 = get_available_models()
        
        # Modify first result
        models1[0]["name"] = "modified"
        
        # Second result should be unaffected
        assert models2[0]["name"] != "modified"