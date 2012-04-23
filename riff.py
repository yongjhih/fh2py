
import struct, binascii
from StringIO import StringIO

compressions = {
    0x01: 'Microsoft PCM',
    0x02: 'Microsoft ADPCM',
    0x03: 'Microsoft IEEE float',
    0x04: 'Compaq VSELP',
    0x05: 'IBM CVSD',
    0x06: 'Microsoft a-Law',
    0x07: 'Microsoft u-Law',
    0x08: 'Microsoft DTS',
    0x09: 'DRM',
    0x0a: 'WMA 9 Speech',
    0x10: 'OKI-ADPCM',
    0x11: 'Intel IMA/DVI-ADPCM',
    0x12: 'Videologic Mediaspace ADPCM',
    0x13: 'Sierra ADPCM',
    0x14: 'Antex G.723 ADPCM',
    0x15: 'DSP Solutions DIGISTD',
    0x16: 'DSP Solutions DIGIFIX',
    0x17: 'Dialoic OKI ADPCM',
    0x18: 'Media Vision ADPCM',
    0x19: 'HP CU',
    0x20: 'Yamaha ADPCM',
    0x21: 'SONARC Speech Compression',
    0x22: 'DSP Group True Speech',
    0x23: 'Echo Speech Corp.',
    0x24: 'Virtual Music Audiofile AF36',
    0x25: 'Audio Processing Tech.',
    0x26: 'Virtual Music Audiofile AF10',
    0x27: 'Aculab Prosody 1612',
    0x28: 'Merging Tech. LRC',
    0x30: 'Dolby AC2',
    0x31: 'Microsoft GSM610',
    0x32: 'MSN Audio',
    0x33: 'Antex ADPCME',
    0x34: 'Control Resources VQLPC',
    0x35: 'DSP Solutions DIGIREAL',
    0x36: 'DSP Solutions DIGIADPCM',
    0x37: 'Control Resources CR10',
    0x38: 'Natural MicroSystems VBX ADPCM',
    0x39: 'Crystal Semiconductor IMA ADPCM',
    0x3a: 'Echo Speech ECHOSC3',
    0x3b: 'Rockwell ADPCM',
    0x3c: 'Rockwell DIGITALK',
    0x3d: 'Xebec Multimedia',
    0x40: 'Antex G.721 ADPCM',
    0x41: 'Antex G.728 CELP',
    0x42: 'Microsoft MSG723',
    0x45: 'ITU-T G.726',
    0x50: 'Microsoft MPEG',
    0x51: 'RT23 or PAC',
    0x52: 'InSoft RT24',
    0x53: 'InSoft PAC',
    0x55: 'MP3',
    0x59: 'Cirrus',
    0x60: 'Cirrus Logic',
    0x61: 'ESS Tech. PCM',
    0x62: 'Voxware Inc.',
    0x63: 'Canopus ATRAC',
    0x64: 'APICOM G.726 ADPCM',
    0x65: 'APICOM G.722 ADPCM',
    0x66: 'Microsoft DSAT',
    0x67: 'Micorsoft DSAT DISPLAY',
    0x69: 'Voxware Byte Aligned',
    0x70: 'Voxware AC8',
    0x71: 'Voxware AC10',
    0x72: 'Voxware AC16',
    0x73: 'Voxware AC20',
    0x74: 'Voxware MetaVoice',
    0x75: 'Voxware MetaSound',
    0x76: 'Voxware RT29HW',
    0x77: 'Voxware VR12',
    0x78: 'Voxware VR18',
    0x79: 'Voxware TQ40',
    0x80: 'Soundsoft',
    0x81: 'Voxware TQ60',
    0x82: 'Microsoft MSRT24',
    0x83: 'AT&T G.729A',
    0x84: 'Motion Pixels MVI MV12',
    0x85: 'DataFusion G.726',
    0x86: 'DataFusion GSM610',
    0x88: 'Iterated Systems Audio',
    0x89: 'Onlive',
    0x91: 'Siemens SBC24',
    0x92: 'Sonic Foundry Dolby AC3 APDIF',
    0x93: 'MediaSonic G.723',
    0x94: 'Aculab Prosody 8kbps',
    0x97: 'ZyXEL ADPCM',
    0x98: 'Philips LPCBB',
    0x99: 'Studer Professional Audio Packed',
    0xa0: 'Malden PhonyTalk',
    0x100: 'Rhetorex ADPCM',
    0x101: 'IBM u-Law',
    0x102: 'IBM a-Law',
    0x103: 'IBM ADPCM',
    0x111: 'Vivo G.723',
    0x112: 'Vivo Siren',
    0x123: 'Digital G.723',
    0x125: 'Sanyo LD ADPCM',
    0x130: 'Sipro Lab ACEPLNET',
    0x131: 'Sipro Lab ACELP4800',
    0x132: 'Sipro Lab ACELP8V3',
    0x133: 'Sipro Lab G.729',
    0x134: 'Sipro Lab G.729A',
    0x135: 'Sipro Lab Kelvin',
    0x140: 'Dictaphone G.726 ADPCM',
    0x150: 'Qualcomm PureVoice',
    0x151: 'Qualcomm HalfRate',
    0x155: 'Ring Zero Systems TUBGSM',
    0x160: 'Microsoft Audio1',
    0x200: 'Creative Labs ADPCM',
    0x202: 'Creative Labs FASTSPEECH8',
    0x203: 'Creative Labs FASTSPEECH10',
    0x210: 'UHER ADPCM',
    0x220: 'Quarterdeck Corp.',
    0x230: 'I-Link VC',
    0x240: 'Aureal Semiconductor Raw Sport',
    0x250: 'Interactive Products HSX',
    0x251: 'Interactive Products RPELP',
    0x260: 'Consistent CS2',
    0x270: 'Sony SCX',
    0x300: 'Fujitsu FM TOWNS SND',
    0x400: 'Brooktree Digital',
    0x450: 'QDesign Music',
    0x680: 'AT&T VME VMPCM',
    0x681: 'AT&T TCP',
    0x1000: 'Olivetti GSM',
    0x1001: 'Olivetti ADPCM',
    0x1002: 'Olivetti CELP',
    0x1003: 'Olivetti SBC',
    0x1004: 'Olivetti OPR',
    0x1100: 'Lernout & Hauspie',
    0x1400: 'Norris Comm. Inc.',
    0x1401: 'ISIAudio',
    0x1500: 'AT&T Soundspace Music Compression',
    0x2000: 'FAST Multimedia DVM',
    0xfffe: 'Extensible',
    0xffff: 'Development',
}

info_chunks = dict(
    IARL = 'ArchivalLocation',
    IART = 'Artist',
    ICMS = 'Commissioned',
    ICMT = 'Comment',
    ICOP = 'Copyright',
    ICRD = 'DateCreated',
    ICRP = 'Cropped',
    IDIM = 'Dimensions',
    IDPI = 'DotsPerInch',
    IENG = 'Engineer',
    IGNR = 'Genre',
    IKEY = 'Keywords',
    ILGT = 'Lightness',
    IMED = 'Medium',
    INAM = 'Title',
    IPLT = 'NumColors',
    IPRD = 'Product',
    ISBJ = 'Subject',
    ISFT = 'Software',
    ISHP = 'Sharpness',
    ISRC = 'Source',
    ISRF = 'SourceForm',
    ITCH = 'Technician',
    TURL = 'URL',
    TORG = 'Organisation',
)

def readint(f):
    ind = f.read(4)
    x, = struct.unpack('L', ind)
    return x

def readinfo(f):
    out = {}
    while True:
        type = f.read(4)
        if type == '': break
        len = readint(f)
        val = f.read(len-2)
        f.read(2)
        if len % 2: f.read(1)
        assert type in info_chunks, 'unknown chunk %r'%type
        out[info_chunks[type]] = val
    return out

def readwavechunk(f):
    type = f.read(4)
    #print 'chunk type', type
    len = readint(f)
    #print 'chunk len', len
    chunkdata = f.read(len)
    if len % 2:
        print 'odd', len
        f.read(1)
    if type == 'LIST' and chunkdata.startswith('INFO'):
        sio = StringIO(chunkdata)
        sio.read(4)
        info = readinfo(sio)
        if info != {}:
            # print 'file:', f.name
            for k, v in info.items():
                pass #print '  ', k + ':', v
            # print

def readwav(f):
    f.seek(0)
    assert 0 == f.tell(), 'tell %d != expected 0'%f.tell()
    assert 'RIFF' == f.read(4), 'not a RIFF'
    assert 4 == f.tell(), 'tell %d != expected 4'%f.tell()
    mainchunklen = readint(f)
    assert 'WAVE' == f.read(4), 'NOT WAVE'
    while f.tell() + 4 < mainchunklen:
        chunk = readwavechunk(f)
        #print chunk