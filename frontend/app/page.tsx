"use client";

import { MarvinChat } from "@/components/marvin-chat";
import { ConversationsProvider } from "@/contexts/conversations-context";
import { useActiveConversation } from "@/hooks/use-active-conversation";

function MarvinApp() {
  const { conversationId, setConversationId } = useActiveConversation();

  return (
    <MarvinChat
      conversationId={conversationId}
      onConversationIdChange={setConversationId}
    />
  );
}

export default function Home() {
  return (
    <div className="flex h-svh flex-col bg-background">
      <ConversationsProvider>
        <MarvinApp />
      </ConversationsProvider>
    </div>
  );
}
