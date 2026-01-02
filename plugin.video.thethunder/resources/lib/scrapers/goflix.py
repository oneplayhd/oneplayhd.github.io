# -*- coding: utf-8 -*-
WEBSITE = 'GOFLIX'

import re
import os
import sys
import difflib
import base64
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
import requests

# Sessão requests com headers realistas
session = requests.Session()
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
session.headers.update({
    'User-Agent': USER_AGENT,
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept': '*/*',
    'Referer': 'https://goflixy.lol/',
})

try:
    from resources.lib.autotranslate import AutoTranslate
    portuguese = AutoTranslate.language('Portuguese')
    english = AutoTranslate.language('English')
except ImportError:
    portuguese = 'DUBLADO'
    english = 'LEGENDADO'

try:
    from kodi_helper import myAddon
    addonId = re.search('plugin://(.+?)/', str(sys.argv[0])).group(1)
    addon = myAddon(addonId)
    select = addon.select
except ImportError:
    local_path = os.path.dirname(os.path.realpath(__file__))
    lib_path = local_path.replace('scrapers', '')
    sys.path.append(lib_path)

from resources.lib.resolver import Resolver


class source:

    @classmethod
    def normalize_title(cls, title):
        if not title:
            return ''
        title = re.sub(r'\s*[:]\s*', ' ', title)
        title = re.sub(r'\s+', ' ', title).strip()
        return title

    @classmethod
    def find_title(cls, imdb):
        url = f'https://m.imdb.com/pt/title/{imdb}/'
        headers = {'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'}

        try:
            r = session.get(url, headers=headers, timeout=15)
            if not r or r.status_code != 200:
                return '', '', ''

            soup = BeautifulSoup(r.text, 'html.parser')

            title_pt = ''
            hero = soup.find('h1', {'data-testid': 'hero__pageTitle'})
            if hero:
                span = hero.find('span')
                title_pt = (span.text if span else hero.text).strip()

            original_title = ''
            orig_block = soup.find('div', {'data-testid': 'hero-title-block__original-title'})
            if orig_block:
                txt = orig_block.get_text(strip=True)
                original_title = re.sub(r'^(T[íi]tulo original|Original title)[:\s]*', '', txt, flags=re.I).strip()

            if not original_title:
                m = re.search(r'T[íi]tulo original[:\s]*["\']?([^<"\']+)["\']?', r.text, re.I)
                if m:
                    original_title = m.group(1).strip()

            year = ''
            year_link = soup.find('a', href=re.compile(r'/releaseinfo'))
            if year_link:
                y = re.search(r'\d{4}', year_link.text)
                if y:
                    year = y.group(0)

            if not year:
                release_li = soup.find('li', {'data-testid': 'title-details-releasedate'})
                if release_li:
                    y = re.search(r'\d{4}', release_li.get_text())
                    if y:
                        year = y.group(0)

            if not year:
                y = re.search(r'\b(19|20)\d{2}\b', r.text[:6000])
                if y:
                    year = y.group(0)

            return title_pt or original_title, original_title or title_pt, year or ''

        except Exception:
            return '', '', ''

    @classmethod
    def _resolve_fembed(cls, share_id, lang, cvalue=""):
        try:
            page = f"https://fembed.sx/e/{share_id}/"
            if cvalue:
                page = f"https://fembed.sx/e/{share_id}/{cvalue}"

            r0 = session.get(page)
            if not r0.ok:
                return None

            html = r0.text
            cookies = r0.cookies

            api_match = re.search(r'api\s*=\s*"([^"]+)"', html)
            api_path = api_match.group(1).replace("\\/", "/") if api_match else f"/api.php?s={share_id}&c={cvalue}"
            api_url = urljoin("https://fembed.sx", api_path)

            pdata = {"action": "getPlayer", "lang": lang, "key": base64.b64encode(b"0").decode()}

            r1 = session.post(api_url, data=pdata, headers={"Referer": page}, cookies=cookies)
            if not r1.ok:
                return None

            m = re.search(r'src=["\']([^"\']*action=getAds[^"\']*)["\']', r1.text)
            if not m:
                return None
            getads = m.group(1)
            if getads.startswith("//"):
                getads = "https:" + getads
            elif getads.startswith("/"):
                getads = "https://fembed.sx" + getads

            r2 = session.get(getads,
                               headers={"Referer": page, "X-Requested-With": "XMLHttpRequest"},
                               cookies=cookies)
            if not r2.ok:
                return None

            link = re.search(r'src=["\']([^"\']*bysevepoin\.[^"\']*)["\']', r2.text, re.I)
            if not link:
                return None

            dirty_url = link.group(1)
            if dirty_url.startswith("//"):
                dirty_url = "https:" + dirty_url

            clean_url = re.sub(r'(/e/[0-9A-Za-z]+).*', r'\1', dirty_url)
            clean_url = clean_url.replace("http://", "https://")
            return clean_url

        except:
            return None

    @classmethod
    def search_movies(cls, imdb, year=None):
        pt, original_title, imdb_year = cls.find_title(imdb)
        if not pt:
            return []

        pt = cls.normalize_title(pt)
        original_title = cls.normalize_title(original_title or pt)

        r = session.get(f"https://goflixy.lol/buscar?q={quote_plus(pt)}")
        if not r.ok:
            return []

        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", class_="card"):
            if "/filme/" not in a.get("href", ""):
                continue
            title_tag = a.find("div", "card-title")
            if not title_tag:
                continue

            raw = title_tag.get_text(strip=True)
            clean_title = re.sub(r"\s*\(\d{4}\)\s*$", "", raw).strip()
            card_year_match = re.search(r"\((\d{4})\)", raw)
            card_year = card_year_match.group(1) if card_year_match else None

            ratio = difflib.SequenceMatcher(None, pt.lower(), clean_title.lower()).ratio()
            if ratio < 0.82:
                continue
            if year and card_year and abs(int(year) - int(card_year)) > 1:
                continue

            page = urljoin("https://goflixy.lol", a.get("href"))
            r2 = session.get(page)
            if not r2.ok:
                continue

            iframe = BeautifulSoup(r2.text, "html.parser").find("iframe", id="player")
            if not iframe:
                continue

            src = iframe.get("src", "")
            if src.startswith("//"):
                src = "https:" + src

            m = re.search(r"/e/([0-9A-Za-z]+)", src)
            if not m:
                continue

            ID = m.group(1)
            out = []
            dub = cls._resolve_fembed(ID, "DUB")
            leg = cls._resolve_fembed(ID, "LEG")

            if dub:
                out.append(("FILEMOON - DUBLADO", dub))
            if leg:
                out.append(("FILEMOON - LEGENDADO", leg))

            return out
        return []

    @classmethod
    def search_tvshows(cls, imdb, year, season, episode):
        try:
            season = int(season)
            episode = int(episode)
        except:
            return []

        pt, original_title, imdb_year = cls.find_title(imdb)
        if not pt:
            return []

        pt = cls.normalize_title(pt)
        original_title = cls.normalize_title(original_title or pt)

        r = session.get(f"https://goflixy.lol/buscar?q={quote_plus(pt)}")
        if not r.ok:
            return []

        soup = BeautifulSoup(r.text, "html.parser")
        serie_url = None
        for a in soup.find_all("a", class_="card"):
            href = a.get("href", "")
            if "/serie/" not in href:
                continue
            title_tag = a.find("div", "card-title")
            if not title_tag:
                continue

            raw = title_tag.get_text(strip=True)
            clean = re.sub(r"\s*\(\d{4}\)\s*$", "", raw).strip()
            card_year_match = re.search(r"\((\d{4})\)", raw)
            card_year = card_year_match.group(1) if card_year_match else None

            ratio = difflib.SequenceMatcher(None, pt.lower(), clean.lower()).ratio()
            if ratio >= 0.82 and (not year or not card_year or abs(int(year) - int(card_year)) <= 1):
                serie_url = urljoin("https://goflixy.lol", href)
                break
        if not serie_url:
            return []

        r2 = session.get(serie_url)
        if not r2.ok:
            return []

        m = re.search(r"const EP = (\{[\s\S]*?\});", r2.text)
        if not m:
            return []

        ep = eval(m.group(1).replace("true", "True").replace("false", "False"))
        skey = str(season)
        if skey not in ep:
            return []

        for e in ep[skey]:
            if str(e.get("n")) == str(episode):
                url = e.get("url", "")
                if url.startswith("//"):
                    url = "https:" + url

                m2 = re.search(r"/e/([0-9A-Za-z]+)/(.+)", url)
                if not m2:
                    continue

                ID = m2.group(1)
                cvalue = m2.group(2)

                out = []
                dub = cls._resolve_fembed(ID, "DUB", cvalue)
                leg = cls._resolve_fembed(ID, "LEG", cvalue)

                if dub:
                    out.append(("FILEMOON - DUBLADO", dub))
                if leg:
                    out.append(("FILEMOON - LEGENDADO", leg))

                return out
        return []

    @classmethod
    def resolve_movies(cls, url):
        streams = []
        if not url:
            return streams
        sub = ''
        try:
            sub_part = url.split('http')[2]
            sub = 'http' + sub_part.split('&')[0]
            if '.srt' not in sub:
                sub = ''
        except:
            pass
        stream = url.split('?')[0].split('#')[0]
        resolver = Resolver()
        resolved, sub_from_resolver = resolver.resolverurls(stream)
        if resolved:
            streams.append((resolved, sub if sub else sub_from_resolver, USER_AGENT))
        return streams

    @classmethod
    def resolve_tvshows(cls, url):
        return cls.resolve_movies(url)

    __site_url__ = ['https://goflixy.lol/']
