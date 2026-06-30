import { ConversationRow } from "@/components/sidebar/conversation-row";
import { render, screen } from "@testing-library/react";
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

describe("ConversationRow", () => {
  const entry = {
    id: "conv-1",
    title: "Net worth check",
    createdAt: Date.now() - 60_000,
  };

  it("selects a conversation on row click", async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();

    render(
      <ConversationRow
        activeId="other"
        entry={entry}
        onDelete={vi.fn()}
        onPin={vi.fn()}
        onSelect={onSelect}
      />
    );

    await user.click(screen.getByRole("button", { name: /Net worth check/i }));
    expect(onSelect).toHaveBeenCalledWith("conv-1");
  });

  it("highlights the active conversation", () => {
    render(
      <ConversationRow
        activeId="conv-1"
        entry={entry}
        onDelete={vi.fn()}
        onPin={vi.fn()}
        onSelect={vi.fn()}
      />
    );

    expect(screen.getByRole("button", { name: /Net worth check/i })).toHaveClass(
      "bg-sidebar-accent"
    );
  });

  it("pins and deletes from the options menu", async () => {
    const user = userEvent.setup();
    const onPin = vi.fn();
    const onDelete = vi.fn();

    render(
      <ConversationRow
        activeId="other"
        entry={entry}
        onDelete={onDelete}
        onPin={onPin}
        onSelect={vi.fn()}
      />
    );

    await user.click(screen.getByRole("button", { name: "Conversation options" }));
    await user.click(screen.getByRole("menuitem", { name: /Pin/i }));
    expect(onPin).toHaveBeenCalledWith("conv-1", false);

    await user.click(screen.getByRole("button", { name: "Conversation options" }));
    await user.click(screen.getByRole("menuitem", { name: /Delete/i }));
    expect(onDelete).toHaveBeenCalledWith("conv-1");
  });

  it("shows Unpin for pinned conversations", async () => {
    const user = userEvent.setup();

    render(
      <ConversationRow
        activeId="other"
        entry={{ ...entry, pinned: true }}
        onDelete={vi.fn()}
        onPin={vi.fn()}
        onSelect={vi.fn()}
      />
    );

    await user.click(screen.getByRole("button", { name: "Conversation options" }));
    expect(screen.getByRole("menuitem", { name: /Unpin/i })).toBeInTheDocument();
  });
});
