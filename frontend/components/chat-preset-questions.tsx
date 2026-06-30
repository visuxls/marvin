"use client";

import { Suggestion, Suggestions } from "@/components/ai-elements/suggestion";
import type { PresetQuestion } from "@/lib/chat-suggestions";
import { cn } from "@/lib/utils";

interface ChatPresetQuestionsProps {
  questions: readonly PresetQuestion[];
  disabled?: boolean;
  className?: string;
  onSelect: (prompt: string) => void;
}

export function ChatPresetQuestions({
  questions,
  disabled = false,
  className,
  onSelect,
}: ChatPresetQuestionsProps) {
  return (
    <Suggestions className={cn("mb-3", className)}>
      {questions.map((question) => (
        <Suggestion
          disabled={disabled}
          key={question.id}
          onClick={onSelect}
          suggestion={question.prompt}
        >
          {question.title}
        </Suggestion>
      ))}
    </Suggestions>
  );
}
