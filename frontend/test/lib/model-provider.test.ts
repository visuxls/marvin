import {
  groupModelsByProvider,
  providerGroupLabel,
  providerKey,
  providerLogoSlug,
} from "@/lib/model-provider";

describe("model-provider", () => {
  describe("providerKey", () => {
    it("strips openrouter prefix and returns the provider segment", () => {
      expect(providerKey("openrouter:anthropic/claude-sonnet")).toBe(
        "anthropic",
      );
    });

    it("handles ids without a prefix", () => {
      expect(providerKey("openai/gpt-4.1")).toBe("openai");
    });

    it("returns the full id when there is no slash", () => {
      expect(providerKey("custom-model")).toBe("custom-model");
    });
  });

  describe("providerLogoSlug", () => {
    it("maps OpenRouter aliases to models.dev slugs", () => {
      expect(providerLogoSlug("openrouter:x-ai/grok-4.5")).toBe("xai");
      expect(providerLogoSlug("z-ai/glm-5.2")).toBe("zai");
    });

    it("passes through known providers unchanged", () => {
      expect(providerLogoSlug("anthropic/claude-sonnet")).toBe("anthropic");
    });
  });

  describe("providerGroupLabel", () => {
    it("returns friendly labels for known providers", () => {
      expect(providerGroupLabel("openrouter:anthropic/claude")).toBe(
        "Anthropic",
      );
      expect(providerGroupLabel("x-ai/grok")).toBe("xAI");
    });

    it("title-cases unknown providers", () => {
      expect(providerGroupLabel("acme/widget")).toBe("Acme");
    });
  });

  describe("groupModelsByProvider", () => {
    it("groups models by provider and preserves order", () => {
      const groups = groupModelsByProvider([
        { id: "anthropic/a", name: "A", builtinTools: [] },
        { id: "openai/b", name: "B", builtinTools: [] },
        { id: "anthropic/c", name: "C", builtinTools: [] },
      ]);

      expect(groups).toEqual([
        {
          key: "anthropic",
          label: "Anthropic",
          models: [
            { id: "anthropic/a", name: "A", builtinTools: [] },
            { id: "anthropic/c", name: "C", builtinTools: [] },
          ],
        },
        {
          key: "openai",
          label: "OpenAI",
          models: [{ id: "openai/b", name: "B", builtinTools: [] }],
        },
      ]);
    });
  });
});
