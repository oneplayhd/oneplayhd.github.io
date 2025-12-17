from pathlib import Path
import re

ROOT = Path(".").resolve()

def extrair_versao(nome):
    m = re.search(r"-([\d\.]+)\.zip$", nome)
    return m.group(1) if m else None

def pasta_tem_zip(pasta: Path) -> bool:
    return any(pasta.rglob("*.zip"))

def zip_mais_recente(pasta: Path):
    zips = []
    for f in pasta.iterdir():
        if f.is_file() and f.suffix.lower() == ".zip":
            ver = extrair_versao(f.name)
            if ver:
                zips.append((ver, f))
    if not zips:
        return None
    return max(
        zips,
        key=lambda x: [int(p) for p in x[0].split(".")]
    )[1]

def gerar_index(pasta: Path):
    # ❗ regra: raiz sempre gera index
    if pasta != ROOT and not pasta_tem_zip(pasta):
        index = pasta / "index.html"
        if index.exists():
            index.unlink()
        return

    linhas = [
        "<html>",
        "<body>",
        "<h1>Directory listing</h1>",
        "<hr/>",
        "<pre>"
    ]

    if pasta != ROOT:
        linhas.append('<a href="../index.html">..</a>')

    # pastas válidas
    for item in sorted(pasta.iterdir(), key=lambda x: x.name.lower()):
        if item.is_dir() and pasta_tem_zip(item):
            linhas.append(f'<a href="./{item.name}/index.html">{item.name}</a>')

    # zip mais recente (somente se existir na pasta)
    zip_recente = zip_mais_recente(pasta)
    if zip_recente:
        linhas.append(f'<a href="./{zip_recente.name}">{zip_recente.name}</a>')

    linhas += ["</pre>", "</body>", "</html>"]
    (pasta / "index.html").write_text("\n".join(linhas), encoding="utf-8")

def varrer(pasta: Path):
    gerar_index(pasta)
    for p in pasta.iterdir():
        if p.is_dir() and not p.name.startswith("."):
            varrer(p)

if __name__ == "__main__":
    varrer(ROOT)
