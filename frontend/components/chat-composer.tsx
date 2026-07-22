"use client";

import {
  ModelSelector,
  ModelSelectorContent,
  ModelSelectorEmpty,
  ModelSelectorGroup,
  ModelSelectorInput,
  ModelSelectorItem,
  ModelSelectorList,
  ModelSelectorLogo,
  ModelSelectorName,
  ModelSelectorTrigger,
} from "@/components/ai-elements/model-selector";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
} from "@/components/ui/select";
import type { MarvinConfigure, ReasoningEffortId } from "@/lib/marvin-api";
import {
  groupModelsByProvider,
  providerLogoSlug,
} from "@/lib/model-provider";
import { cn } from "@/lib/utils";
import { ArrowUpIcon, BrainIcon, SquareIcon } from "lucide-react";
import { useMemo, useState, type FormEvent, type KeyboardEvent } from "react";

/** Shared pill chrome for model + reasoning composer controls. */
const COMPOSER_CONTROL_TRIGGER_CLASS =
  "h-8 max-w-[9.5rem] shrink-0 gap-1.5 rounded-full border-0 bg-muted px-2.5 text-muted-foreground text-xs shadow-none hover:bg-muted sm:max-w-[11rem] sm:px-3 data-popup-open:bg-muted aria-expanded:bg-muted";

interface ChatComposerProps {
  input: string;
  onInputChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onStop: () => void;
  isBusy: boolean;
  config: MarvinConfigure | null;
  model: string;
  onModelChange: (modelId: string) => void;
  reasoningEffort: ReasoningEffortId;
  onReasoningEffortChange: (effort: ReasoningEffortId) => void;
}

export function ChatComposer({
  input,
  onInputChange,
  onSubmit,
  onStop,
  isBusy,
  config,
  model,
  onModelChange,
  reasoningEffort,
  onReasoningEffortChange,
}: ChatComposerProps) {
  const [modelSelectorOpen, setModelSelectorOpen] = useState(false);

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      event.currentTarget.form?.requestSubmit();
    }
  };

  const reasoningEfforts = config?.reasoningEfforts ?? [];
  const modelLabel =
    config?.models.find((entry) => entry.id === model)?.name ?? "Model";
  const reasoningLabel =
    reasoningEfforts.find((entry) => entry.id === reasoningEffort)?.label ??
    "Reasoning";
  const canSend = isBusy || Boolean(input.trim());
  const modelGroups = useMemo(
    () => groupModelsByProvider(config?.models ?? []),
    [config?.models],
  );

  const handleModelSelect = (modelId: string) => {
    onModelChange(modelId);
    setModelSelectorOpen(false);
  };

  return (
    <form className="w-full" onSubmit={onSubmit}>
      <div className="rounded-3xl border border-border bg-card shadow-sm transition-shadow focus-within:shadow-md">
        <textarea
          className="block max-h-40 min-h-[48px] w-full resize-none bg-transparent px-4 pt-4 pb-1 text-[16px] text-foreground leading-6 outline-none placeholder:text-muted-foreground field-sizing-content md:text-[15px]"
          onChange={(event) => onInputChange(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask Marvin"
          rows={1}
          suppressHydrationWarning
          value={input}
        />

        <div className="flex items-center gap-2 px-2 pb-2">
          <div className="flex min-w-0 flex-1 items-center gap-1.5 overflow-x-auto [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden sm:gap-2">
            <ThemeToggle />

            {reasoningEfforts.length > 0 && (
              <Select
                disabled={isBusy}
                onValueChange={(value) => {
                  if (value) {
                    onReasoningEffortChange(value as ReasoningEffortId);
                  }
                }}
                value={reasoningEffort}
              >
                <SelectTrigger
                  className={cn(
                    COMPOSER_CONTROL_TRIGGER_CLASS,
                    // Hide Select's trailing chevron (direct svg child).
                    "[&>svg]:hidden",
                  )}
                >
                  <span className="flex min-w-0 items-center gap-1.5">
                    <BrainIcon className="size-3 shrink-0" />
                    <span className="truncate text-left">{reasoningLabel}</span>
                  </span>
                </SelectTrigger>
                <SelectContent
                  align="end"
                  alignItemWithTrigger={false}
                  className="w-max min-w-40 rounded-xl border-0 bg-popover p-1 text-popover-foreground shadow-md ring-1 ring-foreground/10"
                  side="top"
                  sideOffset={6}
                >
                  {reasoningEfforts.map((entry) => (
                    <SelectItem
                      className="cursor-default rounded-lg py-1.5 pr-8 pl-2 text-sm focus:bg-muted focus:text-foreground data-highlighted:bg-muted"
                      key={entry.id}
                      value={entry.id}
                    >
                      {entry.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}

            {config && config.models.length > 1 && (
              <ModelSelector
                onOpenChange={setModelSelectorOpen}
                open={modelSelectorOpen}
              >
                <ModelSelectorTrigger
                  disabled={isBusy}
                  render={
                    <Button
                      className={COMPOSER_CONTROL_TRIGGER_CLASS}
                      disabled={isBusy}
                      size="sm"
                      type="button"
                      variant="ghost"
                    />
                  }
                >
                  <ModelSelectorLogo provider={providerLogoSlug(model)} />
                  <ModelSelectorName className="min-w-0 truncate">
                    {modelLabel}
                  </ModelSelectorName>
                </ModelSelectorTrigger>
                <ModelSelectorContent showCloseButton={false} title="Select model">
                  <ModelSelectorInput placeholder="Search models..." />
                  <ModelSelectorList>
                    <ModelSelectorEmpty>No models found.</ModelSelectorEmpty>
                    {modelGroups.map((group) => (
                      <ModelSelectorGroup heading={group.label} key={group.key}>
                        {group.models.map((entry) => (
                          <ModelSelectorItem
                            data-checked={model === entry.id || undefined}
                            key={entry.id}
                            onSelect={() => handleModelSelect(entry.id)}
                            value={`${entry.name} ${entry.id}`}
                          >
                            <ModelSelectorLogo
                              provider={providerLogoSlug(entry.id)}
                            />
                            <ModelSelectorName>{entry.name}</ModelSelectorName>
                          </ModelSelectorItem>
                        ))}
                      </ModelSelectorGroup>
                    ))}
                  </ModelSelectorList>
                </ModelSelectorContent>
              </ModelSelector>
            )}
          </div>

          <Button
            aria-label={isBusy ? "Stop" : "Send"}
            className={cn(
              "size-9 shrink-0 rounded-full transition-colors",
              canSend
                ? "bg-primary text-primary-foreground hover:bg-primary/90"
                : "bg-muted text-muted-foreground"
            )}
            disabled={!canSend}
            onClick={
              isBusy
                ? (event) => {
                    event.preventDefault();
                    onStop();
                  }
                : undefined
            }
            size="icon-sm"
            type={isBusy ? "button" : "submit"}
          >
            {isBusy ? (
              <SquareIcon className="size-3.5" />
            ) : (
              <ArrowUpIcon className="size-4" />
            )}
          </Button>
        </div>
      </div>
    </form>
  );
}
