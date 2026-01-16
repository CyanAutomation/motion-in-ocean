#!/usr/bin/env python3
"""
Test script to validate MotionInOcean configuration and code structure.
This tests the docker-compose configuration, Python code syntax, and endpoints.
"""

import sys
import json
import ast
import yaml

def test_python_syntax():
    """Test if main.py has valid Python syntax."""
    print("\n=== Testing Python Syntax ===")
    try:
        with open('pi_camera_in_docker/main.py', 'r') as f:
            code = f.read()
        ast.parse(code)
        print("✓ main.py has valid Python syntax")
        return True
    except SyntaxError as e:
        print(f"✗ Syntax error in main.py: {e}")
        return False
    except Exception as e:
        print(f"✗ Error reading main.py: {e}")
        return False

def test_docker_compose():
    """Test if docker-compose.yml has valid YAML syntax."""
    print("\n=== Testing Docker Compose Configuration ===")
    try:
        with open('docker-compose.yml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Verify essential keys
        assert 'services' in config, "Missing 'services' key"
        assert 'motioninocean' in config['services'], "Missing 'motioninocean' service"
        
        service = config['services']['motioninocean']
        
        # Check required fields (environment can be via env_file or environment key)
        required_fields = ['image', 'restart', 'ports', 'healthcheck']
        optional_env = ['environment', 'env_file']
        
        for field in required_fields:
            assert field in service, f"Missing required field: {field}"
        
        # Verify environment variables are configured (via env_file or environment)
        assert any(field in service for field in optional_env), "Missing environment configuration (env_file or environment)"
        
        print("✓ docker-compose.yml is valid YAML")
        
        # Verify healthcheck configuration
        healthcheck = service.get('healthcheck', {})
        assert 'test' in healthcheck, "Missing healthcheck test"
        assert '/health' in str(healthcheck.get('test')), "Healthcheck should use /health endpoint"
        print("✓ Healthcheck uses /health endpoint")
        
        # Verify device mappings
        devices = service.get('devices', [])
        assert len(devices) > 0, "No device mappings found"
        assert any('/dev/dma_heap' in str(d) for d in devices), "Missing /dev/dma_heap device"
        assert any('/dev/vchiq' in str(d) for d in devices), "Missing /dev/vchiq device"
        assert any('/dev/video' in str(d) for d in devices), "Missing /dev/video* devices"
        print(f"✓ Device mappings configured ({len(devices)} devices)")
        
        # Verify no privileged mode (should be explicit devices instead)
        if service.get('privileged'):
            print("⚠ Warning: privileged mode is enabled (comment suggests fallback only)")
        else:
            print("✓ Using explicit device mappings instead of privileged mode")
        
        return True
    except yaml.YAMLError as e:
        print(f"✗ YAML error in docker-compose.yml: {e}")
        return False
    except AssertionError as e:
        print(f"✗ Configuration error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error reading docker-compose.yml: {e}")
        return False

def test_endpoints():
    """Verify that Flask endpoints are defined."""
    print("\n=== Testing Flask Endpoints ===")
    try:
        with open('pi_camera_in_docker/main.py', 'r') as f:
            code = f.read()
        
        endpoints = {
            '@app.route(\'/\')': 'Root endpoint',
            '@app.route(\'/health\')': 'Health check',
            '@app.route(\'/ready\')': 'Readiness probe',
            '@app.route(\'/stream.mjpg\')': 'MJPEG stream',
        }
        
        for route, description in endpoints.items():
            if route in code:
                print(f"✓ {description}: {route}")
            else:
                print(f"✗ Missing {description}: {route}")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Error checking endpoints: {e}")
        return False

def test_error_handling():
    """Verify error handling in main.py."""
    print("\n=== Testing Error Handling ===")
    with open('pi_camera_in_docker/main.py', 'r') as f:
        code = f.read()
    
    checks = {
        'PermissionError handling': 'except PermissionError',
        'RuntimeError handling': 'except RuntimeError',
        'General exception handling': 'except Exception',
        'Try-finally block': 'finally:',
        'Edge detection error handling': 'try:' in code and 'apply_edge_detection' in code,
    }
    
    passed = 0
    for check_name, pattern in checks.items():
        if isinstance(pattern, bool):
            if pattern:
                print(f"✓ {check_name}")
                passed += 1
        elif pattern in code:
            print(f"✓ {check_name}")
            passed += 1
        else:
            print(f"✗ Missing {check_name}")
    
    return passed == len(checks)

def test_logging():
    """Verify logging configuration."""
    print("\n=== Testing Logging Configuration ===")
    with open('pi_camera_in_docker/main.py', 'r') as f:
        code = f.read()
    
    checks = {
        'Logging basicConfig': 'logging.basicConfig',
        'Logger instance': 'logger = logging.getLogger',
        'Structured log format': 'format=',
        'INFO level': "level=logging.INFO",
    }
    
    passed = 0
    for check_name, pattern in checks.items():
        if pattern in code:
            print(f"✓ {check_name}")
            passed += 1
        else:
            print(f"✗ Missing {check_name}")
    
    return passed == len(checks)

def test_environment_variables():
    """Verify environment variable handling."""
    print("\n=== Testing Environment Variables ===")
    with open('pi_camera_in_docker/main.py', 'r') as f:
        code = f.read()
    
    env_vars = {
        'RESOLUTION': 'resolution configuration',
        'EDGE_DETECTION': 'edge detection toggle',
        'FPS': 'frame rate control',
    }
    
    passed = 0
    for var, description in env_vars.items():
        if f'os.environ.get("{var}"' in code:
            print(f"✓ {var}: {description}")
            passed += 1
        else:
            print(f"✗ Missing environment variable: {var}")
    
    return passed == len(env_vars)

def test_env_file():
    """Verify .env file exists with required variables."""
    print("\n=== Testing .env File ===")
    try:
        with open('.env', 'r') as f:
            env_content = f.read()
        
        required_vars = ['TZ', 'RESOLUTION', 'EDGE_DETECTION']
        passed = 0
        
        for var in required_vars:
            if f'{var}=' in env_content:
                # Extract value
                line = [l for l in env_content.split('\n') if l.startswith(var)][0]
                value = line.split('=', 1)[1]
                print(f"✓ {var}={value}")
                passed += 1
            else:
                print(f"✗ Missing {var} in .env")
        
        return passed == len(required_vars)
    except FileNotFoundError:
        print("✗ .env file not found")
        return False
    except Exception as e:
        print(f"✗ Error reading .env file: {e}")
        return False

def test_dockerfile():
    """Basic checks on Dockerfile."""
    print("\n=== Testing Dockerfile ===")
    try:
        with open('Dockerfile', 'r') as f:
            dockerfile = f.read()
        
        checks = {
            'Base image': 'FROM debian:bookworm',
            'Python picamera2': 'python3-picamera2',
            'Python flask': 'python3-flask',
            'Python opencv': 'python3-opencv',
            'Working directory': 'WORKDIR /app',
            'Entry point': 'CMD',
        }
        
        passed = 0
        for check_name, pattern in checks.items():
            if pattern in dockerfile:
                print(f"✓ {check_name}")
                passed += 1
            else:
                print(f"✗ Missing: {check_name}")
        
        return passed == len(checks)
    except Exception as e:
        print(f"✗ Error reading Dockerfile: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("MotionInOcean Configuration & Code Tests")
    print("=" * 60)
    
    tests = [
        ("Python Syntax", test_python_syntax),
        ("Docker Compose", test_docker_compose),
        (".env File", test_env_file),
        ("Flask Endpoints", test_endpoints),
        ("Error Handling", test_error_handling),
        ("Logging Configuration", test_logging),
        ("Environment Variables", test_environment_variables),
        ("Dockerfile", test_dockerfile),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed! Configuration is ready for deployment.")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed. Please review the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
