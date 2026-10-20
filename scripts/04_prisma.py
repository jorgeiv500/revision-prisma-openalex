"""Paso 4. Diagrama de flujo PRISMA 2020 a partir de los conteos reales.

Lee datos/conteo_dedup.json y datos/cribado.csv (decision_final, texto_completo_recuperado, incluido_final).
Mientras las decisiones humanas estén vacías, usa la sugerencia preliminar y lo marca como BORRADOR.
"""
import json, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from comun import DATOS, RES

c = json.loads((DATOS / 'conteo_dedup.json').read_text(encoding='utf-8'))
cr = pd.read_csv(DATOS / 'cribado.csv', dtype=str).fillna('')
borrador = (cr['decision_final'] == '').all()
dec = cr['decision_final'].where(cr['decision_final'] != '', cr['sugerencia'].str.replace('_probable', ''))
cribados = len(cr)
excl_cribado = int(dec.str.startswith('excluir').sum() + dec.str.startswith('revisar_excluir').sum())
pasan = cribados - excl_cribado
no_recuperados = int((cr['texto_completo_recuperado'].str.lower() == 'no').sum())
evaluados = pasan - no_recuperados
if borrador or (cr['incluido_final'] == '').all():
    incluidos, excl_texto = evaluados, 0
else:
    incluidos = int((cr['incluido_final'].str.lower() == 'si').sum())
    excl_texto = evaluados - incluidos
motivos = cr.loc[(cr['incluido_final'].str.lower() == 'no'), 'motivo_exclusion'].value_counts().to_dict()

RES.mkdir(exist_ok=True)
fig, ax = plt.subplots(figsize=(12, 13)); ax.set_xlim(0, 12); ax.set_ylim(0, 13); ax.axis('off')
AZUL, GRIS = '#315190', '#F4F1EA'


def caja(x, y, w, h, txt, color='white'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.02,rounding_size=0.08', fc=color, ec='#14223F', lw=1.2))
    ax.text(x + w / 2, y + h / 2, txt, ha='center', va='center', fontsize=10.5, wrap=True, color='#14223F')


def flecha(x1, y1, x2, y2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle='->', lw=1.3, color='#14223F'))


fuentes = '\n'.join(f'{k}: n = {v}' for k, v in c['por_fuente'].items())
for et, y, h in [('Identificación', 10.4, 1.8), ('Cribado', 3.4, 5.9), ('Incluidos', 1.0, 1.4)]:
    ax.add_patch(FancyBboxPatch((0.1, y), 0.6, h, boxstyle='round,pad=0.02', fc=AZUL, ec=AZUL))
    ax.text(0.4, y + h / 2, et, rotation=90, ha='center', va='center', color='white', fontsize=12, weight='bold')
caja(1.1, 10.4, 5.2, 1.8, f"Registros identificados\n(n = {c['identificados']})\n{fuentes}")
caja(7.0, 10.4, 4.6, 1.8, f"Eliminados antes del cribado\nDuplicados (n = {c['duplicados']})")
caja(1.1, 8.0, 5.2, 1.3, f'Registros cribados\n(n = {cribados})')
caja(7.0, 8.0, 4.6, 1.3, f'Registros excluidos\n(n = {excl_cribado})')
caja(1.1, 5.8, 5.2, 1.3, f'Informes buscados para recuperar\n(n = {pasan})')
caja(7.0, 5.8, 4.6, 1.3, f'Informes no recuperados\n(n = {no_recuperados})')
caja(1.1, 3.4, 5.2, 1.4, f'Informes evaluados por elegibilidad\n(n = {evaluados})')
mot = '\n'.join(f'{k} (n = {v})' for k, v in list(motivos.items())[:4]) or 'Motivos: completar en cribado.csv'
caja(7.0, 3.0, 4.6, 2.2, f'Informes excluidos (n = {excl_texto})\n{mot}')
caja(1.1, 1.0, 5.2, 1.4, f'Estudios incluidos en la revisión\n(n = {incluidos})', GRIS)
flecha(3.7, 10.4, 3.7, 9.3); flecha(6.3, 11.3, 7.0, 11.3)
flecha(3.7, 8.0, 3.7, 7.1); flecha(6.3, 8.65, 7.0, 8.65)
flecha(3.7, 5.8, 3.7, 4.8); flecha(6.3, 6.45, 7.0, 6.45)
flecha(3.7, 3.4, 3.7, 2.4); flecha(6.3, 4.1, 7.0, 4.1)
ax.set_title('Diagrama de flujo PRISMA 2020' + ('  ·  BORRADOR (faltan decisiones humanas)' if borrador else ''),
             fontsize=14, color='#14223F', pad=8)
fig.savefig(RES / 'prisma_2020.png', dpi=160, bbox_inches='tight'); fig.savefig(RES / 'prisma_2020.svg', bbox_inches='tight')
json.dump({'identificados': c['identificados'], 'duplicados': c['duplicados'], 'cribados': cribados, 'excluidos_cribado': excl_cribado,
           'no_recuperados': no_recuperados, 'evaluados': evaluados, 'excluidos_texto': excl_texto, 'incluidos': incluidos,
           'borrador': bool(borrador)}, open(RES / 'conteo_prisma.json', 'w'), indent=2)
print('Diagrama en resultados/prisma_2020.png', '(BORRADOR)' if borrador else '')
