# -*- coding: utf-8 -*-
from resources.lib.menus import thunder, Donate
import sys
import re
import xbmcaddon

addonId = re.search('plugin://(.+?)/', str(sys.argv[0])).group(1)
addon = thunder(addonId)

def router(params):
    action = params.get("action")
    name = params.get("name", "")
    url = params.get("url", "")
    iconimage = params.get("iconimage", "")
    fanart = params.get("fanart", "")
    description = params.get("description", "")
    codec = params.get("codec", "")
    playable = params.get("playable", "")
    duration = params.get("duration", "")
    originaltitle = params.get("originaltitle", "")
    imdbnumber = params.get("imdbnumber", "")
    aired = params.get("aired", "")
    genre = params.get("genre", "")
    season = params.get("season", "")
    episode = params.get("episode", "")
    year = params.get("year", "")
    video_title = params.get("video_title", "")
    search_text = params.get("search", "")
    video_id = params.get("video_id")
    page = params.get("page", "1")
    mediatype = params.get("mediatype", "")
    is_anime = params.get("is_anime", "false")
    anime_year = params.get("anime_year", "")
    anime_season = params.get("anime_season", "")

    if action is None:
        addon.home()
    elif action == "movies":
        addon.movies()
    elif action == "tv_shows":
        addon.tv_shows()
    elif action == "animes":
        addon.animes()
    elif action == "popular_movies":
        addon.pagination_movies_popular(page)
    elif action == "premiere_movies":
        addon.pagination_movies_premiere(page)
    elif action == "trending_movies":
        addon.pagination_movies_trending(page)
    elif action == "search_movies":
        addon.search_movies(search_text, page)
    elif action == "popular_tv_shows":
        addon.pagination_tv_shows_popular(page)
    elif action == "premiere_tv_shows":
        addon.pagination_tv_shows_premiere(page)
    elif action == "trending_tv_shows":
        addon.pagination_tv_shows_trending(page)
    elif action == "search_tv_shows":
        addon.search_tv_shows(search_text, page)
    elif action == "popular_animes":
        addon.pagination_animes_popular(page)
    elif action == "airing_animes":
        addon.pagination_animes_airing(page)
    elif action == "search_animes":
        addon.search_animes(search_text, page)
    elif action == "animes_by_year":
        addon.animes_by_year(anime_year)
    elif action == "animes_by_season":
        addon.pagination_animes_by_season(anime_year, anime_season, page)
    elif action == "details":
        addon.details(video_id, year, iconimage, fanart, description, mediatype, is_anime)
    elif action == "season_tvshow":
        addon.season_tvshow(video_id, year, season)
    elif action == "provider":
        if addon.is_auto_play_enabled():
            addon.auto_play_preferred_language(imdbnumber, year, season, episode, video_title, genre, iconimage, fanart, description)
        else:
            addon.list_server_links(imdbnumber, year, season, episode, name, video_title, genre, iconimage, fanart, description, is_anime)
    elif action == "play_resolve":
        addon.resolve_links(url, video_title, imdbnumber, year, season, episode, genre, iconimage, fanart, description, playable, is_anime)
    elif action == "settings":
        xbmcaddon.Addon().openSettings()
    elif action == "clear_cache":
        addon.clear_cache()
    elif action == "show_cache_size":
        addon.show_cache_size()
    elif action == "donate":
        i = Donate()
        i.doModal()

if __name__ == '__main__':
    try:
        from urllib.parse import parse_qsl
    except Exception:
        from six.moves.urllib_parse import parse_qsl

    params = {}
    if len(sys.argv) > 2 and sys.argv[2]:
        m = re.search(r'\?(.+)', sys.argv[2])
        if m:
            params = dict(parse_qsl(m.group(1)))

    router(params)