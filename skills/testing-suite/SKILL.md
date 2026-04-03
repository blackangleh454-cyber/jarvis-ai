# Testing Suite

**Description:** Generate and run unit tests, integration tests, and E2E tests for various frameworks.

**Commands:**
- `init-jest` - Setup Jest for Node.js
- `init-pytest` - Setup pytest for Python
- `init-playwright` - Setup Playwright for E2E
- `init-cypress` - Setup Cypress for E2E
- `generate-test <type> <name>` - Generate test file
- `run-tests` - Run all tests
- `coverage` - Run with coverage

**Test Types:**
- Unit tests
- Integration tests
- E2E tests
- Snapshot tests

**Usage:**
```bash
python handler.py init-jest
python handler.py init-pytest
python handler.py init-playwright
python handler.py generate-test unit user-service
python handler.py run-tests
```
