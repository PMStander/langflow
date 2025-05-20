import { useEffect } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../../../components/ui/select";
import { useSetLLMProviderMutation } from "../../../controllers/API/queries/ai-assistant";
import { useToast } from "../../../components/ui/use-toast";
import IconComponent from "../../common/genericIconComponent";

interface LLMProviderSelectorProps {
  providers: Record<string, string[]>;
  selectedProvider: string;
  selectedModel: string;
  onProviderChange: (provider: string) => void;
  onModelChange: (model: string) => void;
  isLoading: boolean;
}

export default function LLMProviderSelector({
  providers,
  selectedProvider,
  selectedModel,
  onProviderChange,
  onModelChange,
  isLoading,
}: LLMProviderSelectorProps) {
  const { toast } = useToast();
  
  const { mutate: setLLMProvider, isLoading: isSettingProvider } = useSetLLMProviderMutation({
    onSuccess: (data) => {
      toast({
        title: "LLM Provider Updated",
        description: `Using ${data.provider} with model ${data.model}`,
      });
    },
    onError: (error) => {
      toast({
        title: "Error setting LLM provider",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  // Update the model when the provider changes
  useEffect(() => {
    if (providers[selectedProvider]?.length > 0 && !providers[selectedProvider].includes(selectedModel)) {
      onModelChange(providers[selectedProvider][0]);
    }
  }, [selectedProvider, selectedModel, providers, onModelChange]);

  // Update the backend when provider or model changes
  useEffect(() => {
    if (selectedProvider && selectedModel) {
      setLLMProvider({
        provider_name: selectedProvider,
        model_name: selectedModel,
      });
    }
  }, [selectedProvider, selectedModel, setLLMProvider]);

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center gap-2">
        <div className="flex-1">
          <label className="text-sm font-medium">LLM Provider</label>
          <Select
            value={selectedProvider}
            onValueChange={onProviderChange}
            disabled={isLoading || isSettingProvider || Object.keys(providers).length === 0}
          >
            <SelectTrigger className="mt-1">
              <SelectValue placeholder="Select provider" />
            </SelectTrigger>
            <SelectContent>
              {Object.keys(providers).map((provider) => (
                <SelectItem key={provider} value={provider}>
                  {provider}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        
        <div className="flex-1">
          <label className="text-sm font-medium">Model</label>
          <Select
            value={selectedModel}
            onValueChange={onModelChange}
            disabled={
              isLoading ||
              isSettingProvider ||
              !selectedProvider ||
              !providers[selectedProvider] ||
              providers[selectedProvider].length === 0
            }
          >
            <SelectTrigger className="mt-1">
              <SelectValue placeholder="Select model" />
            </SelectTrigger>
            <SelectContent>
              {selectedProvider &&
                providers[selectedProvider]?.map((model) => (
                  <SelectItem key={model} value={model}>
                    {model}
                  </SelectItem>
                ))}
            </SelectContent>
          </Select>
        </div>
      </div>
      
      {(isLoading || isSettingProvider) && (
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <IconComponent name="Loader2" className="h-3 w-3 animate-spin" />
          {isLoading ? "Loading providers..." : "Updating provider..."}
        </div>
      )}
    </div>
  );
}
