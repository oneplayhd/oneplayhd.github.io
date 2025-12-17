from pathlib import Path
from datetime import datetime
import re

ROOT = Path(".").resolve()

ICON_BACK = "../icons/back.gif"
ICON_ZIP  = "../icons/compressed.gif"
ICON_BLANK = "../icons/blank.gif"

def extrair_versao(nome):
    m = re.search(r"-([\d\.]+)\.zip$", nome)
    return m.group(1) if m else None

def versao_key(ver):
    return [int(p) for p in ver.split(".")]

def zip_mais_recente(pasta: Path):
    zips = []
    for f in pasta.iterdir():
        if f.is_file() and f.suffix.lower() == ".zip":
            ver = extrair_versao(f.name)
            if ver:
                zips.append((ver, f))
    if not zips:
        return None
    return max(zips, key=lambda x: versao_key(x[0]))[1]

def data_formatada(path: Path):
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%d/%m/%Y")

# 🔥 REMOVE index.html DE TODAS AS SUBPASTAS
def remover_indexes_subpastas():
    for path in ROOT.rglob("index.html"):
        if path.parent != ROOT:
            path.unlink()

def gerar_index_raiz():
    linhas = []
    linhas.append("<html>")
    linhas.append("<body>")
    linhas.append("<h1>          Repositorio OnePlay</h1>")
    linhas.append("<table>")
    linhas.append(
        f'<tr><th valign="top"><img src="{ICON_BLANK}" alt="[ICO]"></th>'
        '<th>Name</th><th>Last updates</th><th></th></tr>'
    )
    linhas.append('<tr><th colspan="5"><hr></th></tr>')

    # Link Inicio
    linhas.append(
        f'<tr><td valign="top"><img src="{ICON_BACK}" alt="[PARENTDIR]"></td>'
        '<td><a href="https://oneplayhd.com">Inicio</a></td>'
        '<td>&nbsp;</td><td align="right"> - </td><td>&nbsp;</td></tr>'
    )

    # ZIPs (1 por pasta)
    for pasta in sorted(ROOT.iterdir(), key=lambda x: x.name.lower()):
        if not pasta.is_dir() or pasta.name.startswith("."):
            continue

        zip_ok = zip_mais_recente(pasta)
        if not zip_ok:
            continue

        rel = zip_ok.relative_to(ROOT).as_posix()
        data = data_formatada(zip_ok)

        linhas.append(
            f'<tr><td valign="top"><img src="{ICON_ZIP}" alt="[   ]"></td>'
            f'<td><a href="{rel}">{zip_ok.name}</a></td>'
            f'<td align="right">{data}</td></tr>'
        )

    linhas.append('<tr><th colspan="5"><hr></th></tr>')
    linhas.append("</table>")
    linhas.append("</body>")
    linhas.append("</html>")

    (ROOT / "index.html").write_text("\n".join(linhas), encoding="utf-8")

def main():
    remover_indexes_subpastas()
    gerar_index_raiz()

if __name__ == "__main__":
    main()
