"""
Integration tests for Docker deployment and production configuration.

Tests Docker Compose setup, service health, and production readiness.
"""

import pytest
import subprocess
import time
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List
import requests

@pytest.mark.docker
@pytest.mark.integration
class TestDockerDeployment:
    """Test Docker deployment configurations."""
    
    @pytest.fixture(scope="class")
    def project_root(self) -> Path:
        """Get project root directory."""
        return Path(__file__).parent.parent.parent
    
    @pytest.fixture(scope="class")
    def docker_compose_files(self, project_root) -> Dict[str, Path]:
        """Get Docker Compose file paths."""
        return {
            'base': project_root / 'docker-compose.yml',
            'override': project_root / 'docker-compose.override.yml',
            'prod': project_root / 'docker-compose.prod.yml'
        }
    
    def test_docker_compose_file_validity(self, docker_compose_files):
        """Test Docker Compose files are valid YAML."""
        for name, file_path in docker_compose_files.items():
            assert file_path.exists(), f"Docker Compose file missing: {name} ({file_path})"
            
            with open(file_path, 'r') as f:
                try:
                    compose_config = yaml.safe_load(f)
                    assert isinstance(compose_config, dict), f"Invalid YAML structure in {name}"
                    assert 'services' in compose_config, f"No services defined in {name}"
                except yaml.YAMLError as e:
                    pytest.fail(f"Invalid YAML in {name}: {e}")
    
    def test_docker_compose_service_definitions(self, docker_compose_files):
        """Test required services are defined in Docker Compose."""
        with open(docker_compose_files['base'], 'r') as f:
            base_config = yaml.safe_load(f)
        
        services = base_config.get('services', {})
        required_services = ['postgres', 'redis', 'backend', 'worker', 'frontend']
        
        for service in required_services:
            assert service in services, f"Required service '{service}' not found in docker compose.yml"
    
    def test_production_docker_compose_configuration(self, docker_compose_files):
        """Test production Docker Compose configuration."""
        with open(docker_compose_files['prod'], 'r') as f:
            prod_config = yaml.safe_load(f)
        
        services = prod_config.get('services', {})
        
        # Check production-specific configurations
        if 'backend' in services:
            backend = services['backend']
            
            # Should have resource limits in production
            assert 'deploy' in backend, "Backend should have deploy configuration in production"
            assert 'resources' in backend['deploy'], "Backend should have resource limits"
            
            # Should use production build target
            if 'build' in backend:
                assert backend['build'].get('target') == 'production', "Backend should use production build target"
        
        # Check that production uses appropriate restart policies
        for service_name, service_config in services.items():
            if 'restart' in service_config:
                assert service_config['restart'] in ['always', 'unless-stopped'], f"{service_name} should have production restart policy"
    
    def test_environment_variable_configuration(self, docker_compose_files):
        """Test environment variable configuration."""
        with open(docker_compose_files['base'], 'r') as f:
            base_config = yaml.safe_load(f)
        
        services = base_config.get('services', {})
        
        # Check backend environment variables
        if 'backend' in services:
            backend_env = services['backend'].get('environment', [])
            
            # Convert list format to dict if needed
            if isinstance(backend_env, list):
                env_dict = {}
                for env_var in backend_env:
                    if '=' in env_var:
                        key, value = env_var.split('=', 1)
                        env_dict[key] = value
                backend_env = env_dict
            
            required_env_vars = [
                'DATABASE_URL',
                'CELERY_BROKER_URL',
                'CELERY_RESULT_BACKEND'
            ]
            
            for env_var in required_env_vars:
                assert env_var in backend_env, f"Required environment variable '{env_var}' not found in backend service"
    
    def test_docker_networks_configuration(self, docker_compose_files):
        """Test Docker networks are properly configured."""
        with open(docker_compose_files['base'], 'r') as f:
            base_config = yaml.safe_load(f)
        
        # Check networks are defined
        assert 'networks' in base_config, "No networks defined in docker compose.yml"
        
        networks = base_config['networks']
        assert 'image2model-network' in networks, "Main network not defined"
        
        # Check services use the network
        services = base_config.get('services', {})
        for service_name, service_config in services.items():
            if 'networks' in service_config:
                assert 'image2model-network' in service_config['networks'], f"{service_name} not connected to main network"
    
    def test_docker_volumes_configuration(self, docker_compose_files):
        """Test Docker volumes are properly configured."""
        with open(docker_compose_files['base'], 'r') as f:
            base_config = yaml.safe_load(f)
        
        # Check volumes are defined
        assert 'volumes' in base_config, "No volumes defined in docker compose.yml"
        
        volumes = base_config['volumes']
        required_volumes = [
            'postgres_data',
            'redis_data',
            'backend_uploads',
            'backend_results'
        ]
        
        for volume in required_volumes:
            assert volume in volumes, f"Required volume '{volume}' not defined"
    
       
    def test_docker_health_checks(self, docker_compose_files):
        """Test Docker health checks are properly configured."""
        with open(docker_compose_files['base'], 'r') as f:
            base_config = yaml.safe_load(f)
        
        services = base_config.get('services', {})
        
        # Services that should have health checks
        health_check_services = ['postgres', 'redis']
        
        for service_name in health_check_services:
            if service_name in services:
                service_config = services[service_name]
                assert 'healthcheck' in service_config, f"{service_name} should have health check configured"
                
                healthcheck = service_config['healthcheck']
                assert 'test' in healthcheck, f"{service_name} health check missing test command"
                assert 'interval' in healthcheck, f"{service_name} health check missing interval"
                assert 'timeout' in healthcheck, f"{service_name} health check missing timeout"
                assert 'retries' in healthcheck, f"{service_name} health check missing retries"
    
    def test_docker_compose_override_structure(self, docker_compose_files):
        """Test Docker Compose override file structure."""
        if not docker_compose_files['override'].exists():
            pytest.skip("Docker Compose override file not found")
        
        with open(docker_compose_files['override'], 'r') as f:
            override_config = yaml.safe_load(f)
        
        services = override_config.get('services', {})
        
        # Check development-specific overrides
        if 'backend' in services:
            backend = services['backend']
            
            # Should have development-specific configurations
            if 'build' in backend:
                assert backend['build'].get('target') == 'development', "Override should use development build target"
            
            # Should have volume mounts for development
            if 'volumes' in backend:
                volume_mounts = backend['volumes']
                has_source_mount = any('./backend:/app' in str(mount) for mount in volume_mounts)
                assert has_source_mount, "Backend should have source code volume mount in development"
    
    def test_makefile_docker_targets(self, project_root):
        """Test Makefile Docker targets exist."""
        makefile_path = project_root / 'Makefile'
        
        if not makefile_path.exists():
            pytest.skip("Makefile not found")
        
        with open(makefile_path, 'r') as f:
            makefile_content = f.read()
        
        # Check for essential Docker targets
        required_targets = [
            'up',
            'down',
            'build',
            'logs',
            'clean'
        ]
        
        for target in required_targets:
            assert f"{target}:" in makefile_content, f"Makefile target '{target}' not found"
    
    def test_dockerfile_structure(self, project_root):
        """Test Dockerfile structure and best practices."""
        dockerfiles = [
            project_root / 'backend' / 'Dockerfile',
            project_root / 'frontend' / 'Dockerfile'
        ]
        
        for dockerfile_path in dockerfiles:
            if not dockerfile_path.exists():
                continue
            
            with open(dockerfile_path, 'r') as f:
                dockerfile_content = f.read()
            
            # Check for multi-stage build
            assert 'FROM' in dockerfile_content, f"No FROM instruction in {dockerfile_path}"
            
            # Check for non-root user (security best practice)
            has_user_instruction = 'USER' in dockerfile_content
            has_non_root = any(user in dockerfile_content.lower() for user in ['user app', 'user node', 'user 1000'])
            
            # Should have some form of non-root user configuration
            if has_user_instruction or has_non_root:
                pass  # Good, has non-root user configuration
            else:
                print(f"Warning: {dockerfile_path} may not have non-root user configuration")
    
    def test_docker_ignore_files(self, project_root):
        """Test .dockerignore files exist and have proper content."""
        dockerignore_files = [
            project_root / 'backend' / '.dockerignore',
            project_root / 'frontend' / '.dockerignore'
        ]
        
        for dockerignore_path in dockerignore_files:
            if not dockerignore_path.exists():
                continue
            
            with open(dockerignore_path, 'r') as f:
                dockerignore_content = f.read()
            
            # Check for common ignore patterns
            if 'backend' in str(dockerignore_path):
                common_patterns = ['__pycache__', '*.pyc', '.pytest_cache', 'venv']
            else:  # frontend
                common_patterns = ['node_modules', 'dist', '.next']
            
            for pattern in common_patterns:
                if pattern not in dockerignore_content:
                    print(f"Warning: {pattern} not found in {dockerignore_path}")
    
