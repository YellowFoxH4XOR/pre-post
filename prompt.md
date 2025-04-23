# Prompt Guide: Comprehensive Angular Best Practices for AI Agents

**Goal:** To guide an AI agent in generating, reviewing, or refactoring Angular code according to current best practices, ensuring the development of scalable, maintainable, performant, accessible, and secure web applications.

**Context:** Assume work is being done on an Angular application using TypeScript, targeting the latest stable Long-Term Support (LTS) version unless otherwise specified. Prioritize Standalone APIs for new development.

## Core Principles & Best Practices

### 1. Project Setup & CLI Usage
*   **Angular CLI:** The foundation. Use `ng new`, `ng generate` (or `ng g`), `ng serve`, `ng build`, `ng test`, `ng lint`, and `ng update` consistently.
*   **Workspace Configuration (`angular.json`):** Understand and leverage `angular.json` for build configurations, proxy settings, and project defaults.
*   **Strict Mode:** Enable strict mode (`ng new --strict`) for new projects to enforce stricter TypeScript settings and Angular template checks, catching potential issues earlier.

### 2. Architecture & Code Organization
*   **Standalone APIs:** **Prioritize** standalone components, directives, and pipes for new features. They simplify the architecture by reducing the need for `NgModule` boilerplate.
*   **Feature Modules (for older/larger apps):** If not using standalone exclusively, group related components, services, and routes into cohesive feature modules. Use `NgModule` to encapsulate features.
*   **Folder Structure:** Adopt a consistent and scalable folder structure (e.g., feature-based grouping: `src/app/features/feature-name/components`, `src/app/core`, `src/app/shared`).
*   **Core Module/Services:** Centralize application-wide singleton services (like authentication, logging) often provided in `root`.
*   **Shared Module/Components:** Place reusable components, directives, and pipes used across multiple feature modules here (if not using standalone).

### 3. Component Design
*   **Smart/Container & Presentational/Dumb Components:** Separate components responsible for fetching/managing state (smart) from those purely displaying data and emitting events (presentational). This improves reusability and testability.
*   **Inputs (`@Input()`) & Outputs (`@Output()`):** Define clear component APIs. Use setters for inputs if logic needs to run when an input changes. Use `EventEmitter` for outputs.
*   **Single Responsibility Principle (SRP):** Keep components focused on a single task or piece of UI.
*   **Lifecycle Hooks:** Understand and use component lifecycle hooks (`OnInit`, `OnDestroy`, `OnChanges`, etc.) appropriately. Implement `OnDestroy` to clean up subscriptions and avoid memory leaks.

### 4. TypeScript & Coding Style
*   **Strong Typing:** Maximize TypeScript's benefits. Define interfaces and types for data structures (API responses, models). Avoid `any` whenever possible.
*   **Readonly:** Use the `readonly` modifier for properties that should not be reassigned after initialization.
*   **Linting & Formatting:** Enforce code style consistency using ESLint (`ng lint`) and Prettier. Configure rules in `.eslintrc.json` and `.prettierrc.json`.
*   **Naming Conventions:** Follow standard naming conventions (e.g., PascalCase for classes/interfaces, camelCase for variables/functions, `$` suffix for Observable variables).

### 5. State Management & Reactivity
*   **Angular Signals:** **Prefer** Signals for managing component-level state and reactivity due to their fine-grained change detection and performance benefits.
*   **RxJS:** Use RxJS for complex asynchronous operations, event streams, and managing state across multiple services. Key operators: `map`, `filter`, `switchMap`, `catchError`, `takeUntil`, `debounceTime`.
*   **State Management Libraries (Optional):** For complex global state, consider libraries like NgRx (Redux pattern) or NgXs. Evaluate if the complexity warrants their use over simpler service-based state or Signals.
*   **Subscription Management:** Crucial for avoiding memory leaks with RxJS. Use the `async` pipe in templates (preferred), `takeUntil` pattern with a subject, `take(1)` for single-value streams, or manual `unsubscribe()` in `ngOnDestroy`.

### 6. Modularity & Dependency Injection (DI)
*   **Standalone APIs:** Import standalone components/directives/pipes directly where needed.
*   **`providedIn: 'root'`:** The standard way to provide application-wide singleton services.
*   **Component/Module Providers:** Provide services at the component or module level for more scoped instances when necessary.
*   **Injection Tokens:** Use `InjectionToken` for providing non-class dependencies or configuring services.

### 7. Routing (`@angular/router`)
*   **Lazy Loading:** Essential for performance. Use `loadComponent` (for standalone) or `loadChildren` (for modules) in route definitions.
*   **Route Guards:** Implement `CanActivate`, `CanActivateChild`, `CanDeactivate`, `CanMatch` for controlling navigation flow (authentication, authorization, unsaved changes).
*   **Route Resolvers (`ResolveFn`):** Pre-fetch data needed for a route before activation.
*   **Child Routes & Nested Routers:** Structure complex application sections using child routes.
*   **Typed Routers:** Leverage typed routers for better type safety in route parameters and navigation.

### 8. Forms (`@angular/forms`)
*   **Reactive Forms:** Generally preferred for complex forms due to testability, explicit control management, and easier handling of dynamic scenarios.
*   **Template-Driven Forms:** Suitable for simpler forms where validation and logic are minimal.
*   **Custom Validators:** Create reusable custom validation functions.
*   **Async Validators:** Handle validation logic that requires asynchronous operations (e.g., checking username availability).
*   **Value Accessors (`ControlValueAccessor`):** Implement this interface to integrate custom form controls with Angular's form APIs.

### 9. HTTP Communication (`@angular/common/http`)
*   **`HttpClient` Service:** The standard for making HTTP requests.
*   **Interceptors (`HttpInterceptor`):** Intercept requests and responses globally to handle tasks like adding authentication tokens, logging, or centralized error handling.
*   **Typed Clients:** Define interfaces for API request/response payloads for type safety.
*   **Error Handling:** Use RxJS `catchError` and `retry` operators effectively.

### 10. Performance Optimization
*   **Change Detection (`OnPush`):** Use `ChangeDetectionStrategy.OnPush` on components to minimize change detection cycles. Trigger updates explicitly via `async` pipe, Signal changes, `@Input` changes (for primitives/new object references), or `ChangeDetectorRef.markForCheck()`.
*   **`@defer` Blocks:** Use declarative deferrable views for fine-grained lazy loading within templates.
*   **`trackBy` Function:** Use `trackBy` with `*ngFor` to help Angular efficiently update lists by tracking items by a unique identifier.
*   **Bundle Analysis:** Use tools like `source-map-explorer` or `webpack-bundle-analyzer` (via `ng build --stats-json`) to inspect bundle sizes and identify optimization opportunities.
*   **SSR/SSG & Hydration:** Implement Angular Universal for Server-Side Rendering or Static Site Generation to improve perceived performance and SEO.
*   **`NgOptimizedImage`:** Use the `<img ngSrc="...">` directive for optimized image loading.
*   **Web Workers:** Offload CPU-intensive tasks to background threads using Web Workers.

### 11. Security
*   **Sanitization:** Trust Angular's built-in sanitization for preventing XSS via property binding and interpolation. Use `DomSanitizer` explicitly only when necessary and with extreme caution.
*   **Avoid `bypassSecurityTrust...`:** Use `DomSanitizer.bypassSecurityTrust...` methods sparingly and only when you fully understand the security implications.
*   **Template Injection:** Be cautious when dynamically generating templates.
*   **CSRF Protection:** Implement Cross-Site Request Forgery protection mechanisms (often handled server-side with token synchronization).
*   **Content Security Policy (CSP):** Define a strict CSP header on the server.
*   **Regular Dependency Updates:** Keep Angular and third-party libraries updated to patch known vulnerabilities (`ng update`).

### 12. Testing
*   **Testing Pyramid:** Focus on a large base of unit tests, fewer integration tests, and even fewer E2E tests.
*   **Unit Tests (Jasmine/Karma/Jest):** Test components, services, pipes in isolation. Use `TestBed` for configuring testing modules/providers. Mock dependencies effectively.
*   **Component Testing:** Test component logic, template rendering, input/output interactions, and event handling.
*   **Integration Tests:** Test interactions between multiple components or services.
*   **E2E Tests (Cypress/Playwright):** Test user flows through the application in a real browser environment.
*   **Code Coverage:** Aim for meaningful code coverage, focusing on critical paths and complex logic.

### 13. Accessibility (a11y)
*   **Semantic HTML:** Use appropriate HTML5 elements (`<nav>`, `<main>`, `<button>`, etc.).
*   **ARIA Attributes:** Use Accessible Rich Internet Applications (ARIA) attributes where necessary to enhance semantics for assistive technologies.
*   **Keyboard Navigation:** Ensure all interactive elements are focusable and operable via keyboard.
*   **Focus Management:** Manage focus programmatically when UI changes dynamically (e.g., opening modals, navigating).
*   **Color Contrast:** Ensure sufficient contrast between text and background colors.
*   **Testing Tools:** Use accessibility linters and browser extensions (like Axe DevTools) to audit accessibility.

### 14. Internationalization (i18n)
*   **Angular i18n (`@angular/localize`):** Use Angular's built-in i18n tools for marking text in templates (`i18n` attribute) and code for translation.
*   **Translation Files:** Manage translations in standard formats (XLIFF, JSON, etc.).
*   **Build-time i18n:** Generate separate application builds for each language (common approach).

### 15. UI Component Libraries
*   **Angular Material/CDK:** Leverage Angular Material for pre-built, high-quality UI components following Material Design principles. Use the Component Dev Kit (CDK) for building custom components with common interaction patterns (overlays, scrolling, drag-and-drop).
*   **Other Libraries:** Consider other libraries like NG-ZORRO, PrimeNG, etc., based on project requirements.

## Instructions for Agent

*   **Generation:** When creating new Angular code, strictly adhere to the principles outlined above, prioritizing modern practices like Standalone APIs and Signals.
*   **Review/Refactoring:** When analyzing existing code, identify deviations from these best practices and propose specific, actionable improvements with clear justifications.
*   **Priorities:** Emphasize code clarity, long-term maintainability, performance, security, and accessibility.
*   **Justification:** Clearly explain the rationale behind any suggested code changes, referencing the relevant best practice.
*   **Compatibility:** Ensure generated or modified code is compatible with the target Angular version (defaulting to the latest LTS).
