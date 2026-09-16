# macOS Persistence Mechanisms, Packaging Triage & Behavioral Monitoring Reference

This reference details installer package peeling, Apple persistence vectors, real-time behavioral monitoring, and string/payload deobfuscation on macOS, derived from Patrick Wardle's *The Art of Mac Malware: The Guide to Analyzing Malicious Software* (TAOMM, Volume 1).

---

## 1. Distribution Packaging & Nonbinary Triage

Attackers and software distributors rarely deliver raw Mach-O executables directly; they package payloads inside disk images, installer packages, or script wrappers.

### Apple Disk Images (`.dmg`)
DMGs are read-only or compressed disk image containers:
```bash
# Attach DMG without mounting GUI / executing auto-run helpers
hdiutil attach -nobrowse -readonly <path_to_dmg>

# Inspect mounted volume mountpoint (typically /Volumes/<VolumeName>)
ls -la /Volumes/<VolumeName>

# Unmount after extracting candidate files
hdiutil detach /Volumes/<VolumeName>
```

### Flat Packages (`.pkg`)
macOS flat packages are XAR (eXtensible ARchive) containers holding compressed payloads and execution scripts:
```bash
# 1. Expand flat PKG structure to inspection directory
pkgutil --expand <installer.pkg> ./expanded_pkg/

# 2. Inspect Distribution XML and PackageInfo for pre/post-install triggers
cat ./expanded_pkg/Distribution
cat ./expanded_pkg/PackageInfo

# 3. Extract the Payload archive (CPIO format)
cd ./expanded_pkg/*.pkg/
cat Payload | cpio -idmv
```
*Key Audit Site*: Inspect `Scripts/preinstall` and `Scripts/postinstall` shell scripts. These run as `root` during installation and are the primary vector for establishing persistence and dropping secondary payloads.

### Compiled AppleScript (`.scpt` / `.app`)
Scripts compiled into run-only or binary AppleScript:
```bash
# Decompile AppleScript bytecode to human-readable source
osadecompile <script_path>

# Extract embedded payload if wrapped inside an AppleScript droplet app bundle
ls -la <Droplet.app>/Contents/Resources/Scripts/
```

---

## 2. macOS Persistence Mechanisms

Software and malware establish survivable execution across reboots using structured launch hooks:

### Launch Daemons & Launch Agents
The standard, supported Apple mechanism for background execution (`launchd`):

| Scope | Path | Privileges | Execution Context |
|:------|:-----|:-----------|:------------------|
| System Daemon | `/System/Library/LaunchDaemons/` | `root` | System startup (SIP-protected) |
| Third-Party Daemon | `/Library/LaunchDaemons/` | `root` | System startup |
| System Agent | `/System/Library/LaunchAgents/` | User | User GUI login (SIP-protected) |
| Global Agent | `/Library/LaunchAgents/` | User | User GUI login |
| User Agent | `~/Library/LaunchAgents/` | User | Target user GUI login |

#### Key Plist Audit Keys
- `Label`: Unique service identifier (e.g., `com.company.service`).
- `Program` / `ProgramArguments`: Binary path and command-line flags.
- `RunAtLoad`: Set to `true` to execute immediately when loaded/booted.
- `KeepAlive`: Set to `true` to restart automatically if killed.
- `StartInterval` / `StartCalendarInterval`: Cron-like periodic scheduling.

### Login Items & Background Items (BTM)
Modern macOS (Ventura 13+) tracks login items through Background Task Management (BTM):
- Legacy path: `~/Library/Application Support/com.apple.backgroundtaskmanagementagent/backgrounditems.btm`
- Modern inspection via `sfltool`:
  ```bash
  sfltool dump-btm
  ```
- Framework API: `SMAppService` / `SMLoginItemSetEnabled`.

### Dynamic Library Hijacking & Proxying
Exploiting weak dylib loading or `@rpath` resolution order:
1. **Dylib Hijacking**: A binary contains an `LC_LOAD_DYLIB` or `LC_LOAD_WEAK_DYLIB` command pointing to a dylib that does not exist at the primary `@rpath` search path. An attacker places a dylib with that name in an earlier `@rpath` directory.
2. **Dylib Proxying**: The planted dylib exports identical functions as the genuine dylib (proxying calls to the real library) while executing initialization code inside its `__attribute__((constructor))` routine.
3. **Auditing Vulnerable Binaries**:
   ```bash
   # Check all rpaths and dependent dylibs
   otool -l <binary> | grep -A 2 LC_RPATH
   otool -L <binary>
   ```

### Additional Persistence Sites
- **Cron Jobs**: Checked via `crontab -l` and `/usr/lib/cron/tabs/`.
- **Periodic Scripts**: `/etc/periodic/daily/`, `/etc/periodic/weekly/`, `/etc/periodic/monthly/`.
- **Login/Logout Hooks**: Query via `defaults read com.apple.loginwindow LoginHook`.
- **Reopened Applications**: Stored in `~/Library/Saved Application State/<bundle-id>.savedState`.

---

## 3. Real-Time Behavioral Monitoring

Static analysis reveals capability; dynamic behavioral monitoring reveals live intent.

### File System Monitoring (`fs_usage`)
Monitor file modifications, dropped binaries, and persistence installations in real time:
```bash
# Monitor filesystem operations by target process name
sudo fs_usage -w -f filesys <process_name>

# Exclude noisy system processes and filter for writes/creations
sudo fs_usage -w -f filesys | grep -E "(open|write|rename|unlink)" | grep -v "mds"
```

### Network Monitoring
Audit outbound connections, DNS queries, and command-and-control (C2) beacons:
```bash
# List established sockets with process names and PIDs
sudo lsof -i -n -P | grep ESTABLISHED

# Monitor live packet stream on loopback or external interfaces
sudo tcpdump -i en0 -nn -s0 -A 'tcp port 80 or tcp port 443'
```

### Endpoint Security Framework (ESF)
Modern macOS monitoring standard replacing kernel extensions (KEXTs):
- Subscribes via `es_new_client()` to kernel event notifications: `ES_EVENT_TYPE_AUTH_EXEC`, `ES_EVENT_TYPE_NOTIFY_FORK`, `ES_EVENT_TYPE_NOTIFY_CREATE`.
- Wardle's open-source tools (`ProcessMonitor`, `FileMonitor`) wrap ESF to emit structured JSON logs of every executed process, parent-child process tree, and file system mutation.

---

## 4. Deobfuscation & Anti-Analysis Bypasses

Malware employs anti-analysis checks to detect virtual machines, sandboxes, and debuggers.

### Hardware & Virtual Machine Evasion Checks

| Target Check | Mechanism | Bypass Recipe |
|:-------------|:----------|:--------------|
| **Model Name** | Queries `sysctl hw.model` looking for `VMware`, `VirtualBox`, `Parallels` | Hook `sysctl` via LLDB or interpose library; return `MacBookPro18,1`. |
| **CPU Core Count** | Queries `sysctl hw.ncpu` (virtual machines often assigned 1 or 2 vCPUs) | In LLDB, set breakpoint on `sysctl` return and write register value `>= 4`. |
| **MAC Address** | Queries `getifaddrs` checking OUI prefix against hypervisor vendors | Patch network interface MAC address to legitimate Apple OUI prefix. |
| **SIP Status** | Calls `csr_get_active_config()` or parses `csrutil status` | In sandboxed analysis VMs, ensure SIP returns enabled (`0x0`) if malware terminates upon seeing disabled SIP. |

### String & Payload Deobfuscation

1. **Stack Strings**: Strings constructed character-by-character at runtime to defeat `strings` or static signatures:
   - Identify repetitive register moves in disassembly (e.g. `mov byte ptr [rbp - 0x10], 'h'`, `mov byte ptr [rbp - 0xf], 't'`).
2. **Forced Emulation / Execution via LLDB**:
   Instead of manually reversing complex XOR/AES decryption routines, force the binary to execute its own decryption routine under debugger control:
   ```lldb
   # 1. Break at function call right before decryption routine returns
   (lldb) breakpoint set -a 0x100002890

   # 2. Run to breakpoint
   (lldb) continue

   # 3. Read decrypted buffer from destination pointer register
   (lldb) memory read --format s $x0
   (lldb) memory read --size 1 --format c --count 64 $x0
   ```

---

## 5. Gatekeeper, Quarantine Attributes & Notarization

Gatekeeper enforces runtime validation on binaries downloaded from external networks.

### The Quarantine Extended Attribute (`com.apple.quarantine`)
When a file is saved via web browsers, email clients, or AirDrop, the downloading application attaches `com.apple.quarantine`:
```bash
# Display extended attributes
xattr -l <file_path>

# Raw quarantine string format:
# flag;timestamp;agent_bundle_id;UUID
# e.g.: 0081;5f5b2c7e;Safari;E7B82C05-64AC-4A3C-901B-39E0A243F6E1

# Manually strip quarantine (administrative / analysis override)
xattr -d com.apple.quarantine <file_path>
```

### Gatekeeper Policy & Notarization Verification
Gatekeeper requires that quarantined binaries possess a valid Developer ID signature and an **Apple Notarization ticket**:
```bash
# Assess whether Gatekeeper will permit execution
spctl -a -vv -t execute <binary_path>

# Validate embedded or stapled notarization ticket
stapler validate <binary_path>
```

### Quarantine Blindspots & Evasion Vectors
1. **Non-Browser Tools**: Terminal tools (`curl`, `wget`, `git clone`, `scp`, `rsync`) do **not** route downloads through LaunchServices and do **not** apply `com.apple.quarantine`. Binaries fetched via command-line bypass Gatekeeper entirely.
2. **AppleScript Droplets**: Launching unquarantined secondary helper scripts or droplets embedded in resource directories.
3. **Notarized Malicious Binaries**: Attackers occasionally pass automated notary checks by obfuscating malicious intent behind delayed logic or secondary payload staging.

---

## 6. TCC (Transparency, Consent, and Control) Auditing

TCC restricts application access to sensitive user data, peripherals, and system folders (Microphone, Camera, Screen Recording, `~/Library/Safari`, `~/Library/Mail`, `~/Library/Messages`).

### TCC SQLite Database Layout
TCC policy entries are stored in SQLite databases:
- **User Scope**: `~/Library/Application Support/com.apple.TCC/TCC.db`
- **System Scope**: `/Library/Application Support/com.apple.TCC/TCC.db` (SIP-protected)

```bash
# Query TCC access grants for target client bundle (requires Full Disk Access)
sqlite3 ~/Library/Application\ Support/com.apple.TCC/TCC.db \
  "SELECT service, client, auth_value FROM access WHERE client LIKE '%target%';"
```

### Full Disk Access (FDA) Probing
Binaries probe for FDA silently without prompting the user by attempting non-blocking reads on TCC-protected paths:
```bash
# If exit status is non-zero (Operation not permitted), FDA is absent
ls ~/Library/Safari > /dev/null 2>&1
```

### TCC Privilege Inheritance & Evasion
1. **Remote Login / SSH Privilege Inheritance**: Historically, the system `sshd` daemon held Full Disk Access. Local loopback operations (`scp user@localhost:~/Library/Safari/Cookies.binarycookies .`) inherited SSHD's disk access without triggering user authorization prompts.
2. **Entitlement Hijacking via DYLD**: Injecting dynamic libraries (`DYLD_INSERT_LIBRARIES`, `DYLD_FRAMEWORK_PATH`) into unhardened developer tools or utilities (e.g. `SafariForWebKitDevelopment`) lacking library validation (`disable-library-validation`) inherits the donor process's TCC rights.

---

## 7. Developer Supply-Chain: Xcode Project Subversion

Targeting developers by weaponizing source project files (`OSX.XCSSET` pattern):

### Project File Structure (`project.pbxproj`)
Xcode stores build configuration in `<App>.xcodeproj/project.pbxproj`. It supports script build phases:
- **`PBXShellScriptBuildPhase`**: Arbitrary shell scripts executed whenever the developer builds the project.
- **Hidden Invocations**: Attackers insert background script runs:
  ```
  shellScript = "nohup python3 -c '...' > /dev/null 2>&1 &";
  ```
- **Auditing Projects for Supply-Chain Backdoors**:
  ```bash
  grep -E "(PBXShellScriptBuildPhase|shellScript)" <App>.xcodeproj/project.pbxproj
  ```

---

## 8. Packed Binaries & UPX on macOS

Cross-platform malware (e.g. `OSX.IPStorm`) frequently leverages UPX (Ultimate Packer for eXecutables) to compress Mach-O binaries and obscure static disassembly:

```bash
# Inspect whether binary has UPX signature
strings <binary_path> | grep -E "(UPX!|\$Info: This file is packed under the help of the UPX)"

# Decompress standard UPX Mach-O binary
upx -d <binary_path> -o <unpacked_binary>
```
If the UPX header magic or section names were stripped/altered, set an LLDB breakpoint on the trailing jump instruction (`jmp` or `br`) at the end of the decompression stub to dump memory after reaching the Original Entry Point (OEP).
