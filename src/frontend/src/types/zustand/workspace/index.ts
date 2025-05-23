import { WorkspaceMemberType, WorkspaceType } from "../../workspace";

/**
 * Workspace store type
 */
export type WorkspaceStoreType = {
  // Current workspace
  currentWorkspaceId: string | null;
  setCurrentWorkspaceId: (id: string | null) => void;
  
  // All workspaces
  workspaces: WorkspaceType[];
  setWorkspaces: (workspaces: WorkspaceType[]) => void;
  
  // Workspace members
  workspaceMembers: WorkspaceMemberType[];
  setWorkspaceMembers: (members: WorkspaceMemberType[]) => void;
  
  // Workspace to edit
  workspaceToEdit: WorkspaceType | null;
  setWorkspaceToEdit: (workspace: WorkspaceType | null) => void;
  
  // Reset store
  resetStore: () => void;
};
