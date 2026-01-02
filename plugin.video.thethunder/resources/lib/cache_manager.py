#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cache_manager.py - plugin.video.thethunder
- Limpa arquivos de cache e mostra notificação.
- Mostra o tamanho atual do cache.
- Funciona dentro e fora do Kodi.
"""

import sys
import os

try:
    import xbmc
    import xbmcgui
    import xbmcvfs
    import xbmcaddon
except ImportError:
    xbmc = xbmcgui = xbmcvfs = xbmcaddon = None

# --- Utilidades ---
def is_kodi():
    return xbmc is not None and xbmcgui is not None

def notify(title, message, duration=3000):
    try:
        if is_kodi():
            xbmcgui.Dialog().notification(title, message, xbmcgui.NOTIFICATION_INFO, duration)
        else:
            print(f"[{title}] {message}")
    except Exception:
        print(f"[{title}] {message}")

def log(msg):
    try:
        if is_kodi():
            xbmc.log(f"[thethunder][cache_manager] {msg}", xbmc.LOGINFO)
        else:
            print(f"[thethunder][cache_manager] {msg}")
    except Exception:
        print(f"[thethunder][cache_manager] {msg}")

# --- Diretório de Cache ---
def get_cache_dir():
    if is_kodi():
        try:
            addon = xbmcaddon.Addon("plugin.video.thethunder")
            profile_dir = xbmcvfs.translatePath(addon.getAddonInfo("profile"))
            return os.path.join(profile_dir, "cache")
        except Exception:
            pass

    if os.name == "nt":
        base = os.getenv("APPDATA", os.path.expanduser("~"))
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Caches")
    else:
        base = os.getenv("XDG_CACHE_HOME", os.path.expanduser("~/.cache"))

    return os.path.join(base, "thethunder", "cache")

def get_cache_db_path():
    return os.path.join(get_cache_dir(), "cache.db")

# --- Operações de Cache ---
def clear_cache():
    cache_dir = get_cache_dir()
    db_path = get_cache_db_path()

    deleted = False
    if is_kodi() and xbmcvfs.exists(db_path):
        xbmcvfs.delete(db_path)
        deleted = True
    elif os.path.exists(db_path):
        try:
            os.remove(db_path)
            deleted = True
        except Exception as e:
            log(f"Erro ao remover cache.db: {e}")

    # Remove também o diretório se estiver vazio (opcional)
    try:
        if is_kodi() and xbmcvfs.exists(cache_dir):
            dirs, files = xbmcvfs.listdir(cache_dir)
            if not dirs and not files:
                xbmcvfs.rmdir(cache_dir, force=True)
    except:
        pass

    notify("TheThunder", "Cache limpo com sucesso!" if deleted else "Nenhum cache encontrado")
    log("Cache limpo")

# --- Medição de tamanho ---
def human_readable_size(size_bytes):
    if size_bytes == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(units) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.2f} {units[i]}"

def get_cache_size_local():
    db_path = get_cache_db_path()
    if is_kodi() and xbmcvfs.exists(db_path):
        try:
            stat = xbmcvfs.Stat(db_path)
            return stat.st_size()
        except:
            return 0
    elif os.path.exists(db_path):
        try:
            return os.path.getsize(db_path)
        except:
            return 0
    return 0

def show_cache():
    size = get_cache_size_local()
    size_str = human_readable_size(size)
    notify("TheThunder", f"Tamanho do cache: {size_str}", 4000)
    log(f"Tamanho do cache: {size_str}")

# --- Execução via RunScript ---
if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ("clear_cache", "--clear-cache", "-c"):
            clear_cache()
        elif arg in ("show_cache", "--show-cache", "-s"):
            show_cache()
    else:
        clear_cache()