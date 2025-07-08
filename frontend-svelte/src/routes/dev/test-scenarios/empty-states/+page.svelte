<script>
  import Navbar from '$lib/components/Navbar.svelte';
  import Footer from '$lib/components/Footer.svelte';
  import Button from '$lib/components/Button.svelte';
  import Hero from '$lib/components/Hero.svelte';
  import Icon from '$lib/components/Icon.svelte';
</script>

<Navbar />

<main class="component-gallery">
  <Hero 
    title="Empty States Showcase"
    subtitle="UI patterns for when there's no data to display"
  />
  
  <section class="gallery-content">
    <div class="container">
      <!-- Upload Empty States -->
      <div class="component-section">
        <h2>Upload Page Empty States</h2>
        <div class="component-grid large">
          <div class="component-demo">
            <h3>No Files Selected</h3>
            <div class="demo-area large">
              <div class="empty-state">
                <div class="empty-icon">
                  <Icon name="cloud-upload" size={64} />
                </div>
                <h3>No images uploaded yet</h3>
                <p>Drag and drop your images here or click to browse</p>
                <Button variant="primary">
                  <Icon name="upload" size={20} />
                  Select Images
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Results Empty States -->
      <div class="component-section">
        <h2>Results Page Empty States</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>No Models Generated</h3>
            <div class="demo-area">
              <div class="empty-state">
                <Icon name="info" size={64} color="#94a3b8" />
                <h3>No models generated</h3>
                <p>The processing completed but no 3D models were generated.</p>
                <Button href="/upload" variant="primary">Try Again</Button>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Processing Failed</h3>
            <div class="demo-area">
              <div class="empty-state error">
                <Icon name="x-circle" size={64} color="#ef4444" />
                <h3>Processing Failed</h3>
                <p>Unable to generate 3D models from your images.</p>
                <Button href="/upload" variant="primary">Upload New Images</Button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Search Empty States -->
      <div class="component-section">
        <h2>Search & Filter Empty States</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>No Search Results</h3>
            <div class="demo-area">
              <div class="empty-state">
                <Icon name="search" size={64} color="#94a3b8" />
                <h3>No results found</h3>
                <p>Try adjusting your search criteria or filters</p>
                <Button variant="ghost">Clear Filters</Button>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>No Matching Items</h3>
            <div class="demo-area">
              <div class="empty-state">
                <Icon name="filter" size={64} color="#94a3b8" />
                <h3>No items match your filters</h3>
                <p>Try removing some filters to see more results</p>
                <div class="button-group">
                  <Button variant="ghost" size="sm">Reset Filters</Button>
                  <Button variant="primary" size="sm">Browse All</Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- List Empty States -->
      <div class="component-section">
        <h2>List & Table Empty States</h2>
        <div class="component-grid large">
          <div class="component-demo">
            <h3>Empty Table</h3>
            <div class="demo-area">
              <div class="table-container">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th>File Name</th>
                      <th>Size</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td colspan="4">
                        <div class="empty-state inline">
                          <Icon name="document" size={48} color="#94a3b8" />
                          <div>
                            <h4>No files uploaded</h4>
                            <p>Upload some images to get started</p>
                          </div>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Empty List</h3>
            <div class="demo-area">
              <div class="list-container">
                <div class="list-header">
                  <h4>Recent Projects</h4>
                  <Button variant="primary" size="sm">New Project</Button>
                </div>
                <div class="empty-state">
                  <Icon name="folder" size={64} color="#94a3b8" />
                  <h3>No projects yet</h3>
                  <p>Create your first project to see it here</p>
                  <Button variant="primary">
                    <Icon name="plus" size={20} />
                    Create Project
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Feature-Specific Empty States -->
      <div class="component-section">
        <h2>Feature-Specific Empty States</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>No Notifications</h3>
            <div class="demo-area">
              <div class="empty-state small">
                <Icon name="bell" size={48} color="#94a3b8" />
                <h4>No new notifications</h4>
                <p>You're all caught up!</p>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>No History</h3>
            <div class="demo-area">
              <div class="empty-state small">
                <Icon name="clock" size={48} color="#94a3b8" />
                <h4>No processing history</h4>
                <p>Your completed jobs will appear here</p>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>No Favorites</h3>
            <div class="demo-area">
              <div class="empty-state small">
                <Icon name="star" size={48} color="#94a3b8" />
                <h4>No favorites saved</h4>
                <p>Star your best models to access them quickly</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Contextual Empty States -->
      <div class="component-section">
        <h2>Contextual Empty States</h2>
        <div class="component-grid">
          <div class="component-demo">
            <h3>First Time User</h3>
            <div class="demo-area">
              <div class="empty-state welcome">
                <div class="welcome-icon">
                  <Icon name="cube" size={64} />
                </div>
                <h3>Welcome to Image2Model!</h3>
                <p>Transform your 2D images into stunning 3D models in minutes</p>
                <Button variant="primary" size="lg">
                  Start Your First Project
                </Button>
                <a href="#" class="help-link">Watch Tutorial</a>
              </div>
            </div>
          </div>

          <div class="component-demo">
            <h3>Permission Denied</h3>
            <div class="demo-area">
              <div class="empty-state error">
                <Icon name="lock" size={64} color="#ef4444" />
                <h3>Access Denied</h3>
                <p>You don't have permission to view this content</p>
                <Button variant="ghost">Request Access</Button>
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
    min-height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .demo-area.large {
    min-height: 300px;
  }

  /* Empty state styles */
  .empty-state {
    text-align: center;
    padding: 3rem;
    max-width: 400px;
  }

  .empty-state.small {
    padding: 2rem;
    max-width: 300px;
  }

  .empty-state.inline {
    display: flex;
    align-items: center;
    gap: 1.5rem;
    text-align: left;
    padding: 2rem;
  }

  .empty-state h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #1e293b;
    margin: 1rem 0 0.5rem;
  }

  .empty-state h4 {
    font-size: 1rem;
    font-weight: 600;
    color: #1e293b;
    margin: 0.5rem 0;
  }

  .empty-state p {
    color: #64748b;
    margin: 0 0 1.5rem;
    line-height: 1.5;
  }

  .empty-state.error h3 {
    color: #dc2626;
  }

  .empty-icon {
    color: #94a3b8;
    margin-bottom: 1rem;
  }

  .welcome-icon {
    width: 80px;
    height: 80px;
    margin: 0 auto 1rem;
    background: linear-gradient(135deg, #5dade2 0%, #3498db 100%);
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
  }

  .button-group {
    display: flex;
    gap: 0.75rem;
    justify-content: center;
  }

  .help-link {
    display: inline-block;
    margin-top: 1rem;
    color: #5dade2;
    text-decoration: none;
    font-size: 0.875rem;
  }

  .help-link:hover {
    text-decoration: underline;
  }

  /* Table styles */
  .table-container {
    width: 100%;
    overflow-x: auto;
  }

  .data-table {
    width: 100%;
    border-collapse: collapse;
  }

  .data-table th {
    text-align: left;
    padding: 0.75rem 1rem;
    font-weight: 500;
    color: #475569;
    border-bottom: 1px solid #e2e8f0;
    background: white;
  }

  .data-table td {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid #f1f5f9;
  }

  /* List styles */
  .list-container {
    background: white;
    border-radius: 8px;
    overflow: hidden;
  }

  .list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 1.5rem;
    border-bottom: 1px solid #e2e8f0;
  }

  .list-header h4 {
    margin: 0;
    font-size: 1.125rem;
    font-weight: 600;
    color: #1e293b;
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