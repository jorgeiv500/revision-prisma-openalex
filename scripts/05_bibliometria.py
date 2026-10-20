"""Paso 5. Panorama bibliométrico rápido de los registros únicos (no reemplaza la síntesis)."""
import pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from comun import DATOS, RES

df = pd.read_csv(DATOS / 'registros.csv')
RES.mkdir(exist_ok=True)
AZUL = '#315190'
fig, ax = plt.subplots(figsize=(9, 4.5))
df['anio'].value_counts().sort_index().plot.bar(ax=ax, color=AZUL)
ax.set_title('Publicaciones por año'); ax.set_xlabel(''); ax.set_ylabel('Registros')
ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout(); fig.savefig(RES / 'por_anio.png', dpi=160)

top = df['revista'].fillna('').replace('', pd.NA).dropna().value_counts().head(12)
fig, ax = plt.subplots(figsize=(9, 5))
top.sort_values().plot.barh(ax=ax, color=AZUL); ax.set_title('Revistas con más registros'); ax.set_xlabel('Registros')
ax.spines[['top', 'right']].set_visible(False)
fig.tight_layout(); fig.savefig(RES / 'revistas.png', dpi=160)

temas = df['tema'].fillna('').replace('', pd.NA).dropna().value_counts().head(10) if 'tema' in df else pd.Series(dtype=int)
mas_citados = df.sort_values('citas', ascending=False).head(10)[['anio', 'titulo', 'revista', 'citas', 'doi']]
with open(RES / 'resumen_bibliometrico.md', 'w', encoding='utf-8') as f:
    f.write(f'# Resumen bibliométrico\n\nRegistros únicos: {len(df)}\n\n## Temas principales (OpenAlex)\n\n')
    f.write('\n'.join(f'- {k}: {v}' for k, v in temas.items()) + '\n\n## Diez más citados\n\n')
    f.write('| Año | Título | Revista | Citas | DOI |\n|---|---|---|---|---|\n')
    for r in mas_citados.itertuples():
        f.write(f'| {r.anio} | {r.titulo} | {r.revista} | {r.citas} | {r.doi} |\n')
print('Gráficas y resumen en resultados/')
