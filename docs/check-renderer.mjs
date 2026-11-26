// Runnable check of the Markdown renderer. From docs/:  bun run check
//
// Renders small pieces of Markdown through src/components/MarkdownRenderer.tsx and compares
// the HTML. Vite loads the module, so the loader's import.meta.glob works; nothing is served.
// Add a case here when the renderer learns something new.
import assert from 'node:assert/strict'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { createElement } from 'react'
import { renderToStaticMarkup } from 'react-dom/server'
import { createServer } from 'vite'

const vite = await createServer({
  logLevel: 'silent', // a failed case still throws below
  appType: 'custom',
  // Vite's cache normally goes to node_modules/.vite, which this repository tracks in git.
  cacheDir: join(tmpdir(), 'pam4serdes-docs-check'),
  server: { middlewareMode: true, hmr: false, watch: null },
  optimizeDeps: { noDiscovery: true },
})

try {
  const { MarkdownRenderer } = await vite.ssrLoadModule('/src/components/MarkdownRenderer.tsx')
  const render = (content, source = 'analog/PAM4SerDes/docs/Clocking/tx_pll.md') => {
    const page = { id: 'tx_pll', path: 'Clocking/tx_pll', source, content, metadata: { title: '', order: 0 } }
    return renderToStaticMarkup(createElement(MarkdownRenderer, { page })).replace(/^<div class="markdown-content">|<\/div>$/g, '')
  }

  const cases = [
    ['heading with an id', '## Sizing research', '<h2 id="sizing-research">Sizing research</h2>'],
    ['wrapped lines are one paragraph', 'one\ntwo\n\nthree', '<p>one two</p><p>three</p>'],
    ['a number at a line start does not start a list', 'Lee et al., JSSC\n2015. A team', '<p>Lee et al., JSSC 2015. A team</p>'],
    ['nested list, wrapped item', '- one\n  more\n  - inner\n- two', '<ul><li>one more<ul><li>inner</li></ul></li><li>two</li></ul>'],
    ['numbered list after a paragraph', 'Steps:\n1. a\n2. b', '<p>Steps:</p><ol><li>a</li><li>b</li></ol>'],
    ['code block inside a list item', '1. run\n   ```\n   make # x\n   ```\n2. done', '<ol><li>run<pre><code>make # x</code></pre></li><li>done</li></ol>'],
    ['code block keeps Markdown as text', '```va\n# no | **heading**\n```', '<pre><code># no | **heading**</code></pre>'],
    ['a longer fence can show a fence', '````\n```\nx\n```\n````', '<pre><code>```\nx\n```</code></pre>'],
    ['table', '| A | B |\n|---|--:|\n| `x` | **y** \\| z |',
      '<div class="table-wrap"><table><thead><tr><th>A</th><th style="text-align:right">B</th></tr></thead>' +
      '<tbody><tr><td><code>x</code></td><td style="text-align:right"><strong>y</strong> | z</td></tr></tbody></table></div>'],
    ['inline formatting, stars and underscores in names', 'div2_cml*, mux2_cs* x4, *soon* and **b `c`** in tx_ser_ffe_path',
      '<p>div2_cml*, mux2_cs* x4, <em>soon</em> and <strong>b <code>c</code></strong> in tx_ser_ffe_path</p>'],
    ['code that holds a backtick', 'Starts with `` `ifndef X `` and `a`.', '<p>Starts with <code>`ifndef X</code> and <code>a</code>.</p>'],
    ['link to a repo file goes to GitHub', '[model](../../va/Clocking/tx_pll.va)',
      '<p><a href="https://github.com/UW-ASIC/PAM4SerDes/blob/main/analog/PAM4SerDes/va/Clocking/tx_pll.va">model</a></p>'],
    ['heading link stays on the page', '[sizing](#sizing-research)', '<p><a href="#/Clocking/tx_pll#sizing-research">sizing</a></p>'],
    ['site path and web links', '[a](/Flows/Digital) [**b**](https://example.com)',
      '<p><a href="#/Flows/Digital">a</a> <a href="https://example.com"><strong>b</strong></a></p>'],
    ['brackets in link text', '[rxd_m[0:31]](https://example.com)', '<p><a href="https://example.com">rxd_m[0:31]</a></p>'],
    ['missing picture is reported', '![x](../img/no_such_file.svg)', '<p><span class="missing-image">[image not found: ../img/no_such_file.svg]</span></p>'],
    ['quote and rule', '> note\n\n---', '<blockquote><p>note</p></blockquote><hr/>'],
  ]

  for (const [name, markdown, html] of cases) assert.equal(render(markdown), html, name)

  // A picture in analog/PAM4SerDes/docs/img/ is found by its file name and becomes a figure.
  assert.match(render('![Top](../img/top.svg)'), /^<a class="figure" href="[^"]*top[^"]*\.svg" title="Open full size"><img src="[^"]*top[^"]*\.svg" alt="Top"\/><\/a>$/)

  console.log(`renderer check: ${cases.length + 1} cases pass`)
} finally {
  await vite.close()
}
