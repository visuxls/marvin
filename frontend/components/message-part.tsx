"use client";

import {
  MessageAction,
  MessageActions,
  MessageResponse,
} from "@/components/ai-elements/message";
import {
  Reasoning,
  ReasoningContent,
  ReasoningTrigger,
} from "@/components/ai-elements/reasoning";
import {
  Tool,
  ToolContent,
  ToolHeader,
  ToolInput,
  ToolOutput,
  type ToolPart,
} from "@/components/ai-elements/tool";
import { Button } from "@/components/ui/button";
import {
  isToolPart,
  type MessagePartGroup,
} from "@/lib/message-parts";
import type {
  ChatAddToolApproveResponseFunction,
  ChatStatus,
  UIMessage,
} from "ai";
import { CopyIcon, RefreshCcwIcon } from "lucide-react";
import { cjk } from "@streamdown/cjk";
import { code } from "@streamdown/code";
import { math } from "@streamdown/math";
import { mermaid } from "@streamdown/mermaid";
import { Streamdown } from "streamdown";

const streamdownPlugins = { cjk, code, math, mermaid };

function humanizeToolName(raw: string): string {
  const name = raw.replace(/^get_/, "").replace(/_/g, " ");
  return name.charAt(0).toUpperCase() + name.slice(1);
}

function toolDisplayName(part: ToolPart): string {
  if (part.type === "dynamic-tool") {
    return humanizeToolName(part.toolName);
  }
  return humanizeToolName(part.type.replace(/^tool-/, ""));
}

function MarvinToolPart({
  toolPart,
  nested = false,
  onApprovalResponse,
}: {
  toolPart: ToolPart;
  nested?: boolean;
  onApprovalResponse?: ChatAddToolApproveResponseFunction;
}) {
  const needsApproval = toolPart.state === "approval-requested";

  return (
    <Tool
      className={nested ? "mb-2 border-border/40 bg-muted/20" : "mb-2 border-border/60"}
    >
      {toolPart.type === "dynamic-tool" ? (
        <ToolHeader
          state={toolPart.state}
          title={toolDisplayName(toolPart)}
          toolName={toolPart.toolName}
          type="dynamic-tool"
        />
      ) : (
        <ToolHeader
          state={toolPart.state}
          title={toolDisplayName(toolPart)}
          type={toolPart.type}
        />
      )}
      <ToolContent>
        {"input" in toolPart &&
          toolPart.input !== undefined &&
          JSON.stringify(toolPart.input) !== "{}" && (
            <ToolInput input={toolPart.input} />
          )}
        <ToolOutput
          errorText={"errorText" in toolPart ? toolPart.errorText : undefined}
          output={"output" in toolPart ? toolPart.output : undefined}
        />
        {needsApproval && onApprovalResponse && "toolCallId" in toolPart && (
          <div className="flex gap-2">
            <Button
              onClick={() =>
                onApprovalResponse({
                  id: toolPart.toolCallId,
                  approved: true,
                })
              }
              size="sm"
              type="button"
            >
              Approve
            </Button>
            <Button
              onClick={() =>
                onApprovalResponse({
                  id: toolPart.toolCallId,
                  approved: false,
                })
              }
              size="sm"
              type="button"
              variant="outline"
            >
              Deny
            </Button>
          </div>
        )}
      </ToolContent>
    </Tool>
  );
}

function isThinkingGroupStreaming(
  chatStatus: ChatStatus,
  message: UIMessage,
  group: Extract<MessagePartGroup, { type: "thinking" }>
): boolean {
  if (chatStatus !== "streaming" || message.role !== "assistant") {
    return false;
  }

  const lastPartIndex = group.startIndex + group.parts.length - 1;
  if (lastPartIndex !== message.parts.length - 1) {
    return false;
  }

  const lastPart = group.parts[group.parts.length - 1];
  if (lastPart?.type === "reasoning") {
    return true;
  }

  if (lastPart && isToolPart(lastPart)) {
    return (
      lastPart.state === "input-streaming" || lastPart.state === "input-available"
    );
  }

  return false;
}

interface ThinkingGroupProps {
  group: Extract<MessagePartGroup, { type: "thinking" }>;
  message: UIMessage;
  chatStatus: ChatStatus;
  onApprovalResponse?: ChatAddToolApproveResponseFunction;
}

export function ThinkingGroup({
  group,
  message,
  chatStatus,
  onApprovalResponse,
}: ThinkingGroupProps) {
  const reasoningText = group.parts
    .filter((part) => part.type === "reasoning")
    .map((part) => part.text)
    .join("\n\n");
  const toolParts = group.parts.filter(isToolPart);

  return (
    <Reasoning isStreaming={isThinkingGroupStreaming(chatStatus, message, group)}>
      <ReasoningTrigger />
      <ReasoningContent>
        <div className="space-y-3">
          {reasoningText ? (
            <Streamdown plugins={streamdownPlugins}>{reasoningText}</Streamdown>
          ) : null}
          {toolParts.map((toolPart) => (
            <MarvinToolPart
              key={toolPart.toolCallId}
              nested
              onApprovalResponse={onApprovalResponse}
              toolPart={toolPart}
            />
          ))}
        </div>
      </ReasoningContent>
    </Reasoning>
  );
}

interface MessagePartProps {
  part: UIMessage["parts"][number];
  message: UIMessage;
  chatStatus: ChatStatus;
  isLastAssistantPart: boolean;
  onRegenerate: (messageId: string) => void;
}

export function MessagePart({
  part,
  message,
  chatStatus,
  isLastAssistantPart,
  onRegenerate,
}: MessagePartProps) {
  if (part.type === "text") {
    const isStreamingText =
      chatStatus === "streaming" &&
      message.role === "assistant" &&
      isLastAssistantPart;

    if (message.role === "user") {
      return <p className="whitespace-pre-wrap">{part.text}</p>;
    }

    return (
      <>
        <MessageResponse
          animated={isStreamingText}
          className="[&_h1]:mb-4 [&_h1]:font-semibold [&_h1]:text-lg [&_h2]:mb-3 [&_h2]:mt-6 [&_h2]:font-semibold [&_h3]:mb-2 [&_h3]:mt-4 [&_h3]:font-medium [&_li]:my-1 [&_ol]:my-4 [&_ol]:list-decimal [&_ol]:pl-5 [&_p:last-child]:mb-0 [&_p]:mb-4 [&_ul]:my-4 [&_ul]:list-disc [&_ul]:pl-5"
          isAnimating={isStreamingText}
          mode={isStreamingText ? "streaming" : "static"}
        >
          {part.text}
        </MessageResponse>
        {message.role === "assistant" &&
          isLastAssistantPart &&
          chatStatus !== "submitted" &&
          chatStatus !== "streaming" && (
          <MessageActions className="mt-1 opacity-80">
            <MessageAction
              label="Regenerate"
              onClick={() => onRegenerate(message.id)}
              tooltip="Regenerate"
            >
              <RefreshCcwIcon className="size-3.5" />
            </MessageAction>
            <MessageAction
              label="Copy"
              onClick={() => {
                // User feedback for clipboard failures is deferred.
                navigator.clipboard.writeText(part.text).catch(() => {});
              }}
              tooltip="Copy"
            >
              <CopyIcon className="size-3.5" />
            </MessageAction>
          </MessageActions>
        )}
      </>
    );
  }

  return null;
}
