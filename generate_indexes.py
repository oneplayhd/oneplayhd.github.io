from pathlib import Path

def pasta_tem_zip(pasta: Path) -> bool:
    return any(pasta.rglob("*.zip"))

def gerar_index(pasta: Path):
    linhas = [
        "<html>",
        "<body>",
        "<h1>Directory listing</h1>",
        "<hr/>",
        "<pre>"
    ]

    if pasta.parent != pasta:
        linhas.append('<a href="../index.html">..</a>')

    for item in sorted(pasta.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
        if item.name.startswith(".") or item.name == "index.html":
            continue

        if item.is_dir() and pasta_tem_zip(item):
            linhas.append(f'<a href="./{item.name}/index.html">{item.name}</a>')

        elif item.is_file() and item.suffix.lower() == ".zip":
            linhas.append(f'<a href="./{item.name}">{item.name}</a>')

    linhas += ["</pre>", "</body>", "</html>"]
    (pasta / "index.html").write_text("\n".join(linhas), encoding="utf-8")

def varrer(raiz: Path):
    gerar_index(raiz)
    for p in raiz.iterdir():
        if p.is_dir() and not p.name.startswith("."):
            varrer(p)

if __name__ == "__main__":
    varrer(Path("."))
