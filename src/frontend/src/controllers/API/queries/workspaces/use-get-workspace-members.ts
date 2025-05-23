import { WorkspaceMemberType } from "@/types/workspace";
import { useQueryFunctionType } from "@/types/api";
import { api } from "../../api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";
import useAuthStore from "@/stores/authStore";
import useWorkspaceStore from "@/stores/workspaceStore";

/**
 * Interface for get workspace members parameters
 */
interface IGetWorkspaceMembers {
  workspaceId: string;
}

/**
 * Hook to get workspace members
 */
export const useGetWorkspaceMembersQuery: useQueryFunctionType<
  IGetWorkspaceMembers,
  WorkspaceMemberType[]
> = (options) => {
  const { query } = UseRequestProcessor();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const setWorkspaceMembers = useWorkspaceStore((state) => state.setWorkspaceMembers);

  /**
   * Function to get workspace members
   */
  const getWorkspaceMembersFn = async (
    params: IGetWorkspaceMembers
  ): Promise<WorkspaceMemberType[]> => {
    if (!params.workspaceId) {
      throw new Error("Workspace ID is required");
    }
    
    const url = getURL("WORKSPACE_MEMBERS").replace("{workspace_id}", params.workspaceId);
    const { data } = await api.get<WorkspaceMemberType[]>(url);
    
    setWorkspaceMembers(data);
    
    return data;
  };

  return query(
    ["useGetWorkspaceMembers", options?.workspaceId], 
    () => getWorkspaceMembersFn(options as IGetWorkspaceMembers), 
    {
      enabled: isAuthenticated && !!options?.workspaceId,
      ...options,
    }
  );
};
