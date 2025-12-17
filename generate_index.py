from pathlib import Path
from datetime import datetime
import re

ROOT = Path(".").resolve()

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

def formatar_data(path: Path):
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%d/%m/%Y")

# 🔹 INDEX DAS SUBPASTAS (modo humano)
def gerar_index_pasta(pasta: Path):
    zip_local = zip_mais_recente(pasta)
    if not zip_local:
        return

    data = formatar_data(zip_local)

    html = f"""<html>
<body>
<h1>Index of /{pasta.name}</h1>
<hr>
<table>
<tr><th></th><th>Name</th><th align="right">Last modified</th></tr>
<tr><td colspan="3"><hr></td></tr>

<tr>
<td valign="top"><img alt="[DIR]"></td>
<td><a href="../index.html">..</a></td>
<td align="right"></td>
</tr>

<tr>
<td valign="top"><img alt="[ZIP]"></td>
<td><a href="{zip_local.name}">{zip_local.name}</a></td>
<td align="right">{data}</td>
</tr>

<tr><td colspan="3"><hr></td></tr>
</table>
</body>
</html>"""

    (pasta / "index.html").write_text(html, encoding="utf-8")

# 🔹 INDEX DA RAIZ (modo Kodi)
def gerar_index_raiz():
    linhas = [
        "<html><body>",
        "<h1>Index of /</h1>",
        "<hr>",
        "<table>",
        '<tr><th></th><th>Name</th><th align="right">Last modified</th></tr>',
        '<tr><td colspan="3"><hr></td></tr>',
    ]

    for pasta in sorted(ROOT.iterdir(), key=lambda x: x.name.lower()):
        if not pasta.is_dir() or pasta.name.startswith("."):
            continue

        zip_ok = zip_mais_recente(pasta)
        if zip_ok:
            data = formatar_data(zip_ok)
            rel = zip_ok.relative_to(ROOT).as_posix()

            linhas.append(f"""
<tr>
<td valign="top"><img alt="[ZIP]"></td>
<td><a href="{rel}">{zip_ok.name}</a></td>
<td align="right">{data}</td>
</tr>
""")

    linhas += [
        '<tr><td colspan="3"><hr></td></tr>',
        "</table>",
        "</body></html>"
    ]

    (ROOT / "index.html").write_text("\n".join(linhas), encoding="utf-8")

def main():
    for pasta in ROOT.iterdir():
        if pasta.is_dir() and not pasta.name.startswith("."):
            gerar_index_pasta(pasta)
    gerar_index_raiz()

if __name__ == "__main__":
    main()
