import os, re
from pathlib import Path
from datetime import datetime, timezone
from mako.template import Template

rfc_ish_fqdn = re.compile(r"^([a-z0-9-]{1,63}\.)+[a-z]{1,63}$")

def validate_fqdn_poorly(dn):
    if len(dn) < 1 or len(dn) > 253:
        return False
    return rfc_ish_fqdn.match(dn)

def ensure_fqdn(dn):
    if not validate_fqdn_poorly(dn):
        raise ValueError(f'"{dn}" does not seem to be a valid lowercase fully qualified domain name')

output_dir = "."
output_filename = "ai-spam-abp.txt"

template = Template("""\
[Adblock Plus]
! Version: ${ version }
! Title: ${ title }
! Description: ${ description }
! Syntax: Adblock Plus Filter List
! Entries: ${ len(rows) }
! Last modified: ${ date }
! Expires: 1 hours
! License: ${ url }/LICENSE
! Homepage: ${ url }

% for row in rows:
||${ row }^
% endfor
""")

input_dir = Path.cwd().parent

source = input_dir / "ai-spam.txt"
with source.open() as f:
    rows = f.read().splitlines()

for row in rows:
    ensure_fqdn(row)

now = datetime.now(tz=timezone.utc)

data = {
    "version": now.strftime("%Y%m%d%H%M%S"),
    "title": "AI Spam",
    "description": "Target websites that fraudulently host AI-generated content masquerading as human-authored",
    "url": "https://github.com/ai-nasir/blocklists",
    "date": now.isoformat(),
    "rows": rows
}

try:
    rendered_output = template.render_unicode(**data)
except:
    print(mako_exceptions.text_error_template().render())

with open(f"{output_dir}{os.path.sep}{os.path.basename(output_filename)}", "wb") as outfile:
    outfile.write(rendered_output.encode())
