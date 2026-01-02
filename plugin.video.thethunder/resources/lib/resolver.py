# resolver.py
import resolveurl
import xbmc  

class Resolver:
    def resolverurls(self, url, referer=None):
        try:
            stream_url = resolveurl.resolve(url)
            if stream_url:
                return stream_url, None
            else:
                return None, None
        except Exception as e:
            xbmc.log(f"[resolver.py] Erro ao resolver URL: {str(e)}", xbmc.LOGERROR)
            return None, None
