import re
from datetime import datetime, timezone
from itertools import pairwise
from pathlib import Path
from mako.template import Template

rfc1034_ish_fqdn = re.compile(r"^([a-z0-9-]{1,63}\.)+[a-z]{1,63}$")

def validate_fqdn_poorly(dn):
    if len(dn) < 1 or len(dn) > 253:
        return False
    return rfc1034_ish_fqdn.match(dn)

def check_fqdn(dn):
    if not validate_fqdn_poorly(dn):
        raise ValueError(f'"{dn}" does not seem to be a valid lowercase fully qualified domain name')

def read_entries(source):
    lines = source.read_text(encoding="utf-8", newline="").splitlines()

    entries = [entry for entry in lines if len(entry) > 0]

    for entry in entries:
        check_fqdn(entry)

    entries.sort()

    for a, b in pairwise(entries):
        if a == b:
            raise ValueError(f'"{a}" is duplicated')

    return entries


template = Template("""\
[Adblock Plus]
! Version: ${ version }
! Title: ${ title }
! Description: ${ description }
! Syntax: Adblock Plus Filter List
! Entries: ${ len(entries) }
! Last modified: ${ last_modified }
! Expires: 1 hours
! License: ${ project_url }/LICENSE
! Homepage: ${ project_url }

% for entry in entries:
||${ entry }^
% endfor
""")

input_dir = Path.cwd().parent
output_dir = Path.cwd().parent

input_filename = "ai-spam.txt"
output_filename = "ai-spam-abp.txt"

source = input_dir / input_filename

entries = read_entries(source)

now = datetime.now(tz=timezone.utc)

data = {
    "version": now.strftime("%Y%m%d%H%M%S"),
    "title": "AI Spam",
    "description": "Target websites that fraudulently host AI-generated content masquerading as human-authored",
    "project_url": "https://github.com/ai-nasir/blocklists",
    "last_modified": now.isoformat(),
    "entries": entries
}

rendered_output = template.render_unicode(**data)

target = output_dir / output_filename
target.write_bytes(rendered_output.encode())
