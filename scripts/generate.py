import re, shutil, tempfile
from datetime import datetime, timezone
from itertools import pairwise
from pathlib import Path
from mako.template import Template
from mako.lookup import TemplateLookup

PROJECT_URL = "https://github.com/ai-nasir/filterlists"

RFC1034_ISH_FQDN = re.compile(r"^([a-z0-9-]{1,63}\.)+[a-z]{1,63}$")

def validate_fqdn_poorly(dn):
    if len(dn) < 1 or len(dn) > 253:
        return False
    return RFC1034_ISH_FQDN.match(dn)

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

def write_entries(target, entries):
    text = "\n".join(entries)

    target.write_text(text, encoding="utf-8", newline="")

def render(template_file, output_dir, templates, data):
    base = data["source"]
    format = template_file.stem
    output_filename = f"{base}-{format}.txt"

    template = templates.get_template(template_file.name)
    rendered_output = template.render_unicode(**data)

    target = output_dir / output_filename
    target.write_bytes(rendered_output.encode())


input_dir = Path.cwd().parent / "sources"
input_filename = "ai-authored.txt"

source = input_dir / input_filename

entries = read_entries(source)

write_entries(source, entries)

now = datetime.now(timezone.utc)

data = {
    "source": source.stem,
    "version": now.strftime("%Y%m%d%H%M%S"),
    "title": "Ai-nasir's AI-Authored Content Blocklist",
    "description": "Block websites that deceptively serve AI-generated content as human-authored.",
    "project_url": PROJECT_URL,
    "last_modified": now.isoformat(timespec="seconds"),
    "entries": entries
}


template_dir = Path.cwd() / "templates"
temp_mako_path = tempfile.mkdtemp(prefix = "mako_modules")
templates = TemplateLookup(directories=[template_dir], module_directory=temp_mako_path)

output_dir = Path.cwd().parent / "lists"

for template_file in template_dir.glob("*.txt"):
    render(template_file, output_dir, templates, data)

shutil.rmtree(temp_mako_path);
