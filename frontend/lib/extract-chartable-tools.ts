import { getChartableKind } from "@/lib/finance-tool-charts";
import type { ChartableTool } from "@/lib/finance-tool-types";
import { isToolPart } from "@/lib/message-parts";
import type { DynamicToolUIPart, ToolUIPart, UIMessage } from "ai";

const DEFAULT_MAX_CHARTS = 2;

function toolNameFromPart(part: ToolUIPart | DynamicToolUIPart): string {
  if (part.type === "dynamic-tool") {
    return part.toolName;
  }

  return part.type;
}

/**
 * Collect chart-eligible completed tool outputs from a message.
 */
export function extractChartableTools(
  parts: UIMessage["parts"],
  maxCharts = DEFAULT_MAX_CHARTS
): ChartableTool[] {
  const chartable: ChartableTool[] = [];

  for (const part of parts) {
    if (!isToolPart(part) || part.state !== "output-available") {
      continue;
    }

    if (!("output" in part) || part.output === undefined) {
      continue;
    }

    const toolName = toolNameFromPart(part);
    const kind = getChartableKind(toolName, part.output);
    if (!kind) {
      continue;
    }

    chartable.push({
      toolCallId: part.toolCallId,
      toolName,
      kind,
      output: part.output,
    });

    if (chartable.length >= maxCharts) {
      break;
    }
  }

  return chartable;
}
