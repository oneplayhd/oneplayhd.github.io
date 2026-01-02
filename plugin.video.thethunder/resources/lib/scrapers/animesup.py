# -*- coding: utf-8 -*-
WEBSITE = 'ANIMESUP'

import re
import difflib
import unicodedata
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
import requests

session = requests.Session()
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
session.headers.update({
    'User-Agent': USER_AGENT,
    'Accept-Language': 'en-US,en;q=0.9,pt-BR;q=0.8,pt;q=0.7',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Referer': 'https://www.animesup.info/',
})

from resources.lib.resolver import Resolver


class source:

    QUOTE_MIN_CHARS = 60
    QUOTE_MIN_WORDS = 8

    @classmethod
    def _normalize(cls, text):
        if not text:
            return ""
        return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")

    @classmethod
    def _normalize_movie_hyphen(cls, title):
        if not title:
            return title
        return re.sub(
            r'\s*[\u002D\u2010\u2011\u2012\u2013\u2014\u2015-]\s*(the movie\b)',
            r' the movie',
            title,
            flags=re.I
        )

    @classmethod
    def _adjust_base_title(cls, title):
        if not title or '"' not in title:
            return title

        words = title.split()
        if len(title) < cls.QUOTE_MIN_CHARS and len(words) < cls.QUOTE_MIN_WORDS:
            return title

        return title.split('"', 1)[0].strip()

    @classmethod
    def _clean_title(cls, title):
        if not title:
            return ""

        t = cls._normalize(title.lower())
        t = re.sub(r'\bassistir\s+online\b', '', t)
        t = re.sub(r'\bonline\b', '', t)
        t = re.sub(r'[\"“”\'`]', '', t)
        t = re.sub(r'[-_:]', ' ', t)
        t = re.sub(r'[()\[\]]', '', t)
        t = re.sub(r'\b(\d+)(?:st|nd|rd|th|ª|º)\b', r'\1', t)
        t = re.sub(r'\s+', ' ', t)
        return t.strip()

    @classmethod
    def _strip_dublado(cls, text):
        return re.sub(r'\bdublado\b', '', text).strip()

    @classmethod
    def _has_extra_words(cls, base_clean, cand_clean):
        return cls._strip_dublado(cand_clean) != base_clean

    @classmethod
    def _extract_year(cls, text):
        if not text:
            return None
        m = re.search(r'\b(19|20)\d{2}\b', text)
        return int(m.group()) if m else None

    @classmethod
    def _extract_season_number(cls, text):
        if not text:
            return None
        text_lower = text.lower()
        patterns = [
            r'\b(\d+)[ªº]?\s*(?:temporada|season|t|temp|s)\b',
            r'\b(temporada|season|t|temp|s)\s*(\d+)\b',
            r'\b(\d+)\s*(?:ª|º|st|nd|rd|th)?\s*(?:temporada|season)\b',
            r'\b(\d+)\b',  # fallback para casos como "Boku no Hero 6"
        ]
        for pattern in patterns:
            m = re.search(pattern, text_lower)
            if m:
                try:
                    num = int(m.group(1))
                    if 1 <= num <= 20:
                        return num
                except:
                    pass
        return None

    @classmethod
    def _similarity_score(cls, base_titles, candidate_title, base_year=None, cand_year=None):
        cand_title = cls._normalize_movie_hyphen(candidate_title)
        cand_clean = cls._clean_title(cand_title)

        best_score = 0.0

        for base_title in base_titles:
            adj_base = cls._adjust_base_title(base_title)
            base_clean = cls._clean_title(adj_base)
            if not base_clean:
                continue

            if cls._has_extra_words(base_clean, cand_clean):
                continue

            score = difflib.SequenceMatcher(
                None,
                base_clean,
                cls._strip_dublado(cand_clean)
            ).ratio()

            if 'dublado' in cand_clean:
                score += 0.25

            if base_year and cand_year:
                score += 0.5 if base_year == cand_year else -0.5

            if score > best_score:
                best_score = score

        return best_score

    @classmethod
    def _extract_episode_links_from_page(cls, page_text):
        soup = BeautifulSoup(page_text, 'html.parser')
        items = soup.find_all('div', class_='ultimosEpisodiosHomeItem')
        episodes = {}
        for item in items:
            num_div = item.find('div', class_='ultimosEpisodiosHomeItemInfosNum')
            if not num_div:
                continue
            text = num_div.get_text(strip=True)
            m = re.search(r'epis[óo]dio\s*(\d+)', text, re.I)
            if not m:
                continue
            ep_num = int(m.group(1))
            a = item.find('a', href=True)
            if a and a['href'].startswith('/episodio/'):
                episodes[ep_num] = a['href']
        return episodes

    @classmethod
    def _build_page_url(cls, series_url, page_num):
        base = series_url.rstrip('/')
        if page_num <= 1:
            return base
        return f"{base}/page/{page_num}"

    @classmethod
    def _get_episode_page_url(cls, series_url, episode_num):
        page_num = 1
        while True:
            page_url = cls._build_page_url(series_url, page_num)
            r = session.get(page_url, timeout=15)
            if not r.ok:
                break
            episodes = cls._extract_episode_links_from_page(r.text)
            if not episodes:
                break
            if episode_num in episodes:
                return urljoin("https://www.animesup.info/", episodes[episode_num])
            page_num += 1

        r = session.get(series_url, timeout=15)
        if r.ok:
            episodes = cls._extract_episode_links_from_page(r.text)
            if episodes:
                fallback_ep = min(episodes.keys())
                return urljoin("https://www.animesup.info/", episodes[fallback_ep])
        return None

    @classmethod
    def _get_movie_episode_url(cls, page_text):
        soup = BeautifulSoup(page_text, "html.parser")
        for item in soup.select("div.ultimosEpisodiosHomeItem"):
            if re.search(r'\bfilme\b', item.get_text(" ", strip=True), re.I):
                a = item.find("a", href=True)
                if a:
                    return urljoin("https://www.animesup.info/", a["href"])
        return None

    @classmethod
    def _get_available_qualities(cls, episode_page_text):
        soup = BeautifulSoup(episode_page_text, 'html.parser')
        abas_box = soup.find('div', class_=re.compile(r'AbasBox', re.I))
        if not abas_box:
            return ["SD"]

        available = []
        for aba in abas_box.find_all('div', class_=re.compile(r'Aba', re.I)):
            text = aba.get_text(strip=True).upper()
            if text in ("SD", "HD"):
                available.append(text)
            elif text in ("FULLHD", "FULL HD", "FHD"):
                available.append("FULLHD")
        return available if available else ["SD"]

    @classmethod
    def _extract_video_urls(cls, episode_page_text):
        videos = {}
        containers = re.split(r'<div class="playerContainer"', episode_page_text)[1:]
        for i, container in enumerate(containers[:3]):
            m = re.search(r"var\s+vid\s*=\s*'([^']+\.mp4)';", container)
            if not m:
                continue
            url = m.group(1).strip()
            if "r2.cloudflarestorage.com" not in url:
                continue
            quality = ("SD", "HD", "FULLHD")[i]
            videos[quality] = url
        return videos

    @classmethod
    def _get_highest_quality_link(cls, episode_page_text, available):
        videos = cls._extract_video_urls(episode_page_text)
        for q in ("FULLHD", "HD", "SD"):
            if q in available and q in videos:
                return f"ANIMESUP - {q}", videos[q]
        return "ANIMESUP - SD", None

    @classmethod
    def search_animes(cls, mal_id, season=None, episode=None):
        is_movie = episode is None

        if not is_movie:
            try:
                episode = int(episode)
            except:
                return []

        r = session.get(f"https://api.jikan.moe/v4/anime/{mal_id}/full", timeout=10)
        if not r.ok:
            return []

        data = r.json().get('data', {})
        title_english = data.get('title_english')
        title_default = data.get('title')
        title_synonyms = data.get('title_synonyms') or []
        base_year = data.get('year')

        base_titles = [t for t in [title_english, title_default] + title_synonyms if t]
        search_title = title_english or title_default
        search_url = f"https://www.animesup.info/busca?busca={quote_plus(search_title)}"

        r = session.get(search_url, timeout=15)
        if not r.ok:
            return []

        soup = BeautifulSoup(r.text, "html.parser")
        anchors = soup.find_all("a", href=re.compile(r"/(animes|anime-dublado)/[^/]+$"))

        candidates = []
        for a in anchors:
            raw_title = a.get_text(strip=True)
            page_url = urljoin("https://www.animesup.info/", a["href"])
            cand_year = cls._extract_year(raw_title)
            score = cls._similarity_score(base_titles, raw_title, base_year, cand_year)
            candidates.append({
                "title": raw_title,
                "url": page_url,
                "score": score,
                "year": cand_year,
                "season": cls._extract_season_number(raw_title),
                "clean_title": cls._clean_title(raw_title)
            })

        candidates.sort(key=lambda x: x["score"], reverse=True)

        results = []
        seen = set()

        expected_season = None
        if not is_movie and base_titles:
            for t in base_titles:
                m = re.search(r'(?:season|part|temporada|s)\s*(\d+)', t.lower())
                if m:
                    expected_season = int(m.group(1))
                    break

        # Palavras-chave base do anime (normalizadas) para match parcial
        base_keywords = set()
        for t in base_titles:
            clean = cls._clean_title(t)
            words = clean.split()
            if len(words) > 1:
                base_keywords.update(words[:3])  # pega as primeiras palavras significativas (ex: boku no hero)

        for c in candidates:
            accept = False

            # 1. Ano bate (prioridade alta)
            if base_year and c["year"] and base_year == c["year"]:
                accept = True

            # 2. Temporada bate (número)
            elif not is_movie and expected_season and c["season"] and c["season"] == expected_season:
                accept = True

            # 3. Novo: título contém keywords base + número da temporada (ex: "boku no hero 6")
            elif not is_movie and expected_season and c["season"] == expected_season:
                clean_cand = c["clean_title"]
                if any(kw in clean_cand for kw in base_keywords) and str(expected_season) in clean_cand:
                    accept = True

            # 4. Fallback score
            if not accept:
                min_score = 0.75 if 'dublado' in c["title"].lower() else 0.55  # abaixado um pouco
                if c["score"] >= min_score:
                    accept = True

            if not accept:
                continue

            if c["url"] in seen:
                continue
            seen.add(c["url"])

            r_page = session.get(c["url"], timeout=15)
            if not r_page.ok:
                continue

            ep_url = (
                cls._get_movie_episode_url(r_page.text)
                if is_movie
                else cls._get_episode_page_url(c["url"], episode)
            )
            if not ep_url:
                continue

            r_ep = session.get(ep_url, timeout=15)
            if not r_ep.ok:
                continue

            available = cls._get_available_qualities(r_ep.text)
            label, url = cls._get_highest_quality_link(r_ep.text, available)
            if not url:
                continue

            prefix = "DUBLADO" if "dublado" in c["title"].lower() else "LEGENDADO"
            final_label = f"{label} ({prefix})"
            results.append((final_label, url))

        return results

    @classmethod
    def resolve_movies(cls, url):
        resolved, sub = Resolver().resolverurls(url)
        return [(resolved or url, sub or '', USER_AGENT)]

    resolve_tvshows = resolve_movies
    __site_url__ = ['https://www.animesup.info/']
