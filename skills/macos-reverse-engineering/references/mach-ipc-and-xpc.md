# Mach IPC, MIG & XPC Architecture Reference

This reference details the low-level inter-process communication (IPC) subsystems on Darwin, macOS, and iOS, including Mach messaging primitives, the Mach Interface Generator (MIG), bootstrap namespaces, and the modern XPC protocol, derived from Jonathan Levin's *Mac OS X and iOS Internals: Volume 1 (User Mode)*.

---

## 1. Mach Messaging Primitives

Mach IPC is message-oriented, capability-based communication implemented in the microkernel.

### Mach Ports & Port Rights
A **Mach Port** is a kernel-managed unidirectional FIFO message queue. Processes interact with ports using integer identifiers called **port names** (`mach_port_t`), which index into the task's IPC table (`ipc_space_t`).

| Right Type | Macro Constant | Semantics |
|:-----------|:---------------|:----------|
| **Receive Right** | `MACH_PORT_RIGHT_RECEIVE` | Only one task may hold a receive right per port. Owns the queue. |
| **Send Right** | `MACH_PORT_RIGHT_SEND` | Multiple tasks can hold send rights to transmit messages into the port. |
| **Send-Once Right** | `MACH_PORT_RIGHT_SEND_ONCE` | Valid for exactly one message transmission, then invalidated by kernel. Used for RPC replies. |
| **Port Set** | `MACH_PORT_RIGHT_PORT_SET` | Group of receive rights polled atomically by a single thread. |

### Message Header Layout (`mach_msg_header_t`)
Every message begins with `mach_msg_header_t`:
```c
typedef struct {
    mach_msg_bits_t msgh_bits;         /* Flags specifying complex msg, port right descriptors */
    mach_msg_size_t msgh_size;         /* Total message byte size including payload */
    mach_port_t     msgh_remote_port;  /* Destination port (Send or Send-Once right) */
    mach_port_t     msgh_local_port;   /* Reply port (Send-Once right provided by sender) */
    mach_port_name_t msgh_voucher_port;/* Mach voucher (resource accounting / personas) */
    mach_msg_id_t   msgh_id;           /* Operation / Function selector ID */
} mach_msg_header_t;
```

### Simple vs. Complex Messages
- **Simple Message**: Carries inline scalar bytes only (`msgh_bits & MACH_MSGH_BITS_COMPLEX == 0`).
- **Complex Message**: Followed by `mach_msg_body_t` containing descriptors (`mach_msg_descriptor_t`) that transfer port rights (`MACH_MSG_PORT_DESCRIPTOR`) or out-of-line virtual memory pages (`MACH_MSG_OOL_DESCRIPTOR`) directly between address spaces without memory copying.

---

## 2. Mach Interface Generator (MIG)

MIG is an IDL (Interface Definition Language) compiler that generates type-safe C client and server RPC stubs over Mach messages.

### MIG Message Routing Architecture
1. **Request**: The client invokes a generated stub (e.g. `mach_vm_allocate(...)`). The stub fills `mach_msg_header_t` with an operation-specific `msgh_id` (e.g. `4800` for VM subsystem), packs arguments into the body, sets `msgh_local_port` to a newly allocated send-once reply port, and calls `mach_msg()`.
2. **Server Dispatch**: The server thread listens on its receive port. When a message arrives, it passes the raw buffer to a MIG subsystem server dispatch function:
   ```c
   boolean_t subsystem_server(mach_msg_header_t *InHeadP, mach_msg_header_t *OutHeadP);
   ```
3. **Subsystem Descriptor**:
   ```c
   struct mig_subsystem {
       mig_server_routine_t server;   /* Fallback handler */
       mach_msg_id_t        start;    /* Lowest message ID in subsystem */
       mach_msg_id_t        end;      /* Highest message ID + 1 */
       mach_msg_size_t      maxsize;  /* Maximum reply size */
       vm_address_t         reserved;
       routine_descriptor_t routine[];/* Array of function pointers indexed by (msgh_id - start) */
   };
   ```

### Reverse-Engineering MIG Subsystems
When analyzing a binary implementing Mach RPC:
1. Locate calls to `mach_msg()` receiving messages.
2. Follow the message pointer to the dispatch function.
3. Identify the `mig_subsystem` struct in `__DATA_CONST` or `__CONST`.
4. Calculate function target from `routine[msgh_id - subsystem.start].stub_routine`.

---

## 3. Bootstrap Namespace (`launchd`)

Because Mach ports are anonymous kernel objects, processes discover public services via the **Bootstrap Server** (`launchd`):

### Registration & Discovery
- **Server Registration**: A daemon registered in `/System/Library/LaunchDaemons/com.example.daemon.plist` checks in with `bootstrap_check_in(bootstrap_port, "com.example.daemon", &receive_port)`.
- **Client Resolution**: A client resolves the daemon's send right using:
  ```c
  mach_port_t daemon_port;
  kern_return_t kr = bootstrap_look_up(bootstrap_port, "com.example.daemon", &daemon_port);
  ```

### Auditing LaunchDaemons & LaunchAgents
```bash
# List all registered Mach services
launchctl list

# Inspect specific service configuration
launchctl print system/<service-name>
launchctl print gui/<uid>/<service-name>
```

---

## 4. XPC Architecture (libxpc)

XPC is Apple's high-level IPC framework built on top of Mach messaging, Grand Central Dispatch (GCD), and launchd.

### Wire Format & Dictionary Serialization
XPC messages are serialized dictionaries (`xpc_dictionary_t` / `OS_xpc_object`) transmitted over anonymous Mach ports:
- **Primitives**: Int64, String, Data, UUID, FD (file descriptors transferred via `MACH_MSG_OOL_PORTS_DESCRIPTOR`), Mach send rights.
- **Magic Prefix**: Serialized XPC payloads on the wire begin with the 4-byte magic `!cat` (`0x21636174`) or `!xpc` followed by versioning flags.

### Client-Server Connection Lifecycle
```c
// Client establishing XPC service connection
xpc_connection_t conn = xpc_connection_create_mach_service(
    "com.apple.windowserver.active",
    dispatch_get_main_queue(),
    0
);

xpc_connection_set_event_handler(conn, ^(xpc_object_t event) {
    xpc_type_t type = xpc_get_type(event);
    if (type == XPC_TYPE_DICTIONARY) {
        // Handle response
    }
});

xpc_connection_resume(conn);

// Sending structured dictionary
xpc_object_t msg = xpc_dictionary_create(NULL, NULL, 0);
xpc_dictionary_set_string(msg, "command", "ping");
xpc_connection_send_message(conn, msg);
```

### Auditing & Security Verification
Secure daemons must verify caller identity before processing XPC commands:
1. **Audit Token**: Extracted via `xpc_connection_get_audit_token(conn, &audit_token)`.
2. **Entitlement Verification**: The daemon passes the audit token to `SecTaskCreateWithAuditToken` and inspects `SecTaskCopyValueForEntitlement`.
3. **Sandbox Check**: The daemon queries `sandbox_check_by_audit_token` to confirm the caller possesses permissions to request the operation.

### Dynamic XPC Sniffing & Tracing
```bash
# Trace XPC message dispatch with log stream
log stream --predicate 'subsystem contains "com.apple.xpc"' --info --debug

# Monitor Mach IPC context switches with DTrace
sudo dtrace -n 'mach_msg:entry /execname == "target_process"/ { printf("Port: %d, ID: %d", arg0, arg4); }'
```
