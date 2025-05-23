#!/bin/bash
# Fix the commit message
echo "feat: Implement workspace management features including creation, updating, and deletion of workspaces and members

- Added hooks for fetching, adding, updating, and removing workspaces and workspace members.
- Created modals for managing workspace members and workspaces.
- Introduced a new workspace store for state management.
- Enhanced workspace-related types and utilities for better type safety and functionality.
- Integrated workspace management into the main application flow, including routing and UI components." > /tmp/commit-msg

# Continue the rebase using the fixed commit message
export GIT_EDITOR="cat /tmp/commit-msg >"
git rebase --continue

# Check the status after rebase
git status
