"use client";

import { ConversationRow } from "@/components/sidebar/conversation-row";
import { useConversations } from "@/contexts/conversations-context";
import type { ConversationEntry } from "@/lib/conversations";
interface ConversationSectionProps {
  title: string;
  entries: ConversationEntry[];
  activeId: string;
  onSelect: (id: string) => void;
  onPin: (id: string, currentlyPinned: boolean) => void;
  onDelete: (id: string) => void;
}

function ConversationSection({
  title,
  entries,
  activeId,
  onSelect,
  onPin,
  onDelete,
}: ConversationSectionProps) {
  if (entries.length === 0) {
    return null;
  }

  return (
    <div className="w-full">
      <p className="px-3 pt-2 pb-1 font-semibold text-foreground text-xs">{title}</p>
      <div className="flex w-full flex-col gap-0.5">
        {entries.map((entry) => (
          <ConversationRow
            activeId={activeId}
            entry={entry}
            key={entry.id}
            onDelete={onDelete}
            onPin={onPin}
            onSelect={onSelect}
          />
        ))}
      </div>
    </div>
  );
}

interface ConversationListProps {
  activeId: string;
  onSelect: (id: string) => void;
  onNew: () => void;
}

export function ConversationList({
  activeId,
  onSelect,
  onNew,
}: ConversationListProps) {
  const {
    isLoading,
    isEmpty,
    noMatches,
    pinnedEntries,
    recentEntries,
    pinConversation,
    deleteConversation,
  } = useConversations();

  const handleDelete = async (id: string) => {
    await deleteConversation(id);
    if (id === activeId) {
      onNew();
    }
  };

  return (
    <div className="flex min-h-0 w-full flex-1 flex-col">
      <div className="min-h-0 w-full flex-1 overflow-y-auto">
        {isLoading && (
          <p className="py-8 text-center text-muted-foreground text-xs">
            Loading conversations…
          </p>
        )}

        {!isLoading && isEmpty && (
          <p className="py-8 text-center text-muted-foreground text-xs">
            No conversations yet
          </p>
        )}

        {!isLoading && noMatches && (
          <p className="py-8 text-center text-muted-foreground text-xs">
            No chats found
          </p>
        )}

        {!isLoading && !isEmpty && !noMatches && (
          <div className="flex w-full flex-col gap-4 pb-1">
            <ConversationSection
              activeId={activeId}
              entries={pinnedEntries}
              onDelete={handleDelete}
              onPin={pinConversation}
              onSelect={onSelect}
              title="Pinned"
            />
            <ConversationSection
              activeId={activeId}
              entries={recentEntries}
              onDelete={handleDelete}
              onPin={pinConversation}
              onSelect={onSelect}
              title="Recent"
            />
          </div>
        )}
      </div>
    </div>
  );
}
