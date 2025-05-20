import { create } from "zustand";
import { 
  ClarificationQuestion, 
  ComponentRequirement, 
  ConnectionRequirement, 
  InstructionResponse 
} from "../controllers/API/queries/ai-assistant";

interface AIAssistantState {
  // UI State
  isOpen: boolean;
  isLoading: boolean;
  activeTab: "instruction" | "chat" | "preview";
  
  // Instruction State
  instruction: string;
  llmProvider: string;
  llmModel: string;
  
  // Response State
  interpretation: InstructionResponse | null;
  clarificationQuestions: ClarificationQuestion[];
  clarificationResponses: Record<string, string>;
  
  // Flow State
  flowNodes: any[];
  flowEdges: any[];
  
  // Chat History
  chatHistory: Array<{
    id: string;
    role: "user" | "assistant";
    content: string;
    timestamp: number;
  }>;
  
  // Actions
  setIsOpen: (isOpen: boolean) => void;
  setIsLoading: (isLoading: boolean) => void;
  setActiveTab: (tab: "instruction" | "chat" | "preview") => void;
  setInstruction: (instruction: string) => void;
  setLLMProvider: (provider: string) => void;
  setLLMModel: (model: string) => void;
  setInterpretation: (interpretation: InstructionResponse | null) => void;
  setClarificationQuestions: (questions: ClarificationQuestion[]) => void;
  addClarificationResponse: (questionId: string, response: string) => void;
  setFlowData: (nodes: any[], edges: any[]) => void;
  addChatMessage: (role: "user" | "assistant", content: string) => void;
  clearChatHistory: () => void;
  reset: () => void;
}

const initialState = {
  isOpen: false,
  isLoading: false,
  activeTab: "instruction" as const,
  instruction: "",
  llmProvider: "OpenAI",
  llmModel: "gpt-4",
  interpretation: null,
  clarificationQuestions: [],
  clarificationResponses: {},
  flowNodes: [],
  flowEdges: [],
  chatHistory: [],
};

export const useAIAssistantStore = create<AIAssistantState>((set) => ({
  ...initialState,
  
  setIsOpen: (isOpen) => set({ isOpen }),
  
  setIsLoading: (isLoading) => set({ isLoading }),
  
  setActiveTab: (activeTab) => set({ activeTab }),
  
  setInstruction: (instruction) => set({ instruction }),
  
  setLLMProvider: (llmProvider) => set({ llmProvider }),
  
  setLLMModel: (llmModel) => set({ llmModel }),
  
  setInterpretation: (interpretation) => set({ interpretation }),
  
  setClarificationQuestions: (clarificationQuestions) => set({ clarificationQuestions }),
  
  addClarificationResponse: (questionId, response) => 
    set((state) => ({
      clarificationResponses: {
        ...state.clarificationResponses,
        [questionId]: response,
      },
    })),
  
  setFlowData: (flowNodes, flowEdges) => set({ flowNodes, flowEdges }),
  
  addChatMessage: (role, content) => 
    set((state) => ({
      chatHistory: [
        ...state.chatHistory,
        {
          id: Math.random().toString(36).substring(2, 9),
          role,
          content,
          timestamp: Date.now(),
        },
      ],
    })),
  
  clearChatHistory: () => set({ chatHistory: [] }),
  
  reset: () => set(initialState),
}));
