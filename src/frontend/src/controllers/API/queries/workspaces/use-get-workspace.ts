import { WorkspaceType } from "@/types/workspace";
import { useQueryFunctionType } from "@/types/api";
import { api } from "../../api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";
import useAuthStore from "@/stores/authStore";
import { useRef } from "react";

/**
 * Interface for get workspace parameters
 */
interface IGetWorkspace {
  id: string;
}

/**
 * Hook to get a specific workspace
 */
export const useGetWorkspaceQuery: useQueryFunctionType<
  IGetWorkspace,
  WorkspaceType
> = (options) => {
  const { query } = UseRequestProcessor();
  const latestIdRef = useRef<string | null>(null);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  /**
   * Function to get a specific workspace
   */
  const getWorkspaceFn = async (
    params: IGetWorkspace
  ): Promise<WorkspaceType> => {
    if (!params.id) {
      throw new Error("Workspace ID is required");
    }

    latestIdRef.current = params.id;
    
    const url = `${getURL("WORKSPACES")}/${params.id}`;
    const { data } = await api.get<WorkspaceType>(url);
    
    return data;
  };

  return query(["useGetWorkspace", options?.id], () => getWorkspaceFn(options as IGetWorkspace), {
    enabled: isAuthenticated && !!options?.id,
    ...options,
  });
};
