# Dynamic Linking (`dyld`) & Runtime Linking Reference

This reference details the mechanics of Apple's dynamic linker (`dyld`), symbol rebasing/binding pipelines, modern chained fixups, the dyld shared cache, and library interposing, derived from Jonathan Levin's *Mac OS X and iOS Internals: Volume 1 (User Mode)*.

---

## 1. Dynamic Loader Lifecycle

When a process is launched via `posix_spawn` or `execve`:
1. **Kernel Image Mapping**: The Darwin kernel (`xnu`) maps the main executable into memory, maps the dynamic linker declared in `LC_LOAD_DYLINKER` (`/usr/lib/dyld`), sets up the initial stack (registers, arguments, environment, mach bootstrap port), and transfers execution to `dyld`'s entry point (`_dyld_start`).
2. **Environment Sanitization**: `dyld` inspects process flags. If the binary is suid/sgid or has Hardened Runtime / restricted entitlements, `dyld` purges all dangerous environment variables (`DYLD_INSERT_LIBRARIES`, `DYLD_LIBRARY_PATH`, `DYLD_FRAMEWORK_PATH`).
3. **Dependency Graph Resolution**: `dyld` recursively parses `LC_LOAD_DYLIB`, `LC_LOAD_WEAK_DYLIB`, and `LC_RPATH` commands, loading required libraries into the address space.
4. **Rebasing (ASLR Slide)**: Rebase opcodes adjust internal pointers within `__DATA` to account for the randomized load address:
   $$\text{Actual Address} = \text{Compiled VM Address} + \text{ASLR Slide}$$
5. **Symbol Binding**: `dyld` resolves external function/data references:
   - **Non-lazy binding**: Evaluated immediately at startup (e.g. pointers in `__DATA_CONST,__got`).
   - **Weak binding**: Deduplicates weak symbols across multiple libraries (e.g., C++ inline templates).
   - **Lazy binding**: Postponed until first invocation via `__TEXT,__stub_helper` and `__DATA,__la_symbol_ptr`.
6. **Module Initialization**: Executes static constructors declared in `LC_ROUTINES_64` or sections marked with `S_MOD_INIT_FUNC_POINTERS` (`__mod_init_func`).
7. **Main Transfer**: Calls binary entry point specified in `LC_MAIN`.

---

## 2. Rebase and Bind Opcodes (`LC_DYLD_INFO_ONLY`)

In classic Mach-O binaries, `LC_DYLD_INFO_ONLY` points to byte streams encoding state-machine opcodes:

### Rebase Stream
Encodes locations inside `__DATA` that must be incremented by the ASLR slide value:
- `REBASE_OPCODE_SET_TYPE_IMM`
- `REBASE_OPCODE_SET_SEGMENT_AND_OFFSET_ULEB`
- `REBASE_OPCODE_DO_REBASE_IMM_TIMES`

### Binding Stream
Encodes dynamic symbol lookups:
- `BIND_OPCODE_SET_DYLIB_ORDINAL_IMM`: Index into `LC_LOAD_DYLIB` array (ordinal 1 = first dylib).
- `BIND_OPCODE_SET_SYMBOL_TRAILING_FLAGS_IMM`: Target symbol string name.
- `BIND_OPCODE_SET_TYPE_IMM`: Pointer type (pointer, absolute, text relocation).
- `BIND_OPCODE_SET_SEGMENT_AND_OFFSET_ULEB`: Pointer target memory location.
- `BIND_OPCODE_DO_BIND`: Write resolved address to location.

### Inspecting Binding with CLI
```bash
# Display rebase operations
dyld_info -rebase <binary>

# Display non-lazy and lazy binding targets
dyld_info -bind <binary>
dyld_info -lazy_bind <binary>

# Dump export trie symbols
dyld_info -export <binary>
```

---

## 3. Modern Chained Fixups (`LC_DYLD_CHAINED_FIXUPS`)

Starting with macOS 12 (Monterey) and iOS 15, Apple transitioned from opcode streams to **Chained Fixups**:
- Combines rebasing and binding into contiguous linked lists embedded directly within the memory locations in `__DATA`.
- Each pointer either stores a rebase offset or a bind import index, plus a 16-bit offset to the *next* pointer in the chain within the memory page.
- Dramatically accelerates launch time and reduces binary size.

### Chained Fixups Structure
`LC_DYLD_CHAINED_FIXUPS` points to `dyld_chained_fixups_header`:
```c
struct dyld_chained_fixups_header {
    uint32_t fixups_version;    /* 0 */
    uint32_t starts_offset;     /* Offset to dyld_chained_starts_in_image */
    uint32_t imports_offset;    /* Offset to imports table */
    uint32_t symbols_offset;    /* Offset to symbol strings */
    uint32_t imports_count;     /* Number of imported symbols */
    uint32_t imports_format;    /* Format variant */
    uint32_t symbols_format;
};
```

### Inspecting Chained Fixups
```bash
# View chained fixups using modern dyld_info
dyld_info -fixups <binary>
```

---

## 4. Dyld Shared Cache (DSC)

On modern Apple OSes, system dynamic libraries and frameworks (e.g., `libSystem.B.dylib`, `Foundation.framework`) are **not** present as standalone files in `/usr/lib` or `/System/Library/Frameworks`.
Instead, they are merged into a single multi-gigabyte monolithic cache file:
- **Location**: `/System/Library/dyld/dyld_shared_cache_<arch>`
- All system libraries share optimized address spaces with eliminated cross-library symbol resolution latency and deduplicated text/data.

### Shared Cache Extraction
To disassemble or reverse-engineer a system dylib on modern macOS:
```bash
# List dylibs inside the local system shared cache
dyld_info -shared_cache_dylibs /System/Library/dyld/dyld_shared_cache_arm64e

# Extract individual dylib using Xcode developer tools / dsc_extractor
# (Compile standard Apple dsc_extractor.cpp or use jtool2)
jtool2 -extract <library_path> /System/Library/dyld/dyld_shared_cache_arm64e
```

---

## 5. Dynamic Library Interposing

Mach-O supports clean function hooking without inline assembly patching through `dyld` interposing:
- Works when a library is injected via `DYLD_INSERT_LIBRARIES`.
- Declares a replacement table in a special `__interpose` section inside `__DATA`.

### Interposing Schema
```c
#include <stdio.h>
#include <unistd.h>

// Definition of the interpose structure
typedef struct interpose_s {
    const void *replacement;
    const void *original;
} interpose_t;

// Replacement function
ssize_t my_write(int fd, const void *buf, size_t count) {
    printf("[Hook] write() intercepted for fd=%d\n", fd);
    return write(fd, buf, count); // Calls original
}

// Register hook in __DATA, __interpose section
__attribute__((used, section("__DATA,__interpose")))
static const interpose_t interposers[] = {
    { (const void *)my_write, (const void *)write }
};
```

### Constraints & Caveats
- Blocked on binaries with `com.apple.security.cs.allow-dyld-environment-variables` unset under Hardened Runtime.
- Blocked on binaries signed with restricted entitlements or running under System Integrity Protection (SIP) without developer root override.
