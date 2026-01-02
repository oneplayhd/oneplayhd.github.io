# -*- coding: utf-8 -*-
import requests
import logging
import os


logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0'
PROXY = 'https://proxy.liyao.space/------'

class cfscraper:
    session = requests.Session()
    
    @classmethod
    def get(cls, url, headers={}, timeout=None, allow_redirects=True, cookies={},direct=True):
        sess = cls.session
        proxy_url = PROXY + url
        if not direct:
            url = proxy_url
        if not headers:
            headers = {'User-Agent': USER_AGENT}
        else:
            headers_ = {'User-Agent': USER_AGENT}
            headers.update(headers_)

        try:
            res = sess.get(url, headers=headers, cookies=cookies, allow_redirects=allow_redirects, timeout=timeout)
            res.raise_for_status()            
            return res
        except requests.exceptions.HTTPError as err:
            if err.response.status_code in [403, 503]:                
                try:
                    res = sess.get(proxy_url, headers=headers, cookies=cookies, allow_redirects=allow_redirects, timeout=timeout)
                    res.raise_for_status()            
                    return res
                except requests.exceptions.HTTPError as err:
                    if err.response.status_code == 403:
                        logger.error("Erro 403: Access denied")
                        try:
                            res = sess.get(url, headers=headers, cookies=cookies, allow_redirects=allow_redirects, timeout=timeout)
                            return res
                        except:
                            res = sess.get(proxy_url, headers=headers, cookies=cookies, allow_redirects=allow_redirects, timeout=timeout)
                            return res
                    elif err.response.status_code == 503:
                        logger.error("Erro 503: Service unavailable.")
                    else:
                        logger.error("HTTP error occurred: {0}".format(err))
            else:
                logger.error("HTTP error occurred: {0}".format(err))
        except Exception as e:
            try:
                res = sess.get(proxy_url, headers=headers, cookies=cookies, allow_redirects=allow_redirects, timeout=timeout)
                res.raise_for_status()            
                return res  # Retorna a resposta aqui também
            except requests.exceptions.HTTPError as err:
                if err.response.status_code == 403:
                    logger.error("Erro 403: Access denied")
                elif err.response.status_code == 503:
                    logger.error("Erro 503: Service unavailable.")             
                else:
                    logger.error("HTTP error occurred: {0}".format(err))
            except Exception as e:
                logger.error("HTTP error occurred: {0}".format(e)) 
                       
        return None

    @classmethod
    def post(cls, url, headers={}, timeout=None, data=None, json=None, allow_redirects=True, cookies={}, direct=True):
        sess = cls.session
        proxy_url = PROXY + url
        if not direct:
            url = proxy_url        
        if not headers:
            headers = {'User-Agent': USER_AGENT}
        else:
            headers_ = {'User-Agent': USER_AGENT}
            headers.update(headers_)
        try:
            if data:
                res = sess.post(url,headers=headers, data=data, allow_redirects=allow_redirects, cookies=cookies, timeout=timeout)
            else:
                res = sess.post(url,headers=headers, json=json, allow_redirects=allow_redirects, cookies=cookies, timeout=timeout)
            res.raise_for_status()
            return res
        except requests.exceptions.HTTPError as err:
            if err.response.status_code in [403, 503]:
                try:
                    if data:
                        res = sess.post(proxy_url, headers=headers, data=data, allow_redirects=allow_redirects, cookies=cookies, timeout=timeout)
                    else:
                        res = sess.post(proxy_url, headers=headers, json=json, allow_redirects=allow_redirects, cookies=cookies, timeout=timeout)
                    res.raise_for_status()            
                    return res
                except requests.exceptions.HTTPError as err:
                    if err.response.status_code == 403:
                        logger.error("Erro 403: Access denied")
                    elif err.response.status_code == 503:
                        logger.error("Erro 503: Service unavailable.")
                    else:
                        logger.error("HTTP error occurred: {0}".format(err))
            else:
                logger.error("HTTP error occurred: {0}".format(err))
        except Exception as e:
            try:
                if data:
                    res = sess.post(proxy_url, headers=headers, data=data, allow_redirects=allow_redirects, cookies=cookies, timeout=timeout)
                else:
                    res = sess.post(proxy_url, headers=headers, json=json, allow_redirects=allow_redirects, cookies=cookies, timeout=timeout)
                res.raise_for_status()            
                return res
            except requests.exceptions.HTTPError as err:
                if err.response.status_code == 403:
                    logger.error("Erro 403: Access denied")
                elif err.response.status_code == 503:
                    logger.error("Erro 503: Service unavailable.")
                else:
                    logger.error("HTTP error occurred: {0}".format(err))
            except Exception as e:
                logger.error("HTTP error occurred: {0}".format(e))
        return None 
                                
