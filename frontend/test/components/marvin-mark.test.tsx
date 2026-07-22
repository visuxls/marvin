import { MarvinMark } from "@/components/marvin-mark";
import { render, screen } from "@testing-library/react";

describe("MarvinMark", () => {
  it("renders the brand mark SVG", () => {
    render(<MarvinMark className="size-8" />);

    const mark = screen.getByTestId("marvin-mark");
    expect(mark).toBeInTheDocument();
    expect(mark).toHaveAttribute("aria-hidden");
    expect(mark).toHaveClass("size-8");
  });
});
