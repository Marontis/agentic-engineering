# Objective-C & Swift Runtime Metadata Reference

This reference details the internal runtime data structures, class registration mechanisms, method dispatch pipelines, and symbol demangling conventions for Objective-C and Swift binaries on Apple platforms, derived from Jonathan Levin's *Mac OS X and iOS Internals: Volume 1 (User Mode)*.

---

## 1. Objective-C Runtime Data Layout

Objective-C is a reflective, dynamic runtime (`libobjc.A.dylib`). All class definitions, protocols, ivars, and selectors are preserved in structured Mach-O sections.

### Class Memory Layout (`objc_class` & `class_ro_t`)

At compile time, the compiler generates a `class_ro_t` structure in `__DATA_CONST,__objc_const`:
```c
struct class_ro_t {
    uint32_t flags;
    uint32_t instanceStart;
    uint32_t instanceSize;       /* Total byte size of object allocation */
    uint32_t reserved;           /* 64-bit alignment padding */
    const uint8_t *ivarLayout;
    const char *name;            /* Class name string */
    method_list_t *baseMethodList;
    protocol_list_t *baseProtocols;
    const ivar_list_t *ivars;    /* Instance variable descriptors */
    const uint8_t *weakIvarLayout;
    property_list_t *baseProperties;
};
```

When `dyld` loads the binary and the Objective-C runtime initializes the image, it allocates a dynamic `class_rw_t` and sets up the live class:
```c
struct objc_class {
    Class isa;                   /* Metaclass pointer */
    Class superclass;            /* Superclass pointer */
    cache_t cache;               /* Fast-lookup method dispatch cache */
    uintptr_t bits;              /* Fast flags + pointer to class_rw_t / class_ro_t */
};
```

### Method Structure (`method_t`)
Methods are declared in `method_list_t`:
```c
struct method_t {
    SEL name;                    /* Pointer to string in __TEXT,__objc_methname */
    const char *types;           /* Type encoding string in __TEXT,__objc_methtype */
    IMP imp;                     /* Function entry point pointer */
};
```

### Type Encoding Cheat Sheet
Objective-C encodes argument and return types into a compact string:
- `v`: `void`
- `@`: `id` (Objective-C object instance, always parameter 0 = `self`)
- `:`: `SEL` (Method selector, always parameter 1 = `_cmd`)
- `i` / `q`: `int` / `long long` (`NSInteger` on 64-bit)
- `B`: `BOOL`
- `^v`: `void *`

*Example*: `v24@0:8@16`
- Return type: `void` (`v`)
- Total argument frame size: 24 bytes
- Arg 0 (`self`): object (`@`) at offset 0
- Arg 1 (`_cmd`): selector (`:`) at offset 8
- Arg 2 (first param): object (`@`) at offset 16

---

## 2. Objective-C Mach-O Sections

| Section | Segment | Content |
|:--------|:--------|:--------|
| `__objc_classlist` | `__DATA_CONST` | Array of pointers to all defined `objc_class` structures |
| `__objc_catlist` | `__DATA_CONST` | Array of pointers to categories extending existing classes |
| `__objc_protolist` | `__DATA_CONST` | Protocol descriptors |
| `__objc_imageinfo` | `__DATA_CONST` | Version (always 0) and flags (Swift version, ARC flag) |
| `__objc_const` | `__DATA_CONST` | Compile-time `class_ro_t`, method lists, ivar names |
| `__objc_selrefs` | `__DATA` | Selector references cached for `objc_msgSend` calls |
| `__objc_msgrefs` | `__DATA` | Method references for fast vtable-style dispatch |
| `__objc_methname` | `__TEXT` | Selector names as null-terminated C-strings |
| `__objc_methtype` | `__TEXT` | Method signature type encodings |
| `__objc_classname`| `__TEXT` | Class name strings |

### Header Dumping & Static Reconstruction
```bash
# Dump all class declarations and methods using class-dump
class-dump <binary> -H -o ./headers/

# Using modern Levin's jtool2
jtool2 -d objc <binary>

# Dump selector names using otool
otool -v -s __TEXT __objc_methname <binary>
```

---

## 3. Dynamic Message Dispatch & Swizzling

### `objc_msgSend` Execution Pipeline
Calls in source code (`[object doWork:arg]`) compile into:
```c
objc_msgSend(object, @selector(doWork:), arg);
```
1. Reads `object->isa` to locate the class.
2. Checks inline `class->cache` bucket for `@selector(doWork:)`.
3. On cache miss, traverses `class_rw_t` method lists and superclass hierarchy.
4. If unresolved, triggers runtime dynamic resolution (`+resolveInstanceMethod:`) and forwarding (`forwardInvocation:`).

### Method Swizzling
Intercepting methods at runtime without binary patching:
```objc
#import <objc/runtime.h>

void Swizzle(Class c, SEL orig, SEL replacement) {
    Method origMethod = class_getInstanceMethod(c, orig);
    Method newMethod  = class_getInstanceMethod(c, replacement);
    method_exchangeImplementations(origMethod, newMethod);
}
```

---

## 4. Swift Metadata & ABI

Modern Swift (macOS 10.14.4+ / iOS 12.2+) uses a stable ABI. Swift symbols are heavily mangled and metadata is stored in specialized sections.

### Swift Mangling Prefixes
- `$s`: Global Swift 5+ symbol prefix (e.g. `$s7MyModule10MyClassC9calculateyyF`).
- `$S`: Specialized generic instantiation.
- `_T`: Legacy Swift 3 / Swift 4 prefix.

### Demangling CLI
```bash
# Demangle a single symbol
swift-demangle '$s7MyModule10MyClassC9calculateyyF'
# Output: MyModule.MyClass.calculate() -> ()

# Demangle interactive stream
nm -g <binary> | swift-demangle
```

### Swift Reflection Sections in Mach-O
Swift defines custom metadata sections in `__TEXT`:
- `__swift5_types`: Nominal type descriptors (structs, classes, enums).
- `__swift5_fieldmd`: Field record types and member variable offsets.
- `__swift5_reflstr`: Reflection field names as literal strings.
- `__swift5_proto`: Protocol conformances.
- `__swift5_assocty`: Associated type descriptors.

### Swift Calling Convention Quirks
- **Self Pointer**: Passed in register `x20` on arm64 (unlike C/ObjC which pass `self` in `x0`).
- **Error Register**: If a function `throws`, the error pointer is returned in `x21` (`swifterror`).
- **Context Register**: Generics and closure context are passed in `x17` or `x18`.
