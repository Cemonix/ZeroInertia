import { EditorView } from "@codemirror/view";
import { type Extension } from "@codemirror/state";
import { HighlightStyle, syntaxHighlighting } from "@codemirror/language";
import { tags as t } from "@lezer/highlight";

// Light theme colors inspired by GitHub Light and One Light
const blue = "#0550ae",
    red = "#cf222e",
    teal = "#0969da",
    invalid = "#86181d",
    black = "#1f2328",
    gray = "#57606a",
    lightBlue = "#0969da",
    green = "#1a7f37",
    orange = "#953800",
    purple = "#8250df",
    lightBackground = "#ffffff",
    highlightBackground = "#f6f8fa",
    background = "#ffffff",
    tooltipBackground = "#f6f8fa",
    selection = "#add6ff4d",
    cursor = "#0550ae";

/// The colors used in the light theme
export const color = {
    blue,
    red,
    teal,
    invalid,
    black,
    gray,
    lightBlue,
    green,
    orange,
    purple,
    lightBackground,
    highlightBackground,
    background,
    tooltipBackground,
    selection,
    cursor,
};

/// The editor theme styles for One Light
export const oneLightTheme = EditorView.theme(
    {
        "&": {
            color: black,
            backgroundColor: background,
        },

        ".cm-content": {
            caretColor: cursor,
        },

        ".cm-cursor, .cm-dropCursor": { borderLeftColor: cursor },
        "&.cm-focused > .cm-scroller > .cm-selectionLayer .cm-selectionBackground, .cm-selectionBackground, .cm-content ::selection":
            { backgroundColor: selection },

        ".cm-panels": { backgroundColor: lightBackground, color: black },
        ".cm-panels.cm-panels-top": { borderBottom: "2px solid #d0d7de" },
        ".cm-panels.cm-panels-bottom": { borderTop: "2px solid #d0d7de" },

        ".cm-searchMatch": {
            backgroundColor: "#ffdf5d66",
            outline: "1px solid #fb8500",
        },
        ".cm-searchMatch.cm-searchMatch-selected": {
            backgroundColor: "#ffdf5d",
        },

        ".cm-activeLine": { backgroundColor: "#f6f8fa" },
        ".cm-selectionMatch": { backgroundColor: "#add6ff26" },

        "&.cm-focused .cm-matchingBracket, &.cm-focused .cm-nonmatchingBracket":
            {
                backgroundColor: "#ddf4ff",
            },

        ".cm-gutters": {
            backgroundColor: background,
            color: gray,
            border: "none",
        },

        ".cm-activeLineGutter": {
            backgroundColor: highlightBackground,
        },

        ".cm-foldPlaceholder": {
            backgroundColor: "transparent",
            border: "none",
            color: "#6e7781",
        },

        ".cm-tooltip": {
            border: "1px solid #d0d7de",
            backgroundColor: tooltipBackground,
        },
        ".cm-tooltip .cm-tooltip-arrow:before": {
            borderTopColor: "transparent",
            borderBottomColor: "transparent",
        },
        ".cm-tooltip .cm-tooltip-arrow:after": {
            borderTopColor: tooltipBackground,
            borderBottomColor: tooltipBackground,
        },
        ".cm-tooltip-autocomplete": {
            "& > ul > li[aria-selected]": {
                backgroundColor: highlightBackground,
                color: black,
            },
        },
    },
    { dark: false }
);

/// The highlighting style for code in the One Light theme
export const oneLightHighlightStyle = HighlightStyle.define([
    { tag: t.keyword, color: purple },
    {
        tag: [t.name, t.deleted, t.character, t.propertyName, t.macroName],
        color: red,
    },
    { tag: [t.function(t.variableName), t.labelName], color: lightBlue },
    { tag: [t.color, t.constant(t.name), t.standard(t.name)], color: orange },
    { tag: [t.definition(t.name), t.separator], color: black },
    {
        tag: [
            t.typeName,
            t.className,
            t.number,
            t.changed,
            t.annotation,
            t.modifier,
            t.self,
            t.namespace,
        ],
        color: orange,
    },
    {
        tag: [
            t.operator,
            t.operatorKeyword,
            t.url,
            t.escape,
            t.regexp,
            t.link,
            t.special(t.string),
        ],
        color: teal,
    },
    { tag: [t.meta, t.comment], color: gray },
    { tag: t.strong, fontWeight: "bold", color: black },
    { tag: t.emphasis, fontStyle: "italic", color: black },
    { tag: t.strikethrough, textDecoration: "line-through" },
    { tag: t.link, color: lightBlue, textDecoration: "underline" },
    { tag: t.heading, fontWeight: "bold", color: blue },
    { tag: [t.atom, t.bool, t.special(t.variableName)], color: orange },
    { tag: [t.processingInstruction, t.string, t.inserted], color: green },
    { tag: t.invalid, color: invalid },
]);

/// Extension to enable the One Light theme (both the editor theme and
/// the highlight style)
export const oneLight: Extension = [
    oneLightTheme,
    syntaxHighlighting(oneLightHighlightStyle),
];
