"""Paso 3. Hoja de cribado por título y resumen.

Genera datos/cribado.csv con una sugerencia preliminar (por reglas o, con --ia, por un modelo)
y columnas vacías para la DECISIÓN HUMANA. La IA nunca decide sola: solo ordena y sugiere.

Uso:
  python scripts/03_cribado.py            # sugerencia por reglas del protocolo
  python scripts/03_cribado.py --ia 50    # además, sugerencia de un LLM para los primeros 50
"""
import os, sys, json, pandas as pd
from comun import DATOS, cargar_env, protocolo

cargar_env()
P = protocolo()
df = pd.read_csv(DATOS / 'registros.csv')
texto = (df['titulo'].fillna('') + ' ' + df['resumen'].fillna('')).str.lower()


def regla(t):
    exc = [k for k in P['criterios_exclusion'] if k.lower() in t]
    inc = [k for k in P['criterios_inclusion'] if k.lower() in t]
    if exc:
        return 'revisar_excluir', 'contiene: ' + ', '.join(exc)
    if not t.strip() or len(t) < 120:
        return 'revisar', 'sin resumen'
    if len(inc) >= 2:
        return 'incluir_probable', 'coincide: ' + ', '.join(inc)
    return 'excluir_probable', 'pocas coincidencias'


s = texto.map(regla)
df['sugerencia'] = [x[0] for x in s]
df['motivo_sugerencia'] = [x[1] for x in s]

if '--ia' in sys.argv:
    import anthropic
    n = int(sys.argv[sys.argv.index('--ia') + 1]) if len(sys.argv) > sys.argv.index('--ia') + 1 else 20
    cli = anthropic.Anthropic()
    modelo = os.environ.get('MODELO_IA', 'claude-sonnet-5-5')
    guia = (f"Pregunta de la revisión: {P['pregunta']}\nResponda SOLO un JSON "
            '{"sugerencia": "incluir_probable|excluir_probable|revisar", "motivo": "<máx. 20 palabras>"}.')
    for i in df.index[:n]:
        msg = cli.messages.create(model=modelo, max_tokens=200, messages=[{'role': 'user', 'content':
              f"{guia}\n\nTítulo: {df.at[i, 'titulo']}\nResumen: {str(df.at[i, 'resumen'])[:3000]}"}])
        try:
            js = json.loads(msg.content[0].text.strip().strip('`').removeprefix('json'))
            df.at[i, 'sugerencia'], df.at[i, 'motivo_sugerencia'] = js['sugerencia'], 'IA: ' + js['motivo']
        except Exception:
            df.at[i, 'motivo_sugerencia'] = 'IA: respuesta no válida, revisar a mano'
    with open(DATOS / 'uso_ia.log', 'a', encoding='utf-8') as f:
        f.write(f'Cribado sugerido con {modelo} para {n} registros. Decisión final humana.\n')

for c in ['decision_R1', 'decision_R2', 'decision_final', 'motivo_exclusion', 'texto_completo_recuperado', 'incluido_final']:
    if c not in df:
        df[c] = ''
cols = ['rid', 'sugerencia', 'motivo_sugerencia', 'decision_R1', 'decision_R2', 'decision_final', 'motivo_exclusion',
        'texto_completo_recuperado', 'incluido_final', 'titulo', 'anio', 'revista', 'doi', 'resumen', 'fuente', 'citas', 'tema']
salida = DATOS / 'cribado.csv'
if salida.exists() and '--forzar' not in sys.argv:
    raise SystemExit('datos/cribado.csv ya existe y puede tener decisiones humanas. Use --forzar para sobrescribir.')
df[[c for c in cols if c in df]].to_csv(salida, index=False)
print(df['sugerencia'].value_counts().to_string())
print('\nAbra datos/cribado.csv en Excel o Sheets y complete decision_R1 / decision_R2 (incluir / excluir).')
