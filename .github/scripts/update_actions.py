#!/usr/bin/env python3
"""Check and update GitHub Action versions in workflow files.

Scans every `uses:` step that references a third-party action
(owner/repo@ref) and compares it with the latest stable release of the
upstream repository. In --update mode it rewrites the reference to the
full commit SHA of the latest version, keeping the version number as a
trailing comment, following this repo's convention:

    uses: owner/repo@<40-hex-sha> # vX.Y.Z

Version tags are resolved with `git ls-remote` (no authentication
needed). Annotated tags are resolved to their peeled commit SHA.

Usage:
  update_actions.py [--check | --update] [--dry-run] [--path PATH]

Modes:
  --check    (default) Report outdated or unpinned actions.
             Exit 1 if any are found.
  --update   Rewrite the workflow files in place.
  --dry-run  With --update, print the changes without writing files.
  --path     Scan a specific file or directory instead of
             .github/workflows (default).
"""

import argparse
import os
import re
import subprocess
import sys

USES_RE = re.compile(r'^(\s*(?:-\s+)?)(uses:\s*)([^\s#]+)(.*)$')
SHA_RE = re.compile(r'^[0-9a-f]{40}$')
VERSION_RE = re.compile(r'^v?(\d+)\.(\d+)\.(\d+)$')
VERSION_COMMENT_RE = re.compile(r'#\s*(v?\d+\.\d+\.\d+)\s*$')
SKIP_PREFIXES = ('docker://', './', '../')


def version_key(tag):
    """Sort key for stable vX.Y.Z tags (pre-releases are filtered out)."""
    m = VERSION_RE.match(tag)
    return None if not m else tuple(int(g) for g in m.groups())


def ls_remote_tags(repo):
    """Return {version_tag: commit_sha} for all stable tags of `repo`,
    preferring the peeled commit of annotated tags."""
    url = f'https://github.com/{repo}.git'
    try:
        proc = subprocess.run(
            ['git', 'ls-remote', '--tags', url],
            capture_output=True, text=True, check=True, timeout=60,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
        print(f'  error: could not fetch tags for {repo}: {e}', file=sys.stderr)
        return {}
    tags = {}
    for line in proc.stdout.splitlines():
        sha, _, ref = line.partition('\t')
        if not ref.startswith('refs/tags/'):
            continue
        name = ref[len('refs/tags/'):]
        peeled = name.endswith('^{}')
        if peeled:
            name = name[:-3]
        if version_key(name) is None:
            continue
        # For annotated tags keep the peeled commit; for lightweight tags
        # keep the tag ref itself (which already points at the commit).
        if peeled or name not in tags:
            tags[name] = sha
    return tags


def latest_release(repo):
    """Return (version, commit_sha) of the latest stable release, or
    (None, None) if it could not be determined."""
    tags = ls_remote_tags(repo)
    if not tags:
        return None, None
    best = max(tags, key=version_key)
    return best, tags[best]


def parse_uses(line):
    """Parse a `uses:` line into its parts, or None if not a third-party
    action reference."""
    m = USES_RE.match(line)
    if not m:
        return None
    indent, _, ref, rest = m.groups()
    if ref.startswith(SKIP_PREFIXES) or '@' not in ref or '/' not in ref:
        return None
    action, _, current_ref = ref.partition('@')
    comment = VERSION_COMMENT_RE.search(rest)
    return {
        'indent': indent,
        'action': action,
        'ref': current_ref,
        'version': comment.group(1) if comment else None,
    }


def collect(paths):
    """Yield (path, lineno, parsed) for every action use found."""
    files = []
    for p in paths:
        if os.path.isdir(p):
            for root, _, names in os.walk(p):
                for name in sorted(names):
                    if name.endswith(('.yml', '.yaml')):
                        files.append(os.path.join(root, name))
        else:
            files.append(p)
    for f in sorted(set(files)):
        with open(f, encoding='utf-8') as fh:
            for i, line in enumerate(fh, 1):
                parsed = parse_uses(line.rstrip('\n'))
                if parsed:
                    yield f, i, parsed


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check', action='store_true', help='report only (default)')
    ap.add_argument('--update', action='store_true', help='rewrite files in place')
    ap.add_argument('--dry-run', action='store_true',
                    help='with --update, show changes without writing')
    ap.add_argument('--path', nargs='+', default=['.github/workflows'],
                    help='file or directory to scan (default: .github/workflows)')
    args = ap.parse_args()
    if args.update:
        args.check = False
    if args.dry_run and not args.update:
        ap.error('--dry-run requires --update')

    entries = list(collect(args.path))
    if not entries:
        print('no action uses found')
        return 1

    cache = {}
    outdated = []
    errors = []
    print(f'{"action":<34} {"current":<12} {"latest":<12} status')
    print('-' * 76)

    # Group entries by file so each file is only rewritten once.
    by_file = set()
    for f, lineno, parsed in entries:
        by_file.add(f)
        action = parsed['action']
        if action not in cache:
            cache[action] = latest_release(action)
        latest_version, latest_sha = cache[action]

        pinned = SHA_RE.match(parsed['ref']) is not None
        if latest_sha is None:
            errors.append((f, lineno, action, 'could not determine latest release'))
            status = 'ERROR'
        elif pinned and parsed['ref'] == latest_sha:
            status = 'up to date'
        else:
            outdated.append((f, lineno, parsed, latest_version, latest_sha))
            status = 'OUTDATED' if pinned else 'UNPINNED'
        print(f'{action:<34} {parsed["version"] or parsed["ref"][:7]:<12} '
              f'{latest_version or "-":<12} {status}')

    print()
    if not outdated and not errors:
        print('all actions are up to date and pinned to a commit SHA')
        return 0

    if errors:
        print(f'{len(errors)} error(s):')
        for f, lineno, action, msg in errors:
            print(f'  {f}:{lineno} {action}: {msg}')

    if args.check:
        print(f'{len(outdated)} action(s) outdated or unpinned')
        return 1

    # Apply updates.
    for f in sorted(by_file):
        updates = {(ln, p['action'], p['ref']): (v, s)
                   for (ff, ln, p, v, s) in outdated if ff == f}
        with open(f, encoding='utf-8') as fh:
            original = fh.readlines()
        rewritten = []
        changed = False
        for lineno, line in enumerate(original, 1):
            stripped = line.rstrip('\n')
            parsed = parse_uses(stripped)
            key = (lineno, parsed['action'], parsed['ref']) if parsed else None
            if key in updates:
                version, sha = updates[key]
                new_line = f'{parsed["indent"]}uses: {parsed["action"]}@{sha} # {version}\n'
                changed = changed or new_line != line
                if not args.dry_run:
                    line = new_line
                elif new_line != line:
                    print(f'{f}:{lineno}')
                    print(f'  - {stripped}')
                    print(f'  + {new_line.rstrip()}')
            rewritten.append(line)
        if changed and not args.dry_run:
            with open(f, 'w', encoding='utf-8') as fh:
                fh.writelines(rewritten)
            print(f'updated {f}')

    if args.dry_run:
        print(f'\n{len(outdated)} action(s) would be updated')
    else:
        print(f'\nupdated {len(outdated)} action(s)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
