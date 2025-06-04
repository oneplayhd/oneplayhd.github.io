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
import os
import re
import requests
import logging
import base64
from customdns import DNSOverride
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_local_ip():
    try:
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
    try: 
        logger.info(msg)    
    except:
        pass

HOST_NAME = get_local_ip()
PORT_NUMBER = 57461

url_proxy = 'http://'+HOST_NAME+':'+str(PORT_NUMBER)+'/?url='

global HEADERS_BASE
global STOP_SERVER
HEADERS_BASE = {}
STOP_SERVER = False

class XtreamCodes:
    def set_headers(self, url):
        global HEADERS_BASE        
        headers_default = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0', 'Connection': 'keep-alive'}
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
        if headers != {}:
            headers.update({'Connection': 'keep-alive'})
            HEADERS_ = headers
        else:
            HEADERS_ = headers_default
        if HEADERS_BASE == {}:
            HEADERS_BASE = HEADERS_

    def parse_url(self, url):
        parsed_url = urlparse(url)
        scheme = parsed_url.scheme
        host = parsed_url.hostname
        port = parsed_url.port
        return scheme, host, port    

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
            try:
                range_str = range_header.decode().split('=')[-1]
                start, end = range_str.split('-')
                start = int(start) if start else 0
                end = int(end) if end else (content_length - 1 if content_length > 0 else float('inf'))
                return start, end
            except (ValueError, IndexError) as e:
                log(f"Erro ao processar Range: {e}")
                return 0, float('inf')
        return 0, float('inf')

    # def stream_video(self, video_url, request_data):
    #     try:
    #         try:
    #             video_url = video_url.split('|')[0]
    #         except:
    #             pass
    #         try:
    #             video_url = video_url.split('%7C')[0]
    #         except:
    #             pass
    #         DNSOverride()
    #         global HEADERS_BASE

    #         headers = HEADERS_BASE.copy()
    #         headers['Accept'] = 'video/mp4,*/*'
    #         headers['Accept-Ranges'] = 'bytes'

    #         content_length = 0
    #         start, end = self.get_range(request_data, content_length)

    #         if start > 0 or end < float('inf'):
    #             headers['Range'] = f'bytes={start}-{end if end != float("inf") else ""}'
    #         else:
    #             headers['Range'] = 'bytes=0-'
    #         log(headers)

    #         with requests.get(video_url, headers=headers, stream=True) as response:
    #             if response.status_code not in [200, 206, 301, 302]:
    #                 self.send_response(404)
    #                 return

    #             content_length = int(response.headers.get('Content-Length', 0))
    #             if content_length == 0 and response.status_code == 206:
    #                 content_range = response.headers.get('Content-Range', '')
    #                 if content_range:
    #                     try:
    #                         content_length = int(content_range.split('/')[-1])
    #                     except (ValueError, IndexError):
    #                         content_length = 0

    #             if response.status_code == 206:
    #                 if not end or end == float('inf'):
    #                     end = content_length - 1 if content_length > 0 else start + 1024 * 1024 - 1
    #                 self.send_partial_response(
    #                     status_code=206,
    #                     headers=response.headers,
    #                     content_length=end - start + 1,
    #                     content_generator=response.iter_content(chunk_size=8192),
    #                     start=start,
    #                     end=end,
    #                     total_length=content_length
    #                 )
    #             else:
    #                 self.send_partial_response(
    #                     status_code=200,
    #                     headers=response.headers,
    #                     content_length=content_length,
    #                     content_generator=response.iter_content(chunk_size=8192),
    #                     start=0,
    #                     end=content_length - 1,
    #                     total_length=content_length
    #                 )

    #     except requests.exceptions.RequestException as e:
    #         log(f"Erro ao acessar o vídeo: {e}")
    #         self.send_response(502)
    #     except Exception as e:
    #         log(f"Erro no stream_video: {e}")
    #         self.send_response(500)

    def stream_video(self, video_url, request_data):
        try:
            # Configuração rápida dos headers
            headers = HEADERS_BASE.copy()
            headers.update({
                'Accept': 'video/mp4,*/*',
                'Accept-Ranges': 'bytes',
                'Connection': 'keep-alive'
            })

            # Obtém o range solicitado ANTES da requisição
            content_length = 0
            start, end = self.get_range(request_data, content_length)
            
            # Se for um range request, adiciona o header correspondente
            if start > 0 or end < float('inf'):
                headers['Range'] = f'bytes={start}-{end if end != float("inf") else ""}'
            # trocar dns
            DNSOverride()
            # Faz a requisição com timeout
            with requests.get(video_url, headers=headers, stream=True, timeout=(3, 10)) as response:
                # Verifica se é uma resposta válida
                if response.status_code not in [200, 206]:
                    self.send_response(response.status_code)
                    return

                # Determina o tamanho real do conteúdo
                if 'Content-Range' in response.headers:
                    content_length = int(response.headers['Content-Range'].split('/')[-1])
                else:
                    content_length = int(response.headers.get('Content-Length', 0))

                # Envia os headers IMEDIATAMENTE
                self.send_response(response.status_code)
                self.send_header('Content-Type', response.headers.get('Content-Type', 'video/mp4'))
                
                if response.status_code == 206:
                    content_range = response.headers['Content-Range']
                    self.send_header('Content-Range', content_range)
                    self.send_header('Content-Length', str(int(content_range.split('-')[-1].split('/')[0]) - start + 1))
                else:
                    self.send_header('Content-Length', str(content_length))
                
                self.send_header('Accept-Ranges', 'bytes')
                self.end_headers()

                # Stream eficiente com tratamento de erro
                try:
                    for chunk in response.iter_content(chunk_size=16*1024):  # 16KB chunks
                        if STOP_SERVER:
                            break
                        try:
                            self.conn.sendall(chunk)
                        except (ConnectionResetError, BrokenPipeError):
                            log("Cliente fechou a conexão durante o streaming")
                            break
                except requests.exceptions.ChunkedEncodingError as e:
                    log(f"Erro no streaming: {e}")

        except requests.exceptions.RequestException as e:
            log(f"Erro na requisição: {e}")
            self.send_response(502)
        except Exception as e:
            log(f"Erro geral: {e}")
            self.send_response(500)    

    # def send_partial_response(self, status_code, headers, content_length, content_generator, start, end, total_length):
    #     try:
    #         self.send_response(status_code)
    #         self.send_header('Server', 'nginx/1.24.0')
    #         self.send_header('Content-Type', headers.get('Content-Type', 'video/mp4'))
    #         self.send_header('Content-Length', str(content_length))
    #         self.send_header('Accept-Ranges', 'bytes')
            
    #         if status_code == 206:
    #             self.send_header('Content-Range', f'bytes {start}-{end}/{total_length if total_length > 0 else "*"}')
            
    #         for key in ['Cache-Control', 'ETag', 'Last-Modified']:
    #             if key in headers:
    #                 self.send_header(key, headers[key])
                    
    #         self.end_headers()

    #         for chunk in content_generator:
    #             if STOP_SERVER:
    #                 break
    #             try:
    #                 # Verifica se a conexão ainda está ativa antes de enviar
    #                 self.conn.settimeout(5)  # Timeout de 5 segundos
    #                 self.conn.sendall(chunk)
    #             except socket.timeout:
    #                 log("Timeout ao enviar dados - conexão pode ter sido perdida")
    #                 break
    #             except ConnectionResetError:
    #                 log("Conexão resetada pelo cliente")
    #                 break
    #             except BrokenPipeError:
    #                 log("Pipe quebrado - cliente fechou a conexão")
    #                 break
    #             except Exception as e:
    #                 log(f"Erro ao enviar chunk: {e}")
    #                 break
    #     except Exception as e:
    #         log(f"Erro ao enviar resposta parcial: {e}")
    #     finally:
    #         try:
    #             self.conn.close()
    #         except:
    #             pass

    def handle_request(self):
        global HEADERS_BASE
        global STOP_SERVER    
        request_data = self.conn.recv(1024)
        self.parse_request(request_data)
        self.parse_request2(request_data)
        if self.request_method == 'HEAD':
            self.send_response(200)
            pass
        elif self.path == "/stop":
            self.send_response(200)
            STOP_SERVER = True
            HEADERS_BASE = {}          
            self.server.stop_server()
        elif self.path == "/reset":
            self.send_response(200)
            HEADERS_BASE = {}
        elif self.path == '/check':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.conn.sendall(b"Hello, world!")
        else:
            url_path = unquote_plus(self.path)
            try:
                url_path = url_path.replace('VIDEO_TS.IFO', '')
            except:
                pass
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
            else:
                url = url_path
            if '.mp4' in url and not '.m3u8' in url and not '.ts' in url:
                log('URL: '+url)
                self.stream_video(url, request_data)
        self.conn.close()

def monitor():
    try:
        try:
            from kodi_six import xbmc
        except:
            import xbmc
        monitor = xbmc.Monitor()
        while not monitor.waitForAbort(3):
            pass
        url = 'http://'+HOST_NAME+':'+str(PORT_NUMBER)+'/stop'
        try:
            r = requests.get(url, timeout=4)
        except:
            pass
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
            r = requests.get(url, timeout=3)
        except:
            pass

    def check_service(self):
        try:
            url = 'http://'+HOST_NAME+':'+str(PORT_NUMBER)+'/check'
            r = requests.head(url, timeout=3)
            if r.status_code == 200:
                return True
            return False
        except:
            return False

    def start(self):
        status = self.check_service()
        if status == False:
            proxy_service = threading.Thread(target=loop_server).start()
            monitor_service = threading.Thread(target=monitor).start()
        else:
            self.reset()

# XtreamProxy().start()