import ForwardedIconComponent from "@/components/common/genericIconComponent";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useDeleteWorkspace, useGetWorkspacesQuery } from "@/controllers/API/queries/workspaces";
import DeleteConfirmationModal from "@/modals/deleteConfirmationModal";
import WorkspaceMembersModal from "@/modals/workspaceMembersModal";
import WorkspaceModal from "@/modals/workspaceModal";
import useAlertStore from "@/stores/alertStore";
import useAuthStore from "@/stores/authStore";
import useWorkspaceStore from "@/stores/workspaceStore";
import { WorkspaceType } from "@/types/workspace";
import { formatDate } from "@/utils/utils";
import { MoreHorizontal, Plus, Settings, Trash, Users } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

/**
 * WorkspacePage component
 * Page for managing workspaces
 */
export const WorkspacePage = () => {
  const navigate = useNavigate();
  const userData = useAuthStore((state) => state.userData);
  const setErrorData = useAlertStore((state) => state.setErrorData);
  const setSuccessData = useAlertStore((state) => state.setSuccessData);
  
  const [openCreateModal, setOpenCreateModal] = useState(false);
  const [openEditModal, setOpenEditModal] = useState(false);
  const [openMembersModal, setOpenMembersModal] = useState(false);
  const [openDeleteModal, setOpenDeleteModal] = useState(false);
  const [selectedWorkspace, setSelectedWorkspace] = useState<WorkspaceType | null>(null);
  
  const setWorkspaceToEdit = useWorkspaceStore((state) => state.setWorkspaceToEdit);
  const workspaceToEdit = useWorkspaceStore((state) => state.workspaceToEdit);
  const setCurrentWorkspaceId = useWorkspaceStore((state) => state.setCurrentWorkspaceId);
  
  const { data: workspaces = [], isLoading } = useGetWorkspacesQuery();
  
  const { mutate: deleteWorkspace, isPending: isDeleting } = useDeleteWorkspace({
    onSuccess: () => {
      setSuccessData({
        title: "Success",
        list: ["Workspace deleted successfully"],
      });
      setOpenDeleteModal(false);
    },
    onError: (error) => {
      setErrorData({
        title: "Error deleting workspace",
        list: [error.message],
      });
    },
  });
  
  // Handle creating a workspace
  const handleCreateWorkspace = () => {
    setWorkspaceToEdit(null);
    setOpenCreateModal(true);
  };
  
  // Handle editing a workspace
  const handleEditWorkspace = (workspace: WorkspaceType) => {
    setWorkspaceToEdit(workspace);
    setOpenEditModal(true);
  };
  
  // Handle managing workspace members
  const handleManageMembers = (workspace: WorkspaceType) => {
    setSelectedWorkspace(workspace);
    setOpenMembersModal(true);
  };
  
  // Handle deleting a workspace
  const handleDeleteWorkspace = (workspace: WorkspaceType) => {
    setSelectedWorkspace(workspace);
    setOpenDeleteModal(true);
  };
  
  // Handle confirming workspace deletion
  const handleConfirmDelete = () => {
    if (selectedWorkspace) {
      deleteWorkspace({ id: selectedWorkspace.id });
    }
  };
  
  // Handle selecting a workspace
  const handleSelectWorkspace = (workspace: WorkspaceType) => {
    setCurrentWorkspaceId(workspace.id);
    navigate("/");
  };
  
  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <ForwardedIconComponent
            name="loader-2"
            className="mx-auto h-8 w-8 animate-spin text-primary"
          />
          <p className="mt-2 text-sm text-muted-foreground">Loading workspaces...</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto py-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Workspaces</h1>
          <p className="text-muted-foreground">
            Manage your workspaces and their members
          </p>
        </div>
        <Button onClick={handleCreateWorkspace} className="flex items-center gap-2">
          <Plus className="h-4 w-4" />
          <span>Create Workspace</span>
        </Button>
      </div>
      
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {workspaces.map((workspace) => (
          <Card key={workspace.id} className="overflow-hidden">
            <CardHeader className="pb-2">
              <div className="flex items-start justify-between">
                <CardTitle className="truncate">{workspace.name}</CardTitle>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem
                      onClick={() => handleSelectWorkspace(workspace)}
                    >
                      <ForwardedIconComponent
                        name="check"
                        className="mr-2 h-4 w-4"
                      />
                      <span>Select</span>
                    </DropdownMenuItem>
                    
                    {workspace.owner_id === userData?.id && (
                      <>
                        <DropdownMenuItem
                          onClick={() => handleEditWorkspace(workspace)}
                        >
                          <Settings className="mr-2 h-4 w-4" />
                          <span>Edit</span>
                        </DropdownMenuItem>
                        
                        <DropdownMenuItem
                          onClick={() => handleManageMembers(workspace)}
                        >
                          <Users className="mr-2 h-4 w-4" />
                          <span>Members</span>
                        </DropdownMenuItem>
                        
                        <DropdownMenuItem
                          onClick={() => handleDeleteWorkspace(workspace)}
                          className="text-destructive"
                        >
                          <Trash className="mr-2 h-4 w-4" />
                          <span>Delete</span>
                        </DropdownMenuItem>
                      </>
                    )}
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
              <CardDescription className="line-clamp-2">
                {workspace.description || "No description"}
              </CardDescription>
            </CardHeader>
            <CardContent className="pb-2">
              <div className="flex items-center text-sm text-muted-foreground">
                <ForwardedIconComponent
                  name="user"
                  className="mr-1 h-4 w-4"
                />
                <span>
                  {workspace.owner_id === userData?.id
                    ? "You are the owner"
                    : "You are a member"}
                </span>
              </div>
            </CardContent>
            <CardFooter className="border-t pt-2 text-xs text-muted-foreground">
              Created {formatDate(new Date(workspace.created_at))}
            </CardFooter>
          </Card>
        ))}
      </div>
      
      {/* Create Workspace Modal */}
      <WorkspaceModal
        open={openCreateModal}
        onOpenChange={setOpenCreateModal}
      />
      
      {/* Edit Workspace Modal */}
      <WorkspaceModal
        open={openEditModal}
        onOpenChange={setOpenEditModal}
        workspace={workspaceToEdit}
      />
      
      {/* Workspace Members Modal */}
      {selectedWorkspace && (
        <WorkspaceMembersModal
          open={openMembersModal}
          onOpenChange={setOpenMembersModal}
          workspace={selectedWorkspace}
        />
      )}
      
      {/* Delete Confirmation Modal */}
      <DeleteConfirmationModal
        open={openDeleteModal}
        setOpen={setOpenDeleteModal}
        title="Delete Workspace"
        description="Are you sure you want to delete this workspace? This action cannot be undone and will remove all projects and flows in this workspace."
        onConfirm={handleConfirmDelete}
        isDeleting={isDeleting}
      />
    </div>
  );
};

export default WorkspacePage;
