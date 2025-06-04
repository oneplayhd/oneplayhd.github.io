# -*- coding: utf-8 -*-
import socket
import random
import struct
import sys
import logging
from resources.modules import control

# Configura logging para depuração
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class DNSOverride(object):
    def __init__(self, dns_server="1.1.1.1"):
        self.dns_server = control.setting('dns_resolver') if control.setting('dns_resolver') else dns_server
        self.PY2 = sys.version_info[0] == 2
        self.original_getaddrinfo = socket.getaddrinfo
        self.cache = {}
        self.debug_mode = False  # Modo de depuração ativado

        # Ativa override
        socket.getaddrinfo = self._resolver

    def bchr(self, val):
        return chr(val) if self.PY2 else bytes([val])

    def bjoin(self, parts):
        return b"".join(parts)

    def to_bytes(self, val):
        if self.PY2:
            return val if isinstance(val, str) else val.encode("utf-8")
        return val if isinstance(val, bytes) else val.encode("utf-8")
    
    def is_valid_ipv4(self, ip):
        try:
            socket.inet_aton(ip)
            return True
        except socket.error:
            return False    

    def resolve(self, domain):
        if domain in self.cache:
            logging.debug("Cache hit for {0}: {1}".format(domain, self.cache[domain]))
            return self.cache[domain]

        def build_query(domain):
            tid = random.randint(0, 65535)
            header = struct.pack(">HHHHHH", tid, 0x0100, 1, 0, 0, 0)
            qname_parts = []
            for part in domain.split('.'):
                if not part:
                    continue
                qname_parts.append(self.bchr(len(part)))
                qname_parts.append(self.to_bytes(part))
            qname_parts.append(self.bchr(0))
            qname = self.bjoin(qname_parts)
            question = qname + struct.pack(">HH", 1, 1)  # A, IN
            return header + question, tid

        def parse_response(data, tid):
            if len(data) < 12:
                logging.error("Resposta DNS muito curta")
                return None
            if struct.unpack(">H", data[:2])[0] != tid:
                logging.error("ID da transação DNS não corresponde")
                return None
            answers = struct.unpack(">H", data[6:8])[0]
            i = 12
            while i < len(data) and (ord(data[i]) if self.PY2 else data[i]) != 0:
                i += 1
            i += 5
            for _ in range(answers):
                if i + 10 >= len(data):
                    logging.error("Resposta DNS inválida: truncada")
                    return None
                i += 2  # Pular name
                type_, class_, ttl, rdlen = struct.unpack(">HHIH", data[i:i+10])
                i += 10
                if type_ == 1 and class_ == 1 and rdlen == 4:  # A record, IN class
                    ip = ".".join(str(ord(c)) if self.PY2 else str(c) for c in data[i:i+4])
                    self.cache[domain] = ip
                    logging.debug("Resolved {0} to {1}".format(domain, ip))
                    return ip
                i += rdlen
            logging.warning("Nenhum registro A encontrado para {0}".format(domain))
            return None

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(5)  # Aumentado para 5 segundos
            query, tid = build_query(domain)
            s.sendto(query, (self.dns_server, 53))
            data, _ = s.recvfrom(512)
            s.close()
            return parse_response(data, tid)
        except socket.timeout:
            logging.error("Timeout ao consultar DNS para {0}".format(domain))
            return None
        except Exception as e:
            logging.error("Erro ao resolver {0}: {1}".format(domain, e))
            return None

    def _resolver(self, host, port, *args, **kwargs):
        try:
            # Se já for um IP válido, retorna direto
            if self.is_valid_ipv4(host):
                logging.debug("Bypass DNS: {0} já é um IP".format(host))
                return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (host, port))]

            ip = self.resolve(host)
            if ip:
                return [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (ip, port))]
            logging.warning("Falha ao resolver {0}, usando getaddrinfo original".format(host))
            if not self.debug_mode:
                return self.original_getaddrinfo(host, port, *args, **kwargs)
        except Exception as e:
            logging.error("Erro no resolver para {0}: {1}".format(host, e))
        if not self.debug_mode:
            return self.original_getaddrinfo(host, port, *args, **kwargs)

