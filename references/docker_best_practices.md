# Docker Best Practices

This guide outlines the standard practices that all DevOps Agents must follow when creating Docker images or `docker-compose.yml` files for the current project.

---

## 1. Multi-Stage Builds
Always use multi-stage builds to minimize the final image size and reduce the attack surface. Do not ship build tools (like `gcc`, `npm`, or `pip` dev-dependencies) in the final production image.

**Example (Node.js/NestJS):**
```dockerfile
# Stage 1: Build
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 2: Production
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY package*.json ./
RUN npm ci --only=production
USER node
CMD ["node", "dist/main"]
```

## 2. Principle of Least Privilege
Never run containers as the `root` user unless absolutely necessary (e.g., system-level containers). 
- In Node.js images, switch to the built-in `node` user: `USER node`.
- In custom images, create a dedicated non-root user and group before the `CMD` instruction.

## 3. Leverage Build Cache
Order your `Dockerfile` instructions from least-frequently-changed to most-frequently-changed to maximize Docker's layer caching.
- *Correct*: `COPY package.json` -> `RUN npm install` -> `COPY src/ .`
- *Incorrect*: `COPY . .` -> `RUN npm install`

## 4. Environment Variables
Never hardcode secrets inside `Dockerfile` or `docker-compose.yml`. Use `.env` files and reference them in Compose files.
```yaml
services:
  api:
    image: my-api:latest
    env_file:
      - .env.production
```

## 5. 100% Dynamic Infrastructure & Zero-Config Architecture (CRITICAL)
NEVER hardcode generated runtime keys, public/private WireGuard keys, fixed host IPs, or server-dependent parameters inside `docker-compose.yml`, `Dockerfile`, or static `.env` files.

- **Anti-pattern**: Hardcoding static WireGuard public keys (`WG_PUBLIC_KEY=xyz`) or fixed node credentials in `.env` or `docker-compose.yml`. When deploying on another VPS or environment, regenerating container state breaks static keys immediately.
- **Required Pattern**: Always design Zero-Config, environment-agnostic infrastructure:
  1. **Dynamic Runtime Discovery**: Use shared read-only volumes (e.g., `/etc/wireguard/publickey`) or init-scripts so services dynamically read generated state at startup.
  2. **Management API / Ephemeral States**: Fetch keys and server parameters dynamically via internal API endpoints or container state inspection.
  3. **Universal Portability**: Infrastructure configurations MUST work out-of-the-box on ANY VPS/server without requiring manual environment file edits for runtime-generated keys.

## 6. Strict Tenant Isolation & Dynamic Container Provisioning (STRICT ANTI-PATTERN GUARD)
- **STRICTLY FORBIDDEN**: Using shared multi-tenancy in a single PostgreSQL database or single shared WireGuard container (e.g. `visnet-wg-dev`) as a shortcut for tenant onboarding.
- **MANDATORY ARCHITECTURE**: Every company/tenant unit MUST be a fully isolated instance with its own dedicated database container (`visnet-db-{company_id}`) and its own dedicated WireGuard container (`visnet-wg-{company_id}`).
- **Dynamic Provisioner Enforcement**: Onboarding or setup services MUST interact with the Docker API / socket or Provisioner agent to dynamically spawn isolated container stacks per company/tenant. NEVER substitute isolated containers with single-table database inserts or shared WireGuard peers.


