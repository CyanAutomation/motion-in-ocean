# Pytest Usage Examples

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run only unit tests
```bash
pytest tests/ -m unit
# OR
pytest tests/unit/
```

### Run only integration tests
```bash
pytest tests/ -m integration
# OR
pytest tests/integration/
```

### Run specific test file
```bash
pytest tests/unit/test_config.py
pytest tests/unit/test_flask_routes.py
pytest tests/unit/test_pykms_import.py
pytest tests/integration/test_integration.py
```

### Run specific test function
```bash
pytest tests/unit/test_config.py::test_python_syntax
pytest tests/unit/test_flask_routes.py::test_environment_parsing
```

### Verbose output
```bash
pytest tests/ -v
```

### Show print statements
```bash
pytest tests/ -s
```

### Stop on first failure
```bash
pytest tests/ -x
```

### Show test coverage
```bash
pytest tests/ --cov=pi_camera_in_docker --cov-report=term-missing
```

### Run tests matching a pattern
```bash
pytest tests/ -k "docker"
pytest tests/ -k "environment"
```

## Expected Output

```
======================== test session starts ========================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0
rootdir: /home/runner/work/motioninocean/motioninocean
configfile: pyproject.toml
collected 32 items

tests/unit/test_config.py ..........                         [ 34%]
tests/unit/test_flask_routes.py s......                      [ 56%]
tests/unit/test_pykms_import.py .....s                       [ 75%]
tests/integration/test_integration.py s......s               [100%]

=================== 28 passed, 4 skipped in 0.14s ===================
```

## Markers

The tests use pytest markers to categorize tests:

- `@pytest.mark.unit` - Fast, isolated unit tests
- `@pytest.mark.integration` - Integration tests requiring external services

## Fixtures

Available fixtures in `tests/conftest.py`:

- `mock_env_vars` - Sets up mock environment variables
- `temp_env_file` - Creates a temporary .env file
- `sample_image_data` - Provides sample JPEG image data

## Skipped Tests

Some tests are skipped when dependencies are not available:

- **Flask tests** - Skipped if Flask is not installed (available in Docker container)
- **picamera2 tests** - Skipped if picamera2 is not installed (Raspberry Pi only)
- **Docker Compose tests** - Skipped if docker-compose is not installed

This is expected behavior and allows tests to run in any environment.
