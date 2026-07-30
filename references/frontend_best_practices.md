# Frontend Best Practices

This guide outlines standard frontend engineering guidelines for web applications (Angular, React, Vue, Svelte).

---

## 1. Strict Prohibition on Hardcoded Host Addresses & Static IPs (CRITICAL ZERO-CONFIG RULE)

- **STRICTLY FORBIDDEN**: Hardcoding static IP addresses (`http://192.168.121.1:8081`, `http://147.x.x.x`), static domain names (`http://api.myproject.com`), or static ports (`http://localhost:3000`) anywhere in frontend source code, components, services, HTTP interceptors, or environment files (`environment.ts`).
- **MANDATORY RELATIVE PATHS**:
  1. Frontend services and HTTP clients MUST use relative API paths (e.g. `/api/auth/login`, `/api/units`).
  2. If an absolute origin is required at runtime (e.g. WebSockets or OAuth redirects), it MUST be dynamically derived from `window.location.origin` or runtime configuration — NEVER static string literals.
- **BUILD PORTABILITY**: Built frontend assets (`dist/`) MUST be 100% environment-agnostic and able to run behind Nginx / reverse proxies on ANY domain or IP address without requiring rebuilding or environment file modifications.

---

## 2. API Contract Compliance & Type Safety

- **OpenAPI / DTO Sync**: Frontend interfaces and DTO types MUST match the OpenAPI spec (`.openspec/api-contract.yaml`) exactly.
- **Strict Typing**: FORBIDDEN to use `any` or untyped HTTP response payloads. Wrap all responses in strongly typed models or interfaces.

---

## 3. UI/UX & State Management Discipline

- **State Isolation**: Use reactive state management (Signals, NgRx, Redux, Zustand) for shared application state. Keep transient view state inside local components.
- **Error Handling**: Gracefully intercept HTTP errors (e.g., 401, 403, 500) using global interceptors and present user-friendly notifications.
