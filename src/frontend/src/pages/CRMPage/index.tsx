import { Outlet } from "react-router-dom";
import { useWorkspaceStore } from "@/stores/workspaceStore";
import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function CRMPage() {
  const navigate = useNavigate();
  const currentWorkspaceId = useWorkspaceStore((state) => state.currentWorkspaceId);

  // Redirect to workspace selection if no workspace is selected
  useEffect(() => {
    if (!currentWorkspaceId) {
      navigate("/workspaces");
    }
  }, [currentWorkspaceId, navigate]);

  if (!currentWorkspaceId) {
    return null;
  }

  return <Outlet />;
}
