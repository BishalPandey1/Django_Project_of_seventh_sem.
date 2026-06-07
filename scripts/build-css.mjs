#!/usr/bin/env node
/**
 * Tailwind v4 build glue.
 *
 * The Tailwind v4 CLI refuses to use the same path for --input and --output,
 * and any in-place compile overwrites the source. To keep `static/css/app.css`
 * usable as both the editable source AND the file Django serves, we:
 *   1. Snapshot the current source to `static/css/app.source.css` (so future
 *      edits can be re-applied after a build).
 *   2. Copy the source to a temp file, run the CLI with that as input and
 *      `app.css` as the output, then delete the temp file.
 *
 * Usage:
 *   node scripts/build-css.mjs           # compile once
 *   node scripts/build-css.mjs --watch   # watch mode (no-op stub)
 *   node scripts/build-css.mjs --minify  # minify (for production)
 */

import { spawn } from 'node:child_process';
import { copyFile, unlink, stat } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname  = path.dirname(__filename);

const ROOT        = path.resolve(__dirname, '..');
const SOURCE_CSS  = path.join(ROOT, 'static', 'css', 'app.css');
const SOURCE_BAK  = path.join(ROOT, 'static', 'css', 'app.source.css');
const TMP_CSS     = path.join(ROOT, 'static', 'css', '.app.tmp.css');

const args = process.argv.slice(2);
const isWatch  = args.includes('--watch');
const isMinify = args.includes('--minify') || process.env.NODE_ENV === 'production';

if (isWatch) {
    console.log('[build-css] Watch mode not supported by this script. Re-run after editing `app.css`.');
    process.exit(0);
}

async function exists(p) {
    try { await stat(p); return true; } catch { return false; }
}

async function main() {
    if (!(await exists(SOURCE_CSS))) {
        console.error(`[build-css] source not found: ${SOURCE_CSS}`);
        process.exit(1);
    }

    // Snapshot the current source before the CLI overwrites it.
    await copyFile(SOURCE_CSS, SOURCE_BAK);

    await copyFile(SOURCE_CSS, TMP_CSS);

    const cliArgs = [
        'tailwindcss',
        '-i', TMP_CSS,
        '-o', SOURCE_CSS,
    ];
    if (isMinify) cliArgs.push('--minify');

    await new Promise((resolve, reject) => {
        // Use the installed tailwindcss CLI directly so Node's spawn
        // doesn't need to resolve `npx` from the system PATH. On Windows
        // the CLI ships as a .cmd shim, which requires `shell: true`.
        const cliPath = path.join(ROOT, 'node_modules', '.bin',
            process.platform === 'win32' ? 'tailwindcss.cmd' : 'tailwindcss');
        const child = spawn(cliPath, cliArgs.slice(1), {
            stdio: 'inherit',
            shell: process.platform === 'win32',
        });
        child.on('exit', code => code === 0 ? resolve() : reject(new Error(`tailwindcss exited with code ${code}`)));
    });

    try { await unlink(TMP_CSS); } catch {}
    console.log(`[build-css] ok → ${path.relative(ROOT, SOURCE_CSS)}`);
    console.log(`[build-css] source snapshot → ${path.relative(ROOT, SOURCE_BAK)}`);
}

main().catch(err => { console.error(err); process.exit(1); });
