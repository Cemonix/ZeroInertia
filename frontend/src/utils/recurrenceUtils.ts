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
 * Numeric indices for JavaScript days (for iteration).
 */
export const JS_WEEKDAY_INDICES = [0, 1, 2, 3, 4, 5, 6];
