# Converting a Vanilla JS Frontend to Svelte (with File Upload & SSE Progress)

Converting your vanilla JS/HTML app to Svelte will make it easier to maintain and extend. Svelte's component-based, reactive architecture lets you preserve all the existing functionality (file upload, server-sent events for progress, download links, error handling, etc.) in a cleaner way. Below is a step-by-step guide:

## 1. Set Up a Svelte Project

First, scaffold a new Svelte project. You can use Svelte’s official template via the degit tool. For example, run:

```bash
npx degit sveltejs/template image2model-svelte-app
cd image2model-svelte-app
npm install
npm run dev
```

This uses the basic Svelte template (with Rollup or Vite) and will create a project structure with an `App.svelte` component, a `main.js`, etc. The development server (`npm run dev`) will serve your app locally so you can test as you build.

**Optional:** If you anticipate multiple distinct pages (e.g. a separate landing page and an app page), you might consider using **SvelteKit**, which is a framework on top of Svelte that provides file-based routing and other features. However, to keep things simple for now, you can also manage a "landing view" and "app view" within a single Svelte app (explained in Step 6 below) without introducing full SvelteKit routing.

## 2. Create the File Upload Component

In Svelte, you can create components for different parts of your UI. For example, you might have a component for the upload interface (or just use `App.svelte` as the main component for everything). Svelte allows you to write markup, script, and styles together in a `.svelte` file.

Here's how you can set up the file upload input in Svelte:

**HTML (in your Svelte component):** Use an `<input type="file">` element. Svelte provides two convenient ways to get the selected file: you can either use a two-way binding or an event handler. For simplicity, let's use the binding approach with `bind:files`:

```svelte
<script>
  let files;  // this will hold the FileList from the input
  let selectedFile = null;
  
  // Other state variables we'll use
  let progress = 0;
  let downloadUrl = "";
  let errorMsg = "";
  let uploading = false;
  
  function onFileSelected() {
    if (files && files.length > 0) {
      selectedFile = files[0];  // get the first (and presumably only) file
    }
  }
</script>

<!-- File input field -->
<input 
  id="fileInput"
  type="file" 
  bind:files={files} 
  on:change={onFileSelected} 
/>
<label for="fileInput">Choose an image file</label>

<button on:click={startUpload} disabled={!selectedFile || uploading}>
  Upload and Convert
</button>
```

In the above snippet, `bind:files={files}` tells Svelte to bind the input's FileList to our `files` variable. When the user selects a file, `files` gets populated and we then set `selectedFile` to the first file. We also disable the upload button until a file is selected and while an upload is in progress.

**Note:** You can restrict file types via the `accept` attribute if needed (e.g. `accept="image/png, image/jpeg"`). Also, if you want to allow multiple file uploads at once, you could set `multiple` on the input and handle an array of files (but your backend likely expects one file, so we'll assume single file).

## 3. Preserving the FastAPI Upload Call (Using Fetch and FormData)

To send the selected file to your FastAPI backend, use the Fetch API with a FormData object – very similar to how you might do it in plain JS. In Svelte (which runs in the browser), you can call `fetch()` inside a function or lifecycle hook. For example, define the `startUpload` function in your `<script>`:

```svelte
<script>
  async function startUpload() {
    if (!selectedFile) return;
    uploading = true;
    progress = 0;
    errorMsg = "";
    downloadUrl = "";

    try {
      // Prepare FormData
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      // Make the POST request to FastAPI (adjust URL as needed)
      const response = await fetch('http://YOUR_API/upload', {
        method: 'POST',
        body: formData
        // No need to set Content-Type for multipart/form-data; the browser will handle it
      });
      
      if (!response.ok) {
        // Backend returned an error status
        const errorText = await response.text();
        throw new Error(`Upload failed: ${errorText}`);
      }
      
      // Parse JSON response (assuming your API returns JSON with maybe an ID or result)
      const result = await response.json();
      console.log("Upload response:", result);
      // If the API immediately returns a result or download link, you could handle it here.
      // Otherwise, if using SSE for progress, we will handle updates in the SSE section.
      
    } catch (err) {
      console.error(err);
      errorMsg = err.message || "Upload failed.";
      uploading = false;
    }
  }
</script>
```

This code creates a FormData with the file and sends it via fetch. Notice we did *not* manually set the `Content-Type` header – when using FormData, you should allow the browser to set the multipart boundaries and headers automatically. The snippet above assumes an endpoint like `/upload` on your FastAPI; use the correct URL/path as in your current app.

*Citing reference:* For example, MDN demonstrates file upload with fetch as: appending the file to FormData and calling `fetch('...url...', { method: 'POST', body: formData })`.

Depending on how your FastAPI backend works, the response to this upload might include a job ID or immediate result:

* **If the FastAPI endpoint starts processing in background and uses SSE for progress**: it might respond quickly (e.g. with a job identifier or just a 202 Accepted), and the client should then listen on an SSE endpoint for progress updates. In that case, the `result` from the initial fetch likely contains an ID or confirmation.
* **If the FastAPI endpoint itself streams an SSE response** (i.e. the HTTP response is a streaming event source): then `fetch` as shown might not directly give you JSON, because the response is an event stream. More typically, SSE is done on a separate GET endpoint, which we'll cover next.

For now, let's assume the POST gives us enough info to start the SSE (like a job ID or some flag to know the process started). We set `uploading = true` to indicate the process is underway (you can use this to disable inputs or show a spinner, etc.).

## 4. Implementing Server-Sent Events (SSE) for Progress Updates

Server-Sent Events will allow the backend to push progress messages to the frontend. In the browser, SSE is accessed via the **EventSource** API. In Svelte, you'll typically create an `EventSource` when you need to start listening (e.g. right after starting the upload).

Let's say your FastAPI has an endpoint (e.g. `/progress/{job_id}` or maybe just `/progress` if it manages one job at a time) that yields SSE events. We will open an EventSource to that endpoint:

```svelte
<script>
  import { onMount } from 'svelte';
  let evtSource;  // will hold the EventSource instance
  
  function connectToProgressStream(jobId) {
    // Open SSE connection (make sure URL is correct and accessible)
    evtSource = new EventSource(`http://YOUR_API/progress/${jobId}`);
    
    evtSource.onmessage = (event) => {
      // parse event data (assuming server sends JSON string in event.data)
      try {
        const data = JSON.parse(event.data);
        // Example: data could be { progress: 50 } or { progress: 100, download_url: '...' }
        if (data.progress !== undefined) {
          progress = data.progress;
        }
        if (data.download_url) {
          // When done, server might send the download link
          downloadUrl = data.download_url;
          uploading = false;
          evtSource.close();  // stop listening since job is finished
        }
      } catch(e) {
        console.error("Error parsing SSE message", e);
      }
    };
    
    evtSource.onerror = (error) => {
      console.error("SSE connection error:", error);
      errorMsg = "Lost connection to server for progress updates.";
      uploading = false;
      evtSource.close();
    };
  }
</script>
```

You would call `connectToProgressStream(jobId)` after initiating the upload. For example, if the `startUpload()` function’s fetch returns a `job_id`, you can do `connectToProgressStream(result.job_id)` inside `startUpload` (after the fetch). If your backend uses a single SSE stream without job IDs, you might call it directly after `fetch` returns OK. Adapt this to your actual API design.

**How this works:** `new EventSource(url)` opens a persistent connection to the server. The server will send events with `data:` lines, which arrive in the `event.data` of the `onmessage` handler. In the code above, we assume the server sends JSON strings; adjust parsing to your format. Each time an SSE message arrives, we update the Svelte state (`progress`, `downloadUrl`, etc.). Because these are reactive `let` variables in a Svelte component, updating them will automatically update the UI wherever they are used.

**Important:** Clean up the SSE connection when it's no longer needed. We called `evtSource.close()` once we got the final download link or on error. If your component can be destroyed (navigating away), it's also good to close the EventSource in Svelte's cleanup hook. Svelte allows returning a teardown function from `onMount` or using `onDestroy`. For example, we could set up SSE in an `onMount` and return a cleanup:

```svelte
onMount(() => {
  // ... (set up evtSource as above) ...
  return () => {
    // Cleanup when component is destroyed
    if (evtSource) evtSource.close();
  };
});
```

Rich Harris (the creator of Svelte) notes that you can return a cleanup function from onMount instead of using a separate `onDestroy` block. This approach closes the SSE connection automatically if the component unmounts, avoiding memory leaks.

**SSE Example References:** A Svelte chat app example opens an EventSource and listens for messages like so:

```js
const eventSource = new EventSource('http://localhost:3000/your_sse_endpoint');
eventSource.onmessage = e => {
    // handle incoming message
    const newData = JSON.parse(e.data);
    // update Svelte store or state with newData
};
```

. This is exactly what we're doing for your progress updates. Another example from StackOverflow shows using `onMount` to initiate the EventSource and `onDestroy` (or return cleanup) to close it when done.

## 5. Updating the UI with Progress and Download Links

Now that we have the file upload and SSE logic, we need to reflect this in the UI:

* **Progress Indicator:** You can use a `<progress>` element or a simple text percentage. For instance, in your Svelte component's markup, add:

  ```svelte
  {#if uploading}
    <p>Processing... {progress}% complete</p>
    <progress max="100" value={progress}></progress>
  {/if}
  ```

  This will show a progress bar and percentage text when `uploading` is true. As the `progress` variable updates (via SSE events), Svelte’s reactivity will update the DOM automatically. No manual DOM manipulation needed – you just update the variable in the script, and the bound value in the markup reflects it.

* **Download Button/Link:** Once processing is done, your code should set `downloadUrl` (e.g. from the SSE final message or as part of the fetch response). In the UI, you can conditionally show a download link:

  ```svelte
  {#if downloadUrl}
    <p>Conversion complete! Download your model file here:</p>
    <a class="download-btn" href={downloadUrl} download>📥 Download Result</a>
  {/if}
  ```

  The `download` attribute on `<a>` prompts a download rather than navigating to the file, and it can even specify a filename (you can set `download="myModel.obj"` or similar if you want). This way, when the link appears and the user clicks it, the file will be downloaded to their computer. *(Ensure your backend sets appropriate CORS headers if the file is served from an API, and note that the download attribute works best for same-origin or properly CORS-enabled files.)*

* **Error Messages:** Use the `errorMsg` state to display any errors that occur. For example:

  ```svelte
  {#if errorMsg}
    <p class="error">Error: {errorMsg}</p>
  {/if}
  ```

  Your earlier logic in `startUpload` and SSE `.onerror` sets `errorMsg` when something goes wrong. By wrapping it in `{#if}`, the message will show up only when there's an actual error.

* **Styling:** You mentioned you are not wedded to specific styles, so feel free to style as you like. In Svelte, you can put a `<style>` block in the component for component-specific CSS. These styles are scoped to the component by default (meaning they won’t leak to other components). For example:

  ```svelte
  <style>
    .error { color: red; }
    .download-btn {
      /* your styling for the download link/button */
      padding: 0.5em 1em;
      background-color: #4caf50;
      color: white;
      text-decoration: none;
      border-radius: 4px;
    }
    /* etc. */
  </style>
  ```

  You can also use global styles (in `public/global.css` or via `<style global>` in Svelte), or even a CSS framework, but starting simple is fine given your comfort with basic HTML/CSS.

## 6. Structuring Pages: Landing Page vs. Single-Page App

You indicated you might want a landing page and then the app page, but you're okay if it's all in one for now. There are a couple of approaches:

* **Single-Page with Conditional Sections:** The simplest method (especially if you're new to frameworks) is to use one Svelte component and toggle between a "landing view" and the "upload app view" using a state variable. For example, in `App.svelte`:

  ```svelte
  <script>
    let showApp = false;
  </script>

  {#if !showApp}
    <!-- Landing Page Content -->
    <div class="landing">
      <h1>Welcome to Image2Model</h1>
      <p>Upload an image to generate a 3D model...</p>
      <button on:click={() => showApp = true}>Get Started</button>
    </div>
  {:else}
    <!-- Main App Content (file upload UI) -->
    <FileUploadComponent />
  {/if}
  ```

  In this snippet, before the user clicks "Get Started", they see the landing content. When `showApp` becomes true, we render the file upload component. You could keep the upload UI directly in `App.svelte` or import it as a separate component (`FileUploadComponent.svelte`) for clarity. This method does not require a routing library.

* **Multiple Pages with Routing:** Alternatively, you could set up routing so that, for example, `/` is landing and `/app` is the upload page. If using **SvelteKit**, it’s straightforward by creating `src/routes/+page.svelte` for landing and `src/routes/app/+page.svelte` for the app. SvelteKit will handle navigation for you. However, introducing SvelteKit means learning its file-based routing and loading mechanics. Given that you're a self-described beginner and since this app can function as a single page, you might hold off on this until you add more features (like authentication or user profiles) that truly warrant multiple pages.

In summary, the conditional-rendering approach is quick and easy, while SvelteKit provides a more scalable structure if needed. Since *“whatever makes the simplest easiest version”* is the goal, starting with one page and a conditional landing section is perfectly fine. You can always refactor into separate pages later if the project grows.

## 7. Putting It All Together (Summary)

By converting to Svelte, you maintain the core functionality but simplify the implementation:

* **File Upload**: Handled with a bound file input and a fetch call using FormData (no need for complex libraries).
* **SSE Progress**: Managed with the EventSource web API within Svelte's reactivity. The SSE pushes updates that directly update Svelte's state, which auto-rerenders the progress bar/text.
* **Download Links**: Easily rendered once available, using an anchor tag with the `download` attribute so users can download the result file.
* **Error Handling**: Svelte's reactivity makes it simple to show/hide error messages based on an `errorMsg` variable.
* **Styling**: You can write CSS in the component for localized styles (scoped to that component), or adjust global styles – whatever you prefer, without being locked into a library.

One big advantage is that Svelte is very beginner-friendly. You write nearly standard HTML and CSS inside components, and use normal JavaScript for the logic. There is no virtual DOM to manage and no complex state management library needed for this use case. Svelte’s reactivity (the fact that updating a `let` variable in a component updates the UI) will feel natural once you get used to it.

**Next Steps:** Try building the Svelte app with the above approach. Test the file upload and see the progress updates coming through. Since you have a FastAPI backend, you might need to enable CORS for the frontend if they’re on different hosts/ports (tools like `fastapi-cors` can help). Also, as you mentioned, authentication is not built yet – you can add that later (possibly using tokens or session cookies with your FastAPI, and adding some login UI in Svelte).

Good luck with the conversion! You’ll find that the end result is a cleaner and more maintainable frontend, while preserving all the functionality of your vanilla JS version. If you get stuck, Svelte’s official documentation and community are very helpful resources.

**Sources:**

* Svelte official docs on file bindings (using `bind:files` for `<input type="file">`).
* Example of using Fetch API with FormData to upload a file (MDN/StackOverflow).
* Medium article showing SSE usage with EventSource in a Svelte context (chat app example).
* StackOverflow example of initializing and cleaning up an EventSource in Svelte’s lifecycle and Rich Harris’s guidance on using `onMount` cleanup for SSE.
* W3Schools reference on the anchor `download` attribute for file downloads.
* Svelte documentation on scoped component styles (CSS encapsulation).
