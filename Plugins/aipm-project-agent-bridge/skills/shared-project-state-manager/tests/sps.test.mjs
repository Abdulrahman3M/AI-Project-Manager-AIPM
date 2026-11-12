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
function run(args, cwd=skillRoot, env={}) {
  return spawnSync(process.execPath, [cli, ...args], {cwd, encoding:'utf8', env: {...process.env, ...env}});
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
  const routePy = path.join(shared, 'Route-Transient-State.py');
  const routePs = path.join(shared, 'Route-Transient-State.ps1');
  const safeMove = path.join(shared, 'safe_move.py');
  assert.equal(fs.existsSync(safeMove), true);
  fs.writeFileSync(routePy, '# preserve Python route\n', 'utf8');
  fs.writeFileSync(routePs, '# preserve PowerShell route\n', 'utf8');
  fs.writeFileSync(safeMove, '# preserve helper\n', 'utf8');
  r = run(['init','--project-root',root,'--task-id','Task-Example','--title','Example','--agent','Another-Agent']);
  assert.equal(r.status, 0, r.stderr);
  assert.equal(fs.readFileSync(current,'utf8'), '# Preserve Me\n');
  assert.equal(fs.readFileSync(routePy, 'utf8'), '# preserve Python route\n');
  assert.equal(fs.readFileSync(routePs, 'utf8'), '# preserve PowerShell route\n');
  assert.equal(fs.readFileSync(safeMove, 'utf8'), '# preserve helper\n');
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

test('init refuses a linked state root without writing through it', (t) => {
  const parent = tempProject();
  const root = path.join(parent, 'project');
  const outside = path.join(parent, 'outside');
  fs.mkdirSync(root);
  fs.mkdirSync(outside);
  try {
    fs.symlinkSync(outside, path.join(root, 'Shared-Project-State'), 'dir');
  } catch (error) {
    t.skip(`Link creation unavailable: ${error.message}`);
    return;
  }
  const result = run(['init', '--project-root', root, '--task-id', 'Task-Link', '--title', 'Link', '--agent', 'Test']);
  assert.notEqual(result.status, 0);
  assert.deepEqual(fs.readdirSync(outside), []);
});

test('checkpoint rejects a traversal task id from a manipulated manifest', () => {
  const root = tempProject();
  const initial = run(['init', '--project-root', root, '--task-id', 'Task-Safe', '--title', 'Safe', '--agent', 'Test']);
  assert.equal(initial.status, 0, initial.stderr);
  const manifestPath = path.join(root, 'Shared-Project-State', 'State-Manifest.json');
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  manifest.task_id = '../../outside';
  fs.writeFileSync(manifestPath, JSON.stringify(manifest), 'utf8');
  const result = run(['checkpoint', '--project-root', root, '--last-verified', 'test', '--next-action', 'test']);
  assert.notEqual(result.status, 0);
  assert.equal(fs.existsSync(path.join(root, 'outside')), false);
});

test('init refuses a linked nested task directory before writing', (t) => {
  const parent = tempProject();
  const root = path.join(parent, 'project');
  const outside = path.join(parent, 'outside');
  const shared = path.join(root, 'Shared-Project-State');
  fs.mkdirSync(shared, { recursive: true });
  fs.mkdirSync(outside);
  try {
    fs.symlinkSync(outside, path.join(shared, 'Tasks'), 'dir');
  } catch (error) {
    t.skip(`Link creation unavailable: ${error.message}`);
    return;
  }
  const result = run(['init', '--project-root', root, '--task-id', 'Task-Link', '--title', 'Link', '--agent', 'Test']);
  assert.notEqual(result.status, 0);
  assert.deepEqual(fs.readdirSync(outside), []);
  assert.deepEqual(fs.readdirSync(shared), ['Tasks']);
});

test('init rejects a state root swapped to a link between guarded writes', (t) => {
  const parent = tempProject();
  const root = path.join(parent, 'project');
  const outside = path.join(parent, 'outside');
  fs.mkdirSync(root);
  fs.mkdirSync(outside);
  const probe = path.join(parent, 'probe');
  try {
    fs.symlinkSync(outside, probe, 'dir');
    fs.unlinkSync(probe);
  } catch (error) {
    t.skip(`Link creation unavailable: ${error.message}`);
    return;
  }
  const preload = path.join(parent, 'inject.cjs');
  fs.writeFileSync(preload, `
    const fs = require('node:fs');
    const path = require('node:path');
    const cp = require('node:child_process');
    const original = cp.spawnSync;
    let injected = false;
    cp.spawnSync = function(command, args, options) {
      if (!injected && options && typeof options.input === 'string') {
        let request;
        try { request = JSON.parse(options.input); } catch {}
        if (request && request.action === 'mkdir' && request.path.endsWith(path.join('Tasks', 'Task-Race', 'Checkpoints'))) {
          injected = true;
          fs.renameSync(process.env.AUDIT_SHARED, process.env.AUDIT_DETACHED);
          fs.symlinkSync(process.env.AUDIT_OUTSIDE, process.env.AUDIT_SHARED, 'dir');
          fs.writeFileSync(process.env.AUDIT_MARKER, 'injected');
        }
      }
      return original.apply(this, arguments);
    };
    require('node:module').syncBuiltinESMExports();
  `, 'utf8');
  const marker = path.join(parent, 'injected.txt');
  const shared = path.join(root, 'Shared-Project-State');
  const result = run(['init', '--project-root', root, '--task-id', 'Task-Race', '--title', 'Race', '--agent', 'Test'], skillRoot, {
    NODE_OPTIONS: `--require="${preload.replaceAll('\\', '/')}"`, AUDIT_SHARED: shared,
    AUDIT_DETACHED: path.join(root, 'detached'), AUDIT_OUTSIDE: outside, AUDIT_MARKER: marker
  });
  assert.equal(fs.existsSync(marker), true, `The race was not injected: ${result.stderr} ${result.stdout}`);
  assert.notEqual(result.status, 0);
  assert.deepEqual(fs.readdirSync(outside), []);
});

test('handoff refuses a state file swapped to an external link', (t) => {
  const parent = tempProject();
  const root = path.join(parent, 'project');
  fs.mkdirSync(root);
  const initial = run(['init', '--project-root', root, '--task-id', 'Task-Race', '--title', 'Race', '--agent', 'Test']);
  assert.equal(initial.status, 0, initial.stderr);
  const outside = path.join(parent, 'outside.txt');
  fs.writeFileSync(outside, 'outside canary', 'utf8');
  const probe = path.join(parent, 'probe');
  try { fs.symlinkSync(outside, probe, 'file'); fs.unlinkSync(probe); }
  catch (error) { t.skip(`Link creation unavailable: ${error.message}`); return; }
  const preload = path.join(parent, 'inject.cjs');
  fs.writeFileSync(preload, `
    const fs = require('node:fs');
    const cp = require('node:child_process');
    const original = cp.spawnSync;
    let injected = false;
    cp.spawnSync = function(command, args, options) {
      if (!injected && options && typeof options.input === 'string') {
        let request;
        try { request = JSON.parse(options.input); } catch {}
        if (request && request.action === 'update' && request.path.endsWith('Next-Agent-Handoff.md')) {
          injected = true;
          fs.renameSync(process.env.AUDIT_TARGET, process.env.AUDIT_DETACHED);
          fs.symlinkSync(process.env.AUDIT_OUTSIDE, process.env.AUDIT_TARGET, 'file');
          fs.writeFileSync(process.env.AUDIT_MARKER, 'injected');
        }
      }
      return original.apply(this, arguments);
    };
    require('node:module').syncBuiltinESMExports();
  `, 'utf8');
  const marker = path.join(parent, 'injected.txt');
  const target = path.join(root, 'Shared-Project-State', 'Next-Agent-Handoff.md');
  const detached = path.join(root, 'Shared-Project-State', 'detached-handoff.md');
  const result = run(['handoff', '--project-root', root, '--from-agent', 'One', '--to-agent', 'Two', '--next-action', 'Test'], skillRoot, {
    NODE_OPTIONS: `--require="${preload.replaceAll('\\', '/')}"`, AUDIT_TARGET: target,
    AUDIT_DETACHED: detached, AUDIT_OUTSIDE: outside, AUDIT_MARKER: marker
  });
  assert.equal(fs.existsSync(marker), true, `The race was not injected: ${result.stderr}`);
  assert.notEqual(result.status, 0);
  assert.equal(fs.readFileSync(outside, 'utf8'), 'outside canary');
  assert.equal(fs.existsSync(detached), true);
});
