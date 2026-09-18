"""Campbell TOB3 reader (ring-buffered, frame-per-record layout).

Record layout, verified against CardConvert output:
  bytes  0..3    uint32 LE  seconds since 1990-01-01
  bytes  4..7    uint32 LE  subseconds (units per header 'frame time resolution')
  bytes  8..11   uint32 LE  record number
  bytes 12..     field data, big-endian per the types header line
  last 4 bytes   validation footer - constant for live records, garbage for stale slots

Stride (total record size) is header line 2, field 3.
"""
import struct, datetime, collections
import numpy as np

EPOCH = datetime.datetime(1990, 1, 1)
SZ = {'IEEE4':4,'IEEE4B':4,'IEEE4L':4,'IEEE8':8,'FP2':2,'UINT1':1,'UINT2':2,
      'UINT4':4,'INT2':2,'INT4':4,'LONG':4,'ULONG':4,'BOOL':1,'NSEC':8,'SecNano':8}

def _fp2(raw):
    """Campbell 2-byte float: sign, 2-bit decimal exponent, 13-bit mantissa.
    Special encodings: 0x1FFF and 0x9FFE are NaN; 0x1FFE is +INF."""
    man = raw & 0x1FFF
    if raw == 0x9FFE or man == 0x1FFF: return float('nan')
    if man == 0x1FFE: return float('-inf') if raw & 0x8000 else float('inf')
    v = man / (10 ** ((raw >> 13) & 0x03))
    return -v if raw & 0x8000 else v

def read_header(path):
    with open(path, 'rb') as f: blob = f.read(1 << 16)
    lines, off = [], 0
    for _ in range(6):
        i = blob.index(b'\r\n', off)
        lines.append(blob[off:i].decode('utf-8', 'replace'))
        off = i + 2
    return [[x.strip('"').strip() for x in l.split(',')] for l in lines], off

def field_defs(hdr):
    names, types = hdr[2], hdr[5]
    out, off = [], 0
    for n, t in zip(names, types):
        base = t.split('(')[0].strip('"')
        if base.startswith('ASCII'):
            w = int(t.split('(')[1].rstrip(')"')); out.append((n,'ASCII',off,w)); off += w
        else:
            if base not in SZ: raise ValueError('unhandled type %r' % t)
            out.append((n, base, off, SZ[base])); off += SZ[base]
    return out, off

def _interval_secs(txt):
    """Table interval from header line 2, e.g. '10 MIN' -> 600. 0 = event-driven."""
    try: n, unit = txt.split()
    except ValueError: return 0
    mult = {'USEC':1e-6,'MSEC':1e-3,'SEC':1,'MIN':60,'HR':3600,'HOUR':3600,'DAY':86400}
    return float(n) * mult.get(unit.upper(), 0)

def read_tob3(path, mode='cardconvert'):
    hdr, hlen = read_header(path)
    stride = int(hdr[1][2])
    fields, datalen = field_defs(hdr)
    b = open(path, 'rb').read()
    nslot = (len(b) - hlen) // stride

    # Slot metadata. The footer is big-endian (flags << 16) | validation_stamp; live records
    # share a stamp AND run with consecutive record numbers. Stale ring-buffer
    # slots may reuse an old stamp, so the stamp alone is not sufficient.
    meta = []
    for i in range(nslot):
        o = hlen + i*stride
        s, ss, rn = struct.unpack('<3I', b[o:o+12])
        foot = struct.unpack('>I', b[o+stride-4:o+stride])[0]
        meta.append((s, ss, rn, foot & 0xFFFF))

    # Plausible time window, centred on the file's creation time: a card written
    # in 2025-26 cannot hold records from 1990 or 2050. Without this a 16-bit stamp plus a
    # 2-slot run is far too easy for random stale bytes to satisfy.
    try:
        created = datetime.datetime.strptime(hdr[0][7], '%Y-%m-%d %H:%M:%S')
        c = (created - EPOCH).total_seconds()
        t_lo, t_hi = c - 400*86400, c + 400*86400
    except Exception:
        t_lo, t_hi = 0, 2_000_000_000
    interval = _interval_secs(hdr[1][1])

    def ok(i):
        s, ss = meta[i][0], meta[i][1]
        if not (t_lo <= s <= t_hi): return False
        # A fixed-interval table records on the second; a non-zero subsecond
        # field means the slot is stale bytes, not a live record.
        if interval > 0 and ss != 0: return False
        return True

    # Maximal runs of consecutive slots sharing a validation stamp, with record
    # numbers incrementing by 1 AND timestamps advancing by the table interval
    # (monotonically, for event-driven tables).
    runs, i = [], 0
    while i < nslot:
        st = meta[i][3]
        if not ok(i):
            i += 1; continue
        j = i + 1
        while j < nslot:
            s2, ss2, rn2, st2 = meta[j]
            if st2 != st or rn2 != meta[j-1][2] + 1 or not ok(j): break
            dt = s2 - meta[j-1][0]
            if interval > 0:
                if dt != interval: break
            elif dt < 0: break
            j += 1
        runs.append((i, j))
        i = max(j, i + 1)

    if mode == 'cardconvert':
        # CardConvert reads sequentially and stops at the first invalid frame,
        # discarding any live data beyond it.
        slots = list(range(*runs[0])) if runs and runs[0][0] == 0 else []
    elif mode == 'all':
        # Recover every live run, ordered by record number.
        slots = sorted((i for a, z in runs for i in range(a, z)),
                       key=lambda i: (meta[i][2], meta[i][0]))
    else:
        raise ValueError('mode must be "cardconvert" or "all"')

    recs = []
    for i in slots:
        o = hlen + i*stride
        s, ss, rn = struct.unpack('<3I', b[o:o+12])
        vals = []
        for n, t, fo, w in fields:
            q = o + 12 + fo
            if   t in ('IEEE4','IEEE4B'): vals.append(struct.unpack('>f', b[q:q+4])[0])
            elif t == 'IEEE4L':           vals.append(struct.unpack('<f', b[q:q+4])[0])
            elif t == 'IEEE8':            vals.append(struct.unpack('>d', b[q:q+8])[0])
            elif t == 'FP2':              vals.append(_fp2(struct.unpack('>H', b[q:q+2])[0]))
            elif t == 'UINT2':            vals.append(struct.unpack('>H', b[q:q+2])[0])
            elif t == 'UINT4':            vals.append(struct.unpack('>I', b[q:q+4])[0])
            elif t == 'UINT1':            vals.append(b[q])
            elif t == 'BOOL':             vals.append(b[q])
            elif t == 'INT2':             vals.append(struct.unpack('>h', b[q:q+2])[0])
            elif t in ('INT4','LONG'):    vals.append(struct.unpack('>i', b[q:q+4])[0])
            elif t == 'ASCII':            vals.append(b[q:q+w].split(b'\0')[0].decode('latin-1'))
            else: raise ValueError(t)
        recs.append((s, ss, rn, vals))
    return hdr, fields, recs
