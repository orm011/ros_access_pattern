#! /usr/bin/env python2.7

import sys

import numpy as np
import matplotlib.pyplot as pl
from matplotlib import collections  as mc
from collections import namedtuple

FsReadOp = namedtuple('FsReadOp', 'cmdpid timestamp size_requested offset')

# expected format:
#
#vfs_read
#Tracing kprobe vfs_read. Ctrl-C to end.
# cat-3967  [007] d... 81183.379444: vfs_read: (vfs_read+0x0/0x140) inum=0x760f7e size_requested=0x20000 offset=0x0
# cat-3967  [007] d... 81183.379489: vfs_read: (vfs_read+0x0/0x140) inum=0x760f7e size_requested=0x20000 offset=0x7aa
#
# Ending tracing...
def parse_line(line):
    parts = [x for x in line.strip().split(' ') if x != '']
    kvs = {'cmdpid':parts[0], 'timestamp':float(parts[3][:-1])}
    for p in parts[4:]:
        if p.startswith('size_requested='):
            kvs['size_requested'] = int(p.split('=')[1], base=16)
        elif p.startswith('offset='):
            kvs['offset'] = int(p.split('=')[1], base=16)

    return FsReadOp(**kvs)

def show_access_pattern(f, note):
    initial_timestamp = None
    counter=0

    initial_timestamp == None
    lines = []
    start_offsets = []
    start_times = []
    total = 0
    max_offset = 0
    min_offset = 9999999999999999

    bad_count = 0
    for l in f:
        try:
            rop = parse_line(l)
        except:
            bad_count += 1
            continue

        if initial_timestamp == None:
            initial_timestamp = rop.timestamp
        timestamp = rop.timestamp - initial_timestamp

        lines.append([(timestamp, rop.offset/1024/1024), (timestamp, (rop.offset + rop.size_requested)/1024/1024)])
        start_offsets.append(rop.offset/1024/1024)
        start_times.append(timestamp)
        total += rop.size_requested
        max_offset = max(max_offset, rop.offset)
        min_offset = min(min_offset, rop.offset)

    print("skipped lines: %d\ntotal read() calls: %d\nduration (s): %.1f\ntotal bytes requested (MB): %d\n"
          "min_offset (B): %d\nmax_offset (MB): %d" % (bad_count, len(lines), start_times[-1], total/1024/1024, min_offset, max_offset/1024/1024))
    lc = mc.LineCollection(lines, linewidths=5, label='bytes requested')
    fig, ax = pl.subplots()
    ax.add_collection(lc)
    ax.scatter(start_times, start_offsets, color='r', marker='x', label='start offsets')
    ax.autoscale()
    ax.margins(0.1)
    ax.set_title('Access pattern plot for "%s"\nRed x marks start of read.\nBlue bar marks extent of read' % note)
    ax.set_ylabel("file offset (MB)")
    ax.set_xlabel("time elapsed (s)")
    return (fig,ax)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        f = sys.stdin
        nm = 'stdin'
    else:
        f = open(sys.argv[1], 'r')
        nm = sys.argv[1]

    # skip first two non-data lines.
    (fig, ax) = show_access_pattern(f,nm)
    pl.savefig('access_pattern_%s.png' % nm)
