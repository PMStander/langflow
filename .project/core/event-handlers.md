# Event Handlers

This document describes the event handlers used in the project management system. These handlers are triggered by specific events and perform actions to maintain the system's state.

## SessionStart Handler

Triggered when a new session begins.

### Actions
1. Check if `.project/` directory structure exists
2. If structure doesn't exist, scaffold it by creating all required directories
3. If memory files don't exist, initialize them with available project information
4. Load all memory layers from `.project/core/`
5. Verify memory consistency using checksums in memory-index.md
6. Identify current task context from activeContext.md
7. Create a memory of this initialization process using the TASK LOG

## TaskStart Handler

Triggered when a new task begins.

### Actions
1. Document task objectives in new task log
2. Develop criteria for successful task completion
3. Load relevant context from memory
4. Create implementation plan

## ErrorDetected Handler

Triggered when an error is detected.

### Actions
1. Document error details in `.project/errors/`
2. Check memory for similar errors
3. Apply recovery strategy
4. Update error patterns

## TaskComplete Handler

Triggered when a task is completed.

### Actions
1. Document implementation details in task log
2. Evaluate performance
3. Update all memory layers
4. Update activeContext.md with next steps

## SessionEnd Handler

Triggered when a session ends.

### Actions
1. Ensure all memory layers are synchronized
2. Document session summary in activeContext.md
3. Update checksums in memory-index.md
