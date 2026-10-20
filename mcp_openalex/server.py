"""Servidor MCP mínimo para OpenAlex.

Le da a Claude Code, Codex o cualquier cliente MCP tres herramientas para consultar la literatura
con datos reales y citables, en vez de "recordar" referencias (que es como se inventan).
Ejecución directa de prueba: python mcp_openalex/server.py
"""
import os, requests
from mcp.server.fastmcp import FastMCP

API = 'https://api.openalex.org'
CORREO = os.environ.get('OPENALEX_EMAIL', '')
CLAVE = os.environ.get('OPENALEX_API_KEY', '')
mcp = FastMCP('openalex')


def _get(ruta, **params):
    if CORREO:
        params['mailto'] = CORREO
    if CLAVE:
        params['api_key'] = CLAVE
    r = requests.get(API + ruta, params=params, timeout=60)
    r.raise_for_status()
    return r.json()


def _resumen(inv):
    if not inv:
        return ''
    pos = {p: w for w, ps in inv.items() for p in ps}
    return ' '.join(pos[i] for i in sorted(pos))


def _ficha(w, con_resumen=False):
    src = ((w.get('primary_location') or {}).get('source') or {})
    f = {'id': w['id'], 'doi': w.get('doi'), 'titulo': w.get('title'), 'anio': w.get('publication_year'),
         'revista': src.get('display_name'), 'citas': w.get('cited_by_count'),
         'autores': [a['author']['display_name'] for a in w.get('authorships', [])[:6]],
         'acceso_abierto': (w.get('open_access') or {}).get('oa_url')}
    if con_resumen:
        f['resumen'] = _resumen(w.get('abstract_inverted_index'))[:2500]
    return f


@mcp.tool()
def buscar_trabajos(consulta: str, anio_desde: int = 2018, anio_hasta: int = 2026, n: int = 25, orden: str = 'relevance_score') -> dict:
    """Busca artículos en OpenAlex por título y resumen. Admite AND, OR, NOT y comillas.
    orden: relevance_score | cited_by_count | publication_date. Devuelve el total y hasta n fichas."""
    js = _get('/works', filter=f'title_and_abstract.search:{consulta},publication_year:{anio_desde}-{anio_hasta}',
              sort=f'{orden}:desc', **{'per-page': min(n, 200)})
    return {'total': js['meta']['count'], 'resultados': [_ficha(w) for w in js['results']]}


@mcp.tool()
def obtener_trabajo(doi_o_id: str) -> dict:
    """Ficha completa (con resumen) de un trabajo por DOI (10.xxxx/...) o ID de OpenAlex (W123...)."""
    clave = doi_o_id.strip()
    if clave.startswith('10.'):
        clave = 'https://doi.org/' + clave
    return _ficha(_get('/works/' + clave), con_resumen=True)


@mcp.tool()
def contar_por_anio(consulta: str) -> dict:
    """Cuántos trabajos coinciden con la consulta en cada año. Útil para justificar la vigencia de un tema."""
    js = _get('/works', filter=f'title_and_abstract.search:{consulta}', group_by='publication_year')
    return {g['key']: g['count'] for g in js['group_by']}


if __name__ == '__main__':
    mcp.run()
