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
