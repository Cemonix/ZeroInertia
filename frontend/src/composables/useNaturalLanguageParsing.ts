import * as chrono from 'chrono-node';

export interface ParsedDateResult {
    date: Date | null;
    originalText: string;
    matchedText: string;
    cleanedText: string;
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
    /**
     * Parse a date/time from text and return the parsed result
     */
    function parseTaskDate(text: string): ParsedDateResult {
        if (!text || text.trim() === '') {
            return {
                date: null,
                originalText: text,
                matchedText: '',
                cleanedText: text
            };
        }

        // Use chrono to parse the date
        const results = chrono.parse(text);

        if (results.length === 0) {
            return {
                date: null,
                originalText: text,
                matchedText: '',
                cleanedText: text
            };
        }

        // Get the first match
        const match = results[0];
        const parsedDate = match.start.date();
        const matchedText = match.text;

        // Remove the matched date text from the original text to get the task title
        const cleanedText = text.replace(matchedText, '').trim();

        return {
            date: parsedDate,
            originalText: text,
            matchedText,
            cleanedText
        };
    }

    /**
     * Check if text contains a date expression
     */
    function containsDate(text: string): boolean {
        if (!text || text.trim() === '') return false;
        const results = chrono.parse(text);
        return results.length > 0;
    }

    /**
     * Get all date matches from text (useful for recurring tasks or multiple dates)
     */
    function parseAllDates(text: string): ParsedDateResult[] {
        if (!text || text.trim() === '') return [];

        const results = chrono.parse(text);

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
