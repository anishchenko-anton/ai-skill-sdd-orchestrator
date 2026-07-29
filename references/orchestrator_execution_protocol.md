# Orchestrator Execution & Circuit Breaker Protocol

This document defines mandatory protocols for Orchestrator execution limits, delegation thresholds, and circuit breaker anti-looping rules under Spec-Driven Development (SDD).

---

## 1. Universal Delegation Threshold (Scope Rule)

Orchestrators across ALL domains (Frontend, Backend, QA, DevOps/Infrastructure, Embedded) MUST strictly adhere to the scope threshold:

1. **Direct Execution (<= 15-20 lines)**:
   - Allowed ONLY for minor inline fixes, type fixes, single-line configuration tweaks, or urgent small bug patches.

2. **Mandatory Subagent Delegation (> 20 lines / Multi-step features)**:
   - Any non-trivial task (creating UI components, backend endpoints, database migrations, CI/CD pipelines, Docker configs, or deployment scripts) MUST be specified in English `.openspec/specs/task_xxx.yaml`.
   - The Orchestrator MUST delegate execution to a Worker subagent via `ask_local_llm.py` specifying the appropriate system persona (`devops_worker_persona`, `backend_worker_persona`, `frontend_worker_persona`, etc.).
   - **For TypeScript Tasks**: The Orchestrator MUST pass `--rules references/typescript_advanced_types_guide.md` to `ask_local_llm.py` to physically inject the advanced type safety rules into the Worker prompt.

3. **Strict Context & Phase Isolation Protocol (Planner vs Coder)**:
   - **Phase 1: Planning (Orchestrator)**: Reads all relevant project documentation (`docs/`, `.openspec/system-architecture.md`, `README.md`) to formulate the design and distills it into a compact, self-contained English micro-spec (`task_xxx.yaml` or `.openspec/instruction.md`).
   - **Phase 2: Coding (Worker LLM / Subagent)**: The Worker LLM is provided ONLY with the micro-spec (`task_xxx.yaml` / `instruction.md`), target file paths, and coding standards. The Worker LLM MUST NOT load global `docs/` planning noise, preventing context pollution, saving token budget, and eliminating hallucinations.

---


## 2. Universal Circuit Breaker Protocol (Anti-Looping)

To prevent resource exhaustion, token drain, and infinite debugging loops across CLI execution, builds, deployments, or automated tests:

1. **3-Attempt Failure Limit**:
   - If execution of terminal commands, build steps, test runs, or deployment tasks fails **3 consecutive times** along the same logical path, the Orchestrator MUST IMMEDIATELY HALT further execution.

2. **Escalation Protocol**:
   - Do NOT attempt a 4th automated retry.
   - Do NOT guess server credentials, ports, or missing environment configurations.
   - Output a clear, empirical error report to the user in chat (summarizing exact commands, stack traces, and failure points).
   - Explicitly ask the user for clarification, missing credentials, or manual guidance before proceeding.

---

## 3. DevOps & Infrastructure Pre-Flight Protocol

For any task involving server deployment, Docker, Nginx, network setup, or server diagnostics:
1. **Auto-Load Persona & Guides**: Immediately read `resources/devops_worker_persona.md` and `references/devops_deployment_protocol.md`.
2. **Git-Driven Only**: Enforce pure Git workflow (`git push`/`git pull`); prohibit manual file copying.
3. **Empirical Health Verification**: Verify Prisma/DB migrations, inspect logs, and confirm `HTTP 200 OK` before marking tasks complete.

---

## 4. Mandatory Component & Module Local Specification Protocol (.openspec/instruction.md)

Whenever working on, modifying, or creating ANY component, feature directory, or backend module:

1. **Pre-Task Spec Inspection**:
   - Before modifying or refactoring an existing module, the agent MUST read `.openspec/instruction.md` in that module directory to understand and align on expected behavior, state management, and contracts.

2. **New Module Creation FIRST**:
   - Before writing any implementation code (`.ts`, `.html`, `.css`, `.py`, etc.), the agent MUST create `.openspec/instruction.md` inside the target component/module directory FIRST.

3. **Continuous Spec Sync & Bug-Fix Post-Verification Update Rule**:
   - **Feature Work**: If module logic or interface contracts change during feature development, `instruction.md` MUST be updated to reflect the new state.
   - **Bug Fix Constraint**: When investigating or fixing bugs, DO NOT update `instruction.md` while the bug is active or unresolved.
   - **Post-Fix Update Only**: `instruction.md` MUST be updated **ONLY AFTER the bug has been empirically fixed, verified, and closed** (all tests pass, exit code 0). Upon resolution, update `instruction.md` with the verified root-cause fix and updated behavior contract.

---

## 5. Mandatory Pre-Planning Documentation Inspection Protocol (Auto-Read docs/ & .openspec/)

Before forming any proposal, technical plan, architecture answer, or delegating tasks:
1. **Mandatory Documentation Inspection FIRST**: The Orchestrator MUST execute file inspection tools (`list_dir`, `view_file`, `grep_search`) to read existing project documentation in `docs/`, `.openspec/`, and relevant architecture specification files.
2. **Strict Prohibition**: It is STRICTLY FORBIDDEN to draft a proposal, technical plan, or make assumptions about system design BEFORE reading the workspace's existing documentation in `docs/` and `.openspec/`.




