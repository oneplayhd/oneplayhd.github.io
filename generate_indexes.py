from pathlib import Path
import re

ROOT = Path(".")

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
    return max(zips, key=lambda x: list(map(int, x[0].split("."))))[1]

def gerar_index(pasta: Path):
    if not pasta_tem_zip(pasta):
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

    if pasta.parent != pasta:
        linhas.append('<a href="../index.html">..</a>')

    # pastas válidas
    for item in sorted(pasta.iterdir()):
        if item.is_dir() and pasta_tem_zip(item):
            linhas.append(f'<a href="./{item.name}/index.html">{item.name}</a>')

    # apenas o zip mais recente
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
