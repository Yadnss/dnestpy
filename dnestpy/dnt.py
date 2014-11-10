import logging
import struct
from pathlib import Path
from collections import namedtuple
logger = logging.getLogger(__name__)

# Functions for parsing cells from the DNT file

def parse_byte(buff):
    return struct.unpack('B', buff.read(1))[0]

def parse_varchar(buff):
    nchar = struct.unpack('<H', buff.read(2))[0]
    return buff.read(nchar).decode('euckr')

def parse_bool(buff):
    return struct.unpack('?xxx', buff.read(4))[0]

def parse_int(buff):
    return struct.unpack('<I', buff.read(4))[0]

def parse_float(buff):
    return struct.unpack('<f', buff.read(4))[0]

Column = namedtuple('Column', ['name', 'parse'])


class DNTFile(object):
    """Parses a DNT file into a set of named tuples"""
    HEADER = b'\x00\x00\x00\x00'
    TAIL = b'\x05THEND'
    TYPEMAP = {
        1: parse_varchar,
        2: parse_bool,
        3: parse_int,
        4: parse_float,
        5: parse_float
    }

    def __init__(self, path):
        logger.info('Parsing DNT File: {}'.format(path))
        with Path(path).open('rb') as buff:
            assert buff.read(4) == self.HEADER, \
                   "Not a recognized DNT file, invalid header"
            ncols, nrows = struct.unpack('<HI', buff.read(6))
            self.columns = [Column('id', parse_int)]
            self.columns.extend(self.parse_column(buff) for _ in range(ncols))
            self.Row = namedtuple('Row', [c.name for c in self.columns])
            self.rows = tuple(self.parse_row(buff) for _ in range(nrows))

    def parse_column(self, buff):
        """Read column information from header data"""
        name = parse_varchar(buff)[1:] # strip leading underscores from names
        parser = self.TYPEMAP[parse_byte(buff)]
        return Column(name, parser)

    def parse_row(self, buff):
        """Read row information from cursor position"""
        return self.Row(*[c.parse(buff) for c in self.columns])
