# Mach-O Binary Anatomy & Load Commands Reference

This reference details the file format specifications, header layouts, load commands, and segment/section conventions for macOS and iOS Mach-O binaries, derived from Jonathan Levin's *Mac OS X and iOS Internals: Volume 1 (User Mode)* and Darwin kernel (`sys/loader.h`) definitions.

---

## 1. Universal (Fat) Binaries

Universal binaries package multiple architecture-specific Mach-O slices into a single file container.

### Header Layout (`fat_header` & `fat_arch`)
Located at file offset `0`:
```c
struct fat_header {
    uint32_t magic;     /* FAT_MAGIC (0xcafebabe) or FAT_MAGIC_64 (0xcafebabf) */
    uint32_t nfat_arch; /* Number of architecture slices following */
};

struct fat_arch {
    cpu_type_t    cputype;    /* CPU specifier (e.g., CPU_TYPE_ARM64, CPU_TYPE_X86_64) */
    cpu_subtype_t cpusubtype; /* Machine-specific subtype (e.g., ARM64_ALL, ARM64_V8) */
    uint32_t      offset;     /* File offset to slice start */
    uint32_t      size;       /* Size of slice in bytes */
    uint32_t      align;      /* Alignment power of 2 (e.g., 14 -> 16KB alignment) */
};
```

### Essential CLI Operations
- **Inspect slices**: `lipo -info <binary>` or `otool -v -f <binary>`
- **Extract slice**: `lipo <binary> -extract arm64 -output <binary>_arm64`
- **Thin slice**: `lipo <binary> -thin arm64e -output <binary>_arm64e`

---

## 2. Mach-O 64-bit Header (`mach_header_64`)

Each architectural slice starts with a `mach_header_64`:

```c
struct mach_header_64 {
    uint32_t magic;       /* MH_MAGIC_64 (0xfeedfacf) */
    cpu_type_t cputype;   /* CPU_TYPE_X86_64 (0x01000007), CPU_TYPE_ARM64 (0x0100000c) */
    cpu_subtype_t cpusubtype; /* Capability flags (e.g., PAC flags in ARM64E: 0x80000000) */
    uint32_t filetype;    /* MH_EXECUTE (2), MH_DYLIB (6), MH_BUNDLE (8), MH_DSYM (10) */
    uint32_t ncmds;       /* Number of load commands */
    uint32_t sizeofcmds;  /* Total byte size of all load commands */
    uint32_t flags;       /* Runtime execution flags */
    uint32_t reserved;    /* 64-bit reserved padding */
};
```

### Critical Header Flags (`flags`)
- `MH_PIE` (`0x200000`): Position Independent Executable; kernel randomizes base address (ASLR).
- `MH_TWOLEVEL` (`0x80`): Two-level symbol namespace (symbol name bound to specific dylib).
- `MH_BINDATLOAD` (`0x08`): Prevents lazy symbol binding; dynamic loader resolves all symbols at startup.
- `MH_ALLOW_STACK_EXECUTION` (`0x20000`): Disables non-executable stack (NX stack).
- `MH_NO_HEAP_EXECUTION` (`0x1000000`): Enforces NX heap protection.

---

## 3. Load Commands (`load_command`)

Load commands directly follow `mach_header_64`. Every command starts with an identical 8-byte prefix:
```c
struct load_command {
    uint32_t cmd;     /* Command identifier constant */
    uint32_t cmdsize; /* Total byte length of this command record */
};
```

### Key Load Commands Summary

| Command (`cmd`) | Numeric Value | Purpose |
|:----------------|:--------------|:--------|
| `LC_SEGMENT_64` | `0x19` | Maps file slice range into memory address space |
| `LC_LOAD_DYLINKER`| `0x0e` | Specifies path of dynamic loader (`/usr/lib/dyld`) |
| `LC_MAIN` | `0x80000028` | Declares binary entrypoint offset and stack reservation |
| `LC_LOAD_DYLIB` | `0x0c` | Declares required dynamic library dependency |
| `LC_LOAD_WEAK_DYLIB`| `0x80000018` | Optional dylib; unresolved symbols resolve to NULL |
| `LC_RPATH` | `0x8000001c` | Adds search directory for `@rpath`-prefixed dylibs |
| `LC_CODE_SIGNATURE`| `0x1d` | File offset and size of embedded code signature blob |
| `LC_DYLD_INFO_ONLY`| `0x80000022` | Compressed rebase, bind, weak, lazy, and export tables |
| `LC_DYLD_EXPORTS_TRIE`| `0x80000033` | Trie-structured export symbol table (modern macOS/iOS) |
| `LC_DYLD_CHAINED_FIXUPS`| `0x80000034`| Modern chained pointer fixup table (macOS 12+ / iOS 15+) |
| `LC_SYMTAB` | `0x02` | Symbol table (`nlist_64`) and string table offset |
| `LC_DYSYMTAB` | `0x0b` | Dynamic symbol table indexing tables |
| `LC_ENCRYPTION_INFO_64`| `0x2c` | FairPlay App Store DRM encryption bounds |
| `LC_BUILD_VERSION`| `0x32` | Minimum OS version, SDK version, and build tools |

---

## 4. Segment & Section Layout

### Segment Command (`segment_command_64`)
```c
struct segment_command_64 {
    uint32_t cmd;         /* LC_SEGMENT_64 */
    uint32_t cmdsize;
    char     segname[16]; /* __PAGEZERO, __TEXT, __DATA_CONST, __DATA, __LINKEDIT */
    uint64_t vmaddr;      /* Virtual memory start address */
    uint64_t vmsize;      /* Virtual memory size (page-aligned) */
    uint64_t fileoff;     /* Offset in slice */
    uint64_t filesize;    /* Size on disk */
    vm_prot_t maxprot;    /* Maximum VM protection permissions */
    vm_prot_t initprot;   /* Initial VM protection permissions (e.g. r-x) */
    uint32_t nsects;      /* Number of section records following */
    uint32_t flags;
};
```

### Standard Segments

1. **`__PAGEZERO`**:
   - `vmaddr = 0x0`, `vmsize = 0x100000000` (4GB on 64-bit), `initprot = 0` (no access).
   - Catches null-pointer dereferences in user space.
2. **`__TEXT`**:
   - Read-only + executable (`r-x`).
   - Contains machine instructions, read-only strings, and runtime structures.
3. **`__DATA_CONST`**:
   - Initialized read-write during dynamic linking, protected read-only before user code runs.
   - Contains constant Objective-C metadata and GOT (Global Offset Table).
4. **`__DATA`**:
   - Read-write non-executable (`rw-`).
   - Contains global variables, static variables, non-lazy symbol pointers.
5. **`__LINKEDIT`**:
   - Read-only data used by `dyld`: export trie, symbol table, string table, code signature.

### Critical Sections within Segments

| Section Name | Segment | Contents |
|:-------------|:--------|:---------|
| `__text` | `__TEXT` | Compiled machine instructions |
| `__stubs` | `__TEXT` | Dynamic symbol calling stubs (trampolines) |
| `__stub_helper`| `__TEXT` | Helper functions invoked to resolve lazy symbols |
| `__cstring` | `__TEXT` | Literal null-terminated C-strings |
| `__const` | `__TEXT` | Constant data |
| `__unwind_info`| `__TEXT`| Compact unwinding tables for exception handling |
| `__got` | `__DATA_CONST` | Non-lazy Global Offset Table pointers |
| `__la_symbol_ptr`| `__DATA` | Lazy symbol pointer table (populated by `dyld`) |
| `__nl_symbol_ptr`| `__DATA` | Non-lazy symbol pointer table |
| `__bss` | `__DATA` | Uninitialized global variables |
| `__objc_classlist`| `__DATA_CONST`| Pointers to Objective-C class structures |
| `__objc_methname`| `__TEXT` | Selector string names |
| `__objc_data` | `__DATA` | Objective-C class object instances |

---

## 5. Inspection Tooling Recipes

### CLI Commands
```bash
# Display Mach-O header
otool -v -h <binary>

# List all load commands
otool -v -l <binary>

# List all segments and sections with offsets
size -m -l -x <binary>

# Dump disassembled text section
otool -v -t <binary>

# Dump symbol table (local and external symbols)
nm -m -p <binary>

# View shared library dependencies
otool -L <binary>
```

---

## 6. Binary Overlay & Tampering Detection

In a well-formed Mach-O executable, the entire file content on disk is accounted for by the segment commands. The final segment on disk is almost universally `__LINKEDIT`:
$$\text{Expected End Offset} = \text{fileoff}(\text{\_\_LINKEDIT}) + \text{filesize}(\text{\_\_LINKEDIT})$$

### Detecting Viral Prependers & Append Overlays
Malicious implants and viral file infectors (e.g. OSX.EvilQuest/ThiefQuest) inject code by either:
1. **Appending Overlay Data**: Appending raw encrypted payloads or metadata markers beyond `__LINKEDIT`. If `ActualFileSize > ExpectedEndOffset`, trailing overlay data exists.
2. **Prepending Executable Stubs**: Writing an initial loader Mach-O at offset 0, concatenating the host binary at a fixed offset, and appending a 32-byte trailer containing the original host size and infection magic.

```bash
# Automated verification of Mach-O boundary integrity
python3 -c '
import sys, struct
with open(sys.argv[1], "rb") as f:
    data = f.read()
# Parse mach_header_64
magic, cputype, cpusubtype, filetype, ncmds, sizeofcmds, flags, res = struct.unpack_from("<IIIIIIII", data, 0)
offset = 32
max_end = 0
for _ in range(ncmds):
    cmd, cmdsize = struct.unpack_from("<II", data, offset)
    if cmd == 0x19: # LC_SEGMENT_64
        segname = data[offset+8:offset+24].split(b"\x00")[0].decode()
        vmaddr, vmsize, fileoff, filesize = struct.unpack_from("<QQQQ", data, offset+24)
        if fileoff + filesize > max_end:
            max_end = fileoff + filesize
    offset += cmdsize
overlay_bytes = len(data) - max_end
print(f"File size: {len(data)}, Segment bound: {max_end}, Overlay: {overlay_bytes} bytes")
if overlay_bytes > 0:
    print(f"[!] Warning: {overlay_bytes} bytes of trailing overlay detected!")
' <binary_path>
```

