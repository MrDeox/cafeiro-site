from __future__ import annotations
import base64
import os
import requests
from .config import cfg
from .utils import ensure_dir, slugify


OPENROUTER_IMAGES_URL = "https://openrouter.ai/api/v1/images"


def _image_prompt(keyword: str, site_name: str) -> str:
    return (
        f"Capa minimalista e limpa para artigo sobre '{keyword}'. "
        "Estilo fotográfico leve ou ilustração flat; foco em café em casa (equipamentos como cafeteira italiana, prensa francesa, filtros e moedores). "
        "Sem texto na imagem, cores neutras, boa legibilidade como thumbnail."
    )


def _save_bytes(path: str, content: bytes) -> str:
    ensure_dir(os.path.dirname(path))
    with open(path, "wb") as f:
        f.write(content)
    return path


def _save_placeholder_svg(slug: str, title: str) -> str:
    ensure_dir(cfg.ASSETS_DIR)
    path = os.path.join(cfg.ASSETS_DIR, f"{slug}.svg")
    svg = f"""
    <svg xmlns='http://www.w3.org/2000/svg' width='1200' height='630'>
      <defs>
        <linearGradient id='g' x1='0' y1='0' x2='1' y2='1'>
          <stop offset='0%' stop-color='#0f141b'/>
          <stop offset='100%' stop-color='#1a2230'/>
        </linearGradient>
      </defs>
      <rect width='100%' height='100%' fill='url(#g)'/>
      <circle cx='250' cy='330' r='140' fill='#2a3547'/>
      <rect x='400' y='250' width='380' height='200' rx='16' fill='#2a3547'/>
      <circle cx='880' cy='320' r='110' fill='#243040'/>
      <text x='600' y='360' font-size='44' text-anchor='middle' fill='#e6e8eb' font-family='Inter, sans-serif'>{title}</text>
    </svg>
    """.strip()
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return path


def generate_image(keyword: str, title: str) -> tuple[str, str] | None:
    """Gera imagem para o artigo e retorna (abs_url, alt). Usa OpenRouter se possível; caso contrário, placeholder SVG.

    Retorna None se imagens estiverem desabilitadas.
    """
    if not cfg.GENERATE_IMAGES:
        return None

    slug = slugify(keyword)
    alt = f"Imagem de capa: {title}"
    # Caminhos de saída
    out_png = os.path.join(cfg.ASSETS_DIR, f"{slug}.png")
    out_svg = os.path.join(cfg.ASSETS_DIR, f"{slug}.svg")

    # Se já existe arquivo (de execuções anteriores), reusa
    if os.path.exists(out_png):
        return (f"{cfg.SITE_URL}/assets/{slug}.png", alt)
    if os.path.exists(out_svg):
        return (f"{cfg.SITE_URL}/assets/{slug}.svg", alt)

    # Tenta via OpenRouter se houver chave
    if cfg.OPENROUTER_API_KEY:
        try:
            headers = {
                "Authorization": f"Bearer {cfg.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": cfg.SITE_URL,
                "X-Title": cfg.SITE_NAME,
            }
            payload = {
                "model": cfg.IMAGE_MODEL,
                "prompt": _image_prompt(keyword, cfg.SITE_NAME),
                "size": "1200x630",
                "response_format": "b64_json",
            }
            resp = requests.post(OPENROUTER_IMAGES_URL, headers=headers, json=payload, timeout=90)
            resp.raise_for_status()
            data = resp.json()
            img_b64 = None
            if isinstance(data, dict) and data.get("data"):
                item = data["data"][0]
                img_b64 = item.get("b64_json") or item.get("b64")
                url = item.get("url")
                if url and not img_b64:
                    # baixa do URL
                    r2 = requests.get(url, timeout=60)
                    r2.raise_for_status()
                    _save_bytes(out_png, r2.content)
                    return (f"{cfg.SITE_URL}/assets/{slug}.png", alt)
            if img_b64:
                content = base64.b64decode(img_b64)
                _save_bytes(out_png, content)
                return (f"{cfg.SITE_URL}/assets/{slug}.png", alt)
        except Exception:
            pass

    # Fallback: placeholder SVG local
    path = _save_placeholder_svg(slug, title)
    return (f"{cfg.SITE_URL}/assets/{slug}.svg", alt)

