import { useEffect, useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../components/ui/tabs";
import { Button } from "../../components/ui/button";
import { Separator } from "../../components/ui/separator";
import { useAIAssistantStore } from "../../stores/aiAssistantStore";
import { useGetLLMProvidersQuery } from "../../controllers/API/queries/ai-assistant";
import IconComponent from "../common/genericIconComponent";
import ShadTooltip from "../common/shadTooltipComponent";
import InstructionInput from "./components/instruction-input";
import ChatInterface from "./components/chat-interface";
import FlowPreview from "./components/flow-preview";
import LLMProviderSelector from "./components/llm-provider-selector";
import APIKeyManager from "./components/api-key-manager";
import { cn } from "../../utils/utils";

export default function AIAssistantPanel() {
  const {
    isOpen,
    setIsOpen,
    activeTab,
    setActiveTab,
    llmProvider,
    llmModel,
    setLLMProvider,
    setLLMModel,
    clarificationQuestions,
  } = useAIAssistantStore();

  const { data: llmProviders, isLoading: isLoadingProviders } = useGetLLMProvidersQuery();

  // Set default provider and model when providers are loaded
  useEffect(() => {
    if (llmProviders && Object.keys(llmProviders).length > 0) {
      const firstProvider = Object.keys(llmProviders)[0];
      const firstModel = llmProviders[firstProvider][0];

      if (!llmProvider || !Object.keys(llmProviders).includes(llmProvider)) {
        setLLMProvider(firstProvider);
      }

      if (!llmModel || !llmProviders[llmProvider]?.includes(llmModel)) {
        setLLMModel(firstModel);
      }
    }
  }, [llmProviders, llmProvider, llmModel, setLLMProvider, setLLMModel]);

  // Auto-switch to chat tab when clarification questions are received
  useEffect(() => {
    if (clarificationQuestions.length > 0 && activeTab !== "chat") {
      setActiveTab("chat");
    }
  }, [clarificationQuestions, activeTab, setActiveTab]);

  if (!isOpen) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <ShadTooltip content="AI Assistant" side="left">
          <Button
            className="h-12 w-12 rounded-full bg-primary text-primary-foreground shadow-lg hover:bg-primary/90"
            onClick={() => setIsOpen(true)}
          >
            <IconComponent name="Bot" className="h-6 w-6" />
          </Button>
        </ShadTooltip>
      </div>
    );
  }

  return (
    <div className="fixed bottom-0 right-0 z-50 flex h-[600px] w-[400px] flex-col rounded-tl-lg border border-border bg-background shadow-xl overflow-hidden">
      <div className="flex items-center justify-between border-b border-border p-4 flex-shrink-0">
        <div className="flex items-center gap-2">
          <IconComponent name="Bot" className="h-5 w-5 text-primary" />
          <h2 className="text-lg font-semibold">AI Assistant</h2>
        </div>
        <div className="flex items-center gap-2">
          <ShadTooltip content="Close" side="left">
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8"
              onClick={() => setIsOpen(false)}
            >
              <IconComponent name="X" className="h-4 w-4" />
            </Button>
          </ShadTooltip>
        </div>
      </div>

      <div className="flex flex-col p-4 space-y-4 flex-shrink-0">
        <LLMProviderSelector
          providers={llmProviders || {}}
          selectedProvider={llmProvider}
          selectedModel={llmModel}
          onProviderChange={setLLMProvider}
          onModelChange={setLLMModel}
          isLoading={isLoadingProviders}
        />

        <APIKeyManager />
      </div>

      <Separator />

      <Tabs
        value={activeTab}
        onValueChange={(value) => setActiveTab(value as any)}
        className="flex-1 flex flex-col overflow-hidden"
      >
        <TabsList className="grid w-full grid-cols-3 flex-shrink-0">
          <TabsTrigger value="instruction" className={cn(clarificationQuestions.length > 0 && "relative")}>
            Instruction
          </TabsTrigger>
          <TabsTrigger value="chat" className={cn(clarificationQuestions.length > 0 && "relative")}>
            Chat
            {clarificationQuestions.length > 0 && (
              <span className="absolute -right-1 -top-1 flex h-5 w-5 items-center justify-center rounded-full bg-primary text-xs text-primary-foreground">
                {clarificationQuestions.length}
              </span>
            )}
          </TabsTrigger>
          <TabsTrigger value="preview">Preview</TabsTrigger>
        </TabsList>

        <TabsContent value="instruction" className="flex-1 overflow-auto p-4">
          <InstructionInput />
        </TabsContent>

        <TabsContent value="chat" className="flex-1 overflow-hidden flex flex-col h-full">
          <ChatInterface />
        </TabsContent>

        <TabsContent value="preview" className="flex-1 overflow-auto p-4">
          <FlowPreview />
        </TabsContent>
      </Tabs>
    </div>
  );
}
