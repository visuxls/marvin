"use client";

import { MarvinModelIcon } from "@/components/model-icon";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
} from "@/components/ui/select";
import type { MarvinConfigure } from "@/lib/marvin-api";
import { cn } from "@/lib/utils";
import { ArrowUpIcon, SquareIcon } from "lucide-react";
import type { FormEvent, KeyboardEvent } from "react";

interface ChatComposerProps {
  input: string;
  onInputChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onStop: () => void;
  isBusy: boolean;
  config: MarvinConfigure | null;
  model: string;
  onModelChange: (modelId: string) => void;
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
}: ChatComposerProps) {
  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      event.currentTarget.form?.requestSubmit();
    }
  };

  const modelLabel =
    config?.models.find((entry) => entry.id === model)?.name ?? "Model";
  const canSend = isBusy || Boolean(input.trim());

  return (
    <form className="w-full" onSubmit={onSubmit}>
      <div className="rounded-3xl border border-border bg-card shadow-sm transition-shadow focus-within:shadow-md">
        <textarea
          className="block max-h-40 min-h-[48px] w-full resize-none bg-transparent px-4 pt-4 pb-1 text-[15px] text-foreground leading-6 outline-none placeholder:text-muted-foreground field-sizing-content"
          onChange={(event) => onInputChange(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask Marvin"
          rows={1}
          suppressHydrationWarning
          value={input}
        />

        <div className="flex items-center justify-between gap-2 px-2 pb-2">
          <ThemeToggle />

          <div className="flex items-center gap-2">
            {config && config.models.length > 1 && (
              <Select
                disabled={isBusy}
                onValueChange={(value) => {
                  if (value) {
                    onModelChange(value);
                  }
                }}
                value={model}
              >
                <SelectTrigger
                  className="h-8 shrink-0 rounded-full border-0 bg-muted/80 px-3 text-muted-foreground text-xs shadow-none hover:bg-muted data-popup-open:bg-muted"
                  size="sm"
                >
                  <span className="flex items-center gap-1.5 whitespace-nowrap">
                    <MarvinModelIcon modelId={model} />
                    <span>{modelLabel}</span>
                  </span>
                </SelectTrigger>
                <SelectContent
                  align="end"
                  alignItemWithTrigger={false}
                  className="w-max min-w-(--anchor-width) rounded-2xl border-0 bg-muted/80 p-1 text-muted-foreground text-xs shadow-none ring-0"
                  side="top"
                  sideOffset={6}
                >
                  {config.models.map((entry) => (
                    <SelectItem
                      className="rounded-full py-1.5 pr-8 pl-3 focus:bg-muted data-highlighted:bg-muted/70"
                      key={entry.id}
                      value={entry.id}
                    >
                      <MarvinModelIcon modelId={entry.id} />
                      {entry.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}

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
      </div>
    </form>
  );
}
