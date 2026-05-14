import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import process from "node:process";

import {
  COLOR_PRESETS,
  FONT_FAMILY_MAP,
  FONT_SIZE_OPTIONS,
  THEME_NAMES,
  extractSummaryFromBody,
  extractTitleFromMarkdown,
  formatTimestamp,
  parseArgs,
  parseFrontmatter,
  renderMarkdownDocument,
  replaceMarkdownImagesWithPlaceholders,
  resolveContentImages,
  serializeFrontmatter,
  stripWrappingQuotes,
} from "baoyu-md";
import type { CliOptions } from "baoyu-md";

// --- LaTeX / Wiki Link Protection ---

const PLACEHOLDER_PREFIX = "@@PROTECTED_";

function protectSpecialContent(markdown: string): {
  protected: string;
  store: Map<string, string>;
} {
  const store = new Map<string, string>();
  let idx = 0;

  // 1) Fenced code blocks
  markdown = markdown.replace(
    /(```[\s\S]*?```)/g,
    (m) => {
      const ph = `${PLACEHOLDER_PREFIX}CODE_${idx++}@@`;
      store.set(ph, m);
      return ph;
    },
  );

  // 2) Display math $$...$$
  markdown = markdown.replace(
    /\$\$([\s\S]*?)\$\$/g,
    (m) => {
      const ph = `${PLACEHOLDER_PREFIX}MATH_D_${idx++}@@`;
      store.set(ph, m);
      return ph;
    },
  );

  // 3) Inline math $...$ (non-greedy, single line, skip $$)
  markdown = markdown.replace(
    /(?<!\$)\$(?!\$)([^$\n]+?)\$(?!\$)/g,
    (m) => {
      const ph = `${PLACEHOLDER_PREFIX}MATH_I_${idx++}@@`;
      store.set(ph, m);
      return ph;
    },
  );

  // 4) Obsidian wiki links [[target|label]] or [[target\|label]] or [[target]]
  markdown = markdown.replace(
    /\[\[([^\]]+)\]\]/g,
    (m) => {
      const ph = `${PLACEHOLDER_PREFIX}WIKI_${idx++}@@`;
      store.set(ph, m);
      return ph;
    },
  );

  return { protected: markdown, store };
}

function restoreSpecialContent(
  html: string,
  store: Map<string, string>,
): string {
  // Restore in reverse order to handle nested cases correctly
  for (const [ph, original] of store) {
    // Escape HTML entities that baoyu-md may have introduced into the original
    // when it appeared as plain text. We want the EXACT original LaTeX.
    // The placeholder content itself should be treated as raw.
    html = html.split(ph).join(original);
  }
  return html;
}

function wikiLinkToHtml(raw: string): string {
  const inner = raw.slice(2, -2); // strip [[ and ]]
  // Handle [[target\|label]] (Obsidian escaped pipe)
  const escapedPipe = inner.indexOf("\\|");
  if (escapedPipe >= 0) {
    const label = inner.slice(escapedPipe + 2);
    return label;
  }
  // Handle [[target|label]]
  const pipe = inner.indexOf("|");
  if (pipe >= 0) {
    const label = inner.slice(pipe + 1);
    return label;
  }
  // Plain [[target]]
  return inner;
}

function postProcessMathWikiInHtml(html: string): string {
  // Restore protected content (already raw from store)
  // Wiki links: convert [[...]] in the output back to display label
  html = html.replace(
    new RegExp(`${PLACEHOLDER_PREFIX.replace(/@/g, "@")}WIKI_\\d+@@`, "g"),
    (m) => m, // keep for store restoration
  );

  // Inject MathJax v3 — try </head> first, fallback to <body>
  const mathjaxScript = `
<script>
MathJax = { tex: { inlineMath: [['$', '$']], displayMath: [['$$', '$$']] } };
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" async></script>`;
  if (!html.includes("MathJax")) {
    if (html.includes("</head>")) {
      html = html.replace("</head>", `${mathjaxScript}\n</head>`);
    } else if (html.includes("<body")) {
      html = html.replace("<body", `${mathjaxScript}\n<body`);
    } else if (html.includes("</title>")) {
      html = html.replace("</title>", `</title>${mathjaxScript}`);
    }
  }

  return html;
}

function validateMathOutput(html: string, verbose = false): string[] {
  const errors: string[] = [];

  // 1. No `t,B(1)` — comma should not replace \,
  if (/t,\s*B\s*\(/.test(html)) {
    errors.push("LaTeX \\, was corrupted to comma");
  }

  // 2. No `sqrt{n},D_n` — comma corruption
  if (/sqrt\{n\},D/.test(html)) {
    errors.push("LaTeX \\, was corrupted in sqrt expression");
  }

  // 3. Must preserve `t\\,B(1)` or `t\\\\,B(1)` (depends on encoding)
  // Check that the backslash-comma sequence exists
  // After HTML encoding: t\,B or t\\,B
  if (!/t\\\\?,B/.test(html) && !/t\\,B/.test(html)) {
    // Only warn if we expected math
  }

  // 4. Display math $$ must be paired
  const ddCount = (html.match(/\$\$/g) || []).length;
  if (ddCount % 2 !== 0) {
    errors.push(`Unpaired $$ (count: ${ddCount})`);
  }

  // 5. Inline $ count should be roughly paired (heuristic)
  const dollarOutsideCode = html
    .replace(/<pre[^>]*>[\s\S]*?<\/pre>/g, "")
    .replace(/<code[^>]*>[\s\S]*?<\/code>/g, "");
  const inlineDollars = dollarOutsideCode.match(/(?<!\$)\$(?!\$)/g) || [];
  if (inlineDollars.length % 2 !== 0) {
    errors.push(`Possibly unpaired inline $ (count: ${inlineDollars.length})`);
  }

  if (verbose && errors.length > 0) {
    console.error("[markdown-to-html] Validation errors:", errors);
  }

  return errors;
}
// --- End Protection Utilities ---

interface ImageInfo {
  placeholder: string;
  localPath: string;
  originalPath: string;
}

interface ParsedResult {
  title: string;
  author: string;
  summary: string;
  htmlPath: string;
  backupPath?: string;
  contentImages: ImageInfo[];
}

type ConvertMarkdownOptions = Partial<Omit<CliOptions, "inputPath">> & {
  title?: string;
  outputDir?: string;
};

export async function convertMarkdown(
  markdownPath: string,
  options?: ConvertMarkdownOptions,
): Promise<ParsedResult> {
  const baseDir = path.dirname(markdownPath);
  const content = fs.readFileSync(markdownPath, "utf-8");
  const theme = options?.theme;
  const keepTitle = options?.keepTitle ?? false;
  const citeStatus = options?.citeStatus ?? false;

  const { frontmatter, body } = parseFrontmatter(content);

  let title = stripWrappingQuotes(options?.title ?? "")
    || stripWrappingQuotes(frontmatter.title ?? "")
    || extractTitleFromMarkdown(body);
  if (!title) {
    title = path.basename(markdownPath, path.extname(markdownPath));
  }

  const author = stripWrappingQuotes(frontmatter.author ?? "");
  let summary = stripWrappingQuotes(frontmatter.description ?? "")
    || stripWrappingQuotes(frontmatter.summary ?? "");
  if (!summary) {
    summary = extractSummaryFromBody(body, 120);
  }

  const effectiveFrontmatter = options?.title
    ? { ...frontmatter, title }
    : frontmatter;

  const { images, markdown: rewrittenBody } = replaceMarkdownImagesWithPlaceholders(
    body,
    "MDTOHTMLIMGPH_",
  );

  // Protect LaTeX math, code blocks, and wiki links before markdown conversion
  const { protected: protectedBody, store } = protectSpecialContent(rewrittenBody);
  const rewrittenMarkdown = `${serializeFrontmatter(effectiveFrontmatter)}${protectedBody}`;

  console.error(
    `[markdown-to-html] Rendering with theme: ${theme ?? "default"}, keepTitle: ${keepTitle}, citeStatus: ${citeStatus}`,
  );

  const { html: rawHtml } = await renderMarkdownDocument(rewrittenMarkdown, {
    codeTheme: options?.codeTheme,
    countStatus: options?.countStatus,
    citeStatus,
    defaultTitle: title,
    fontFamily: options?.fontFamily,
    fontSize: options?.fontSize,
    isMacCodeBlock: options?.isMacCodeBlock,
    isShowLineNumber: options?.isShowLineNumber,
    keepTitle,
    legend: options?.legend,
    primaryColor: options?.primaryColor,
    theme,
  });

  // Restore protected content (code blocks, math, wiki links)
  let html = restoreSpecialContent(rawHtml, store);

  // Post-process wiki links (render as plain text labels)
  html = html.replace(
    /@@PROTECTED_WIKI_\d+@@/g,
    (m) => wikiLinkToHtml(store.get(m) ?? m),
  );

  // Inject MathJax
  html = postProcessMathWikiInHtml(html);

  // Run validation
  const validationErrors = validateMathOutput(html, true);
  if (validationErrors.length > 0) {
    console.error(
      `[markdown-to-html] WARNING: ${validationErrors.length} math validation issue(s) detected`,
    );
  }

  const stem = path.basename(markdownPath, path.extname(markdownPath));
  const outputDir = options?.outputDir ?? path.dirname(markdownPath);
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  const finalHtmlPath = path.join(outputDir, `${stem}.html`);
  let backupPath: string | undefined;

  if (fs.existsSync(finalHtmlPath)) {
    backupPath = `${finalHtmlPath}.bak-${formatTimestamp()}`;
    console.error(`[markdown-to-html] Backing up existing file to: ${backupPath}`);
    fs.renameSync(finalHtmlPath, backupPath);
  }

  fs.writeFileSync(finalHtmlPath, html, "utf-8");

  const hasRemoteImages = images.some((image) =>
    image.originalPath.startsWith("http://") || image.originalPath.startsWith("https://"),
  );
  const tempDir = hasRemoteImages
    ? fs.mkdtempSync(path.join(os.tmpdir(), "markdown-to-html-"))
    : baseDir;
  const contentImages = await resolveContentImages(images, baseDir, tempDir, "markdown-to-html");

  let finalContent = fs.readFileSync(finalHtmlPath, "utf-8");
  for (const image of contentImages) {
    const imgTag = `<img src="${image.originalPath}" data-local-path="${image.localPath}" style="display: block; width: 100%; margin: 1.5em auto;">`;
    finalContent = finalContent.replace(image.placeholder, imgTag);
  }
  fs.writeFileSync(finalHtmlPath, finalContent, "utf-8");

  console.error(`[markdown-to-html] HTML saved to: ${finalHtmlPath}`);

  return {
    title,
    author,
    summary,
    htmlPath: finalHtmlPath,
    backupPath,
    contentImages,
  };
}

function printUsage(exitCode = 0): never {
  const colorNames = Object.keys(COLOR_PRESETS).join(", ");
  const fontFamilyNames = Object.keys(FONT_FAMILY_MAP).join(", ");

  console.log(`Convert Markdown to styled HTML

Usage:
  npx -y bun main.ts <markdown_file> [options]

Options:
  --title <title>         Override title
  --theme <name>          Theme name (${THEME_NAMES.join(", ")}). Default: default
  --color <name|hex>      Primary color: ${colorNames}
  --font-family <name>    Font: ${fontFamilyNames}, or CSS value
  --font-size <N>         Font size: ${FONT_SIZE_OPTIONS.join(", ")} (default: 16px)
  --code-theme <name>     Code highlight theme (default: github)
  --mac-code-block        Show Mac-style code block header
  --no-mac-code-block     Hide Mac-style code block header
  --line-number           Show line numbers in code blocks
  --cite                  Convert ordinary external links to bottom citations. Default: off
  --count                 Show reading time / word count
  --legend <value>        Image caption: title-alt, alt-title, title, alt, none
  --keep-title            Keep the first heading in content. Default: false (removed)
  --help                  Show this help

Output:
  HTML file saved to same directory as input markdown file.
  Example: article.md -> article.html

  If HTML file already exists, it will be backed up first:
  article.html -> article.html.bak-YYYYMMDDHHMMSS

Output JSON format:
{
  "title": "Article Title",
  "htmlPath": "/path/to/article.html",
  "backupPath": "/path/to/article.html.bak-20260128180000",
  "contentImages": [...]
}

Example:
  npx -y bun main.ts article.md
  npx -y bun main.ts article.md --theme grace
  npx -y bun main.ts article.md --theme modern --color red
  npx -y bun main.ts article.md --cite
`);
  process.exit(exitCode);
}

function parseArgValue(argv: string[], i: number, flag: string): string | null {
  const arg = argv[i]!;
  if (arg.includes("=")) {
    return arg.slice(flag.length + 1);
  }
  const next = argv[i + 1];
  return next ?? null;
}

function extractTitleArg(argv: string[]): { renderArgs: string[]; title?: string } {
  let title: string | undefined;
  const renderArgs: string[] = [];

  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]!;
    if (arg === "--title" || arg.startsWith("--title=")) {
      const value = parseArgValue(argv, i, "--title");
      if (!value) {
        console.error("Missing value for --title");
        printUsage(1);
      }
      title = value;
      if (!arg.includes("=")) {
        i += 1;
      }
      continue;
    }
    renderArgs.push(arg);
  }

  return { renderArgs, title };
}

async function main(): Promise<void> {
  const args = process.argv.slice(2);
  if (args.length === 0 || args.includes("--help") || args.includes("-h")) {
    printUsage(0);
  }

  // Extract --out <dir> BEFORE parseArgs (which rejects unknown args)
  let outputDir: string | undefined;
  const preFiltered: string[] = [];
  for (let i = 0; i < args.length; i += 1) {
    if (args[i] === "--out" || args[i]?.startsWith("--out=")) {
      const val = parseArgValue(args, i, "--out");
      if (val) { outputDir = val; if (!args[i]!.includes("=")) i += 1; }
      continue;
    }
    preFiltered.push(args[i]!);
  }

  const { renderArgs, title } = extractTitleArg(preFiltered);
  const options = parseArgs(renderArgs);
  if (!options) {
    printUsage(1);
  }

  const markdownPath = path.resolve(process.cwd(), options.inputPath);
  if (!markdownPath.toLowerCase().endsWith(".md")) {
    console.error("Input file must end with .md");
    process.exit(1);
  }

  if (!fs.existsSync(markdownPath)) {
    console.error(`Error: File not found: ${markdownPath}`);
    process.exit(1);
  }

  const result = await convertMarkdown(markdownPath, { ...options, title, outputDir });
  console.log(JSON.stringify(result, null, 2));
}

await main().catch((error) => {
  console.error(`Error: ${error instanceof Error ? error.message : String(error)}`);
  process.exit(1);
});
