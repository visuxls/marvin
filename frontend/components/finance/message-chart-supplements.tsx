"use client";

import { extractChartableTools } from "@/lib/extract-chartable-tools";
import { resolveToolChart } from "@/lib/finance-tool-charts";
import type { UIMessage } from "ai";

interface MessageChartSupplementsProps {
  message: UIMessage;
}

/**
 * Compact charts shown after assistant prose to reinforce tool-backed advice.
 */
export function MessageChartSupplements({ message }: MessageChartSupplementsProps) {
  if (message.role !== "assistant") {
    return null;
  }

  const chartableTools = extractChartableTools(message.parts);
  if (chartableTools.length === 0) {
    return null;
  }

  return (
    <div className="w-full">
      {chartableTools.map((tool) => {
        const chart = resolveToolChart(tool.toolName, tool.output);
        if (!chart) {
          return null;
        }

        return <div key={tool.toolCallId}>{chart}</div>;
      })}
    </div>
  );
}
