import { useState } from "react";
import { Button } from "../../../components/ui/button";
import { Textarea } from "../../../components/ui/textarea";
import { useAIAssistantStore } from "../../../stores/aiAssistantStore";
import { useInterpretInstructionMutation, useBuildFlowMutation } from "../../../controllers/API/queries/ai-assistant";
import IconComponent from "../../common/genericIconComponent";
import { useToast } from "../../../components/ui/use-toast";

export default function InstructionInput() {
  const { toast } = useToast();
  const [inputValue, setInputValue] = useState("");
  
  const {
    setInstruction,
    setIsLoading,
    setInterpretation,
    setClarificationQuestions,
    setFlowData,
    addChatMessage,
    llmProvider,
    llmModel,
    setActiveTab,
  } = useAIAssistantStore();

  const { mutate: interpretInstruction, isLoading: isInterpreting } = useInterpretInstructionMutation({
    onSuccess: (data) => {
      setInterpretation(data);
      
      // Add the instruction to chat history
      addChatMessage("user", inputValue);
      
      // If clarification is needed, add assistant message and switch to chat tab
      if (data.clarification_needed && data.clarification_questions.length > 0) {
        const question = data.clarification_questions[0].question;
        addChatMessage("assistant", question);
        setClarificationQuestions(data.clarification_questions);
        setActiveTab("chat");
      } else {
        // If no clarification needed, build the flow
        buildFlow({
          instruction: inputValue,
          llm_provider: llmProvider,
          llm_model: llmModel,
        });
      }
    },
    onError: (error) => {
      toast({
        title: "Error interpreting instruction",
        description: error.message,
        variant: "destructive",
      });
      setIsLoading(false);
    },
  });

  const { mutate: buildFlow, isLoading: isBuilding } = useBuildFlowMutation({
    onSuccess: (data) => {
      setFlowData(data.flow.nodes, data.flow.edges);
      
      // Add success message to chat
      addChatMessage(
        "assistant",
        "I've built a flow based on your instructions. You can view it in the Preview tab."
      );
      
      // Switch to preview tab
      setActiveTab("preview");
      setIsLoading(false);
    },
    onError: (error) => {
      toast({
        title: "Error building flow",
        description: error.message,
        variant: "destructive",
      });
      setIsLoading(false);
    },
  });

  const handleSubmit = () => {
    if (!inputValue.trim()) return;
    
    setIsLoading(true);
    setInstruction(inputValue);
    
    // Interpret the instruction
    interpretInstruction({
      instruction: inputValue,
      llm_provider: llmProvider,
      llm_model: llmModel,
    });
  };

  return (
    <div className="flex h-full flex-col gap-4">
      <div className="flex-1">
        <Textarea
          placeholder="Describe the flow you want to build..."
          className="h-full min-h-[300px] resize-none"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          disabled={isInterpreting || isBuilding}
        />
      </div>
      
      <div className="flex items-center justify-between">
        <div className="text-sm text-muted-foreground">
          {isInterpreting || isBuilding ? (
            <span className="flex items-center gap-2">
              <IconComponent name="Loader2" className="h-4 w-4 animate-spin" />
              {isInterpreting ? "Interpreting..." : "Building flow..."}
            </span>
          ) : (
            "Enter a natural language instruction"
          )}
        </div>
        
        <Button
          onClick={handleSubmit}
          disabled={!inputValue.trim() || isInterpreting || isBuilding}
        >
          <IconComponent name="Wand2" className="mr-2 h-4 w-4" />
          Build Flow
        </Button>
      </div>
      
      <div className="text-xs text-muted-foreground">
        <p>Example: "Create a simple chatbot using OpenAI and a prompt template"</p>
        <p>Example: "Build a document QA system with vector storage and retrieval"</p>
      </div>
    </div>
  );
}
