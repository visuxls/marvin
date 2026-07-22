"use client";

import {
  fetchConfigure,
  type MarvinConfigure,
  type ReasoningEffortId,
} from "@/lib/marvin-api";
import { REASONING_EFFORT_KEY } from "@/lib/constants";
import { useEffect, useState } from "react";

function readStoredReasoningEffort(
  efforts: ReasoningEffortId[],
  fallback: ReasoningEffortId,
): ReasoningEffortId {
  const stored = localStorage.getItem(REASONING_EFFORT_KEY);
  if (stored && efforts.includes(stored as ReasoningEffortId)) {
    return stored as ReasoningEffortId;
  }
  return fallback;
}

/** Fetch Marvin configure endpoint and track model and reasoning selections. */
export function useMarvinConfig() {
  const [config, setConfig] = useState<MarvinConfigure | null>(null);
  const [model, setModel] = useState("");
  const [reasoningEffort, setReasoningEffort] =
    useState<ReasoningEffortId>("off");

  useEffect(() => {
    fetchConfigure().then((data) => {
      if (!data) {
        return;
      }
      setConfig(data);
      if (data.models.length > 0) {
        // Keep a model already restored from the active conversation.
        setModel((current) => current || data.models[0].id);
      }
      const effortIds = (data.reasoningEfforts ?? []).map((entry) => entry.id);
      setReasoningEffort(
        readStoredReasoningEffort(
          effortIds,
          data.defaultReasoningEffort ?? "off",
        ),
      );
    });
  }, []);

  const updateReasoningEffort = (effort: ReasoningEffortId) => {
    setReasoningEffort(effort);
    localStorage.setItem(REASONING_EFFORT_KEY, effort);
  };

  return {
    config,
    model,
    setModel,
    reasoningEffort,
    setReasoningEffort: updateReasoningEffort,
  };
}
