#!/usr/bin/env python3
"""Extract release notes from CHANGELOG.rst for a given tag."""
import os
import re

tag = os.environ['TAG']
repo = os.environ['REPO']

with open('CHANGELOG.rst') as f:
    text = f.read()

# Find all version headings
versions = re.findall(r'^(v[\d.]+) [\d/-]+$', text, re.MULTILINE)

# Find current version's section
escaped = re.escape(tag)
pattern = r'^' + escaped + r'.*?(?=^v[\d.]+ [\d/-]+|\Z)'
m = re.search(pattern, text, re.MULTILINE | re.DOTALL)
if m:
    notes = m.group(0).strip()
    # Drop the RST-style heading line and its underline.
    # e.g. "v3.8.1 2026-07-06\n~~~~~~~~~~~~~~~~~" -> remove both.
    lines = notes.splitlines()
    if len(lines) >= 2 and set(lines[1]) <= set('~=-^'):
        notes = '\n'.join(lines[2:]).strip()
else:
    notes = ''

# Find previous version in the same major.minor series for changelog link
prefix = tag.rsplit('.', 1)[0]
prev = ''
found = False
for v in versions:
    if v == tag:
        found = True
        continue
    if found and v.startswith(prefix):
        prev = v
        break
if prev:
    notes += '\n\n**Full Changelog**: https://github.com/' + repo + '/compare/' + prev + '...' + tag

with open('release_notes.md', 'w') as f:
    f.write(notes + '\n')
