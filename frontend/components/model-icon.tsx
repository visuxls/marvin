"use client";

import { cn } from "@/lib/utils";
import { BotIcon } from "lucide-react";

interface MarvinModelIconProps {
  modelId: string;
  className?: string;
  size?: number;
}

const PROVIDER_COLORS: Record<string, string> = {
  anthropic: "bg-orange-500",
  openai: "bg-emerald-600",
  google: "bg-blue-500",
  meta: "bg-sky-600",
  mistral: "bg-violet-500",
  cohere: "bg-pink-500",
  deepseek: "bg-indigo-500",
  qwen: "bg-cyan-600",
};

function providerKey(modelId: string): string {
  const key = modelId.replace(/^openrouter:/, "");
  const slash = key.indexOf("/");
  if (slash === -1) {
    return key.toLowerCase();
  }
  return key.slice(0, slash).toLowerCase();
}

/** Render a compact provider badge for an OpenRouter model id. */
export function MarvinModelIcon({
  modelId,
  className,
  size = 14,
}: MarvinModelIconProps) {
  const provider = providerKey(modelId);
  const colorClass = PROVIDER_COLORS[provider];

  if (!colorClass) {
    return (
      <BotIcon
        aria-hidden
        className={cn("shrink-0 text-muted-foreground", className)}
        size={size}
      />
    );
  }

  return (
    <span
      aria-hidden
      className={cn(
        "inline-flex shrink-0 items-center justify-center rounded-full font-semibold text-white",
        colorClass,
        className
      )}
      style={{
        width: size,
        height: size,
        fontSize: Math.max(8, Math.round(size * 0.58)),
      }}
    >
      {provider.charAt(0).toUpperCase()}
    </span>
  );
}
