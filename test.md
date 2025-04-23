# Prompt Guide: Extensive FastAPI Unit Testing (>90% Coverage)

**Goal:** Generate a comprehensive suite of unit tests for the given FastAPI application, ensuring test coverage exceeds 90%. The tests should be robust, maintainable, and verify the application's logic thoroughly.

**Context:**
*   **Framework:** FastAPI
*   **Language:** Python
*   **Testing Framework:** `pytest`
*   **HTTP Client for Testing:** `httpx` (via FastAPI's `TestClient` or directly)
*   **Coverage Tool:** `pytest-cov`
*   **Mocking:** `unittest.mock` or FastAPI's dependency overrides.

**Key Areas for Testing:**

1.  **API Endpoints:**
    *   Test success scenarios (2xx status codes) with valid inputs.
    *   Test expected error scenarios (4xx status codes) with invalid inputs (validation errors, missing data).
    *   Test edge cases and boundary conditions for input parameters.
    *   Verify response structure and data types.
    *   Test different HTTP methods (GET, POST, PUT, DELETE, etc.) as applicable.

2.  **Dependency Injection & Mocking:**
    *   Utilize FastAPI's dependency overrides or `unittest.mock.patch` to mock external services (databases, APIs, etc.) and internal dependencies.
    *   Ensure dependencies are correctly injected and mocked within the test scope.
    *   Verify that mocked dependencies are called with the expected arguments.

3.  **Authentication & Authorization:**
    *   Test endpoints requiring authentication with valid and invalid credentials/tokens.
    *   Test endpoints requiring specific permissions/roles with authorized and unauthorized users.
    *   Mock authentication backends/dependencies effectively.

4.  **Business Logic & Utility Functions:**
    *   Write direct unit tests for service layer functions, utility functions, and complex business logic components, isolating them from the FastAPI framework where possible.

5.  **Data Validation (Pydantic Models):**
    *   While FastAPI handles basic validation, test specific complex validation logic within models or endpoints if present.

6.  **Background Tasks:**
    *   If using background tasks, devise strategies to test their initiation and potentially mock their execution.

7.  **Database Interactions (if applicable):**
    *   Mock the database layer entirely OR
    *   Use a dedicated test database (in-memory like SQLite or a separate instance) with proper setup and teardown fixtures.
    *   Verify data creation, retrieval, updates, and deletion logic.

**Testing Best Practices:**

*   **Use `TestClient`:** Leverage `from fastapi.testclient import TestClient` for testing HTTP endpoints.
*   **Isolation:** Tests must be independent and not rely on external services or the state of previous tests.
*   **Fixtures (`pytest.fixture`):** Use fixtures for setting up reusable resources (e.g., `TestClient` instance, mock data, database connections).
*   **Parameterization (`pytest.mark.parametrize`):** Use parameterization to test functions or endpoints with multiple input variations efficiently.
*   **Assertions:** Use clear and specific assertions (`assert response.status_code == 200`, `assert response.json() == expected_data`).
*   **Structure:** Organize tests logically (e.g., by feature, by module).

**Coverage Requirements:**

*   **Target:** Achieve **>90%** code coverage as reported by `pytest-cov`.
*   **Reporting:** Assume coverage reports (`pytest --cov=your_app --cov-report=html`) will be generated.
*   **Focus:** Prioritize testing uncovered lines and branches identified in the coverage report, ensuring the tests are meaningful and not just hitting lines.

**Instructions for Agent:**

*   Analyze the provided FastAPI application code.
*   Generate comprehensive `pytest` test suites covering the areas mentioned above.
*   Implement necessary mocks and fixtures.
*   Write clear, readable, and maintainable test code with appropriate comments where needed.
*   Ensure tests effectively verify application logic and edge cases.
*   Iteratively refine tests to meet the >90% coverage goal, focusing on meaningful test cases.
