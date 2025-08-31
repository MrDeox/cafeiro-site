# Cafeiro — Site afiliado programático (PT‑BR)

Gerador estático em Python que cria um site de conteúdo sobre café em casa, com SEO básico, sitemap, páginas institucionais e monetização via links de afiliados. Integração opcional com LLM (OpenRouter) para redação automática e automação diária via GitHub Actions + Pages.

## Como funciona
- Seeds de palavras‑chave em `data/keywords.txt`.
- A cada execução, gera páginas em `public/` com HTML estático e `sitemap.xml`.
- Se houver `OPENROUTER_API_KEY`, o conteúdo é criado/enriquecido por LLM com cache em `cache/llm/` para evitar custo repetido.
- Hospedagem automática via GitHub Pages usando o workflow `.github/workflows/publish.yml`.

## Primeiros passos (local)
1. Python 3.11+ instalado.
2. `cp .env.example .env` e ajuste valores (opcional agora).
3. Instale deps:
   ```bash
   pip install -r requirements.txt
   ```
4. Gere o site:
   ```bash
   python scripts/generate.py
   ```
5. Abra `public/index.html` no navegador. O CSS é copiado para `public/styles.css` automaticamente.

## LLM (OpenRouter)
- Defina `OPENROUTER_API_KEY` no `.env` (ou como secret no GitHub).
- Parâmetros úteis no `.env`:
  - `OPENROUTER_MODEL` (padrão: `openrouter/anthropic/claude-3.5-sonnet`)
  - `GENERATE_WITH_LLM=true|false`
  - `LLM_MAX_CALLS_PER_RUN` (limita chamadas por execução)
- Cache: conteúdos LLM ficam em `cache/llm/<slug>.md`.

## Afiliados e monetização
- Defina `AMAZON_TAG_BR` (ex.: `SEU_TAG-20`).
- O gerador insere CTAs com buscas na Amazon BR relacionadas ao tema do artigo.

## Deploy automático (GitHub Pages)
1. Suba este repositório para o GitHub.
2. Em Settings → Pages, configure “Build and deployment: GitHub Actions”.
3. Em Settings → Secrets and variables → Actions → New repository secret, crie:
   - `OPENROUTER_API_KEY` (opcional)
   - `AMAZON_TAG_BR` (opcional)
   - `SITE_URL` (ex.: `https://seuusuario.github.io/seu-repo`)
   - `GA_MEASUREMENT_ID` (opcional)
4. O workflow `.github/workflows/publish.yml` vai:
   - Restaurar cache LLM, instalar deps e gerar o site (diariamente às 03:17 UTC e a cada push)
   - Subir `public/` como artifact e publicar no Pages.

Observação sobre custos: mesmo com LLM habilitado, há limite por execução (`LLM_MAX_CALLS_PER_RUN`). O cache preserva textos já gerados entre execuções (via actions/cache).

## Estrutura
- `scripts/generate.py` — orquestra geração de páginas e SEO
- `generator/` — núcleo (config, LLM, templates/renderer, afiliados)
- `templates/` — HTML/CSS base e sitemap/robots
- `data/keywords.txt` — lista de temas
- `public/` — saída estática pronta para deploy

## Customizações rápidas
- Nome do site e tagline: edite `.env` ou use variáveis de ambiente.
- Nicho/tema: troque `data/keywords.txt` por outro cluster de interesse.
- Estilo: ajuste `templates/styles.css`.
- CTAs: altere heurística em `generator/affiliate.py`.

## Avisos legais
Incluímos páginas padrão de "Privacidade" e "Afiliados" (sem aconselhamento legal). Ajuste conforme sua realidade e LGPD.

---
Feito para rodar 24/7 com baixo atrito, gerando páginas úteis e monetizáveis com manutenção mínima.
