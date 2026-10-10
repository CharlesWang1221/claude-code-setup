#!/usr/bin/env python3
"""Deploy repo-owned Skills to Claude; default is a read-only audit."""
import argparse
import hashlib
import json
import re
import shutil
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def tree_hash(root):
    return {
        p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.rglob('*') if p.is_file() and p.name != '.DS_Store'
    }


def write_verified(path, content):
    if path.is_symlink():
        raise RuntimeError('Refusing symlink destination: ' + str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(content)
    temporary.replace(path)
    if path.read_bytes() != content:
        raise RuntimeError('Written file differs: ' + str(path))


def reset_memory(claude_home, workspace):
    # Claude encodes non-alphanumeric path characters with hyphens on both OSes.
    encoded = re.sub(r'[^a-zA-Z0-9]', '-', str(workspace.resolve()))
    memory = claude_home / 'projects' / encoded / 'memory'
    if not memory.exists():
        print('SKIP\tMemory\tNo memory directory for ' + str(workspace))
        return
    if memory.is_symlink():
        raise RuntimeError('Refusing symlink memory directory')
    old = list(memory.glob('*.md'))
    if any(p.is_symlink() for p in old):
        raise RuntimeError('Refusing symlink memory file')
    for item in old:
        item.unlink()
    write_verified(memory / 'MEMORY.md', (
        '# Current project navigation\n\n'
        'Shared rules use the repo codex/AGENTS.global.md master.\n'
        'Read this workspace AGENTS.md and the selected project HANDOFF.md.\n'
        'Do not reuse old task status or overwrite current rules from memory.\n'
    ).encode('utf-8'))
    print('RESET\tMemory\t' + str(len(old)) + ' old Markdown files')


def remove_legacy_hook(claude_home):
    path = claude_home / 'settings.json'
    if not path.exists():
        return
    settings = json.loads(path.read_text(encoding='utf-8-sig'))
    removed = 0
    for event, entries in settings.get('hooks', {}).items():
        kept = []
        for entry in entries:
            hooks = []
            for hook in entry.get('hooks', []):
                command = hook.get('command', '')
                normalized = command.replace('\\', '/').lower()
                if '.claude/skills' in normalized and 'git pull' in normalized:
                    removed += 1
                else:
                    hooks.append(hook)
            if hooks:
                updated = dict(entry)
                updated['hooks'] = hooks
                kept.append(updated)
        settings['hooks'][event] = kept
    if removed:
        write_verified(path, (json.dumps(settings, ensure_ascii=False, indent=2)
                              + '\n').encode('utf-8'))
    print('CLEAN\tHooks\t' + str(removed) + ' obsolete Skill sync hooks')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--claude-home', type=Path,
                        default=Path.home() / '.claude')
    parser.add_argument('--global-rules', action='store_true',
                        help='Also deploy/audit repo-owned shared global rules')
    parser.add_argument('--clean-legacy', action='store_true',
                        help='Delete non-repo Skill directories and old sync hook')
    parser.add_argument('--reset-memory', type=Path, action='append', default=[],
                        help='Delete Markdown memory for this explicit workspace')
    parser.add_argument('--destination', type=Path,
                        help='Override Skill destination for auditing/testing')
    args = parser.parse_args()
    if not args.apply and (args.clean_legacy or args.reset_memory):
        parser.error('--clean-legacy and --reset-memory require --apply')
    source = REPO / 'skills'
    claude_home = args.claude_home.expanduser().absolute()
    destination = (args.destination or claude_home / 'skills').expanduser().absolute()
    if destination.is_symlink():
        raise RuntimeError('Refusing symlink Skill directory')
    names = {p.name for p in source.iterdir() if (p / 'SKILL.md').is_file()}
    if args.apply:
        destination.mkdir(parents=True, exist_ok=True)
    failures = 0
    checked = 0
    for item in sorted(source.iterdir()):
        if not (item / 'SKILL.md').is_file():
            continue
        target = destination / item.name
        expected = tree_hash(item)
        if target.is_symlink():
            raise RuntimeError('Refusing symlink destination: ' + str(target))
        status = 'MISSING' if not (target / 'SKILL.md').is_file() else (
            'MATCH' if expected == tree_hash(target) else 'DIFF')
        if args.apply and status != 'MATCH':
            stage = destination / ('.sync-' + item.name)
            if stage.exists():
                raise RuntimeError('Staging path already exists: ' + str(stage))
            shutil.copytree(item, stage)
            if tree_hash(stage) != expected:
                raise RuntimeError('Staged copy differs: ' + item.name)
            if target.exists():
                shutil.rmtree(target)
            stage.rename(target)
            status = 'MATCH' if tree_hash(target) == expected else 'DIFF'
        print(status + '\tClaude\t' + item.name)
        failures += status != 'MATCH'
        checked += 1
    if args.global_rules:
        expected = (REPO / 'codex/AGENTS.global.md').read_bytes()
        target = claude_home / 'CLAUDE.md'
        if args.apply:
            write_verified(target, expected)
        matches = target.is_file() and target.read_bytes() == expected
        failures += not matches
        print(('MATCH' if matches else 'DIFF') + '\tClaude\tGlobal rules')
    if args.clean_legacy and not failures:
        for item in sorted(destination.iterdir()):
            if item.name.startswith('.') or item.name in names:
                continue
            if item.is_symlink():
                raise RuntimeError('Refusing legacy symlink: ' + str(item))
            if item.is_dir():
                shutil.rmtree(item)
                print('REMOVED\tLegacy\t' + item.name)
        remove_legacy_hook(claude_home)
    if not failures:
        for workspace in args.reset_memory:
            reset_memory(claude_home, workspace.expanduser())
    print(('FAIL' if failures else 'PASS') + '\t' + str(checked)
          + ' repo Skills; ' + str(failures) + ' differences')
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
