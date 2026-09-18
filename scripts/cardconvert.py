#!/usr/bin/env python3
"""Mac-native replacement for Campbell PC400 CardConvert: TOB1 -> TOA5.

Validated byte-exact against logger-produced TOA5 over 1.6M values.
Faithful conversion: no timestamp reconstruction, counter passed through as-is.
"""
import os, sys, time, argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import tob

def convert(args):
    src, dst = args
    try:
        a, lines = tob.read_tob1(src)
        names = lines[1]
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        hdr = ['"TOA5"' + lines[0][6:], names, lines[2], lines[3]]
        fmt = tob.csi7
        cols = a.dtype.names
        isflt = [np.issubdtype(a.dtype[c], np.floating) for c in cols]
        tmp = dst + '.part'
        with open(tmp, 'w', newline='', encoding='utf-8') as f:
            f.write('\r\n'.join(hdr) + '\r\n')
            arrs = [a[c] for c in cols]
            out = []
            for i in range(len(a)):
                out.append(','.join(fmt(arrs[j][i]) if isflt[j] else str(arrs[j][i])
                                    for j in range(len(cols))))
                if len(out) >= 50000:
                    f.write('\r\n'.join(out) + '\r\n'); out = []
            if out:
                f.write('\r\n'.join(out) + '\r\n')
        os.replace(tmp, dst)
        return (src, len(a), os.path.getsize(dst), None)
    except Exception as e:
        return (src, 0, 0, f'{type(e).__name__}: {e}')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root'); ap.add_argument('outroot')
    ap.add_argument('-j', type=int, default=max(1, os.cpu_count() - 2))
    A = ap.parse_args()
    jobs = []
    for dp, _, fs in os.walk(A.root):
        for fn in sorted(fs):
            if not fn.lower().endswith('.dat'): continue
            p = os.path.join(dp, fn)
            with open(p, 'rb') as fh:
                if fh.read(6)[1:5] != b'TOB1': continue
            rel = os.path.relpath(p, A.root)
            jobs.append((p, os.path.join(A.outroot, rel[:-4] + '_TOA5.dat')))
    jobs = [j for j in jobs if not os.path.exists(j[1])]
    print(f'{len(jobs)} TOB1 files to convert on {A.j} workers', flush=True)
    t0 = time.time(); done = recs = nbytes = 0; errs = []
    with ProcessPoolExecutor(max_workers=A.j) as ex:
        futs = [ex.submit(convert, j) for j in jobs]
        for fu in as_completed(futs):
            src, n, sz, err = fu.result(); done += 1
            if err: errs.append((src, err))
            recs += n; nbytes += sz
            if done % 25 == 0 or done == len(jobs):
                el = time.time() - t0
                print(f'  {done}/{len(jobs)}  {recs:,} rec  {nbytes/1e9:.2f} GB  '
                      f'{el/60:.1f} min  eta {(el/done*(len(jobs)-done))/60:.1f} min', flush=True)
    print(f'\nDONE {done - len(errs)} ok, {len(errs)} failed, {recs:,} records, {nbytes/1e9:.2f} GB')
    for s, e in errs[:20]: print('  FAIL', s, e)

if __name__ == '__main__':
    main()
