import { UseMutationResult } from "@tanstack/react-query";
import { api } from "../../api";
import { getURL } from "../../helpers/constants";
import { UseRequestProcessor } from "../../services/request-processor";
import { useMutationFunctionType, useQueryFunctionType } from "../../../../types/api";

// Types for AI Assistant API
export interface InstructionRequest {
  instruction: string;
  llm_provider?: string;
  llm_model?: string;
}

export interface ComponentRequirement {
  component_type: string;
  component_name: string;
  parameters: Record<string, any>;
  description: string;
}

export interface ConnectionRequirement {
  source_component_idx: number;
  target_component_idx: number;
  source_field: string;
  target_field: string;
  description: string;
}

export interface ClarificationQuestion {
  question_id: string;
  question: string;
  options: string[];
  context: Record<string, any>;
}

export interface InstructionResponse {
  instruction: string;
  components: ComponentRequirement[];
  connections: ConnectionRequirement[];
  parameters: Record<string, any>;
  clarification_needed: boolean;
  clarification_questions: ClarificationQuestion[];
  flow_description: string;
}

export interface FlowRequest {
  instruction: string;
  llm_provider?: string;
  llm_model?: string;
}

export interface FlowResponse {
  instruction: string;
  interpretation: InstructionResponse;
  flow: {
    nodes: any[];
    edges: any[];
  };
}

export interface ClarificationRequest {
  question_id: string;
  response: string;
}

export interface ClarificationResponse {
  question_id: string;
  response: string;
  processed: boolean;
  updated_interpretation: InstructionResponse;
}

export interface ComponentInfoRequest {
  component_type: string;
  component_name: string;
}

export interface CompatibleComponentsRequest {
  component_type: string;
  component_name: string;
}

export interface LLMProviderRequest {
  provider_name: string;
  model_name: string;
}

export interface APIKeyRequest {
  key_name: string;
  api_key: string;
}

export interface APIKeysResponse {
  api_keys: string[];
}

// Query to interpret an instruction
export const useInterpretInstructionMutation: useMutationFunctionType<
  InstructionRequest,
  InstructionResponse
> = (options) => {
  const { mutate } = UseRequestProcessor();

  const interpretInstructionFn = async (request: InstructionRequest) => {
    const response = await api.post<InstructionResponse>(
      `${getURL("AI_ASSISTANT")}/interpret`,
      request
    );
    return response.data;
  };

  const mutationResult = mutate(
    ["useInterpretInstructionMutation"],
    interpretInstructionFn,
    {
      ...options,
    }
  );

  return mutationResult as UseMutationResult<
    InstructionResponse,
    Error,
    InstructionRequest,
    unknown
  >;
};

// Query to build a flow from an instruction
export const useBuildFlowMutation: useMutationFunctionType<
  FlowRequest,
  FlowResponse
> = (options) => {
  const { mutate } = UseRequestProcessor();

  const buildFlowFn = async (request: FlowRequest) => {
    const response = await api.post<FlowResponse>(
      `${getURL("AI_ASSISTANT")}/build-flow`,
      request
    );
    return response.data;
  };

  const mutationResult = mutate(
    ["useBuildFlowMutation"],
    buildFlowFn,
    {
      ...options,
    }
  );

  return mutationResult as UseMutationResult<
    FlowResponse,
    Error,
    FlowRequest,
    unknown
  >;
};

// Query to process a clarification response
export const useProcessClarificationMutation: useMutationFunctionType<
  ClarificationRequest,
  ClarificationResponse
> = (options) => {
  const { mutate } = UseRequestProcessor();

  const processClarificationFn = async (request: ClarificationRequest) => {
    const response = await api.post<ClarificationResponse>(
      `${getURL("AI_ASSISTANT")}/clarify`,
      request
    );
    return response.data;
  };

  const mutationResult = mutate(
    ["useProcessClarificationMutation"],
    processClarificationFn,
    {
      ...options,
    }
  );

  return mutationResult as UseMutationResult<
    ClarificationResponse,
    Error,
    ClarificationRequest,
    unknown
  >;
};

// Query to get available LLM providers
export const useGetLLMProvidersQuery: useQueryFunctionType<
  undefined,
  Record<string, string[]>
> = (options) => {
  const { query } = UseRequestProcessor();

  const getLLMProvidersFn = async () => {
    const response = await api.get<Record<string, string[]>>(
      `${getURL("AI_ASSISTANT")}/llm-providers`
    );
    return response.data;
  };

  const queryResult = query(
    ["useGetLLMProvidersQuery"],
    getLLMProvidersFn,
    {
      ...options,
    }
  );

  return queryResult;
};

// Mutation to set the LLM provider
export const useSetLLMProviderMutation: useMutationFunctionType<
  LLMProviderRequest,
  { provider: string; model: string }
> = (options) => {
  const { mutate } = UseRequestProcessor();

  const setLLMProviderFn = async (request: LLMProviderRequest) => {
    const response = await api.post<{ provider: string; model: string }>(
      `${getURL("AI_ASSISTANT")}/set-llm-provider`,
      request
    );
    return response.data;
  };

  const mutationResult = mutate(
    ["useSetLLMProviderMutation"],
    setLLMProviderFn,
    {
      ...options,
    }
  );

  return mutationResult as UseMutationResult<
    { provider: string; model: string },
    Error,
    LLMProviderRequest,
    unknown
  >;
};

// Mutation to save an API key
export const useSaveAPIKeyMutation: useMutationFunctionType<
  APIKeyRequest,
  { message: string; key_name: string }
> = (options) => {
  const { mutate } = UseRequestProcessor();

  const saveAPIKeyFn = async (request: APIKeyRequest) => {
    const response = await api.post<{ message: string; key_name: string }>(
      `${getURL("AI_ASSISTANT")}/save-api-key`,
      request
    );
    return response.data;
  };

  const mutationResult = mutate(
    ["useSaveAPIKeyMutation"],
    saveAPIKeyFn,
    {
      ...options,
    }
  );

  return mutationResult as UseMutationResult<
    { message: string; key_name: string },
    Error,
    APIKeyRequest,
    unknown
  >;
};

// Query to get saved API keys
export const useGetAPIKeysQuery: useQueryFunctionType<
  undefined,
  APIKeysResponse
> = (options) => {
  const { query } = UseRequestProcessor();

  const getAPIKeysFn = async () => {
    const response = await api.get<APIKeysResponse>(
      `${getURL("AI_ASSISTANT")}/api-keys`
    );
    return response.data;
  };

  const queryResult = query(
    ["useGetAPIKeysQuery"],
    getAPIKeysFn,
    {
      ...options,
    }
  );

  return queryResult;
};
