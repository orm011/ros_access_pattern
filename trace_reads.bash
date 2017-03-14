#!/usr/bin/env bash
#
usage="$(basename "$0") [-h] file -- kprobe to record read() offsets and read lengths to a specific file. eg, to understand application specific access patterns."
while getopts ':h' option; do
    case "$option" in
        h) echo "$usage"
           exit
           ;;
        :) printf "missing argument" >&2
           echo "$usage" >&2
           exit 1
           ;;
        \?) printf "illegal option: -%s\n" "$OPTARG" >&2
            echo "$usage" >&2
            exit 1
            ;;
    esac
done
shift $((OPTIND - 1))

# arg check
if [  $# -eq 0 ]
then
    printf "missing argument\n" >&2 && echo "$usage" >&2 && exit 1
fi

set -e

inum=$(stat -c '%i' $1)
arch="x86_64"
supported_version="4.8.0-28-generic"

# test if assumptions still hold 
test $(uname -m) = $arch || (echo "Warning: x86-64 assumed" && exit 1)
test $(uname -r) = $supported_version  || (echo "Warning: this kprobe was only tested with $supported_version"; exit 1)
test $(grep 'CONFIG_FS_POSIX_ACL=' /boot/config-$(uname -r)) = 'CONFIG_FS_POSIX_ACL=y' || (echo "Warning: mem offsets are probably wrong"; exit 1)
test $(grep 'CONFIG_SECURITY=' /boot/config-$(uname -r)) = 'CONFIG_SECURITY=y' || (echo "Warning: mem offsets are probably wrong"; exit 1)

# 
# vfs_read(struct file *file, char __user *buf, size_t count, loff_t *pos)
#                       RDI,               RSI,        RDX,           RCX
# we want to read: file->f_inode->i_inum, count, and *pos
f_inode=32
i_inum=64
kprobe "p:vfs_read inum=+$i_inum(+$f_inode(%di)):u64 size_requested=%dx:u64 offset=+0(%cx):u64" "inum == $inum"

# references:
# vfs_read signature @ http://lxr.free-electrons.com/source/fs/read_write.c?v=4.8#L460
# struct file @ http://lxr.free-electrons.com/source/include/linux/fs.h?v=4.8#L876
# struct inode @ http://lxr.free-electrons.com/source/include/linux/fs.h?v=4.8#L600
# x64 abi: https://en.wikipedia.org/wiki/X86_calling_conventions#List_of_x86_calling_conventions
