"use client";

import {
  deleteConversation as deleteConversationApi,
  filterConversations,
  listConversations,
  togglePinConversation,
  type ConversationEntry,
} from "@/lib/conversations";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

interface ConversationsContextValue {
  entries: ConversationEntry[];
  filteredEntries: ConversationEntry[];
  pinnedEntries: ConversationEntry[];
  recentEntries: ConversationEntry[];
  isLoading: boolean;
  isEmpty: boolean;
  noMatches: boolean;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  refresh: () => Promise<void>;
  pinConversation: (id: string, currentlyPinned: boolean) => Promise<void>;
  deleteConversation: (id: string) => Promise<void>;
}

const ConversationsContext = createContext<ConversationsContextValue | null>(
  null
);

export function ConversationsProvider({ children }: { children: ReactNode }) {
  const [entries, setEntries] = useState<ConversationEntry[]>([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  const refresh = useCallback(async () => {
    setEntries(await listConversations());
    setIsLoading(false);
  }, []);

  useEffect(() => {
    let cancelled = false;

    void listConversations().then((data) => {
      if (!cancelled) {
        setEntries(data);
        setIsLoading(false);
      }
    });

    return () => {
      cancelled = true;
    };
  }, []);

  const pinConversation = useCallback(
    async (id: string, currentlyPinned: boolean) => {
      await togglePinConversation(id, currentlyPinned);
      await refresh();
    },
    [refresh]
  );

  const deleteConversation = useCallback(
    async (id: string) => {
      await deleteConversationApi(id);
      await refresh();
    },
    [refresh]
  );

  const filteredEntries = useMemo(
    () => filterConversations(entries, searchQuery),
    [entries, searchQuery]
  );

  const pinnedEntries = useMemo(
    () => filteredEntries.filter((entry) => entry.pinned),
    [filteredEntries]
  );

  const recentEntries = useMemo(
    () => filteredEntries.filter((entry) => !entry.pinned),
    [filteredEntries]
  );

  const isEmpty = entries.length === 0;
  const noMatches = !isEmpty && filteredEntries.length === 0;

  const value = useMemo<ConversationsContextValue>(
    () => ({
      entries,
      filteredEntries,
      pinnedEntries,
      recentEntries,
      isLoading,
      isEmpty,
      noMatches,
      searchQuery,
      setSearchQuery,
      refresh,
      pinConversation,
      deleteConversation,
    }),
    [
      entries,
      filteredEntries,
      pinnedEntries,
      recentEntries,
      isLoading,
      isEmpty,
      noMatches,
      searchQuery,
      refresh,
      pinConversation,
      deleteConversation,
    ]
  );

  return (
    <ConversationsContext.Provider value={value}>
      {children}
    </ConversationsContext.Provider>
  );
}

export function useConversations(): ConversationsContextValue {
  const context = useContext(ConversationsContext);
  if (!context) {
    throw new Error("useConversations must be used within ConversationsProvider");
  }
  return context;
}
