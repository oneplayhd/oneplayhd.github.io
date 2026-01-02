# -*- coding: utf-8 -*-
import requests
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36'
PROXY = 'https://proxy.liyao.space/------'

class cfscraper:
    session = requests.Session()
    
    @classmethod
    def get(cls, url, headers={}, timeout=20, allow_redirects=True, cookies={}, direct=True):
        sess = cls.session
        # Use raw URL for proxy without encoding
        proxy_url = f"{PROXY}{url}"
        request_url = url if direct else proxy_url
        if not headers:
            headers = {
                'User-Agent': USER_AGENT,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://overflixtv.ltd/'
            }
        else:
            headers_ = {'User-Agent': USER_AGENT}
            headers.update(headers_)

        try:
            logger.debug(f"Attempting GET request to {request_url} (direct={direct})")
            res = sess.get(request_url, headers=headers, cookies=cookies, allow_redirects=allow_redirects, timeout=timeout)
            res.raise_for_status()
            # Check if response is relevant
            if "captcha" in res.text.lower():
                logger.error(f"Captcha detected in response for {request_url}")
                return None
            if "/pesquisar/" in url and "pesquisar" not in res.url:
                logger.error(f"Response URL {res.url} does not match expected search URL {url}")
                return None
            logger.debug(f"Successful GET request to {request_url}, response URL: {res.url}")
            return res
        except requests.exceptions.HTTPError as err:
            logger.error(f"HTTP error {err.response.status_code} for {request_url}: {err}")
            if err.response.status_code in [400, 403, 503]:
                if direct:
                    # Retry with proxy if direct request failed
                    logger.debug(f"Retrying GET request via proxy: {proxy_url}")
                    try:
                        res = sess.get(proxy_url, headers=headers, cookies=cookies, allow_redirects=allow_redirects, timeout=timeout)
                        res.raise_for_status()
                        if "captcha" in res.text.lower():
                            logger.error(f"Captcha detected in proxy response for {proxy_url}")
                            return None
                        if "/pesquisar/" in url and "pesquisar" not in res.url:
                            logger.error(f"Proxy response URL {res.url} does not match expected search URL {url}")
                            return None
                        logger.debug(f"Successful proxy GET request to {proxy_url}, response URL: {res.url}")
                        return res
                    except Exception as e:
                        logger.error(f"Proxy request failed for {proxy_url}: {e}")
                else:
                    # Retry direct request if proxy failed
                    logger.debug(f"Retrying GET request directly to {url}")
                    try:
                        res = sess.get(url, headers=headers, cookies=cookies, allow_redirects=allow_redirects, timeout=timeout)
                        res.raise_for_status()
                        if "captcha" in res.text.lower():
                            logger.error(f"Captcha detected in direct response for {url}")
                            return None
                        logger.debug(f"Successful direct GET request to {url}")
                        return res
                    except Exception as e:
                        logger.error(f"Direct retry failed for {url}: {e}")
            return None
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout error occurred for {request_url}: {e}")
            if not direct:
                logger.debug(f"Retrying GET request directly to {url}")
                try:
                    res = sess.get(url, headers=headers, cookies=cookies, allow_redirects=allow_redirects, timeout=timeout)
                    res.raise_for_status()
                    if "captcha" in res.text.lower():
                        logger.error(f"Captcha detected in direct response for {url}")
                        return None
                    logger.debug(f"Successful direct GET request to {url}")
                    return res
                except Exception as e:
                    logger.error(f"Direct request failed for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for {request_url}: {e}")
            if not direct:
                logger.debug(f"Retrying GET request directly to {url}")
                try:
                    res = sess.get(url, headers=headers, cookies=cookies, allow_redirects=allow_redirects, timeout=timeout)
                    res.raise_for_status()
                    if "captcha" in res.text.lower():
                        logger.error(f"Captcha detected in direct response for {url}")
                        return None
                    logger.debug(f"Successful direct GET request to {url}")
                    return res
                except Exception as e:
                    logger.error(f"Direct request failed for {url}: {e}")
            return None

    @classmethod
    def post(cls, url, headers={}, timeout=20, data=None, json=None, allow_redirects=True, cookies={}, direct=True):
        sess = cls.session
        proxy_url = f"{PROXY}{url}"
        request_url = url if direct else proxy_url
        if not headers:
            headers = {
                'User-Agent': USER_AGENT,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://overflixtv.ltd/'
            }
        else:
            headers_ = {'User-Agent': USER_AGENT}
            headers.update(headers_)
        try:
            logger.debug(f"Attempting POST request to {request_url} (direct={direct})")
            if data:
                res = sess.post(request_url, headers=headers, data=data, allow_redirects=allow_redirects, cookies=cookies, timeout=timeout)
            else:
                res = sess.post(request_url, headers=headers, json=json, allow_redirects=allow_redirects, cookies=cookies, timeout=timeout)
            res.raise_for_status()
            if "captcha" in res.text.lower():
                logger.error(f"Captcha detected in POST response for {request_url}")
                return None
            logger.debug(f"Successful POST request to {request_url}")
            return res
        except requests.exceptions.HTTPError as err:
            logger.error(f"HTTP error {err.response.status_code} for {request_url}: {err}")
            if err.response.status_code in [400, 403, 503]:
                if direct:
                    logger.debug(f"Retrying POST request via proxy: {proxy_url}")
                    try:
                        if data:
                            res = sess.post(proxy_url, headers=headers, data=data, allow_redirects=allow_redirects, cookies=cookies, timeout=timeout)
                        else:
                            res = sess.post(proxy_url, headers=headers, json=json, allow_redirects=allow_redirects, cookies=cookies, timeout=timeout)
                        res.raise_for_status()
                        if "captcha" in res.text.lower():
                            logger.error(f"Captcha detected in proxy POST response for {proxy_url}")
                            return None
                        logger.debug(f"Successful proxy POST request to {proxy_url}")
                        return res
                    except Exception as e:
                        logger.error(f"Proxy POST request failed for {proxy_url}: {e}")
                else:
                    logger.debug(f"Retrying POST request directly to {url}")
                    try:
                        if data:
                            res = sess.post(url, headers=headers, data=data, allow_redirects=allow_redirects, cookies=cookies, timeout=timeout)
                        else:
                            res = sess.post(url, headers=headers, json=json, allow_redirects=allow_redirects, cookies=cookies, timeout=timeout)
                        res.raise_for_status()
                        if "captcha" in res.text.lower():
                            logger.error(f"Captcha detected in direct POST response for {url}")
                            return None
                        logger.debug(f"Successful direct POST request to {url}")
                        return res
                    except Exception as e:
                        logger.error(f"Direct POST retry failed for {url}: {e}")
            return None
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout error occurred for {request_url}: {e}")
            if not direct:
                logger.debug(f"Retrying POST request directly to {url}")
                try:
                    if data:
                        res = sess.post(url, headers=headers, data=data, allow_redirects=allow_redirects, cookies=cookies, timeout=timeout)
                    else:
                        res = sess.post(url, headers=headers, json=json, allow_redirects=allow_redirects, cookies=cookies, timeout=timeout)
                    res.raise_for_status()
                    if "captcha" in res.text.lower():
                        logger.error(f"Captcha detected in direct POST response for {url}")
                        return None
                    logger.debug(f"Successful direct POST request to {url}")
                    return res
                except Exception as e:
                    logger.error(f"Direct request failed for {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for {request_url}: {e}")
            if not direct:
                logger.debug(f"Retrying POST request directly to {url}")
                try:
                    if data:
                        res = sess.post(url, headers=headers, data=data, allow_redirects=allow_redirects, cookies=cookies, timeout=timeout)
                    else:
                        res = sess.post(url, headers=headers, json=json, allow_redirects=allow_redirects, cookies=cookies, timeout=timeout)
                    res.raise_for_status()
                    if "captcha" in res.text.lower():
                        logger.error(f"Captcha detected in direct POST response for {url}")
                        return None
                    logger.debug(f"Successful direct POST request to {url}")
                    return res
                except Exception as e:
                    logger.error(f"Direct request failed for {url}: {e}")
            return None
