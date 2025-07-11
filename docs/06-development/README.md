# Development Guide

> **Last Updated**: 2025-07-11  
> **Status**: Active  
> **Version**: 1.0

Everything you need to set up and maintain a productive development environment for image2model.

## 📋 In This Section

### Setup

- **[Local Development](./setup/local-development.md)** *(coming soon)* - Complete local setup guide
- **[Environment Variables](./setup/environment-vars.md)** *(coming soon)* - Configuration reference
- **[API Keys Guide](./setup/API_KEYS_GUIDE.md)** - Authentication setup ✓

### Workflows

- **[Development Flow](./workflows/development-flow.md)** *(coming soon)* - Best practices
- **[Debugging Guide](./workflows/debugging-guide.md)** *(coming soon)* - Troubleshooting tips
- **[Contribution Guide](./workflows/contribution-guide.md)** *(coming soon)* - How to contribute

### Tools

- **[VSCode Setup](./tools/vscode-setup.md)** *(coming soon)* - IDE configuration
- **[Linting & Formatting](./tools/linting-formatting.md)** *(coming soon)* - Code style
- **[DevContainer](./tools/devcontainer.md)** *(coming soon)* - Container development

## 🎯 Quick Start

### Prerequisites

- Git
- Docker & Docker Compose
- Node.js 18+ and npm
- Python 3.11+
- Redis (or use Docker)
- Code editor (VSCode recommended)

### One-Command Setup

```bash
# Clone and setup
git clone https://github.com/your-org/image2model.git
cd image2model
make setup  # Runs complete setup
```

### Manual Setup

```bash
# 1. Clone repository
git clone https://github.com/your-org/image2model.git
cd image2model

# 2. Copy environment file
cp .env.example .env
# Edit .env with your API keys

# 3. Start services with Docker
docker-compose up -d

# 4. Install frontend dependencies
cd frontend-svelte
npm install

# 5. Install backend dependencies
cd ../backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Run development servers
# Terminal 1: Frontend
cd frontend-svelte && npm run dev

# Terminal 2: Backend
cd backend && uvicorn app.main:app --reload

# Terminal 3: Celery worker
cd backend && celery -A app.core.celery_app worker --loglevel=info
```

## 📊 Development Environment

### Project Structure

```
image2model/
├── frontend-svelte/     # SvelteKit frontend
├── backend/            # FastAPI backend
├── docs/              # Documentation
├── tests/             # Integration tests
├── scripts/           # Utility scripts
├── docker/            # Docker configs
└── deployment/        # Deploy scripts
```

### Service Ports

| Service | Port | URL |
|---------|------|-----|
| Frontend | 5173 | http://localhost:5173 |
| Backend | 8000 | http://localhost:8000 |
| API Docs | 8000 | http://localhost:8000/docs |
| Redis | 6379 | redis://localhost:6379 |

### Environment Variables

Key variables to configure:

```bash
# API Authentication
API_KEY=your-internal-api-key
FAL_AI_KEY=your-fal-ai-key

# Service URLs
FRONTEND_URL=http://localhost:5173
BACKEND_URL=http://localhost:8000

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Development Settings
DEBUG=true
LOG_LEVEL=DEBUG
```

## 🔧 Common Tasks

### Running Tests

```bash
# Frontend tests
cd frontend-svelte
npm test                 # Unit tests
npm run test:e2e        # E2E tests

# Backend tests
cd backend
pytest                   # All tests
pytest -xvs             # Verbose with stop on failure
```

### Code Formatting

```bash
# Frontend
npm run format          # Format code
npm run lint           # Check linting

# Backend
black app/             # Format Python code
flake8 app/           # Lint Python code
```

### Database Tasks

```bash
# Redis operations
redis-cli              # Open Redis CLI
redis-cli FLUSHALL    # Clear all data (careful!)
redis-cli MONITOR     # Watch commands
```

### Docker Operations

```bash
# View logs
docker-compose logs -f backend

# Restart services
docker-compose restart

# Rebuild containers
docker-compose build

# Clean up
docker-compose down -v
```

## 🐛 Debugging

### Frontend Debugging

1. **Browser DevTools**: F12 for console, network, etc.
2. **Svelte DevTools**: Browser extension
3. **VSCode Debugger**: Launch configuration included
4. **Console Logging**: Strategic `console.log()`

### Backend Debugging

1. **FastAPI Docs**: Interactive API testing at `/docs`
2. **Python Debugger**: 
   ```python
   import pdb; pdb.set_trace()
   ```
3. **Logging**:
   ```python
   import logging
   logger = logging.getLogger(__name__)
   logger.debug("Debug message")
   ```
4. **VSCode Debugger**: Python debug config included

### Common Issues

#### Frontend Won't Start
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

#### Backend Import Errors
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### Celery Not Processing
```bash
# Check Redis connection
redis-cli ping  # Should return PONG

# Check Celery workers
celery -A app.core.celery_app inspect active
```

## 🔨 Development Tools

### Recommended Extensions

#### VSCode Extensions
- Svelte for VS Code
- Python
- Prettier
- ESLint
- GitLens
- Docker
- Thunder Client (API testing)

#### Browser Extensions
- Svelte DevTools
- React Developer Tools (works with Svelte)
- Redux DevTools

### Git Hooks

Pre-commit hooks for code quality:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Code Quality Tools

- **Frontend**: ESLint, Prettier
- **Backend**: Black, Flake8, mypy
- **Commits**: Conventional Commits
- **Documentation**: Markdown linting

## 🔄 Development Workflow

### Feature Development

1. **Create Branch**
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Develop Feature**
   - Write code
   - Add tests
   - Update documentation

3. **Test Locally**
   ```bash
   npm test
   pytest
   ```

4. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```

5. **Push and PR**
   ```bash
   git push origin feature/your-feature
   # Create PR on GitHub
   ```

### Code Review Process

- All code requires review
- Tests must pass
- Documentation updated
- No merge conflicts
- Follows style guide

## 🔗 Resources

### Internal Documentation

- [Architecture Overview](../01-getting-started/architecture-overview.md)
- [API Reference](../03-backend/api-reference/)
- [Component Library](../02-frontend/components/)

### External Resources

- [SvelteKit Tutorial](https://learn.svelte.dev/)
- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [Docker Documentation](https://docs.docker.com/)

### Development Channels

- GitHub Issues: Bug reports
- GitHub Discussions: Questions
- Pull Requests: Code reviews

## 💡 Best Practices

### Code Style

1. **Consistent naming**: Use clear, descriptive names
2. **Small commits**: One logical change per commit
3. **Test coverage**: Write tests for new code
4. **Documentation**: Update docs with changes
5. **Error handling**: Handle edge cases

### Performance

- Profile before optimizing
- Use browser DevTools
- Monitor API response times
- Watch bundle sizes
- Cache appropriately

### Security

- Never commit secrets
- Use environment variables
- Validate all inputs
- Sanitize user data
- Keep dependencies updated

## 🚀 Productivity Tips

### Aliases

Add to your shell profile:

```bash
# Navigation
alias im='cd ~/path/to/image2model'
alias imf='cd ~/path/to/image2model/frontend-svelte'
alias imb='cd ~/path/to/image2model/backend'

# Common commands
alias imdev='docker-compose up -d && npm run dev'
alias imtest='npm test && pytest'
```

### Scripts

Useful development scripts in `scripts/`:
- `dev.sh`: Start all services
- `test.sh`: Run all tests
- `clean.sh`: Clean up files

---

**Next Steps**: Set up your [Local Development](./setup/local-development.md) environment or configure [VSCode](./tools/vscode-setup.md).

*This guide is actively maintained. Contributions welcome!*