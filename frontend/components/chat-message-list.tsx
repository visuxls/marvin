"use client";

import { Message, MessageContent } from "@/components/ai-elements/message";
import { MessageChartSupplements } from "@/components/finance/message-chart-supplements";
import {
  MessagePart,
  ThinkingGroup,
} from "@/components/message-part";
import {
  groupMessageParts,
  lastTextPartIndex,
  mergeConsecutiveAssistantMessages,
  orderMessageGroupsForDisplay,
} from "@/lib/message-parts";
import { Button } from "@/components/ui/button";
import { Spinner } from "@/components/ui/spinner";
import { CHAT_COLUMN } from "@/lib/constants";
import { cn } from "@/lib/utils";
import type {
  ChatAddToolApproveResponseFunction,
  ChatStatus,
  UIMessage,
} from "ai";
import {
  ConversationEmptyState,
} from "@/components/ai-elements/conversation";
import { WalletIcon } from "lucide-react";

function messagePartKey(
  message: UIMessage,
  part: UIMessage["parts"][number],
  index: number
): string {
  if ("toolCallId" in part && part.toolCallId) {
    return `${message.id}-tool-${part.toolCallId}`;
  }
  return `${message.id}-${part.type}-${index}`;
}

interface ChatMessageListProps {
  messages: UIMessage[];
  status: ChatStatus;
  isLoadingMessages: boolean;
  error: Error | undefined;
  onRegenerate: (messageId: string) => void;
  onRetry: () => void;
  onApprovalResponse: ChatAddToolApproveResponseFunction;
}

export function ChatMessageList({
  messages,
  status,
  isLoadingMessages,
  error,
  onRegenerate,
  onRetry,
  onApprovalResponse,
}: ChatMessageListProps) {
  return (
    <div className={cn(CHAT_COLUMN, "flex flex-col gap-8 py-8")}>
      {isLoadingMessages ? (
        <div className="flex min-h-[40vh] items-center justify-center gap-2 text-muted-foreground text-sm">
          <Spinner className="size-4" />
          Loading conversation…
        </div>
      ) : messages.length === 0 ? (
        <ConversationEmptyState
          className="min-h-[40vh] p-0"
          description="Pick a starting point below or ask anything."
          icon={<WalletIcon className="size-8 text-muted-foreground" />}
          title="How can I help with your finances?"
        />
      ) : (
        mergeConsecutiveAssistantMessages(
          messages.filter((message) => message.role !== "system")
        ).map((message, messageIndex, visibleMessages) => {
          const isLastMessage = messageIndex === visibleMessages.length - 1;
          const hideCharts =
            message.role === "assistant" &&
            isLastMessage &&
            (status === "streaming" || status === "submitted");
          const lastTextIndex = lastTextPartIndex(message.parts);

          return (
          <Message
            className={cn(
              "w-full max-w-none",
              message.role === "user" ? "items-end" : "gap-4"
            )}
            from={message.role}
            key={message.id}
          >
            <MessageContent
              className={cn(
                message.role === "user"
                  ? "max-w-[85%] rounded-[20px] bg-muted px-4 py-2.5 text-[15px] leading-6"
                  : "w-full max-w-none text-[15px] leading-7"
              )}
            >
              {orderMessageGroupsForDisplay(
                groupMessageParts(message.parts)
              ).map((group) => {
                if (group.type === "thinking") {
                  return (
                    <ThinkingGroup
                      chatStatus={status}
                      group={group}
                      key={`${message.id}-thinking-${group.startIndex}`}
                      message={message}
                      onApprovalResponse={onApprovalResponse}
                    />
                  );
                }

                const { part, index } = group;
                return (
                  <MessagePart
                    chatStatus={status}
                    isLastAssistantPart={index === lastTextIndex}
                    key={messagePartKey(message, part, index)}
                    message={message}
                    onRegenerate={onRegenerate}
                    part={part}
                  />
                );
              })}
              {message.role === "assistant" && !hideCharts ? (
                <MessageChartSupplements message={message} />
              ) : null}
            </MessageContent>
          </Message>
        );
        })
      )}

      {status === "submitted" && (
        <div className="flex items-center gap-2 text-muted-foreground text-sm">
          <Spinner className="size-4" />
          Thinking…
        </div>
      )}

      {status === "error" && error && (
        <div className="rounded-2xl border border-destructive/30 bg-destructive/5 p-4 text-sm">
          <p className="font-medium text-destructive">Error</p>
          <p className="mt-1 text-muted-foreground">{error.message}</p>
          <Button
            className="mt-3"
            onClick={onRetry}
            size="sm"
            type="button"
            variant="outline"
          >
            Retry
          </Button>
        </div>
      )}
    </div>
  );
}
