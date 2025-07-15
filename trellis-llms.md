# Trellis

> Generate 3D models from your images using Trellis. A native 3D generative model enabling versatile and high-quality 3D asset creation.


## Overview

- **Endpoint**: `https://fal.run/fal-ai/trellis`
- **Model ID**: `fal-ai/trellis`
- **Category**: image-to-3d
- **Kind**: inference
**Tags**: stylized



## API Information

This model can be used via our HTTP API or more conveniently via our client libraries.
See the input and output schema below, as well as the usage examples.


### Input Schema

The API accepts the following input parameters:


- **`image_url`** (`string`, _required_):
  URL of the input image to convert to 3D
  - Examples: "https://storage.googleapis.com/falserverless/web-examples/rodin3d/warriorwoman.png"

- **`seed`** (`integer`, _optional_):
  Random seed for reproducibility

- **`ss_guidance_strength`** (`float`, _optional_):
  Guidance strength for sparse structure generation Default value: `7.5`
  - Default: `7.5`
  - Range: `0` to `10`

- **`ss_sampling_steps`** (`integer`, _optional_):
  Sampling steps for sparse structure generation Default value: `12`
  - Default: `12`
  - Range: `1` to `50`

- **`slat_guidance_strength`** (`float`, _optional_):
  Guidance strength for structured latent generation Default value: `3`
  - Default: `3`
  - Range: `0` to `10`

- **`slat_sampling_steps`** (`integer`, _optional_):
  Sampling steps for structured latent generation Default value: `12`
  - Default: `12`
  - Range: `1` to `50`

- **`mesh_simplify`** (`float`, _optional_):
  Mesh simplification factor Default value: `0.95`
  - Default: `0.95`
  - Range: `0.9` to `0.98`

- **`texture_size`** (`TextureSizeEnum`, _optional_):
  Texture resolution Default value: `"1024"`
  - Default: `1024`
  - Options: `512`, `1024`, `2048`



**Required Parameters Example**:

```json
{
  "image_url": "https://storage.googleapis.com/falserverless/web-examples/rodin3d/warriorwoman.png"
}
```

**Full Example**:

```json
{
  "image_url": "https://storage.googleapis.com/falserverless/web-examples/rodin3d/warriorwoman.png",
  "ss_guidance_strength": 7.5,
  "ss_sampling_steps": 12,
  "slat_guidance_strength": 3,
  "slat_sampling_steps": 12,
  "mesh_simplify": 0.95,
  "texture_size": 1024
}
```


### Output Schema

The API returns the following output format:

- **`model_mesh`** (`File`, _required_):
  Generated 3D mesh file

- **`timings`** (`Timings`, _required_):
  Processing timings



**Example Response**:

```json
{
  "model_mesh": {
    "url": "",
    "content_type": "image/png",
    "file_name": "z9RV14K95DvU.png",
    "file_size": 4404019
  }
}
```


## Usage Examples

### cURL

```bash
curl --request POST \
  --url https://fal.run/fal-ai/trellis \
  --header "Authorization: Key $FAL_KEY" \
  --header "Content-Type: application/json" \
  --data '{
     "image_url": "https://storage.googleapis.com/falserverless/web-examples/rodin3d/warriorwoman.png"
   }'
```

### Python

```python
import fal_client

def on_queue_update(update):
    if isinstance(update, fal_client.InProgress):
        for log in update.logs:
           print(log["message"])

result = fal_client.subscribe(
    "fal-ai/trellis",
    arguments={
        "image_url": "https://storage.googleapis.com/falserverless/web-examples/rodin3d/warriorwoman.png"
    },
    with_logs=True,
    on_queue_update=on_queue_update,
)
print(result)
```

### JavaScript

```javascript
import { fal } from "@fal-ai/client";

const result = await fal.subscribe("fal-ai/trellis", {
  input: {
    image_url: "https://storage.googleapis.com/falserverless/web-examples/rodin3d/warriorwoman.png"
  },
  logs: true,
  onQueueUpdate: (update) => {
    if (update.status === "IN_PROGRESS") {
      update.logs.map((log) => log.message).forEach(console.log);
    }
  },
});
console.log(result.data);
console.log(result.requestId);
```


## Additional Resources

### Documentation

- [Model Playground](https://fal.ai/models/fal-ai/trellis)
- [API Documentation](https://fal.ai/models/fal-ai/trellis/api)
- [OpenAPI Schema](https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=fal-ai/trellis)
- [GitHub Repository](https://github.com/microsoft/TRELLIS/blob/main/LICENSE)

### fal.ai Platform

- [Platform Documentation](https://docs.fal.ai)
- [Python Client](https://docs.fal.ai/clients/python)
- [Errors](https://docs.fal.ai/errors)