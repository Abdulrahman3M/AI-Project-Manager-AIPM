import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const testDir = path.dirname(fileURLToPath(import.meta.url));
const skillRoot = path.resolve(testDir, '..');
const cli = path.join(skillRoot, 'scripts', 'sps.mjs');

function tempProject() {
  return fs.mkdtempSync(path.join(os.tmpdir(), 'sps-node-'));
}
function run(args, cwd=skillRoot) {
  return spawnSync(process.execPath, [cli, ...args], {cwd, encoding:'utf8'});
}

test('init creates canonical state and preserves an existing current-state file', () => {
  const root = tempProject();
  let r = run(['init','--project-root',root,'--task-id','Task-Example','--title','Example','--agent','Test-Agent']);
  assert.equal(r.status, 0, r.stderr);
  const shared = path.join(root,'Shared-Project-State');
  assert.equal(fs.existsSync(path.join(shared,'State-Manifest.json')), true);
  assert.equal(fs.existsSync(path.join(shared,'Tasks','Task-Example','Task-Plan.md')), true);
  assert.equal(fs.existsSync(path.join(shared,'Quarantine','Records')), true);
  const current = path.join(shared,'Current-State.md');
  fs.writeFileSync(current, '# Preserve Me\n', 'utf8');
  r = run(['init','--project-root',root,'--task-id','Task-Example','--title','Example','--agent','Another-Agent']);
  assert.equal(r.status, 0, r.stderr);
  assert.equal(fs.readFileSync(current,'utf8'), '# Preserve Me\n');
});

test('handoff updates manifest and handoff content', () => {
  const root = tempProject();
  let r = run(['init','--project-root',root,'--task-id','Task-Handoff','--title','Handoff','--agent','Claude Code']);
  assert.equal(r.status, 0, r.stderr);
  r = run(['handoff','--project-root',root,'--from-agent','Claude Code','--to-agent','Codex','--last-verified','P01 passed','--next-action','Begin P02']);
  assert.equal(r.status, 0, r.stderr);
  const shared = path.join(root,'Shared-Project-State');
  const manifest = JSON.parse(fs.readFileSync(path.join(shared,'State-Manifest.json'),'utf8'));
  assert.equal(manifest.next_agent, 'Codex');
  assert.equal(manifest.next_action, 'Begin P02');
  const handoff = fs.readFileSync(path.join(shared,'Next-Agent-Handoff.md'),'utf8');
  assert.match(handoff, /Codex/);
  assert.match(handoff, /P01 passed/);
});
