<script>
  import Navbar from '$lib/components/Navbar.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import Button from '$lib/components/Button.svelte';
  import Hero from '$lib/components/Hero.svelte';
  import Icon from '$lib/components/Icon.svelte';
  
  let textValue = 'Sample text';
  let emailValue = 'user@example.com';
  let passwordValue = '';
  let numberValue = 10000;
  let rangeValue = 50;
  let textareaValue = 'This is a sample textarea content.\nIt can have multiple lines.';
  let selectValue = 'option2';
  let checkboxValue = true;
  let radioValue = 'radio2';
  let fileValue = null;
  let searchValue = '';
  
  // Form validation states
  let showValidation = false;
  let showError = false;
  let showSuccess = false;
</script>

<Navbar />

<main class="component-gallery">
  <Hero 
    title="Form Components Gallery"
    subtitle="Form elements and input components used in the application"
  />
  
  <section class="gallery-content">
    <div class="container">
      <!-- Text Inputs -->
      <div class="component-section">
        <h2>Text Inputs</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Basic Text Input</h3>
            <div class="demo-area">
              <div class="form-group">
                <label for="text-basic">Label</label>
                <input 
                  id="text-basic"
                  type="text" 
                  class="form-control" 
                  bind:value={textValue}
                  placeholder="Enter text..."
                />
                <small class="form-text">Helper text for additional information</small>
              </div>
            </div>
            <div class="code-snippet">
              <code>{`<div class="form-group">
  <label for="input-id">Label</label>
  <input type="text" class="form-control" placeholder="Enter text..." />
  <small class="form-text">Helper text</small>
</div>`}</code>
            </div>
          </div>

          <div class="component-demo">
            <h3>Email Input</h3>
            <div class="demo-area">
              <div class="form-group">
                <label for="email-input">Email Address</label>
                <input 
                  id="email-input"
                  type="email" 
                  class="form-control" 
                  bind:value={emailValue}
                  placeholder="name@example.com"
                />
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Password Input</h3>
            <div class="demo-area">
              <div class="form-group">
                <label for="password-input">Password</label>
                <input 
                  id="password-input"
                  type="password" 
                  class="form-control" 
                  bind:value={passwordValue}
                  placeholder="Enter password..."
                />
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Search Input</h3>
            <div class="demo-area">
              <div class="form-group">
                <div class="search-input">
                  <Icon name="search" size={20} />
                  <input 
                    type="search" 
                    class="form-control" 
                    bind:value={searchValue}
                    placeholder="Search..."
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Number & Range Inputs -->
      <div class="component-section">
        <h2>Number & Range Inputs</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Number Input</h3>
            <div class="demo-area">
              <div class="form-group">
                <label for="number-input">Face Limit</label>
                <input 
                  id="number-input"
                  type="number" 
                  class="form-control" 
                  bind:value={numberValue}
                  min="1000"
                  max="50000"
                  step="1000"
                />
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Range Slider</h3>
            <div class="demo-area">
              <div class="form-group">
                <label for="range-input">Quality Level: {rangeValue}%</label>
                <input 
                  id="range-input"
                  type="range" 
                  class="slider" 
                  bind:value={rangeValue}
                  min="0"
                  max="100"
                  step="5"
                />
                <div class="range-labels">
                  <span>Low</span>
                  <span>Medium</span>
                  <span>High</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Textareas -->
      <div class="component-section">
        <h2>Textareas</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Basic Textarea</h3>
            <div class="demo-area">
              <div class="form-group">
                <label for="textarea-basic">Description</label>
                <textarea 
                  id="textarea-basic"
                  class="form-control" 
                  bind:value={textareaValue}
                  rows="4"
                  placeholder="Enter description..."
                ></textarea>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Resizable Textarea</h3>
            <div class="demo-area">
              <div class="form-group">
                <label for="textarea-resize">Notes</label>
                <textarea 
                  id="textarea-resize"
                  class="form-control resizable" 
                  rows="3"
                  placeholder="Drag corner to resize..."
                ></textarea>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Selects & Dropdowns -->
      <div class="component-section">
        <h2>Selects & Dropdowns</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Basic Select</h3>
            <div class="demo-area">
              <div class="form-group">
                <label for="select-basic">Choose Option</label>
                <select 
                  id="select-basic"
                  class="form-control" 
                  bind:value={selectValue}
                >
                  <option value="">Select an option...</option>
                  <option value="option1">Option 1</option>
                  <option value="option2">Option 2</option>
                  <option value="option3">Option 3</option>
                </select>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Multi-Select</h3>
            <div class="demo-area">
              <div class="form-group">
                <label for="select-multi">Choose Multiple</label>
                <select 
                  id="select-multi"
                  class="form-control" 
                  multiple
                  size="4"
                >
                  <option value="opt1">First Option</option>
                  <option value="opt2">Second Option</option>
                  <option value="opt3">Third Option</option>
                  <option value="opt4">Fourth Option</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Checkboxes & Radios -->
      <div class="component-section">
        <h2>Checkboxes & Radio Buttons</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Checkboxes</h3>
            <div class="demo-area">
              <div class="form-group">
                <label class="checkbox-label">
                  <input type="checkbox" bind:checked={checkboxValue} />
                  <span>Enable notifications</span>
                </label>
                <label class="checkbox-label">
                  <input type="checkbox" />
                  <span>Subscribe to newsletter</span>
                </label>
                <label class="checkbox-label">
                  <input type="checkbox" disabled />
                  <span>Disabled option</span>
                </label>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Radio Buttons</h3>
            <div class="demo-area">
              <div class="form-group">
                <label class="radio-label">
                  <input type="radio" name="radio-demo" value="radio1" bind:group={radioValue} />
                  <span>Option A</span>
                </label>
                <label class="radio-label">
                  <input type="radio" name="radio-demo" value="radio2" bind:group={radioValue} />
                  <span>Option B</span>
                </label>
                <label class="radio-label">
                  <input type="radio" name="radio-demo" value="radio3" bind:group={radioValue} />
                  <span>Option C</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- File Inputs -->
      <div class="component-section">
        <h2>File Inputs</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Basic File Input</h3>
            <div class="demo-area">
              <div class="form-group">
                <label for="file-basic">Choose File</label>
                <input 
                  id="file-basic"
                  type="file" 
                  class="form-control-file"
                  accept=".jpg,.jpeg,.png"
                />
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Custom File Upload</h3>
            <div class="demo-area">
              <div class="file-upload-wrapper">
                <input 
                  id="file-custom"
                  type="file" 
                  class="file-input-hidden"
                  multiple
                />
                <label for="file-custom" class="file-upload-label">
                  <Icon name="cloud-upload" size={24} />
                  <span>Click to upload or drag and drop</span>
                  <small>PNG, JPG up to 10MB</small>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Form States -->
      <div class="component-section">
        <h2>Form Validation States</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Success State</h3>
            <div class="demo-area">
              <div class="form-group">
                <label for="input-success">Username</label>
                <input 
                  id="input-success"
                  type="text" 
                  class="form-control is-valid" 
                  value="validusername"
                />
                <small class="form-text text-success">Username is available!</small>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Error State</h3>
            <div class="demo-area">
              <div class="form-group">
                <label for="input-error">Email</label>
                <input 
                  id="input-error"
                  type="email" 
                  class="form-control is-invalid" 
                  value="invalid-email"
                />
                <small class="form-text text-danger">Please enter a valid email address</small>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Disabled State</h3>
            <div class="demo-area">
              <div class="form-group">
                <label for="input-disabled">Disabled Input</label>
                <input 
                  id="input-disabled"
                  type="text" 
                  class="form-control" 
                  value="Cannot edit this"
                  disabled
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Form Layouts -->
      <div class="component-section">
        <h2>Form Layouts</h2>
        <div class="component-grid large">
          <div class="component-demo">
            <h3>Inline Form</h3>
            <div class="demo-area">
              <form class="form-inline">
                <div class="form-group">
                  <label for="inline-email">Email</label>
                  <input id="inline-email" type="email" class="form-control" placeholder="Email" />
                </div>
                <div class="form-group">
                  <label for="inline-password">Password</label>
                  <input id="inline-password" type="password" class="form-control" placeholder="Password" />
                </div>
                <Button variant="primary" size="sm">Sign In</Button>
              </form>
            </div>
          </div>

          <div class="component-demo">
            <h3>Form with Grid</h3>
            <div class="demo-area">
              <form class="form-grid">
                <div class="form-row">
                  <div class="form-group col">
                    <label for="grid-first">First Name</label>
                    <input id="grid-first" type="text" class="form-control" />
                  </div>
                  <div class="form-group col">
                    <label for="grid-last">Last Name</label>
                    <input id="grid-last" type="text" class="form-control" />
                  </div>
                </div>
                <div class="form-group">
                  <label for="grid-email">Email</label>
                  <input id="grid-email" type="email" class="form-control" />
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- Back to Dev -->
  <section class="dev-nav">
    <div class="container">
      <Button href="/dev" variant="ghost">← Back to Dev Dashboard</Button>
    </div>
  </section>
</main>

<Footer />

<style>
  @import '/css/upload-page.css';

  .component-gallery {
    min-height: 100vh;
    background-color: #f8f9fa;
  }

  .gallery-content {
    padding: 4rem 0;
  }

  .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
  }

  .component-section {
    margin-bottom: 4rem;
  }

  .component-section h2 {
    font-size: 2rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid #e2e8f0;
  }

  .component-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 2rem;
  }

  .component-grid.large {
    grid-template-columns: repeat(auto-fill, minmax(500px, 1fr));
  }

  .component-demo {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .component-demo h3 {
    font-size: 1.125rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 1rem;
  }

  .demo-area {
    padding: 2rem;
    background: #f8f9fa;
    border-radius: 8px;
    margin-bottom: 1rem;
  }

  .code-snippet {
    background: #1e293b;
    border-radius: 6px;
    padding: 1rem;
    overflow-x: auto;
  }

  .code-snippet code {
    color: #e2e8f0;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 0.875rem;
    white-space: pre;
  }

  /* Form styles */
  .form-group {
    margin-bottom: 1rem;
  }

  .form-group:last-child {
    margin-bottom: 0;
  }

  label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #475569;
    font-size: 0.875rem;
  }

  .form-control {
    display: block;
    width: 100%;
    padding: 0.625rem 1rem;
    font-size: 1rem;
    line-height: 1.5;
    color: #1e293b;
    background-color: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
  }

  .form-control:focus {
    outline: none;
    border-color: #5dade2;
    box-shadow: 0 0 0 3px rgba(93, 173, 226, 0.1);
  }

  .form-control.is-valid {
    border-color: #22c55e;
  }

  .form-control.is-invalid {
    border-color: #ef4444;
  }

  .form-control:disabled {
    background-color: #f1f5f9;
    opacity: 0.6;
    cursor: not-allowed;
  }

  .form-text {
    display: block;
    margin-top: 0.25rem;
    font-size: 0.875rem;
    color: #64748b;
  }

  .text-success {
    color: #22c55e;
  }

  .text-danger {
    color: #ef4444;
  }

  /* Search input */
  .search-input {
    position: relative;
  }

  .search-input :global(.icon) {
    position: absolute;
    left: 1rem;
    top: 50%;
    transform: translateY(-50%);
    color: #94a3b8;
  }

  .search-input input {
    padding-left: 3rem;
  }

  /* Range slider */
  .slider {
    width: 100%;
    height: 6px;
    border-radius: 3px;
    background: #e2e8f0;
    outline: none;
    margin: 1rem 0;
    -webkit-appearance: none;
  }

  .slider::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #5dade2;
    cursor: pointer;
    transition: transform 0.2s;
  }

  .slider::-webkit-slider-thumb:hover {
    transform: scale(1.1);
  }

  .slider::-moz-range-thumb {
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: #5dade2;
    cursor: pointer;
    transition: transform 0.2s;
  }

  .range-labels {
    display: flex;
    justify-content: space-between;
    font-size: 0.75rem;
    color: #94a3b8;
  }

  /* Textarea */
  textarea.form-control {
    resize: none;
  }

  textarea.resizable {
    resize: vertical;
    min-height: 80px;
    max-height: 300px;
  }

  /* Select */
  select.form-control {
    cursor: pointer;
  }

  select[multiple] {
    padding: 0.5rem;
  }

  select[multiple] option {
    padding: 0.25rem 0.5rem;
  }

  /* Checkboxes and Radios */
  .checkbox-label,
  .radio-label {
    display: flex;
    align-items: center;
    margin-bottom: 0.5rem;
    cursor: pointer;
    font-weight: normal;
  }

  .checkbox-label input,
  .radio-label input {
    margin-right: 0.5rem;
    cursor: pointer;
  }

  .checkbox-label input:disabled,
  .radio-label input:disabled {
    cursor: not-allowed;
  }

  .checkbox-label input:disabled + span,
  .radio-label input:disabled + span {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* File upload */
  .form-control-file {
    display: block;
    width: 100%;
    padding: 0.375rem 0;
    font-size: 1rem;
    line-height: 1.5;
    color: #475569;
  }

  .file-upload-wrapper {
    position: relative;
  }

  .file-input-hidden {
    position: absolute;
    opacity: 0;
    width: 0;
    height: 0;
  }

  .file-upload-label {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    border: 2px dashed #e2e8f0;
    border-radius: 8px;
    background: white;
    cursor: pointer;
    transition: all 0.2s;
    text-align: center;
  }

  .file-upload-label:hover {
    border-color: #5dade2;
    background: #f0f9ff;
  }

  .file-upload-label :global(.icon) {
    color: #5dade2;
    margin-bottom: 0.5rem;
  }

  .file-upload-label span {
    color: #475569;
    font-weight: 500;
  }

  .file-upload-label small {
    display: block;
    margin-top: 0.25rem;
    color: #94a3b8;
    font-size: 0.875rem;
  }

  /* Form layouts */
  .form-inline {
    display: flex;
    align-items: flex-end;
    gap: 1rem;
  }

  .form-inline .form-group {
    flex: 1;
    margin-bottom: 0;
  }

  .form-grid .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .dev-nav {
    padding: 2rem 0;
    border-top: 1px solid #e2e8f0;
  }

  /* Override hero gradient text */
  :global(.component-gallery .hero h1) {
    background: none !important;
    -webkit-text-fill-color: white !important;
    color: white !important;
  }
</style>