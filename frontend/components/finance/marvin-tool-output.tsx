"use client";

import { CodeBlock } from "@/components/ai-elements/code-block";
import type { ToolPart } from "@/components/ai-elements/tool";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { cn } from "@/lib/utils";
import { ChevronDownIcon } from "lucide-react";
import { isValidElement } from "react";

interface MarvinToolOutputProps {
  toolPart: ToolPart;
}

/**
 * JSON-only Marvin tool result for collapsed thinking panels.
 */
export function MarvinToolOutput({ toolPart }: MarvinToolOutputProps) {
  const output = "output" in toolPart ? toolPart.output : undefined;
  const errorText = "errorText" in toolPart ? toolPart.errorText : undefined;

  if (!(output || errorText)) {
    return null;
  }

  let serializedOutput: string | null = null;
  if (output) {
    if (typeof output === "string") {
      serializedOutput = output;
    } else if (!isValidElement(output)) {
      serializedOutput = JSON.stringify(output, null, 2);
    }
  }

  return (
    <div className="space-y-2">
      {errorText ? (
        <div className="rounded-md bg-destructive/10 p-3 text-destructive text-xs">
          {errorText}
        </div>
      ) : null}
      {serializedOutput ? (
        <Collapsible className="group" defaultOpen={false}>
          <CollapsibleTrigger
            className={cn(
              "flex w-full items-center justify-between rounded-md bg-muted/50 px-3 py-2 text-muted-foreground text-xs uppercase tracking-wide"
            )}
          >
            Raw data
            <ChevronDownIcon className="size-3.5 transition-transform group-data-[state=open]:rotate-180" />
          </CollapsibleTrigger>
          <CollapsibleContent className="mt-2 overflow-x-auto rounded-md bg-muted/50">
            <CodeBlock code={serializedOutput} language="json" />
          </CollapsibleContent>
        </Collapsible>
      ) : null}
    </div>
  );
}
