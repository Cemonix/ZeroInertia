/**
 * Utilities for handling recurring task day numbering conversions between
 * JavaScript (0=Sunday) and Python (0=Monday) conventions.
 */

/**
 * Convert from JavaScript's Date.getDay() convention (0=Sunday) to Python's
 * date.weekday() convention (0=Monday).
 *
 * JavaScript: 0=Sun, 1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat
 * Python:     0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
 *
 * @param jsDayIndex - Day index using JavaScript's convention (0-6, 0=Sunday)
 * @returns Day index using Python's convention (0-6, 0=Monday)
 */
export function jsDayToPythonDay(jsDayIndex: number): number {
    if (jsDayIndex < 0 || jsDayIndex > 6) {
        throw new Error(`Invalid day index: ${jsDayIndex}. Must be 0-6.`);
    }
    // Sunday (0 in JS) becomes 6 in Python
    // Monday (1 in JS) becomes 0 in Python
    // ... and so on
    return jsDayIndex === 0 ? 6 : jsDayIndex - 1;
}

/**
 * Convert from Python's date.weekday() convention (0=Monday) to JavaScript's
 * Date.getDay() convention (0=Sunday).
 *
 * Python:     0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
 * JavaScript: 0=Sun, 1=Mon, 2=Tue, 3=Wed, 4=Thu, 5=Fri, 6=Sat
 *
 * @param pythonDayIndex - Day index using Python's convention (0-6, 0=Monday)
 * @returns Day index using JavaScript's convention (0-6, 0=Sunday)
 */
export function pythonDayToJsDay(pythonDayIndex: number): number {
    if (pythonDayIndex < 0 || pythonDayIndex > 6) {
        throw new Error(`Invalid day index: ${pythonDayIndex}. Must be 0-6.`);
    }
    // Monday (0 in Python) becomes 1 in JS
    // Sunday (6 in Python) becomes 0 in JS
    return pythonDayIndex === 6 ? 0 : pythonDayIndex + 1;
}

/**
 * Convert an array of JavaScript day indices to Python day indices.
 * @param jsDays - Array of day indices using JavaScript's convention
 * @returns Array of day indices using Python's convention, sorted
 */
export function jsDaysToPythonDays(jsDays: number[]): number[] {
    return jsDays.map(jsDayToPythonDay).sort((a, b) => a - b);
}

/**
 * Convert an array of Python day indices to JavaScript day indices.
 * @param pythonDays - Array of day indices using Python's convention
 * @returns Array of day indices using JavaScript's convention, sorted
 */
export function pythonDaysToJsDays(pythonDays: number[]): number[] {
    return pythonDays.map(pythonDayToJsDay).sort((a, b) => a - b);
}

/**
 * Day labels using JavaScript's convention (for UI display).
 * Array index matches JavaScript's Date.getDay() (0=Sunday).
 */
export const JS_WEEKDAY_LABELS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

/**
 * Python weekday labels (0=Monday, 6=Sunday).
 */
const PYTHON_WEEKDAY_LABELS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

/**
 * Format a recurrence pattern for display.
 *
 * Examples:
 * - "Every day"
 * - "Every 3 days"
 * - "Every week"
 * - "Every 2 weeks"
 * - "Every 2 weeks on Mon · Wed"
 * - "Every month"
 * - "Every 3 months"
 * - "Every year"
 *
 * @param interval - Number of units between recurrences
 * @param unit - Unit type (days, weeks, months, years)
 * @param pythonDays - Optional array of Python weekday indices for weekly recurrence
 * @returns Formatted recurrence string
 */
export function formatRecurrence(
    interval: number | null,
    unit: string | null,
    pythonDays: number[] | null = null
): string {
    if (!interval || !unit) {
        return "";
    }

    const isPlural = interval > 1;
    let result = `Every ${interval > 1 ? interval + " " : ""}`;

    switch (unit) {
        case "days":
            result += isPlural ? "days" : "day";
            break;
        case "weeks":
            result += isPlural ? "weeks" : "week";
            if (pythonDays && pythonDays.length > 0) {
                const dayLabels = pythonDays
                    .map((day) => PYTHON_WEEKDAY_LABELS[day])
                    .join(" · ");
                result += ` on ${dayLabels}`;
            }
            break;
        case "months":
            result += isPlural ? "months" : "month";
            break;
        case "years":
            result += isPlural ? "years" : "year";
            break;
        default:
            return "";
    }

    return result;
}
