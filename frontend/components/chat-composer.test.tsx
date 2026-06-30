import { ChatComposer } from "@/components/chat-composer";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

vi.mock("@/components/theme-toggle", () => ({
  ThemeToggle: () => <button type="button">Theme</button>,
}));

vi.mock("@/components/model-icon", () => ({
  MarvinModelIcon: () => <span data-testid="model-icon" />,
}));

const config = {
  models: [
    { id: "model-a", name: "Model A", builtinTools: [] },
    { id: "model-b", name: "Model B", builtinTools: [] },
  ],
  builtinTools: [],
};

describe("ChatComposer", () => {
  it("submits trimmed input via the form", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn((event) => event.preventDefault());
    const onInputChange = vi.fn();

    render(
      <ChatComposer
        config={config}
        input="  hello  "
        isBusy={false}
        model="model-a"
        onInputChange={onInputChange}
        onModelChange={vi.fn()}
        onStop={vi.fn()}
        onSubmit={onSubmit}
      />
    );

    await user.click(screen.getByRole("button", { name: "Send" }));

    expect(onSubmit).toHaveBeenCalled();
  });

  it("disables send when input is blank", () => {
    render(
      <ChatComposer
        config={config}
        input="   "
        isBusy={false}
        model="model-a"
        onInputChange={vi.fn()}
        onModelChange={vi.fn()}
        onStop={vi.fn()}
        onSubmit={vi.fn()}
      />
    );

    expect(screen.getByRole("button", { name: "Send" })).toBeDisabled();
  });

  it("shows stop control while busy", async () => {
    const user = userEvent.setup();
    const onStop = vi.fn();

    render(
      <ChatComposer
        config={config}
        input="working"
        isBusy={true}
        model="model-a"
        onInputChange={vi.fn()}
        onModelChange={vi.fn()}
        onStop={onStop}
        onSubmit={vi.fn()}
      />
    );

    await user.click(screen.getByRole("button", { name: "Stop" }));
    expect(onStop).toHaveBeenCalled();
  });

  it("submits on Enter without Shift", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn((event) => event.preventDefault());

    render(
      <ChatComposer
        config={config}
        input="hello"
        isBusy={false}
        model="model-a"
        onInputChange={vi.fn()}
        onModelChange={vi.fn()}
        onStop={vi.fn()}
        onSubmit={onSubmit}
      />
    );

    const textarea = screen.getByPlaceholderText("Ask Marvin");
    await user.click(textarea);
    await user.keyboard("{Enter}");

    expect(onSubmit).toHaveBeenCalled();
  });
});
