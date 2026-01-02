import requests
try:
    from thunderlib import bencodepy
except ImportError:
    import bencodepy
import hashlib
import base64
from urllib.parse import quote_plus


def make_magnet_from_file(file):
    try:
        metadata = bencodepy.decode(file)
    except:
        metadata = bencodepy.decode_from_file(file)
    subj = metadata[b'info']
    hashcontents = bencodepy.encode(subj)
    digest = hashlib.sha1(hashcontents).digest()
    b32hash = base64.b32encode(digest).decode()
    return 'magnet:?'\
             + 'xt=urn:btih:' + b32hash\
             + '&amp;dn=' + quote_plus(metadata[b'info'][b'name'].decode())\
             + '&amp;tr=' + quote_plus(metadata[b'announce'].decode())\


def get_magnet(url):
    try:
        r = requests.get(url)
        file = r.content
        magnet = make_magnet_from_file(file)
    except:
        magnet = ''
    return magnet  

