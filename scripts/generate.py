import os
from pathlib import Path
from datetime import datetime, timezone
from mako.template import Template


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

source = Path.cwd().parent / "ai-spam.txt"
with source.open() as f:
    rows = f.read().splitlines()

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
