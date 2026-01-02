# resources/lib/update.py
# -*- coding: utf-8 -*-
'''
Atualização automática do TheThunder - Branch: main
Com exclusão automática de scrapers removidos + correção para .update vazio ou ausente
'''

import os
import json
import glob
import xbmc
import xbmcvfs
import xbmcaddon
from urllib.request import urlopen, Request
from contextlib import closing

ADDON = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo("path")
SCRAPERS_PATH = xbmcvfs.translatePath(os.path.join(ADDON_PATH, "resources", "lib", "scrapers"))
LIB_PATH = xbmcvfs.translatePath(os.path.join(ADDON_PATH, "resources", "lib"))
RESOURCES_PATH = xbmcvfs.translatePath(os.path.join(ADDON_PATH, "resources"))

LOCAL_VERSION = os.path.join(SCRAPERS_PATH, ".update")

BRANCH = "main"
BASE_URL = f"https://raw.githubusercontent.com/icarok99/plugin.video.thethunder/{BRANCH}/"
REMOTE_VERSION_URL = BASE_URL + "last_update.txt"
RAW_SCRAPERS = BASE_URL + "resources/lib/scrapers/"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

def log(msg):
    xbmc.log(f"[TheThunder AutoUpdate] {msg}", xbmc.LOGINFO)

def http_get(url, binary=False):
    try:
        req = Request(url, headers={"User-Agent": USER_AGENT})
        # Timeout removido para evitar interrupções em conexões lentas
        with closing(urlopen(req)) as r:
            data = r.read()
            if binary:
                return data
            else:
                return data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n").strip()
    except Exception as e:
        log(f"Erro ao baixar {url}: {e}")
        return None

def get_local_version():
    if not xbmcvfs.exists(LOCAL_VERSION):
        log("Arquivo de controle de versão (.update) não encontrado")
        return None
    try:
        with open(LOCAL_VERSION, "r", encoding="utf-8") as f:
            content = f.read()
            normalized = content.replace("\r\n", "\n").replace("\r", "\n").strip()
            if not normalized:
                log("Arquivo .update está vazio (primeira instalação ou versão antiga)")
                return None
            log(f"Versão local atual: {normalized}")
            return normalized
    except Exception as e:
        log(f"Erro ao ler arquivo .update: {e}")
        return None

def save_local_version(ver):
    try:
        with open(LOCAL_VERSION, "w", encoding="utf-8", newline="\n") as f:
            f.write(ver + "\n")
        log(f"Versão local atualizada para: {ver}")
    except Exception as e:
        log(f"Erro ao salvar versão local: {e}")

def get_remote_version():
    version = http_get(REMOTE_VERSION_URL)
    if version is None:
        log("Não foi possível obter a versão do repositório (problema de conexão)")
    else:
        log(f"Versão mais recente no repositório: {version}")
    return version

def list_remote_scrapers():
    tree_url = f"https://api.github.com/repos/icarok99/plugin.video.thethunder/git/trees/{BRANCH}?recursive=1"
    tree = http_get(tree_url)
    if not tree:
        return []
    try:
        data = json.loads(tree)
        files = []
        for item in data.get("tree", []):
            if item["path"].startswith("resources/lib/scrapers/") and item["type"] == "blob":
                fname = os.path.basename(item["path"])
                if fname not in ["__init__.py", ".update"]:
                    files.append(fname)
        return files
    except Exception as e:
        log(f"Erro ao listar scrapers do repositório: {e}")
        return []

ADDITIONAL_FILES = [
    {"remote": "resources/lib/sources.py",   "local": os.path.join(LIB_PATH, "sources.py")},
    {"remote": "resources/settings.xml",     "local": os.path.join(RESOURCES_PATH, "settings.xml")},
]

def auto_update():
    remote_version = get_remote_version()
    if remote_version is None:
        log("Atualização cancelada: sem conexão com o repositório")
        return False

    local_version = get_local_version()

    if local_version is None:
        log("Primeira instalação detectada - marcando versão atual, sem baixar arquivos")
        save_local_version(remote_version)
        return False

    if local_version == remote_version:
        log("Addon já está na versão mais recente")
        return False

    log(f"Atualização necessária: versão local {local_version} → versão nova {remote_version}")

    updated = 0

    remote_scrapers = list_remote_scrapers()
    if not remote_scrapers:
        log("Aviso: não foi possível obter lista de scrapers do repositório")

    local_pattern = os.path.join(SCRAPERS_PATH, "*.py")
    local_scrapers = [os.path.basename(f) for f in glob.glob(local_pattern)]
    local_scrapers = [f for f in local_scrapers if f not in ["__init__.py", ".update"]]

    for fname in remote_scrapers:
        url = f"{RAW_SCRAPERS}{fname}"
        content = http_get(url, binary=True)
        if content is not None:
            dest = os.path.join(SCRAPERS_PATH, fname)
            try:
                with open(dest, "wb") as f:
                    f.write(content)
                updated += 1
                log(f"Scraper atualizado/adicionado: {fname}")
                if fname in local_scrapers:
                    local_scrapers.remove(fname)
            except Exception as e:
                log(f"Erro ao salvar scraper {fname}: {e}")

    for fname in local_scrapers:
        try:
            os.remove(os.path.join(SCRAPERS_PATH, fname))
            log(f"Scraper removido (não existe mais no repositório): {fname}")
            updated += 1
        except Exception as e:
            log(f"Erro ao remover scraper {fname}: {e}")

    for file in ADDITIONAL_FILES:
        url = BASE_URL + file["remote"]
        content = http_get(url, binary=True)
        if content is not None:
            try:
                with open(file["local"], "wb") as f:
                    f.write(content)
                updated += 1
                log(f"Arquivo atualizado: {os.path.basename(file['remote'])}")
            except Exception as e:
                log(f"Erro ao atualizar {os.path.basename(file['remote'])}: {e}")

    save_local_version(remote_version)
    log(f"Atualização concluída com sucesso! {updated} arquivo(s) alterado(s)")
    return True

if __name__ == "__main__":
    auto_update()