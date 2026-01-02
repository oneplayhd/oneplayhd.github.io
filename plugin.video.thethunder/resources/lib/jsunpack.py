# -*- coding: utf-8 -*-
"""
    ResolveUrl Kodi Addon
    Copyright (C) 2013 Bstrdsmkr
    Additional fixes by mortael, jairoxyz

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    Adapted for use in xbmc from:
    https://github.com/beautify-web/js-beautify/blob/master/python/jsbeautifier/unpackers/packer.py

    Unpacker for Dean Edward's p.a.c.k.e.r, a part of javascript beautifier
    by Einar Lielmanis <einar@jsbeautifier.org>

        written by Stefano Sanfilippo <a.little.coder@gmail.com>

    usage:

    if detect(some_string):
        unpacked = unpack(some_string)

    Unpacker for Dean Edward's p.a.c.k.e.r
"""

import re
import binascii

__all__ = ["detect", "unpack", "UnpackingError"]

# Precompile regexes for performance
_WORD_REGEX = re.compile(r"\b\w+\b", flags=re.ASCII)


def detect(source: str) -> bool:
    """Detects whether `source` is P.A.C.K.E.R. coded."""
    return re.search(
        r"eval\s*\(\s*function\s*\(\s*p\s*,\s*a\s*,\s*c\s*,\s*k\s*,\s*e\s*,",
        source,
    ) is not None


def unpack(source: str) -> str:
    """Unpacks P.A.C.K.E.R. packed JS code."""
    payload, symtab, radix, count = _filterargs(source)

    if count != len(symtab):
        raise UnpackingError("Malformed p.a.c.k.e.r. symtab.")

    try:
        unbase = Unbaser(radix)
    except TypeError:
        raise UnpackingError("Unknown p.a.c.k.e.r. encoding.")

    def lookup(match: re.Match) -> str:
        word = match.group(0)
        return symtab[int(word)] if radix == 1 else symtab[unbase(word)] or word

    def getstring(c: int, a: int = radix) -> str:
        chars = []
        while True:
            chars.append(chr(c % a + 161))
            if c < a:
                break
            c //= a
        return "".join(reversed(chars))

    payload = payload.replace("\\\\", "\\").replace("\\'", "'")

    # Detect variant using String.fromCharCode(..., +161)
    p = re.search(r"eval\(function\(p,a,c,k,e.+?String\.fromCharCode\(([^)]+)", source)
    pnew = bool(
        p and re.findall(r"String\.fromCharCode\(([^)]+)", source)[0].split("+")[1] == "161"
    )

    if pnew:
        replacer = {getstring(i): symtab[i] for i in range(count)}
        regex = re.compile("|".join(map(re.escape, replacer.keys())))
        payload = regex.sub(lambda m: replacer[m.group(0)], payload)
        return _replacejsstrings(_replacestrings(payload))
    else:
        return _replacestrings(_WORD_REGEX.sub(lookup, payload))


def _filterargs(source: str):
    """Extract args from source needed by decoder."""
    argsregex = r"}\s*\('(.*)',\s*(.*?),\s*(\d+),\s*'(.*?)'\.split\('\|'\)"
    args = re.search(argsregex, source, re.DOTALL).groups()

    try:
        payload, radix, count, symtab = args
        radix = 36 if not radix.isdigit() else int(radix)
        return payload, symtab.split("|"), radix, int(count)
    except ValueError:
        raise UnpackingError("Corrupted p.a.c.k.e.r. data.")


def _replacestrings(source: str) -> str:
    """Replace JS lookup string table with actual values."""
    match = re.search(r'var *(_\w+)=\["(.*?)"];', source, re.DOTALL)
    if match:
        varname, strings = match.groups()
        startpoint = len(match.group(0))
        lookup = strings.split('","')
        variable = f"{varname}[%d]"
        for index, value in enumerate(lookup):
            if "\\x" in value:
                value = binascii.unhexlify(value.replace("\\x", "")).decode("ascii")
            source = source.replace(variable % index, f'"{value}"')
        return source[startpoint:]
    return source


def _replacejsstrings(source: str) -> str:
    """Replace JS \\x encoded strings with their ASCII values."""
    return re.sub(
        r"\\x([0-7][0-9A-F])",
        lambda m: binascii.unhexlify(m.group(1)).decode("ascii"),
        source,
    )


class Unbaser:
    """Functor for a given base. Converts strings to natural numbers."""

    ALPHABET = {
        62: "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
        95: (
            r' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            r"[\]^_`abcdefghijklmnopqrstuvwxyz{|}~"
        ),
    }

    def __init__(self, base: int):
        self.base = base
        if 2 <= base <= 36:
            self.unbase = lambda s: int(s, base)
        else:
            if base < 62:
                self.ALPHABET[base] = self.ALPHABET[62][:base]
            elif 62 < base < 95:
                self.ALPHABET[base] = self.ALPHABET[95][:base]
            try:
                self.dictionary = {c: i for i, c in enumerate(self.ALPHABET[base])}
            except KeyError:
                raise TypeError("Unsupported base encoding.")
            self.unbase = self._dictunbaser

    def __call__(self, string: str) -> int:
        return self.unbase(string)

    def _dictunbaser(self, string: str) -> int:
        ret = 0
        for index, cipher in enumerate(reversed(string)):
            ret += (self.base**index) * self.dictionary[cipher]
        return ret


class UnpackingError(Exception):
    """Raised when unpacking fails due to corrupted or malformed source."""
    pass
