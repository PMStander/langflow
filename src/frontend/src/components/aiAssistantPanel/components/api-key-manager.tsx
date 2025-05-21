import { useState, useEffect } from "react";
import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { useToast } from "../../../components/ui/use-toast";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "../../../components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../../../components/ui/select";
import { useGetAPIKeysQuery, useSaveAPIKeyMutation } from "../../../controllers/API/queries/ai-assistant";
import { Separator } from "../../../components/ui/separator";
import { KeyIcon, PlusIcon } from "lucide-react";

// Common API key names for LLM providers
const COMMON_API_KEYS = [
  "OPENAI_API_KEY",
  "ANTHROPIC_API_KEY",
  "GOOGLE_API_KEY",
  "COHERE_API_KEY",
  "GROQ_API_KEY",
  "HUGGINGFACEHUB_API_TOKEN",
  "AZURE_OPENAI_API_KEY",
];

export default function APIKeyManager() {
  const { toast } = useToast();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [selectedKeyName, setSelectedKeyName] = useState(COMMON_API_KEYS[0]);
  const [customKeyName, setCustomKeyName] = useState("");
  const [apiKeyValue, setApiKeyValue] = useState("");
  const [isCustomKey, setIsCustomKey] = useState(false);

  // Get saved API keys
  const { data: apiKeysData, isLoading: isLoadingKeys, refetch: refetchApiKeys } = useGetAPIKeysQuery();

  // Save API key mutation
  const { mutate: saveApiKey, isPending: isSavingKey } = useSaveAPIKeyMutation({
    onSuccess: () => {
      toast({
        title: "API Key Saved",
        description: "Your API key has been saved successfully.",
      });
      setIsDialogOpen(false);
      setApiKeyValue("");
      refetchApiKeys();
    },
    onError: (error) => {
      toast({
        title: "Error Saving API Key",
        description: error.message,
        variant: "destructive",
      });
    },
  } as any);

  // Handle form submission
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const keyName = isCustomKey ? customKeyName : selectedKeyName;

    if (!keyName) {
      toast({
        title: "Error",
        description: "Please select or enter an API key name.",
        variant: "destructive",
      });
      return;
    }

    if (!apiKeyValue) {
      toast({
        title: "Error",
        description: "Please enter an API key value.",
        variant: "destructive",
      });
      return;
    }

    saveApiKey({
      key_name: keyName,
      api_key: apiKeyValue,
    } as any);
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center justify-between">
        <Label className="text-sm font-medium">API Keys</Label>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button variant="outline" size="sm">
              <PlusIcon className="h-4 w-4 mr-1" />
              Add Key
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add API Key</DialogTitle>
              <DialogDescription>
                Add an API key for use with the AI Assistant. Your key will be securely stored.
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit}>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="keyType" className="text-right">
                    Key Type
                  </Label>
                  <div className="col-span-3">
                    <Select
                      value={isCustomKey ? "custom" : "predefined"}
                      onValueChange={(value) => setIsCustomKey(value === "custom")}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select key type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="predefined">Predefined</SelectItem>
                        <SelectItem value="custom">Custom</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {isCustomKey ? (
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="customKeyName" className="text-right">
                      Key Name
                    </Label>
                    <Input
                      id="customKeyName"
                      value={customKeyName}
                      onChange={(e) => setCustomKeyName(e.target.value)}
                      placeholder="e.g., MY_CUSTOM_API_KEY"
                      className="col-span-3"
                    />
                  </div>
                ) : (
                  <div className="grid grid-cols-4 items-center gap-4">
                    <Label htmlFor="keyName" className="text-right">
                      Key Name
                    </Label>
                    <Select
                      value={selectedKeyName}
                      onValueChange={setSelectedKeyName}
                    >
                      <SelectTrigger className="col-span-3">
                        <SelectValue placeholder="Select key name" />
                      </SelectTrigger>
                      <SelectContent>
                        {COMMON_API_KEYS.map((key) => (
                          <SelectItem key={key} value={key}>
                            {key}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                )}

                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="apiKey" className="text-right">
                    API Key
                  </Label>
                  <Input
                    id="apiKey"
                    type="password"
                    value={apiKeyValue}
                    onChange={(e) => setApiKeyValue(e.target.value)}
                    placeholder="Enter your API key"
                    className="col-span-3"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button type="submit" disabled={isSavingKey}>
                  {isSavingKey ? "Saving..." : "Save"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="border rounded-md p-2 max-h-32 overflow-y-auto">
        {isLoadingKeys ? (
          <div className="text-sm text-muted-foreground p-2">Loading API keys...</div>
        ) : apiKeysData?.api_keys && apiKeysData.api_keys.length > 0 ? (
          <div className="space-y-1">
            {apiKeysData.api_keys.map((keyName) => (
              <div key={keyName} className="flex items-center gap-2 p-1 text-sm">
                <KeyIcon className="h-3 w-3 text-muted-foreground" />
                <span>{keyName}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-sm text-muted-foreground p-2">No API keys saved. Add a key to use with the AI Assistant.</div>
        )}
      </div>
    </div>
  );
}
