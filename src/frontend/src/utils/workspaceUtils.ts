import { WorkspaceMemberType, WorkspaceRole, WorkspaceType } from "@/types/workspace";

/**
 * Check if user is a member of the workspace
 * @param workspaceId Workspace ID
 * @param userId User ID
 * @param members Workspace members
 * @returns True if user is a member of the workspace
 */
export const isWorkspaceMember = (
  workspaceId: string,
  userId: string,
  members: WorkspaceMemberType[]
): boolean => {
  return members.some(
    (member) => member.workspace_id === workspaceId && member.user_id === userId
  );
};

/**
 * Get user's role in the workspace
 * @param workspaceId Workspace ID
 * @param userId User ID
 * @param members Workspace members
 * @param workspaces All workspaces
 * @returns User's role in the workspace or null if not a member
 */
export const getUserWorkspaceRole = (
  workspaceId: string,
  userId: string,
  members: WorkspaceMemberType[],
  workspaces: WorkspaceType[]
): WorkspaceRole | null => {
  // Check if user is the owner of the workspace
  const workspace = workspaces.find((w) => w.id === workspaceId);
  if (workspace && workspace.owner_id === userId) {
    return WorkspaceRole.OWNER;
  }

  // Check if user is a member of the workspace
  const member = members.find(
    (m) => m.workspace_id === workspaceId && m.user_id === userId
  );
  
  return member ? (member.role as WorkspaceRole) : null;
};

/**
 * Check if user has permission to perform an action in the workspace
 * @param workspaceId Workspace ID
 * @param userId User ID
 * @param members Workspace members
 * @param workspaces All workspaces
 * @param requiredRole Required role to perform the action
 * @returns True if user has permission to perform the action
 */
export const hasWorkspacePermission = (
  workspaceId: string,
  userId: string,
  members: WorkspaceMemberType[],
  workspaces: WorkspaceType[],
  requiredRole: WorkspaceRole
): boolean => {
  const role = getUserWorkspaceRole(workspaceId, userId, members, workspaces);
  
  if (!role) {
    return false;
  }
  
  // Owner has all permissions
  if (role === WorkspaceRole.OWNER) {
    return true;
  }
  
  // Editor can do everything except owner-specific actions
  if (role === WorkspaceRole.EDITOR && requiredRole !== WorkspaceRole.OWNER) {
    return true;
  }
  
  // Viewer can only view
  if (role === WorkspaceRole.VIEWER && requiredRole === WorkspaceRole.VIEWER) {
    return true;
  }
  
  return false;
};
