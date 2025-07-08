<script>
  import Navbar from '$lib/components/Navbar.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import Button from '$lib/components/Button.svelte';
  import Hero from '$lib/components/Hero.svelte';
  import Icon from '$lib/components/Icon.svelte';
  
  // All available icons from the Icon component
  const iconCategories = {
    'Success/Status': [
      { name: 'check', label: 'Check' },
      { name: 'check-circle', label: 'Check Circle' },
      { name: 'info', label: 'Info' },
      { name: 'warning', label: 'Warning' },
      { name: 'error', label: 'Error' },
      { name: 'x', label: 'Close' },
      { name: 'x-circle', label: 'Close Circle' }
    ],
    'File/Document': [
      { name: 'folder', label: 'Folder' },
      { name: 'document', label: 'Document' },
      { name: 'cube', label: '3D Cube' }
    ],
    'Actions': [
      { name: 'download', label: 'Download' },
      { name: 'upload', label: 'Upload' },
      { name: 'cloud-download', label: 'Cloud Download' },
      { name: 'eye', label: 'View' },
      { name: 'external-link', label: 'External Link' },
      { name: 'cog', label: 'Settings' },
      { name: 'key', label: 'Key/Security' }
    ],
    'Navigation': [
      { name: 'arrow-down', label: 'Arrow Down' },
      { name: 'chevron-down', label: 'Chevron Down' },
      { name: 'chevron-right', label: 'Chevron Right' }
    ],
    'Time': [
      { name: 'clock', label: 'Clock' }
    ]
  };
  
  // Sizes to demonstrate
  const sizes = [16, 20, 24, 32, 48];
  
  // Colors to demonstrate
  const colors = [
    { value: 'currentColor', label: 'Current Color', bg: 'light' },
    { value: '#5DADE2', label: 'Primary Blue', bg: 'light' },
    { value: '#3498DB', label: 'Blue', bg: 'light' },
    { value: '#22c55e', label: 'Success', bg: 'light' },
    { value: '#ef4444', label: 'Error', bg: 'light' },
    { value: '#f59e0b', label: 'Warning', bg: 'light' },
    { value: '#ffffff', label: 'White', bg: 'dark' },
    { value: '#1e293b', label: 'Dark', bg: 'light' }
  ];
  
  let selectedSize = 24;
  let selectedColor = 'currentColor';
  let searchQuery = '';
  
  // Filter icons based on search
  $: filteredCategories = Object.entries(iconCategories).reduce((acc, [category, icons]) => {
    const filtered = icons.filter(icon => 
      icon.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      icon.label.toLowerCase().includes(searchQuery.toLowerCase())
    );
    if (filtered.length > 0) {
      acc[category] = filtered;
    }
    return acc;
  }, {});
</script>

<Navbar />

<main class="icon-gallery">
  <Hero 
    title="Icon Component Gallery"
    subtitle="All available icons with size and color variations"
  />
  
  <section class="gallery-content">
    <div class="container">
      <!-- Controls -->
      <div class="controls-section">
        <div class="control-group">
          <label for="search">Search Icons</label>
          <input 
            id="search"
            type="text" 
            placeholder="Search by name..." 
            bind:value={searchQuery}
            class="search-input"
          />
        </div>
        
        <div class="control-group">
          <label>Size</label>
          <div class="size-buttons">
            {#each sizes as size}
              <button 
                class="size-btn {selectedSize === size ? 'active' : ''}"
                on:click={() => selectedSize = size}
              >
                {size}px
              </button>
            {/each}
          </div>
        </div>
        
        <div class="control-group">
          <label>Color</label>
          <div class="color-buttons">
            {#each colors as color}
              <button 
                class="color-btn {selectedColor === color.value ? 'active' : ''}"
                style="background-color: {color.value === 'currentColor' ? '#64748b' : color.value}"
                on:click={() => selectedColor = color.value}
                title={color.label}
              ></button>
            {/each}
          </div>
        </div>
      </div>

      <!-- Icon Categories -->
      {#each Object.entries(filteredCategories) as [category, icons]}
        <div class="icon-category">
          <h2>{category}</h2>
          <div class="icon-grid">
            {#each icons as icon}
              <div class="icon-item">
                <div class="icon-preview {colors.find(c => c.value === selectedColor)?.bg === 'dark' ? 'dark-bg' : ''}">
                  <Icon name={icon.name} size={selectedSize} color={selectedColor} />
                </div>
                <div class="icon-info">
                  <span class="icon-name">{icon.label}</span>
                  <code class="icon-code">{icon.name}</code>
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/each}
      
      {#if Object.keys(filteredCategories).length === 0}
        <div class="no-results">
          <Icon name="info" size={48} color="#94a3b8" />
          <p>No icons found matching "{searchQuery}"</p>
        </div>
      {/if}

      <!-- Usage Examples -->
      <div class="usage-section">
        <h2>Usage Examples</h2>
        <div class="example-grid">
          <div class="example-card">
            <h3>Basic Usage</h3>
            <div class="example-demo">
              <Icon name="check" />
            </div>
            <div class="code-snippet">
              <code>{`<Icon name="check" />`}</code>
            </div>
          </div>

          <div class="example-card">
            <h3>With Size</h3>
            <div class="example-demo">
              <Icon name="download" size={32} />
            </div>
            <div class="code-snippet">
              <code>{`<Icon name="download" size={32} />`}</code>
            </div>
          </div>

          <div class="example-card">
            <h3>With Color</h3>
            <div class="example-demo">
              <Icon name="warning" size={24} color="#f59e0b" />
            </div>
            <div class="code-snippet">
              <code>{`<Icon name="warning" size={24} color="#f59e0b" />`}</code>
            </div>
          </div>

          <div class="example-card">
            <h3>In Button</h3>
            <div class="example-demo">
              <Button variant="primary" size="sm">
                <Icon name="upload" size={16} />
                Upload
              </Button>
            </div>
            <div class="code-snippet">
              <code>{`<Button variant="primary" size="sm">
  <Icon name="upload" size={16} />
  Upload
</Button>`}</code>
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
  .icon-gallery {
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

  /* Controls */
  .controls-section {
    background: white;
    border-radius: 12px;
    padding: 2rem;
    margin-bottom: 3rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    display: grid;
    grid-template-columns: 1fr auto auto;
    gap: 2rem;
    align-items: end;
  }

  .control-group label {
    display: block;
    font-size: 0.875rem;
    font-weight: 600;
    color: #475569;
    margin-bottom: 0.5rem;
  }

  .search-input {
    width: 100%;
    padding: 0.5rem 1rem;
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    font-size: 1rem;
    transition: border-color 0.2s;
  }

  .search-input:focus {
    outline: none;
    border-color: #5dade2;
  }

  .size-buttons {
    display: flex;
    gap: 0.5rem;
  }

  .size-btn {
    padding: 0.5rem 1rem;
    border: 1px solid #e2e8f0;
    background: white;
    border-radius: 6px;
    font-size: 0.875rem;
    cursor: pointer;
    transition: all 0.2s;
  }

  .size-btn:hover {
    border-color: #5dade2;
  }

  .size-btn.active {
    background: #5dade2;
    color: white;
    border-color: #5dade2;
  }

  .color-buttons {
    display: flex;
    gap: 0.5rem;
  }

  .color-btn {
    width: 32px;
    height: 32px;
    border: 2px solid transparent;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .color-btn:hover {
    transform: scale(1.1);
  }

  .color-btn.active {
    border-color: #1e293b;
    box-shadow: 0 0 0 2px white, 0 0 0 4px #1e293b;
  }

  /* Icon Categories */
  .icon-category {
    margin-bottom: 3rem;
  }

  .icon-category h2 {
    font-size: 1.5rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 2px solid #e2e8f0;
  }

  .icon-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 1rem;
  }

  .icon-item {
    background: white;
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
    transition: all 0.2s;
    border: 1px solid #e2e8f0;
  }

  .icon-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .icon-preview {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 0.75rem;
    border-radius: 6px;
    background: #f8f9fa;
  }

  .icon-preview.dark-bg {
    background: #1e293b;
  }

  .icon-info {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }

  .icon-name {
    font-size: 0.875rem;
    font-weight: 600;
    color: #1e293b;
  }

  .icon-code {
    font-size: 0.75rem;
    color: #64748b;
    font-family: monospace;
    background: #f1f5f9;
    padding: 0.125rem 0.5rem;
    border-radius: 4px;
  }

  /* No Results */
  .no-results {
    text-align: center;
    padding: 4rem 2rem;
    color: #94a3b8;
  }

  .no-results p {
    margin-top: 1rem;
    font-size: 1.125rem;
  }

  /* Usage Examples */
  .usage-section {
    margin-top: 4rem;
  }

  .usage-section h2 {
    font-size: 2rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid #e2e8f0;
  }

  .example-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
  }

  .example-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }

  .example-card h3 {
    font-size: 1.125rem;
    font-weight: 600;
    color: #1e293b;
    margin-bottom: 1rem;
  }

  .example-demo {
    padding: 1.5rem;
    background: #f8f9fa;
    border-radius: 8px;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 60px;
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

  .dev-nav {
    padding: 2rem 0;
    border-top: 1px solid #e2e8f0;
  }

  /* Override hero gradient text */
  :global(.icon-gallery .hero h1) {
    background: none !important;
    -webkit-text-fill-color: white !important;
    color: white !important;
  }

  /* Responsive */
  @media (max-width: 768px) {
    .controls-section {
      grid-template-columns: 1fr;
    }
    
    .icon-grid {
      grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    }
  }
</style>