"""Paso 1. Búsqueda en OpenAlex con paginación por cursor.

Guarda los registros crudos y deja constancia de la consulta, la fecha y el total,
que es lo que PRISMA 2020 pide reportar (ítems 6 y 7).
Uso: python scripts/01_buscar.py
"""
import json, os, sys, time, datetime, requests
from comun import CRUDO, cargar_env, protocolo, resumen_desde_indice

cargar_env()
P = protocolo()
correo = os.environ.get('OPENALEX_EMAIL', '')
filtros = [
    f"title_and_abstract.search:{P['consulta']}",
    f"publication_year:{P['anio_desde']}-{P['anio_hasta']}",
    'type:' + '|'.join(P['tipos']),
    'language:' + '|'.join(P['idiomas']),
]
params = {'filter': ','.join(filtros), 'per-page': 200, 'cursor': '*',
          'select': 'id,doi,title,publication_year,type,language,primary_location,authorships,'
                    'abstract_inverted_index,cited_by_count,primary_topic,open_access'}
if correo:
    params['mailto'] = correo
clave = os.environ.get('OPENALEX_API_KEY', '')
if clave:
    params['api_key'] = clave
else:
    print('Aviso: sin OPENALEX_API_KEY se comparte un presupuesto diario mínimo con toda la red. '
          'Pida una clave gratuita en https://openalex.org/settings/api', file=sys.stderr)

registros, total, incompleta = [], None, False
while params['cursor'] and len(registros) < P['max_registros']:
    for intento in range(5):
        r = requests.get('https://api.openalex.org/works', params=params, timeout=60)
        if r.status_code in (200, 401, 403):
            break
        time.sleep(2 ** intento)
    if r.status_code != 200:
        print(f'OpenAlex respondió {r.status_code} (presupuesto agotado o clave inválida). '
              f'Se guardan los {len(registros)} registros descargados; la búsqueda queda INCOMPLETA.', file=sys.stderr)
        incompleta = True
        break
    js = r.json()
    total = js['meta']['count']
    for w in js['results']:
        loc = w.get('primary_location') or {}
        src = loc.get('source') or {}
        registros.append({
            'fuente': 'OpenAlex', 'id': w['id'], 'doi': w.get('doi') or '', 'titulo': w.get('title') or '',
            'anio': w.get('publication_year'), 'tipo': w.get('type'), 'idioma': w.get('language'),
            'revista': src.get('display_name') or '', 'autores': '; '.join(a['author']['display_name'] for a in w.get('authorships', [])[:10]),
            'resumen': resumen_desde_indice(w.get('abstract_inverted_index')), 'citas': w.get('cited_by_count', 0),
            'tema': (w.get('primary_topic') or {}).get('display_name', ''), 'acceso_abierto': (w.get('open_access') or {}).get('is_oa'),
        })
    params['cursor'] = js['meta'].get('next_cursor')
    print(f'  {len(registros)} de {total}', file=sys.stderr)

CRUDO.mkdir(parents=True, exist_ok=True)
hoy = datetime.date.today().isoformat()
with open(CRUDO / 'openalex.jsonl', 'w', encoding='utf-8') as f:
    for x in registros:
        f.write(json.dumps(x, ensure_ascii=False) + '\n')
with open(CRUDO / 'registro_busqueda.md', 'a', encoding='utf-8') as f:
    f.write(f"\n## {hoy} · OpenAlex\n- Filtro: `{params['filter']}`\n- Total informado por la API: {total}\n- Registros descargados: {len(registros)}{' (INCOMPLETA: repetir con clave de API)' if incompleta else ''}\n")
print(f'OpenAlex: {len(registros)} registros guardados en datos/crudo/openalex.jsonl')
