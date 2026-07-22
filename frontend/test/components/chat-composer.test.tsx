import { ChatComposer } from "@/components/chat-composer";
import type { MarvinConfigure } from "@/lib/marvin-api";
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

vi.mock("@/components/theme-toggle", () => ({
  ThemeToggle: () => <button type="button">Theme</button>,
}));

const config = {
  models: [
    { id: "anthropic/model-a", name: "Model A", builtinTools: [] },
    { id: "openai/model-b", name: "Model B", builtinTools: [] },
  ],
  builtinTools: [],
  reasoningEfforts: [
    { id: "off", label: "Off" },
    { id: "high", label: "High" },
  ],
  defaultReasoningEffort: "off",
} satisfies MarvinConfigure;

const singleModelConfig = {
  ...config,
  models: [{ id: "anthropic/model-a", name: "Model A", builtinTools: [] }],
} satisfies MarvinConfigure;

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
        model="anthropic/model-a"
        onInputChange={onInputChange}
        onModelChange={vi.fn()}
        onReasoningEffortChange={vi.fn()}
        onStop={vi.fn()}
        onSubmit={onSubmit}
        reasoningEffort="off"
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
        model="anthropic/model-a"
        onInputChange={vi.fn()}
        onModelChange={vi.fn()}
        onReasoningEffortChange={vi.fn()}
        onStop={vi.fn()}
        onSubmit={vi.fn()}
        reasoningEffort="off"
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
        model="anthropic/model-a"
        onInputChange={vi.fn()}
        onModelChange={vi.fn()}
        onReasoningEffortChange={vi.fn()}
        onStop={onStop}
        onSubmit={vi.fn()}
        reasoningEffort="off"
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
        model="anthropic/model-a"
        onInputChange={vi.fn()}
        onModelChange={vi.fn()}
        onReasoningEffortChange={vi.fn()}
        onStop={vi.fn()}
        onSubmit={onSubmit}
        reasoningEffort="off"
      />
    );

    const textarea = screen.getByPlaceholderText("Ask Marvin");
    await user.click(textarea);
    await user.keyboard("{Enter}");

    expect(onSubmit).toHaveBeenCalled();
  });

  it("shows the model selector when multiple models are available", () => {
    render(
      <ChatComposer
        config={config}
        input=""
        isBusy={false}
        model="anthropic/model-a"
        onInputChange={vi.fn()}
        onModelChange={vi.fn()}
        onReasoningEffortChange={vi.fn()}
        onStop={vi.fn()}
        onSubmit={vi.fn()}
        reasoningEffort="off"
      />
    );

    expect(screen.getByRole("button", { name: /Model A/i })).toBeInTheDocument();
  });

  it("hides the model selector when only one model is available", () => {
    render(
      <ChatComposer
        config={singleModelConfig}
        input=""
        isBusy={false}
        model="anthropic/model-a"
        onInputChange={vi.fn()}
        onModelChange={vi.fn()}
        onReasoningEffortChange={vi.fn()}
        onStop={vi.fn()}
        onSubmit={vi.fn()}
        reasoningEffort="off"
      />
    );

    expect(screen.queryByRole("button", { name: /Model A/i })).not.toBeInTheDocument();
  });

  it("calls onModelChange when a model is selected", async () => {
    const user = userEvent.setup();
    const onModelChange = vi.fn();

    render(
      <ChatComposer
        config={config}
        input=""
        isBusy={false}
        model="anthropic/model-a"
        onInputChange={vi.fn()}
        onModelChange={onModelChange}
        onReasoningEffortChange={vi.fn()}
        onStop={vi.fn()}
        onSubmit={vi.fn()}
        reasoningEffort="off"
      />
    );

    await user.click(screen.getByRole("button", { name: /Model A/i }));

    const dialog = await screen.findByRole("dialog");
    await user.click(within(dialog).getByText("Model B"));

    expect(onModelChange).toHaveBeenCalledWith("openai/model-b");
  });

  it("disables the model selector while busy", () => {
    render(
      <ChatComposer
        config={config}
        input="working"
        isBusy={true}
        model="anthropic/model-a"
        onInputChange={vi.fn()}
        onModelChange={vi.fn()}
        onReasoningEffortChange={vi.fn()}
        onStop={vi.fn()}
        onSubmit={vi.fn()}
        reasoningEffort="off"
      />
    );

    expect(screen.getByRole("button", { name: /Model A/i })).toBeDisabled();
  });

  it("calls onReasoningEffortChange when an effort is selected", async () => {
    const user = userEvent.setup();
    const onReasoningEffortChange = vi.fn();

    render(
      <ChatComposer
        config={config}
        input=""
        isBusy={false}
        model="anthropic/model-a"
        onInputChange={vi.fn()}
        onModelChange={vi.fn()}
        onReasoningEffortChange={onReasoningEffortChange}
        onStop={vi.fn()}
        onSubmit={vi.fn()}
        reasoningEffort="off"
      />
    );

    await user.click(screen.getByRole("combobox"));
    await user.click(await screen.findByRole("option", { name: "High" }));

    expect(onReasoningEffortChange).toHaveBeenCalledWith("high");
  });
});
