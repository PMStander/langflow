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
We've implemented the AI Flow Builder Assistant feature, which helps users build flows through natural language instructions. We've completed Phase 1 (Foundation), Phase 2 (Core Functionality), and the core components of Phase 3 (Advanced Features), including both the backend flow construction engine and the frontend UI components. We're now focusing on enhancing the feature with better clarification, testing, and documentation.
→ [Active Context](core/activeContext.md)

## Implementation Plans
- [AI Flow Builder Assistant Plan](plans/ai-flow-builder-assistant-plan.md) - Comprehensive plan for implementing the AI assistant feature
- [Frontend Build Optimization Plan](plans/frontend-build-optimization-plan.md) - Plan for addressing frontend build process issues
- [Networking Issue Resolution Plan](plans/networking-issue-resolution-plan.md) - Plan for resolving frontend-backend connection issues

## Task Logs
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
- **Overall Progress**: Core features implemented, AI Flow Builder Assistant core functionality completed
- **Current Phase**: AI Assistant Implementation - Phase 3 (Advanced Features)
- **Recent Achievements**: Completed flow construction engine and frontend UI components for the AI Assistant
- **Current Issues**: Investigating networking issues between frontend and backend components

→ [Implementation Progress](core/progress.md)
→ [Networking Issue](errors/error_2023-05-21_networking.md)

## Key Documentation
- [User Stories](core/userStories.md) - Core user requirements and needs
- [Acceptance Criteria](core/acceptanceCriteria.md) - Detailed validation criteria
- [Technology Stack](core/techContext.md) - Technologies and dependencies
- [System Patterns](core/systemPatterns.md) - Architecture and design patterns

## Memory Checksums
- activeContext.md: 2023-05-21-07-45
- progress.md: 2023-05-23-12-30
- memory-index.md: 2023-05-21-07-45

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


