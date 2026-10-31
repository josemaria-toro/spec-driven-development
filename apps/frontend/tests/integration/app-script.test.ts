// @vitest-environment node
import { spawnSync } from 'node:child_process';
import { chmodSync, copyFileSync, mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { createServer, connect } from 'node:net';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

import { afterEach, beforeEach, describe, expect, it } from 'vitest';

const SCRIPT = fileURLToPath(new URL('../../app.sh', import.meta.url));
// Stands in for `pnpm dev --port <port> --strictPort`: listens on the port, or fails on demand.
const FAKE_PNPM = `#!/usr/bin/env bash
if [[ "\${FAKE_PNPM_FAIL:-}" == "1" ]]; then echo "boom" >&2; exit 1; fi
exec node -e 'require("net").createServer().listen(Number(process.argv[1]))' "$3"
`;

let workDir: string;
let port: number;

function freePort(): Promise<number> {
  return new Promise((resolve, reject) => {
    const server = createServer();
    server.once('error', reject);
    server.listen(0, () => {
      const { port: assigned } = server.address() as { port: number };
      server.close(() => {
        resolve(assigned);
      });
    });
  });
}

function isListening(target: number): Promise<boolean> {
  return new Promise((resolve) => {
    const socket = connect(target, 'localhost');
    socket.once('connect', () => {
      socket.destroy();
      resolve(true);
    });
    socket.once('error', () => {
      resolve(false);
    });
  });
}

function run(command: string, env: Record<string, string> = {}) {
  const result = spawnSync('bash', [join(workDir, 'app', 'app.sh'), command], {
    encoding: 'utf8',
    env: { ...process.env, PATH: `${join(workDir, 'bin')}:${process.env.PATH ?? ''}`, ...env },
    timeout: 60_000,
  });
  return { output: `${result.stdout}${result.stderr}`, status: result.status };
}

/* eslint-disable security/detect-non-literal-fs-filename -- every path is inside a temp directory this test just created */
beforeEach(async () => {
  workDir = mkdtempSync(join(tmpdir(), 'app-script-'));
  mkdirSync(join(workDir, 'bin'));
  mkdirSync(join(workDir, 'app', 'node_modules'), { recursive: true });
  copyFileSync(SCRIPT, join(workDir, 'app', 'app.sh'));
  writeFileSync(join(workDir, 'bin', 'pnpm'), FAKE_PNPM);
  chmodSync(join(workDir, 'bin', 'pnpm'), 0o755);
  port = await freePort();
});

/* eslint-enable security/detect-non-literal-fs-filename */
afterEach(() => {
  run('stop', { PORT: String(port) });
  rmSync(workDir, { force: true, recursive: true });
});

describe('frontend app.sh', () => {
  it('starts the server, reports a second start, and stops it', async () => {
    const env = { PORT: String(port) };

    const started = run('start', env);
    expect(started.status).toBe(0);
    expect(started.output).toContain(`http://localhost:${String(port)}`);
    expect(await isListening(port)).toBe(true);

    expect(run('start', env).output).toContain('already running');

    const stopped = run('stop', env);
    expect(stopped.status).toBe(0);
    expect(stopped.output).toContain('frontend stopped');
    expect(await isListening(port)).toBe(false);
  });

  it('stops cleanly when nothing is running', () => {
    const result = run('stop', { PORT: String(port) });

    expect(result.status).toBe(0);
    expect(result.output).toContain('not running');
  });

  it('asks to install dependencies when they are missing', () => {
    rmSync(join(workDir, 'app', 'node_modules'), { recursive: true });

    const result = run('start', { PORT: String(port) });

    expect(result.status).toBe(1);
    expect(result.output).toContain('pnpm install --frozen-lockfile');
  });

  it('reports the log when the server fails to start', () => {
    const result = run('start', { FAKE_PNPM_FAIL: '1', PORT: String(port) });

    expect(result.status).toBe(1);
    expect(result.output).toContain('failed to start');
    expect(result.output).toContain('boom');
  });

  it('rejects an unknown command with the usage', () => {
    const result = run('restart');

    expect(result.status).toBe(2);
    expect(result.output).toContain('Usage:');
  });
});
