# -*- coding: utf-8 -*-
try:
    from lib.ClientScraper import cfscraper
except ImportError:
    from ClientScraper import cfscraper
import xml.dom.minidom
import base64
try:
    from lib.helper import *
except:
    from helper import *
import re

IPTV_PROBLEM_LOG = translate(os.path.join(profile, 'iptv_problems_log.txt'))

def extract_info(url):
    # Parseia a URL
    parsed_url = urlparse(url)
    protocol = parsed_url.scheme
    # Extrai o host e a porta
    host = parsed_url.hostname
    # Define a porta padrão se não estiver especificada
    if parsed_url.port:
        port = parsed_url.port
    else:
        port = 80 if parsed_url.scheme == 'http' else 443
    
    # Extrai o username e o password dos parâmetros da query
    query_params = parse_qs(parsed_url.query)
    username = query_params.get('username', [None])[0]
    password = query_params.get('password', [None])[0]
    dns = '{0}://{1}:{2}'.format(protocol,host,port)
    
    return dns, username, password

def check_iptv(url_iptv):
    cond = True
    if exists(IPTV_PROBLEM_LOG):
        if six.PY2:
            import io
            open_file = lambda filename, mode: io.open(filename, mode, encoding='utf-8')
        else:
            open_file = lambda filename, mode: open(filename, mode, encoding='utf-8')
        with open_file(IPTV_PROBLEM_LOG, "r") as arquivo:
            urls = arquivo.read()
            urls = urls.split('\n')
            for i in urls:
                if 'http' in i:
                    if i in url_iptv:
                        cond = False
                        break
    return cond

def parselist(url):
    iptv = []
    try:
        url = cfscraper.get(url).json()['url']
    except:
        pass
    try:
        if 'paste.kodi.tv' in url and not 'documents' in url and not 'raw' in url:
            try:
                key = url.split('/')[-1]
                url = 'https://paste.kodi.tv/documents/' + key
                src = cfscraper.get(url).json()['data']
                lines = src.split('\n')
                if lines:
                    for i in lines:
                        i = i.replace(' ', '')
                        if 'http' in i:
                            if check_iptv(i):
                                dns, username, password = extract_info(i)
                                iptv.append((dns,username,password))
            except:
                pass
        else:
            src = cfscraper.get(url).text
            lines = src.split('\n')
            if lines:
                for i in lines:
                    i = i.replace(' ', '')
                    if 'http' in i:
                        if check_iptv(i):
                            dns, username, password = extract_info(i)
                            iptv.append((dns,username,password))
    except:
        pass
    return iptv


def replace_desc(desc):
    substituicoes = {
        '[': '[COLOR yellow][',
        '(': '[/COLOR]('
    }

    def substituidor(match):
        return substituicoes[match.group(0)]

    padrao = re.compile('|'.join(map(re.escape, substituicoes.keys())))
    resultado = padrao.sub(substituidor, desc)
    return resultado

def replace_name(name):
    if '-' in name:
        name = name.replace('-', '-[COLOR yellow]')
        name = name + '[/COLOR]'
    return name

def ordenar_resolucao(item):
    name = item[0]
    if 'FHD' in name:
        return 1
    elif 'HD' in name:
        return 2
    elif '4K' in name:
        return 3    
    elif 'SD' in name:
        return 4
    return 5 

    

class API:
    def __init__(self, dns, username, password):
        self.live_url = '{0}/enigma2.php?username={1}&password={2}&type=get_live_categories'.format(dns, username, password)
        self.vod_url = '{0}/enigma2.php?username={1}&password={2}&type=get_vod_categories'.format(dns, username, password)
        self.series_url = '{0}/enigma2.php?username={1}&password={2}&type=get_series_categories'.format(dns, username, password)
        self.player_api = '{0}/player_api.php?username={1}&password={2}'.format(dns, username, password)
        self.play_url = '{0}/live/{1}/{2}/'.format(dns,username,password)
        self.play_movies = '{0}/movie/{1}/{2}/'.format(dns,username,password)
        self.play_series = '{0}/series/{1}/{2}/'.format(dns,username,password)
        self.adult_tags = ['xxx','xXx','XXX','adult','Adult','ADULT','adults','Adults','ADULTS','porn','Porn','PORN', 'teste', 'TESTE', 'Teste']
        self.hide_adult = 'true'

    def http(self, url='', mode=None):
        if not mode:
            try:
                return cfscraper.get(url).content    
            except:
                pass
        elif mode == 'channels_category':
            try:
                return cfscraper.get(self.live_url).content
            except:
                pass
        elif mode == 'json_url':
            try:
                return cfscraper.get(url).json()
            except:
                pass
        elif mode == 'vod':
            try:
                return cfscraper.get(url).text
            except:
                pass
        return ''


        
        
    def b64(self, obj):
        return base64.b64decode(obj).decode('utf-8')
    
    def check_protocol(self,url):
        parsed = urlparse(self.live_url)
        protocol = parsed.scheme
        if protocol=='https':
            return url.replace('http','https')
        return url
    
    def regex_from_to(self, text, from_string, to_string, excluding=True):
        if excluding:
            try: r = re.search("(?i)" + from_string + "([\S\s]+?)" + to_string, text).group(1)
            except: r = ''
        else:
            try: r = re.search("(?i)(" + from_string + "[\S\s]+?" + to_string + ")", text).group(1)
            except: r = ''
        return r 

    def regex_get_all(self, text, start_with, end_with):
        r = re.findall("(?i)(" + start_with + "[\S\s]+?" + end_with + ")", text)
        return r       

    
    def channels_category(self):
        itens = []
        xml_data = self.http('', 'channels_category')
        if xml_data:
            doc = xml.dom.minidom.parseString(xml_data)
            if doc:
                for i, _ in enumerate(doc.getElementsByTagName('channel')):
                    name = self.b64(doc.getElementsByTagName('title')[i].firstChild.nodeValue)
                    url = self.check_protocol(doc.getElementsByTagName('playlist_url')[i].firstChild.nodeValue).replace('<![CDATA[','').replace(']]>','')
                    if not 'All' in name: 
                        if self.hide_adult == 'false':                      
                            itens.append((name,url))
                        else:
                            if not any(s in name for s in self.adult_tags):
                                itens.append((name,url))
        return itens
    
    def channel_id(self,json_data,n):
        if json_data:
            for i, d in enumerate(json_data):
                if n == i:
                    return d.get('stream_id', '')
        return ''

    
    def channels_open(self,url):
        try:
            chan_id = url.split('cat_id=')[1]
        except:
            chan_id = ''
        try:
            chan_id = chan_id.split('&')[0]
        except:
            pass
        if not chan_id:
            try:
                chan_id = url.split('category_id=')[1]
            except:
                chan_id = ''
            try:
                chan_id = chan_id.split('&')[0]
            except:
                pass           

        itens = []
        xml_data = self.http(url)
        if xml_data and chan_id:
            url_json_channels = '{0}&action=get_live_streams&category_id={1}'.format(self.player_api,chan_id)
            json_data = self.http(url_json_channels,'json_url')            
            doc = xml.dom.minidom.parseString(xml_data)
            if doc:
                for i, _ in enumerate(doc.getElementsByTagName('channel')):
                    name = re.sub('\[.*?min ','-',self.b64(doc.getElementsByTagName('title')[i].firstChild.nodeValue))
                    url_ = self.check_protocol(doc.getElementsByTagName('stream_url')[i].firstChild.nodeValue).replace('<![CDATA[','').replace(']]>','')
                    stream_id = self.channel_id(json_data,i)
                    url_ = '{0}{1}.m3u8'.format(self.play_url,stream_id)
                    try:
                        name = replace_name(name)
                    except:
                        pass
                    try:
                        thumb = (doc.getElementsByTagName('desc_image')[i].firstChild.nodeValue).replace('<![CDATA[ ','').replace(' ]]>','')
                        desc = self.b64(doc.getElementsByTagName('description')[i].firstChild.nodeValue)
                        try:
                            desc = replace_desc(desc)
                        except:
                            pass
                    except:
                        thumb = ''
                        desc = 'No Info Available'
                    itens.append((name,url_,thumb,desc))
        
        if itens:
            try:
                itens = sorted(itens, key=ordenar_resolucao)
            except:
                pass
        return itens

    def series_cat(self):
        itens = []
        url_series = '{0}&action=get_series_categories'.format(self.player_api)
        vod_cat = self.http(url_series,'json_url')
        if vod_cat:
            for cat in vod_cat:
                name = cat['category_name']
                url = self.player_api + '&action=get_series&category_id='+cat['category_id']                
                if self.hide_adult == 'false':
                    itens.append((name,url))
                else:
                    if not any(s in name for s in self.adult_tags):
                        itens.append((name,url))
        return itens
    
    def series_list(self,url):
        itens = []
        ser_cat = self.http(url,'json_url')
        if ser_cat:
            for ser in ser_cat:	
                name = ser['name']
                url = self.player_api+'&action=get_series_info&series_id='+str(ser['series_id'])
                try:
                    thumb = ser['cover']
                    background = ser['backdrop_path'][0]
                    plot = ser['plot']
                    releaseDate = ser['releaseDate']
                    cast = str(ser['cast']).split()
                    rating_5based = ser['rating_5based']
                    episode_run_time = str(ser['episode_run_time'])
                    genre = ser['genre']
                except:
                    thumb = ''
                    plot = ''
                    releasedate = ''
                    cast = ('', '')
                    rating_5based = ''
                    episode_run_time = ''
                    genre = ''
                itens.append((name,url,thumb,background,plot,releaseDate,cast,rating_5based,episode_run_time,genre)) # series seasons
        return itens
    
    def series_seasons(self,url):
        itens = []
        ser_cat = self.http(url,'json_url')
        if ser_cat:
            for ser in ser_cat['episodes']:
                info = ser_cat['info']
                try:
                    thumb = info['cover']
                except:
                    thumb = ''
                try:
                    background = info['backdrop_path'][0]
                except:
                    background = ''
                name = 'Season - '+ser
                url_ = url+'&season_number='+str(ser)
                itens.append((name,url_,thumb,background)) # season list
        return itens
    
    def season_list(self,url):
        itens = []
        ser_cat = self.http(url,'json_url')
        info = ser_cat['info']
        ser_cat = ser_cat['episodes']
        parsed_url = urlparse(url)
        season_number = str(parse_qs(parsed_url.query)['season_number'][0])
        for ser in ser_cat[season_number]:
            url = self.play_series+str(ser['id'])+'.'+ser['container_extension']
            name = ser['title']
            try:
                thumb = ser['info']['movie_image']
            except:
                thumb = ''
            try:
                background = ser['info']['movie_image']
            except:
                background = ''
            try:
                plot = ser['info']['plot']
            except:
                plot = ''
            try:
                releasedate = ser['info']['releasedate']
            except:
                releasedate = ''
            try:
                cast = str(info['cast']).split()
            except:
                cast = ('', '')
            try:
                rating_5based = info['rating_5based']
            except:
                rating_5based = ''
            try:
                duration = str(ser['info']['duration'])
            except:
                duration = ''
            try:
                genre = info['genre']
            except:
                genre = ''
            itens.append((name,url,thumb,background,plot,releasedate,cast,rating_5based,duration,genre))
        return itens 

    def vod(self,url=''):
        # exemplo no addon
        # tipo = t[0]
        # if tipo == 'dir':
        #     d, name1, name2 = t        
        itens = []
        if not url:
            open = self.http(self.vod_url, mode='vod')
        else:
            open = self.http(url, 'vod')
        if open:
            all_cats = self.regex_get_all(open,'<channel>','</channel>')
            if all_cats:
                for a in all_cats:
                    if '<playlist_url>' in open:
                        name = str(self.b64(self.regex_from_to(a,'<title>','</title>'))).replace('?','')
                        url = self.check_protocol(self.regex_from_to(a,'<playlist_url>','</playlist_url>').replace('<![CDATA[','').replace(']]>',''))
                        if not 'All' in name: 
                            if self.hide_adult == 'false':
                                itens.append(('dir', name,url))
                            else:
                                if not any(s in name for s in self.adult_tags):
                                    itens.append(('dir', name,url))
                    else:
                        try:
                            name = self.b64(self.regex_from_to(a,'<title>','</title>'))
                            thumb= self.regex_from_to(a,'<desc_image>','</desc_image>').replace('<![CDATA[','').replace(']]>','')
                            url = self.check_protocol(self.regex_from_to(a,'<stream_url>','</stream_url>').replace('<![CDATA[','').replace(']]>',''))
                            desc = self.b64(self.regex_from_to(a,'<description>','</description>'))
                            plot = self.regex_from_to(desc,'PLOT:','\n')
                            try:
                                cast = self.regex_from_to(desc,'CAST:','\n')
                            except:
                                cast = ('', '')
                            ratin= self.regex_from_to(desc,'RATING:','\n')
                            year = self.regex_from_to(desc,'RELEASEDATE:','\n').replace(' ','-')
                            year = re.compile('-.*?-.*?-(.*?)-',re.DOTALL).findall(year)
                            runt = self.regex_from_to(desc,'DURATION_SECS:','\n')
                            genre= self.regex_from_to(desc,'GENRE:','\n')
                            background = ''
                            itens.append(('play', name, url, thumb, background,plot,str(year).replace("['","").replace("']",""),str(cast).split(),ratin,genre))
                        except:pass
        return itens                        


