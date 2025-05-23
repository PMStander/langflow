import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useGetWorkspacesQuery } from "@/controllers/API/queries/workspaces";
import useAuthStore from "@/stores/authStore";
import useWorkspaceStore from "@/stores/workspaceStore";
import { WorkspaceRole } from "@/types/workspace";
import { getUserWorkspaceRole } from "@/utils/workspaceUtils";
import { ChevronDown, Plus, Settings } from "lucide-react";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

/**
 * WorkspaceSelector component props
 */
interface WorkspaceSelectorProps {
  onCreateWorkspace?: () => void;
  onManageWorkspaces?: () => void;
}

/**
 * WorkspaceSelector component
 * Displays a dropdown to select the current workspace
 */
export const WorkspaceSelector = ({
  onCreateWorkspace,
  onManageWorkspaces,
}: WorkspaceSelectorProps) => {
  const navigate = useNavigate();
  const userData = useAuthStore((state) => state.userData);

  const workspaces = useWorkspaceStore((state) => state.workspaces);
  const currentWorkspaceId = useWorkspaceStore((state) => state.currentWorkspaceId);
  const setCurrentWorkspaceId = useWorkspaceStore((state) => state.setCurrentWorkspaceId);
  const workspaceMembers = useWorkspaceStore((state) => state.workspaceMembers);

  const { data: fetchedWorkspaces, isLoading } = useGetWorkspacesQuery();

  // Set the first workspace as current if none is selected
  useEffect(() => {
    if (workspaces?.length > 0 && !currentWorkspaceId) {
      setCurrentWorkspaceId(workspaces[0].id);
    }
  }, [workspaces, currentWorkspaceId, setCurrentWorkspaceId]);

  // Refetch workspaces when the component mounts
  useEffect(() => {
    if (fetchedWorkspaces) {
      // This will update the workspaces in the store
      // and trigger a re-render of components that depend on it
    }
  }, [fetchedWorkspaces]);

  // Get the current workspace
  const currentWorkspace = workspaces?.find((w) => w.id === currentWorkspaceId);

  // Handle workspace selection
  const handleSelectWorkspace = (workspaceId: string) => {
    setCurrentWorkspaceId(workspaceId);
    // Navigate to home to refresh the folders list with the new workspace
    navigate("/");
  };

  // Handle create workspace
  const handleCreateWorkspace = () => {
    if (onCreateWorkspace) {
      onCreateWorkspace();
    }
  };

  // Handle manage workspaces
  const handleManageWorkspaces = () => {
    if (onManageWorkspaces) {
      onManageWorkspaces();
    }
  };

  if (isLoading || !workspaces || workspaces.length === 0) {
    return null;
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          className="flex items-center gap-2 px-2 py-1"
          data-testid="workspace-selector"
        >
          <span className="max-w-[150px] truncate font-medium">
            {currentWorkspace?.name || "Select Workspace"}
          </span>
          <ChevronDown className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-56">
        {workspaces.map((workspace) => {
          const role = userData?.id
            ? getUserWorkspaceRole(
                workspace.id,
                userData.id,
                workspaceMembers,
                workspaces
              )
            : null;

          return (
            <DropdownMenuItem
              key={workspace.id}
              className="flex items-center justify-between"
              onSelect={() => handleSelectWorkspace(workspace.id)}
              data-testid={`workspace-item-${workspace.id}`}
            >
              <span className="max-w-[180px] truncate">{workspace.name}</span>
              {role && (
                <span className="text-xs text-muted-foreground">
                  {role}
                </span>
              )}
            </DropdownMenuItem>
          );
        })}

        <DropdownMenuSeparator />

        <DropdownMenuItem
          className="flex items-center gap-2"
          onSelect={handleCreateWorkspace}
          data-testid="create-workspace"
        >
          <Plus className="h-4 w-4" />
          <span>Create Workspace</span>
        </DropdownMenuItem>

        <DropdownMenuItem
          className="flex items-center gap-2"
          onSelect={handleManageWorkspaces}
          data-testid="manage-workspaces"
        >
          <Settings className="h-4 w-4" />
          <span>Manage Workspaces</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};

export default WorkspaceSelector;
