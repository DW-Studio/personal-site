#!/usr/bin/env python3
"""把 projects.json 渲染进 index.html 的 <!-- REVIEWS:START --> … <!-- REVIEWS:END --> 之间。

用法：python build_reviews.py
只依赖标准库。已填 fields 的项目输出完整复盘；没填的输出「待补」行。
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
DATA = ROOT / "projects.json"
PAGE = ROOT / "index.html"
FIELDS = ["问题", "判断", "做了什么", "结果", "为什么停"]


def esc(t: str) -> str:
    return html.escape(t, quote=False)


def name_html(p: dict) -> str:
    """公开仓库的项目名带链接，私有仓库只写文字（否则访客点开是 404）。"""
    name = esc(p["name"])
    if p.get("repo") and not p.get("private"):
        return (f'<a class="repo" href="{esc(p["repo"])}" target="_blank" rel="noopener">'
                f'{name}<span class="arw">↗</span></a>')
    return name


def render_fields(fields: dict) -> str:
    rows = []
    for k in FIELDS:
        v = (fields.get(k) or "").strip()
        if not v:
            v = '<span class="todo">待补</span>'
        rows.append(f"""        <div class="row"><dt>{k}</dt><dd>{v}</dd></div>""")
    return "\n".join(rows)


def render(p: dict) -> str:
    filled = any((p.get("fields") or {}).get(k) for k in FIELDS)
    status = f'<span class="status">{esc(p["status"])}</span>' if p.get("status") else ""
    sub = f'<p class="rev-sub">{esc(p["sub"])}</p>' if p.get("sub") else ""

    if p.get("featured") and filled:
        return f"""    <article class="rev rev-featured">
      <div class="rev-head">
        <span class="rev-when">{esc(p["when"])}</span>
        <h3>{name_html(p)}</h3>
        {status}
      </div>
      {sub}
      <dl class="rev-dl">
{render_fields(p["fields"])}
      </dl>
    </article>"""

    if filled:
        return f"""    <details class="rev-fold">
      <summary>
        <span class="rev-when">{esc(p["when"])}</span>
        <span class="rev-name">{name_html(p)}</span>
        <span class="rev-brief">{esc(p["sub"])}</span>
        <span class="chev">+</span>
      </summary>
      <dl class="rev-dl">
{render_fields(p["fields"])}
      </dl>
    </details>"""

    return f"""    <div class="rev-empty">
      <span class="rev-when">{esc(p["when"])}</span>
      <span class="rev-name">{name_html(p)}</span>
      <span class="rev-brief"><span class="todo">待回忆</span></span>
    </div>"""


def main() -> None:
    data = json.loads(DATA.read_text(encoding="utf-8"))
    body = "\n".join(render(p) for p in data["projects"])
    page = PAGE.read_text(encoding="utf-8")
    pattern = re.compile(r"(<!-- REVIEWS:START -->)(.*?)(<!-- REVIEWS:END -->)", re.S)
    if not pattern.search(page):
        raise SystemExit("index.html 里找不到 REVIEWS 标记")
    page = pattern.sub(lambda m: m.group(1) + "\n" + body + "\n    " + m.group(3), page)
    PAGE.write_text(page, encoding="utf-8")
    done = sum(1 for p in data["projects"] if any((p.get("fields") or {}).get(k) for k in FIELDS))
    print(f"写入 {len(data['projects'])} 个项目，其中 {done} 个已填复盘")


if __name__ == "__main__":
    main()
