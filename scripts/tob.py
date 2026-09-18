"""Campbell TOB1 reader. Mixed endianness: CSI integer types big-endian,
IEEE floats little-endian (CR1000X native)."""
import numpy as np

# (numpy code, is_bigendian)
TYPES = {
    'UINT1':('u1',True), 'UINT2':('u2',True), 'UINT4':('u4',True),
    'INT1':('i1',True),  'INT2':('i2',True),  'INT4':('i4',True),
    'LONG':('i4',True),  'ULONG':('u4',True), 'BOOL':('u1',True),
    'IEEE4':('f4',False),'IEEE4L':('f4',False),'IEEE4B':('f4',True),
    'IEEE8':('f8',False),'IEEE8L':('f8',False),'IEEE8B':('f8',True),
}

def read_header(path, nlines=5):
    with open(path,'rb') as f:
        blob = f.read(65536)
    lines, off = [], 0
    for _ in range(nlines):
        i = blob.index(b'\r\n', off)
        lines.append(blob[off:i].decode('utf-8', 'replace'))
        off = i + 2
    return lines, off

def _split(line):
    return [x.strip('"') for x in line.split(',')]

def read_tob1(path):
    lines, off = read_header(path, 5)
    assert _split(lines[0])[0] == 'TOB1', f'not TOB1: {path}'
    names, types = _split(lines[1]), _split(lines[4])
    fields = []
    for n, t in zip(names, types):
        base = t.split('(')[0]
        if base not in TYPES:
            raise ValueError(f'unhandled type {t} in {path}')
        code, be = TYPES[base]
        fields.append((n, ('>' if be else '<') + code))
    dt = np.dtype(fields)
    nbytes = os_size(path) - off
    if nbytes % dt.itemsize:
        raise ValueError(f'{path}: body {nbytes} not a multiple of record {dt.itemsize}')
    return np.fromfile(path, dtype=dt, offset=off), lines

def os_size(p):
    import os; return os.path.getsize(p)

from decimal import Decimal, ROUND_HALF_UP

def csi7(x):
    """Render a float the way Campbell TOA5 does: 7 significant digits,
    halves rounded away from zero, E-notation below 1e-4."""
    import numpy as _np
    xf = float(_np.float32(x))
    if xf != xf: return 'NAN'
    if xf in (float('inf'), float('-inf')): return 'INF' if xf > 0 else '-INF'
    if xf == 0: return '0'
    d = Decimal(xf)
    q = d.quantize(Decimal(1).scaleb(d.adjusted() - 6), rounding=ROUND_HALF_UP)
    if abs(xf) < 1e-4:
        sign = '-' if q < 0 else ''
        digits = format(abs(q), 'f').replace('.', '').lstrip('0')
        digits = digits.rstrip('0') or '0'
        mant = digits[0] + ('.' + digits[1:] if len(digits) > 1 else '')
        return f'{sign}{mant}E{abs(q).adjusted():+03d}'
    s = format(q, 'f')
    return s.rstrip('0').rstrip('.') if '.' in s else s
