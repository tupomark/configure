"""Печать README через Chromium в PDF (аналог Ctrl+P браузера)."""

from pathlib import Path
import markdown
from playwright.sync_api import sync_playwright

STYLE = """
@page { size: A4; margin: 17mm; }
body { font: 11pt Arial, sans-serif; color: #20252b; line-height: 1.45; }
h1 { font-size: 21pt; } h2 { font-size: 15pt; margin-top: 22pt; }
h1,h2,h3 { break-after: avoid; }
pre { background: #f3f5f7; padding: 10px; white-space: pre-wrap;
      overflow-wrap: anywhere; font-size: 9pt; break-inside: avoid; }
code { font-size: 9pt; overflow-wrap: anywhere; }
table { width: 100%; border-collapse: collapse; font-size: 9pt; }
th,td { border: 1px solid #ccd2d8; padding: 6px; text-align: left; }
a { color: #245488; overflow-wrap: anywhere; }
"""


def main():
    """Отобразить Markdown и сохранить браузерную печатную версию."""
    text = Path("README.md").read_text(encoding="utf-8")
    content = markdown.markdown(text, extensions=["fenced_code", "tables"])
    html = f'<meta charset="utf-8"><style>{STYLE}</style>{content}'
    Path("output").mkdir(exist_ok=True)
    with sync_playwright() as runtime:
        browser = runtime.chromium.launch()
        page = browser.new_page()
        page.set_content(html)
        page.pdf(path="output/README_PR2_V31.pdf", print_background=True)
        browser.close()


if __name__ == "__main__":
    main()
