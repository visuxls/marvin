/** Same-origin `/api/*` routes are proxied to Marvin via `app/api/[...path]/route.ts`. */
export const API_BASE = process.env.NEXT_PUBLIC_MARVIN_API_URL ?? "";

export interface ModelConfig {
  id: string;
  name: string;
  builtinTools: string[];
}

export interface BuiltinToolConfig {
  id: string;
  name: string;
}

export type ReasoningEffortId =
  | "off"
  | "minimal"
  | "low"
  | "medium"
  | "high"
  | "xhigh";

export interface ReasoningEffortOption {
  id: ReasoningEffortId;
  label: string;
}

export interface MarvinConfigure {
  models: ModelConfig[];
  builtinTools: BuiltinToolConfig[];
  reasoningEfforts: ReasoningEffortOption[];
  defaultReasoningEffort: ReasoningEffortId;
}

export const DEFAULT_REASONING_EFFORTS: ReasoningEffortOption[] = [
  { id: "off", label: "Off" },
  { id: "minimal", label: "Minimal" },
  { id: "low", label: "Low" },
  { id: "medium", label: "Medium" },
  { id: "high", label: "High" },
  { id: "xhigh", label: "Extra high" },
];

function normalizeConfigureResponse(
  data: Partial<MarvinConfigure> & Pick<MarvinConfigure, "models" | "builtinTools">,
): MarvinConfigure {
  return {
    models: data.models,
    builtinTools: data.builtinTools,
    reasoningEfforts: data.reasoningEfforts ?? DEFAULT_REASONING_EFFORTS,
    defaultReasoningEffort: data.defaultReasoningEffort ?? "off",
  };
}

function apiUrl(path: string): string {
  return `${API_BASE}${path}`;
}

export { apiUrl };

export async function fetchConfigure(): Promise<MarvinConfigure | null> {
  try {
    const response = await fetch(apiUrl("/api/configure"));
    if (!response.ok) {
      return null;
    }
    const data = (await response.json()) as Partial<MarvinConfigure> &
      Pick<MarvinConfigure, "models" | "builtinTools">;
    return normalizeConfigureResponse(data);
  } catch {
    return null;
  }
}

export function chatApiUrl(): string {
  return apiUrl("/api/chat");
}
