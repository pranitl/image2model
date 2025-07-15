# Tripo3D

> State of the art Image to 3D Object generation


## Overview

- **Endpoint**: `https://fal.run/tripo3d/tripo/v2.5/image-to-3d`
- **Model ID**: `tripo3d/tripo/v2.5/image-to-3d`
- **Category**: image-to-3d
- **Kind**: inference
**Tags**: image-to-3d, stylized



## API Information

This model can be used via our HTTP API or more conveniently via our client libraries.
See the input and output schema below, as well as the usage examples.


### Input Schema

The API accepts the following input parameters:


- **`seed`** (`integer`, _optional_):
  This is the random seed for model generation. The seed controls the geometry generation process, ensuring identical models when the same seed is used. This parameter is an integer and is randomly chosen if not set.

- **`face_limit`** (`integer`, _optional_):
  Limits the number of faces on the output model. If this option is not set, the face limit will be adaptively determined.

- **`pbr`** (`boolean`, _optional_):
  A boolean option to enable pbr. The default value is True, set False to get a model without pbr. If this option is set to True, texture will be ignored and used as True.
  - Default: `false`

- **`texture`** (`TextureEnum`, _optional_):
  An option to enable texturing. Default is 'standard', set 'no' to get a model without any textures, and set 'HD' to get a model with hd quality textures. Default value: `"standard"`
  - Default: `"standard"`
  - Options: `"no"`, `"standard"`, `"HD"`

- **`texture_seed`** (`integer`, _optional_):
  This is the random seed for texture generation. Using the same seed will produce identical textures. This parameter is an integer and is randomly chosen if not set. If you want a model with different textures, please use same seed and different texture_seed.

- **`auto_size`** (`boolean`, _optional_):
  Automatically scale the model to real-world dimensions, with the unit in meters. The default value is False.
  - Default: `false`

- **`style`** (`Enum`, _optional_):
  Defines the artistic style or transformation to be applied to the 3D model, altering its appearance according to preset options (extra $0.05 per generation). Omit this option to keep the original style and apperance.
  - Options: `"person:person2cartoon"`, `"object:clay"`, `"object:steampunk"`, `"animal:venom"`, `"object:barbie"`, `"object:christmas"`, `"gold"`, `"ancient_bronze"`

- **`quad`** (`boolean`, _optional_):
  Set True to enable quad mesh output (extra $0.05 per generation). If quad=True and face_limit is not set, the default face_limit will be 10000. Note: Enabling this option will force the output to be an FBX model.
  - Default: `false`

- **`texture_alignment`** (`Enum`, _optional_):
  Determines the prioritization of texture alignment in the 3D model. The default value is original_image. Default value: `original_image`
  - Default: `"original_image"`
  - Options: `"original_image"`, `"geometry"`

- **`orientation`** (`Enum`, _optional_):
  Set orientation=align_image to automatically rotate the model to align the original image. The default value is default. Default value: `default`
  - Default: `"default"`
  - Options: `"default"`, `"align_image"`

- **`image_url`** (`string`, _required_):
  URL of the image to use for model generation.
  - Examples: "https://platform.tripo3d.ai/assets/front-235queJB.jpg", "https://raw.githubusercontent.com/VAST-AI-Research/TripoSR/ea034e12a428fa848684a3f9f267b2042d298ca6/examples/hamburger.png", "https://raw.githubusercontent.com/VAST-AI-Research/TripoSR/ea034e12a428fa848684a3f9f267b2042d298ca6/examples/poly_fox.png", "https://raw.githubusercontent.com/VAST-AI-Research/TripoSR/ea034e12a428fa848684a3f9f267b2042d298ca6/examples/robot.png", "https://raw.githubusercontent.com/VAST-AI-Research/TripoSR/ea034e12a428fa848684a3f9f267b2042d298ca6/examples/teapot.png", "https://raw.githubusercontent.com/VAST-AI-Research/TripoSR/ea034e12a428fa848684a3f9f267b2042d298ca6/examples/tiger_girl.png", "https://raw.githubusercontent.com/VAST-AI-Research/TripoSR/ea034e12a428fa848684a3f9f267b2042d298ca6/examples/horse.png", "https://raw.githubusercontent.com/VAST-AI-Research/TripoSR/ea034e12a428fa848684a3f9f267b2042d298ca6/examples/flamingo.png", "https://raw.githubusercontent.com/VAST-AI-Research/TripoSR/ea034e12a428fa848684a3f9f267b2042d298ca6/examples/unicorn.png", "https://raw.githubusercontent.com/VAST-AI-Research/TripoSR/ea034e12a428fa848684a3f9f267b2042d298ca6/examples/chair.png", "https://raw.githubusercontent.com/VAST-AI-Research/TripoSR/ea034e12a428fa848684a3f9f267b2042d298ca6/examples/iso_house.png", "https://raw.githubusercontent.com/VAST-AI-Research/TripoSR/ea034e12a428fa848684a3f9f267b2042d298ca6/examples/marble.png", "https://raw.githubusercontent.com/VAST-AI-Research/TripoSR/ea034e12a428fa848684a3f9f267b2042d298ca6/examples/police_woman.png", "https://raw.githubusercontent.com/VAST-AI-Research/TripoSR/ea034e12a428fa848684a3f9f267b2042d298ca6/examples/captured_p.png"



**Required Parameters Example**:

```json
{
  "image_url": "https://platform.tripo3d.ai/assets/front-235queJB.jpg"
}
```

**Full Example**:

```json
{
  "texture": "standard",
  "texture_alignment": "original_image",
  "orientation": "default",
  "image_url": "https://platform.tripo3d.ai/assets/front-235queJB.jpg"
}
```


### Output Schema

The API returns the following output format:

- **`task_id`** (`string`, _required_):
  The task id of the 3D model generation.

- **`model_mesh`** (`File`, _optional_):
  Model
  - Examples: {"file_size":6744644,"content_type":"application/octet-stream","url":"https://v3.fal.media/files/zebra/NA4WkhbpI-XdOIFc4cDIk_tripo_model_812c3a8a-6eb3-4c09-9f40-0563d27ae7ea.glb"}

- **`base_model`** (`File`, _optional_):
  Base model

- **`pbr_model`** (`File`, _optional_):
  Pbr model

- **`rendered_image`** (`File`, _optional_):
  A preview image of the model
  - Examples: {"file_size":13718,"content_type":"image/webp","url":"https://v3.fal.media/files/panda/zDTAHqp8ifMOT3upZ1xJv_legacy.webp"}



**Example Response**:

```json
{
  "task_id": "",
  "model_mesh": {
    "file_size": 6744644,
    "content_type": "application/octet-stream",
    "url": "https://v3.fal.media/files/zebra/NA4WkhbpI-XdOIFc4cDIk_tripo_model_812c3a8a-6eb3-4c09-9f40-0563d27ae7ea.glb"
  },
  "rendered_image": {
    "file_size": 13718,
    "content_type": "image/webp",
    "url": "https://v3.fal.media/files/panda/zDTAHqp8ifMOT3upZ1xJv_legacy.webp"
  }
}
```


## Usage Examples

### cURL

```bash
curl --request POST \
  --url https://fal.run/tripo3d/tripo/v2.5/image-to-3d \
  --header "Authorization: Key $FAL_KEY" \
  --header "Content-Type: application/json" \
  --data '{
     "image_url": "https://platform.tripo3d.ai/assets/front-235queJB.jpg"
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
    "tripo3d/tripo/v2.5/image-to-3d",
    arguments={
        "image_url": "https://platform.tripo3d.ai/assets/front-235queJB.jpg"
    },
    with_logs=True,
    on_queue_update=on_queue_update,
)
print(result)
```

### JavaScript

```javascript
import { fal } from "@fal-ai/client";

const result = await fal.subscribe("tripo3d/tripo/v2.5/image-to-3d", {
  input: {
    image_url: "https://platform.tripo3d.ai/assets/front-235queJB.jpg"
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

- [Model Playground](https://fal.ai/models/tripo3d/tripo/v2.5/image-to-3d)
- [API Documentation](https://fal.ai/models/tripo3d/tripo/v2.5/image-to-3d/api)
- [OpenAPI Schema](https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=tripo3d/tripo/v2.5/image-to-3d)

### fal.ai Platform

- [Platform Documentation](https://docs.fal.ai)
- [Python Client](https://docs.fal.ai/clients/python)
- [Errors](https://docs.fal.ai/errors)