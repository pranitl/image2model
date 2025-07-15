"""
Tests for handling malformed FAL.AI responses.
"""

import pytest
from unittest.mock import patch, Mock

from app.workers.fal_client import (
    TripoClient,
    TrellisClient,
    FalAIAPIError
)
from tests.mocks.fal_responses import MALFORMED_RESPONSES, TRIPO_SUCCESS


class TestMalformedResponses:
    """Test cases for handling malformed FAL.AI responses."""
    
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
    
    def test_response_missing_model_mesh(self, tripo_client):
        """Test handling response with no model_mesh key."""
        response = MALFORMED_RESPONSES["missing_model_mesh"]
        
        result = tripo_client._process_result(
            response,
            "test.png",
            progress_callback=None,
            job_id="test-job"
        )
        
        assert result["status"] == "failed"
        assert result["error"] == "No model_mesh.url in API response"
        assert result["input"] == "test.png"
    
    def test_response_missing_url_in_model_mesh(self, trellis_client):
        """Test handling model_mesh without url field."""
        response = MALFORMED_RESPONSES["missing_url"]
        
        result = trellis_client._process_result(
            response,
            "test.png",
            progress_callback=None,
            job_id="test-job"
        )
        
        assert result["status"] == "failed"
        assert result["error"] == "No model_mesh.url in API response"
    
    def test_response_null_url(self, tripo_client):
        """Test handling response with null URL value."""
        response = MALFORMED_RESPONSES["null_url"]
        
        result = tripo_client._process_result(
            response,
            "test.png",
            progress_callback=None,
            job_id="test-job"
        )
        
        assert result["status"] == "failed"
        assert result["error"] == "No model_mesh.url in API response"
    
    def test_response_empty_url(self, trellis_client):
        """Test handling response with empty string URL."""
        response = MALFORMED_RESPONSES["empty_url"]
        
        result = trellis_client._process_result(
            response,
            "test.png",
            progress_callback=None,
            job_id="test-job"
        )
        
        assert result["status"] == "failed"
        assert result["error"] == "No model_mesh.url in API response"
    
    def test_response_completely_empty(self, tripo_client):
        """Test handling completely empty response dict."""
        response = MALFORMED_RESPONSES["empty_response"]
        
        result = tripo_client._process_result(
            response,
            "test.png",
            progress_callback=None,
            job_id="test-job"
        )
        
        assert result["status"] == "failed"
        assert result["error"] == "No model_mesh.url in API response"
    
    def test_response_wrong_structure(self, trellis_client):
        """Test handling response with unexpected structure."""
        response = MALFORMED_RESPONSES["wrong_structure"]
        
        result = trellis_client._process_result(
            response,
            "test.png",
            progress_callback=None,
            job_id="test-job"
        )
        
        assert result["status"] == "failed"
        assert "No model_mesh.url in API response" in result["error"]
    
    def test_response_partial_data(self, tripo_client):
        """Test handling response with only some fields present."""
        response = MALFORMED_RESPONSES["partial_data"]
        
        result = tripo_client._process_result(
            response,
            "test.png",
            progress_callback=None,
            job_id="test-job"
        )
        
        # Should succeed with available data
        assert result["status"] == "success"
        assert result["download_url"] == response["model_mesh"]["url"]
        assert result["file_size"] == 0  # Default when missing
        assert result["content_type"] == "application/octet-stream"  # Default
    
    def test_response_with_error_field(self, trellis_client):
        """Test handling response that indicates an error."""
        response = {
            "error": "Processing failed",
            "message": "Unable to generate 3D model"
        }
        
        # When submit_job receives error response, it should handle it
        with patch.object(trellis_client, 'submit_job') as mock_submit:
            mock_submit.return_value = response
            
            # Process should detect error in response
            result = trellis_client._process_result(
                response,
                "test.png",
                progress_callback=None,
                job_id="test-job"
            )
            
            assert result["status"] == "failed"
    
    def test_response_invalid_json_types(self, tripo_client):
        """Test handling response with wrong data types."""
        response = MALFORMED_RESPONSES["invalid_types"]
        
        # Even with invalid types, we should handle gracefully
        result = tripo_client._process_result(
            response,
            "test.png", 
            progress_callback=None,
            job_id="test-job"
        )
        
        # URL is wrong type (int), should fail
        assert result["status"] == "failed"
        assert "No model_mesh.url in API response" in result["error"]
    
    def test_response_extremely_large_values(self, trellis_client):
        """Test handling response with extremely large file sizes."""
        response = MALFORMED_RESPONSES["extremely_large_file"]
        
        result = trellis_client._process_result(
            response,
            "test.png",
            progress_callback=None,
            job_id="test-job"
        )
        
        # Should handle large values without error
        assert result["status"] == "success"
        assert result["file_size"] == 2147483648  # 2GB
    
    def test_response_missing_optional_fields(self, tripo_client):
        """Test that missing optional fields don't cause failure."""
        response = {
            "model_mesh": {
                "url": "https://fal.media/files/model.glb",
                "file_size": 1000000,
                "content_type": "model/gltf-binary"
            }
            # Missing: rendered_image, task_id, file_name
        }
        
        result = tripo_client._process_result(
            response,
            "test.png",
            progress_callback=None,
            job_id="test-job"
        )
        
        assert result["status"] == "success"
        assert result["download_url"] == response["model_mesh"]["url"]
        assert "rendered_image" not in result  # Optional field
        assert result["task_id"] is None  # Default when missing
    
    def test_response_additional_unexpected_fields(self, trellis_client):
        """Test that extra fields in response are handled gracefully."""
        response = {
            "model_mesh": {
                "url": "https://fal.media/files/model.glb",
                "file_size": 1000000,
                "content_type": "model/gltf-binary",
                "unexpected_field": "value",
                "another_extra": 123
            },
            "extra_data": {"key": "value"},
            "unused_field": True
        }
        
        result = trellis_client._process_result(
            response,
            "test.png",
            progress_callback=None,
            job_id="test-job"
        )
        
        # Should succeed and ignore extra fields
        assert result["status"] == "success"
        assert result["download_url"] == response["model_mesh"]["url"]
    
    def test_submit_job_malformed_response(self, tripo_client, mock_fal_subscribe):
        """Test submit_job handling of malformed responses."""
        # Configure mock to return malformed response
        mock_fal_subscribe.response_type = "missing_model_mesh"
        
        result = tripo_client.submit_job({"image_url": "test.png"})
        
        # Should return the malformed response as-is
        assert result == MALFORMED_RESPONSES["missing_model_mesh"]
    
    def test_process_result_with_progress_callback(self, trellis_client):
        """Test that progress callback is called even with malformed response."""
        progress_calls = []
        def progress_callback(message, percent):
            progress_calls.append((message, percent))
        
        # Test with successful response first
        result = trellis_client._process_result(
            TRIPO_SUCCESS,
            "test.png",
            progress_callback=progress_callback,
            job_id="test-job"
        )
        
        assert len(progress_calls) > 0
        assert progress_calls[-1][1] == 100  # Final progress should be 100%
    
    def test_edge_case_model_mesh_not_dict(self, tripo_client):
        """Test handling when model_mesh is not a dictionary."""
        response = {
            "model_mesh": "https://fal.media/files/model.glb"  # String instead of dict
        }
        
        result = tripo_client._process_result(
            response,
            "test.png",
            progress_callback=None,
            job_id="test-job"
        )
        
        assert result["status"] == "failed"
        assert "Result processing failed" in result["error"]
    
    def test_exception_during_processing(self, trellis_client):
        """Test exception handling during result processing."""
        # Create a response that will cause an exception
        response = {
            "model_mesh": {
                "url": "https://fal.media/files/model.glb",
                "file_size": "not_a_number"  # This might cause issues
            }
        }
        
        # Mock something that will definitely raise
        with patch.object(trellis_client, '_process_result') as mock_process:
            mock_process.side_effect = Exception("Unexpected error")
            
            # The actual method catches exceptions and returns error result
            client = TrellisClient()
            result = client._process_result(
                response,
                "test.png",
                progress_callback=None,
                job_id="test-job"
            )
            
            assert result["status"] == "failed"
            assert "Result processing failed" in result["error"]