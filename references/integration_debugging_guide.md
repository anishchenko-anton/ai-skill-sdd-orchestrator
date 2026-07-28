# Integration Debugging Guide (Frontend ↔ Backend)

This guide defines the mandatory protocol for diagnosing and resolving bugs at the boundary between Frontend components, Backend services, and API endpoints under the Spec-Driven Development (SDD) methodology.

---

## 1. API-First Verification Protocol

When a bug occurs in feature functionality involving client-server communication, **Orchestrators and Workers are STRICTLY FORBIDDEN from modifying UI components or Backend services before inspecting the empirical API response.**

### Mandatory Diagnostic Sequence

1. **Step 1: Inspect Raw HTTP Response**:
   - Perform a direct API call (via `curl`, CLI, or inspect Network logs).
   - Capture status code, headers, and exact JSON response payload.

2. **Step 2: Validate Against `api-contract.yaml`**:
   Compare the actual HTTP response against the OpenAPI contract in `.openspec/api-contract.yaml`:

| Condition / API Response | Target Subagent | Action Required |
| :--- | :--- | :--- |
| **Response != Contract** (HTTP 500, broken JSON, missing required fields, wrong data types) | **Backend-Worker** | Fix server logic or database queries. **Do NOT touch Frontend.** |
| **Response == Contract** (HTTP 200/201 OK, valid schema), but UI renders incorrectly or crashes | **Frontend-Engineer** | Fix UI state mapping, RxJS/Signals, or component logic. **Do NOT touch Backend.** |
| **Missing Contract Fields** (UI requires new data not defined in contract) | **Root-Orchestrator** | 1. Update `api-contract.yaml`<br>2. Update Backend<br>3. Update Frontend |

---

## 2. Bug Localization Report

Before requesting code modifications or generating code:
- Document the exact HTTP Endpoint (`METHOD /path`).
- Provide expected vs actual JSON payload.
- State explicitly whether the bug originates in Backend, Frontend, or OpenAPI contract specification.
