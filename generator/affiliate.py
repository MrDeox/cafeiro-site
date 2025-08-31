from .config import cfg
from .utils import slugify
import urllib.parse


def amazon_search_url_br(query: str) -> str:
    tag = cfg.AMAZON_TAG_BR or "SEU_TAG-20"
    params = {
        "k": query,
        "tag": tag,
        "i": "kitchen",
    }
    return f"https://www.amazon.com.br/s?{urllib.parse.urlencode(params)}"


def pick_cta_terms(keyword: str) -> list[str]:
    k = (keyword or "").lower()
    if any(w in k for w in ["moedor", "moer", "grão", "grao", "moinho"]):
        return ["moedor de café", "moedor elétrico", "moedor manual"]
    if any(w in k for w in ["cafeteira", "método", "metodo", "preparo", "espresso", "expresso"]):
        return ["cafeteira italiana", "prensa francesa", "aeropress"]
    if "filtro" in k:
        return ["filtro de papel", "filtro de metal", "coador de café"]
    if any(w in k for w in ["balança", "balanca", "escala"]):
        return ["balança de café", "balança de precisão"]
    return ["cafeteira", "moedor de café", "balança de café"]


def render_cta_links(keyword: str) -> list[dict]:
    terms = pick_cta_terms(keyword)
    items = []
    for t in terms:
        items.append({
            "label": t.capitalize(),
            "url": amazon_search_url_br(t)
        })
    return items

