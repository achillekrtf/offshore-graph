"""Build report/report.pdf from report/report.md (markdown -> HTML -> Chrome headless).
Usage: uv run --no-project --with markdown python report/build_pdf.py
"""
import re, subprocess, sys
from pathlib import Path
import markdown

here = Path(__file__).resolve().parent
md = (here / "report.md").read_text()
meta = {}
m = re.match(r"---\n(.*?)\n---\n", md, re.S)
if m:
    for line in m.group(1).splitlines():
        k, v = line.split(":", 1); meta[k.strip()] = v.strip().strip('"')
    md = md[m.end():]
md = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)\{width=(\d+)%\}",
            lambda x: f'<figure><img src="{x.group(2)}" style="width:{x.group(3)}%"><figcaption>{x.group(1)}</figcaption></figure>', md)
md = re.sub(r"\$([^$]+)\$", r"<i>\1</i>", md)
body = markdown.markdown(md, extensions=["tables", "fenced_code"])
css = """body{font-family:Helvetica,Arial,sans-serif;font-size:10.5pt;line-height:1.4;margin:0;color:#111}
h1{font-size:20pt;margin:0 0 4pt}h2{font-size:14pt;margin:16pt 0 6pt;border-bottom:1px solid #ccc;padding-bottom:2pt}
.sub,.auth{color:#444;margin:0 0 3pt}table{border-collapse:collapse;margin:8pt 0;font-size:9.5pt}
td,th{border:1px solid #bbb;padding:3pt 6pt;text-align:left}th{background:#f0f0f0}
figure{margin:8pt 0;text-align:center;page-break-inside:avoid}figcaption{font-size:9pt;color:#555}
blockquote{background:#fff4d6;margin:8pt 0;padding:4pt 10pt;border-left:3px solid #e0a800}
p:has(+ul),p:has(+table),p:has(+figure){break-after:avoid}h2{break-after:avoid}table{break-inside:avoid}@page{size:A4;margin:18mm}"""
head = f'<h1>{meta.get("title","")}</h1><p class="sub">{meta.get("subtitle","")}</p><p class="auth">{meta.get("author","")} - {meta.get("date","")}</p>'
html = f"<!doctype html><meta charset=utf-8><style>{css}</style>{head}{body}"
out = here / "report.html"; out.write_text(html)
chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
subprocess.run([chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                f"--print-to-pdf={here/'report.pdf'}", out.as_uri()], check=True, capture_output=True)
print("wrote", here / "report.pdf")
