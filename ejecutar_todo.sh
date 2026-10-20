#!/usr/bin/env bash
# Corre la tubería completa. El paso 3 no sobrescribe decisiones humanas ya registradas.
set -e
cd "$(dirname "$0")"
python scripts/01_buscar.py
python scripts/02_deduplicar.py
python scripts/03_cribado.py || true
python scripts/04_prisma.py
python scripts/05_bibliometria.py
