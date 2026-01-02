# -*- coding: utf-8 -*-
from resources.lib.utils import get_current_date, get_dates, years_tvshows
from resources.lib.autotranslate import AutoTranslate
from kodi_helper import requests
import xbmcaddon
import xbmcvfs
import os
import time
import hashlib
import json
from urllib.parse import quote
import sqlite3

addon = xbmcaddon.Addon()
TRANSLATE = xbmcvfs.translatePath
profile_dir = TRANSLATE(addon.getAddonInfo('profile'))
cache_dir = os.path.join(profile_dir, 'cache')
db_file = os.path.join(cache_dir, 'cache.db')

if not xbmcvfs.exists(cache_dir):
    xbmcvfs.mkdirs(cache_dir)

API_KEY = '92c1507cc18d85290e7a0b96abb37316'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36'

def get_config_ttl():
    try:
        days = int(addon.getSetting('cache_ttl_days') or '7')
        return days * 86400 if days > 0 else 0
    except:
        return 7 * 86400

def init_db():
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cache (
            url_hash TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            timestamp REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def clean_expired_cache(ttl_seconds):
    if ttl_seconds <= 0:
        return
    current_time = time.time()
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM cache WHERE timestamp < ?', (current_time - ttl_seconds,))
    conn.commit()
    conn.close()

def save_to_cache(url, data):
    hash_val = hashlib.md5(url.encode()).hexdigest()
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO cache (url_hash, data, timestamp)
        VALUES (?, ?, ?)
    ''', (hash_val, json.dumps(data), time.time()))
    conn.commit()
    conn.close()

def get_json(url, ttl=None):
    if ttl is None:
        ttl = get_config_ttl()

    try:
        cache_ttl_days = int(addon.getSetting('cache_ttl_days') or '7')
        cache_ttl_seconds = cache_ttl_days * 86400 if cache_ttl_days > 0 else 0

        if cache_ttl_days == 0:
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM cache')
            conn.commit()
            conn.close()
        elif cache_ttl_days > 0:
            clean_expired_cache(cache_ttl_seconds)
    except:
        pass

    hash_val = hashlib.md5(url.encode()).hexdigest()
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('SELECT data, timestamp FROM cache WHERE url_hash = ?', (hash_val,))
    row = cursor.fetchone()

    if row:
        cached_data, timestamp = row
        if time.time() - timestamp < ttl:
            conn.close()
            return json.loads(cached_data)

    conn.close()

    try:
        r = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=10)
        r.raise_for_status()
        data = r.json()
        save_to_cache(url, data)
        return data
    except:
        return {}

def get_cache_size():
    if xbmcvfs.exists(db_file):
        try:
            stat = xbmcvfs.Stat(db_file)
            return stat.st_size()
        except:
            pass
    return 0

def movies_popular_api(page):
    url = f'https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&page={page}&language={AutoTranslate.language("lang-api")}'
    src = get_json(url)
    return src.get('total_pages', 0), src.get('results', [])

def movies_api(page, t):
    url = {
        'premiere': f'https://api.themoviedb.org/3/movie/now_playing?api_key={API_KEY}&page={page}&language={AutoTranslate.language("lang-api")}',
        'trending': f'https://api.themoviedb.org/3/trending/movie/day?api_key={API_KEY}&page={page}&language={AutoTranslate.language("lang-api")}'
    }.get(t, '')
    if url:
        src = get_json(url)
        return src.get('total_pages', 0), src.get('results', [])
    return 0, []

def tv_shows_popular_api(page):
    url = f'https://api.themoviedb.org/3/tv/popular?api_key={API_KEY}&page={page}&language={AutoTranslate.language("lang-api")}'
    src = get_json(url)
    return src.get('total_pages', 0), src.get('results', [])

def tv_shows_trending_api(page):
    url = f'https://api.themoviedb.org/3/trending/tv/day?api_key={API_KEY}&page={page}&language={AutoTranslate.language("lang-api")}'
    src = get_json(url)
    return src.get('total_pages', 0), src.get('results', [])

def search_movies_api(search, page):
    url = f'https://api.themoviedb.org/3/search/multi?api_key={API_KEY}&query={quote(search)}&page={page}&language={AutoTranslate.language("lang-api")}'
    src = get_json(url)
    return src.get('total_pages', 0), src.get('results', [])

def tv_shows_premiere_api(page):
    year = get_current_date()
    url = f'https://api.themoviedb.org/3/discover/tv?api_key={API_KEY}&sort_by=popularity.desc&first_air_date_year={year}&page={page}&language={AutoTranslate.language("lang-api")}'
    src = get_json(url)
    return src.get('total_pages', 0), src.get('results', [])

def animes_popular_api(page):
    url = f'https://api.jikan.moe/v4/top/anime?page={page}&filter=bypopularity'
    src = get_json(url)
    return src.get('pagination', {}).get('last_visible_page', 0), src.get('data', [])

def animes_airing_api(page):
    url = f'https://api.jikan.moe/v4/seasons/now?page={page}'
    src = get_json(url)
    return src.get('pagination', {}).get('last_visible_page', 0), src.get('data', [])

def search_animes_api(search, page):
    url = f'https://api.jikan.moe/v4/anime?q={quote(search)}&page={page}'
    src = get_json(url)
    return src.get('pagination', {}).get('last_visible_page', 0), src.get('data', [])

def animes_by_season_api(year, season, page):
    url = f'https://api.jikan.moe/v4/seasons/{year}/{season}?page={page}'
    src = get_json(url)
    return src.get('pagination', {}).get('last_visible_page', 0), src.get('data', [])

def open_movie_api(id):
    url = f'https://api.themoviedb.org/3/movie/{id}?api_key={API_KEY}&append_to_response=external_ids&language={AutoTranslate.language("lang-api")}'
    return get_json(url)

def open_season_api(id):
    url = f'https://api.themoviedb.org/3/tv/{id}?api_key={API_KEY}&append_to_response=external_ids&language={AutoTranslate.language("lang-api")}'
    return get_json(url)

def show_episode_api(id, season):
    url = f'https://api.themoviedb.org/3/tv/{id}/season/{season}?api_key={API_KEY}&append_to_response=external_ids&language={AutoTranslate.language("lang-api")}'
    return get_json(url)

def open_episode_api(id, season, episode):
    url = f'https://api.themoviedb.org/3/tv/{id}/season/{season}/episode/{episode}?api_key={API_KEY}&append_to_response=external_ids&language={AutoTranslate.language("lang-api")}'
    return get_json(url)

def open_anime_api(id):
    url = f'https://api.jikan.moe/v4/anime/{id}/full'
    return get_json(url)

def open_anime_episodes_api(id):
    cache_url = f'https://cache.jikan.moe/anime/{id}/episodes_full'
    cached = get_json(cache_url)
    if cached and 'episodes' in cached:
        return cached['episodes']

    all_episodes = []
    page = 1
    first_request = True
    
    while True:
        url = f'https://api.jikan.moe/v4/anime/{id}/episodes?page={page}'
        src = get_json(url)
        episodes = src.get('data', [])
        
        if not episodes:
            break
            
        all_episodes.extend(episodes)
        
        pagination = src.get('pagination', {})
        has_next_page = pagination.get('has_next_page', False)
        
        if not has_next_page:
            break
            
        page += 1
        
        if first_request:
            first_request = False
        else:
            time.sleep(0.4)
    
    save_to_cache(cache_url, {'episodes': all_episodes})
    return all_episodes

def open_anime_episode_api(id, episode):
    url = f'https://api.jikan.moe/v4/anime/{id}/episodes/{episode}'
    src = get_json(url)
    return src.get('data', {})

def find_tv_show_api(imdb):
    url = f'https://api.themoviedb.org/3/find/{imdb}?api_key={API_KEY}&external_source=imdb_id&language={AutoTranslate.language("lang-api")}'
    return get_json(url)

def search_tv_by_title(title, year=None):
    try:
        q = quote(title)
        url = f'https://api.themoviedb.org/3/search/tv?api_key={API_KEY}&language={AutoTranslate.language("lang-api")}&query={q}'
        if year:
            url += f'&first_air_date_year={year}'
        return get_json(url)
    except:
        return {}

def search_movie_by_title(title, year=None):
    try:
        q = quote(title)
        url = f'https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&language={AutoTranslate.language("lang-api")}&query={q}'
        if year:
            url += f'&year={year}'
        return get_json(url)
    except:
        return {}

def lastest_episodes_api(date):
    url = f'https://api.tvmaze.com/schedule?date={date}'
    return get_json(url)

def cleanhtml(raw_html):
    import re
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html)

def get_date():
    api_time = 'http://worldtimeapi.org/api/timezone/America/New_York'
    src = get_json(api_time)
    datetime = src.get('datetime', '')
    if datetime:
        last_year = datetime.split('-')[0]
        fulldate = datetime.split('T')[0]
    else:
        from datetime import date
        date_today = date.today()
        last_year = date_today.year
        fulldate = str(date_today)
    return last_year, fulldate