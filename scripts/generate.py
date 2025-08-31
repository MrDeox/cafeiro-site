#!/usr/bin/env python3
from __future__ import annotations
import argparse
import os
from datetime import datetime

from generator.config import cfg
from generator.utils import ensure_dir, slugify, write_text, read_text
from generator.renderer import render_article, render_index, render_page, render_sitemap, render_robots
from generator.llm import gen_title_and_description, gen_article_body
from generator.affiliate import render_cta_links
from generator.images import generate_image


SEED_PATH = "data/keywords.txt"


def load_seeds() -> list[str]:
    if not os.path.exists(SEED_PATH):
        return [
            "como fazer café coado",
            "moedor de café para iniciantes",
            "melhor cafeteira italiana",
            "como usar prensa francesa",
            "proporção café e água",
            "moagem para aeropress",
            "café gelado em casa",
            "balança para café",
            "filtro de papel vs metal",
            "como armazenar café em grãos",
        ]
    with open(SEED_PATH, "r", encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip()]


def outline_from_keyword(keyword: str) -> list[str]:
    k = keyword.lower()
    base = [
        "Materiais e itens necessários",
        "Passo a passo simplificado",
        "Erros comuns e como evitar",
        "Ajustes finos e variações",
    ]
    if "moedor" in k or "moagem" in k:
        base.insert(1, "Tipos de moedores e moagens")
    if "cafeteira" in k or "método" in k or "metodo" in k:
        base.insert(1, "Como funciona o método")
    if "proporção" in k or "proporcao" in k:
        base.insert(1, "Entendendo proporções e receitas")
    return base


def build_article(keyword: str, used_llm: dict) -> dict:
    title, description = gen_title_and_description(keyword)
    outline = outline_from_keyword(keyword)

    # Cache por slug
    slug = slugify(keyword)
    cache_dir = os.path.join(cfg.CACHE_DIR, "llm")
    ensure_dir(cache_dir)
    cache_file = os.path.join(cache_dir, f"{slug}.md")
    body = read_text(cache_file)

    if body is None and cfg.GENERATE_WITH_LLM and used_llm.get("count", 0) < cfg.LLM_MAX_CALLS_PER_RUN:
        body = gen_article_body(keyword, outline)
        # Se veio do LLM, persiste cache para rodadas futuras
        if body:
            write_text(cache_file, body)
            used_llm["count"] = used_llm.get("count", 0) + 1

    if body is None:
        body = gen_article_body(keyword, outline)

    ctas = render_cta_links(keyword)
    # Imagem (com limite por run)
    image_url = None
    image_alt = None
    if cfg.GENERATE_IMAGES and used_llm.get("img", 0) < cfg.IMG_MAX_CALLS_PER_RUN:
        res = generate_image(keyword, title)
        if res:
            image_url, image_alt = res
            used_llm["img"] = used_llm.get("img", 0) + 1
    return {
        "slug": slug,
        "url": f"{cfg.SITE_URL}/posts/{slug}/",
        "title": title,
        "description": description,
        "keyword": keyword,
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "body_md": body,
        "ctas": ctas,
        "image_url": image_url,
        "image_alt": image_alt,
    }


def markdown_to_html(md: str) -> str:
    # Conversão muito simples: apenas títulos e listas básicas.
    # Para manter leve, sem dependência pesada de markdown.
    import re
    html = md
    html = re.sub(r"^### (.*)$", r"<h3>\1</h3>", html, flags=re.MULTILINE)
    html = re.sub(r"^## (.*)$", r"<h2>\1</h2>", html, flags=re.MULTILINE)
    html = re.sub(r"^# (.*)$", r"<h1>\1</h1>", html, flags=re.MULTILINE)
    # listas
    lines = html.splitlines()
    out = []
    in_ul = False
    for line in lines:
        if line.strip().startswith("- ") or line.strip().startswith("* "):
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{line.strip()[2:]}</li>")
        else:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if line.strip() == "":
                out.append("")
            else:
                out.append(f"<p>{line}</p>")
    if in_ul:
        out.append("</ul>")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-posts", type=int, default=None, help="Limitar total de posts renderizados")
    args = parser.parse_args()

    seeds = load_seeds()[: cfg.MAX_POSTS_TOTAL]
    used_llm = {"count": 0}

    posts: list[dict] = []
    for kw in seeds:
        article = build_article(kw, used_llm)
        # Render post
        outdir = os.path.join(cfg.OUTPUT_DIR, "posts", article["slug"])
        article_html = markdown_to_html(article["body_md"]) if article.get("body_md") else ""
        article_render = {
            **article,
            "body_html": article_html,
        }
        render_article(outdir, article_render)
        posts.append(article_render)

        if args.max_posts and len(posts) >= args.max_posts:
            break

    # Index
    posts_sorted = sorted(posts, key=lambda x: x["slug"])  # simples
    render_index(cfg.OUTPUT_DIR, posts_sorted)

    # Páginas estáticas
    pages = [
        {
            "slug": "sobre",
            "title": "Sobre o " + cfg.SITE_NAME,
            "description": "Quem somos e nossa missão.",
            "body_html": "<p>Publicamos guias práticos e selecionamos produtos úteis para café em casa. Conteúdo sem enrolação, com foco no que realmente ajuda você a fazer um café melhor.</p>",
        },
        {
            "slug": "privacidade",
            "title": "Política de Privacidade",
            "description": "Como tratamos dados e cookies.",
            "body_html": "<p>Usamos ferramentas de analytics e afiliados. Não vendemos seus dados. Consulte esta página periodicamente para atualizações.</p>",
        },
        {
            "slug": "afiliados",
            "title": "Aviso de Afiliados",
            "description": "Links podem gerar comissões sem custo extra.",
            "body_html": "<p>Participamos de programas de afiliados. Ao comprar por nossos links, podemos ganhar uma comissão que nos ajuda a manter o conteúdo gratuito.</p>",
        },
    ]
    for page in pages:
        pdir = os.path.join(cfg.OUTPUT_DIR, page["slug"])
        render_page(pdir, page)

    # SEO
    urls = [
        f"{cfg.SITE_URL}/",
        *[p["url"] for p in posts_sorted],
        *[f"{cfg.SITE_URL}/{p['slug']}/" for p in pages],
    ]
    render_sitemap(cfg.OUTPUT_DIR, urls)
    render_robots(cfg.OUTPUT_DIR)

    # Copia CSS
    src_css = os.path.join("templates", "styles.css")
    dst_css = os.path.join(cfg.OUTPUT_DIR, "styles.css")
    if os.path.exists(src_css):
        with open(src_css, "r", encoding="utf-8") as f:
            css = f.read()
        with open(dst_css, "w", encoding="utf-8") as f:
            f.write(css)

    print(
        f"Gerados {len(posts)} posts em {cfg.OUTPUT_DIR} (LLM textos: {used_llm.get('count', 0)}, imagens: {used_llm.get('img', 0)})."
    )


if __name__ == "__main__":
    main()
