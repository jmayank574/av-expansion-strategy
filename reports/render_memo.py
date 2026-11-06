"""Render reports/memo.md to memo_preview.html and memo_preview.pdf (Python-Markdown + headless Edge/Chrome) and verify it.

Checks: the PDF is one Letter page, and every bullet in the markdown became a real <li> (not folded into a paragraph).
Usage: python reports/render_memo.py
"""
import pathlib, re, shutil, subprocess, sys
import markdown

HERE = pathlib.Path(__file__).resolve().parent
CSS = ("@page{size:Letter;margin:0.6in}body{font-family:Calibri,Arial,sans-serif;font-size:10pt;line-height:1.28;color:#111}"
       "h1{font-size:15pt;margin:0 0 4px}p{margin:5px 0}ul{margin:3px 0 3px 18px;padding:0}li{margin:1px 0}code{font-size:9pt}")
BROWSERS = [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe", "msedge", "google-chrome", "chromium", "chrome"]


def render():
    md = (HERE / "memo.md").read_text(encoding="utf-8")
    html = markdown.markdown(md)
    page = f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{html}</body></html>"
    (HERE / "memo_preview.html").write_text(page, encoding="utf-8")
    bullets_md = len(re.findall(r"^- ", md, flags=re.M))
    bullets_html = html.count("<li>")
    ok = bullets_md == bullets_html and bullets_md > 0
    print(f"bullets in markdown: {bullets_md}; rendered <li>: {bullets_html} -> {'OK' if ok else 'FAIL (list not preceded by a blank line?)'}")
    exe = next((b for b in BROWSERS if pathlib.Path(b).exists() or shutil.which(b)), None)
    if not exe:
        print("no Edge/Chrome found: HTML written, PDF skipped"); return ok
    pdf = HERE / "memo_preview.pdf"
    subprocess.run([exe, "--headless", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", (HERE / "memo_preview.html").as_uri()],
                   check=True, capture_output=True, timeout=120)
    pages = len(re.findall(rb"/Type\s*/Page[^s]", pdf.read_bytes()))
    print(f"PDF pages: {pages} -> {'OK' if pages == 1 else 'FAIL (memo spills past one page)'}")
    return ok and pages == 1


if __name__ == "__main__":
    sys.exit(0 if render() else 1)
