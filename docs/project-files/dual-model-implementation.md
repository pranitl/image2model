# Dual-Model Implementation for Image-to-3D Generation

## Overview
This document outlines the abstraction and integration of multiple image-to-3D models (Tripo 2.5 and Trellis) via FAL.AI in our backend system. The goal is to create a flexible, scalable architecture that minimizes changes when adding new models, offloads storage to FAL.AI by using direct download URLs, and handles model-specific parameters dynamically. This aligns with GitHub issue #12, ensuring the system isn't tightly coupled to any single model's API or output format.

### Updated GitHub Issue Description (Issue #12)
**Title:** Abstract FAL.AI Client Interface for Flexible Image-to-3D Model Integration (Tripo 2.5 and Trellis)

**Description:**

As our platform evolves, we need to support multiple image-to-3D models via FAL.AI without tightly coupling the system to any single model's API or output format. Currently, the implementation in `backend/app/workers/fal_client.py` is tailored to Tripo 2.5 (endpoint: tripo3d/tripo/v2.5/image-to-3d), handling parameters like face_limit and texture_enabled, and returning direct FAL.AI download URLs for models (e.g., GLB format) to offload storage.

We want to integrate Trellis (endpoint: fal-ai/trellis) as the next model, which has different parameters:
- ss_guidance_strength (default: 7.5, range: 0-10)
- ss_sampling_steps (default: 12, range: 1-50)
- slat_guidance_strength (default: 3, range: 0-10)
- slat_sampling_steps (default: 12, range: 1-50)
- mesh_simplify (default: 0.95, range: 0.9-0.98)
- texture_size (enum: 512, 1024 [default], 2048)

To minimize changes when adding new models (e.g., future ones beyond Tripo 2.5 and Trellis), we should create an abstract interface in `fal_client.py` that:
- Defines common methods (e.g., authenticate, upload_image, generate_model) while allowing model-specific subclasses (e.g., TripoClient, TrellisClient) to handle nuances.
- Passes model-specific parameters dynamically (e.g., via a params dict in requests).
- Continues offloading storage by returning FAL.AI download URLs directly, without local downloads (update `app/api/endpoints/download.py` and `app/api/endpoints/models.py` to handle model-agnostic responses).
- Ensures endpoints like `/generate` in `app/api/endpoints/models.py` can accept model_type (e.g., "tripo3d" or "trellis") and route to the appropriate client.

This abstraction will make the system scalable: adding a new model would involve creating a new subclass with its endpoint and param mapping, without altering core logic in workers, endpoints, or download handling.

**Acceptance Criteria:**
- System supports both Tripo 2.5 and Trellis via a unified interface.
- No local file storage/downloads; rely on FAL.AI URLs.
- Minimal changes to existing endpoints (e.g., add model_type to requests).
- Tests for both models, ensuring output is a download URL.
- Documentation updates in code and README.

## Rationale for Abstraction
- **Current Limitations:** The codebase is Tripo 2.5-specific (e.g., hardcoded endpoint and params in fal_client.py), making new model integration require widespread changes.
- **Goals:** 
  - Scalability: Easy addition of models without rearchitecting.
  - Minimal Repetition: Share common logic (auth, upload, job submission).
  - Flexibility: Handle varying params/output without changing core endpoints.
  - Efficiency: Offload storage to FAL.AI URLs.
- **Design Pattern:** Factory pattern with abstract base class—proven for pluggable systems.
- **Trade-offs:** Slight increase in code complexity (subclasses) but gains in maintainability. No performance overhead since it's runtime instantiation.

## Potential Challenges and Mitigations
- **Param Differences:** Models have unique params—mitigated by subclass-specific validation and mapping.
- **Output Variations:** If future models return different formats, override process_result in subclasses.
- **Error Handling:** Ensure base class handles common FAL errors; subclasses add model-specific ones.
- **Backward Compatibility:** Keep Tripo 2.5 working as-is during transition.
- **Testing:** Mock FAL responses to avoid API costs; test param validation edge cases (e.g., invalid ranges).
- **Future Models:** If a model requires non-URL outputs, extend process_result to handle optionally.

## Dependency Implications
Based on the dependency graph in deps.json:
- Changes to app/workers/fal_client.py affect app/workers/tasks.py, which is imported by app/api/endpoints/models.py and app/api/endpoints/upload.py.
- Recommend verifying no breaking changes in these dependents during testing (e.g., ensure tasks.py can handle the new client factory).
- If adding model_type affects job_store (used in download.py), confirm it stores model-agnostic data like URLs.

## Granular Implementation Steps

### Step 1: Refactor fal_client.py (Core Abstraction Layer)
- **1.1: Define AbstractFalClient (Abstract Base Class)**
  - Import ABC and abstractmethod.
  - Attributes: self.model_endpoint (abstract property), self.max_retries=3, self.base_timeout=300, etc.
  - Methods:
    - `__init__(self)`: Setup authentication (as current).
    - `upload_file_to_fal(self, file_path: str) -> str`: A new common method to handle `fal.upload_file()`.
    - `submit_job(self, input_data: Dict) -> Dict`: Refactor subscribe call with progress handling.
    - `process_result(self, result: Dict, ...) -> Dict`: Refactor to extract URLs generically.
    - Abstract: `@abstractmethod def prepare_input(self, image_url: str, params: Dict) -> Dict`
    - Abstract (optional): `@abstractmethod def validate_params(self, params: Dict)`
    - Common error handler: _handle_fal_error (as current).

- **1.2: Implement TripoClient (Subclass)**
  - Inherit from AbstractFalClient.
  - `@property def model_endpoint(self) -> str: return "tripo3d/tripo/v2.5/image-to-3d"`
  - `prepare_input(self, image_url: str, params: Dict) -> Dict`: 
    ```python
    input_data = {
        "image_url": image_url,
        "texture": "standard" if params.get('texture_enabled', True) else "no",
        "texture_alignment": "original_image",
        "orientation": "default"
    }
    if 'face_limit' in params: input_data['face_limit'] = params['face_limit']
    return input_data
    ```
  - `validate_params(self, params: Dict)`: Check types (e.g., face_limit int, texture_enabled bool), ranges if applicable.

- **1.3: Implement TrellisClient (Subclass)**
  - Inherit from AbstractFalClient.
  - `@property def model_endpoint(self) -> str: return "fal-ai/trellis"`
  - `prepare_input(self, image_url: str, params: Dict) -> Dict`:
    ```python
    input_data = {"image_url": image_url}
    defaults = {  # From Trellis docs
        "ss_guidance_strength": 7.5,
        "ss_sampling_steps": 12,
        "slat_guidance_strength": 3,
        "slat_sampling_steps": 12,
        "mesh_simplify": 0.95,
        "texture_size": "1024"
    }
    input_data.update({k: params.get(k, v) for k, v in defaults.items()})
    return input_data
    ```
  - `validate_params(self, params: Dict)`: Enforce ranges (e.g., ss_guidance_strength 0-10), enum for texture_size.

- **1.4: Add Factory Function**
  ```python
  def get_model_client(model_type: str) -> AbstractFalClient:
      if model_type == "tripo3d": return TripoClient()
      if model_type == "trellis": return TrellisClient()
      raise ValueError(f"Unsupported model: {model_type}")
  ```

- **1.5: Update process_single_image**
    - Make it a base method in `AbstractFalClient`.
    - It should first call `image_url = self.upload_file_to_fal(file_path)`.
    - Then, `input_data = self.prepare_input(image_url, params)`.
    - Finally, it calls `self.submit_job(input_data)` and `self.process_result(...)`.
    - This ensures the flow is clear: local file -> FAL.AI URL -> model input.
    - Remove Tripo specifics.

### Step 2: Update app/api/endpoints/models.py (Endpoint and Queuing)
- **2.1: Enhance ModelGenerationRequest**
    - Add `params: Optional[Dict[str, Any]] = None` (e.g., for Tripo: {"face_limit": 1000}, for Trellis: {"texture_size": "2048"}).

- **2.2: Update generate_3d_model**
    - `client = get_model_client(request.model_type)`
    - In Celery task: Pass model_type and params; use client.process_single_image(..., params=params).
    - Validate model_type in available_models.

- **2.3: Update get_available_models**
    - Remove hardcoded Tripo endpoint/params; rely on client subclasses.
    - Edge Cases: Default params if not provided, validate model_type early.


### Step 3: Minimal Updates to app/api/endpoints/download.py
- __3.1: Confirm Generic Handling (Effort: Low)__

    - Ensure routes handle any URL (FAL.AI direct links) without assuming model-specific formats.
    - If needed, add a field in JobFilesResponse for model_type to inform clients (e.g., for rendering previews).

- __3.2: Update Any Job Store/Result Handling (Effort: Low)__

    - If job_result includes model-specific data, make it generic (e.g., use 'download_url' uniformly).
- __3.3: Handle Direct URLs__

    - Update the endpoint to return a redirect (e.g., HTTP 302) to the FAL.AI URL instead of a local StreamingResponse.
    - Ensure job_store updates store the FAL.AI URL instead of local paths.


### Step 4: Integrate Trellis
- As per Step 1.3; test param mapping.

### Step 5: Testing
- Unit: Mock FAL, test subclasses.
    - Test AbstractFalClient methods (upload, submit, process).
    - Test TripoClient: Mock FAL responses, assert correct input_data, validate params.
    - Test TrellisClient: Similar, with Trellis params.

- Integration: End-to-end with mocks.
- Manual: Real API calls.

### Step 6: Documentation
- Docstrings, README updates on adding models.
