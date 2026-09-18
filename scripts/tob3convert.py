#!/usr/bin/env python3
"""TOB3 -> TOA5 batch converter. mode='all' recovers live records that
CardConvert discards when it hits a corrupt frame or a ring-buffer wrap."""
import os, sys, glob, datetime, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tob3
from tob import csi7
EPOCH = datetime.datetime(1990, 1, 1)

def render(s, ss, rn, vals, fields, subres):
    t = EPOCH + datetime.timedelta(seconds=s)
    frac = ss * 1e-4 if subres == 'Sec100Usec' else ss * 1e-6
    ts = ((t + datetime.timedelta(seconds=frac)).strftime('%Y-%m-%d %H:%M:%S.%f').rstrip('0')
          if frac else t.strftime('%Y-%m-%d %H:%M:%S'))
    out = [f'"{ts}"', str(rn)]
    for (n, ty, fo, w), v in zip(fields, vals):
        if ty == 'ASCII': out.append(f'"{v}"')
        elif isinstance(v, float): out.append('"NAN"' if v != v else csi7(v))
        else: out.append(str(v))
    return ','.join(out)

def convert(src, dst, mode='all'):
    hdr, fields, recs = tob3.read_tob3(src, mode=mode)
    head = ['"TOA5",' + ','.join(f'"{x}"' for x in hdr[0][1:7]) + f',"{hdr[1][0]}"',
            '"TIMESTAMP","RECORD",' + ','.join(f'"{x}"' for x in hdr[2]),
            '"TS","RN",' + ','.join(f'"{x}"' for x in hdr[3]),
            '"",""," + "'.join([]) or '"","",' + ','.join(f'"{x}"' for x in hdr[4])]
    with open(dst, 'w', newline='', encoding='utf-8') as f:
        f.write('\r\n'.join(head) + '\r\n')
        for s, ss, rn, v in recs:
            f.write(render(s, ss, rn, v, fields, hdr[1][5]) + '\r\n')
    return len(recs)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('src'); ap.add_argument('out')
    ap.add_argument('--mode', default='all', choices=['all', 'cardconvert'])
    A = ap.parse_args()
    os.makedirs(A.out, exist_ok=True)
    tot = n = 0; fails = []
    for p in sorted(glob.glob(os.path.join(A.src, '*.dat'))):
        d = os.path.join(A.out, 'TOA5_' + os.path.basename(p))
        try:
            c = convert(p, d, A.mode); tot += c; n += 1
            if c == 0: fails.append((os.path.basename(p), 'zero records'))
        except Exception as e:
            fails.append((os.path.basename(p), f'{type(e).__name__}: {e}'))
    print(f'{n} files converted, {tot:,} records')
    for f, e in fails: print('  ISSUE', f, e)
