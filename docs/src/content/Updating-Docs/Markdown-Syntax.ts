export const metadata = {
  title: "Markdown Syntax",
  order: 3
}

export const content = `
# Markdown Syntax

What the site understands. It is the part of GitHub-flavoured Markdown that the block pages use, so a page looks the same here and on GitHub.

## Headings

\`\`\`
# Page title
## Section
### Subsection
\`\`\`

The first \`# \` heading of a block page is also its name in the sidebar.

## Text

\`\`\`
**Bold text**
*Italic text*
\`inline code\`
Lines that follow each other
are one paragraph.

A blank line starts the next paragraph.
\`\`\`

## Lists

\`\`\`
- Item
- Item whose text is wrapped:
  indent the following lines
  - Nested item (indent it under its parent)

1. First
2. Second
\`\`\`

## Code Blocks

Put the code between two lines of three backticks. A language name after the opening backticks is allowed and ignored.

For code inside a sentence that itself contains a backtick, such as a Verilog-A \`\` \`include \`\`, put two backticks and a space on each side: \`\`\` \`\` \`include \`\` \`\`\`.

\`\`\`\`
\`\`\`bash
make CreateProject
\`\`\`
\`\`\`\`

## Tables

A header row, a divider row, then one row per line. Cells can hold bold, code and links. End a divider cell with a colon to right-align the column. A wide table scrolls sideways on its own.

\`\`\`
| Block | File | Lanes |
|---|---|---:|
| \`tx_pll\` | [tx_pll.va](../../va/Clocking/tx_pll.va) | 1 |
| **mux2_cmos** | \`Transmitter/mux2_cmos.va\` | 24 |
\`\`\`

| Block | File | Lanes |
|---|---|---:|
| \`tx_pll\` | \`Clocking/tx_pll.va\` | 1 |
| **mux2_cmos** | \`Transmitter/mux2_cmos.va\` | 24 |

Write \`\\|\` for a vertical bar inside a cell.

## Links

\`\`\`
[TX PLL](tx_pll.md)
[Clocking overview](../Clocking/README.md)
[Sizing](tx_pll.md#sizing-research)
[the model](../../va/Clocking/tx_pll.va)
[Vite](https://vitejs.dev)
\`\`\`

- A relative link to another Markdown page opens that page on the site. Add \`#heading\` to jump to a heading: lower case, spaces become hyphens.
- A relative link to any other file in the repository opens the file on GitHub.
- A link that starts with \`http\` is left alone. A bare \`https://...\` address in the text becomes a link too.
- The template pages are \`.ts\` files, not Markdown files, so they link to each other by sidebar path: [Build & Deploy](/Updating-Docs/Build-Deploy) is written \`[Build & Deploy](/Updating-Docs/Build-Deploy)\`.

## Images

\`\`\`
![Transmitter](../img/transmitter.svg)
\`\`\`

Put the file in \`analog/PAM4SerDes/docs/img/\` (\`.svg\`, \`.png\`, \`.jpg\`, \`.gif\` or \`.webp\`) and write the path relative to the Markdown file, so GitHub shows it too. The site finds the picture by its file name, so every file name in \`img/\` must be different. A picture on a line of its own becomes a figure: click it to open it full size.

## Also Supported

\`\`\`
> A quoted note

---
\`\`\`

A line of three hyphens draws a rule. A backslash keeps the next character as it is: \`\\*\` shows a star.

## Not Supported

- HTML tags: they are shown as text
- Italics with underscores: \`_\` stays as typed, so names like \`tx_ser_ffe_path\` are safe. Use \`*text*\`
- Bold and italic at once (\`***text***\`)
- Strikethrough, task lists and footnotes
- Colours in code blocks
- A line break inside a paragraph: start a new paragraph or use a list

Keep it simple!
`
