import { useEffect, useRef, useState } from "react";
import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { ScrollArea } from "../../../components/ui/scroll-area";
import { useAIAssistantStore } from "../../../stores/aiAssistantStore";
import { useProcessClarificationMutation, useBuildFlowMutation } from "../../../controllers/API/queries/ai-assistant";
import IconComponent from "../../common/genericIconComponent";
import { useToast } from "../../../components/ui/use-toast";
import { cn } from "../../../utils/utils";

export default function ChatInterface() {
  const { toast } = useToast();
  const [inputValue, setInputValue] = useState("");
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const {
    chatHistory,
    addChatMessage,
    clarificationQuestions,
    clarificationResponses,
    addClarificationResponse,
    setClarificationQuestions,
    setInterpretation,
    setFlowData,
    setActiveTab,
    instruction,
    llmProvider,
    llmModel,
    setIsLoading,
    interpretation,
  } = useAIAssistantStore();

  // Scroll to bottom when chat history changes
  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollContainer = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [chatHistory]);

  const { mutate: processClarification, isPending: isProcessing } = useProcessClarificationMutation({
    onSuccess: (data) => {
      // Update the interpretation with the new data
      setInterpretation(data.updated_interpretation);

      // If there are more clarification questions, add them to the chat
      if (
        data.updated_interpretation.clarification_needed &&
        data.updated_interpretation.clarification_questions.length > 0
      ) {
        const question = data.updated_interpretation.clarification_questions[0].question;
        addChatMessage("assistant", question);
        setClarificationQuestions(data.updated_interpretation.clarification_questions);
      } else {
        // If no more clarification needed, build the flow
        buildFlow({
          instruction,
          llm_provider: llmProvider,
          llm_model: llmModel,
        } as any);
      }

      setIsLoading(false);
    },
    onError: (error) => {
      toast({
        title: "Error processing clarification",
        description: error.message,
        variant: "destructive",
      });
      setIsLoading(false);
    },
  } as any);

  const { mutate: buildFlow, isPending: isBuilding } = useBuildFlowMutation({
    onSuccess: (data) => {
      setFlowData(data.flow.nodes, data.flow.edges);

      // Add success message to chat
      addChatMessage(
        "assistant",
        "I've built a flow based on your instructions. You can view it in the Preview tab."
      );

      // Clear clarification questions
      setClarificationQuestions([]);

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
  } as any);

  const handleSubmit = () => {
    if (!inputValue.trim() || isProcessing || isBuilding) return;

    // Add user message to chat
    addChatMessage("user", inputValue);

    // If there are clarification questions, process the response
    if (clarificationQuestions.length > 0) {
      const questionId = clarificationQuestions[0].question_id;

      setIsLoading(true);
      addClarificationResponse(questionId, inputValue);

      processClarification({
        question_id: questionId,
        response: inputValue,
        instruction: instruction, // Add the required instruction field
      } as any);
    } else if (interpretation) {
      // If there's an interpretation but no clarification questions,
      // add a helpful assistant message
      addChatMessage(
        "assistant",
        "Your flow has been built based on your instructions. You can view it in the Preview tab."
      );
    } else {
      // If there's no instruction or interpretation yet, guide the user
      addChatMessage(
        "assistant",
        "Please enter your instruction in the Instruction tab first to create a flow."
      );
      setActiveTab("instruction");
    }

    // Clear input
    setInputValue("");
  };

  return (
    <div className="flex h-full flex-col">
      {/* Set a fixed height for the scroll area with flex-grow to take remaining space */}
      <ScrollArea ref={scrollAreaRef} className="flex-grow p-4" style={{ minHeight: 0 }}>
        <div className="flex flex-col gap-4 pb-2">
          {chatHistory.length === 0 ? (
            <div className="flex flex-col items-center justify-center text-center text-muted-foreground py-8">
              <IconComponent name="MessageSquare" className="mb-2 h-12 w-12" />
              <p>No messages yet</p>
              <p className="text-sm">Start by entering an instruction in the Instruction tab</p>
            </div>
          ) : (
            chatHistory.map((message) => (
              <div
                key={message.id}
                className={cn(
                  "flex w-full max-w-[80%] flex-col rounded-lg p-3",
                  message.role === "user"
                    ? "ml-auto bg-primary text-primary-foreground"
                    : "bg-muted"
                )}
              >
                <div className="text-sm">{message.content}</div>
                <div className="mt-1 text-right text-xs opacity-70">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </div>
              </div>
            ))
          )}

          {(isProcessing || isBuilding) && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <IconComponent name="Loader2" className="h-4 w-4 animate-spin" />
              {isProcessing ? "Processing..." : "Building flow..."}
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Set the input area to be fixed at the bottom with flex-shrink-0 */}
      <div className="border-t border-border p-4 flex-shrink-0">
        <div className="flex items-center gap-2">
          <Input
            placeholder="Type your response..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit();
              }
            }}
            disabled={isProcessing || isBuilding}
          />
          <Button
            size="icon"
            onClick={handleSubmit}
            disabled={!inputValue.trim() || isProcessing || isBuilding}
          >
            <IconComponent name="Send" className="h-4 w-4" />
          </Button>
        </div>

        {/* Show information about the flow if available */}
        {interpretation && !interpretation.clarification_needed && (
          <div className="mt-2 text-xs text-muted-foreground">
            {clarificationQuestions.length === 0
              ? "No clarification needed. Check the Preview tab to see your flow."
              : "Answering clarification questions will help refine your flow."}
          </div>
        )}
      </div>
    </div>
  );
}
