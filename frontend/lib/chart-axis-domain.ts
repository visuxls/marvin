/**
 * Y-axis domain that emphasizes movement when values cluster together.
 */
export function netWorthYAxisDomain(values: number[]): [number, number] {
  if (values.length === 0) {
    return [0, 1];
  }

  const min = Math.min(...values);
  const max = Math.max(...values);
  const spread = max - min;

  if (spread === 0) {
    const cushion = Math.max(Math.abs(min) * 0.02, 1_000);
    return [min - cushion, max + cushion];
  }

  const padding = spread * 0.15;
  return [min - padding, max + padding];
}
