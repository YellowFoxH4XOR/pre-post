
# Prompt Guide: Angular Best Practices for AI Agents

**Goal:** To guide an AI agent in generating, reviewing, or refactoring Angular code according to current best practices, ensuring the development of scalable, maintainable, and performant web applications.

**Context:** Assume work is being done on an Angular application using TypeScript, targeting the latest stable Long-Term Support (LTS) version unless otherwise specified.

## Core Principles & Best Practices

### 1. Angular CLI Usage
*   **Standardize Workflow:** Leverage the Angular CLI (`ng`) for core development tasks. Use `ng generate` (e.g., `ng g c my-component`) to create components, services, modules, etc., ensuring consistency and adherence to the conventional project structure.
*   **Essential Commands:** Utilize standard commands like `ng build` for compiling the application, `ng serve` for local development, `ng test` for running unit tests, and `ng update` for managing dependencies and facilitating smooth migrations between Angular versions.

### 2. Component-Based Architecture
*   **Modularity:** Design the application using small, reusable, and well-defined components.
*   **Clear Communication:** Use `@Input()` decorators for passing data into a component and `@Output()` decorators (typically with `EventEmitter`) for sending data or events out of a component.
*   **Single Responsibility:** Ensure each component focuses on a specific piece of functionality or UI element.

### 3. TypeScript Integration
*   **Strong Typing:** Fully utilize TypeScript's static typing features (interfaces, types, classes) to improve code clarity, enable better tooling (like autocompletion and refactoring), and catch errors during development rather than at runtime.
*   **Avoid `any`:** Refrain from using the `any` type whenever a more specific type can be defined. This enhances type safety and code predictability.

### 4. State Management & Reactivity
*   **Angular Signals:** Prioritize Angular Signals for managing component state and reactivity. Signals offer fine-grained change detection and often lead to simpler, more performant code compared to traditional methods, especially for new development.
*   **RxJS for Complexity:** Use RxJS for handling complex asynchronous operations, managing streams of events (like user input or WebSocket messages), and composing asynchronous logic where Signals might be less suitable.

### 5. Modularity & Dependency Injection (DI)
*   **Organization:** Structure the application into logical feature areas using NgModules or standalone components/directives/pipes.
*   **Leverage DI:** Utilize Angular's built-in Dependency Injection (DI) system extensively. Provide services using `providedIn: 'root'` for application-wide singletons or within specific modules/components for more scoped instances. DI promotes loose coupling, testability, and code reuse.

### 6. Routing
*   **Navigation:** Implement application navigation using the official `@angular/router` module.
*   **Lazy Loading:** Employ lazy loading for feature modules or routing configurations (using `loadChildren` or `loadComponent`) to significantly improve initial application load times by only loading code when needed.
*   **Route Guards:** Protect routes using guards (e.g., `CanActivate`, `CanDeactivate`) to control access based on conditions like user authentication or unsaved changes.
*   **Route Resolvers:** Use resolvers (`ResolveFn`) to pre-fetch data required by a component before the route activation completes, improving user experience by avoiding empty component states.

### 7. Forms Handling
*   **Structured Forms:** Use Angular's Reactive Forms API for complex forms requiring robust validation, dynamic controls, and easier testing. Template-Driven Forms can be suitable for simpler scenarios.
*   **Validation:** Implement comprehensive validation using Angular's built-in validators (e.g., `Validators.required`, `Validators.email`) and create custom validators for specific business rules.

### 8. HTTP Communication
*   **`HttpClient`:** Use the `HttpClientModule` and inject the `HttpClient` service for making asynchronous requests to backend APIs.
*   **Error Handling:** Implement robust error handling for HTTP requests (e.g., using RxJS `catchError` operator).
*   **Subscription Management:** Prevent memory leaks by properly managing Observable subscriptions. Use the `async` pipe in templates, or operators like `takeUntil`, `take(1)`, or manual `unsubscribe()` in component logic.

### 9. Performance Optimization
*   **Declarative Lazy Loading (`@defer`):** Use `@defer` blocks within component templates for fine-grained, declarative lazy loading of components, directives, or pipes based on various triggers (viewport, interaction, timer, etc.).
*   **Rendering Strategies:** Leverage Server-Side Rendering (SSR) or Static Site Generation (SSG) with hydration for improved initial load performance (First Contentful Paint) and better SEO.
*   **Change Detection:** Use the `ChangeDetectionStrategy.OnPush` strategy for components whenever possible to reduce the scope and frequency of change detection cycles.
*   **Image Optimization:** Utilize the `NgOptimizedImage` directive (`<img ngSrc="...">`) for automatic image optimization (lazy loading, preconnect hints, automatic `srcset` generation).
*   **Debugging:** Use Angular DevTools to inspect component structure, profiler performance, and debug applications effectively.

### 10. Security Considerations
*   **Built-in Protection:** Understand and rely on Angular's built-in protections against common web vulnerabilities, such as Cross-Site Scripting (XSS), through automatic output sanitization.
*   **Trusted Types:** Be aware of and potentially enforce Trusted Types for stricter security policies.
*   **Input Handling:** Always treat user input as potentially unsafe and handle it accordingly.

### 11. Testing Practices
*   **Unit Testing:** Write comprehensive unit tests for components, services, pipes, and directives using frameworks like Jasmine and test runners like Karma or Jest. Focus on testing individual units in isolation.
*   **End-to-End (E2E) Testing:** Implement E2E tests using tools like Cypress or Playwright to simulate user interactions and verify application workflows from start to finish.

## Instructions for Agent

*   **Generation:** When creating new Angular code, strictly adhere to the principles outlined above.
*   **Review/Refactoring:** When analyzing existing code, identify deviations from these best practices and propose specific, actionable improvements.
*   **Priorities:** Emphasize code clarity, long-term maintainability, and application performance.
*   **Justification:** Clearly explain the rationale behind any suggested code changes, referencing the relevant best practice.
*   **Compatibility:** Ensure generated or modified code is compatible with the target Angular version (defaulting to the latest LTS).
