import { ConversationList } from "@/components/sidebar/conversation-list";
import { SidebarActions } from "@/components/sidebar/sidebar-actions";
import { listConversations } from "@/lib/conversations";
import { renderWithProviders } from "@/test/test-utils";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

vi.mock("@/lib/conversations", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@/lib/conversations")>();
  return {
    ...actual,
    listConversations: vi.fn(),
  };
});

describe("SidebarActions", () => {
  beforeEach(() => {
    vi.mocked(listConversations).mockResolvedValue([]);
  });

  it("calls onNew when New Chat is clicked", async () => {
    const onNew = vi.fn();
    const user = userEvent.setup();

    renderWithProviders(<SidebarActions onNew={onNew} />);

    await user.click(screen.getByRole("button", { name: "New chat" }));

    expect(onNew).toHaveBeenCalledOnce();
  });

  it("collapses search and calls onNew when New Chat is clicked while searching", async () => {
    const onNew = vi.fn();
    const user = userEvent.setup();

    renderWithProviders(<SidebarActions onNew={onNew} />);

    await user.click(screen.getByRole("button", { name: "Search chats" }));
    expect(screen.getByPlaceholderText("Search chats…")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "New chat" }));

    expect(onNew).toHaveBeenCalledOnce();
    expect(screen.queryByPlaceholderText("Search chats…")).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "New chat" })).toHaveTextContent(
      "New Chat"
    );
  });

  it("toggles search input visibility", async () => {
    const user = userEvent.setup();

    renderWithProviders(<SidebarActions onNew={vi.fn()} />);

    expect(screen.queryByPlaceholderText("Search chats…")).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Search chats" }));

    expect(screen.getByPlaceholderText("Search chats…")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Search chats" }));

    expect(screen.queryByPlaceholderText("Search chats…")).not.toBeInTheDocument();
  });

  it("filters conversations via search", async () => {
    vi.mocked(listConversations).mockResolvedValue([
      { id: "1", title: "Alpha", createdAt: 1 },
      { id: "2", title: "Beta", createdAt: 2 },
    ]);

    const user = userEvent.setup();

    renderWithProviders(
      <>
        <SidebarActions onNew={vi.fn()} />
        <ConversationList activeId="1" onNew={vi.fn()} onSelect={vi.fn()} />
      </>
    );

    await waitFor(() => {
      expect(screen.getByText("Alpha")).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: "Search chats" }));
    await user.type(screen.getByPlaceholderText("Search chats…"), "beta");

    expect(screen.queryByText("Alpha")).not.toBeInTheDocument();
    expect(screen.getByText("Beta")).toBeInTheDocument();
  });
});
