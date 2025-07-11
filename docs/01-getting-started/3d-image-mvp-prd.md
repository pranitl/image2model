# Product Requirements Document

> **Last Updated**: 2025-07-11  
> **Status**: Complete  
> **Version**: 1.4  
> **Changelog**:
> - 1.4 (2025-07-11): Added framework compliance and cross-references
> - 1.3 (2025-07-01): Initial PRD by Gemini

## AI 3D Model Generator - MVP

## Table of Contents

- [Introduction & Vision](#1-introduction--vision)
- [Problem Statement](#2-problem-statement)
- [Target Audience](#3-target-audience)
- [Goals & Success Metrics](#4-goals--success-metrics)
- [Features & Scope (MVP)](#5-features--scope-mvp)
- [User Journey](#6-user-journey)
- [Technical Requirements](#7-technical-requirements)
- [Out of Scope (MVP)](#8-out-of-scope-mvp)
- [Future Roadmap](#9-future-roadmap-post-mvp)
- [Assumptions & Dependencies](#10-assumptions--dependencies)
- [Risks & Mitigations](#11-risks--mitigations)
- [Appendix](#12-appendix)

### **1\. Introduction & Vision**

This document outlines the requirements for the Minimum Viable Product (MVP) of the AI 3D Model Generator.

The vision is to create a simple, web-based tool that allows users to effortlessly transform a batch of 2D images into 3D models using the power of generative AI. For the MVP, the focus is on providing a core, end-to-end user experience: uploading images, configuring a key generation parameter, processing them via the FAL.AI API, and allowing the user to download the results.

### **2\. Problem Statement**

Creating 3D models from 2D images is a complex, time-consuming, and often expensive process that requires specialized software and skills. Generative AI models can automate this, but they are often only accessible through APIs, which can be intimidating for non-technical users. There is a need for a simple, user-friendly interface that bridges the gap between the user and the power of these AI models.

This MVP aims to solve this by providing a straightforward "upload, configure, process, download" workflow, abstracting away the complexities of API calls and batch processing.

### **3\. Target Audience**

For the MVP, the primary target audience is:

* **Exhibit Designers:** Exhibit designers for architectural firms have to currently manually model out museum objects into 3D renders. This solution will enable them to perform this function in bulk.

### **4\. Goals & Success Metrics**

The primary goal of the MVP is to **validate the core functionality and user demand** for a simplified 2D-to-3D conversion tool.

| Goal | Success Metric |
| :---- | :---- |
| **Validate Core Functionality** | 95% of batch jobs initiated are completed without critical errors. |
| **Assess User Engagement** | At least 100 unique users process at least one batch of images within the first month of deployment. |
| **Gather User Feedback** | Collect qualitative feedback from at least 10 users to inform future development. |
| **Establish Technical Feasibility** | The end-to-end architecture (Frontend \-\> FastAPI \-\> Celery \-\> FAL.AI) operates reliably under expected load. |

### **5\. Features & Scope (MVP)**

The scope of the MVP is strictly limited to the essential features required to deliver the core user journey.

#### **User Story 1: Image Upload & Configuration**

*As a user, I want to upload a batch of images from my computer and configure the model's face limit so that I can control the complexity of the generated 3D models.*

**Acceptance Criteria:**

* The UI must provide a clear area for file selection or drag-and-drop.  
* The user can select multiple image files at once (up to **25 images**).  
* Each individual image file must be **10 MB or less**. The UI should provide clear feedback if a file exceeds this limit.  
* Supported file formats are: .jpg, .jpeg, .png.  
* After selecting images, the UI must display a configuration option for **"Face Limit"**. This should be a simple number input field.  
* A tooltip or helper text should explain the face\_limit parameter (e.g., "Controls the level of detail. Leave blank for auto.").  
* An "Upload and Generate" button initiates the process, sending both the images and the face\_limit value to the backend.

#### **User Story 2: 3D Model Generation**

*As a system, I need to receive the batch of images and configuration, process them using the FAL.AI API, and store the resulting 3D models.*

**Acceptance Criteria:**

* The FastAPI backend must have an endpoint to receive the image files and the optional face\_limit parameter.  
* The backend must enforce the 10 MB per-file upload limit.  
* Uploaded images are temporarily stored on the server's local file system.  
* A background job (using Celery) is created for the batch.  
* The Celery worker iterates through each image and calls the tripo3d/tripo/v2.5/image-to-3d model, passing the face\_limit if provided by the user.  
* The generated 3D model files (in the format provided by the API, e.g., .glb) are saved to a unique directory on the local file system.  
* The system must handle API errors from FAL.AI gracefully (e.g., log the error, skip the failed image, and continue with the batch).

#### **User Story 3: Real-time Progress Monitoring**

*As a user, I want to see the real-time status of my batch job so that I know it is being processed and when it is complete.*

**Acceptance Criteria:**

* After uploading, the user is presented with a progress view, likely a grid of cards where each card represents an uploaded image.  
* Each card should display a thumbnail of the image and its current status (e.g., "Queued", "Processing...", "Complete", "Failed").  
* The UI must display updates pushed from the server (via Server-Sent Events).  
* An overall progress bar for the entire batch should be visible.  
* The connection for status updates closes automatically once the job is finished.

#### **User Story 4: Downloading Results**

*As a user, I want to be able to preview and download the generated 3D models once the processing is complete.*

**Acceptance Criteria:**

* When an image's status changes to "Complete," its corresponding card in the UI updates to show a download button.  
* The system will provide download links for the format generated by the FAL.AI API (e.g., GLB). The UI should clearly label the download button with the format.  
* *(Post-MVP consideration)* While the TripoSR API does not natively support multiple export formats, the UI should be designed with the future possibility of multiple download buttons (e.g., "Download GLB", "Download OBJ") in mind. For the MVP, only one format will be offered.  
* Clicking a download link will download the corresponding 3D model file to the user's computer.  
* The backend must provide an endpoint to serve these files from the local filesystem.

### **6\. Out of Scope for MVP**

* **User Accounts & Authentication**  
* **Job History**  
* **Cloud Storage**  
* **Advanced Model Options:** Users can only configure face\_limit. All other model parameters (style, pbr, etc.) will use the API's default values.  
* **Payment/Billing Integration**  
* **File Management**  
* **Server-side 3D Model Conversion:** The app will only serve the file format provided directly by the FAL.AI API.

### **7\. Technical Architecture & Stack**

* **Frontend:** Single-Page Application (SPA).  
  * **Implementation:** **SvelteKit**, providing server-side rendering, excellent performance, and a modern developer experience with built-in routing and API capabilities.  
* **Backend:** FastAPI (Python).  
* **Background Task Processing:** Celery with Redis as the message broker.  
* **Real-time Communication:** Server-Sent Events (SSE).  
* **Deployment:** To be determined (e.g., Docker containers on a cloud provider).

### **8\. Assumptions & Dependencies**

* A valid API key and access to the FAL.AI platform are available.  
* The tripo3d/tripo/v2.5/image-to-3d model is the target for the MVP.  
* The local server will have sufficient disk space for temporary file storage.  
* Users have a modern web browser that supports the chosen frontend technology and SSE.

### **9\. Future Considerations (Post-MVP)**

* Integration of user authentication via Clerk and job history.  
* Migration to cloud storage (e.g., S3) for scalability and persistence instead of relying on 7 day limits by fal.ai.
* Allowing users to configure **all relevant model parameters** (e.g., style, pbr, texture, file output format).  
* Implementing **server-side file conversion** to offer multiple download formats (OBJ, STL, etc.).  
* Implementing model selection so you are able to select a high quality model (Tripo 2.5) or a standard quality model (Tripo SR, Hunyuan 2.1 3D, etc.) to manage costs
* Implementing a credit or payment system via Stripe for API usage via a "credits system".  
* Adding a 3D viewer (e.g., \<model-viewer\>) to preview the generated models directly in the browser.

### **10\. API Interaction Examples**

This section provides basic code examples for interacting with the FAL.AI endpoint directly. The application's backend will implement this logic.

#### **cURL (HTTP)**

curl \-X POST \\  
  \-H "Authorization: Key YOUR\_FAL\_AI\_KEY" \\  
  \-H "Content-Type: application/json" \\  
  \-d '{  
    "image\_url": "https://raw.githubusercontent.com/VAST-AI-Research/TripoSR/main/examples/hamburger.png",  
    "face\_limit": 15000  
  }' \\  
  "https://queue.fal.run/tripo3d/tripo/v2.5/image-to-3d"

#### **JavaScript Client**

import { fal } from "@fal-ai/client";

// Ensure you have set your FAL\_KEY as an environment variable  
// or configured it in your application.

const result \= await fal.subscribe("tripo3d/tripo/v2.5/image-to-3d", {  
  input: {  
    image\_url: "https://raw.githubusercontent.com/VAST-AI-Research/TripoSR/main/examples/hamburger.png",  
    face\_limit: 15000  
  },  
  logs: true,  
  onQueueUpdate: (update) \=\> {  
    console.log("Queue update", update);  
  },  
});

console.log(result);

#### **Python Client**

import fal

\# Make sure to set your credentials  
\# fal.config.credentials \= "FAL\_KEY\_ID:FAL\_KEY\_SECRET"

handler \= fal.subscribe(  
    "tripo3d/tripo/v2.5/image-to-3d",  
    arguments={  
        "image\_url": "https://raw.githubusercontent.com/VAST-AI-Research/TripoSR/main/examples/hamburger.png",  
        "face\_limit": 15000,  
    },  
)

for event in handler.iter\_events():  
    if isinstance(event, fal.InProgress):  
        print("Request in progress")  
        print("Logs:", event.logs)

result \= handler.get()  
print(result)

### **11\. References**

- **FAL.AI TripoSR Model API Documentation:** [https://fal.ai/models/tripo3d/tripo/v2.5/image-to-3d/api](https://fal.ai/models/tripo3d/tripo/v2.5/image-to-3d/api)

## Related Documentation

- [Quick Start Guide](./quick-start.md) - Get started with development
- [Architecture Overview](./architecture-overview.md) - Technical implementation details
- [Technology Stack](./technology-stack.md) - Frameworks and tools used
- [API Reference](../03-backend/api-reference/) - Complete API documentation (coming soon)