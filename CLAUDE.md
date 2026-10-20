# Instrucciones para agentes (Claude Code, Codex y similares)

Este repositorio es una revisión sistemática reproducible que sigue PRISMA 2020.

## Reglas
1. **No invente referencias.** Toda cita sale de OpenAlex (herramientas MCP `openalex`) o de `datos/registros.csv`. Si no la encuentra, dígalo.
2. **No tome decisiones de inclusión.** Puede sugerir en `sugerencia` y `motivo_sugerencia`; las columnas `decision_*` e `incluido_final` son de las personas revisoras.
3. **No sobrescriba** `datos/cribado.csv` si tiene decisiones humanas. Nunca use `--forzar` sin que se lo pidan.
4. **Registre** cada búsqueda nueva en `datos/crudo/registro_busqueda.md` (fecha, filtro, total) y cada uso de IA en `datos/uso_ia.log`.
5. Si cambia `protocolo.yaml`, anote el cambio y la razón en `docs/desviaciones.md`: una revisión sistemática declara sus desviaciones.
6. Escriba en español, con frases cortas.

## Tubería
`python scripts/01_buscar.py` → `02_deduplicar.py` → `03_cribado.py` → (cribado humano) → `04_prisma.py` → `05_bibliometria.py`

## Tareas que sí le pedimos
- Afinar la consulta con `contar_por_anio` y `buscar_trabajos` antes de correr el paso 1.
- Resumir resúmenes para acelerar el cribado humano, siempre citando el `rid`.
- Extraer datos de los textos incluidos a `datos/extraccion.csv` (método, datos, métrica, resultado), con la página de donde sale cada dato.
- Revisar el borrador contra `docs/checklist_prisma2020.md`.
