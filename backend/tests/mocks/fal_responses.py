"""
Mock FAL.AI API responses for testing.

These mock responses are based on the actual FAL.AI API documentation
for both Tripo3D and Trellis models.
"""

import json

# Tripo3D Success Response (based on actual API structure from tripo-llms.md)
TRIPO_SUCCESS = {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "model_mesh": {
        "url": "https://v3.fal.media/files/zebra/NA4WkhbpI-XdOIFc4cDIk_tripo_model_812c3a8a-6eb3-4c09-9f40-0563d27ae7ea.glb",
        "file_size": 6744644,
        "content_type": "application/octet-stream",
        "file_name": "abc123_model.glb"
    },
    "rendered_image": {
        "url": "https://v3.fal.media/files/panda/zDTAHqp8ifMOT3upZ1xJv_legacy.webp",
        "file_size": 13718,
        "content_type": "image/webp"
    },
    # Additional fields that might be present based on parameters
    "base_model": None,  # Only when pbr=false
    "pbr_model": None    # Only when pbr=true
}

# Trellis Success Response (based on actual API structure from trellis-llms.md)
TRELLIS_SUCCESS = {
    "model_mesh": {
        "url": "https://fal.media/files/zebra/xyz789_model.glb",
        "file_size": 5123456,
        "content_type": "image/png",  # Based on the example showing content_type as image/png
        "file_name": "z9RV14K95DvU.png"
    },
    "timings": {
        "inference": 45.2
    }
}

# Malformed responses for edge case testing
MALFORMED_RESPONSES = {
    "missing_model_mesh": {
        "task_id": "123",
        "rendered_image": {
            "url": "https://fal.media/files/preview.webp"
        }
    },
    "missing_url": {
        "model_mesh": {
            "file_size": 1000,
            "content_type": "model/gltf-binary"
        }
    },
    "empty_response": {},
    "null_url": {
        "model_mesh": {
            "url": None,
            "file_size": 1000
        }
    },
    "empty_url": {
        "model_mesh": {
            "url": "",
            "file_size": 1000
        }
    },
    "wrong_structure": {
        "data": {
            "model": {
                "link": "https://fal.media/files/model.glb"
            }
        }
    },
    "partial_data": {
        "model_mesh": {
            "url": "https://fal.media/files/partial.glb"
            # Missing file_size, content_type
        }
    },
    "invalid_types": {
        "model_mesh": {
            "url": 12345,  # Should be string
            "file_size": "large",  # Should be int
            "content_type": None
        }
    },
    "extremely_large_file": {
        "model_mesh": {
            "url": "https://fal.media/files/huge.glb",
            "file_size": 2147483648,  # 2GB
            "content_type": "model/gltf-binary"
        }
    }
}

# Error responses based on fal.ai documentation
ERROR_RESPONSES = {
    # Rate limiting error
    "rate_limit": {
        "detail": [{
            "loc": ["body"],
            "msg": "Rate limit exceeded",
            "type": "rate_limit_exceeded",
            "url": "https://docs.fal.ai/errors/#rate_limit_exceeded"
        }],
        "status_code": 429,
        "headers": {"X-Fal-Retryable": "true"}
    },
    
    # Authentication error
    "authentication": {
        "detail": [{
            "loc": ["body"],
            "msg": "Invalid API key",
            "type": "unauthorized",
            "url": "https://docs.fal.ai/errors/#unauthorized"
        }],
        "status_code": 401,
        "headers": {"X-Fal-Retryable": "false"}
    },
    
    # Timeout errors
    "generation_timeout": {
        "detail": [{
            "loc": ["body"],
            "msg": "Generation timeout",
            "type": "generation_timeout",
            "url": "https://docs.fal.ai/errors/#generation_timeout",
            "input": {"image_url": "https://example.com/image.jpg"}
        }],
        "status_code": 504,
        "headers": {"X-Fal-Retryable": "true"}
    },
    
    # Server errors
    "internal_server_error": {
        "detail": [{
            "loc": ["body"],
            "msg": "Internal server error",
            "type": "internal_server_error",
            "url": "https://docs.fal.ai/errors/#internal_server_error",
            "input": {"image_url": "https://example.com/image.jpg"}
        }],
        "status_code": 500,
        "headers": {"X-Fal-Retryable": "true"}
    },
    
    # Downstream service errors
    "downstream_service_error": {
        "detail": [{
            "loc": ["body"],
            "msg": "Downstream service error",
            "type": "downstream_service_error",
            "url": "https://docs.fal.ai/errors/#downstream_service_error"
        }],
        "status_code": 400,
        "headers": {"X-Fal-Retryable": "true"}
    },
    
    "downstream_service_unavailable": {
        "detail": [{
            "loc": ["body"],
            "msg": "Downstream service unavailable",
            "type": "downstream_service_unavailable",
            "url": "https://docs.fal.ai/errors/#downstream_service_unavailable"
        }],
        "status_code": 500,
        "headers": {"X-Fal-Retryable": "true"}
    },
    
    # Content policy violation
    "content_policy_violation": {
        "detail": [{
            "loc": ["body", "image_url"],
            "msg": "The content could not be processed because it contained material flagged by a content checker.",
            "type": "content_policy_violation",
            "url": "https://docs.fal.ai/errors/#content_policy_violation",
            "input": "https://example.com/forbidden.jpg"
        }],
        "status_code": 422,
        "headers": {"X-Fal-Retryable": "false"}
    },
    
    # Image validation errors
    "image_too_small": {
        "detail": [{
            "loc": ["body", "image_url"],
            "msg": "Image too small",
            "type": "image_too_small",
            "url": "https://docs.fal.ai/errors/#image_too_small",
            "ctx": {
                "min_height": 512,
                "min_width": 512
            },
            "input": "https://example.com/tiny_image.jpg"
        }],
        "status_code": 422,
        "headers": {"X-Fal-Retryable": "false"}
    },
    
    "image_too_large": {
        "detail": [{
            "loc": ["body", "image_url"],
            "msg": "Image too large",
            "type": "image_too_large",
            "url": "https://docs.fal.ai/errors/#image_too_large",
            "ctx": {
                "max_height": 4096,
                "max_width": 4096
            },
            "input": "https://example.com/huge_image.jpg"
        }],
        "status_code": 422,
        "headers": {"X-Fal-Retryable": "false"}
    },
    
    "image_load_error": {
        "detail": [{
            "loc": ["body", "image_url"],
            "msg": "Image load error",
            "type": "image_load_error",
            "url": "https://docs.fal.ai/errors/#image_load_error",
            "input": "https://example.com/corrupted.jpg"
        }],
        "status_code": 422,
        "headers": {"X-Fal-Retryable": "false"}
    },
    
    "file_download_error": {
        "detail": [{
            "loc": ["body", "image_url"],
            "msg": "File download error",
            "type": "file_download_error",
            "url": "https://docs.fal.ai/errors/#file_download_error",
            "input": "https://private-server.com/image.jpg"
        }],
        "status_code": 422,
        "headers": {"X-Fal-Retryable": "false"}
    },
    
    "unsupported_image_format": {
        "detail": [{
            "loc": ["body", "image_url"],
            "msg": "Unsupported image format. Supported formats are .jpg, .jpeg, .png, .webp.",
            "type": "unsupported_image_format",
            "url": "https://docs.fal.ai/errors/#unsupported_image_format",
            "ctx": {
                "supported_formats": [".jpg", ".jpeg", ".png", ".webp"]
            },
            "input": "https://example.com/image.tiff"
        }],
        "status_code": 422,
        "headers": {"X-Fal-Retryable": "false"}
    },
    
    # Parameter validation errors
    "greater_than": {
        "detail": [{
            "loc": ["body", "face_limit"],
            "msg": "Input should be greater than 0",
            "type": "greater_than",
            "url": "https://docs.fal.ai/errors/#greater_than",
            "ctx": {"gt": 0},
            "input": 0
        }],
        "status_code": 422,
        "headers": {"X-Fal-Retryable": "false"}
    },
    
    "greater_than_equal": {
        "detail": [{
            "loc": ["body", "ss_guidance_strength"],
            "msg": "Input should be greater than or equal to 0",
            "type": "greater_than_equal",
            "url": "https://docs.fal.ai/errors/#greater_than_equal",
            "ctx": {"ge": 0},
            "input": -0.5
        }],
        "status_code": 422,
        "headers": {"X-Fal-Retryable": "false"}
    },
    
    "less_than_equal": {
        "detail": [{
            "loc": ["body", "ss_guidance_strength"],
            "msg": "Input should be less than or equal to 10",
            "type": "less_than_equal",
            "url": "https://docs.fal.ai/errors/#less_than_equal",
            "ctx": {"le": 10},
            "input": 11
        }],
        "status_code": 422,
        "headers": {"X-Fal-Retryable": "false"}
    },
    
    "one_of": {
        "detail": [{
            "loc": ["body", "texture_size"],
            "msg": "Input should be '512', '1024' or '2048'",
            "type": "one_of",
            "url": "https://docs.fal.ai/errors/#one_of",
            "ctx": {"expected": ["512", "1024", "2048"]},
            "input": "4096"
        }],
        "status_code": 422,
        "headers": {"X-Fal-Retryable": "false"}
    },
    
    # Legacy simple format for backward compatibility
    "simple_rate_limit": {
        "error": "Rate limit exceeded",
        "message": "Too many requests. Please try again later.",
        "status_code": 429
    },
    
    "simple_server_error": {
        "error": "Internal server error",
        "message": "An unexpected error occurred",
        "status_code": 500
    }
}

# FAL.AI InProgress update objects for progress tracking
PROGRESS_UPDATES = {
    "upload": {
        "logs": [{
            "message": "Uploading image to FAL.AI...",
            "timestamp": "2024-01-10T10:00:00.000Z",
            "level": "info"
        }]
    },
    "processing_start": {
        "logs": [{
            "message": "Starting 3D model generation...",
            "timestamp": "2024-01-10T10:00:05.000Z",
            "level": "info"
        }]
    },
    "processing_25": {
        "logs": [{
            "message": "Progress: 25% - Analyzing image features",
            "timestamp": "2024-01-10T10:00:10.000Z",
            "level": "info"
        }]
    },
    "processing_50": {
        "logs": [{
            "message": "Progress: 50% - Generating 3D mesh",
            "timestamp": "2024-01-10T10:00:20.000Z",
            "level": "info"
        }]
    },
    "processing_75": {
        "logs": [{
            "message": "Progress: 75% - Applying textures",
            "timestamp": "2024-01-10T10:00:30.000Z",
            "level": "info"
        }]
    },
    "processing_90": {
        "logs": [{
            "message": "Progress: 90% - Finalizing model",
            "timestamp": "2024-01-10T10:00:40.000Z",
            "level": "info"
        }]
    }
}

# Parameter validation test cases
INVALID_PARAMS = {
    "tripo_invalid_texture": {
        "texture_enabled": "yes"  # Should be boolean
    },
    "tripo_negative_face_limit": {
        "face_limit": -100
    },
    "tripo_zero_face_limit": {
        "face_limit": 0
    },
    "tripo_string_face_limit": {
        "face_limit": "1000"
    },
    "trellis_ss_guidance_negative": {
        "ss_guidance_strength": -1.0
    },
    "trellis_ss_guidance_over_max": {
        "ss_guidance_strength": 15.0
    },
    "trellis_ss_steps_zero": {
        "ss_sampling_steps": 0
    },
    "trellis_ss_steps_over_max": {
        "ss_sampling_steps": 100
    },
    "trellis_mesh_simplify_under_min": {
        "mesh_simplify": 0.85
    },
    "trellis_mesh_simplify_over_max": {
        "mesh_simplify": 0.99
    },
    "trellis_invalid_texture_size": {
        "texture_size": "4096"
    },
    "trellis_texture_size_int": {
        "texture_size": 1024  # Should be string
    }
}

def get_mock_response(response_type: str, model: str = "tripo") -> dict:
    """
    Get a mock response for testing.
    
    Args:
        response_type: Type of response (success, error, malformed)
        model: Model type (tripo or trellis)
        
    Returns:
        Mock response dictionary
    """
    if response_type == "success":
        return TRIPO_SUCCESS if model == "tripo" else TRELLIS_SUCCESS
    elif response_type in ERROR_RESPONSES:
        return ERROR_RESPONSES[response_type]
    elif response_type in MALFORMED_RESPONSES:
        return MALFORMED_RESPONSES[response_type]
    else:
        raise ValueError(f"Unknown response type: {response_type}")


def create_fal_exception(error_type: str) -> Exception:
    """
    Create a realistic FAL.AI exception based on error type.
    
    Args:
        error_type: Type of error from ERROR_RESPONSES
        
    Returns:
        Exception with proper error structure
    """
    import json
    
    if error_type not in ERROR_RESPONSES:
        raise ValueError(f"Unknown error type: {error_type}")
    
    error_data = ERROR_RESPONSES[error_type]
    
    # For structured errors, create a JSON exception
    if "detail" in error_data:
        return Exception(json.dumps({
            "detail": error_data["detail"],
            "status_code": error_data.get("status_code", 500)
        }))
    else:
        # Legacy format
        return Exception(error_data.get("message", "Unknown error"))


def create_progress_update(update_type: str, custom_message: str = None):
    """
    Create a mock FAL.AI progress update.
    
    Args:
        update_type: Type of update from PROGRESS_UPDATES
        custom_message: Optional custom message
        
    Returns:
        Mock InProgress object
    """
    from unittest.mock import Mock
    import fal_client
    
    update = Mock(spec=fal_client.InProgress)
    
    if update_type in PROGRESS_UPDATES:
        update.logs = PROGRESS_UPDATES[update_type]["logs"].copy()
        if custom_message:
            update.logs[0]["message"] = custom_message
    else:
        # Create custom update
        update.logs = [{
            "message": custom_message or f"Custom update: {update_type}",
            "timestamp": "2024-01-10T10:00:00.000Z",
            "level": "info"
        }]
    
    return update


# Additional test data for edge cases
EDGE_CASE_PARAMS = {
    "tripo_max_params": {
        "texture_enabled": True,
        "face_limit": 100000,
        "pbr": True,
        "texture": "HD",
        "texture_seed": 12345,
        "auto_size": True,
        "style": "gold",
        "quad": True,
        "texture_alignment": "geometry",
        "orientation": "align_image"
    },
    
    "trellis_boundary_params": {
        "ss_guidance_strength": 10.0,  # Max value
        "ss_sampling_steps": 50,  # Max value
        "slat_guidance_strength": 10.0,  # Max value
        "slat_sampling_steps": 50,  # Max value
        "mesh_simplify": 0.98,  # Max value
        "texture_size": "2048"  # Max value
    },
    
    "minimal_params": {
        # Empty params to test defaults
    }
}


# Mock file upload responses
UPLOAD_RESPONSES = {
    "success": "https://fal.ai/uploads/test_image_abc123.png",
    "error": None
}


# Batch processing mock data
BATCH_RESPONSES = {
    "all_success": [
        {"status": "success", "result": TRIPO_SUCCESS},
        {"status": "success", "result": TRIPO_SUCCESS},
        {"status": "success", "result": TRIPO_SUCCESS}
    ],
    
    "mixed_results": [
        {"status": "success", "result": TRIPO_SUCCESS},
        {"status": "error", "error": create_fal_exception("image_too_large")},
        {"status": "success", "result": TRELLIS_SUCCESS}
    ],
    
    "all_failed": [
        {"status": "error", "error": create_fal_exception("rate_limit")},
        {"status": "error", "error": create_fal_exception("image_load_error")},
        {"status": "error", "error": create_fal_exception("content_policy_violation")}
    ]
}