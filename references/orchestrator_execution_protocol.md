# Orchestrator Execution & Circuit Breaker Protocol

This document defines mandatory protocols for Orchestrator execution limits, delegation thresholds, and circuit breaker anti-looping rules under Spec-Driven Development (SDD).

---

## 1. Universal Strict Planning & Delegation Threshold (STRICT PLAN FIRST)

1. **Mandatory Pre-Execution Plan & Approval (STRICT PLAN FIRST)**:
   - BEFORE making ANY file edits (whether micro-fixes, single line edits, configs, typos, or large feature code) or running deployment commands, the Orchestrator MUST first formulate a plan in chat (or create `implementation_plan.md` / `.openspec/proposal.md`), explicitly detailing:
     - The root cause / rationale for the change.
     - The exact target files to be modified.
   - The Orchestrator MUST STOP and wait for explicit textual user confirmation in chat ("ok", "делай", "погнали", "одобряю") BEFORE invoking ANY file editing tool or executing worker tasks.
   - Modifying files directly without prior plan presentation and human textual approval is a CRITICAL PROTOCOL VIOLATION.

2. **Subagent & Worker LLM Delegation (> 20 lines / Multi-step features)**:
   - Any non-trivial task (creating UI components, backend endpoints, database migrations, CI/CD pipelines, Docker configs, or deployment scripts) MUST be specified in English `.openspec/specs/task_xxx.yaml` or `.openspec/instruction.md`.
   - The Orchestrator MUST delegate execution to a Worker subagent via `ask_local_llm.py` specifying the appropriate system persona (`devops_worker_persona`, `backend_worker_persona`, `frontend_worker_persona`, etc.).
   - **For Frontend Worker Tasks**: The Orchestrator MUST pass/inject `--rules references/frontend_best_practices.md` to physically inject zero-config and relative path rules into the Worker prompt.
   - **For Backend & DevOps Worker Tasks**: The Orchestrator MUST pass/inject `--rules references/backend_best_practices.md` to physically inject dynamic infrastructure, container isolation, and anti-hardcode IP rules into the Worker prompt.
   - **For TypeScript Tasks**: The Orchestrator MUST pass `--rules references/typescript_advanced_types_guide.md` to `ask_local_llm.py` to physically inject advanced type safety rules into the Worker prompt.
3. **Three Mandatory Pillars of SDD Execution**:

   a) **Сначала Спецификация (Mandatory Contract First)**:
      - Forbidden to delegate or write ANY implementation code (`.ts`, `.html`, `.py`, etc.) without a pre-written contract/spec file (`.openspec/instruction.md` or `.openspec/specs/task_xxx.yaml`).

   b) **Сначала Тест (TDD Red Phase)**:
      - Before writing implementation code, the Worker or Orchestrator MUST first write a failing unit/integration test (`*.spec.ts`, `test_*.py`) defining the expected behavior, and verify that the test fails (Red Phase) prior to writing passing code.

   c) **DEFAULT: Strict Local LLM Delegation Only (По умолчанию только локальная LLM)**:
      - BY DEFAULT, ALL code writing, component creation, refactoring, and file generation MUST be executed STRICTLY by querying the local LLM (Ollama / LM Studio) via `python scripts/ask_local_llm.py`.
      - **Sole Exception ("Сделай сам")**: The Orchestrator is ONLY allowed to write implementation code files directly using IDE tools IF AND ONLY IF the user explicitly orders in chat: *"сделай сам"*, *"делай сам"*, or *"пиши сам"*.
      - Without this explicit command, direct implementation code writing by the Orchestrator is STRICTLY FORBIDDEN.

   d) **Физический вызов локальной LLM (No Text Simulation)**:
      - The Orchestrator MUST NEVER simulate or pretend to call `ask_local_llm.py` by outputting a fake generated code response in chat text.
      - The Orchestrator MUST physically invoke `run_command` with `python .../ask_local_llm.py` to query LM Studio / Ollama and read the generated file output.

4. **Strict Context & Phase Isolation Protocol (Planner vs Coder)**:
   - **Phase 1: Planning (Orchestrator)**: Reads all relevant project documentation (`docs/`, `.openspec/system-architecture.md`, `README.md`) to formulate the design and creates the required Markdown specs (`.openspec/proposal.md`, `.openspec/design.md`, `.openspec/instruction.md`).
   - **Pre-Delegation Spec Gate (STRICT)**: The Orchestrator MUST NEVER call `ask_local_llm.py` or delegate tasks to a Worker LLM/subagent until the Markdown spec files are physically written to `.openspec/` AND explicit textual approval has been granted by the human user in chat. Calling Worker LLM directly without pre-written Markdown specs is a CRITICAL PROTOCOL VIOLATION.
   - **Phase 2: Coding (Worker LLM / Subagent)**: The Worker LLM is provided ONLY with the approved micro-spec (`task_xxx.yaml` / `instruction.md`), target file paths, and coding standards. The Worker LLM MUST NOT load global `docs/` planning noise, preventing context pollution, saving token budget, and eliminating hallucinations.

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

## 5. Mandatory Pre-Planning Documentation Lock & Strict Compliance Protocol

Before generating ANY proposal, technical plan, architecture answer, or writing code:

1. **Mandatory First Tool Call Gate**: The agent's VERY FIRST action in a turn MUST be tool calls (`list_dir` on `docs/` / `.openspec/` and `view_file` on target documentation like `.openspec/system-architecture.md`, `docs/*.md`).
2. **Strict Prohibition on Text Generation Before Reading**: Outputting text proposals, architecture assumptions, or code plans BEFORE invoking `view_file` on `docs/` / `.openspec/` files in the current session is STRICTLY FORBIDDEN.
3. **Zero Self-Willed Shortcuts Policy (Strict Spec Compliance)**:
   - The agent MUST NEVER make architectural or design decisions at its own discretion ("на свое усмотрение") or introduce simplified shortcuts (e.g. single-database multi-tenancy) that deviate from or contradict written project documentation.
   - Whatever is specified in the project documentation MUST be implemented EXACTLY AS WRITTEN ("так как написано").
4. **Mandatory Pre-Execution Plan Presentation in Chat**:
   - BEFORE writing or modifying ANY code or creating implementation files, the agent MUST explicitly output in chat:
     1. **Docs Inspected**: List of specific documentation files read.
     2. **Documented Requirements**: Clear summary of what the documentation specifies.
     3. **Execution Plan**: Exact step-by-step implementation plan strictly adhering to the documented specification.


## 6. Dynamic Mode Switching Protocol

The user or Orchestrator can trigger dedicated modes at any point in the conversation:
- **`MODE: ANALYZE` (`Режим: Анализ`)**: Read-Only codebase investigation. Code changes strictly forbidden.
- **`MODE: PLAN` (`Режим: Планирование`)**: Architecture design and spec creation. Reads `docs/`, writes `proposal.md`, `api-contract.yaml`, and `.openspec/instruction.md`. Code writing forbidden.
- **`MODE: CODE` (`Режим: Код`)**: Pure implementation based strictly on `.openspec/instruction.md`. Unloads `docs/` and planning noise. Writes code & verifies build/tests.
- **`MODE: BUG` (`Режим: Баг`)**: Bug investigation and fix. Diagnostic log proof required. Regression test mandatory. `instruction.md` updated ONLY after fix verification.

---

## 7. Context-Aware Verification Protocol (Bug Fixing vs Feature Development)

1. **Feature Development (`MODE: CODE`)**:
   - Automated unit/integration tests (`npm test`), code coverage (>= 80%), and clean TypeScript compilation are completely sufficient for new features before staging/deployment.

2. **Bug Fixing (`MODE: BUG` - Mandatory Live Proof)**:
   - When investigating or fixing a bug, clean compilation or editing code is **NEVER** sufficient.
   - **Mandatory Anti-Looping Live Proof**: The agent MUST execute a concrete runtime check (reproducing test script, `curl` request, live server endpoint call, or log inspection) demonstrating that the specific bug condition no longer occurs and returns `HTTP 200 OK` / `exit 0` with valid payload BEFORE declaring the bug resolved.
   - **Strict Prohibition**: Declaring a bug fixed without displaying actual terminal execution output proving the fix is a CRITICAL PROTOCOL VIOLATION.

---

## 8. Mandatory Pre-Code Explanation Rule for Bug Fixing (MODE: BUG)

Before invoking ANY code editing tool (`replace_file_content`, `multi_replace_file_content`, `write_to_file`) during bug fixing:
1. **Mandatory Pre-Fix Explanation in Chat FIRST**: The agent MUST explicitly output a concise report in chat containing:
   - **Root Cause (Причина бага)**: Exact file path, line number, and technical explanation of the failure.
   - **Proposed Fix Strategy (Что будет сделано)**: Exact description of the proposed logic changes.
   - **Target Files (Затронутые файлы)**: List of files that will be modified.
2. **Strict Prohibition**: Silently executing code edit tools during bug resolution without first presenting the root cause and proposed fix plan in chat is STRICTLY FORBIDDEN.








