# FYPO AI Migration Platform

## 1. Idea

Build an internal AI-powered migration platform that uses **GitHub Copilot Cloud Agents** to migrate existing business logic written by business users in **Dataiku Python scripts** into the existing FYPO solution.

The platform should not try to replace the FYPO architecture.

Instead, it should understand the existing FYPO repositories, identify which repositories need to change for a new business service, create repository-specific Copilot Cloud Agent tasks, track those tasks, collect the resulting code changes, and eventually create/track pull requests.

The first target use case is:

> Migrate the existing **Duration Extension** Dataiku implementation into the FYPO solution.

---

# 2. Existing FYPO Architecture

The current FYPO system has multiple separate services/repositories.

```text
FYPO Studio
    |
    v
FYPO Service
    |
    v
FYPO Data Access
    |
    +-- Currency Repartition
    |
    +-- ETF Basket Primer
    |
    +-- Other Business Services
    |
    +-- Duration Extension       <-- New Business Service
    |
    v
FYPO Aladdin Wrapper
    |
    v
BRS Endpoints
    |
    v
Aladdin
```

### FYPO Studio

The Python-based FYPO Studio is the user-facing/application layer.

It calls:

```text
FYPO Studio
    |
    v
FYPO Service
```

### FYPO Service

FYPO Service acts primarily as the proxy/API layer.

It receives requests from FYPO Studio and calls FYPO Data Access.

```text
FYPO Studio
    |
    v
FYPO Service
    |
    v
FYPO Data Access
```

### FYPO Data Access

FYPO Data Access contains the business logic.

It contains multiple independent business services such as:

- Currency Repartition
- ETF Basket Primer
- Other portfolio-related functionality
- New business services such as Duration Extension

It also communicates with the appropriate lower-level components when Aladdin functionality is required.

### FYPO Aladdin Wrapper

If a business service in FYPO Data Access needs an Aladdin API/BRS endpoint, it should **not call Aladdin directly**.

The intended architecture is:

```text
FYPO Data Access
       |
       v
FYPO Aladdin Wrapper
       |
       v
BRS Endpoint
       |
       v
Aladdin
```

This repository/service owns the Aladdin/BRS integration layer.

---

# 3. The Migration Problem

Business users may already have business logic implemented as Python scripts in Dataiku.

For example:

```text
Dataiku
    |
    +-- duration_extension.py
    |
    +-- helper scripts
    |
    +-- portfolio processing
    |
    +-- optimizer interaction
    |
    +-- Aladdin/BRS interaction
    |
    +-- output generation
```

The business behavior already exists.

The problem is that this logic needs to be migrated into the FYPO architecture.

The migration should therefore be:

```text
Dataiku implementation
        |
        v
AI analysis
        |
        v
Understand business logic
        |
        v
Understand existing FYPO architecture
        |
        v
Identify reusable components
        |
        v
Identify missing components
        |
        v
Create migration plan
        |
        v
Implement changes using Copilot Cloud Agents
```

The objective is **not** to blindly copy the Dataiku Python code.

The objective is to preserve the business behavior while adapting the implementation to existing FYPO patterns.

---

# 4. Why an Orchestrator Is Needed

GitHub Copilot Cloud Agent tasks are associated with a specific repository.

The FYPO architecture spans multiple repositories:

```text
fypo-studio
fypo-service
fypo-data-access
fypo-aladdin-wrapper
```

Therefore, a single Copilot task should not be responsible for arbitrarily modifying all repositories.

Instead, create a separate repository/service:

```text
fypo-ai-orchestrator
```

The orchestrator becomes the control plane for cross-repository work.

```text
                         +--------------------------+
                         |   FYPO AI Orchestrator   |
                         |                          |
                         | Migration orchestration  |
                         | Repository discovery     |
                         | Task management          |
                         | Dependency management    |
                         | Migration state          |
                         +------------+-------------+
                                      |
                   +------------------+------------------+
                   |                  |                  |
                   v                  v                  v
             Copilot Task       Copilot Task       Copilot Task
             fypo-aladdin       fypo-data-access    fypo-service
             -wrapper
```

---

# 5. Separation of Responsibilities

## FYPO AI Orchestrator

The orchestrator answers:

> Which repositories need to change, what needs to happen in each repository, and in what order?

It manages:

- Migration
- Repository discovery
- Repository dependencies
- Analysis tasks
- Implementation tasks
- Copilot task IDs
- Task statuses
- Migration plans
- Diffs
- Pull requests
- Overall migration state

## GitHub Copilot Cloud Agent

Copilot answers:

> How should the required work be implemented inside this particular repository?

It works within the repository assigned to its task.

For example:

```text
Orchestrator
    |
    +--> Copilot task -> fypo-aladdin-wrapper
    |
    +--> Copilot task -> fypo-data-access
    |
    +--> Copilot task -> fypo-service
```

## Repository-specific instructions

Each FYPO repository can contain its own Copilot instructions describing how work should be done in that repository.

For example:

```text
fypo-data-access
    |
    +-- Copilot instructions
    |
    +-- Business logic conventions
    |
    +-- Existing patterns
```

```text
fypo-aladdin-wrapper
    |
    +-- Copilot instructions
    |
    +-- BRS integration patterns
    |
    +-- Authentication/configuration patterns
```

```text
fypo-service
    |
    +-- Copilot instructions
    |
    +-- API patterns
    |
    +-- Request/response conventions
```

This allows the orchestrator to remain repository-independent while each repository teaches Copilot how to work correctly inside that repository.

---

# 6. Central Migration Object

Every migration should have a unique migration ID.

Example:

```text
MIG-1024
```

The migration becomes the central state object.

```text
MIG-1024
|
+-- business_service
|      duration_extension
|
+-- source
|      Dataiku
|
+-- repositories
|
+-- plan
|
+-- tasks
|
+-- diffs
|
+-- pull_requests
```

---

# 7. Complete MIG-1024 Structure

```text
MIG-1024
|
+-- business_service
|      duration_extension
|
+-- source
|      Dataiku
|
+-- repositories
|      |
|      +-- fypo-aladdin-wrapper
|      |      analysis: completed
|      |      implementation: completed
|      |      tests: passed
|      |
|      +-- fypo-data-access
|      |      analysis: completed
|      |      implementation: running
|      |
|      +-- fypo-service
|             analysis: waiting
|             implementation: waiting
|
+-- plan
|
+-- tasks
|
+-- diffs
|
+-- pull_requests
```

For the initial MVP, test orchestration is not part of the workflow.

The `tests: passed` field shown above is not an active test orchestration stage in the MVP. It can simply represent information returned by an existing repository/task process if available.

---

# 8. Migration Workflow

The complete migration workflow is:

```text
Business User
      |
      | "Migrate Duration Extension"
      v
Streamlit
      |
      v
FYPO AI Orchestrator
      |
      v
Analyze Dataiku
      |
      v
Analyze FYPO repositories
      |
      v
Migration Plan
      |
      v
User Approval
      |
      v
Dependency Graph
      |
      v
Create repository-specific Copilot tasks
      |
      v
Poll tasks
      |
      v
Collect changed files and diffs
      |
      v
Create/track Pull Requests
```

---

# 9. Phase 1 - Create Migration

The user enters:

```text
Business Service:
Duration Extension

Source:
Dataiku

Dataiku Implementation:
<Python scripts>
```

The orchestrator creates:

```text
MIG-1024
```

Initial state:

```text
MIG-1024
|
+-- business_service: duration_extension
+-- source: Dataiku
+-- status: created
```

The orchestrator loads the configured FYPO repositories.

---

# 10. Phase 2 - Repository Analysis

The orchestrator creates analysis tasks for relevant repositories.

Example:

```text
MIG-1024
|
+-- Analysis
       |
       +-- fypo-data-access
       |
       +-- fypo-aladdin-wrapper
       |
       +-- fypo-service
```

These initial tasks should be **analysis-only**.

They should not modify code.

---

# 11. Data Access Analysis

The Copilot task for `fypo-data-access` should investigate:

1. Existing business services
2. Closest existing service to Duration Extension
3. Existing portfolio models
4. Existing optimizer integration
5. Existing utilities
6. Existing validation
7. Existing configuration
8. Existing error handling
9. Existing logging
10. Existing service structure
11. Reusable components
12. Components that must be created

The agent should answer:

```text
What can be reused?
What must be migrated?
What must be created?
What should not be duplicated?
```

---

# 12. Aladdin Wrapper Analysis

The Copilot task for `fypo-aladdin-wrapper` should investigate:

1. Existing BRS endpoints
2. Existing portfolio APIs
3. Existing holdings APIs
4. Existing duration-related APIs
5. Existing request/response models
6. Existing authentication
7. Existing configuration
8. Existing wrapper patterns

The important question is:

```text
Does the required Aladdin/BRS endpoint already exist?
```

If yes:

```text
REUSE
```

If no:

```text
CREATE
```

The new endpoint should follow the existing wrapper pattern.

---

# 13. FYPO Service Analysis

The Copilot task for `fypo-service` should investigate:

1. Existing API endpoints
2. Existing routing
3. Request models
4. Response models
5. Validation
6. Dependency injection
7. Existing patterns for exposing Data Access functionality

The FYPO Service should remain a thin API/proxy layer.

---

# 14. Migration Analysis Result

The orchestrator combines the analysis results.

Example:

```text
Duration Extension Migration Analysis

Business Logic
-------------------------------
- Duration calculation
- Portfolio processing
- Optimizer interaction
- Business validations

Existing FYPO Components
-------------------------------
- Portfolio model
- Optimizer client
- Existing portfolio APIs
- Existing configuration

Existing Aladdin APIs
-------------------------------
- Portfolio endpoint
- Holdings endpoint

Missing Aladdin APIs
-------------------------------
- Duration BRS endpoint

New Components
-------------------------------
- Duration Extension business service
- Duration response model
- Duration BRS wrapper
- FYPO Service endpoint
```

---

# 15. Migration Matrix

The orchestrator should generate a migration matrix.

Example:

| Dataiku Component | FYPO Target | Action |
|---|---|---|
| `calculate_duration()` | FYPO Data Access | Migrate |
| `get_portfolio()` | Existing Portfolio Client | Reuse |
| `get_holdings()` | Existing Aladdin Wrapper | Reuse |
| `call_duration_brs()` | FYPO Aladdin Wrapper | Create |
| `validate_input()` | Existing Validator | Reuse |
| Dataiku configuration | FYPO configuration | Adapt |
| Dataiku output | FYPO response model | Create |

This matrix becomes part of the migration plan.

---

# 16. Migration Plan

The final plan should contain:

```text
Plan
|
+-- Business Logic
|
+-- Files To Create
|
+-- Files To Modify
|
+-- Files To Reuse
|
+-- Aladdin Endpoints
|
+-- Repository Actions
|
+-- Dependency Order
```

Example:

```text
Repository Actions

fypo-aladdin-wrapper
    Add missing Duration BRS wrapper

fypo-data-access
    Add Duration Extension business service
    Reuse existing optimizer functionality
    Reuse existing portfolio functionality

fypo-service
    Add Duration Extension API endpoint
```

---

# 17. Repository Dependency Graph

The orchestrator needs to understand repository dependencies.

Example:

```yaml
repositories:

  fypo-service:
    role: api
    depends_on:
      - fypo-data-access

  fypo-data-access:
    role: business_logic
    depends_on:
      - fypo-aladdin-wrapper

  fypo-aladdin-wrapper:
    role: aladdin_integration
    depends_on: []
```

This produces:

```text
fypo-aladdin-wrapper
          |
          v
fypo-data-access
          |
          v
fypo-service
```

The orchestrator can use this dependency graph to determine execution order.

---

# 18. Important Reuse Rule

The migration agent must distinguish between:

```text
REUSE
MIGRATE
CREATE
ADAPT
```

Example:

```text
Dataiku:
get_portfolio()

FYPO:
Existing portfolio client

Action:
REUSE
```

Example:

```text
Dataiku:
custom duration calculation

FYPO:
No equivalent implementation

Action:
MIGRATE
```

Example:

```text
Dataiku:
call duration BRS endpoint

FYPO:
No duration wrapper exists

Action:
CREATE
```

Example:

```text
Dataiku:
Dataiku-specific configuration

FYPO:
Existing FYPO configuration system

Action:
ADAPT
```

This is important because the objective is to avoid duplicate code.

---

# 19. Implementation Workflow

After the user approves the migration plan:

```text
User Approval
      |
      v
Implementation
      |
      +--> fypo-aladdin-wrapper
      |
      +--> fypo-data-access
      |
      +--> fypo-service
```

Each implementation is a separate Copilot Cloud Agent task.

---

# 20. Repository-Specific Copilot Tasks

## Aladdin Wrapper

Prompt concept:

```text
Implement the approved Duration Extension migration in the
fypo-aladdin-wrapper repository.

Use the existing BRS wrapper implementation as the pattern.

If the required duration endpoint already exists, reuse it.

If it does not exist, add the endpoint using the existing
wrapper conventions.

Do not modify unrelated functionality.
```

## Data Access

Prompt concept:

```text
Implement Duration Extension in fypo-data-access.

Use the Dataiku implementation as the behavioral reference.

Use the approved migration plan.

Reuse existing portfolio and optimizer functionality.

Business logic belongs in Data Access.

Do not directly call Aladdin/BRS.

Use the FYPO Aladdin Wrapper for Aladdin communication.

Follow the closest existing business service pattern.

Do not modify unrelated services.
```

## FYPO Service

Prompt concept:

```text
Expose Duration Extension through fypo-service.

Follow the existing API patterns.

Keep the service layer thin.

Call FYPO Data Access rather than implementing business logic
inside the API layer.

Do not modify unrelated endpoints.
```

---

# 21. Existing Copilot Integration

The existing implementation already has an important foundation:

```text
Streamlit
    |
    v
Create Copilot Task
    |
    v
Task ID
    |
    v
Poll Task ID
    |
    v
Task Completed
    |
    v
Get File Changes
    |
    v
Show Changed Lines
```

This should not be thrown away.

It becomes a lower-level component of the new orchestrator.

```text
Migration Orchestrator
        |
        v
Copilot Task Manager
        |
        +-- create task
        |
        +-- get task
        |
        +-- poll task
        |
        +-- collect diff
        |
        +-- collect changed files
```

---

# 22. Task State

Each repository task should have its own state.

Suggested state machine:

```text
WAITING
   |
   v
ANALYZING
   |
   v
ANALYSIS_COMPLETED
   |
   v
IMPLEMENTATION_WAITING
   |
   v
IMPLEMENTING
   |
   v
IMPLEMENTATION_COMPLETED
```

Failure:

```text
IMPLEMENTING
      |
      v
   FAILED
      |
      v
    RETRY
```

The MVP can keep retry handling simple.

---

# 23. Migration-Level State

The overall migration can use:

```text
CREATED
    |
    v
ANALYZING
    |
    v
PLAN_READY
    |
    v
APPROVED
    |
    v
RUNNING
    |
    v
COMPLETED
```

Failure:

```text
RUNNING
   |
   v
FAILED
```

---

# 24. Streamlit UI

The initial Streamlit application should focus on these screens/features:

1. Create Migration
2. Migration Analysis
3. Migration Plan
4. Repository/Task Status
5. Changed Files
6. Line-by-line Diff
7. Pull Requests

No test orchestration is required in the first version.

---

# 25. Create Migration Screen

Example:

```text
+-----------------------------------------------+
| Create Migration                              |
|                                               |
| Business Service:                             |
| [ duration_extension                       ]  |
|                                               |
| Source:                                       |
| [ Dataiku                                  ]  |
|                                               |
| Dataiku Implementation:                       |
| +-------------------------------------------+ |
| |                                           | |
| | Python code                               | |
| |                                           | |
| +-------------------------------------------+ |
|                                               |
|              [ Create Migration ]             |
+-----------------------------------------------+
```

---

# 26. Migration Dashboard

Example:

```text
+------------------------------------------------------+
|                 Migration MIG-1024                   |
|                                                      |
| Business Service: Duration Extension                 |
| Source: Dataiku                                      |
| Status: RUNNING                                      |
+------------------------------------------------------+

Repositories

fypo-aladdin-wrapper
    Analysis:        COMPLETED
    Implementation:  COMPLETED

fypo-data-access
    Analysis:        COMPLETED
    Implementation:  RUNNING

fypo-service
    Analysis:        WAITING
    Implementation:  WAITING
```

---

# 27. Migration Plan Screen

Example:

```text
Migration Plan

Business Logic
    - Duration calculation
    - Portfolio processing
    - Optimizer interaction

Files To Create
    - duration_extension/...

Files To Modify
    - ...

Files To Reuse
    - Existing PortfolioClient
    - Existing OptimizerClient

Aladdin Endpoints
    - Portfolio
    - Holdings
    - Duration BRS endpoint

Dependency Order

1. fypo-aladdin-wrapper
2. fypo-data-access
3. fypo-service

             [ Approve Migration ]
```

---

# 28. Task Screen

Example:

```text
Tasks

TASK-001
Repository: fypo-aladdin-wrapper
Type: Analysis
Status: COMPLETED

TASK-002
Repository: fypo-data-access
Type: Implementation
Status: RUNNING

TASK-003
Repository: fypo-service
Type: Implementation
Status: WAITING
```

---

# 29. Diff Screen

The existing functionality of displaying only changed lines should remain.

Example:

```diff
class DurationExtension:

+    def calculate_duration(self, portfolio):
+        ...
+
+    def extend_duration(self, portfolio):
+        ...
```

The user should be able to see:

```text
Repository
    |
    +-- Changed files
    |
    +-- Added lines
    |
    +-- Modified lines
    |
    +-- Deleted lines
```

---

# 30. Pull Requests

After implementation, the migration should track pull requests.

```text
MIG-1024
|
+-- Pull Requests
       |
       +-- fypo-aladdin-wrapper
       |      PR-001
       |
       +-- fypo-data-access
       |      PR-002
       |
       +-- fypo-service
              PR-003
```

The orchestrator does not need to merge the PRs in the initial MVP.

It only needs to track them.

---

# 31. Proposed High-Level Architecture

```text
                         +----------------------+
                         |      Streamlit       |
                         |        UI            |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         |   FYPO AI            |
                         |   Orchestrator API   |
                         +----------+-----------+
                                    |
             +----------------------+----------------------+
             |                      |                      |
             v                      v                      v
     Migration Manager       Task Manager          Repository Manager
             |                      |                      |
             |                      v                      |
             |               Copilot Client               |
             |                      |                      |
             |                      v                      |
             |                 GitHub API                  |
             |                                             |
             +----------------------+----------------------+
                                    |
                                    v
                         Repository Dependency Graph
                                    |
                  +-----------------+----------------+
                  |                 |                |
                  v                 v                v
          fypo-aladdin       fypo-data-access   fypo-service
             wrapper
```

---

# 32. Suggested Orchestrator Components

```text
fypo-ai-orchestrator/

backend/
|
+-- api/
|   |
|   +-- migrations
|   +-- tasks
|   +-- repositories
|   +-- plans
|
+-- orchestrator/
|   |
|   +-- migration_orchestrator
|   +-- task_orchestrator
|   +-- workflow_engine
|   +-- dependency_graph
|
+-- github/
|   |
|   +-- github_client
|   +-- copilot_client
|   +-- repository_client
|   +-- pull_request_client
|   +-- diff_client
|
+-- agents/
|   |
|   +-- analysis_agent
|   +-- migration_agent
|
+-- models/
|   |
|   +-- migration
|   +-- task
|   +-- repository
|   +-- plan
|
+-- storage/
|   |
|   +-- redis
|   +-- migration_repository
|
+-- config/
|   |
|   +-- repositories.yaml
|
+-- prompts/
|
+-- frontend/
|   |
|   +-- streamlit
|
+-- tests/
```

---

# 33. Repository Registry

The orchestrator should have a central repository registry.

Example:

```yaml
repositories:

  fypo-service:
    owner: your-org
    repo: fypo-service
    role: api
    depends_on:
      - fypo-data-access

  fypo-data-access:
    owner: your-org
    repo: fypo-data-access
    role: business_logic
    depends_on:
      - fypo-aladdin-wrapper

  fypo-aladdin-wrapper:
    owner: your-org
    repo: fypo-aladdin-wrapper
    role: aladdin_integration
    depends_on: []
```

This lets the orchestrator know the architecture without hard-coding repository behavior into the workflow.

---

# 34. Data Storage

Redis can be used for migration/task state.

Example:

```text
migration:MIG-1024
```

contains:

```json
{
  "migration_id": "MIG-1024",
  "business_service": "duration_extension",
  "source": "Dataiku",
  "status": "running"
}
```

Repository state can be stored as part of the migration.

The design should allow replacing Redis with a persistent relational database later if historical reporting becomes important.

---

# 35. Important Architectural Principle

The orchestrator should **not implement FYPO business logic**.

It should only orchestrate.

```text
Wrong:

Orchestrator
    |
    +-- Duration calculation
    +-- Portfolio calculation
    +-- Aladdin API logic


Correct:

Orchestrator
    |
    +-- Analyze
    +-- Plan
    +-- Select repositories
    +-- Create Copilot tasks
    +-- Track tasks
    +-- Collect results
    +-- Track PRs
```

The actual business logic remains in the appropriate FYPO repository.

---

# 36. Important Copilot Principle

Do not give Copilot one giant task such as:

```text
"Implement Duration Extension across all FYPO repositories."
```

Instead:

```text
Orchestrator
      |
      +-- Analyze fypo-aladdin-wrapper
      |
      +-- Analyze fypo-data-access
      |
      +-- Analyze fypo-service
      |
      +-- Build combined migration plan
      |
      +-- Approve
      |
      +-- Implement fypo-aladdin-wrapper
      |
      +-- Implement fypo-data-access
      |
      +-- Implement fypo-service
```

This keeps each Copilot task repository-specific.

---

# 37. The Core Value of the Platform

The platform turns:

```text
Business User
    |
    v
Dataiku Python Script
    |
    v
Manual developer migration
    |
    v
Multiple repositories
    |
    v
Manual investigation
```

into:

```text
Business User
    |
    v
Dataiku Python Script
    |
    v
FYPO AI Orchestrator
    |
    +-- Repository Analysis
    |
    +-- Migration Plan
    |
    +-- Repository Dependency Analysis
    |
    +-- Copilot Cloud Agent Tasks
    |
    +-- Diff Collection
    |
    +-- Pull Request Tracking
```

---

# 38. Initial MVP Scope

The first version should include only:

```text
1. Create migration

2. Store migration ID

3. Register FYPO repositories

4. Analyze repositories using Copilot Cloud Agent

5. Collect analysis results

6. Build migration plan

7. Show migration plan

8. User approval

9. Create implementation tasks

10. Execute repository-specific Copilot tasks

11. Poll task status

12. Track repository status

13. Collect changed files

14. Display line-by-line diff

15. Track pull requests
```

The first version does NOT need:

```text
- Automated test orchestration
- Security scanning
- Architecture validation
- Automatic merge
- Complex retry engine
- Production deployment
- Full autonomous approval
```

These can be added later.

---

# 39. Future Direction

Once the MVP works, the platform can evolve into a broader AI software engineering platform.

Potential future capabilities:

```text
Dataiku Migration
        |
        +-- Business Service Migration
        |
        +-- Bug Fix
        |
        +-- Refactoring
        |
        +-- Add Aladdin Endpoint
        |
        +-- API Migration
        |
        +-- Documentation
```

The same orchestrator architecture can support these workflows.

---

# 40. Final Concept

The core concept is:

```text
                     BUSINESS USER
                           |
                           |
                  "Migrate Duration
                     Extension"
                           |
                           v
                  +----------------+
                  | FYPO AI        |
                  | Orchestrator   |
                  +-------+--------+
                          |
              +-----------+-----------+
              |           |           |
              v           v           v
          Analyze       Analyze     Analyze
          Data Access  Aladdin      Service
              |         Wrapper        |
              +-----------+-----------+
                          |
                          v
                   Migration Plan
                          |
                          v
                    USER APPROVAL
                          |
                          v
                 DEPENDENCY GRAPH
                          |
             +------------+------------+
             |            |            |
             v            v            v
          Copilot      Copilot      Copilot
          Wrapper      Data Access  Service
             |            |            |
             +------------+------------+
                          |
                          v
                  CHANGED FILES
                          |
                          v
                       DIFF
                          |
                          v
                   PULL REQUESTS
```

The most important design principle is:

> **The FYPO AI Orchestrator owns the cross-repository workflow; GitHub Copilot Cloud Agent owns the implementation work inside each individual repository.**

This keeps the architecture clean, allows each FYPO repository to maintain its own conventions, and makes Dataiku-to-FYPO migration a repeatable process rather than a one-off manual development activity.
