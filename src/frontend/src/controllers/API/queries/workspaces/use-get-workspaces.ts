import { WorkspaceType } from "@/types/workspace";
import { useQueryFunctionType } from "@/types/api";
import { api } from "../../api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";
import useWorkspaceStore from "@/stores/workspaceStore";
import useAuthStore from "@/stores/authStore";

/**
 * Hook to get all workspaces
 */
export const useGetWorkspacesQuery: useQueryFunctionType<
  undefined,
  WorkspaceType[]
> = (options) => {
  const { query } = UseRequestProcessor();

  const setWorkspaces = useWorkspaceStore((state) => state.setWorkspaces);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  /**
   * Function to get all workspaces
   */
  const getWorkspacesFn = async (): Promise<WorkspaceType[]> => {
    if (!isAuthenticated) return [];
    
    const res = await api.get(`${getURL("WORKSPACES")}/`);
    const data = res.data;
    
    setWorkspaces(data);
    
    return data;
  };

  return query(["useGetWorkspaces"], getWorkspacesFn, {
    enabled: isAuthenticated,
    ...options,
  });
};
