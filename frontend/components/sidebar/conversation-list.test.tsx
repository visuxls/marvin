import { ConversationList } from "@/components/sidebar/conversation-list";
import { listConversations } from "@/lib/conversations";
import { renderWithProviders } from "@/test/test-utils";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";

vi.mock("@/components/ui/dropdown-menu", () => ({
  DropdownMenu: ({ children }: { children: ReactNode }) => <div>{children}</div>,
  DropdownMenuTrigger: ({
    children,
    ...props
  }: React.ButtonHTMLAttributes<HTMLButtonElement> & { children: ReactNode }) => (
    <button type="button" {...props}>
      {children}
    </button>
  ),
  DropdownMenuContent: ({ children }: { children: ReactNode }) => (
    <div role="menu">{children}</div>
  ),
  DropdownMenuItem: ({
    children,
    onClick,
  }: {
    children: ReactNode;
    onClick?: () => void;
  }) => (
    <button role="menuitem" type="button" onClick={onClick}>
      {children}
    </button>
  ),
}));

vi.mock("@/lib/conversations", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/lib/conversations")>();
  return {
    ...actual,
    listConversations: vi.fn(),
    deleteConversation: vi.fn().mockResolvedValue(true),
    togglePinConversation: vi.fn().mockResolvedValue(true),
  };
});

describe("ConversationList", () => {
  it("shows loading then conversation sections", async () => {
    vi.mocked(listConversations).mockResolvedValue([
      { id: "1", title: "Pinned chat", createdAt: 1, pinned: true },
      { id: "2", title: "Recent chat", createdAt: 2 },
    ]);

    renderWithProviders(
      <ConversationList activeId="2" onNew={vi.fn()} onSelect={vi.fn()} />
    );

    expect(screen.getByText("Loading conversations…")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText("Pinned")).toBeInTheDocument();
    });

    expect(screen.getByText("Pinned chat")).toBeInTheDocument();
    expect(screen.getByText("Recent chat")).toBeInTheDocument();
  });

  it("shows empty state when there are no conversations", async () => {
    vi.mocked(listConversations).mockResolvedValue([]);

    renderWithProviders(
      <ConversationList activeId="x" onNew={vi.fn()} onSelect={vi.fn()} />
    );

    await waitFor(() => {
      expect(screen.getByText("No conversations yet")).toBeInTheDocument();
    });
  });

  it("starts a new chat when deleting the active conversation", async () => {
    vi.mocked(listConversations).mockResolvedValue([
      { id: "active", title: "Active chat", createdAt: Date.now() - 60_000 },
    ]);

    const onNew = vi.fn();
    const user = userEvent.setup();

    renderWithProviders(
      <ConversationList activeId="active" onNew={onNew} onSelect={vi.fn()} />
    );

    await waitFor(() => {
      expect(screen.getByText("Active chat")).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: "Conversation options" }));
    await user.click(screen.getByRole("menuitem", { name: /Delete/i }));

    await waitFor(() => {
      expect(onNew).toHaveBeenCalled();
    });
  });
});
