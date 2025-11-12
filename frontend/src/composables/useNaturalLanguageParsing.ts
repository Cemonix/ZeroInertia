import * as chrono from 'chrono-node';

export interface ParsedDateResult {
    date: Date | null;
    originalText: string;
    matchedText: string;
    cleanedText: string;
    // Optional duration (in minutes) when phrases like "for 15 minutes" are present
    durationMinutes?: number | null;
    matchedDurationText?: string;
}

/**
 * Parse natural language date/time expressions from text
 *
 * Examples:
 * - "tomorrow at 3pm" -> Tomorrow at 15:00
 * - "next Monday 9am" -> Next Monday at 09:00
 * - "in 2 weeks" -> Date 2 weeks from now
 * - "Jan 15 at 2:30pm" -> January 15 at 14:30
 */
export function useNaturalLanguageParsing() {
    // Expand simple shorthands to improve chrono recognition
    function expandShorthand(text: string): string {
        if (!text) return text;
        // Replace standalone "tom" -> "tomorrow" and "tod" -> "today"
        // Case-insensitive, respect word boundaries to avoid words like "atomic"
        return text
            .replace(/\btom\b/gi, (m) => preserveCase(m, 'tomorrow'))
            .replace(/\btod\b/gi, (m) => preserveCase(m, 'today'));
    }

    function preserveCase(source: string, replacement: string): string {
        if (source.toUpperCase() === source) return replacement.toUpperCase();
        if (source[0] === source[0].toUpperCase()) {
            return replacement[0].toUpperCase() + replacement.slice(1);
        }
        return replacement;
    }
    /**
     * Parse a date/time from text and return the parsed result
     */
    function parseTaskDate(text: string): ParsedDateResult {
        if (!text || text.trim() === '') {
            return {
                date: null,
                originalText: text,
                matchedText: '',
                cleanedText: text,
                durationMinutes: null,
                matchedDurationText: undefined,
            };
        }

        // Use chrono to parse the date (with shorthand expansion)
        const expanded = expandShorthand(text);
        const results = chrono.parse(expanded);

        if (results.length === 0) {
            return {
                date: null,
                originalText: text,
                matchedText: '',
                cleanedText: text,
                durationMinutes: null,
                matchedDurationText: undefined,
            };
        }

        // Get the first match
        const match = results[0];
        const parsedDate = match.start.date();
        const matchedText = match.text;

        // Try to extract a trailing duration phrase like "for 15 minutes", "for 1h 30m", etc.
        // Supports: h/hr/hrs/hour/hours and m/min/mins/minute/minutes; also decimals like 1.5h
        const durationRegex = /\bfor\s+(?:(?<hours>\d+(?:[\.,]\d+)?)\s*(?:h|hr|hrs|hour|hours))?\s*(?:(?<minutes>\d+)\s*(?:m|min|mins|minute|minutes))?/i;
        const durMatch = text.match(durationRegex);
        let durationMinutes: number | null = null;
        let matchedDurationText: string | undefined = undefined;
        if (durMatch) {
            const rawH = durMatch.groups?.hours;
            const rawM = durMatch.groups?.minutes;
            const hours = rawH ? parseFloat(rawH.replace(',', '.')) : 0;
            const minutes = rawM ? parseInt(rawM, 10) : 0;
            const total = Math.round(hours * 60 + minutes);
            if (total > 0) {
                durationMinutes = total;
                matchedDurationText = durMatch[0];
            }
        }

        // Remove the matched date text (and duration text if present) from the original text
        let cleanedText = text.replace(matchedText, '').trim();
        if (matchedDurationText) {
            cleanedText = cleanedText.replace(matchedDurationText, '').trim();
        }

        return {
            date: parsedDate,
            originalText: text,
            matchedText,
            cleanedText,
            durationMinutes,
            matchedDurationText,
        };
    }

    /**
     * Check if text contains a date expression
     */
    function containsDate(text: string): boolean {
        if (!text || text.trim() === '') return false;
        const results = chrono.parse(expandShorthand(text));
        return results.length > 0;
    }

    /**
     * Get all date matches from text (useful for recurring tasks or multiple dates)
     */
    function parseAllDates(text: string): ParsedDateResult[] {
        if (!text || text.trim() === '') return [];

        const results = chrono.parse(expandShorthand(text));

        return results.map(match => ({
            date: match.start.date(),
            originalText: text,
            matchedText: match.text,
            cleanedText: text.replace(match.text, '').trim()
        }));
    }

    return {
        parseTaskDate,
        containsDate,
        parseAllDates
    };
}
