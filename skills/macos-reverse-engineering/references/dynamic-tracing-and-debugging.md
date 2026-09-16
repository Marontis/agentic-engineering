# Dynamic Tracing, Debugging & Memory Inspection Reference

This reference details dynamic instrumentation, kernel and user-space tracing via DTrace, LLDB debugger workflows, memory layout inspection, and anti-analysis bypasses on macOS, derived from Jonathan Levin's *Mac OS X and iOS Internals: Volume 1 (User Mode)*.

---

## 1. DTrace Dynamic Tracing

DTrace provides kernel-mediated, zero-probe-overhead tracing across user and kernel boundaries.

### Probe Identifier Syntax
Probes follow the 4-part tuple:
```
provider:module:function:name
```
- Omitted fields act as wildcards (`*`).
- Example: `syscall::open*:entry` matches all syscalls beginning with `open` upon function entry.

### DTrace Scripting Syntax
```d
/* probe_description /predicate/ { action; } */
syscall::open_nocancel:entry
/execname == "target_app"/
{
    printf("Opening file: %s (flags=%d)\n", copyinstr(arg0), arg1);
}
```

### Essential DTrace CLI One-Liners

```bash
# 1. Trace system calls like strace/ltrace using dtruss
sudo dtruss -p <pid>
sudo dtruss -n "AppName"

# 2. Count file opens by process
sudo dtrace -n 'syscall::open*:entry { @[execname, copyinstr(arg0)] = count(); }'

# 3. Trace user-space Objective-C method invocations in target PID
sudo dtrace -n 'pid$target:::entry /probefunc == "objc_msgSend"/ { printf("Selector: %s\n", copyinstr(arg1)); }' -p <pid>

# 4. Trace Mach message dispatch (port ID and function ID)
sudo dtrace -n 'mach_msg:entry /pid == $target/ { printf("msgh_id = %d, remote_port = %d\n", arg4, arg2); }' -p <pid>
```

### System Integrity Protection (SIP) Caveat
On modern macOS, DTrace cannot attach to binaries protected by SIP or Apple internal entitlements unless DTrace SIP restrictions are relaxed via recovery mode:
```bash
csrutil enable --without dtrace --without debug-restrictions
```

---

## 2. LLDB Debugger Workflows

LLDB is the primary debugger for Darwin Mach-O executables.

### ASLR Slide Calculation & Image Base
To map addresses between static disassemblers (IDA, Ghidra) and live memory:
```lldb
# List loaded modules with ASLR slide and load address
(lldb) image list -o -f <binary_name>
# Output: [  0] 0x000000000a240000 /path/to/binary (0x000000010a240000)
# Here, ASLR slide is 0x0a240000.

# Convert static disassembly address to live memory:
# Live Address = Static Address + 0x0a240000
(lldb) breakpoint set -a "0x0000000100004560 + 0x0a240000"
```

### Practical LLDB Recipes
```lldb
# Setting Objective-C method breakpoints
(lldb) breakpoint set -F "-[NetworkManager sendRequest:headers:]"
(lldb) breakpoint set -r ".*Request.*"

# Inspecting Objective-C parameters (arm64 calling convention)
# x0 = self, x1 = _cmd (selector), x2 = first parameter
(lldb) po $x0                      # Print object self description
(lldb) p (char *)$x1               # Print selector string name
(lldb) po $x2                      # Print first object parameter

# Reading memory as Hex and ASCII
(lldb) memory read --size 8 --format x --count 16 $sp
(lldb) memory read --format s $x0

# Disassembling at program counter
(lldb) disassemble --pc --count 20
```

---

## 3. Anti-Debugging Protections & Bypasses

### 1. `ptrace(PT_DENY_ATTACH, 0, 0, 0)`
Binaries call `ptrace` with request `31` (`PT_DENY_ATTACH`). If a debugger is currently attached, the kernel sends `SIGKILL` to the process. If a debugger attempts to attach later, the attach fails.

#### LLDB Breakpoint Bypass
Intercept the call before execution and force a successful return:
```lldb
(lldb) breakpoint set -n ptrace
(lldb) breakpoint command add 1
> register write $x0 0
> thread return 0
> continue
> DONE
```

#### Dynamic Interpose Hook
Compile a dylib with an interposing table replacing `ptrace` with a stub returning `0` and inject via `DYLD_INSERT_LIBRARIES`.

### 2. `sysctl` `P_TRACED` Check
Processes query the kernel via `sysctl` for their own `kinfo_proc` struct to verify if `kp_proc.p_flag & P_TRACED` is set:
```c
int mib[4] = { CTL_KERN, KERN_PROC, KERN_PROC_PID, getpid() };
struct kinfo_proc info;
size_t size = sizeof(info);
sysctl(mib, 4, &info, &size, NULL, 0);
if (info.kp_proc.p_flag & P_TRACED) {
    exit(1); // Debugger detected
}
```
**Bypass**: Set an LLDB breakpoint on `sysctl` and clear the `P_TRACED` bit (`0x800`) in `info.kp_proc.p_flag` upon function return.

---

## 4. Virtual Memory & Heap Inspection CLI

Darwin provides powerful built-in user-mode diagnostic utilities:

```bash
# Display virtual memory regions, sizes, and protection flags (rwx)
vmmap -v <pid>
vmmap -wide <pid>

# Analyze heap allocations and instances by Objective-C class
heap <pid>
heap -addresses "NSString" <pid>

# Detect memory leaks and retain cycle graphs
leaks <pid>

# View call stacks of allocated memory (requires environment variable MallocStackLogging=1)
malloc_history <pid> <allocation_address>
```
