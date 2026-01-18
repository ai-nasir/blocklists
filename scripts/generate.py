import re, shutil, tempfile
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from itertools import pairwise
from pathlib import Path
from typing import List

from mako.lookup import TemplateLookup
from mako.template import Template

PROJECT_URL = "https://github.com/ai-nasir/filterlists"

RFC1034_ISH_FQDN = re.compile(r"^([a-z0-9-]{1,63}\.)+[a-z]{1,63}$")

ALLOW_TOKEN = "-"
EXACT_TOKEN = "^"
TOKENS = re.compile(f"^([{ALLOW_TOKEN}{EXACT_TOKEN}]*)(.+)$")


@dataclass
class Entry:
    hostname: str
    allow: bool
    exact: bool
    sortkey: str


@dataclass
class TemplateData:
    source: str
    version: str
    title: str
    description: str
    project_url: str
    last_modified: str
    entries: List[Entry]


def validate_fqdn_poorly(dn):
    if len(dn) < 1 or len(dn) > 253:
        return False
    return RFC1034_ISH_FQDN.match(dn)


def check_fqdn(dn):
    if not validate_fqdn_poorly(dn):
        raise ValueError(f'"{dn}" does not seem to be a valid lowercase fully qualified domain name')


def to_entry(line):
    allow = False
    exact = False

    match = TOKENS.search(line)
    tokens = match.group(1)
    hostname = match.group(2)
    sortkey = hostname

    if ALLOW_TOKEN in tokens:
        # Allow, presumably for a first-level subdomain of a blocked domain
        allow = True
        # We prefer the entry be sorted adjacent its parent, so switch from sub.domain.tld to domain.tld-sub
        parts = hostname.partition(".")
        sortkey = f"{parts[2]}-{parts[0]}"

    if EXACT_TOKEN in tokens:
        # Exact hostname only, to avoid blocking CDN subdomains
        exact = True

    return Entry(
        hostname=hostname,
        allow=allow,
        exact=exact,
        sortkey=sortkey
    )


def to_line(entry):
    tokens = ""

    if entry.allow:
        tokens += ALLOW_TOKEN

    if entry.exact:
        tokens += EXACT_TOKEN

    return f"{tokens}{entry.hostname}"


def read_entries(source):
    lines = source.read_text(encoding="utf-8", newline="").splitlines()

    entries = [to_entry(line) for line in lines if len(line) > 0]

    for entry in entries:
        check_fqdn(entry.hostname)

    entries.sort(key=lambda e: e.sortkey)

    for a, b in pairwise(entries):
        if a.hostname == b.hostname:
            raise ValueError(f'"{a.hostname}" is duplicated')

    return entries


def write_entries(target, entries):
    lines = [to_line(entry) for entry in entries]

    text = "\n".join(lines)

    target.write_text(text, encoding="utf-8", newline="")


def render(template_file, output_dir, templates, data):
    base = data.source
    template_format = template_file.stem
    output_filename = f"{base}-{template_format}.txt"

    data_dict = {field.name: getattr(data, field.name) for field in fields(data)}

    template = templates.get_template(template_file.name)
    rendered_output = template.render_unicode(**data_dict)

    target = output_dir / output_filename
    target.write_bytes(rendered_output.encode())


def main():
    input_dir = Path.cwd().parent / "sources"
    input_filename = "ai-authored.txt"

    source = input_dir / input_filename

    entries = read_entries(source)

    write_entries(source, entries)

    now = datetime.now(timezone.utc)

    data = TemplateData(
        source=source.stem,
        version=now.strftime("%Y%m%d%H%M%S"),
        title="Ai-nasir's AI-Authored Content Blocklist",
        description="Block websites that deceptively serve AI-generated content as human-authored.",
        project_url=PROJECT_URL,
        last_modified=now.isoformat(timespec="seconds"),
        entries=entries
    )

    template_dir = Path.cwd() / "templates"
    temp_mako_path = tempfile.mkdtemp(prefix="mako_modules")
    templates = TemplateLookup(directories=[template_dir], module_directory=temp_mako_path)

    output_dir = Path.cwd().parent / "lists"

    for template_file in template_dir.glob("*.txt"):
        render(template_file, output_dir, templates, data)

    shutil.rmtree(temp_mako_path)


main()
