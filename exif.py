import struct

data_types = [0, 1, 1, 2, 4, 8, 1, 1, 2, 4, 8, 4, 8]

f=open('Pictures/IMG_2511.JPG', 'rb')
tag = f.read(4)
a, b, c, d = struct.unpack('BBBB', tag)
if a == 0xff and b == 0xd8 and c == 0xff and d==0xe1 :
    #header or tail go on
    print 'start of image'
length = f.read(2)
length, = struct.unpack('>H', length)
print 'length: ', length

flag = f.read(4)
print flag
if flag == 'Exif':
    f.read(2) # trim 0x00
    exif = f.read(length - 8)
    sq = exif[:2]
    if sq == 'II':
        endian = ''
    elif sq == 'MM':
        endian = '>'
    always = exif[2:4]
    always, = struct.unpack(endian+'H', always)
    if always != 0x002a:
        print 'format is not invalid'

    offset = exif[4:8]
    offset, = struct.unpack(endian + 'I', offset)

    entry_amount = exif[offset:offset + 2]
    entry_amount, = struct.unpack(endian + 'H', entry_amount)
    print 'entry amount: ', entry_amount

    entries = exif[offset + 2:]
    for i in xrange(entry_amount):
        entry_item = entries[i*12:i*12+12]
        #tag_no = entry_item[:2]
        #fmt = entry_item[2:4]
        #length = entry_item[4:8]
        #other = entry_item[8:]

        tag_no, fmt, length, other = struct.unpack(endian + 'HHII', entry_item)    
        print 'tag No.: %d, format: %d, length: %d, other: %d' % (tag_no, fmt, length, other)
        data_length = data_types[fmt] * length
        print 'data length: ', data_length
        if data_length > 4:
            if fmt == 2:
                    #format = '%s%ds' % (endian, data_length)
                    #print format
                    #print "%s" % struct.unpack(format, exif[other:data_length + other])
                    print exif[other:data_length + other]
        else:
            print 'value: %s' % entry_item[8:]

#elif a == 0x90 and b == 0x03:
#print 'aaaa'
#length = f.read(2)
##print 'tag 0x%x' % b
#length, = struct.unpack('>H', length)
##print 'length: %d' % length
#f.read(length-2)
#else:
#length = f.read(2)
##print 'tag 0x%x' % b
#length, = struct.unpack('>H', length)
#print 'length: %d' % length
#f.read(length-2)
