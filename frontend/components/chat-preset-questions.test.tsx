import { ChatPresetQuestions } from "@/components/chat-preset-questions";
import { PRESET_QUESTIONS } from "@/lib/chat-suggestions";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

vi.mock("@/components/ai-elements/suggestion", () => ({
  Suggestions: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="suggestions">{children}</div>
  ),
  Suggestion: ({
    children,
    suggestion,
    onClick,
    disabled,
  }: {
    children?: React.ReactNode;
    suggestion: string;
    onClick?: (suggestion: string) => void;
    disabled?: boolean;
  }) => (
    <button
      disabled={disabled}
      onClick={() => onClick?.(suggestion)}
      type="button"
    >
      {children ?? suggestion}
    </button>
  ),
}));

describe("ChatPresetQuestions", () => {
  it("renders preset question cards", () => {
    render(
      <ChatPresetQuestions
        onSelect={vi.fn()}
        questions={PRESET_QUESTIONS}
      />
    );

    expect(screen.getByText("Financial health check")).toBeInTheDocument();
    expect(screen.getByText("Am I growing?")).toBeInTheDocument();
    expect(screen.getByText("Concentration & risk")).toBeInTheDocument();
    expect(screen.getByText("Where is my money?")).toBeInTheDocument();
  });

  it("sends the full prompt when a card is clicked", async () => {
    const user = userEvent.setup();
    const onSelect = vi.fn();

    render(
      <ChatPresetQuestions
        onSelect={onSelect}
        questions={PRESET_QUESTIONS}
      />
    );

    await user.click(screen.getByRole("button", { name: /Financial health check/i }));

    expect(onSelect).toHaveBeenCalledWith(PRESET_QUESTIONS[0].prompt);
  });

  it("disables cards when busy", () => {
    render(
      <ChatPresetQuestions
        disabled
        onSelect={vi.fn()}
        questions={PRESET_QUESTIONS}
      />
    );

    expect(screen.getAllByRole("button")).toHaveLength(PRESET_QUESTIONS.length);
    for (const button of screen.getAllByRole("button")) {
      expect(button).toBeDisabled();
    }
  });
});
