import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useCreateWorkspace, useUpdateWorkspace } from "@/controllers/API/queries/workspaces";
import useAlertStore from "@/stores/alertStore";
import useWorkspaceStore from "@/stores/workspaceStore";
import { CreateWorkspaceType, UpdateWorkspaceType, WorkspaceType } from "@/types/workspace";
import { useState, useEffect } from "react";

/**
 * WorkspaceModal props
 */
interface WorkspaceModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  workspace?: WorkspaceType | null;
}

/**
 * WorkspaceModal component
 * Modal for creating and editing workspaces
 */
export const WorkspaceModal = ({
  open,
  onOpenChange,
  workspace,
}: WorkspaceModalProps) => {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");

  const setErrorData = useAlertStore((state) => state.setErrorData);
  const setSuccessData = useAlertStore((state) => state.setSuccessData);

  const setWorkspaceToEdit = useWorkspaceStore((state) => state.setWorkspaceToEdit);

  const { mutate: createWorkspace, isPending: isCreating } = useCreateWorkspace({
    onSuccess: () => {
      setSuccessData({
        title: "Success",
        list: ["Workspace created successfully"],
      });
      handleClose();
    },
    onError: (error) => {
      setErrorData({
        title: "Error creating workspace",
        list: [error.message],
      });
    },
  });

  const { mutate: updateWorkspace, isPending: isUpdating } = useUpdateWorkspace({
    onSuccess: () => {
      setSuccessData({
        title: "Success",
        list: ["Workspace updated successfully"],
      });
      handleClose();
    },
    onError: (error) => {
      setErrorData({
        title: "Error updating workspace",
        list: [error.message],
      });
    },
  });

  // Set form values when workspace changes
  useEffect(() => {
    if (workspace) {
      setName(workspace.name);
      setDescription(workspace.description || "");
    } else {
      setName("");
      setDescription("");
    }
  }, [workspace]);

  // Handle form submission
  const handleSubmit = () => {
    if (!name.trim()) {
      setErrorData({
        title: "Error",
        list: ["Workspace name is required"],
      });
      return;
    }

    if (workspace) {
      // Update existing workspace
      const data: UpdateWorkspaceType = {
        name: name.trim(),
        description: description.trim() || undefined,
      };

      updateWorkspace({
        id: workspace.id,
        data,
      });
    } else {
      // Create new workspace
      const data: CreateWorkspaceType = {
        name: name.trim(),
        description: description.trim() || undefined,
      };

      createWorkspace({
        data,
      });
    }
  };

  // Handle modal close
  const handleClose = () => {
    setName("");
    setDescription("");
    setWorkspaceToEdit(null);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>
            {workspace ? "Edit Workspace" : "Create Workspace"}
          </DialogTitle>
          <DialogDescription>
            {workspace
              ? "Update your workspace details"
              : "Create a new workspace to organize your projects and flows"}
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="name" className="text-right">
              Name
            </Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="col-span-3"
              placeholder="My Workspace"
              data-testid="workspace-name-input"
            />
          </div>

          <div className="grid grid-cols-4 items-start gap-4">
            <Label htmlFor="description" className="text-right pt-2">
              Description
            </Label>
            <Textarea
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="col-span-3 min-h-[100px] w-full"
              placeholder="Workspace description (optional)"
              data-testid="workspace-description-input"
            />
          </div>
        </div>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={handleClose}
            disabled={isCreating || isUpdating}
          >
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={isCreating || isUpdating}
            data-testid="workspace-submit-button"
          >
            {isCreating || isUpdating
              ? "Saving..."
              : workspace
              ? "Update"
              : "Create"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default WorkspaceModal;
