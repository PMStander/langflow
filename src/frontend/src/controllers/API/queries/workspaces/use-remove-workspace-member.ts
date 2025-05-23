import { useMutationFunctionType } from "@/types/api";
import { api } from "../../api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";

/**
 * Interface for remove workspace member parameters
 */
interface IRemoveWorkspaceMember {
  workspaceId: string;
  userId: string;
}

/**
 * Hook to remove a workspace member
 */
export const useRemoveWorkspaceMember: useMutationFunctionType<
  void,
  IRemoveWorkspaceMember
> = (options?) => {
  const { mutate, queryClient } = UseRequestProcessor();

  /**
   * Function to remove a workspace member
   */
  const removeWorkspaceMemberFn = async (
    params: IRemoveWorkspaceMember
  ): Promise<void> => {
    const url = `${getURL("WORKSPACE_MEMBERS").replace("{workspace_id}", params.workspaceId)}/${params.userId}`;
    await api.delete(url);
  };

  const mutation = mutate(["useRemoveWorkspaceMember"], removeWorkspaceMemberFn, {
    ...options,
    onSuccess: (data, variables, context) => {
      // Refetch workspace members after removing
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
