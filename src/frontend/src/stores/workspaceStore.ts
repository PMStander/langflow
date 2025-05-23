import { WorkspaceMemberType, WorkspaceType } from "../types/workspace";
import { WorkspaceStoreType } from "../types/zustand/workspace";
import { create } from "zustand";
import { persist } from "zustand/middleware";

/**
 * Workspace store
 */
const useWorkspaceStore = create<WorkspaceStoreType>()(
  persist(
    (set) => ({
      // Current workspace
      currentWorkspaceId: null,
      setCurrentWorkspaceId: (id) => set({ currentWorkspaceId: id }),
      
      // All workspaces
      workspaces: [],
      setWorkspaces: (workspaces) => set({ workspaces }),
      
      // Workspace members
      workspaceMembers: [],
      setWorkspaceMembers: (members) => set({ workspaceMembers: members }),
      
      // Workspace to edit
      workspaceToEdit: null,
      setWorkspaceToEdit: (workspace) => set({ workspaceToEdit: workspace }),
      
      // Reset store
      resetStore: () =>
        set({
          currentWorkspaceId: null,
          workspaces: [],
          workspaceMembers: [],
          workspaceToEdit: null,
        }),
    }),
    {
      name: "workspace-storage",
      partialize: (state) => ({
        currentWorkspaceId: state.currentWorkspaceId,
      }),
    }
  )
);

export default useWorkspaceStore;
