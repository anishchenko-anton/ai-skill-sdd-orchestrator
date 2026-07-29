# DevOps & Infrastructure Deployment Protocol

This document defines mandatory operational rules and pre-flight protocols for Orchestrators and Workers managing server deployments, Docker environments, reverse proxies, and infrastructure under Spec-Driven Development (SDD).

---

## 1. Mandatory Pre-Flight Protocol (DevOps Auto-Loading)

Upon receiving ANY user request, prompt, or diagnostic question related to server deployment, Docker containerization, network configuration, or server management (even in consultation or discussion mode), the Orchestrator MUST IMMEDIATELY:

1. **Load Persona & Directives**:
   - Read `resources/devops_worker_persona.md` and `references/devops_deployment_protocol.md`.
   - Read relevant architecture documentation (`.openspec/system-architecture.md` or `docs/deployment-multi-env.md`).

2. **Prohibit Direct Ad-Hoc Execution**:
   - Do NOT execute ad-hoc manual SSH diagnostics or manual file edits without consulting the standard deployment workflow.

---

## 2. Infrastructure Standards & Protocols

### A. Pure Git-Driven Workflow (STRICT PROHIBITION ON SCP / SFTP / RSYNC)
- **STRICTLY FORBIDDEN**: Running `scp`, `sftp`, `rsync`, manual copy-pasting, or direct file uploads of application files, `docker-compose.yml`, `nginx.conf`, or source code directly to remote servers.
- **Mandatory Flow**: ALL deployment and server updates MUST be committed and pushed to Git (`git add` -> `git commit` -> `git push`), followed by pulling on the remote host (`ssh <host> "cd /path && git pull"`) or via automated CI/CD pipelines.
- **Violation Guard**: Executing `scp` or `sftp` to transfer project files to a server is a CRITICAL RULE VIOLATION.


### B. Architectural Compliance & Environment Isolation
- **Environment Isolation**: Secrets, credentials, and host-specific settings MUST be isolated in environment files (`.env`). Standard `.env.example` templates must be maintained in Git.
- **Network Alignment**: Verify container network topology (`network_mode`, subnets, port bindings, reverse proxy routing) against system architecture before launching containers.

### C. Empirical Verification Before Success Announcement
NEVER declare a deployment, container restart, or server configuration successful based merely on command exit codes or `docker ps` listings.

The Orchestrator/DevOps Worker MUST perform empirical validation:
1. **Database Schema Integrity**: Verify database migrations or schema updates (e.g., `npx prisma db push` or `prisma migrate deploy`).
2. **HTTP Endpoints Check**: Perform HTTP GET/POST checks verifying `HTTP 200 OK` on health/application endpoints.
3. **Log Audit**: Inspect container logs (`docker logs --tail 50`) to ensure zero unhandled exceptions or crash loops.

### D. 100% Dynamic Infrastructure & Zero-Config Architecture (CRITICAL)
- **Forbidden**: Hardcoding static runtime-generated keys (e.g., WireGuard public/private keys, ephemeral node IDs, static VPS public IPs) inside `docker-compose.yml`, `Dockerfile`, or static `.env` files.
- **Mandatory Flow**: Infrastructure design MUST be 100% portable and Zero-Config out-of-the-box. Services MUST dynamically read runtime-generated keys from shared volumes (read-only mounts), init scripts, or internal management APIs so that deployment succeeds automatically on ANY server.


---

## 3. Backpressure & Escalation

If environment variables, server credentials, network ports, or deployment targets are missing or ambiguous:
- Do NOT guess host IP addresses, SSH keys, or environment secrets.
- Stop execution and return a clear backpressure report requesting the missing details from the user.
