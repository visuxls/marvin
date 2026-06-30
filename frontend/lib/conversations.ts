import type { UIMessage } from "ai";

import { apiUrl } from "@/lib/marvin-api";

export interface ConversationEntry {
  id: string;
  title: string;
  createdAt: number;
  pinned?: boolean;
}

export function filterConversations(
  entries: ConversationEntry[],
  query: string
): ConversationEntry[] {
  const trimmed = query.trim().toLowerCase();
  if (!trimmed) {
    return entries;
  }
  return entries.filter((entry) =>
    entry.title.toLowerCase().includes(trimmed)
  );
}

export async function listConversations(): Promise<ConversationEntry[]> {
  try {
    const response = await fetch(apiUrl("/api/conversations"));
    if (!response.ok) {
      return [];
    }
    return (await response.json()) as ConversationEntry[];
  } catch {
    return [];
  }
}

export async function fetchConversationMessages(
  conversationId: string
): Promise<UIMessage[]> {
  try {
    const response = await fetch(
      apiUrl(`/api/conversations/${encodeURIComponent(conversationId)}/messages`)
    );
    if (!response.ok) {
      return [];
    }
    const payload = (await response.json()) as { messages: UIMessage[] };
    return payload.messages.filter((message) => message.role !== "system");
  } catch {
    return [];
  }
}

export async function updateConversation(
  id: string,
  partial: Partial<Pick<ConversationEntry, "title" | "pinned">>
): Promise<boolean> {
  try {
    const response = await fetch(apiUrl(`/api/conversations/${encodeURIComponent(id)}`), {
      body: JSON.stringify(partial),
      headers: { "Content-Type": "application/json" },
      method: "PATCH",
    });
    return response.ok;
  } catch {
    return false;
  }
}

export async function togglePinConversation(
  id: string,
  currentlyPinned: boolean
): Promise<boolean> {
  return updateConversation(id, { pinned: !currentlyPinned });
}

export async function deleteConversation(id: string): Promise<boolean> {
  try {
    const response = await fetch(apiUrl(`/api/conversations/${encodeURIComponent(id)}`), {
      method: "DELETE",
    });
    return response.ok;
  } catch {
    return false;
  }
}
