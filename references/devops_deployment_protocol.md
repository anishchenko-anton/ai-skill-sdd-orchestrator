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

### A. Pure Git-Driven Workflow (No Manual File Copying)
- **Forbidden**: Manual copy-pasting or direct SFTP/SCP upload of application files, Docker configs, or source code directly to remote servers.
- **Mandatory Flow**: All infrastructure changes must be committed to Git and pulled on the destination host (`git push` from repository -> `git pull` on server) or deployed via automated CI/CD pipelines.

### B. Architectural Compliance & Environment Isolation
- **Environment Isolation**: Secrets, credentials, and host-specific settings MUST be isolated in environment files (`.env`). Standard `.env.example` templates must be maintained in Git.
- **Network Alignment**: Verify container network topology (`network_mode`, subnets, port bindings, reverse proxy routing) against system architecture before launching containers.

### C. Empirical Verification Before Success Announcement
NEVER declare a deployment, container restart, or server configuration successful based merely on command exit codes or `docker ps` listings.

The Orchestrator/DevOps Worker MUST perform empirical validation:
1. **Database Schema Integrity**: Verify database migrations or schema updates (e.g., `npx prisma db push` or `prisma migrate deploy`).
2. **HTTP Endpoints Check**: Perform HTTP GET/POST checks verifying `HTTP 200 OK` on health/application endpoints.
3. **Log Audit**: Inspect container logs (`docker logs --tail 50`) to ensure zero unhandled exceptions or crash loops.

---

## 3. Backpressure & Escalation

If environment variables, server credentials, network ports, or deployment targets are missing or ambiguous:
- Do NOT guess host IP addresses, SSH keys, or environment secrets.
- Stop execution and return a clear backpressure report requesting the missing details from the user.
