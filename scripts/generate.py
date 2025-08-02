import os
from datetime import datetime, timezone
from mako.template import Template


output_dir = "."
output_filename = "ai-spam-abp.txt"

template = Template("""\
[Adblock Plus]
! Version: ${ version }
! Title: AI Spam
! Description: Target websites that fraudulently host AI-generated content masquerading as human-authored
! Syntax: Adblock Plus Filter List
! Entries: ${ len(rows) }
! Last modified: ${ date }
! Expires: 1 hours
! License: https://github.com/ai-nasir/blocklists/LICENSE
! Homepage: https://github.com/ai-nasir/blocklists

% for row in rows:
||${ row }^
% endfor
"""))
""")

now = datetime.now(tz=timezone.utc)

data = {
    "version": now.strftime("%Y%m%d%H%M%S"),
    "date": now.isoformat(),
    "rows": [
        "hairspeaks.net",
        "chefsresource.com",
        "vtechinsider.com"
    ]
}

try:
    rendered_output = template.render_unicode(**data)
except:
    print(mako_exceptions.text_error_template().render())

with open(f"{output_dir}{os.path.sep}{os.path.basename(output_filename)}", "wb") as outfile:
    outfile.write(rendered_output.encode())
