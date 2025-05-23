import { CreateWorkspaceMemberType, WorkspaceMemberType } from "@/types/workspace";
import { useMutationFunctionType } from "@/types/api";
import { api } from "../../api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";

/**
 * Interface for add workspace member parameters
 */
interface IAddWorkspaceMember {
  workspaceId: string;
  data: CreateWorkspaceMemberType;
}

/**
 * Hook to add a workspace member
 */
export const useAddWorkspaceMember: useMutationFunctionType<
  WorkspaceMemberType,
  IAddWorkspaceMember
> = (options?) => {
  const { mutate, queryClient } = UseRequestProcessor();

  /**
   * Function to add a workspace member
   */
  const addWorkspaceMemberFn = async (
    params: IAddWorkspaceMember
  ): Promise<WorkspaceMemberType> => {
    const payload = {
      user_id: params.data.user_id,
      role: params.data.role,
    };

    const url = getURL("WORKSPACE_MEMBERS").replace("{workspace_id}", params.workspaceId);
    const res = await api.post(url, payload);
    return res.data;
  };

  const mutation = mutate(["useAddWorkspaceMember"], addWorkspaceMemberFn, {
    ...options,
    onSuccess: (data, variables, context) => {
      // Refetch workspace members after adding a new one
      queryClient.refetchQueries({ 
        queryKey: ["useGetWorkspaceMembers", variables.workspaceId] 
      });
      
      if (options?.onSuccess) {
        options.onSuccess(data, variables, context);
      }
    },
  });

  return mutation;
};
