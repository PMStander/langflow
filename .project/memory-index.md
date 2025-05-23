# Project Memory Index

## Project Overview
Langflow is an open-source UI visual tool designed to facilitate the creation, experimentation, and deployment of LangChain applications through a drag-and-drop interface.
→ [Project Brief](core/projectbrief.md)

## Product Context
Langflow aims to democratize access to Large Language Model (LLM) application development by providing a visual, intuitive interface for building complex LangChain workflows.
→ [Product Context](core/productContext.md)
→ [Basic Component](rules/components/basic_component.mdc) - Rules and checklist for creating a basic Langflow Component
→ [Icons](rules/icons.mdc) - Rules and checklist for adding and using langflow component icons.


## System Architecture
Langflow follows a client-server architecture with a React frontend and FastAPI backend, designed for extensibility and ease of use.
→ [System Patterns](core/systemPatterns.md)
→ [Active Context](core/activeContext.md)
→ [Workflow Architecture](core/workflow-architecture.md)
→ [Event Handlers](core/event-handlers.md)
→ [Self-Healing System](core/self-healing.md)

## Current Focus
We've completed Phases 1-4 of the Workspace Dashboard & CRM feature for Langflow, including the foundation, dashboard implementation, CRM core features, and advanced features. We've implemented all CRM entity database models, API endpoints, TypeScript interfaces, API hooks, and created all CRM pages with advanced data visualization. We're now focusing on Phase 5 (Integration and Polish), which includes comprehensive testing, documentation, database query optimization, UI/UX refinement, and final polish.
→ [Active Context](core/activeContext.md)

## Implementation Plans
- [AI Flow Builder Assistant Plan](plans/ai-flow-builder-assistant-plan.md) - Comprehensive plan for implementing the AI assistant feature
- [Frontend Build Optimization Plan](plans/frontend-build-optimization-plan.md) - Plan for addressing frontend build process issues
- [Networking Issue Resolution Plan](plans/networking-issue-resolution-plan.md) - Plan for resolving frontend-backend connection issues
- [Workspace Dashboard & CRM Plan](plans/workspace-dashboard-crm-plan.md) - Comprehensive plan for implementing a CRM system integrated with workspaces
- [Workspace Dashboard UI Mockups](plans/workspace-dashboard-ui-mockups.md) - UI mockups for the dashboard and CRM interfaces
- [Workspace Dashboard Backend Implementation](plans/workspace-dashboard-backend-implementation.md) - Detailed backend implementation plan for CRM features
- [Workspace Dashboard Frontend Implementation](plans/workspace-dashboard-frontend-implementation.md) - Frontend component structure for dashboard and CRM
- [Workspace Dashboard Implementation Timeline](plans/workspace-dashboard-implementation-timeline.md) - Implementation timeline with task dependencies

## Task Logs
- [Session End](task-logs/task-log_2025-05-27_session-end.md) - Session closure and memory bank synchronization
- [CRM Database Optimization](task-logs/task-log_2025-05-27_crm-database-optimization.md) - Optimization of database queries and UUID handling for CRM module
- [Session Start - Phase 5 Preparation](task-logs/task-log_2025-05-27_session-start.md) - Memory system initialization for Phase 5 implementation
- [CRM Phase 4 Implementation](task-logs/task-log_2025-05-26_crm-phase4-implementation.md) - Implementation of advanced features for CRM module
- [CRM Phase 3 Implementation](task-logs/task-log_2025-05-25_crm-phase3-implementation.md) - Implementation of core CRM features
- [Browser Console Fixes](task-logs/task-log_2025-05-25_browser-console-fixes.md) - Fixes for browser console errors
- [SQLAlchemy Foreign Key Fix](task-logs/task-log_2025-05-23_sqlalchemy-foreign-key-fix.md) - Fix for SQLAlchemy foreign key relationship errors in CRM models
- [CRM Frontend Implementation](task-logs/task-log_2025-05-24_crm-frontend-implementation.md) - Implementation of frontend components for CRM module
- [CRM API Endpoints Implementation](task-logs/task-log_2025-05-24_crm-api-endpoints-implementation.md) - Implementation of API endpoints for CRM entities
- [CRM Database Models Implementation](task-logs/task-log_2025-05-24_crm-database-models-implementation.md) - Implementation of CRM entity database models
- [Session Start - CRM Implementation](task-logs/task-log_2025-05-24_session-start.md) - Memory system initialization for CRM implementation
- [Workspace Dashboard & CRM Planning](task-logs/task-log_2025-05-23_workspace-dashboard-crm-planning.md) - Creation of comprehensive implementation plan for CRM features
- [Workspace Implementation](task-logs/task-log_2024-06-01_workspace-implementation.md) - Implementation of workspace feature
- [Session Start](task-logs/task-log_2023-05-21_session-start.md) - Memory system initialization for new session with networking issue identification
- [Session Start](task-logs/task-log_2023-05-24_session-start.md) - Memory system initialization for new session
- [AI Assistant Implementation - Phase 3 (Frontend)](task-logs/task-log_2023-05-23_ai-assistant-implementation-phase3-frontend.md) - Implementation of frontend UI components
- [AI Assistant Implementation - Phase 3 (Backend)](task-logs/task-log_2023-05-23_ai-assistant-implementation-phase3.md) - Implementation of flow construction engine
- [Session Start](task-logs/task-log_2023-05-23_session-start.md) - Memory system initialization for new session
- [AI Assistant Implementation - Phase 2](task-logs/task-log_2023-05-22_ai-assistant-implementation-phase2.md) - Implementation of instruction parsing system
- [AI Assistant Implementation - Phase 1](task-logs/task-log_2023-05-21_ai-assistant-implementation-phase1.md) - Implementation of Component Knowledge Base
- [AI Assistant Plan](task-logs/task-log_2023-05-20_ai-assistant-plan.md) - Creation of implementation plan
- [Memory Initialization](task-logs/task-log_2023-05-20_memory-initialization.md) - Initialization of memory system

## Project Status
- **Overall Progress**: Core features implemented, Workspace feature completed, CRM Phases 1-4 completed
- **Current Phase**: Workspace Dashboard & CRM Implementation - Phase 5 (Integration and Polish)
- **Recent Achievements**: Completed all CRM core and advanced features, including reporting, analytics, data export, and advanced visualization
- **Next Steps**: Comprehensive testing, documentation, database optimization, UI/UX refinement, and final polish

→ [Implementation Progress](core/progress.md)
→ [Networking Issue](errors/error_2023-05-21_networking.md)

## Key Documentation
- [User Stories](core/userStories.md) - Core user requirements and needs
- [Acceptance Criteria](core/acceptanceCriteria.md) - Detailed validation criteria
- [Technology Stack](core/techContext.md) - Technologies and dependencies
- [System Patterns](core/systemPatterns.md) - Architecture and design patterns

## Memory Checksums
- activeContext.md: 2025-05-27-13-15
- progress.md: 2025-05-24-16-00
- memory-index.md: 2025-05-27-13-15
- sqlalchemy-best-practices.md: 2025-05-23-11-45
- task-log_2025-05-27_session-start.md: 2025-05-27-09-15
- task-log_2025-05-27_crm-database-optimization.md: 2025-05-27-13-00
- task-log_2025-05-27_session-end.md: 2025-05-27-13-15

## Active Plans

→ [All Plans](plans/)


## Knowledge Base
- [Lessons Learned](knowledge/lessons-learned.md) - Important lessons from development
- [Best Practices](knowledge/best-practices.md) - Coding and architecture best practices
- [SQLAlchemy Best Practices](knowledge/sqlalchemy-best-practices.md) - Best practices for SQLAlchemy/SQLModel database operations
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


