"use client";

import { ChatComposer } from "@/components/chat-composer";
import { ChatMessageList } from "@/components/chat-message-list";
import { ChatPresetQuestions } from "@/components/chat-preset-questions";
import {
  Conversation,
  ConversationContent,
  ConversationScrollButton,
} from "@/components/ai-elements/conversation";
import { CollapsedSidebarActions } from "@/components/sidebar/collapsed-sidebar-actions";
import { ConversationList } from "@/components/sidebar/conversation-list";
import { MobileConversationMenu } from "@/components/sidebar/mobile-menu";
import { SidebarActions } from "@/components/sidebar/sidebar-actions";
import { SidebarBrandHeader } from "@/components/sidebar/sidebar-brand-header";
import { SidebarFrame } from "@/components/sidebar/sidebar-frame";
import { useConversations } from "@/contexts/conversations-context";
import { useConversationMessages } from "@/hooks/use-conversation-messages";
import { useMarvinChat } from "@/hooks/use-marvin-chat";
import { useMarvinConfig } from "@/hooks/use-marvin-config";
import { useSidebarCollapsed } from "@/hooks/use-sidebar-collapsed";
import { CHAT_COLUMN } from "@/lib/constants";
import { pruneOrphanedAssistantPrefixes } from "@/lib/message-parts";
import { cn } from "@/lib/utils";
import { PRESET_QUESTIONS } from "@/lib/chat-suggestions";
import { nanoid } from "nanoid";
import { FormEvent, useCallback, useState } from "react";

interface MarvinChatProps {
  conversationId: string;
  onConversationIdChange: (id: string) => void;
}

export function MarvinChat({
  conversationId,
  onConversationIdChange,
}: MarvinChatProps) {
  const [input, setInput] = useState("");
  const { config, model, setModel } = useMarvinConfig();
  const { refresh, setSearchQuery } = useConversations();
  const { collapsed: sidebarCollapsed, setCollapsed: setSidebarCollapsed } =
    useSidebarCollapsed();

  const {
    messages,
    sendMessage,
    status,
    stop,
    setMessages,
    regenerate,
    error,
    clearError,
    addToolApprovalResponse,
    isBusy,
  } = useMarvinChat({
    conversationId,
    model,
    onChatComplete: refresh,
  });

  const { isLoadingMessages } = useConversationMessages({
    conversationId,
    setMessages,
    clearError,
  });

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const text = input.trim();
    if (!text || isBusy) {
      return;
    }
    sendMessage({ text });
    setInput("");
  };

  const handlePresetSelect = (prompt: string) => {
    if (isBusy) {
      return;
    }
    sendMessage({ text: prompt });
  };

  const handleNewChat = useCallback(() => {
    setInput("");
    onConversationIdChange(nanoid());
  }, [onConversationIdChange]);

  const handleCollapseSidebar = useCallback(() => {
    setSearchQuery("");
    setSidebarCollapsed(true);
  }, [setSearchQuery, setSidebarCollapsed]);

  const handleExpandSidebar = useCallback(() => {
    setSidebarCollapsed(false);
  }, [setSidebarCollapsed]);

  const handleSelectConversation = useCallback(
    (id: string) => {
      setInput("");
      onConversationIdChange(id);
    },
    [onConversationIdChange]
  );

  const handleRegenerate = useCallback(
    (messageId: string) => {
      const pruned = pruneOrphanedAssistantPrefixes(messages, messageId);
      const didPrune = pruned.length !== messages.length;

      if (didPrune) {
        setMessages(pruned);
        queueMicrotask(() => {
          regenerate({ messageId }).catch(() => {});
        });
        return;
      }

      // User feedback for clipboard/regenerate failures is deferred.
      regenerate({ messageId }).catch(() => {});
    },
    [messages, regenerate, setMessages]
  );

  const handleRetry = useCallback(() => {
    clearError();
    const lastAssistant = [...messages].reverse().find((m) => m.role === "assistant");
    if (lastAssistant) {
      regenerate({ messageId: lastAssistant.id }).catch(() => {});
    }
  }, [clearError, messages, regenerate]);

  return (
    <div className="flex h-full min-h-0 flex-1">
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-10 hidden flex-col border-r bg-background transition-[width] duration-200 md:flex",
          sidebarCollapsed ? "w-14" : "w-72"
        )}
      >
        <SidebarFrame collapsed={sidebarCollapsed}>
          {sidebarCollapsed ? (
            <CollapsedSidebarActions
              onExpand={handleExpandSidebar}
              onNew={handleNewChat}
            />
          ) : (
            <>
              <SidebarBrandHeader onCollapse={handleCollapseSidebar} />
              <SidebarActions onNew={handleNewChat} />
              <ConversationList
                activeId={conversationId}
                onNew={handleNewChat}
                onSelect={handleSelectConversation}
              />
            </>
          )}
        </SidebarFrame>
      </aside>

      <div
        className={cn(
          "flex min-h-0 min-w-0 flex-1 flex-col transition-[padding] duration-200",
          sidebarCollapsed ? "md:pl-14" : "md:pl-72"
        )}
      >
        <div className="flex shrink-0 items-center gap-2 border-b px-4 py-3 md:hidden">
          <MobileConversationMenu
            activeId={conversationId}
            onNew={handleNewChat}
            onSelect={handleSelectConversation}
          />
          <span className="font-medium text-sm">Marvin</span>
        </div>

        <Conversation className="min-h-0 flex-1">
          <ConversationContent className="gap-0 p-0">
            <ChatMessageList
              error={error}
              isLoadingMessages={isLoadingMessages}
              messages={messages}
              onApprovalResponse={addToolApprovalResponse}
              onRegenerate={handleRegenerate}
              onRetry={handleRetry}
              status={status}
            />
          </ConversationContent>
          <ConversationScrollButton />
        </Conversation>

        <div className="shrink-0 bg-gradient-to-t from-background via-background to-transparent px-4 pb-4 pt-2">
          <div className={CHAT_COLUMN}>
            {messages.length === 0 && !isLoadingMessages && (
              <ChatPresetQuestions
                disabled={isBusy}
                onSelect={handlePresetSelect}
                questions={PRESET_QUESTIONS}
              />
            )}

            <ChatComposer
              config={config}
              input={input}
              isBusy={isBusy}
              model={model}
              onInputChange={setInput}
              onModelChange={setModel}
              onStop={stop}
              onSubmit={handleSubmit}
            />

            <p className="mt-3 text-center text-muted-foreground text-xs">
              Marvin is AI and can make mistakes. Verify important financial
              decisions.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
