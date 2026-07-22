import type { ModelConfig } from "@/lib/marvin-api";

/** OpenRouter provider keys that need remapping for models.dev logo slugs. */
const LOGO_SLUG_ALIASES: Record<string, string> = {
  "x-ai": "xai",
  "z-ai": "zai",
};

/** Friendly display names for known providers. */
const PROVIDER_LABELS: Record<string, string> = {
  anthropic: "Anthropic",
  openai: "OpenAI",
  deepseek: "DeepSeek",
  google: "Google",
  meta: "Meta",
  mistral: "Mistral",
  moonshotai: "Moonshot AI",
  cohere: "Cohere",
  qwen: "Qwen",
  "x-ai": "xAI",
  "z-ai": "Z.AI",
};

/**
 * Extract the provider key from an OpenRouter-style model id.
 *
 * Args:
 *   modelId: Model id, optionally prefixed with `openrouter:`.
 *
 * Returns:
 *   Lowercase provider segment (before `/`), or the full id when no slash.
 */
export function providerKey(modelId: string): string {
  const key = modelId.replace(/^openrouter:/, "");
  const slash = key.indexOf("/");
  if (slash === -1) {
    return key.toLowerCase();
  }
  return key.slice(0, slash).toLowerCase();
}

/**
 * Map a provider key to a models.dev logo slug.
 *
 * Args:
 *   modelId: Model id used to derive the provider.
 *
 * Returns:
 *   Logo slug accepted by ModelSelectorLogo.
 */
export function providerLogoSlug(modelId: string): string {
  const key = providerKey(modelId);
  return LOGO_SLUG_ALIASES[key] ?? key;
}

/**
 * Human-readable provider group heading.
 *
 * Args:
 *   modelId: Model id used to derive the provider.
 *
 * Returns:
 *   Display label for ModelSelectorGroup.
 */
export function providerGroupLabel(modelId: string): string {
  const key = providerKey(modelId);
  if (PROVIDER_LABELS[key]) {
    return PROVIDER_LABELS[key];
  }
  if (!key) {
    return "Other";
  }
  return key.charAt(0).toUpperCase() + key.slice(1);
}

export interface ModelProviderGroup {
  key: string;
  label: string;
  models: ModelConfig[];
}

/**
 * Group configure models by provider, preserving first-seen order.
 *
 * Args:
 *   models: Models from `/api/configure`.
 *
 * Returns:
 *   Provider groups for ModelSelectorGroup rendering.
 */
export function groupModelsByProvider(
  models: ModelConfig[],
): ModelProviderGroup[] {
  const groups: ModelProviderGroup[] = [];
  const indexByKey = new Map<string, number>();

  for (const model of models) {
    const key = providerKey(model.id);
    const existing = indexByKey.get(key);
    if (existing === undefined) {
      indexByKey.set(key, groups.length);
      groups.push({
        key,
        label: providerGroupLabel(model.id),
        models: [model],
      });
      continue;
    }
    groups[existing].models.push(model);
  }

  return groups;
}
