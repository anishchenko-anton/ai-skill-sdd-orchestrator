# OpenAPI and REST Best Practices

This guide outlines API design principles for Root Orchestrators to draft the `api-contract.yaml` (OpenAPI 3.0 specification). The API contract is the source of truth for both Frontend and Backend agents.

---

## 1. RESTful URL Naming Conventions

- **Use plural nouns for collections**: `/users`, `/orders`, `/items`. (Never use verbs in paths like `/getUser` or `/createOrder`).
- **Use HTTP methods to represent actions**:
  - `GET /items` - Get list of items.
  - `GET /items/{id}` - Get a single item.
  - `POST /items` - Create a new item (returns `201 Created`).
  - `PATCH /items/{id}` - Partially update fields of an item. (Prefer `PATCH` over `PUT` for partial edits).
  - `DELETE /items/{id}` - Delete an item.

---

## 2. Response Status Codes

Always return the correct semantic HTTP status code:
- `200 OK` - Successful request.
- `201 Created` - Resource successfully created.
- `204 No Content` - Successful request with empty response (e.g. deletion).
- `400 Bad Request` - Client-side validation failure.
- `401 Unauthorized` - Authentication required or failed.
- `403 Forbidden` - User is authenticated but lacks authorization for this resource.
- `404 Not Found` - Resource does not exist.
- `422 Unprocessable Entity` - Syntactically correct request containing semantic/business errors.
- `500 Internal Server Error` - Server crash/database failures (should never happen in production).

---

## 3. Error Representation (RFC 7807)

For all client-side and server-side errors (4xx/5xx), return structured error responses following the **Problem Details (RFC 7807)** format.

### OpenAPI Schema Example:
```yaml
ProblemDetails:
  type: object
  required:
    - type
    - title
    - status
    - detail
  properties:
    type:
      type: string
      format: uri
      example: "https://example.com/errors/invalid-parameters"
    title:
      type: string
      example: "Invalid Request Parameters"
    status:
      type: integer
      example: 400
    detail:
      type: string
      example: "The 'email' field must be a valid email address."
    instance:
      type: string
      format: uri
      example: "/api/v1/users"
```
