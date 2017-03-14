# tools
assorted tools/useful snippets

# trace_reads.bash: 
  like `strace -e trace=read`, but it also shows you the (normally implicit) file offset being read at.

```bash
$ strace -f -e trace=file,read -o strace.out sed 's/test/foo/g' trace_reads.bash
31859 open("trace_reads.bash", O_RDONLY) = 3
31859 read(3, "#!/usr/bin/env bash\n#\nusage=\"$(b"..., 4096) = 1962
31859 read(3, "", 4096)                 = 0
```
vs

``` bash
$sudo ./trace_reads.bash ./trace_reads.bash  # and concurrently: sed 's/test/foo/g' trace_reads.bash
vfs_read
Tracing kprobe vfs_read. Ctrl-C to end.
             sed-757   [008] d... 80128.962194: vfs_read: (vfs_read+0x0/0x140) ...
                  inum=0x760f7e size_requested=0x1000 **offset=0x0**
             sed-757   [008] d... 80128.962511: vfs_read: (vfs_read+0x0/0x140) ...
                  inum=0x760f7e size_requested=0x1000 **offset=0x7aa**
```
# plot_reads.py: 
  takes trace_reads.bash output and plots the reads:
  
usage:
`sudo ./trace_reads.bash /my/file > test.tmp`

meanwhile, a process accesses the file:
`python test_reads.py /my/file 

we can use plot_reads.py to plot the collected traces:
```
$ ./plot_reads.py test.tmp 
skipped lines: 4
total read() calls: 106
duration (s): 19.0
total bytes requested (MB): 33417
min_offset (B): 0
max_offset (MB): 30170
$ eog access_pattern_test.tmp.png
```
![access_pattern_test.tmp.png](https://raw.githubusercontent.com/orm011/tools/master/access_pattern_test.tmp.png "")
