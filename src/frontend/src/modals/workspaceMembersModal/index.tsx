import ForwardedIconComponent from "@/components/common/genericIconComponent";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useGetUsers } from "@/controllers/API/queries/auth";
import {
  useAddWorkspaceMember,
  useGetWorkspaceMembersQuery,
  useRemoveWorkspaceMember,
  useUpdateWorkspaceMember,
} from "@/controllers/API/queries/workspaces";
import useAlertStore from "@/stores/alertStore";
import useAuthStore from "@/stores/authStore";
import { CreateWorkspaceMemberType, WorkspaceRole, WorkspaceType } from "@/types/workspace";
import { ChevronDown, MoreHorizontal, Plus, Trash, UserPlus } from "lucide-react";
import { useState } from "react";

/**
 * WorkspaceMembersModal props
 */
interface WorkspaceMembersModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  workspace: WorkspaceType;
}

/**
 * WorkspaceMembersModal component
 * Modal for managing workspace members
 */
export const WorkspaceMembersModal = ({
  open,
  onOpenChange,
  workspace,
}: WorkspaceMembersModalProps) => {
  const [selectedUserId, setSelectedUserId] = useState<string>("");
  const [selectedRole, setSelectedRole] = useState<WorkspaceRole>(WorkspaceRole.VIEWER);
  const [searchQuery, setSearchQuery] = useState<string>("");
  
  const userData = useAuthStore((state) => state.userData);
  const setErrorData = useAlertStore((state) => state.setErrorData);
  const setSuccessData = useAlertStore((state) => state.setSuccessData);
  
  const { data: members = [], isLoading: isLoadingMembers } = useGetWorkspaceMembersQuery({
    workspaceId: workspace.id,
  });
  
  const { data: users = [], isLoading: isLoadingUsers } = useGetUsers();
  
  const { mutate: addMember, isPending: isAddingMember } = useAddWorkspaceMember({
    onSuccess: () => {
      setSuccessData({
        title: "Success",
        list: ["Member added successfully"],
      });
      setSelectedUserId("");
      setSelectedRole(WorkspaceRole.VIEWER);
    },
    onError: (error) => {
      setErrorData({
        title: "Error adding member",
        list: [error.message],
      });
    },
  });
  
  const { mutate: updateMember } = useUpdateWorkspaceMember({
    onSuccess: () => {
      setSuccessData({
        title: "Success",
        list: ["Member role updated successfully"],
      });
    },
    onError: (error) => {
      setErrorData({
        title: "Error updating member role",
        list: [error.message],
      });
    },
  });
  
  const { mutate: removeMember } = useRemoveWorkspaceMember({
    onSuccess: () => {
      setSuccessData({
        title: "Success",
        list: ["Member removed successfully"],
      });
    },
    onError: (error) => {
      setErrorData({
        title: "Error removing member",
        list: [error.message],
      });
    },
  });
  
  // Filter users that are not already members
  const filteredUsers = users.filter(
    (user) =>
      !members.some((member) => member.user_id === user.id) &&
      user.id !== workspace.owner_id &&
      (searchQuery
        ? user.username.toLowerCase().includes(searchQuery.toLowerCase())
        : true)
  );
  
  // Handle adding a member
  const handleAddMember = () => {
    if (!selectedUserId) {
      setErrorData({
        title: "Error",
        list: ["Please select a user"],
      });
      return;
    }
    
    const data: CreateWorkspaceMemberType = {
      user_id: selectedUserId,
      role: selectedRole,
    };
    
    addMember({
      workspaceId: workspace.id,
      data,
    });
  };
  
  // Handle updating a member's role
  const handleUpdateMemberRole = (userId: string, role: WorkspaceRole) => {
    updateMember({
      workspaceId: workspace.id,
      userId,
      data: { role },
    });
  };
  
  // Handle removing a member
  const handleRemoveMember = (userId: string) => {
    removeMember({
      workspaceId: workspace.id,
      userId,
    });
  };
  
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Manage Workspace Members</DialogTitle>
          <DialogDescription>
            Add, update, or remove members from the workspace
          </DialogDescription>
        </DialogHeader>
        
        <div className="mt-4 space-y-4">
          <div className="flex items-end gap-2">
            <div className="flex-1">
              <Select
                value={selectedUserId}
                onValueChange={setSelectedUserId}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a user" />
                </SelectTrigger>
                <SelectContent>
                  {filteredUsers.map((user) => (
                    <SelectItem key={user.id} value={user.id}>
                      {user.username}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="w-32">
              <Select
                value={selectedRole}
                onValueChange={(value) => setSelectedRole(value as WorkspaceRole)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Role" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={WorkspaceRole.EDITOR}>Editor</SelectItem>
                  <SelectItem value={WorkspaceRole.VIEWER}>Viewer</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <Button
              onClick={handleAddMember}
              disabled={isAddingMember || !selectedUserId}
              className="flex items-center gap-1"
            >
              <UserPlus className="h-4 w-4" />
              <span>Add</span>
            </Button>
          </div>
          
          <div className="rounded-md border">
            <div className="p-4">
              <Input
                placeholder="Search members..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full"
              />
            </div>
            
            <div className="max-h-[300px] overflow-y-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="p-2 text-left font-medium">User</th>
                    <th className="p-2 text-left font-medium">Role</th>
                    <th className="p-2 text-right font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {/* Owner row */}
                  <tr className="border-b">
                    <td className="p-2">
                      {users.find((user) => user.id === workspace.owner_id)?.username || "Owner"}
                      {userData?.id === workspace.owner_id && " (You)"}
                    </td>
                    <td className="p-2">
                      <span className="rounded bg-primary/10 px-2 py-1 text-xs font-medium text-primary">
                        Owner
                      </span>
                    </td>
                    <td className="p-2 text-right">-</td>
                  </tr>
                  
                  {/* Members rows */}
                  {members
                    .filter((member) =>
                      member.user?.username
                        ? member.user.username
                            .toLowerCase()
                            .includes(searchQuery.toLowerCase())
                        : true
                    )
                    .map((member) => (
                      <tr key={member.user_id} className="border-b">
                        <td className="p-2">
                          {member.user?.username || member.user_id}
                          {userData?.id === member.user_id && " (You)"}
                        </td>
                        <td className="p-2">
                          <span className="rounded bg-muted px-2 py-1 text-xs font-medium">
                            {member.role}
                          </span>
                        </td>
                        <td className="p-2 text-right">
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="sm">
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem
                                onClick={() =>
                                  handleUpdateMemberRole(
                                    member.user_id,
                                    member.role === WorkspaceRole.EDITOR
                                      ? WorkspaceRole.VIEWER
                                      : WorkspaceRole.EDITOR
                                  )
                                }
                              >
                                <ForwardedIconComponent
                                  name="pencil"
                                  className="mr-2 h-4 w-4"
                                />
                                <span>
                                  Change to{" "}
                                  {member.role === WorkspaceRole.EDITOR
                                    ? "Viewer"
                                    : "Editor"}
                                </span>
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                onClick={() => handleRemoveMember(member.user_id)}
                                className="text-destructive"
                              >
                                <Trash className="mr-2 h-4 w-4" />
                                <span>Remove</span>
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default WorkspaceMembersModal;
