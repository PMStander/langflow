import {
  DEFAULT_FOLDER,
  DEFAULT_FOLDER_DEPRECATED,
} from "@/constants/constants";
import { FolderType } from "@/pages/MainPage/entities";
import useAuthStore from "@/stores/authStore";
import { useFolderStore } from "@/stores/foldersStore";
import useWorkspaceStore from "@/stores/workspaceStore";
import { useQueryFunctionType } from "@/types/api";
import { api } from "../../api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";

interface IGetFolders {
  workspace_id?: string;
}

export const useGetFoldersQuery: useQueryFunctionType<
  IGetFolders,
  FolderType[]
> = (options) => {
  const { query } = UseRequestProcessor();

  const setMyCollectionId = useFolderStore((state) => state.setMyCollectionId);
  const setFolders = useFolderStore((state) => state.setFolders);
  const currentWorkspaceId = useWorkspaceStore((state) => state.currentWorkspaceId);

  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  const getFoldersFn = async (params: IGetFolders = {}): Promise<FolderType[]> => {
    if (!isAuthenticated) return [];

    // Use the workspace_id from params or the current workspace
    const workspaceId = params.workspace_id || currentWorkspaceId;

    // Build the URL with query parameters if workspace_id is provided
    let url = `${getURL("PROJECTS")}/`;
    if (workspaceId) {
      url += `?workspace_id=${workspaceId}`;
    }

    const res = await api.get(url);
    const data = res.data;

    const myCollectionId = data?.find(
      (f) => f.name === DEFAULT_FOLDER_DEPRECATED,
    )?.id;
    setMyCollectionId(myCollectionId);
    setFolders(data);

    return data;
  };

  const queryResult = query(
    ["useGetFolders", currentWorkspaceId],
    () => getFoldersFn(options as IGetFolders),
    {
      ...options,
      enabled: isAuthenticated,
      // Refetch when the workspace changes
      refetchOnWindowFocus: true,
    }
  );
  return queryResult;
};
