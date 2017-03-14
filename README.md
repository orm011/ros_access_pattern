# tools
assorted tools/useful snippets

eg. 
$ strace -f -e trace=file,read -o strace.out sed 's/test/foo/g' trace_reads.bash
31859 open("trace_reads.bash", O_RDONLY) = 3
31859 read(3, "#!/usr/bin/env bash\n#\nusage=\"$(b"..., 4096) = 1962
31859 read(3, "", 4096)                 = 0

vs

$sudo ./trace_reads.bash ./trace_reads.bash  # and concurrently: sed 's/test/foo/g' trace_reads.bash
vfs_read
Tracing kprobe vfs_read. Ctrl-C to end.
             sed-757   [008] d... 80128.962194: vfs_read: (vfs_read+0x0/0x140) inum=0x760f7e size_requested=0x1000 offset=0x0
             sed-757   [008] d... 80128.962511: vfs_read: (vfs_read+0x0/0x140) inum=0x760f7e size_requested=0x1000 offset=0x7aa
