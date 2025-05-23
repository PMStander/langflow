import { UpdateWorkspaceMemberType, WorkspaceMemberType } from "@/types/workspace";
import { useMutationFunctionType } from "@/types/api";
import { api } from "../../api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";

/**
 * Interface for update workspace member parameters
 */
interface IUpdateWorkspaceMember {
  workspaceId: string;
  userId: string;
  data: UpdateWorkspaceMemberType;
}

/**
 * Hook to update a workspace member
 */
export const useUpdateWorkspaceMember: useMutationFunctionType<
  WorkspaceMemberType,
  IUpdateWorkspaceMember
> = (options?) => {
  const { mutate, queryClient } = UseRequestProcessor();

  /**
   * Function to update a workspace member
   */
  const updateWorkspaceMemberFn = async (
    params: IUpdateWorkspaceMember
  ): Promise<WorkspaceMemberType> => {
    const payload = {
      role: params.data.role,
    };

    const url = `${getURL("WORKSPACE_MEMBERS").replace("{workspace_id}", params.workspaceId)}/${params.userId}`;
    const res = await api.patch(url, payload);
    return res.data;
  };

  const mutation = mutate(["useUpdateWorkspaceMember"], updateWorkspaceMemberFn, {
    ...options,
    onSuccess: (data, variables, context) => {
      // Refetch workspace members after updating
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
