#!/usr/bin/env python3
"""
Extract embedded managed assemblies from Xamarin/Mono bundle libraries.

Supports:
- Direct extraction from libmonodroid_bundle_app.so
- Extraction from an .apk (finds lib/**/libmonodroid_bundle_app.so)

Output: decompressed DLLs (assembly_data_Foo_dll -> Foo.dll)

Dependencies: pyelftools
    pip install pyelftools
"""

import argparse
import gzip
import io
import sys
import zipfile
from pathlib import Path
from typing import Dict, List, Tuple

from elftools.elf.elffile import ELFFile


def _addr_to_offset(elf: ELFFile, addr: int) -> int:
    """Translate a virtual address to a file offset using program headers."""
    for seg in elf.iter_segments():
        p_vaddr = seg["p_vaddr"]
        p_memsz = seg["p_memsz"]
        if p_vaddr <= addr < p_vaddr + p_memsz:
            return seg["p_offset"] + (addr - p_vaddr)
    raise ValueError(f"Address 0x{addr:x} not in any segment")


def _collect_assembly_symbols(elf: ELFFile) -> List[Tuple[str, int]]:
    """Return sorted list of (name, vaddr) for symbols starting with assembly_data_."""
    syms = []
    for section in elf.iter_sections():
        if not hasattr(section, "iter_symbols"):
            continue
        for sym in section.iter_symbols():
            name = sym.name
            if name.startswith("assembly_data_"):
                vaddr = sym.entry.get("st_value")
                if vaddr is None:
                    continue
                syms.append((name, vaddr))
    syms.sort(key=lambda x: x[1])
    return syms


def extract_from_so(so_path: Path, out_dir: Path) -> Dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    with so_path.open("rb") as f:
        elf = ELFFile(f)
        sym_addrs = _collect_assembly_symbols(elf)
        if not sym_addrs:
            raise RuntimeError("No assembly_data_ symbols found; is this a Mono bundle?")

        # Build (name, offset, size)
        blobs: List[Tuple[str, int, int]] = []
        for i, (name, vaddr) in enumerate(sym_addrs):
            start = _addr_to_offset(elf, vaddr)
            end_addr = sym_addrs[i + 1][1] if i + 1 < len(sym_addrs) else None
            if end_addr is not None:
                size = _addr_to_offset(elf, end_addr) - start
            else:
                size = f.seek(0, io.SEEK_END) or f.tell() - start  # type: ignore
            blobs.append((name, start, size))

        extracted: Dict[str, Path] = {}
        for name, off, size in blobs:
            f.seek(off)
            blob = f.read(size)
            dll_name = name.replace("assembly_data_", "").replace("_dll", ".dll")
            out_file = out_dir / dll_name
            try:
                blob = gzip.decompress(blob)
            except OSError:
                # not gzipped; write raw
                pass
            out_file.write_bytes(blob)
            extracted[dll_name] = out_file
        return extracted


def find_bundle_in_apk(apk_path: Path, preferred_arch: str = None) -> Tuple[Path, bytes]:
    arch_order = []
    if preferred_arch:
        arch_order.append(preferred_arch)
    arch_order.extend(["arm64-v8a", "armeabi-v7a", "x86_64", "x86"])

    with zipfile.ZipFile(apk_path, "r") as z:
        names = z.namelist()
        candidates = []
        for arch in arch_order:
            target = f"lib/{arch}/libmonodroid_bundle_app.so"
            if target in names:
                candidates.append(target)
        if not candidates:
            raise RuntimeError("libmonodroid_bundle_app.so not found in APK")
        chosen = candidates[0]
        data = z.read(chosen)
        return Path(chosen), data


def extract_from_apk(apk_path: Path, out_dir: Path, preferred_arch: str = None) -> Dict[str, Path]:
    rel_path, data = find_bundle_in_apk(apk_path, preferred_arch)
    out_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = out_dir / rel_path.name
    bundle_path.write_bytes(data)
    return extract_from_so(bundle_path, out_dir / "dlls")


def main():
    parser = argparse.ArgumentParser(description="Extract managed DLLs from libmonodroid_bundle_app.so or APK.")
    parser.add_argument("input", type=Path, help="Path to libmonodroid_bundle_app.so or APK")
    parser.add_argument("-o", "--out", type=Path, default=Path("extracted_dlls"), help="Output directory")
    parser.add_argument("--arch", help="Preferred APK ABI (e.g., arm64-v8a, x86_64)")
    args = parser.parse_args()

    inp = args.input
    out_dir = args.out

    try:
        if inp.suffix.lower() == ".apk":
            extracted = extract_from_apk(inp, out_dir, args.arch)
        else:
            extracted = extract_from_so(inp, out_dir)
    except Exception as exc:
        print(f"[!] Extraction failed: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"[+] Extracted {len(extracted)} assemblies to {out_dir.resolve()}:")
    for name, path in extracted.items():
        print(f"    {name} -> {path}")


if __name__ == "__main__":
    main()

