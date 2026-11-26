import { Fragment, ReactNode } from 'react'
import { Page, resolveImage, resolveLink } from '../utils/contentLoader'

// A small hand-written renderer for the GitHub-flavoured Markdown the pages use:
// headings, paragraphs, lists (nested), tables, fenced code, block quotes, rules,
// and inline code, bold, *italics*, links and images. No HTML.
//
// renderBlocks() walks the lines and emits one element per block; renderInline()
// handles the formatting inside a line of text.

interface MarkdownRendererProps {
  page: Page
}

export function MarkdownRenderer({ page }: MarkdownRendererProps) {
  return <div className="markdown-content">{renderBlocks(page.content.trim().split(/\r?\n/), page)}</div>
}

// ---------------------------------------------------------------------------
// Blocks
// ---------------------------------------------------------------------------

const FENCE = /^\s*(`{3,})/
const HEADING = /^\s*(#{1,6})\s+(.+)$/
const RULE = /^\s*(-{3,}|\*{3,}|_{3,})\s*$/
const QUOTE = /^\s*>\s?/
const LIST_ITEM = /^(\s*)([-*+]|\d+[.)])\s+(.*)$/
const TABLE_DIVIDER = /^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)*\|?\s*$/
const IMAGE_ONLY = /^!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)$/

const indentOf = (line: string) => line.length - line.trimStart().length
const isBlank = (line: string) => !line.trim()
const isOrdered = (marker: string) => /\d/.test(marker)

const isTableStart = (lines: string[], i: number) =>
  lines[i].includes('|') && i + 1 < lines.length && lines[i + 1].includes('|') && TABLE_DIVIDER.test(lines[i + 1])

/** Does line i end the paragraph before it? (An ordered list only does if it starts at 1.) */
function startsBlock(lines: string[], i: number): boolean {
  const line = lines[i]
  const item = LIST_ITEM.exec(line)
  return (
    FENCE.test(line) || HEADING.test(line) || RULE.test(line) || QUOTE.test(line) ||
    (item !== null && (!isOrdered(item[2]) || parseInt(item[2]) === 1)) ||
    isTableStart(lines, i)
  )
}

/** `tight` is set inside a list item written without blank lines: its text gets no <p>. */
function renderBlocks(lines: string[], page: Page, tight = false): ReactNode[] {
  const blocks: ReactNode[] = []
  let i = 0

  while (i < lines.length) {
    const line = lines[i]
    const key = i

    if (isBlank(line)) {
      i++
      continue
    }

    const fence = FENCE.exec(line)
    if (fence) {
      // Closed by a line of at least as many backticks, so a ```` block can show ``` lines.
      const closes = (text: string) => text.startsWith(fence[1]) && /^`+$/.test(text)
      const indent = indentOf(line)
      const code: string[] = []
      for (i++; i < lines.length && !closes(lines[i].trim()); i++) {
        code.push(lines[i].slice(Math.min(indent, indentOf(lines[i]))))
      }
      i++ // closing fence
      blocks.push(<pre key={key}><code>{code.join('\n')}</code></pre>)
      continue
    }

    const heading = HEADING.exec(line)
    if (heading) {
      const Tag = `h${heading[1].length}` as 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6'
      blocks.push(<Tag key={key} id={slug(heading[2])}>{renderInline(heading[2], page)}</Tag>)
      i++
      continue
    }

    if (RULE.test(line)) {
      blocks.push(<hr key={key} />)
      i++
      continue
    }

    if (QUOTE.test(line)) {
      const quoted: string[] = []
      for (; i < lines.length && QUOTE.test(lines[i]); i++) quoted.push(lines[i].replace(QUOTE, ''))
      blocks.push(<blockquote key={key}>{renderBlocks(quoted, page)}</blockquote>)
      continue
    }

    if (isTableStart(lines, i)) {
      const rows: string[] = []
      for (; i < lines.length && lines[i].includes('|'); i++) rows.push(lines[i])
      blocks.push(renderTable(rows, page, key))
      continue
    }

    if (LIST_ITEM.test(line)) {
      const [list, next] = renderList(lines, i, page)
      blocks.push(list)
      i = next
      continue
    }

    // Paragraph: this line and the ones wrapped below it.
    const text = [line.trim()]
    for (i++; i < lines.length && !isBlank(lines[i]) && !startsBlock(lines, i); i++) text.push(lines[i].trim())
    const paragraph = text.join(' ')
    const image = IMAGE_ONLY.exec(paragraph)
    if (image) blocks.push(renderFigure(image[1], image[2], key))
    else if (tight) blocks.push(<Fragment key={key}>{renderInline(paragraph, page)}</Fragment>)
    else blocks.push(<p key={key}>{renderInline(paragraph, page)}</p>)
  }

  return blocks
}

/**
 * Renders the list that starts at line `start` and returns it with the index of the
 * first line after it. An item owns the lines indented under it (wrapped text, nested
 * lists, code blocks); they are rendered as blocks of their own.
 */
function renderList(lines: string[], start: number, page: Page): [ReactNode, number] {
  const first = LIST_ITEM.exec(lines[start])!
  const baseIndent = first[1].length
  const ordered = isOrdered(first[2])
  const items: ReactNode[] = []
  let i = start

  while (i < lines.length) {
    const item = LIST_ITEM.exec(lines[i])
    if (!item || item[1].length !== baseIndent || isOrdered(item[2]) !== ordered) break

    const textColumn = lines[i].length - item[3].length
    const body = [item[3]]
    let tight = true
    for (i++; i < lines.length; i++) {
      if (isBlank(lines[i])) {
        // A blank line stays in the item only if indented text follows it.
        const next = lines.slice(i + 1).find(line => !isBlank(line))
        if (next === undefined || indentOf(next) <= baseIndent) break
        tight = false
      } else if (indentOf(lines[i]) <= baseIndent) break
      body.push(lines[i].slice(Math.min(indentOf(lines[i]), textColumn)))
    }
    items.push(<li key={i}>{renderBlocks(body, page, tight)}</li>)

    // Blank lines between two items of the same list do not end it.
    let next = i
    while (next < lines.length && isBlank(lines[next])) next++
    if (next < lines.length && LIST_ITEM.test(lines[next]) && indentOf(lines[next]) === baseIndent) i = next
  }

  const firstNumber = parseInt(first[2])
  const list = ordered
    ? <ol key={start} start={firstNumber === 1 ? undefined : firstNumber}>{items}</ol>
    : <ul key={start}>{items}</ul>
  return [list, i]
}

/** `rows` is the header row, the divider row, then the body rows. */
function renderTable(rows: string[], page: Page, key: number): ReactNode {
  // "\|" is a literal pipe inside a cell, so hide it while splitting.
  const cells = (row: string) =>
    row.trim().replace(/^\||\|$/g, '').replace(/\\\|/g, '\u0000').split('|')
      .map(cell => cell.replace(/\u0000/g, '|').trim())

  const [header, divider, ...body] = rows.map(cells)
  const align = divider.map(cell =>
    cell.endsWith(':') ? (cell.startsWith(':') ? 'center' : 'right') : undefined)

  return (
    // The wrapper scrolls sideways, so a wide table never widens the page.
    <div className="table-wrap" key={key}>
      <table>
        <thead>
          <tr>
            {header.map((cell, c) => <th key={c} style={{ textAlign: align[c] }}>{renderInline(cell, page)}</th>)}
          </tr>
        </thead>
        <tbody>
          {body.map((row, r) => (
            <tr key={r}>
              {header.map((_, c) => <td key={c} style={{ textAlign: align[c] }}>{renderInline(row[c] ?? '', page)}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

/** A picture on a line of its own. It links to the file, so a diagram can be opened full size. */
function renderFigure(alt: string, src: string, key: number): ReactNode {
  const url = resolveImage(src)
  if (!url) return <p key={key}>{renderImage(alt, src, key)}</p>
  return (
    <a className="figure" key={key} href={url} title="Open full size">
      <img src={url} alt={alt} />
    </a>
  )
}

function renderImage(alt: string, src: string, key: number): ReactNode {
  const url = resolveImage(src)
  return url
    ? <img key={key} src={url} alt={alt} />
    : <span key={key} className="missing-image">[image not found: {src}]</span>
}

/** Heading id, the way GitHub builds it: "Sizing research" -> "sizing-research". */
// ponytail: repeated headings on one page share an id (GitHub adds -1, -2); a link to
// the second one lands on the first. Number them here if a page ever needs it.
const slug = (heading: string) => heading.toLowerCase().replace(/[^\w\- ]/g, '').replace(/ /g, '-')

// ---------------------------------------------------------------------------
// Inline formatting
// ---------------------------------------------------------------------------

// One alternative per construct; the capture groups are numbered in the comments.
const INLINE = new RegExp(
  [
    /\\([\\`*_{}[\]()#+\-.!|<>~])/, //                                   1      escaped character
    // 2, 3 code: the backticks that open it, the text. It closes at the same number of
    // backticks (\2), so `` `include `` can hold a backtick.
    /(`+)(?!`)(.*?[^`])\2(?!`)/,
    /!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)/, //                       4, 5   image: alt, file
    /\[((?:[^[\]]|\[[^\]]*\])+)\]\(([^)\s]+)(?:\s+"[^"]*")?\)/, //        6, 7   link: text, target
    /\*\*(.+?)\*\*/, //                                                   8      bold
    /(https?:\/\/[^\s<>]*[^\s<>.,;:!?)\]'"*])/, //                        9      bare URL
    // 10, 11 italics: the character before, the text. Only a star that opens a word and one
    // that closes a word count, so "div2_cml*" and "2 * 3" keep their stars.
    /(^|[\s([{"'>])\*([^\s*](?:[^*]*[^\s*])?)\*(?=$|[\s.,;:!?)\]}"'<])/,
  ].map(pattern => pattern.source).join('|'),
  'g',
)

function renderInline(text: string, page: Page): ReactNode[] {
  const nodes: ReactNode[] = []
  let end = 0

  for (const match of text.matchAll(INLINE)) {
    const key = match.index!
    if (key > end) nodes.push(text.slice(end, key))
    end = key + match[0].length

    const [, escaped, , code, alt, src, linkText, target, bold, url, before, italic] = match
    if (escaped !== undefined) nodes.push(escaped)
    // one space of padding inside the backticks is not part of the code
    else if (code !== undefined) nodes.push(<code key={key}>{code.replace(/^ (.*\S.*) $/, '$1')}</code>)
    else if (src !== undefined) nodes.push(renderImage(alt, src, key))
    else if (target !== undefined) nodes.push(<a key={key} href={resolveLink(target, page)}>{renderInline(linkText, page)}</a>)
    else if (bold !== undefined) nodes.push(<strong key={key}>{renderInline(bold, page)}</strong>)
    else if (url !== undefined) nodes.push(<a key={key} href={url}>{url}</a>)
    else nodes.push(before, <em key={key}>{renderInline(italic, page)}</em>)
  }

  if (end < text.length) nodes.push(text.slice(end))
  return nodes
}
