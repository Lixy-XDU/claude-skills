import assert from "node:assert/strict";
import { execFile } from "node:child_process";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import process from "node:process";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);
const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const SCRIPT_PATH = path.join(SCRIPT_DIR, "main.ts");

async function makeTempDir(prefix: string): Promise<string> {
  return fs.mkdtemp(path.join(os.tmpdir(), prefix));
}

test("CLI forwards wrapper title and package render options", async () => {
  const root = await makeTempDir("baoyu-markdown-to-html-cli-");
  const markdownPath = path.join(root, "article.md");
  await fs.writeFile(markdownPath, "## Section\n\nParagraph with **bold** text.\n", "utf-8");

  const { stdout } = await execFileAsync(
    process.execPath,
    [
      "--import",
      "tsx",
      SCRIPT_PATH,
      markdownPath,
      "--theme", "grace",
      "--color", "red",
      "--font-family", "mono",
      "--font-size", "18",
      "--keep-title",
      "--title", "Overridden",
    ],
    { cwd: SCRIPT_DIR },
  );

  const result = JSON.parse(stdout.trim()) as {
    htmlPath: string;
    title: string;
  };

  assert.equal(result.title, "Overridden");

  const html = await fs.readFile(result.htmlPath, "utf-8");
  assert.match(html, /<title>Overridden<\/title>/);
  assert.match(html, /<h2[^>]*style="[^"]*background: #A93226/);
  assert.match(html, /<strong[^>]*style="[^"]*color: #A93226/);
  assert.match(
    html,
    /<body[^>]*style="[^"]*font-family: Menlo, Monaco, 'Courier New', monospace;[^"]*font-size: 18px/,
  );
});

// --- LaTeX Protection Regression Tests ---

test("display math \\boxed with \\, and \\\\ is preserved", async () => {
  const root = await makeTempDir("baoyu-math-d-");
  const md = path.join(root, "test.md");
  await fs.writeFile(md, `---
title: Test
---
$$
\\boxed{
BB(t) = B(t) - t\\,B(1) \\\\
\\text{Cov}(BB(s), BB(t)) = \\min(s,t) - st
}
$$
`, "utf-8");

  const { stdout } = await execFileAsync(
    process.execPath,
    ["--import", "tsx", SCRIPT_PATH, md, "--theme", "default"],
    { cwd: SCRIPT_DIR },
  );
  const result = JSON.parse(stdout.trim()) as { htmlPath: string };
  const html = await fs.readFile(result.htmlPath, "utf-8");

  // Must NOT contain corrupted comma
  assert.ok(!/t,\s*B\s*\(/.test(html), "t\\,B(1) must not become t,B(1)");
  // Must contain the backslash-comma sequence
  assert.match(html, /t\\,B/);
  // Must contain \\\\ (double backslash for line break)
  assert.match(html, /\\\\\\\\/);
  // Must contain \\text{Cov}
  assert.match(html, /\\text\{Cov\}/);
});

test("inline math preserves \\, and \\ast", async () => {
  const root = await makeTempDir("baoyu-math-i-");
  const md = path.join(root, "test.md");
  await fs.writeFile(md, `---
title: Test
---
$\\sqrt{n}\\,D_n = \\sup_u |\\alpha_n^{\\ast}(u)|$
`, "utf-8");

  const { stdout } = await execFileAsync(
    process.execPath,
    ["--import", "tsx", SCRIPT_PATH, md, "--theme", "default"],
    { cwd: SCRIPT_DIR },
  );
  const result = JSON.parse(stdout.trim()) as { htmlPath: string };
  const html = await fs.readFile(result.htmlPath, "utf-8");

  // Must NOT contain comma corruption
  assert.ok(!/sqrt\{n\},D/.test(html), "\\, must not become comma");
  // Must contain \\,
  assert.match(html, /\\,/);
  // Must contain \\ast
  assert.match(html, /\\ast/);
});

test("table formula with \\| is preserved in one cell", async () => {
  const root = await makeTempDir("baoyu-table-math-");
  const md = path.join(root, "test.md");
  await fs.writeFile(md, `---
title: Test
---
| Item | Formula |
|------|---------|
| Test | $\\frac{\\sigma^2}{2\\theta}e^{-\\theta\\|t-s\\|}$ |
`, "utf-8");

  const { stdout } = await execFileAsync(
    process.execPath,
    ["--import", "tsx", SCRIPT_PATH, md, "--theme", "default"],
    { cwd: SCRIPT_DIR },
  );
  const result = JSON.parse(stdout.trim()) as { htmlPath: string };
  const html = await fs.readFile(result.htmlPath, "utf-8");

  // Must contain the full formula
  assert.match(html, /\\frac/);
  assert.match(html, /\\sigma/);
  // \\| must be preserved (not split into multiple columns)
  assert.match(html, /\\\\\|t-s\\\\\|/);
});

test("wiki link \\| in table is preserved in one cell", async () => {
  const root = await makeTempDir("baoyu-wiki-table-");
  const md = path.join(root, "test.md");
  await fs.writeFile(md, `---
title: Test
---
| Method | Dependency |
|--------|------------|
| K-S 检验 | [[Kolmogorov–Smirnov 检验（K-S检验）\\|K-S 检验]] |
`, "utf-8");

  const { stdout } = await execFileAsync(
    process.execPath,
    ["--import", "tsx", SCRIPT_PATH, md, "--theme", "default"],
    { cwd: SCRIPT_DIR },
  );
  const result = JSON.parse(stdout.trim()) as { htmlPath: string };
  const html = await fs.readFile(result.htmlPath, "utf-8");

  // Wiki link should render as label text
  assert.match(html, /K-S 检验/);
  // The \\| must not cause the table to have extra columns
  // (validation would catch unpaired cells)
});

test("$$ display math blocks are paired", async () => {
  const root = await makeTempDir("baoyu-math-paired-");
  const md = path.join(root, "test.md");
  await fs.writeFile(md, `---
title: Test
---
$$
BB(t) = B(t) - t\\,B(1)
$$
`, "utf-8");

  const { stdout } = await execFileAsync(
    process.execPath,
    ["--import", "tsx", SCRIPT_PATH, md, "--theme", "default"],
    { cwd: SCRIPT_DIR },
  );
  const result = JSON.parse(stdout.trim()) as { htmlPath: string };
  const html = await fs.readFile(result.htmlPath, "utf-8");

  const ddCount = (html.match(/\$\$/g) || []).length;
  assert.equal(ddCount % 2, 0, "$$ must be paired");
});
