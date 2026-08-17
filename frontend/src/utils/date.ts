export function formatDateTime(
  value: string | null,
): string {
  if (!value) {
    return "—";
  }

  const hasTimezone =
    value.endsWith("Z") ||
    /[+-]\d{2}:\d{2}$/.test(value);

  const normalizedValue = hasTimezone
    ? value
    : `${value}Z`;

  const date = new Date(normalizedValue);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return new Intl.DateTimeFormat("en-GB", {
    dateStyle: "medium",
    timeStyle: "medium",
  }).format(date);
}
