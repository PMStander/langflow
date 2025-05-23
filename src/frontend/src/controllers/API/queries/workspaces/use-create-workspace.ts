import { CreateWorkspaceType, WorkspaceType } from "@/types/workspace";
import { useMutationFunctionType } from "@/types/api";
import { api } from "../../api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";

/**
 * Interface for create workspace parameters
 */
interface ICreateWorkspace {
  data: CreateWorkspaceType;
}

/**
 * Hook to create a workspace
 */
export const useCreateWorkspace: useMutationFunctionType<
  WorkspaceType,
  ICreateWorkspace
> = (options?) => {
  const { mutate, queryClient } = UseRequestProcessor();

  /**
   * Function to create a workspace
   */
  const createWorkspaceFn = async (
    params: ICreateWorkspace
  ): Promise<WorkspaceType> => {
    const payload = {
      name: params.data.name,
      description: params.data.description || null,
    };

    const res = await api.post(`${getURL("WORKSPACES")}/`, payload);
    return res.data;
  };

  const mutation = mutate(["useCreateWorkspace"], createWorkspaceFn, {
    ...options,
    onSuccess: (data, variables, context) => {
      // Refetch workspaces after creating a new one
      queryClient.refetchQueries({ queryKey: ["useGetWorkspaces"] });
      
      if (options?.onSuccess) {
        options.onSuccess(data, variables, context);
      }
    },
  });

  return mutation;
};
