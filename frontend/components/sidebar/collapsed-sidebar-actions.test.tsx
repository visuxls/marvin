import { CollapsedSidebarActions } from "@/components/sidebar/collapsed-sidebar-actions";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

describe("CollapsedSidebarActions", () => {
  it("calls onExpand when expand is clicked", async () => {
    const onExpand = vi.fn();
    const user = userEvent.setup();

    render(<CollapsedSidebarActions onExpand={onExpand} onNew={vi.fn()} />);

    await user.click(screen.getByRole("button", { name: "Expand sidebar" }));

    expect(onExpand).toHaveBeenCalledOnce();
  });

  it("calls onNew when new chat is clicked", async () => {
    const onNew = vi.fn();
    const user = userEvent.setup();

    render(<CollapsedSidebarActions onExpand={vi.fn()} onNew={onNew} />);

    await user.click(screen.getByRole("button", { name: "New chat" }));

    expect(onNew).toHaveBeenCalledOnce();
  });
});
