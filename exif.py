import sys
import struct

from exif_tags import *

class ExifInfo:
    def __init__(self):
        #self.__file_name =  file_name
        self.__endian = ''
        self.__exif = None
        self.__exif_info = {}

    def _ifd_info(self, offset):
        entry_amount = self.__exif[offset:offset + 2]
        entry_amount, = struct.unpack(self.__endian + 'H', entry_amount)

        entries = self.__exif[offset + 2:]
        for i in xrange(entry_amount):
            entry_item = entries[i*12:i*12+12]

            tag_no, fmt, length = struct.unpack(self.__endian + 'HHI', entry_item[:8])    
            self._tag_handle(tag_no, fmt, length, entry_item[8:])

        return entry_amount

    def _data_handle(self, tag, data_type, length, data):
        if data_type == 2 or data_type == 1 or data_type == 6:
            if data[-1] == '\x00':
                data = data[:-1]
            return data
        elif data_type == 3:
            r = struct.unpack(''.join([self.__endian,'H'*length]), data)
        elif data_type == 4:
            r = struct.unpack(self.__endian + 'I'*length, data)
        elif data_type == 5:
            return " ".join(['%d/%d']*length) % struct.unpack(self.__endian + 'II'*length, data)
        elif data_type == 8:
            r = struct.unpack(self.__endian + 'H'*length, data)
        elif data_type == 9:
            r = struct.unpack(self.__endian + 'I'*length, data)
        elif data_type == 10:
            return " ".join(['%d/%d']*length) % struct.unpack(self.__endian + 'ii'*length, data)
        elif data_type == 11:
            r = struct.unpack(self.__endian + 'f'*length, data)
        elif data_type == 12:
            r = struct.unpack(self.__endian + 'd'*length, data)
        elif data_type == 7:
            if tag == 0x9101:
                a, b, c, d = struct.unpack(self.__endian + 'BBBB', data)
                return "".join([components_config[a], components_config[b], components_config[c]])
            elif tag == 0xa301 or tag == 0xa300:
                return "0x%x" % struct.unpack(self.__endian + 'B', data)
            elif tag == 0xa302:
                return "0x%04x,0x%04x,0x%02x,0x%02x,0x%02x,0x%02x" % struct.unpack(self.__endian + 'HHBBBB', data)
            else:
                return data

        if isinstance(r, tuple) and len(r) == 1:
            return r[0]
        else:
            return r

    def _tag_handle(self, tag, fmt, length, other):
        data_length = data_types[fmt] * length
        if tag == 0x8769:
            offset, = struct.unpack(self.__endian + 'I', other)
            self._ifd_info(offset)
        else:
            if data_length > 4:
                offset, = struct.unpack(self.__endian + 'I', other)
                data = self.__exif[offset:offset + data_length]
            else:
                data = other[:data_length]

            value = self._data_handle(tag, fmt, length, data)
            if ifd_dic.has_key(tag):
                self.__exif_info[ifd_dic[tag]] = value
            else:
                self.__exif_info[tag] = value

    def do_parse(self, file_name):
        f=open(file_name, 'rb')
        tag = f.read(4)
        a, b, c, d = struct.unpack('BBBB', tag)
        if a == 0xff and b == 0xd8 and c == 0xff and d==0xe1 :
            #header or tail go on
            pass
        else:
            print 'format is not invalid'
            return

        length = f.read(2)
        length, = struct.unpack('>H', length)

        flag = f.read(4)
        if flag == 'Exif':
            f.read(2) # trim 0x00
            exif = f.read(length - 8)
            self.__exif = exif
            sq = exif[:2]
            if sq == 'II':
                self.__endian = ''
            elif sq == 'MM':
                self.__endian = '>'
            always = exif[2:4]
            always, = struct.unpack(self.__endian+'H', always)
            if always != 0x002a:
                print 'format is not invalid'
                return -1

            ifd_pos = 4
            while ifd_pos:
                offset = exif[ifd_pos:ifd_pos+4]
                offset, = struct.unpack(self.__endian + 'I', offset)
                if not offset:
                    break

                entry_amount = self._ifd_info(offset)
                ifd_pos = offset + entry_amount * 12 + 2

        return self.__exif_info

from datetime import datetime
if __name__ == '__main__':
    ei = ExifInfo()
    for i in xrange(1, len(sys.argv)):
        r = ei.do_parse(sys.argv[i])
        d = datetime.strptime(r['DateTimeOriginal'], "%Y:%m:%d %H:%M:%S")
        print d
