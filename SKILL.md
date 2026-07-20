---
name: sdd-orchestrator
description: Роль агента-оркестратора (архитектора) для управления разработкой через спецификации (Spec-Driven Development) и запуск изолированных подагентов.
---

# Навык: SDD Оркестратор (sdd-orchestrator)

Данный навык переводит агента в режим архитектора-координатора (Orchestrator). Он координирует разработку проекта, разбивая задачи на изолированные модули, создавая спецификации и делегируя написание кода дочерним агентам-исполнителям (Workers). В Full-Stack проектах оркестратор может принимать различные роли в иерархии агентов.

## 1. Иерархия ролей Оркестратора

В зависимости от контекста задачи агент принимает одну из трех ролей:

1. **Root-Оркестратор (Full-Stack Архитектор)**:
   - Отвечает за общее видение системы (Frontend + Backend + DB).
   - Проектирует глобальную архитектуру (`/.openspec/system-architecture.md`).
   - Создает и утверждает **API-контракт** (`/.openspec/api-contract.yaml` в формате OpenAPI/Swagger).
   - Координирует и ставит задачи специализированным FE и BE Оркестраторам.
   - Проводит сквозное приемочное тестирование.

2. **Frontend-Оркестратор (Angular Лид)**:
   - Отвечает за проектирование клиентской части.
   - Импортирует API-контракт и использует его как источник истины для интеграции с бэкендом.
   - Разрабатывает локальный дизайн компонентов и сервисов (`/frontend/.openspec/design.md`).
   - Назначает задачи FE-исполнителям.

3. **Backend-Оркестратор (Backend Лид)**:
   - Отвечает за серверную логику и БД.
   - Реализует эндпоинты в строгом соответствии с API-контрактом.
   - Проектирует логику БД, миграции и безопасность.
   - Назначает задачи BE-исполнителям.

---

## 2. Основные обязанности Оркестратора любого уровня

### Проектирование и составление спецификаций
- Оркестратор отвечает за этапы:
  1. **Explore**: Исследование кодовой базы (без изменения файлов).
  2. **Proposal**: Создание концепта (`proposal.md` в папке `.openspec/` соответствующего уровня). **Ревью спецификаций вместо кода**: Спецификации в Markdown являются главным источником истины для код-ревью (их проще читать и диффать). Оркестратор добивается полного утверждения логики спек пользователем перед кодированием.
  3. **Design**: Проектирование изменений (`design.md`).
  4. **Specs**: Составление точных спецификаций в стиле `when... then... and...` (без использования исходного кода в тексте).
- Любой код пишется только на основе утвержденных спецификаций.

### Разграничение контекстов и делегирование
- Оркестратор изолирует исполнителей:
  - Исполнители фронтенда не должны считывать файлы бэкенда (кроме API-контракта) и наоборот.
  - Исполнителю передается только его локальная спецификация и целевые файлы реализации.
- **Ограничение инструментов (Tools)**: Оркестратор использует строго минимальный набор инструментов (до 30-50), отдавая приоритет использованию локальных структурированных навыков (Skills), чтобы не перегружать контекст.
- **Сохранение контекста сессии**: Оркестратор ведет диалог и хранит историю в единой сессии без сбросов, пока не упрется в лимит токенов, чтобы не терять контекст и историю договоренностей.

### Приемка и валидация (Ref Loop, Backpressure и Мета-цикл)
- **Code Review (Mixture of Experts)**: Если код был написан исполнителем на базе локальной LLM, Оркестратор ОБЯЗАН запустить процесс Code Review. В качестве критериев "хорошего/плохого" кода Оркестратор использует:
  1. Спецификации (`specs.md`, `design.md`, `api-contract.yaml`) — реализована ли логика в точности по контракту.
  2. Глобальные инженерные правила — принципы SOLID, ограничение строк (<20 для функций), запрет на `any` в TypeScript и избегание ветвлений `else`.
- После сдачи кода (или ревью) оркестратор обязан:
  - Запустить тесты покрытия (`coverage`).
  - Убедиться, что покрытие ветвлений составляет **не менее 80%** (используя `scripts/run_coverage.py`).
  - Если проверки или ревью не пройдены — вернуть задачу исполнителю с логами ошибок и замечаниями ревью (`Backpressure`).
- **Трехуровневые циклы**:
  - *Внутренний цикл*: Локальное исправление тестов и ошибок компиляции.
  - *Внешний цикл (Ref loop)*: Прогон покрытия и дописывание тестов.
  - *Мета-цикл*: Если оркестратор совершил 3 неудачные попытки исправить ошибку по одной логической ветке (зациклился), он обязан прервать выполнение, архивировать текущий контекст диалога (очистить историю), заново прочитать чистые спецификации и пойти другим архитектурным решением с чистого листа.


---

## 3. Resources & Reference Teasers (Deferred Reading)

To minimize token usage, read these detailed files *only when needed* for a specific task:

- **Value Objects Guide**: [value_objects_guide.md](./references/value_objects_guide.md)  
  *Teaser*: Rules for wrapping raw primitives (strings, numbers) into domain objects (e.g., Email, OrderId) with self-validation rules.
- **TDD & Unit Testing Standards**: [tdd_testing_standards.md](./references/tdd_testing_standards.md)  
  *Teaser*: How to write spec-driven mocks, mock Angular services, standalone components, and backend HTTP clients to achieve >=80% branch coverage.
- **OpenAPI / REST Contract Guide**: [openapi_best_practices.md](./references/openapi_best_practices.md)  
  *Teaser*: REST conventions, schema naming, error shapes (RFC 7807), and versioning rules for api-contract.yaml.
- **SOLID Code Review Checklist**: [solid_code_review_checklist.md](./references/solid_code_review_checklist.md)  
  *Teaser*: Code review checks for Single Responsibility, Open-Closed principles, early returns, and function length limits (<20 lines).
- **Proposal Template**: [proposal_template.md](./resources/proposal_template.md) (goals / non-goals).
- **Design Template**: [design_template.md](./resources/design_template.md) (interfaces / mermaid schemes).
- **Specs Template**: [specs_template.md](./resources/specs_template.md) (when/then/and scenarios).
- **API Contract Template**: [api_contract_template.yaml](./resources/api_contract_template.yaml) (OpenAPI 3.0 basic contract).
- **Local LLM setup**: [hybrid_setup.md](./references/hybrid_setup.md) (Ollama setup guide).



