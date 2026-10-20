"""Paso 2. Une OpenAlex con exportaciones de bases de la biblioteca y elimina duplicados.

Si exportó resultados de Scopus (CSV) o Web of Science (texto delimitado por tabulaciones),
déjelos en datos/crudo/ con nombre scopus*.csv o wos*.txt.
Criterio: mismo DOI normalizado o, si no hay DOI, mismo título normalizado y mismo año.
"""
import json, glob, pandas as pd
from comun import CRUDO, DATOS, norm_doi, norm_titulo

partes = []
f = CRUDO / 'openalex.jsonl'
if f.exists():
    partes.append(pd.DataFrame([json.loads(l) for l in f.open(encoding='utf-8')]))
for s in glob.glob(str(CRUDO / 'scopus*.csv')):
    d = pd.read_csv(s)
    partes.append(pd.DataFrame({'fuente': 'Scopus', 'id': d.get('EID', ''), 'doi': d.get('DOI', ''), 'titulo': d['Title'],
                                'anio': d['Year'], 'revista': d.get('Source title', ''), 'autores': d.get('Authors', ''),
                                'resumen': d.get('Abstract', ''), 'citas': d.get('Cited by', 0)}))
for s in glob.glob(str(CRUDO / 'wos*.txt')):
    d = pd.read_csv(s, sep='\t', quoting=3, dtype=str)
    partes.append(pd.DataFrame({'fuente': 'WoS', 'id': d.get('UT', ''), 'doi': d.get('DI', ''), 'titulo': d['TI'],
                                'anio': pd.to_numeric(d['PY'], errors='coerce'), 'revista': d.get('SO', ''),
                                'autores': d.get('AU', ''), 'resumen': d.get('AB', ''), 'citas': d.get('TC', 0)}))
if not partes:
    raise SystemExit('No hay registros. Ejecute primero scripts/01_buscar.py')

todo = pd.concat(partes, ignore_index=True)
n_identificados = len(todo)
por_fuente = todo['fuente'].value_counts().to_dict()
todo['doi_n'] = todo['doi'].map(norm_doi)
todo['tit_n'] = todo['titulo'].map(norm_titulo)
todo = todo[todo['tit_n'] != '']
todo['clave'] = todo.apply(lambda r: 'doi:' + r.doi_n if r.doi_n else f'tit:{r.tit_n}|{r.anio}', axis=1)
# Si un título aparece con y sin DOI, unificamos por título+año también.
todo = todo.sort_values(['doi_n'], ascending=False)
unicos = todo.drop_duplicates('clave').drop_duplicates(['tit_n', 'anio'])
unicos = unicos.reset_index(drop=True)
unicos.insert(0, 'rid', [f'R{i+1:04d}' for i in range(len(unicos))])
unicos.drop(columns=['clave']).to_csv(DATOS / 'registros.csv', index=False)
conteo = {'identificados': n_identificados, 'por_fuente': por_fuente, 'duplicados': n_identificados - len(unicos), 'unicos': len(unicos)}
(DATOS / 'conteo_dedup.json').write_text(json.dumps(conteo, indent=2, ensure_ascii=False), encoding='utf-8')
print(conteo)
