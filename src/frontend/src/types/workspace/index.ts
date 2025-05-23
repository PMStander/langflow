/**
 * Types for workspace feature
 */

/**
 * Workspace role enum
 */
export enum WorkspaceRole {
  OWNER = "owner",
  EDITOR = "editor",
  VIEWER = "viewer",
}

/**
 * Workspace type
 */
export type WorkspaceType = {
  id: string;
  name: string;
  description: string | null;
  owner_id: string;
  created_at: string;
  updated_at: string;
};

/**
 * Workspace member type
 */
export type WorkspaceMemberType = {
  workspace_id: string;
  user_id: string;
  role: WorkspaceRole;
  created_at: string;
  user?: {
    id: string;
    username: string;
    profile_image: string;
  };
};

/**
 * Create workspace type
 */
export type CreateWorkspaceType = {
  name: string;
  description?: string;
};

/**
 * Update workspace type
 */
export type UpdateWorkspaceType = {
  name?: string;
  description?: string;
};

/**
 * Create workspace member type
 */
export type CreateWorkspaceMemberType = {
  user_id: string;
  role: WorkspaceRole;
};

/**
 * Update workspace member type
 */
export type UpdateWorkspaceMemberType = {
  role: WorkspaceRole;
};
