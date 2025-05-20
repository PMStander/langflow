# Project Memory Index

## Project Overview
Langflow is an open-source UI visual tool designed to facilitate the creation, experimentation, and deployment of LangChain applications through a drag-and-drop interface.
→ [Project Brief](core/projectbrief.md)

## Product Context
Langflow aims to democratize access to Large Language Model (LLM) application development by providing a visual, intuitive interface for building complex LangChain workflows.
→ [Product Context](core/productContext.md)

## System Architecture
Langflow follows a client-server architecture with a React frontend and FastAPI backend, designed for extensibility and ease of use.
→ [System Patterns](core/systemPatterns.md)
→ [Active Context](core/activeContext.md)
→ [Workflow Architecture](core/workflow-architecture.md)
→ [Event Handlers](core/event-handlers.md)
→ [Self-Healing System](core/self-healing.md)

## Current Focus
We're currently focused on resolving frontend and backend integration issues, particularly addressing memory constraints during the frontend build process.
→ [Active Context](core/activeContext.md)

## Project Status
- **Overall Progress**: Core features implemented, addressing build process issues
- **Current Phase**: Optimization and stabilization
- **Recent Achievements**: Implemented workaround for frontend-backend integration

→ [Implementation Progress](core/progress.md)

## Key Documentation
- [User Stories](core/userStories.md) - Core user requirements and needs
- [Acceptance Criteria](core/acceptanceCriteria.md) - Detailed validation criteria
- [Technology Stack](core/techContext.md) - Technologies and dependencies
- [System Patterns](core/systemPatterns.md) - Architecture and design patterns

## Active Plans

→ [All Plans](plans/)


## Knowledge Base
- [Lessons Learned](knowledge/lessons-learned.md) - Important lessons from development
- [Best Practices](knowledge/best-practices.md) - Coding and architecture best practices
- [Technical Decisions](knowledge/decisions.md) - Record of important technical decisions

## Directory Structure
``

## How to Use This Index
1. Begin every session by loading all three memory layers:
   - Working Memory: [Active Context](core/activeContext.md)
   - Short-Term Memory: Recent files in [task-logs/](task-logs/)
   - Long-Term Memory: Core files in [core/](core/)
2. Verify memory consistency using this index
3. Follow links to relevant documentation based on your current task
4. After completing work, update the appropriate memory layers to reflect changes
5. Ensure this index is updated to maintain an accurate overview

## Memory Update Process
After each task:
1. Create a detailed task log in the task-logs directory using the [template](templates/task-log-template.md)
2. Evaluate performance using the 23-point scoring system
3. Update the [Active Context](core/activeContext.md) with current state and next steps
4. Update relevant documentation files in the appropriate memory layer
5. Move completed tasks from active to completed
6. Add any new lessons learned or best practices to the knowledge base
7. Update this index to reflect the current state of the project

## Event Handling
The workflow architecture uses an event-driven model with specific handlers:
- **SessionStart**: Load memory layers, verify consistency, identify current context
- **TaskStart**: Document objectives, develop success criteria, create implementation plan
- **ErrorDetected**: Document error details, check for similar errors, apply recovery strategy
- **TaskComplete**: Document implementation details, evaluate performance, update memory layers
- **SessionEnd**: Synchronize memory layers, document session summary, update checksums


