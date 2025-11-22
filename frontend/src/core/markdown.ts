import { marked } from "marked";
import DOMPurify from "dompurify";

/**
 * Custom marked extension for Obsidian-style wikilinks [[Note Title]]
 */
const wikiLinkExtension = {
    name: "wikilink",
    level: "inline" as const,
    start(src: string) {
        return src.indexOf("[[");
    },
    tokenizer(src: string) {
        const rule = /^\[\[([^\]]+)\]\]/;
        const match = rule.exec(src);
        if (match) {
            return {
                type: "wikilink",
                raw: match[0],
                text: match[1].trim(),
            };
        }
        return undefined;
    },
    renderer(token: { text: string }) {
        return `<span class="wikilink" data-note-title="${token.text}">${token.text}</span>`;
    },
};

// Configure marked with custom extensions
marked.use({
    extensions: [wikiLinkExtension],
    breaks: true,
});

/**
 * Parse markdown content to HTML with wikilink support
 * @param content - Raw markdown content
 * @returns Sanitized HTML
 */
export function parseMarkdown(content: string): string {
    if (!content) return "";
    const rawHtml = marked.parse(content, { async: false }) as string;
    return DOMPurify.sanitize(rawHtml);
}

/**
 * Extract all wikilink titles from markdown content
 * @param content - Raw markdown content
 * @returns Array of note titles referenced in the content
 */
export function extractWikilinks(content: string): string[] {
    const pattern = /\[\[([^\]]+)\]\]/g;
    const matches = content.matchAll(pattern);
    return Array.from(matches, (match) => match[1].trim());
}
