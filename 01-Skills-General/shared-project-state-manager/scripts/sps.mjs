#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const SKILL_ROOT = path.resolve(SCRIPT_DIR, '..');
const TEMPLATE_ROOT = path.join(SKILL_ROOT, 'templates');
const STATE_ROOT_NAME = 'Shared-Project-State';
const REQUIRED_ROOT_FILES = [
  'README.md',
  'State-Manifest.json',
  'Current-State.md',
  'Next-Agent-Handoff.md',
  'Root-Exceptions.md',
  'File-Operations-Policy.md'
];

function fail(message, code = 1) {
  console.error(`ERROR: ${message}`);
  process.exit(code);
}

function info(message) {
  console.log(message);
}

function parseArgs(argv) {
  const positional = [];
  const flags = {};
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith('--')) {
      positional.push(token);
      continue;
    }
    const key = token.slice(2);
    const next = argv[i + 1];
    if (next !== undefined && !next.startsWith('--')) {
      flags[key] = next;
      i += 1;
    } else {
      flags[key] = true;
    }
  }
  return { positional, flags };
}

function projectRoot(flags) {
  return path.resolve(String(flags['project-root'] || process.cwd()));
}

function stateRoot(flags) {
  return path.join(projectRoot(flags), STATE_ROOT_NAME);
}

function ensureWithin(root, target) {
  const rel = path.relative(path.resolve(root), path.resolve(target));
  if (rel.startsWith('..') || path.isAbsolute(rel)) {
    fail(`Path escapes project root: ${target}`);
  }
}

function nowIso() {
  return new Date().toISOString();
}

function slug(value) {
  return String(value || '')
    .trim()
    .replace(/[^A-Za-z0-9._-]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '') || 'Task';
}

function readText(file) {
  return fs.readFileSync(file, 'utf8');
}

function writeText(file, content, { overwrite = false } = {}) {
  if (fs.existsSync(file) && !overwrite) return false;
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, content, 'utf8');
  return true;
}

function renderTemplate(name, values) {
  const source = readText(path.join(TEMPLATE_ROOT, name));
  return source.replace(/\{\{([A-Z0-9_]+)\}\}/g, (_, key) => String(values[key] ?? `{{${key}}}`));
}

function loadManifest(root) {
  const file = path.join(root, 'State-Manifest.json');
  if (!fs.existsSync(file)) fail(`Missing ${file}. Run 'sps init' first.`);
  try {
    return JSON.parse(readText(file));
  } catch (error) {
    fail(`State-Manifest.json is invalid JSON: ${error.message}`);
  }
}

function saveManifest(root, manifest) {
  manifest.updated_at = nowIso();
  fs.writeFileSync(path.join(root, 'State-Manifest.json'), `${JSON.stringify(manifest, null, 2)}\n`, 'utf8');
}

function gitSnapshot(root) {
  const base = { branch: null, head_sha: null, working_tree: 'UNKNOWN' };
  const inside = spawnSync('git', ['-C', root, 'rev-parse', '--is-inside-work-tree'], { encoding: 'utf8' });
  if (inside.status !== 0 || inside.stdout.trim() !== 'true') return base;
  const branch = spawnSync('git', ['-C', root, 'branch', '--show-current'], { encoding: 'utf8' });
  const head = spawnSync('git', ['-C', root, 'rev-parse', 'HEAD'], { encoding: 'utf8' });
  const status = spawnSync('git', ['-C', root, 'status', '--porcelain'], { encoding: 'utf8' });
  return {
    branch: branch.status === 0 ? branch.stdout.trim() || '(detached)' : null,
    head_sha: head.status === 0 ? head.stdout.trim() : null,
    working_tree: status.status === 0 ? (status.stdout.trim() ? 'dirty' : 'clean') : 'UNKNOWN'
  };
}

function commandInit(flags) {
  const root = projectRoot(flags);
  if (!fs.existsSync(root) || !fs.statSync(root).isDirectory()) fail(`Project root does not exist: ${root}`);
  const shared = path.join(root, STATE_ROOT_NAME);
  ensureWithin(root, shared);
  const title = String(flags.title || 'Untitled Task');
  const taskId = slug(flags['task-id'] || `Task-${new Date().toISOString().slice(0, 10)}-${title}`);
  const agent = String(flags.agent || 'Unknown-Agent');
  const git = gitSnapshot(root);
  const values = {
    TASK_ID: taskId,
    TASK_TITLE: title,
    AGENT: agent,
    UPDATED_AT: nowIso(),
    BRANCH: git.branch || 'N/A',
    HEAD_SHA: git.head_sha || 'N/A',
    WORKING_TREE: git.working_tree
  };

  const dirs = [
    shared,
    path.join(shared, 'Tasks', taskId, 'Checkpoints'),
    path.join(shared, 'Tasks', taskId, 'Phase-Reports'),
    path.join(shared, 'Tasks', taskId, 'Test-Reports'),
    path.join(shared, 'Tasks', taskId, 'Agent-Sessions'),
    path.join(shared, 'Tool-State'),
    path.join(shared, 'Temporary-Files', taskId),
    path.join(shared, 'Cache'),
    path.join(shared, 'Test-Workspace', taskId),
    path.join(shared, 'Logs', taskId),
    path.join(shared, 'Quarantine', 'Items'),
    path.join(shared, 'Quarantine', 'Records')
  ];
  dirs.forEach((d) => fs.mkdirSync(d, { recursive: true }));

  const mappings = [
    ['Project-State.md', path.join(shared, 'Current-State.md')],
    ['Handoff.md', path.join(shared, 'Next-Agent-Handoff.md')],
    ['Root-Exceptions.md', path.join(shared, 'Root-Exceptions.md')],
    ['File-Operations-Policy.md', path.join(shared, 'File-Operations-Policy.md')],
    ['Task-State.md', path.join(shared, 'Tasks', taskId, 'Task-Plan.md')],
    ['Verification.md', path.join(shared, 'Tasks', taskId, 'Test-Status.md')],
    ['Decision-Log.md', path.join(shared, 'Tasks', taskId, 'Decision-Log.md')],
    ['File-Change-Map.md', path.join(shared, 'Tasks', taskId, 'File-Change-Map.md')],
    ['Blockers.md', path.join(shared, 'Tasks', taskId, 'Blockers.md')]
  ];
  let created = 0;
  mappings.forEach(([template, dest]) => {
    if (writeText(dest, renderTemplate(template, values))) created += 1;
  });

  const stateReadme = `# Shared Project State\n\nCanonical operational state for resumable work.\n\n- Active task: \`${taskId}\`\n- Created by: ${agent}\n- Created at: ${values.UPDATED_AT}\n\nRead \`State-Manifest.json\`, \`Current-State.md\`, and \`Next-Agent-Handoff.md\` before resuming work.\n`;
  if (writeText(path.join(shared, 'README.md'), stateReadme)) created += 1;

  const manifestPath = path.join(shared, 'State-Manifest.json');
  if (!fs.existsSync(manifestPath)) {
    const manifest = JSON.parse(renderTemplate('State-Manifest.json', values));
    fs.writeFileSync(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`, 'utf8');
    created += 1;
  }

  info(`Initialized ${shared}`);
  info(`Task: ${taskId}`);
  info(`Created ${created} new state file(s); existing files were preserved.`);
}

function commandStatus(flags) {
  const shared = stateRoot(flags);
  const manifest = loadManifest(shared);
  const git = gitSnapshot(projectRoot(flags));
  console.log(JSON.stringify({
    project_root: projectRoot(flags),
    state_root: shared,
    task_id: manifest.task_id,
    task_title: manifest.task_title,
    task_status: manifest.task_status,
    active_phase: manifest.active_phase,
    state_health: manifest.state_health,
    next_action: manifest.next_action,
    recorded: {
      branch: manifest.branch,
      head_sha: manifest.head_sha,
      working_tree: manifest.working_tree,
      updated_by: manifest.updated_by,
      updated_at: manifest.updated_at
    },
    current_git: git
  }, null, 2));
}

function commandDoctor(flags) {
  const root = projectRoot(flags);
  const shared = path.join(root, STATE_ROOT_NAME);
  const problems = [];
  if (!fs.existsSync(shared)) problems.push(`Missing ${STATE_ROOT_NAME}; run 'sps init'.`);
  else {
    for (const file of REQUIRED_ROOT_FILES) {
      if (!fs.existsSync(path.join(shared, file))) problems.push(`Missing ${file}`);
    }
    try {
      const manifest = loadManifest(shared);
      for (const key of ['schema_version', 'task_id', 'task_status', 'state_health', 'next_action']) {
        if (!manifest[key]) problems.push(`State-Manifest.json missing '${key}'`);
      }
    } catch (error) {
      problems.push(String(error.message || error));
    }
  }
  const py = spawnSync(process.platform === 'win32' ? 'python' : 'python3', ['--version'], { encoding: 'utf8' });
  const result = {
    node: process.version,
    platform: `${process.platform} ${os.release()}`,
    project_root: root,
    project_writable: (() => { try { fs.accessSync(root, fs.constants.W_OK); return true; } catch { return false; } })(),
    python_available: py.status === 0,
    python_version: py.status === 0 ? (py.stdout || py.stderr).trim() : null,
    git: gitSnapshot(root),
    problems
  };
  console.log(JSON.stringify(result, null, 2));
  process.exit(problems.length ? 2 : 0);
}

function nextCheckpointNumber(dir) {
  if (!fs.existsSync(dir)) return 1;
  const nums = fs.readdirSync(dir)
    .map((n) => /^CP-(\d+)\.md$/.exec(n))
    .filter(Boolean)
    .map((m) => Number(m[1]));
  return (nums.length ? Math.max(...nums) : 0) + 1;
}

function commandCheckpoint(flags) {
  const root = projectRoot(flags);
  const shared = path.join(root, STATE_ROOT_NAME);
  const manifest = loadManifest(shared);
  const taskId = manifest.task_id;
  const dir = path.join(shared, 'Tasks', taskId, 'Checkpoints');
  fs.mkdirSync(dir, { recursive: true });
  const n = nextCheckpointNumber(dir);
  const file = path.join(dir, `CP-${String(n).padStart(3, '0')}.md`);
  const git = gitSnapshot(root);
  const values = {
    TASK_ID: taskId,
    TASK_TITLE: manifest.task_title || taskId,
    AGENT: String(flags.agent || manifest.updated_by || 'Unknown-Agent'),
    UPDATED_AT: nowIso(),
    BRANCH: git.branch || 'N/A',
    HEAD_SHA: git.head_sha || 'N/A',
    WORKING_TREE: git.working_tree,
    PHASE: String(flags.phase || manifest.active_phase || 'N/A'),
    LAST_VERIFIED: String(flags['last-verified'] || 'Not provided'),
    NEXT_ACTION: String(flags['next-action'] || manifest.next_action || 'Not provided'),
    NOTE: String(flags.note || '')
  };
  writeText(file, renderTemplate('Checkpoint.md', values), { overwrite: true });
  manifest.updated_by = values.AGENT;
  manifest.branch = git.branch;
  manifest.head_sha = git.head_sha;
  manifest.working_tree = git.working_tree;
  manifest.next_action = values.NEXT_ACTION;
  saveManifest(shared, manifest);
  info(`Checkpoint created: ${path.relative(root, file)}`);
}

function commandHandoff(flags) {
  const root = projectRoot(flags);
  const shared = path.join(root, STATE_ROOT_NAME);
  const manifest = loadManifest(shared);
  const git = gitSnapshot(root);
  const fromAgent = String(flags['from-agent'] || manifest.updated_by || 'Unknown-Agent');
  const toAgent = String(flags['to-agent'] || 'Next-Agent');
  const nextAction = String(flags['next-action'] || manifest.next_action || 'Inspect current state and continue.');
  const lastVerified = String(flags['last-verified'] || 'See Current-State.md and latest checkpoint.');
  const values = {
    TASK_ID: manifest.task_id,
    TASK_TITLE: manifest.task_title || manifest.task_id,
    AGENT: fromAgent,
    NEXT_AGENT: toAgent,
    UPDATED_AT: nowIso(),
    BRANCH: git.branch || 'N/A',
    HEAD_SHA: git.head_sha || 'N/A',
    WORKING_TREE: git.working_tree,
    LAST_VERIFIED: lastVerified,
    NEXT_ACTION: nextAction
  };
  fs.writeFileSync(path.join(shared, 'Next-Agent-Handoff.md'), renderTemplate('Handoff.md', values), 'utf8');
  manifest.updated_by = fromAgent;
  manifest.next_agent = toAgent;
  manifest.next_action = nextAction;
  manifest.branch = git.branch;
  manifest.head_sha = git.head_sha;
  manifest.working_tree = git.working_tree;
  saveManifest(shared, manifest);
  info(`Handoff prepared from ${fromAgent} to ${toAgent}.`);
}

function commandFiles(argv) {
  const python = process.platform === 'win32' ? 'python' : 'python3';
  const script = path.join(SCRIPT_DIR, 'safe_file_ops.py');
  const result = spawnSync(python, [script, ...argv], { stdio: 'inherit' });
  if (result.error) fail(`Unable to run ${python}: ${result.error.message}`);
  process.exit(result.status ?? 1);
}

function usage() {
  console.log(`Shared Project State Manager CLI\n\nUsage:\n  node scripts/sps.mjs init --project-root <path> --task-id <id> --title <title> --agent <name>\n  node scripts/sps.mjs status --project-root <path>\n  node scripts/sps.mjs doctor --project-root <path>\n  node scripts/sps.mjs checkpoint --project-root <path> --last-verified <text> --next-action <text>\n  node scripts/sps.mjs handoff --project-root <path> --from-agent <name> --to-agent <name> --next-action <text>\n  node scripts/sps.mjs files <safe_file_ops.py arguments>\n\nFile operations example:\n  node scripts/sps.mjs files diagnose .\\temp --project-root .\n`);
}

const rawArgs = process.argv.slice(2);
const { positional, flags } = parseArgs(rawArgs);
const command = positional.shift();
if (!command || ['help', '-h', '--help'].includes(command)) {
  usage();
  process.exit(0);
}

switch (command) {
  case 'init': commandInit(flags); break;
  case 'status': commandStatus(flags); break;
  case 'doctor': commandDoctor(flags); break;
  case 'checkpoint': commandCheckpoint(flags); break;
  case 'handoff': commandHandoff(flags); break;
  case 'files': commandFiles(rawArgs.slice(1)); break;
  default: fail(`Unknown command '${command}'. Run with 'help'.`);
}
