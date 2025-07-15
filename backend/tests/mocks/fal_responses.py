"""
Mock FAL.AI API responses for testing.

These mock responses are based on the actual FAL.AI API documentation
for both Tripo3D and Trellis models.
"""

# Tripo3D Success Response (based on actual API structure)
TRIPO_SUCCESS = {
    "model_mesh": {
        "url": "https://fal.media/files/elephant/abc123_model.glb",
        "file_size": 4404019,
        "content_type": "model/gltf-binary",
        "file_name": "abc123_model.glb"
    },
    "rendered_image": {
        "url": "https://fal.media/files/tiger/abc123_preview.webp",
        "file_size": 123456,
        "content_type": "image/webp"
    },
    "task_id": "550e8400-e29b-41d4-a716-446655440000"
}

# Trellis Success Response (based on actual API structure)
TRELLIS_SUCCESS = {
    "model_mesh": {
        "url": "https://fal.media/files/zebra/xyz789_model.glb",
        "file_size": 5123456,
        "content_type": "model/gltf-binary",
        "file_name": "xyz789_model.glb"
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

# Error responses
ERROR_RESPONSES = {
    "rate_limit": {
        "error": "Rate limit exceeded",
        "message": "Too many requests. Please try again later.",
        "status_code": 429
    },
    "authentication": {
        "error": "Unauthorized",
        "message": "Invalid API key",
        "status_code": 401
    },
    "timeout": {
        "error": "Request timeout",
        "message": "The request took too long to process",
        "status_code": 504
    },
    "server_error": {
        "error": "Internal server error",
        "message": "An unexpected error occurred",
        "status_code": 500
    },
    "bad_request": {
        "error": "Bad request",
        "message": "Invalid parameters provided",
        "status_code": 400
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