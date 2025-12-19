from pathlib import Path
import re

INDEX_MUDOU = False


def extrair_versao(nome: str):
    m = re.search(r"One\.repo-(\d+(?:\.\d+)*)\.zip", nome)
    if not m:
        return ()
    return tuple(map(int, m.group(1).split(".")))


def encontrar_repos_mais_recentes(raiz: Path) -> list[Path]:
    encontrados = []

    for item in raiz.rglob("One.repo-*.zip"):
        versao = extrair_versao(item.name)
        if versao:
            encontrados.append((versao, item))

    if not encontrados:
        return []

    maior_versao = max(v for v, _ in encontrados)
    return [p for v, p in encontrados if v == maior_versao]


def pasta_contem_zip_direto(pasta: Path) -> bool:
    return any(
        p.is_file() and p.suffix.lower() == ".zip"
        for p in pasta.iterdir()
    )


def remover_index(pasta: Path):
    global INDEX_MUDOU
    index = pasta / "index.html"
    if index.exists():
        index.unlink()
        INDEX_MUDOU = True
        print(f"🧹 index removido: {pasta.resolve()}")


def escrever_index(path: Path, conteudo: str):
    global INDEX_MUDOU
    if not path.exists() or path.read_text(encoding="utf-8") != conteudo:
        path.write_text(conteudo, encoding="utf-8")
        INDEX_MUDOU = True
        print(f"✔ index atualizado: {path.parent.resolve()}")


def gerar_index(pasta: Path, raiz: Path, repos_recentes: list[Path]):
    contem_zip_direto = pasta_contem_zip_direto(pasta)
    raiz_tem_zip = bool(repos_recentes)

    # ❌ regra de remoção
    if (
        (pasta == raiz and not raiz_tem_zip) or
        (pasta != raiz and not contem_zip_direto)
    ):
        remover_index(pasta)
        return

    itens = sorted(
        pasta.iterdir(),
        key=lambda x: (not x.is_dir(), x.name.lower())
    )

    linhas = [
        "<!DOCTYPE html>",
        "<html>",
        "<head>",
        '<meta charset="utf-8">',
        "<title>Directory listing</title>",
        "</head>",
        "<body>",
        "<h1>Directory listing</h1>",
        "<hr/>",
        "<pre>",
    ]

    if pasta != raiz:
        linhas.append('<a href="../index.html">..</a>')

    for item in itens:
        if item.name.startswith(".") or item.name == "index.html":
            continue

        if item.is_dir():
            if pasta == raiz or pasta_contem_zip_direto(item):
                linhas.append(
                    f'<a href="./{item.name}/index.html">{item.name}/</a>'
                )

        elif item.is_file() and item.suffix.lower() == ".zip":
            linhas.append(
                f'<a href="./{item.name}">{item.name}</a>'
            )

    linhas.extend([
        "</pre>",
        "</body>",
        "</html>",
    ])

    if pasta == raiz and raiz_tem_zip:
        linhas.append("")
        linhas.append('<div id="Repositorio-KODI" style="display:none">')
        linhas.append("<table>")
        for repo in repos_recentes:
            rel = repo.relative_to(raiz).as_posix()
            linhas.append(f'<tr><td><a href="{rel}">{rel}</a></td></tr>')
        linhas.append("</table>")
        linhas.append("</div>")

    escrever_index(pasta / "index.html", "\n".join(linhas))


def varrer_recursivo(pasta: Path, raiz: Path, repos_recentes: list[Path]):
    for item in pasta.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            varrer_recursivo(item, raiz, repos_recentes)

    gerar_index(pasta, raiz, repos_recentes)


if __name__ == "__main__":
    raiz = Path(".")

    # 1️⃣ primeira leitura
    repos_recentes = encontrar_repos_mais_recentes(raiz)

    varrer_recursivo(raiz, raiz, repos_recentes)

    # 2️⃣ se algo mudou, recalcula versões e atualiza raiz
    if INDEX_MUDOU:
        print("🔁 Recalculando versão mais recente após mudanças...")
        repos_recentes = encontrar_repos_mais_recentes(raiz)
        gerar_index(raiz, raiz, repos_recentes)
