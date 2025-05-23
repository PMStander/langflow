import { UpdateWorkspaceType, WorkspaceType } from "@/types/workspace";
import { useMutationFunctionType } from "@/types/api";
import { api } from "../../api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";

/**
 * Interface for update workspace parameters
 */
interface IUpdateWorkspace {
  id: string;
  data: UpdateWorkspaceType;
}

/**
 * Hook to update a workspace
 */
export const useUpdateWorkspace: useMutationFunctionType<
  WorkspaceType,
  IUpdateWorkspace
> = (options?) => {
  const { mutate, queryClient } = UseRequestProcessor();

  /**
   * Function to update a workspace
   */
  const updateWorkspaceFn = async (
    params: IUpdateWorkspace
  ): Promise<WorkspaceType> => {
    const payload = {
      name: params.data.name,
      description: params.data.description,
    };

    const res = await api.patch(`${getURL("WORKSPACES")}/${params.id}`, payload);
    return res.data;
  };

  const mutation = mutate(["useUpdateWorkspace"], updateWorkspaceFn, {
    ...options,
    onSuccess: (data, variables, context) => {
      // Refetch workspaces and the specific workspace after updating
      queryClient.refetchQueries({ queryKey: ["useGetWorkspaces"] });
      queryClient.refetchQueries({ 
        queryKey: ["useGetWorkspace", variables.id] 
      });
      
      if (options?.onSuccess) {
        options.onSuccess(data, variables, context);
      }
    },
  });

  return mutation;
};
