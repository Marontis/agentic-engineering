---
name: macos-reverse-engineering
description: >
  Systematic reverse engineering and binary analysis of macOS and iOS
  user-mode binaries. Covers Mach-O structural dissection, universal fat
  binary peeling, dynamic loader (dyld) mechanics and chained fixups,
  Objective-C/Swift runtime metadata reconstruction, Mach messaging and
  XPC service auditing, LLDB and DTrace dynamic instrumentation, and
  code signing / entitlement boundary validation.
  Derived from Jonathan Levin's "Mac OS X and iOS Internals: To the
  Apple's Core, Volume 1: User Mode" (2nd Edition, OS Internals series).
---

# macOS Reverse Engineering & User-Mode Binary Analysis

Use this skill when analyzing, auditing, debugging, or reverse-engineering macOS and iOS user-mode executables, dynamic libraries (`.dylib`), application bundles (`.app`), and system services.

---

## When to Use

- Inspecting unknown or third-party macOS/iOS Mach-O binaries to understand functionality, control flow, and external dependencies
- Auditing daemon and client communication over Mach messaging, MIG RPC, or XPC protocols
- Reconstructing Objective-C class hierarchies, protocols, and Swift mangled types from stripped or unstripped binaries
- Debugging or instrumenting running user-mode processes with LLDB and DTrace across ASLR randomized address spaces
- Auditing application security controls: CodeDirectory hashes (`cdhash`), Hardened Runtime flags, entitlements, and sandbox profiles
- Investigating dynamic linker behavior, library search paths (`@rpath`, `@loader_path`), and symbol rebinding / interposing

---

## Core Architecture & Mental Model

Darwin's user-mode architecture departs fundamentally from standard Linux/ELF environments:

1. **Mach-O Container Format**: Binaries are organized into hierarchical **Headers**, **Load Commands**, **Segments** (page-aligned memory mappings), and **Sections** (data compartments). Binaries may be Universal ("Fat"), packing multiple CPU architecture slices into one file.
2. **Two-Level Namespace Dynamic Linking**: Symbols are resolved not globally, but against specific dynamic libraries recorded in load commands (`LC_LOAD_DYLIB`). Modern systems use **Chained Fixups** and pre-compiled **Dyld Shared Caches**.
3. **Reflective Runtimes**: Objective-C and Swift embed rich metadata directly in designated binary sections (`__objc_classlist`, `__objc_methname`, `__swift5_types`), enabling high-fidelity class and method reconstruction without source code.
4. **Mach IPC Foundation**: Inter-process communication relies on microkernel **Mach Ports** and message headers (`mach_msg_header_t`). Higher-level IPC (MIG RPC, XPC) builds directly on these messaging primitives.
5. **Enforced Code Identity**: Execution integrity is enforced by the kernel via cryptographic code signatures (`LC_CODE_SIGNATURE`), developer certificates, and structured XML/DER entitlement dictionaries.

---

## Procedure

```
Binary Triage (lipo, file)
       │
       ▼
Mach-O Dissection (otool, size) ──► References: macho-binary-anatomy.md
       │
       ▼
Dynamic Linking Audit (dyld_info) ──► References: dyld-and-runtime-linking.md
       │
       ▼
Runtime Metadata Extraction (jtool2, class-dump) ──► References: objc-and-swift-metadata.md
       │
       ▼
IPC / XPC Protocol Analysis (launchctl, log stream) ──► References: mach-ipc-and-xpc.md
       │
       ▼
Dynamic Tracing & LLDB Debugging (dtruss, lldb) ──► References: dynamic-tracing-and-debugging.md
       │
       ▼
Security Posture & Entitlement Audit (codesign)
```

---

### Step 1: Binary Triage & Architecture Peeling

Inspect the binary container to identify CPU targets and extract the target architecture slice:

```bash
# 1. Identify file container format and embedded slices
file <binary_path>
lipo -info <binary_path>

# 2. Extract specific architecture slice for clean disassembler loading
# Modern Apple Silicon: arm64 or arm64e; Intel: x86_64
lipo <binary_path> -thin arm64 -output <binary_path>_arm64
```

---

### Step 2: Static Mach-O Dissection & Structural Mapping

Map out the segment permissions, section boundaries, entry points, and load commands:

1. **Inspect Mach-O Header**:
   ```bash
   otool -v -h <binary_arm64>
   ```
   Check for flags: `MH_PIE` (ASLR enabled), `MH_TWOLEVEL` (two-level namespace), `MH_ALLOW_STACK_EXECUTION` (NX stack disabled).

2. **Enumerate Load Commands**:
   ```bash
   otool -v -l <binary_arm64>
   ```
   - Locate `LC_MAIN`: Identify entry point relative virtual address (`entryoff`) and stack size.
   - Locate `LC_SEGMENT_64`: Map out `__PAGEZERO` (null dereference trap), `__TEXT` (executable code `r-x`), `__DATA_CONST` (read-only GOT and constants), and `__DATA` (writable variables).
   - Locate `LC_CODE_SIGNATURE`: Note data offset and size of the signature block.

3. **Measure Section Sizes & Layout**:
   ```bash
   size -m -l -x <binary_arm64>
   ```

*Deep reference*: See [macho-binary-anatomy.md](references/macho-binary-anatomy.md) for complete `mach_header_64` fields, load command ID definitions, and segment protection flags.

---

### Step 3: Dynamic Linking & dyld Dependency Triage

Trace dynamic library dependencies, search paths, and symbol binding mechanisms:

1. **List Shared Library Dependencies**:
   ```bash
   otool -L <binary_arm64>
   ```
   Inspect paths beginning with `@rpath`, `@executable_path`, or `@loader_path`.

2. **List Runpath Search Paths (`LC_RPATH`)**:
   ```bash
   otool -l <binary_arm64> | grep -A 2 LC_RPATH
   ```

3. **Inspect Symbol Binding & Export Trie**:
   ```bash
   # Classic opcode streams
   dyld_info -bind <binary_arm64>
   dyld_info -lazy_bind <binary_arm64>
   dyld_info -export <binary_arm64>

   # Modern chained fixups (macOS 12+ / iOS 15+)
   dyld_info -fixups <binary_arm64>
   ```

4. **Investigate System Dylibs in Shared Cache**:
   If target dependencies reside in `/System/Library/Frameworks` or `/usr/lib`:
   ```bash
   dyld_info -shared_cache_dylibs /System/Library/dyld/dyld_shared_cache_arm64e
   ```

*Deep reference*: See [dyld-and-runtime-linking.md](references/dyld-and-runtime-linking.md) for dynamic loader lifecycle, opcode state-machines, chained fixup structures, and `__interpose` hooking.

---

### Step 4: Objective-C & Swift Runtime Metadata Recovery

Reconstruct object models, class rosters, protocols, and function signatures from metadata:

1. **Extract Objective-C Class Headers**:
   ```bash
   # Dump full class headers and method prototypes
   class-dump <binary_arm64> -H -o ./recovered_headers/

   # Or using jtool2
   jtool2 -d objc <binary_arm64>
   ```

2. **Inspect Selector Names & Signatures**:
   ```bash
   otool -v -s __TEXT __objc_methname <binary_arm64>
   otool -v -s __TEXT __objc_methtype <binary_arm64>
   ```

3. **Demangle Swift Types & Functions**:
   ```bash
   # Demangle individual mangled symbols ($s...)
   swift-demangle '$s7AppCore11AuthServiceC12loginSuccessyyF'

   # Demangle all exported symbols in binary
   nm -g <binary_arm64> | swift-demangle
   ```

*Deep reference*: See [objc-and-swift-metadata.md](references/objc-and-swift-metadata.md) for `objc_class` memory layouts, method type encoding syntax (`v24@0:8@16`), and Swift reflection sections (`__swift5_types`).

---

### Step 5: Mach IPC & XPC Protocol Auditing

Audit service communication boundaries and message dispatch interfaces:

1. **Identify Mach Service Names in Bundle / LaunchDaemons**:
   ```bash
   # Inspect application Info.plist or embedded Launchd service plists
   plutil -p Info.plist
   launchctl list | grep -i <target_keyword>
   ```

2. **Trace Active XPC Traffic**:
   ```bash
   log stream --predicate 'subsystem contains "com.target.subsystem"' --info --debug
   ```

3. **Identify MIG Server Routines in Disassembly**:
   Search for calls to `mach_msg()` or `mach_msg_trap`. Follow the message pointer to the handler function and inspect the `mig_subsystem` dispatch table in `__DATA_CONST`.

*Deep reference*: See [mach-ipc-and-xpc.md](references/mach-ipc-and-xpc.md) for `mach_msg_header_t` fields, complex message descriptors, and XPC dictionary serialization schemas.

---

### Step 6: Dynamic Tracing & LLDB Instrumentation

Observe live execution, calculate ASLR slides, set breakpoints, and trace system calls:

1. **Trace System Calls with DTrace (`dtruss`)**:
   ```bash
   # Trace all syscalls made by target PID
   sudo dtruss -p <pid>

   # Trace system calls of a newly launched command
   sudo dtruss <command> [args]
   ```

2. **Launch & Attach with LLDB**:
   ```bash
   lldb /path/to/binary
   # Or attach to existing PID:
   lldb -p <pid>
   ```

3. **Calculate ASLR Slide for Disassembly Correlation**:
   ```lldb
   (lldb) image list -o -f <binary_name>
   # Note ASLR slide (e.g., 0x0000000004200000)
   # Set breakpoint at static disassembler address:
   (lldb) breakpoint set -a "0x0000000100003500 + 0x04200000"
   ```

4. **Inspect Arguments at Function Breakpoint (arm64)**:
   - `x0`: First integer/pointer argument (or `self` in ObjC)
   - `x1`: Second argument (or `_cmd` in ObjC)
   - `x2` to `x7`: Subsequent arguments
   - `x20`: Swift `self` instance pointer
   - `po $x0`: Print Objective-C object description

5. **Bypass Anti-Debugging Calls (`PT_DENY_ATTACH`)**:
   ```lldb
   (lldb) breakpoint set -n ptrace
   (lldb) breakpoint command add 1
   > register write $x0 0
   > thread return 0
   > continue
   > DONE
   ```

*Deep reference*: See [dynamic-tracing-and-debugging.md](references/dynamic-tracing-and-debugging.md) for DTrace one-liners, LLDB Python scripting, and memory heap auditing (`vmmap`, `heap`, `leaks`).

---

### Step 7: Code Signature, Entitlement & Sandbox Auditing

Verify the cryptographic identity, signature validity, and runtime permission boundaries:

1. **Verify Code Signature & Identity**:
   ```bash
   codesign -dvvv <binary_path>
   ```
   Inspect:
   - `Authority`: Developer ID or Apple root certificate chain.
   - `CodeDirectory`: Format, version, and `flags` (e.g. `flags=0x10000(runtime)` indicates Hardened Runtime).
   - `cdhash`: Unique cryptographic hash of the CodeDirectory.

2. **Extract Entitlements**:
   ```bash
   # Extract embedded XML entitlements
   codesign -d --entitlements :- <binary_path>

   # Extract DER-encoded binary entitlements (macOS 12+)
   codesign -d --entitlements :--der <binary_path>
   ```
   Audit critical entitlement keys:
   - `com.apple.security.get-task-allow`: Enables debugging without root privileges.
   - `com.apple.security.cs.allow-dyld-environment-variables`: Permits `DYLD_INSERT_LIBRARIES` under Hardened Runtime.
   - `com.apple.security.cs.disable-library-validation`: Allows loading third-party or unsigned dylibs.
   - `com.apple.security.app-sandbox`: Enforces App Sandbox confinement.

3. **Inspect Runtime Sandboxing (Seatbelt)**:
   ```bash
   # Check if running process is sandboxed
   sandbox-exec -f /path/to/profile.sb <binary_path>
   ```

---

## Common Pitfalls & Failure Modes

| Symptom | Root Cause | Remediation |
|:--------|:-----------|:------------|
| `EXC_BAD_ACCESS` / `SIGSEGV` when overwriting function pointers on arm64e | **Pointer Authentication (PAC)**: Pointers are signed with cryptographic PAC instructions (`pacia`, `autia`). Replacing with raw pointer causes authentication failure. | Strip PAC signature using `xpaci` or sign the target pointer with the appropriate PAC key and context before writing. |
| LLDB cannot attach: `attach failed (not allowed to attach to process)` | **Hardened Runtime / SIP**: Process lacks `get-task-allow` entitlement, or is marked system-protected by SIP. | Re-sign binary with custom entitlements including `com.apple.security.get-task-allow`, or disable debugging restrictions via recovery mode `csrutil`. |
| `dtruss` / DTrace produces: `dtrace: failed to initialize dtrace: DTrace requires additional privileges` | **SIP DTrace Restriction**: macOS blocks DTrace on restricted binaries. | Relax DTrace restrictions via recovery terminal: `csrutil enable --without dtrace`. |
| Dynamic libraries missing from `/System/Library` on disk | **Dyld Shared Cache**: macOS 11+ caches all system frameworks in a single monolithic archive. | Extract frameworks using `jtool2 -extract` or `dyld_info -shared_cache_dylibs`. |
| Process terminates immediately upon debugger attach | **Anti-Debug `PT_DENY_ATTACH`**: Binary calls `ptrace(31, 0, 0, 0)`. | Intercept `ptrace` in LLDB and force early return with value `0`, or use dynamic interposing. |
| Stripped binary shows no symbols in `nm` | **Stripped Symbol Table**: `LC_SYMTAB` was stripped with `strip`. | Look up exported symbols in `LC_DYLD_INFO_ONLY` export trie or `LC_DYLD_EXPORTS_TRIE`, and reconstruct class/method names from `__objc_methname`. |

---

## Reference Guides

For exhaustive architectural specifications, structs, and code templates:
- [Mach-O Binary Anatomy & Load Commands](references/macho-binary-anatomy.md) — Comprehensive structural breakdown of `mach_header_64`, load commands, segments, and sections.
- [Dynamic Linking & dyld Runtime](references/dyld-and-runtime-linking.md) — Dynamic loader execution model, binding opcodes, chained fixups, and interposing.
- [Mach IPC, MIG & XPC Architecture](references/mach-ipc-and-xpc.md) — Mach ports, message headers, MIG IDL routing, and XPC dictionary protocols.
- [Objective-C & Swift Runtime Metadata](references/objc-and-swift-metadata.md) — Runtime class layouts, method type encodings, and Swift metadata demangling.
- [Dynamic Tracing, Debugging & Memory Inspection](references/dynamic-tracing-and-debugging.md) — DTrace one-liners, LLDB scripting recipes, memory tools (`vmmap`, `heap`), and anti-debug bypasses.
