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


def escrever_index(pasta: Path, conteudo: str):
    global INDEX_MUDOU
    index = pasta / "index.html"

    if not index.exists() or index.read_text(encoding="utf-8") != conteudo:
        index.write_text(conteudo, encoding="utf-8")
        INDEX_MUDOU = True
        print(f"✔ index gerado/atualizado: {pasta.resolve()}")


def gerar_index(pasta: Path, raiz: Path, repos_recentes: list[Path]):
    tem_zip = pasta_contem_zip_direto(pasta)
    raiz_tem_zip = bool(repos_recentes)

    # ❌ remove index de pasta sem zip (exceto raiz)
    if pasta != raiz and not tem_zip:
        remover_index(pasta)
        return

    # ❌ remove index da raiz se não houver nenhum zip no repo
    if pasta == raiz and not raiz_tem_zip:
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

    # 🔥 tabela oculta da raiz
    if pasta == raiz and raiz_tem_zip:
        linhas.append("")
        linhas.append('<div id="Repositorio-KODI" style="display:none">')
        linhas.append("<table>")
        for repo in repos_recentes:
            rel = repo.relative_to(raiz).as_posix()
            linhas.append(f'<tr><td><a href="{rel}">{rel}</a></td></tr>')
        linhas.append("</table>")
        linhas.append("</div>")

    escrever_index(pasta, "\n".join(linhas))


def varrer_recursivo(pasta: Path, raiz: Path, repos_recentes: list[Path]):
    for item in pasta.iterdir():
        if item.is_dir() and not item.name.startswith("."):
            varrer_recursivo(item, raiz, repos_recentes)

    gerar_index(pasta, raiz, repos_recentes)


if __name__ == "__main__":
    raiz = Path(".")

    repos_recentes = encontrar_repos_mais_recentes(raiz)

    varrer_recursivo(raiz, raiz, repos_recentes)

    # 🔥 REGRA FINAL: se QUALQUER index mudou, a raiz é sempre regenerada
    if INDEX_MUDOU:
        print("🔁 Sincronizando index da raiz...")
        repos_recentes = encontrar_repos_mais_recentes(raiz)
        gerar_index(raiz, raiz, repos_recentes)
