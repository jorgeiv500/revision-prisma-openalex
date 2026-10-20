"""Funciones compartidas: lectura del protocolo, rutas y normalización."""
import os, re, unicodedata, pathlib, yaml

RAIZ = pathlib.Path(__file__).resolve().parents[1]
CRUDO = RAIZ / 'datos' / 'crudo'
DATOS = RAIZ / 'datos'
RES = RAIZ / 'resultados'


def cargar_env():
    f = RAIZ / '.env'
    if f.exists():
        for linea in f.read_text(encoding='utf-8').splitlines():
            if '=' in linea and not linea.strip().startswith('#'):
                k, v = linea.split('=', 1)
                os.environ.setdefault(k.strip(), v.strip())


def protocolo():
    return yaml.safe_load((RAIZ / 'protocolo.yaml').read_text(encoding='utf-8'))


def norm_doi(doi):
    if not isinstance(doi, str) or not doi.strip():
        return ''
    d = doi.strip().lower()
    d = re.sub(r'^(https?://)?(dx\.)?doi\.org/', '', d)
    return d.removeprefix('doi:').strip()


def norm_titulo(t):
    if not isinstance(t, str):
        return ''
    t = unicodedata.normalize('NFKD', t).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', ' ', t.lower()).strip()


def resumen_desde_indice(inv):
    """OpenAlex entrega el resumen como índice invertido {palabra: [posiciones]}."""
    if not inv:
        return ''
    pos = {}
    for palabra, lugares in inv.items():
        for p in lugares:
            pos[p] = palabra
    return ' '.join(pos[i] for i in sorted(pos))
