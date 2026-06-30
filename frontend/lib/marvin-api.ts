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

export interface MarvinConfigure {
  models: ModelConfig[];
  builtinTools: BuiltinToolConfig[];
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
    return (await response.json()) as MarvinConfigure;
  } catch {
    return null;
  }
}

export function chatApiUrl(): string {
  return apiUrl("/api/chat");
}
