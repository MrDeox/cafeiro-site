from __future__ import annotations
import json
import os
import random
import textwrap
from typing import Optional
import requests

from .config import cfg


OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def call_openrouter(system: str, user: str, temperature: float = 0.6) -> Optional[str]:
    if not cfg.OPENROUTER_API_KEY:
        return None
    headers = {
        "Authorization": f"Bearer {cfg.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        # Recomendado pela OpenRouter para identificação
        "HTTP-Referer": cfg.SITE_URL,
        "X-Title": cfg.SITE_NAME,
    }
    payload = {
        "model": cfg.OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": temperature,
    }
    try:
        resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def gen_title_and_description(keyword: str) -> tuple[str, str]:
    prompt = f"""
    Gere um título forte (no máximo 62 caracteres) e uma meta description (no máximo 150 caracteres) para um artigo em PT-BR sobre: "{keyword}". Responda em JSON com chaves title e description.
    """.strip()
    system = "Você é um especialista em SEO e copywriting em português do Brasil."
    content = call_openrouter(system, prompt)
    if content:
        try:
            data = json.loads(content)
            title = data.get("title") or keyword.title()
            desc = data.get("description") or f"Guia prático sobre {keyword}."
            return title.strip(), desc.strip()
        except Exception:
            pass
    # Fallback
    base = keyword.strip().capitalize()
    title = base if len(base) <= 62 else base[:59] + "..."
    desc = f"Guia prático para {keyword} em casa."
    return title, desc


def gen_article_body(keyword: str, outline_h2: list[str]) -> str:
    # Quando possível, pede um texto estruturado; caso contrário, gera fallback simples.
    outline = "\n".join(f"- {h}" for h in outline_h2)
    prompt = f"""
    Escreva um artigo objetivo em PT-BR para iniciantes, sobre "{keyword}".
    Estruture com seções claras (H2/H3), listas quando útil e sem enrolação.
    Use tom de voz claro e prático. Evite jargões. Evite redundância.
    Cubra este outline sugerido (ajuste se necessário):
    {outline}

    Regras:
    - Abertura curta (2-3 linhas) com o benefício prático.
    - Cada H2 com 2-4 parágrafos e, se fizer sentido, 1 lista curta.
    - Finalize com um resumo prático (bullet points).
    - Não invente dados. Não inclua links.
    """.strip()
    system = "Você é um redator especialista em café em casa e métodos de preparo."
    content = call_openrouter(system, prompt)
    if content:
        return content

    # Fallback simples
    blocks = [
        f"{keyword.capitalize()} pode parecer complexo, mas com algumas escolhas simples você consegue resultados consistentes em casa.",
    ]
    for h in outline_h2:
        blocks.append(f"\n## {h}\n")
        blocks.append(
            textwrap.fill(
                "Foque no básico primeiro: qualidade da água, proporção café/água, moagem adequada e constância no método. Ajuste um fator de cada vez para evoluir rapidamente.",
                width=90,
            )
        )
        blocks.append("\n- Dica 1 prática\n- Dica 2 rápida\n- Dica 3 econômica\n")
    blocks.append("\n### Resumo prático\n- Comece simples\n- Padronize medidas\n- Ajuste moagem\n- Anote o que funcionou\n")
    return "\n\n".join(blocks)

