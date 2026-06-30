"use client";

import { fetchConfigure, type MarvinConfigure } from "@/lib/marvin-api";
import { useEffect, useState } from "react";

/** Fetch Marvin configure endpoint and track the selected model. */
export function useMarvinConfig() {
  const [config, setConfig] = useState<MarvinConfigure | null>(null);
  const [model, setModel] = useState("");

  useEffect(() => {
    fetchConfigure().then((data) => {
      if (!data) {
        return;
      }
      setConfig(data);
      if (data.models.length > 0) {
        setModel(data.models[0].id);
      }
    });
  }, []);

  return { config, model, setModel };
}
