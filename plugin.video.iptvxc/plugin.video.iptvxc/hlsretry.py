# -*- coding: utf-8 -*-
import socket
import threading
import sys
PY3 = sys.version_info[0] == 3
if PY3:
    from urllib.parse import urlparse, parse_qs, quote, unquote, unquote_plus, quote_plus
else:
    from urlparse import urlparse, parse_qs
    from urllib import quote, unquote, unquote_plus, quote_plus, quote

# try:
#     from resources.modules.helper import monitor_acesso
# except:
#     def monitor_acesso():
#         return True
import re
import requests
import logging
import base64
import random
import binascii
from customdns import DNSOverride
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_local_ip():
    try:
        # Cria um socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.255.255.255', 1))
        local_ip = s.getsockname()[0]
    except Exception as e:
        local_ip = '127.0.0.1'
    finally:
        try:
            s.close()
        except:
            pass
    return local_ip

def log(msg):   
    logger.info(msg)    

#HOST_NAME = '127.0.0.1'
HOST_NAME = get_local_ip()
PORT_NUMBER = 57410

url_proxy = 'http://'+HOST_NAME+':'+str(PORT_NUMBER)+'/?url='

global MAX_RETRY
global URL_BASE
global LAST_URL
global HEADERS_BASE
global STOP_SERVER
global CACHE_CHUNKS
global CACHE_M3U8
global DELAY_MODE
global RESOLUTION
global LAST_M3U8
global PARAMS
global URL_BASE_PARAMS
global CHECK_URL_PARAMS
global URL_BASE_STALKER
global TOKEN_STALKER
MAX_RETRY = 28
DELAY_MODE = True
URL_BASE = ''
URL_BASE_PARAMS = ''
LAST_URL = ''
HEADERS_BASE = {}
STOP_SERVER = False
CACHE_CHUNKS = []
CACHE_M3U8 = ''
RESOLUTION = True
LAST_M3U8 = ''
PARAMS = ''
CHECK_URL_PARAMS = True
URL_BASE_STALKER = ''
TOKEN_STALKER = ''
NSPLAYER = False

def gerar_ip_brasileiro():
    ranges = [
        (167772160, 184549375),   # 10.0.0.0 – 10.255.255.255
        (1879048192, 1884162559), # 112.0.0.0 – 112.63.255.255
        (2896692480, 2896702975), # 172.16.0.0 – 172.31.255.255
        (3232235520, 3232301055)  # 192.168.0.0 – 192.168.255.255
    ]

    faixa = random.choice(ranges)
    ip_numerico = random.randint(faixa[0], faixa[1])

    ip = ".".join([str((ip_numerico >> (i * 8)) & 0xFF) for i in range(4)[::-1]])
    return ip


class XtreamCodes:
    def update_headers(self):
        global HEADERS_BASE
        global NSPLAYER
        header = HEADERS_BASE
        header.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'Connection': 'keep-alive'})
        if NSPLAYER == True:
            header['User-Agent']=binascii.b2a_hex(os.urandom(20))[:32]
        return header


    def basename(self,p):
        """Returns the final component of a pathname"""
        i = p.rfind('/') + 1
        return p[i:]
    
    def convert_to_m3u8(self,url):
        if '|' in url:
            url = url.split('|')[0]
        elif '%7C' in url:
            url = url.split('%7C')[0]
        if not '.m3u8' in url and not '/hl' in url and int(url.count("/")) > 4 and not '.mp4' in url and not '.avi' in url:
            parsed_url = urlparse(url)
            try:
                host_part1 = '%s://%s'%(parsed_url.scheme,parsed_url.netloc)
                host_part2 = url.split(host_part1)[1]
                url = host_part1 + '/live' + host_part2
                file = self.basename(url)
                if '.ts' in file:
                    file_new = file.replace('.ts', '.m3u8')
                    url = url.replace(file, file_new)
                else:
                    url = url + '.m3u8'
                    # file_new = file + '.m3u8'
                    # new_url = url.replace(file, file_new)
            except:
                pass
        return url 

    def set_headers(self,url):
        global URL_BASE
        global HEADERS_BASE        
        headers_default = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36', 'Accept-Encoding': 'gzip, deflate','Connection': 'keep-alive'}
        headers = {}
        if 'User-Agent' in url:
            try:
                user_agent = url.split('User-Agent=')[1]
                try:
                    user_agent = user_agent.split('&')[0]
                except:
                    pass
                try:
                    user_agent = unquote_plus(user_agent)
                except:
                    pass
                try:
                    user_agent = unquote(user_agent)
                except:
                    pass
                if 'Mozilla' in user_agent:
                    headers['User-Agent'] = user_agent
            except:
                pass
        if 'Referer' in url:
            try:
                referer = url.split('Referer=')[1]
                try:
                    referer = referer.split('&')[0]
                except:
                    pass
                try:
                    referer = unquote_plus(referer)
                except:
                    pass
                try:
                    referer = unquote(referer)
                except:
                    pass                
                headers['Referer'] = referer
            except:
                pass
        if 'Origin' in url:
            try:
                origin = url.split('Origin=')[1]
                try:
                    origin = origin.split('&')[0]
                except:
                    pass
                try:
                    origin = unquote_plus(origin)
                except:
                    pass
                try:
                    origin = unquote(origin)
                except:
                    pass                
                headers['Origin'] = origin
            except:
                pass
        #HEADERS_ = headers if headers else headers_default
        if headers != {}:
            headers.update({'Connection': 'keep-alive'})
            HEADERS_ = headers
        else:
            HEADERS_ = headers_default
        if HEADERS_BASE == {}:
            HEADERS_BASE = HEADERS_

    def base_url(self,url):
        global HEADERS_BASE
        global PARAMS
        header_ = self.update_headers()
        try:
            if not PARAMS:
                for i in range(7):
                    DNSOverride()                    
                    r = requests.get(url,headers=header_, timeout=3, verify=False)
                    if r.status_code == 200:
                        url = r.url
                    else:
                        break
        except:
            pass
        filename = url.split('/')[-1]
        if not '.m3u8' in filename:
            url = url.split('?')[0]
            filename = url.split('/')[-1]
            url = url.split(filename)[0]
        else:
            url = url.replace(filename, '')
        return url

    def base_url_params(self,url):
        global HEADERS_BASE
        header_ = self.update_headers()
        try:
            for i in range(7): 
                DNSOverride()                
                r = requests.get(url,headers=header_, timeout=3, verify=False)
                if r.status_code == 200:
                    url = r.url
                    break
        except:
            pass
        filename = url.split('/')[-1]
        if not '.m3u8' in filename:
            url = url.split('?')[0]
            filename = url.split('/')[-1]
            url = url.split(filename)[0]
        else:
            url = url.replace(filename, '')
        return url

    def get_filename_params(self,url):
        if '.m3u8' in url:
            try:
                filename = url.split('.m3u8')[0].split('/')[-1] + '.m3u8'
                url = filename + url.split(filename)[1]
            except:
                pass
        return url

    def check_url_params(self,url):
        global URL_BASE_PARAMS
        global HEADERS_BASE
        global CHECK_URL_PARAMS
        baseurl = url
        if URL_BASE_PARAMS:
            url = URL_BASE_PARAMS + self.get_filename_params(url)
            if '.m3u8' in url and CHECK_URL_PARAMS:
                try:
                    DNSOverride()                      
                    r = requests.get(url,headers=HEADERS_BASE,timeout=3,verify=False)
                    if r.status_code == 200:
                        CHECK_URL_PARAMS = False
                        return url
                except:
                    pass
        return baseurl

    def make_m3u8(self,m3u):
        padrao = r'#EXTINF:\d+\.\d+,\n/hl.+?/[^/]+\d+\.ts\?[^#]+'
        padrao2 = r'#EXTINF:\d+\.\d+,\n/hl.+?/[^/]+\d+\.ts'
        resultados = re.findall(padrao, m3u)
        if not resultados:
            resultados = re.findall(padrao2, m3u)
        if resultados:
            base_m3u = m3u.split('#EXTINF')[0]
            duas_ultimas_linhas = resultados[-1:]
            for linha in duas_ultimas_linhas:
                base_m3u += linha
            m3u = base_m3u
        return m3u

    def magical_hls(self,url):
        global DELAY_MODE
        if '/hl' in url and not 'https' in url:
            segment = re.findall('ls/(.*?).ts', url)
            segment2 = re.findall('/(.*?).ts',url)
            if segment and DELAY_MODE:
                try:
                    s = segment[0]
                    file, part = s.split('_')
                    part = int(part) - 1
                    new_s = file + '_' + str(part)
                    url = url.replace(s, new_s)
                except:
                    pass
            elif segment2 and DELAY_MODE:
                try:
                    s = segment2[0]
                    file, part = s.split('_')
                    part = int(part) - 1
                    new_s = file + '_' + str(part)
                    url = url.replace(s, new_s)
                except:
                    pass            
                
        return url

    def get_max_m3u8(self,src):
        global URL_BASE
        try:
            regex1 = r"RESOLUTION=(\d+x\d+).*\n(.+\.m3u8.+)"
            regex2 = r"RESOLUTION=(\d+x\d+).*\n(.+\.m3u8)"
            matches = re.findall(regex1, src)
            if not matches:
                matches = re.findall(regex2, src)
            max_resolution_url = max(matches, key=lambda x: tuple(map(int, x[0].split('x'))))
            url = URL_BASE + max_resolution_url[1]
        except:
            url = ''
        return url

    # funcao m3u8 principal
    def send_m3u8(self,self_server,url):
        global MAX_RETRY
        global URL_BASE
        global LAST_URL
        global HEADERS_BASE
        global STOP_SERVER
        global CACHE_CHUNKS
        global CACHE_M3U8
        global DELAY_MODE
        global RESOLUTION
        global LAST_M3U8
        global PARAMS
        global URL_BASE_PARAMS
        global CHECK_URL_PARAMS
        global NSPLAYER
        try:
            url = url.split('|')[0]
        except:
            pass
        try:
            url = url.split('%7C')[0]
        except:
            pass
        if '.m3u8' in url or '.php' in url:
            self_server.send_header('Content-Type', 'application/x-mpegURL')
            self_server.end_headers() 
            URL_PLAY = url            
            if not URL_BASE:
                URL_BASE = self.base_url(url)
                LAST_URL = url
            elif URL_BASE:
                if 'http' in url:
                    last_parse = urlparse(LAST_URL)
                    last_host = '%s://%s'%(last_parse.scheme,last_parse.netloc)
                    url_parse = urlparse(url)
                    url_host = '%s://%s'%(url_parse.scheme,url_parse.netloc)
                    if last_host != url_host:
                        URL_BASE = self.base_url(url)
            if not 'http' in url:
                if url.startswith('/'):
                    url = url[1:]
                log('URL DO NO HTTP: %s'%url)
                # verificar param             
                #url = URL_BASE + url
            if PARAMS and not '?' in url:
                url = url + PARAMS
                log('URL DO PARAMS: %s'%url)
            if not URL_BASE_PARAMS and '?' in url:
                URL_BASE_PARAMS = self.base_url_params(url)
            if URL_BASE_PARAMS:
                url = self.check_url_params(url)
                log('URL DO BASE PARAMS: %s'%url)
            for i in range(MAX_RETRY):
                count = i + 1
                if STOP_SERVER:
                    break
                DNSOverride()
                # if count == MAX_RETRY - 4:
                #     notify('Canal ruim, tente outro canal ou lista')
                log('URL POS PROCESSAMENTO: %s'%url)
                header_ = self.update_headers()                 
                if RESOLUTION:                  
                    try:                          
                        r = requests.get(url,headers=header_, allow_redirects=True, timeout=2, verify=False)
                        code = r.status_code
                        log('Status Code: %s'%str(code))
                        if code == 200:
                            src = r.text
                            if '.m3u8' in src and 'RESOLUTION' in src:
                                url = self.get_max_m3u8(src)
                                log('URL DO GET MAX M3U8: %s'%url)
                                LAST_M3U8 = url
                    except:
                        pass
                    RESOLUTION = False
                if LAST_M3U8:
                    url = LAST_M3U8
                    log('URL DO LAST M3U8: %s'%url)
                if PARAMS and not '?' in url:
                    url = url + PARAMS
                    log('URL DO PARAMS: %s'%url)
                try:
                    log('URL FINAL DO M3U: %s'%url)                      
                    r = requests.get(url,headers=header_, allow_redirects=True, timeout=4, verify=False)
                    code = r.status_code
                    log('TESTE DO JOEL')
                    log('HEADERS: %s'%str(header_))
                    log('URL M3U8: %s'%str(url))
                    log('Status Code: %s'%str(code))
                    
                    if code == 200:
                        NSPLAYER = False
                        src = r.text
                        if 'http' in src:
                            url_proxy = 'http://%s:%s/?url=http'%(HOST_NAME,PORT_NUMBER)
                            src = src.replace('http',url_proxy)
                        if '/live/' in url and url.count('/') == 6:
                            try:
                                CACHE_M3U8 = self.make_m3u8(src)
                            except:
                                pass
                        src = src.encode('utf-8') #if six.PY3 else src
                        self_server.conn.sendall(src)
                        break
                    else:
                        NSPLAYER = True
                        if '/live/' in url and url.count('/') == 6 and CACHE_M3U8:
                            src = CACHE_M3U8
                            src = src.encode('utf-8') #if six.PY3 else src
                            self_server.conn.sendall(src)
                            break
                except:
                    pass

    def send_ts(self,self_server,url):
        global MAX_RETRY
        global URL_BASE
        global LAST_URL
        global HEADERS_BASE
        global STOP_SERVER
        global CACHE_CHUNKS
        global CACHE_M3U8
        global DELAY_MODE
        global RESOLUTION
        global LAST_M3U8
        global PARAMS
        global URL_BASE_PARAMS
        global CHECK_URL_PARAMS
        if '.ts' in url or '/hl' in url and not '.ts' in url:
            self_server.send_header('Content-type','video/mp2t')
            self_server.end_headers()            
            if url.startswith('/') and not '/hl' in url:
                url = url[1:]
                ts = URL_BASE + url
            elif url.startswith('/'):
                url = url[1:]
                if 'https' in URL_BASE:
                    ts = 'https://' + URL_BASE.split('/')[2] + '/' + url
                else:
                    ts = 'http://' + URL_BASE.split('/')[2] + '/' + url
            for i in range(MAX_RETRY):
                count = i + 1
                if STOP_SERVER:
                    break
                DNSOverride()            
                # if count == MAX_RETRY - 4:
                #     notify('Canal ruim, tente outro canal ou lista')
                try:
                    header_ = self.update_headers()                     
                    r = requests.get(ts, headers=header_, allow_redirects=True, stream=True, verify=False)
                    code = r.status_code
                    log('Status Code: %s'%str(code))
                    if code == 200:
                        CACHE_CHUNKS = []
                        for chunk in r.iter_content(50*1024):                      
                            try:
                                self_server.conn.sendall(chunk)
                                CACHE_CHUNKS.append(chunk)
                            except:
                                pass
                        break
                    else:
                        if i == 0:
                            DELAY_MODE = False
                        if CACHE_CHUNKS:
                            try:
                                #self.wfile.write(CACHE_CHUNKS[-1])
                                self_server.conn.sendall(CACHE_CHUNKS[-1])
                            except:
                                pass

                except:
                    pass

    def parse_url(self,url):
        parsed_url = urlparse(url)
        scheme = parsed_url.scheme
        host = parsed_url.hostname
        port = parsed_url.port
    
        return scheme, host, port    

    def send_m3u8_stalker(self,self_server,url):
        global URL_BASE_STALKER
        global TOKEN_STALKER
        global NSPLAYER
        DNSOverride()
        if 'm3u8' in url:
            self_server.send_header('Content-Type', 'application/x-mpegURL')
            self_server.end_headers()                       
            if not URL_BASE_STALKER:
                header_ = self.update_headers()
                try:                   
                    r = requests.get(url,headers=header_, allow_redirects=True, timeout=4, verify=False)
                    url = r.url
                except:
                    pass
                scheme, host, port = self.parse_url(url)
                if port:
                    URL_BASE_STALKER = scheme + '://' + host + ':' + str(port)
                else:
                    URL_BASE_STALKER = scheme + '://' + host
        if not TOKEN_STALKER:
            if '?' in url:
                try:
                    TOKEN_STALKER = url.split('?')[1]
                except:
                    pass
        if 'm3u8' in url:
            for i in range(MAX_RETRY):
                count = i + 1
                if STOP_SERVER:
                    break
                if count == MAX_RETRY - 4:
                    notify('Canal ruim, tente outro canal ou lista')
                try:
                    header_ = self.update_headers()
                    r = requests.get(url,headers=header_, allow_redirects=True, timeout=4, verify=False)
                    code = r.status_code
                    log('Status Code: %s'%str(code))
                    if code == 200:
                        NSPLAYER = False
                        src = r.text
                        try:
                            CACHE_M3U8 = self.make_m3u8(src)
                        except:
                            pass
                        src = src.encode('utf-8') #if six.PY3 else src
                        self_server.conn.sendall(src)
                        break
                    else:
                        NSPLAYER = True
                        if CACHE_M3U8:
                            src = CACHE_M3U8
                            #src = response_headers + src
                            src = src.encode('utf-8') #if six.PY3 else src
                            self_server.conn.sendall(src)
                            break
                        
                except:
                    pass
                    
    
    def send_ts_stalker(self,self_server,url): 
        global MAX_RETRY
        global URL_BASE
        global LAST_URL
        global HEADERS_BASE
        global STOP_SERVER
        global CACHE_CHUNKS
        global CACHE_M3U8
        global DELAY_MODE
        global RESOLUTION
        global LAST_M3U8
        global PARAMS
        global URL_BASE_PARAMS
        global CHECK_URL_PARAMS 
        global URL_BASE_STALKER
        global TOKEN_STALKER
        if '.ts' in url and URL_BASE_STALKER:
            DNSOverride()
            # if TOKEN_STALKER:
            #     ts = URL_BASE_STALKER + url + '?' + TOKEN_STALKER
            self_server.send_header('Content-Type', 'video/mp2t')
            self_server.end_headers()            
            ts = URL_BASE_STALKER + url
            for i in range(MAX_RETRY):
                count = i + 1
                if STOP_SERVER:
                    break        
                try:
                    header_ = self.update_headers()                     
                    r = requests.get(ts,headers=header_, allow_redirects=True, stream=True, verify=False)
                    code = r.status_code
                    log('Status Code: %s'%str(code))
                    if code == 200:
                        CACHE_CHUNKS = []
                        for chunk in r.iter_content(50*1024):                      
                            try:
                                self_server.conn.sendall(chunk)
                                CACHE_CHUNKS.append(chunk)
                            except:
                                pass
                        break
                    else:
                        if i == 0:
                            DELAY_MODE = False
                        if CACHE_CHUNKS:
                            try:
                                #self.wfile.write(CACHE_CHUNKS[-1])
                                self_server.conn.sendall(CACHE_CHUNKS[-1])
                            except:
                                pass

                except:
                    pass         









class ProxyHandler(XtreamCodes):
    def __init__(self, conn, addr, server):
        self.conn = conn
        self.addr = addr
        self.server = server
        self.path = ""
        self.request_method = ""

    def parse_request(self, request):
        parts = request.split(b' ')
        self.request_method = parts[0].decode()

    def parse_request2(self, request):
        parts = request.split(b' ')
        if len(parts) >= 2:
            self.path = parts[1].decode()

    def send_response(self, code, message=None):
        response = "HTTP/1.1 {} {}\r\n".format(code, message if message else "")
        self.conn.sendall(response.encode())

    def send_header(self, keyword, value):
        header = "{}: {}\r\n".format(keyword, value)
        self.conn.sendall(header.encode())

    def end_headers(self):
        self.conn.sendall(b"\r\n")

    def extract_header(self, request_data, header_name):
        header_lines = request_data.split(b'\r\n')
        for line in header_lines:
            if header_name in line:
                return line
        return None        

    def get_range(self, request_data, content_length):
        range_header = self.extract_header(request_data, b'Range:')
        if range_header:
            parts = range_header.split(b"-")
            start = int(parts[0].split(b'=')[-1])
            end = int(parts[1]) if parts[1] else content_length - 1
            return start, end
        else:
            return 0, content_length - 1       

    def stream_video(self, video_url, request_data):
        try:
            video_url = video_url.split('|')[0]
        except:
            pass
        try:
            video_url = video_url.split('%7C')[0]
        except:
            pass
        global HEADERS_BASE
        headers = HEADERS_BASE
        try:
            response = requests.head(video_url, headers=headers)
            if response.status_code == 200:
                content_length = int(response.headers.get('Content-Length', 0))
                start, end = self.get_range(request_data, content_length)
                #headers['Range'] = f'bytes={start}-{end}'  # Adicionando cabeçalho de intervalo
                headers['Range'] = 'bytes=%s-%s'%(str(start),str(end))  # Adicionando cabeçalho de intervalo
                response = requests.get(video_url, headers=headers, stream=True)
                if response.status_code == 206 or response.status_code == 200:
                    self.send_partial_response(206, response.headers, content_length, response.iter_content(chunk_size=1024), start, end)
                else:
                    self.send_response(404)
            else:
                self.send_response(404)
        except Exception as e:
            #print("Error streaming video:", e)
            self.send_response(500)

    def send_partial_response(self, status_code, headers, content_length, content_generator, start, end):
        self.send_response(status_code)
        #self.send_header('Content-type','video/mp4')
        self.send_header("Accept-Ranges", "bytes")
        if start is not None:
            #self.send_header("Content-Range", f"bytes {start}-{end}/{content_length}")
            self.send_header("Content-Range", "bytes %s-%s/%s"%(str(start),str(end),str(content_length)))
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()

        for chunk in content_generator:
            if STOP_SERVER:
                break
            try:
                self.conn.sendall(chunk)
            except:
                pass
                        

    def handle_request(self):
        global URL_BASE
        global LAST_URL
        global HEADERS_BASE
        global STOP_SERVER
        global CACHE_CHUNKS
        global CACHE_M3U8
        global DELAY_MODE
        global RESOLUTION
        global LAST_M3U8
        global PARAMS
        global URL_BASE_PARAMS 
        global CHECK_URL_PARAMS
        global URL_BASE_STALKER
        global TOKEN_STALKER       
        request_data = self.conn.recv(1024)
        self.parse_request(request_data)
        self.parse_request2(request_data)
        if self.request_method == 'HEAD':
            self.send_response(200) # envia status 200 sempre
            pass
        elif self.path == "/stop":
            self.send_response(200) # envia status 200 sempre
            STOP_SERVER = True
            URL_BASE = ''
            LAST_URL = ''
            HEADERS_BASE = {}
            CACHE_CHUNKS = []
            CACHE_M3U8 = ''
            DELAY_MODE = True
            LAST_M3U8 = ''            
            RESOLUTION = True
            PARAMS = ''
            CHECK_URL_PARAMS = True
            URL_BASE_STALKER = ''
            TOKEN_STALKER = ''           
            self.server.stop_server()
        elif self.path == "/reset":
            self.send_response(200) # envia status 200 sempre
            URL_BASE = ''
            LAST_URL = ''
            HEADERS_BASE = {}
            CACHE_CHUNKS = []
            CACHE_M3U8 = ''
            DELAY_MODE = True
            RESOLUTION = True
            LAST_M3U8 = ''
            PARAMS = ''
            URL_BASE_PARAMS = ''
            CHECK_URL_PARAMS = True
            URL_BASE_STALKER = ''
            TOKEN_STALKER = ''
        elif self.path == '/check':
            self.send_response(200) # envia status 200 sempre
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.conn.sendall(b"Hello, world!")
        else:
            url_path = unquote_plus(self.path)
            self.set_headers(url_path)
            url_parts = urlparse(url_path)
            query_params = parse_qs(url_parts.query)
            if 'url' in query_params:
                url = url_path.split('url=')[1]
                # try:
                #     url = base64.b64decode(url).decode('utf-8')
                # except:
                #     pass
                try:
                    url = url.split('|')[0]
                except:
                    pass
                try:
                    url = url.split('%7C')[0]
                except:
                    pass
                url = self.convert_to_m3u8(url)
            else:
                url = url_path
            if '.m3u8' in url and '?' in url and not 'extension' in url:
                if not PARAMS:
                    try:
                        PARAMS = '?' + url.split('?')[1]
                    except:
                        pass
            # STALKER
            if '/hl' in url and '.ts' in url:
                self.send_response(200) # envia status 200 sempre
                self.send_ts(self,url)            
            elif '/hl' in url and not '.ts' in url:
                self.send_response(200) # envia status 200 sempre
                self.send_ts(self,url)            
            elif 'm3u8' in url and not 'extension' in url and '/play/' in url and not '.m3u8' in url:
                self.send_response(200) # envia status 200 sempre
                self.send_m3u8_stalker(self,url)               
            elif 'm3u8' in url and 'extension' in url:
                self.send_response(200) # envia status 200 sempre
                #self.send_m3u8_stalker(self,url)
            elif '.ts' in url and URL_BASE_STALKER or 'hls' in url and URL_BASE_STALKER:
                self.send_response(200) # envia status 200 sempre
                self.send_ts_stalker(self,url)
            # XTREAM CODES
            elif '.mp4' in url and not '.m3u8' in url and not '.ts' in url:
                self.stream_video(url, request_data)                    
            elif '.m3u8' in url:
                self.send_response(200) # envia status 200 sempre
                self.send_m3u8(self,url)
            elif '.ts' in url:
                self.send_response(200) # envia status 200 sempre
                self.send_ts(self,url)
                                                


        self.conn.close()  # Fechar o socket de conexão após enviar a resposta

def monitor():
    try:
        try:
            from kodi_six import xbmc
        except:
            import xbmc
        monitor = xbmc.Monitor()
        while not monitor.waitForAbort(3):
            pass
        log('Ecerrando proxy server')
        url = 'http://'+HOST_NAME+':'+str(PORT_NUMBER)+'/stop'
        try:
            r = requests.get(url,timeout=4)
        except:
            pass
        log('Proxy encerrado')
        try:
            os._exit(1)
        except:
            pass
    except:
        pass

class Server:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((HOST_NAME, PORT_NUMBER))
        self.server_socket.listen(10)

    def serve_forever(self):
        global STOP_SERVER
        while True:
            if STOP_SERVER:
                break
            conn, addr = self.server_socket.accept()
            handler = ProxyHandler(conn, addr, self)
            threading.Thread(target=handler.handle_request).start()

    def stop_server(self):
        self.server_socket.close()

def loop_server():
    server = Server()
    server.serve_forever()

class XtreamProxy:
    def reset(self):
        try:
            url = 'http://'+HOST_NAME+':'+str(PORT_NUMBER)+'/reset'
            r = requests.get(url,timeout=3)
        except:
            pass

    def check_service(self):
        try:
            url = 'http://'+HOST_NAME+':'+str(PORT_NUMBER)+'/check'
            r = requests.head(url,timeout=3)
            if r.status_code == 200:
                return True
            return False
        except:
            return False

    def start(self):
        log('Iniciando Xtream Proxy - HLSRETRY')
        status = self.check_service()
        if status == False:
            proxy_service = threading.Thread(target=loop_server).start()
            monitor_service = threading.Thread(target=monitor).start()
        else:
            self.reset()


