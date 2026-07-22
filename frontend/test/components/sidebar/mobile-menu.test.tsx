import { MobileConversationMenu } from "@/components/sidebar/mobile-menu";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactNode } from "react";

vi.mock("@/contexts/conversations-context", () => ({
  useConversations: () => ({
    isLoading: false,
    isEmpty: false,
    noMatches: false,
    pinnedEntries: [],
    recentEntries: [
      {
        id: "c1",
        title: "First chat",
        createdAt: Date.now(),
        pinned: false,
      },
    ],
    pinConversation: vi.fn(),
    deleteConversation: vi.fn(),
    searchQuery: "",
    setSearchQuery: vi.fn(),
    searchOpen: false,
    setSearchOpen: vi.fn(),
  }),
}));

vi.mock("@/components/ui/sheet", () => {
  const React = require("react") as typeof import("react");
  const Ctx = React.createContext({
    open: false,
    setOpen: (_: boolean) => {},
  });

  function Sheet({
    open,
    onOpenChange,
    children,
  }: {
    open?: boolean;
    onOpenChange?: (open: boolean) => void;
    children: ReactNode;
  }) {
    const [internalOpen, setInternalOpen] = React.useState(false);
    const isOpen = open ?? internalOpen;
    const setOpen = onOpenChange ?? setInternalOpen;
    return (
      <Ctx.Provider value={{ open: isOpen, setOpen }}>{children}</Ctx.Provider>
    );
  }

  function SheetTrigger({
    render,
    ...props
  }: {
    render: React.ReactElement<{
      onClick?: () => void;
      "aria-label"?: string;
    }>;
    "aria-label"?: string;
  }) {
    const { setOpen } = React.useContext(Ctx);
    return React.cloneElement(render, {
      ...props,
      onClick: () => setOpen(true),
    });
  }

  function SheetContent({ children }: { children: ReactNode }) {
    const { open } = React.useContext(Ctx);
    if (!open) {
      return null;
    }
    return <div role="dialog">{children}</div>;
  }

  function SheetTitle({ children }: { children: ReactNode }) {
    return <h2>{children}</h2>;
  }

  return { Sheet, SheetTrigger, SheetContent, SheetTitle };
});

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

describe("MobileConversationMenu", () => {
  it("opens the sheet and closes after selecting a conversation", async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();

    render(
      <MobileConversationMenu
        activeId="new"
        onNew={vi.fn()}
        onSelect={onSelect}
      />
    );

    await user.click(screen.getByRole("button", { name: "Open conversations" }));
    expect(screen.getByRole("dialog")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /First chat/i }));
    expect(onSelect).toHaveBeenCalledWith("c1");
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("closes the sheet after starting a new chat", async () => {
    const user = userEvent.setup();
    const onNew = vi.fn();

    render(
      <MobileConversationMenu
        activeId="c1"
        onNew={onNew}
        onSelect={vi.fn()}
      />
    );

    await user.click(screen.getByRole("button", { name: "Open conversations" }));
    await user.click(screen.getByRole("button", { name: /New Chat/i }));

    expect(onNew).toHaveBeenCalled();
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
});
