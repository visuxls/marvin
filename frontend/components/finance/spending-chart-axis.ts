/**
 * Horizontal axis width for spending category labels.
 */
export function spendingCategoryAxisWidth(categories: string[]): number {
  const longestLabelLength = categories.reduce(
    (max, category) => Math.max(max, category.length),
    0
  )

  return Math.min(112, Math.max(72, Math.ceil(longestLabelLength * 6.5) + 8))
}
