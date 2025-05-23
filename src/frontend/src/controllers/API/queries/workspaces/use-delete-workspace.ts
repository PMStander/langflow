import { useMutationFunctionType } from "@/types/api";
import { api } from "../../api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";
import useWorkspaceStore from "@/stores/workspaceStore";

/**
 * Interface for delete workspace parameters
 */
interface IDeleteWorkspace {
  id: string;
}

/**
 * Hook to delete a workspace
 */
export const useDeleteWorkspace: useMutationFunctionType<
  void,
  IDeleteWorkspace
> = (options?) => {
  const { mutate, queryClient } = UseRequestProcessor();
  const currentWorkspaceId = useWorkspaceStore((state) => state.currentWorkspaceId);
  const setCurrentWorkspaceId = useWorkspaceStore((state) => state.setCurrentWorkspaceId);

  /**
   * Function to delete a workspace
   */
  const deleteWorkspaceFn = async (
    params: IDeleteWorkspace
  ): Promise<void> => {
    await api.delete(`${getURL("WORKSPACES")}/${params.id}`);
  };

  const mutation = mutate(["useDeleteWorkspace"], deleteWorkspaceFn, {
    ...options,
    onSuccess: (data, variables, context) => {
      // If the deleted workspace is the current one, reset the current workspace
      if (currentWorkspaceId === variables.id) {
        setCurrentWorkspaceId(null);
      }
      
      // Refetch workspaces after deleting
      queryClient.refetchQueries({ queryKey: ["useGetWorkspaces"] });
      
      if (options?.onSuccess) {
        options.onSuccess(data, variables, context);
      }
    },
  });

  return mutation;
};
