<script>
  import Navbar from '$lib/components/Navbar.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import Button from '$lib/components/Button.svelte';
  import Hero from '$lib/components/Hero.svelte';
  import Icon from '$lib/components/Icon.svelte';
  import ModelCard from '$lib/components/ModelCard.svelte';
  
  // Mock data for edge cases
  const longFileName = {
    filename: 'this-is-a-very-long-filename-that-might-cause-layout-issues-in-the-ui-when-displayed.glb',
    name: 'this-is-a-very-long-filename-that-might-cause-layout-issues-in-the-ui-when-displayed.glb',
    size: 2457600,
    downloadUrl: '#',
    mimeType: 'model/gltf-binary',
    createdTime: new Date().toISOString(),
    rendered_image: { url: 'https://placehold.co/400x300/5DADE2/white?text=3D+Model' }
  };

  const tinyFile = {
    filename: 'tiny.glb',
    name: 'tiny.glb',
    size: 128, // 128 bytes
    downloadUrl: '#',
    mimeType: 'model/gltf-binary',
    createdTime: new Date().toISOString(),
    rendered_image: { url: 'https://placehold.co/400x300/5DADE2/white?text=Tiny' }
  };

  const hugeFile = {
    filename: 'massive-model.glb',
    name: 'massive-model.glb',
    size: 524288000, // 500 MB
    downloadUrl: '#',
    mimeType: 'model/gltf-binary',
    createdTime: new Date().toISOString(),
    rendered_image: null
  };
</script>

<Navbar />

<main class="component-gallery">
  <Hero 
    title="Edge Cases Showcase"
    subtitle="Testing UI with extreme and unusual data"
  />
  
  <section class="gallery-content">
    <div class="container">
      <!-- Text Edge Cases -->
      <div class="component-section">
        <h2>Text Content Edge Cases</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Very Long Text</h3>
            <div class="demo-area">
              <div class="text-card">
                <h4 class="text-truncate">ThisIsAVeryLongWordWithNoSpacesThatMightBreakTheLayoutIfNotHandledProperly</h4>
                <p class="text-wrap">This is a very long description that contains a lot of text and might need to wrap to multiple lines. It's important to test how the UI handles long text content to ensure readability and proper layout behavior across different screen sizes and devices.</p>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Special Characters</h3>
            <div class="demo-area">
              <div class="text-card">
                <h4>File: <>&"'`{}[]()*.jpg</h4>
                <p>Unicode: 你好世界 🌍 مرحبا بالعالم</p>
                <code>Path: C:\Users\John's Files\Images & Videos\</code>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Empty/Minimal Text</h3>
            <div class="demo-area">
              <div class="text-card">
                <h4> </h4>
                <p></p>
                <span class="label">Label:</span> <span class="value"></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Number Edge Cases -->
      <div class="component-section">
        <h2>Number & Data Edge Cases</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Extreme Numbers</h3>
            <div class="demo-area">
              <div class="stats-card">
                <div class="stat">
                  <span class="stat-label">Files:</span>
                  <span class="stat-value">999,999</span>
                </div>
                <div class="stat">
                  <span class="stat-label">Size:</span>
                  <span class="stat-value">9.99 PB</span>
                </div>
                <div class="stat">
                  <span class="stat-label">Progress:</span>
                  <span class="stat-value">0.001%</span>
                </div>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Progress Edge Cases</h3>
            <div class="demo-area">
              <div class="progress-examples">
                <div class="progress-item">
                  <label>0%</label>
                  <div class="progress">
                    <div class="progress-bar" style="width: 0%"></div>
                  </div>
                </div>
                <div class="progress-item">
                  <label>99.9%</label>
                  <div class="progress">
                    <div class="progress-bar" style="width: 99.9%"></div>
                  </div>
                </div>
                <div class="progress-item">
                  <label>100%</label>
                  <div class="progress">
                    <div class="progress-bar" style="width: 100%"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Time Edge Cases</h3>
            <div class="demo-area">
              <div class="time-examples">
                <div class="time-item">
                  <Icon name="clock" size={20} />
                  <span>Processing time: 0s</span>
                </div>
                <div class="time-item">
                  <Icon name="clock" size={20} />
                  <span>Processing time: 23h 59m 59s</span>
                </div>
                <div class="time-item">
                  <Icon name="clock" size={20} />
                  <span>Started: 1 year ago</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- File Edge Cases -->
      <div class="component-section">
        <h2>File Handling Edge Cases</h2>
        <div class="component-grid large">
          <div class="component-demo">
            <h3>Long Filename</h3>
            <div class="demo-area">
              <ModelCard file={longFileName} jobId="test-long" />
            </div>
          </div>

          <div class="component-demo">
            <h3>File Size Extremes</h3>
            <div class="demo-area">
              <div class="file-list">
                <div class="file-item">
                  <Icon name="document" size={20} />
                  <span class="file-name">tiny.jpg</span>
                  <span class="file-size">128 B</span>
                </div>
                <div class="file-item">
                  <Icon name="document" size={20} />
                  <span class="file-name">huge.jpg</span>
                  <span class="file-size">500 MB</span>
                </div>
                <div class="file-item">
                  <Icon name="document" size={20} />
                  <span class="file-name">zero.jpg</span>
                  <span class="file-size">0 B</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- List Edge Cases -->
      <div class="component-section">
        <h2>List & Collection Edge Cases</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Single Item List</h3>
            <div class="demo-area">
              <div class="item-list">
                <div class="list-item">
                  <Icon name="cube" size={20} />
                  <span>Only one item in this list</span>
                </div>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Many Items (Scrollable)</h3>
            <div class="demo-area">
              <div class="item-list scrollable">
                {#each Array(50) as _, i}
                  <div class="list-item">
                    <Icon name="document" size={16} />
                    <span>Item {i + 1} of 50</span>
                  </div>
                {/each}
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Mixed Content Heights</h3>
            <div class="demo-area">
              <div class="mixed-list">
                <div class="mixed-item small">
                  <h5>Small</h5>
                  <p>One line</p>
                </div>
                <div class="mixed-item medium">
                  <h5>Medium Item</h5>
                  <p>This item has more content than the others and takes up more vertical space in the layout.</p>
                </div>
                <div class="mixed-item large">
                  <h5>Large Item with Lots of Content</h5>
                  <p>This item contains significantly more content including multiple paragraphs of text.</p>
                  <p>It's important to test how mixed content heights affect the overall layout and visual balance.</p>
                  <Button size="sm" variant="ghost">Action</Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Form Edge Cases -->
      <div class="component-section">
        <h2>Form Input Edge Cases</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Input Limits</h3>
            <div class="demo-area">
              <form class="edge-form">
                <div class="form-group">
                  <label>Max Length (10 chars)</label>
                  <input type="text" class="form-control" maxlength="10" value="1234567890" />
                </div>
                <div class="form-group">
                  <label>Number Range (1-5)</label>
                  <input type="number" class="form-control" min="1" max="5" value="6" />
                </div>
                <div class="form-group">
                  <label>Decimal Precision</label>
                  <input type="number" class="form-control" step="0.001" value="3.14159265359" />
                </div>
              </form>
            </div>
          </div>

          <div class="component-demo">
            <h3>Disabled States</h3>
            <div class="demo-area">
              <div class="disabled-examples">
                <Button disabled>Disabled Button</Button>
                <input type="text" class="form-control" disabled value="Disabled input" />
                <label class="checkbox-label disabled">
                  <input type="checkbox" disabled checked />
                  <span>Disabled checkbox</span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Layout Edge Cases -->
      <div class="component-section">
        <h2>Layout Edge Cases</h2>
        <div class="component-grid large">
          <div class="component-demo">
            <h3>Responsive Breakpoints</h3>
            <div class="demo-area">
              <div class="responsive-test">
                <div class="breakpoint-indicator">
                  <span class="mobile-only">Mobile View</span>
                  <span class="tablet-only">Tablet View</span>
                  <span class="desktop-only">Desktop View</span>
                </div>
                <div class="responsive-grid">
                  <div class="grid-item">1</div>
                  <div class="grid-item">2</div>
                  <div class="grid-item">3</div>
                  <div class="grid-item">4</div>
                </div>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Content Overflow</h3>
            <div class="demo-area">
              <div class="overflow-container">
                <div class="overflow-box">
                  <p>ThisIsAVeryLongWordThatWillCauseHorizontalOverflowIfNotHandledProperlyInTheLayout</p>
                </div>
                <div class="overflow-box clipped">
                  <p>This content is clipped when it overflows the container boundaries.</p>
                </div>
                <div class="overflow-box scrollable">
                  <p>This content becomes scrollable when it exceeds the container size. Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Performance Edge Cases -->
      <div class="component-section">
        <h2>Performance Edge Cases</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>Rapid State Changes</h3>
            <div class="demo-area">
              <div class="performance-test">
                <p>Test rapid updates:</p>
                <div class="rapid-counter">
                  <span class="counter-value">0</span>
                  <small>Updates every 100ms</small>
                </div>
                <Button variant="primary" size="sm">Start Rapid Updates</Button>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Heavy DOM Elements</h3>
            <div class="demo-area">
              <div class="heavy-dom">
                <p>Complex nested structure:</p>
                <div class="nested-1">
                  <div class="nested-2">
                    <div class="nested-3">
                      <div class="nested-4">
                        <div class="nested-5">
                          Deeply nested content
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
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
    grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
    gap: 2rem;
  }

  .component-grid.large {
    grid-template-columns: repeat(auto-fill, minmax(600px, 1fr));
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
    min-height: 150px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  /* Text edge cases */
  .text-card {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    width: 100%;
    max-width: 300px;
  }

  .text-card h4 {
    margin: 0 0 0.5rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: #1e293b;
  }

  .text-card p {
    margin: 0 0 0.5rem 0;
    color: #64748b;
    font-size: 0.875rem;
  }

  .text-card code {
    display: block;
    padding: 0.5rem;
    background: #f1f5f9;
    border-radius: 4px;
    font-size: 0.75rem;
    overflow-x: auto;
  }

  .text-truncate {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .text-wrap {
    word-wrap: break-word;
    overflow-wrap: break-word;
  }

  /* Stats card */
  .stats-card {
    display: flex;
    gap: 2rem;
    padding: 1rem;
    background: white;
    border-radius: 8px;
  }

  .stat {
    text-align: center;
  }

  .stat-label {
    display: block;
    font-size: 0.875rem;
    color: #64748b;
    margin-bottom: 0.25rem;
  }

  .stat-value {
    display: block;
    font-size: 1.5rem;
    font-weight: 600;
    color: #1e293b;
  }

  /* Progress examples */
  .progress-examples {
    width: 100%;
    max-width: 300px;
  }

  .progress-item {
    margin-bottom: 1rem;
  }

  .progress-item label {
    display: block;
    margin-bottom: 0.25rem;
    font-size: 0.875rem;
    color: #64748b;
  }

  .progress {
    width: 100%;
    height: 0.5rem;
    background: #e2e8f0;
    border-radius: 0.25rem;
    overflow: hidden;
  }

  .progress-bar {
    height: 100%;
    background: #5dade2;
    transition: width 0.3s ease;
  }

  /* Time examples */
  .time-examples {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .time-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    background: white;
    border-radius: 6px;
    font-size: 0.875rem;
    color: #64748b;
  }

  /* File list */
  .file-list {
    background: white;
    border-radius: 8px;
    overflow: hidden;
  }

  .file-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid #f1f5f9;
  }

  .file-item:last-child {
    border-bottom: none;
  }

  .file-name {
    flex: 1;
    font-size: 0.875rem;
    color: #1e293b;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .file-size {
    font-size: 0.75rem;
    color: #94a3b8;
  }

  /* Item list */
  .item-list {
    background: white;
    border-radius: 8px;
    padding: 0.5rem;
    width: 100%;
  }

  .item-list.scrollable {
    max-height: 200px;
    overflow-y: auto;
  }

  .list-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem;
    font-size: 0.875rem;
    color: #64748b;
  }

  .list-item:hover {
    background: #f8f9fa;
    border-radius: 4px;
  }

  /* Mixed list */
  .mixed-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    width: 100%;
  }

  .mixed-item {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
  }

  .mixed-item h5 {
    margin: 0 0 0.5rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: #1e293b;
  }

  .mixed-item p {
    margin: 0 0 0.5rem 0;
    color: #64748b;
    font-size: 0.875rem;
    line-height: 1.5;
  }

  /* Form edge cases */
  .edge-form {
    width: 100%;
    max-width: 300px;
  }

  .form-group {
    margin-bottom: 1rem;
  }

  .form-group label {
    display: block;
    margin-bottom: 0.25rem;
    font-size: 0.875rem;
    color: #64748b;
  }

  .form-control {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    font-size: 0.875rem;
  }

  /* Disabled examples */
  .disabled-examples {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }

  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 0.875rem;
    color: #64748b;
  }

  .checkbox-label.disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* Responsive test */
  .responsive-test {
    width: 100%;
  }

  .breakpoint-indicator {
    text-align: center;
    margin-bottom: 1rem;
    font-weight: 600;
    color: #1e293b;
  }

  .mobile-only { display: none; }
  .tablet-only { display: none; }
  .desktop-only { display: block; }

  @media (max-width: 768px) {
    .mobile-only { display: block; }
    .tablet-only { display: none; }
    .desktop-only { display: none; }
  }

  @media (min-width: 769px) and (max-width: 1024px) {
    .mobile-only { display: none; }
    .tablet-only { display: block; }
    .desktop-only { display: none; }
  }

  .responsive-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 0.5rem;
  }

  .grid-item {
    background: #5dade2;
    color: white;
    padding: 1rem;
    text-align: center;
    border-radius: 6px;
    font-weight: 600;
  }

  /* Overflow examples */
  .overflow-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    width: 100%;
  }

  .overflow-box {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    padding: 1rem;
    max-width: 200px;
    font-size: 0.875rem;
    color: #64748b;
  }

  .overflow-box p {
    margin: 0;
  }

  .overflow-box.clipped {
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }

  .overflow-box.scrollable {
    max-height: 60px;
    overflow-y: auto;
  }

  /* Performance test */
  .performance-test {
    text-align: center;
  }

  .performance-test p {
    margin: 0 0 1rem 0;
    color: #64748b;
    font-size: 0.875rem;
  }

  .rapid-counter {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 1rem;
  }

  .counter-value {
    font-size: 2rem;
    font-weight: 600;
    color: #1e293b;
  }

  .rapid-counter small {
    font-size: 0.75rem;
    color: #94a3b8;
  }

  /* Nested structure */
  .heavy-dom p {
    margin: 0 0 1rem 0;
    color: #64748b;
    font-size: 0.875rem;
  }

  [class^="nested-"] {
    padding: 1rem;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    background: white;
  }

  .nested-1 { background: #f8f9fa; }
  .nested-2 { background: #f1f5f9; }
  .nested-3 { background: #e2e8f0; }
  .nested-4 { background: #cbd5e1; }
  .nested-5 { 
    background: #94a3b8;
    color: white;
    text-align: center;
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