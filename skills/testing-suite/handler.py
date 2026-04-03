#!/usr/bin/env python3
import sys
import os
import subprocess

JEST_CONFIG = """module.exports = {
  testEnvironment: 'node',
  coverageDirectory: 'coverage',
  collectCoverageFrom: [
    'src/**/*.js',
    '!src/**/*.test.js',
  ],
  testMatch: [
    '**/__tests__/**/*.js',
    '**/?(*.)+(spec|test).js',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
};
"""

JEST_SETUP = """// Jest setup file
global.console = {
  ...console,
  error: jest.fn(),
  warn: jest.fn(),
};

process.env.NODE_ENV = 'test';
"""

JEST_TEST_EXAMPLE = """const { add, subtract, multiply, divide } = require('./math');

describe('Math Module', () => {
  describe('add', () => {
    test('should add two numbers correctly', () => {
      expect(add(2, 3)).toBe(5);
    });

    test('should handle negative numbers', () => {
      expect(add(-2, 3)).toBe(1);
    });
  });

  describe('subtract', () => {
    test('should subtract two numbers correctly', () => {
      expect(subtract(5, 3)).toBe(2);
    });
  });

  describe('multiply', () => {
    test('should multiply two numbers correctly', () => {
      expect(multiply(4, 3)).toBe(12);
    });
  });

  describe('divide', () => {
    test('should divide two numbers correctly', () => {
      expect(divide(10, 2)).toBe(5);
    });

    test('should throw error when dividing by zero', () => {
      expect(() => divide(10, 0)).toThrow('Division by zero');
    });
  });
});
"""

PYTEST_CONFIG = """import pytest
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

@pytest.fixture
def sample_data():
    return {'name': 'Test', 'value': 42}

@pytest.fixture
def mock_api():
    # Mock API fixture
    class MockResponse:
        def __init__(self, data, status=200):
            self.data = data
            self.status = status
        
        def json(self):
            return self.data
    
    return MockResponse

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
"""

PYTEST_TEST_EXAMPLE = """import pytest
from myapp import math

class TestMath:
    def test_add(self):
        assert math.add(2, 3) == 5

    def test_subtract(self):
        assert math.subtract(5, 3) == 2

    def test_multiply(self):
        assert math.multiply(4, 3) == 12

    def test_divide(self):
        assert math.divide(10, 2) == 5

    def test_divide_by_zero(self):
        with pytest.raises(ZeroDivisionError):
            math.divide(10, 0)

@pytest.mark.parametrize("a,b,expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (100, 200, 300),
])
def test_add_parametrized(a, b, expected):
    assert math.add(a, b) == expected
"""

PLAYWRIGHT_CONFIG = """import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
"""

PLAYWRIGHT_TEST_EXAMPLE = """import { test, expect } from '@playwright/test';

test.describe('Homepage', () => {
  test('should load homepage', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Brand/);
  });

  test('should display hero section', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('h1')).toBeVisible();
  });

  test('should navigate to features', async ({ page }) => {
    await page.goto('/');
    await page.click('text=Features');
    await expect(page).toHaveURL(/.*features/);
  });
});

test.describe('Authentication', () => {
  test('should show login form', async ({ page }) => {
    await page.goto('/login');
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
  });

  test('should login successfully', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/.*dashboard/);
  });
});
"""

CYPRESS_CONFIG = """{
  "e2e": {
    "baseUrl": "http://localhost:3000",
    "supportFile": "cypress/support/e2e.js",
    "specPattern": "cypress/e2e/**/*.cy.js",
    "viewportWidth": 1280,
    "viewportHeight": 720,
    "video": false,
    "screenshotOnRunFailure": true
  }
}
"""

CYPRESS_TEST_EXAMPLE = """describe('Homepage', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  it('should load homepage', () => {
    cy.get('h1').should('be.visible');
  });

  it('should display navigation', () => {
    cy.get('nav').should('exist');
    cy.contains('Features').should('be.visible');
  });
});

describe('Authentication', () => {
  beforeEach(() => {
    cy.visit('/login');
  });

  it('should display login form', () => {
    cy.get('input[type="email"]').should('be.visible');
    cy.get('input[type="password"]').should('be.visible');
  });

  it('should login with valid credentials', () => {
    cy.get('input[type="email"]').type('test@example.com');
    cy.get('input[type="password"]').type('password123');
    cy.get('button[type="submit"]').click();
    cy.url().should('include', '/dashboard');
  });

  it('should show error with invalid credentials', () => {
    cy.get('input[type="email"]').type('invalid@example.com');
    cy.get('input[type="password"]').type('wrongpassword');
    cy.get('button[type="submit"]').click();
    cy.contains('Invalid credentials').should('be.visible');
  });
});
"""

def init_jest():
    os.makedirs("tests", exist_ok=True)
    
    files = {
        "jest.config.js": JEST_CONFIG,
        "jest.setup.js": JEST_SETUP,
        "tests/math.test.js": JEST_TEST_EXAMPLE,
    }
    
    for name, content in files.items():
        with open(name, 'w') as f:
            f.write(content)
    
    return "Jest configured. Run: npm install --save-dev jest"

def init_pytest():
    files = {
        "pytest.ini": PYTEST_CONFIG,
        "tests/test_example.py": PYTEST_TEST_EXAMPLE,
    }
    
    for name, content in files.items():
        with open(name, 'w') as f:
            f.write(content)
    
    return "pytest configured. Run: pip install pytest pytest-cov"

def init_playwright():
    os.makedirs("tests", exist_ok=True)
    
    files = {
        "playwright.config.ts": PLAYWRIGHT_CONFIG,
        "tests/example.spec.ts": PLAYWRIGHT_TEST_EXAMPLE,
    }
    
    for name, content in files.items():
        with open(name, 'w') as f:
            f.write(content)
    
    return "Playwright configured. Run: npm install --save-dev @playwright/test"

def init_cypress():
    os.makedirs("cypress/e2e", exist_ok=True)
    os.makedirs("cypress/support", exist_ok=True)
    
    files = {
        "cypress.config.js": CYPRESS_CONFIG,
        "cypress/e2e/example.cy.js": CYPRESS_TEST_EXAMPLE,
    }
    
    for name, content in files.items():
        with open(name, 'w') as f:
            f.write(content)
    
    return "Cypress configured. Run: npm install --save-dev cypress"

def run_tests():
    if os.path.exists("package.json"):
        if os.path.exists("jest.config.js"):
            return subprocess.run(["npm", "test"], capture_output=True, text=True).stdout
        elif os.path.exists("playwright.config.ts"):
            return subprocess.run(["npx", "playwright", "test"], capture_output=True, text=True).stdout
    elif os.path.exists("pytest.ini") or os.path.exists("pyproject.toml"):
        return subprocess.run(["pytest", "-v"], capture_output=True, text=True).stdout
    elif os.path.exists("cypress.config.js"):
        return subprocess.run(["npx", "cypress", "run"], capture_output=True, text=True).stdout
    
    return "No test framework found. Run init-jest, init-pytest, init-playwright, or init-cypress"

def run_coverage():
    if os.path.exists("jest.config.js"):
        return subprocess.run(["npm", "test", "--", "--coverage"], capture_output=True, text=True).stdout
    elif os.path.exists("pytest.ini"):
        return subprocess.run(["pytest", "--cov=src", "--cov-report=html"], capture_output=True, text=True).stdout
    return "No coverage tool found"

def main():
    if len(sys.argv) < 2:
        return """Usage: testing-suite <command> [args]

Commands:
  init-jest         - Setup Jest for Node.js
  init-pytest       - Setup pytest for Python
  init-playwright   - Setup Playwright for E2E
  init-cypress      - Setup Cypress for E2E
  run-tests         - Run all tests
  coverage          - Run with coverage

Examples:
  python handler.py init-jest
  python handler.py init-playwright
  python handler.py run-tests"""
    
    command = sys.argv[1]
    
    if command == "init-jest":
        return init_jest()
    elif command == "init-pytest":
        return init_pytest()
    elif command == "init-playwright":
        return init_playwright()
    elif command == "init-cypress":
        return init_cypress()
    elif command == "run-tests":
        return run_tests()
    elif command == "coverage":
        return run_coverage()
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
