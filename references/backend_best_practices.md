# Backend Best Practices

This guide outlines standard software engineering and infrastructure practices that all Backend and DevOps Agents must follow.

---

## 1. Containerization & Docker Best Practices

### A. Multi-Stage Builds
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

### B. Principle of Least Privilege
Never run containers as the `root` user unless system-level permissions are strictly required.
- Switch to built-in non-root users (`USER node`).
- Create dedicated non-root users in custom Linux containers.

### C. Build Layer Caching
Order `Dockerfile` instructions from least-frequently-changed to most-frequently-changed to maximize Docker layer caching.
- *Correct*: `COPY package.json` -> `RUN npm install` -> `COPY src/ .`
- *Incorrect*: `COPY . .` -> `RUN npm install`

### D. Environment Variables
Never hardcode secrets or environment-specific config inside `Dockerfile` or `docker-compose.yml`. Use `.env` files.

---

## 2. 100% Dynamic Infrastructure & Zero-Config Architecture (CRITICAL)

NEVER hardcode generated runtime keys, public/private WireGuard keys, fixed host IPs, subnet CIDRs, or server-dependent parameters inside `docker-compose.yml`, `Dockerfile`, static `.env` files, or backend string templates (e.g. `confContent`).

- **Anti-pattern**: Hardcoding static WireGuard public keys (`WG_PUBLIC_KEY=xyz`), fixed node IPs (`192.168.121.2`), server public endpoints (`147.135.208.25:51821`), or CIDR subnets (`192.168.121.0/24`) in backend source code, DTOs, or `.env` files.
- **PROHIBITION OF FALLBACK IP LITERALS (STRICT)**: Using static IP strings as fallback defaults in code (e.g. `process.env.WG_CLIENT_IP || '192.168.121.2'`, `process.env.WG_ALLOWED_IPS || '192.168.121.0/24'`) is STRICTLY FORBIDDEN. If required configuration is missing, the system MUST throw an explicit error or calculate values dynamically — NEVER silently default to hardcoded IP literals.
- **PROHIBITION OF PLACEHOLDER KEYS & DUMMY SECRETS (STRICT SECURITY RULE)**: Returning fake placeholder strings (e.g. `return 'VISNET_DEV_SERVER_PUBLIC_KEY_PLACEHOLDER='`, `jwtSecret || 'secret'`) for WireGuard keys, secrets, or certificates is STRICTLY FORBIDDEN. If a required key/secret is missing, the service MUST throw an explicit startup error (`throw new Error(...)`) or dynamically read/generate keypairs at deploy time — NEVER return dummy placeholders.
- **Required Pattern**: Always design Zero-Config, environment-agnostic infrastructure:
  1. **Dynamic Runtime Discovery**: Use shared read-only volumes (e.g., `/etc/wireguard/publickey`) or init-scripts so services dynamically read generated state at startup.
  2. **Dynamic Network & Config Templates**: Populate WireGuard configuration templates (`.conf`) dynamically using environment variables (`WG_SERVER_ENDPOINT`, `WG_SUBNET_CIDR`, `SERVER_PUBLIC_IP`) or dynamic IP allocator services.
  3. **Universal Portability**: Infrastructure configurations MUST work out-of-the-box on ANY VPS/server without requiring manual environment file edits or code changes for IP addresses.

---

## 3. Strict Tenant Isolation & Dynamic Provisioning Guard (CRITICAL ANTI-PATTERN)

- **FORBIDDEN SHORTCUT**: Implementing tenant onboarding as single-database multi-tenancy or adding WireGuard peers to a single shared container (`visnet-wg-dev`).
- **MANDATORY ISOLATION**: Each company/tenant MUST be provisioned as a fully isolated stack: dedicated database container (`visnet-db-{company_id}`) and dedicated WireGuard container (`visnet-wg-{company_id}`).
- **PROVISIONER INTEGRATION**: Onboarding services must explicitly trigger dynamic container creation via Docker API / `/var/run/docker.sock` or dedicated provisioner workflows.
