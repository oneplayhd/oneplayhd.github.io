from pathlib import Path
import re

ROOT = Path(".")

def extrair_versao(nome):
    m = re.search(r"-([\d\.]+)\.zip$", nome)
    return m.group(1) if m else None

def zip_mais_recente(pasta: Path):
    zips = []
    for f in pasta.iterdir():
        if f.is_file() and f.suffix.lower() == ".zip":
            ver = extrair_versao(f.name)
            if ver:
                try:
                    vtuple = tuple(map(int, ver.split(".")))
                    zips.append((vtuple, f))
                except ValueError:
                    pass
    if not zips:
        return None
    return max(zips, key=lambda x: x[0])[1]

def gerar_index_raiz():
    # HTML VISUAL (formato antigo, sem table)
    linhas = [
        "<html>",
        "<body>",
        "<h1>Directory listing</h1>",
        "<hr/>",
        "<pre>"
    ]

    # BLOCO OCULTO PARA O KODI (fora do html)
    hidden_links = [
        '<div id="div" style="display:none">',
        "<table>"
    ]

    for pasta in sorted(p for p in ROOT.iterdir() if p.is_dir() and not p.name.startswith(".")):
        zip_recente = zip_mais_recente(pasta)
        if not zip_recente:
            continue

        # Visual para navegador
        linhas.append(f'<a href="./{pasta.name}/">{pasta.name}/</a>')

        # Link direto para o Kodi
        rel = zip_recente.relative_to(ROOT).as_posix()
        hidden_links.append(
            f'<tr><td><a href="{rel}">{rel}</a></td></tr>'
        )

    linhas += [
        "</pre>",
        "</body>",
        "</html>"
    ]

    hidden_links += [
        "</table>",
        "</div>"
    ]

    conteudo_final = "\n".join(linhas) + "\n\n" + "\n".join(hidden_links)
    (ROOT / "index.html").write_text(conteudo_final, encoding="utf-8")

if __name__ == "__main__":
    gerar_index_raiz()
