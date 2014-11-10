"""Module for extracting dragonnest PAK archives"""
import logging
from pathlib import Path
import struct
import zlib
logger = logging.getLogger(__name__)


class PAKFile(object):
    """An individual file inside a PAK archive

    Args:
        buff (file-like): the PAK archive containing this file
    """

    def __init__(self, buff):
        self.buff = buff
        self.path = Path(*buff.read(0x100) \
                                      .partition(b'\x00')[0] \
                                      .decode('euckr') \
                                      .split('\\'))
        self.zsize = struct.unpack('<I', buff.read(4))[0]
        self.size = struct.unpack('<I', buff.read(4))[0]
        self.zsize1 = struct.unpack('<I', buff.read(4))[0]
        self.offset = struct.unpack('<I', buff.read(4))[0]
        self.unk3 = struct.unpack('<I', buff.read(4))[0]
        assert buff.read(0x28) == b'\x00' * 0x28, \
               "Corrupt file listing in PAK archive"

    def __repr__(self):
        return str(self.path)

    def extract(self, path):
        """Extract archived file to specified path

        Args:
            path (str): folder to extract file to
        """
        logger.info('Extracting file {} to {}'.format(self.path, path))
        out = Path(path) / self.path
        if not out.parent.is_dir():
            out.parent.mkdir(parents=True)

        self.buff.seek(self.offset, 0)
        zbytes = zlib.decompress(self.buff.read(self.zsize))
        with out.open('wb') as fout:
            fout.write(zbytes)


class PAKArchive(object):
    """The PAK archive file"""
    IDSTRING = b"EyedentityGames Packing File 0.1"

    def __init__(self, path):
        self.path = Path(path)
        self.buff = None
        self.files = []

    def __enter__(self):
        self.buff = self.path.open('rb')
        self.read_filelist()
        return self

    def __exit__(self, *exc):
        self.buff.close()
        return False

    def read_filelist(self):
        """Read the PAK header to get archive information"""
        logger.info('Reading filelist for {}'.format(self.path))
        assert self.buff.read(len(self.IDSTRING)) == self.IDSTRING, \
               'Not a valid PAK archive: {}'.format(self.path)
        self.buff.seek(0x100, 0)
        assert self.buff.read(4) == b'\x0B\x00\x00\x00', \
               'Not a valid PAK archive: {}'.format(self.path)

        num_files = struct.unpack('<I', self.buff.read(4))[0]
        info_offset = struct.unpack('<I', self.buff.read(4))[0]
        self.buff.seek(info_offset, 0)

        self.files = sorted([PAKFile(self.buff) for _ in range(num_files)],
                            key=lambda x: x.offset)
