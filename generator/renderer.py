from __future__ import annotations
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime, timezone
import os
from urllib.parse import urlparse

from .config import cfg
from .utils import ensure_dir


def _env() -> Environment:
    loader = FileSystemLoader("templates")
    env = Environment(loader=loader, autoescape=select_autoescape(["html", "xml"]))
    # Suporte a GitHub Pages em subcaminho: extrai base path do SITE_URL
    parsed = urlparse(cfg.SITE_URL)
    base_path = parsed.path if parsed and parsed.path else "/"
    if not base_path.endswith("/"):
        base_path = base_path + "/"
    env.globals.update({
        "SITE_NAME": cfg.SITE_NAME,
        "SITE_TAGLINE": cfg.SITE_TAGLINE,
        "SITE_URL": cfg.SITE_URL,
        "GA_MEASUREMENT_ID": cfg.GA_MEASUREMENT_ID,
        "BASE_PATH": base_path,
    })
    return env


def render_article(outdir: str, article: dict) -> str:
    env = _env()
    tpl = env.get_template("article.html")
    html = tpl.render(article=article)
    ensure_dir(outdir)
    path = os.path.join(outdir, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path


def render_index(outdir: str, posts: list[dict]) -> str:
    env = _env()
    tpl = env.get_template("index.html")
    html = tpl.render(posts=posts)
    path = os.path.join(outdir, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path


def render_page(outdir: str, page: dict) -> str:
    env = _env()
    tpl = env.get_template("page.html")
    html = tpl.render(page=page)
    path = os.path.join(outdir, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path


def render_sitemap(outdir: str, urls: list[str]) -> str:
    env = _env()
    tpl = env.get_template("sitemap.xml.j2")
    xml = tpl.render(urls=urls, now=datetime.now(timezone.utc).isoformat())
    path = os.path.join(outdir, "sitemap.xml")
    with open(path, "w", encoding="utf-8") as f:
        f.write(xml)
    return path


def render_robots(outdir: str) -> str:
    env = _env()
    tpl = env.get_template("robots.txt.j2")
    txt = tpl.render()
    path = os.path.join(outdir, "robots.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(txt)
    return path
