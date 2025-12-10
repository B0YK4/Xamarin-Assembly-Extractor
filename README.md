# Xamarin Assembly Extractor

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/) ![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux-lightgrey.svg)

Extract .NET/Xamarin managed assemblies (DLLs) from Android APKs and `libmonodroid_bundle_app.so` bundles.

A reverse engineering tool for analyzing Xamarin and Mono AOT-compiled Android applications. Automatically handles gzip-compressed assemblies and supports direct APK input without manual unpacking.

## ✨ Features

- **APK Support** — Extract directly from `.apk` files without manual unpacking
- **ELF Parsing** — Parse `libmonodroid_bundle_app.so` and locate all `assembly_data_*` symbols
- **Auto Decompression** — Automatically decompress gzip-compressed assemblies
- **Multi-ABI** — Support for all Android ABIs (arm64-v8a, armeabi-v7a, x86, x86_64)
- **Cross-Platform** — Pre-built binaries for Windows and Linux, or run via Python
- **Zero Config** — Works out of the box with sensible defaults

## 📦 Installation

### Option 1: Download Pre-built Binaries (Recommended)

Pre-built standalone executables are available in the [releases](https://github.com/B0YK4/Xamarin-Assembly-Extractor/releases) section:

|Platform|Architecture|Download|
|---|---|---|
|Windows|x64|`xamarin-assembly-extractor-windows-x64.zip`|
|Windows|x86|`xamarin-assembly-extractor-windows-x86.zip`|
|Linux|x64|`xamarin-assembly-extractor-linux-x64.tar.gz`|
|Linux|arm64|`xamarin-assembly-extractor-linux-arm64.tar.gz`|

No Python installation required — just download, extract, and run.

### Option 2: Run with Python

**Requirements:** Python 3.8+

```bash
# Clone the repository
git clone https://github.com/B0YK4/Xamarin-Assembly-Extractor.git
cd Xamarin-Assembly-Extractor

# Install dependencies
pip install -r requirements.txt
```

Or install the dependency directly:

```bash
pip install pyelftools
```

## 🚀 Usage

### Basic Usage

**Extract from an APK:**

```bash
# Using the executable
./xamarin-assembly-extractor app.apk -o output/

# Using Python
python xamarin-assembly-extractor.py app.apk -o output/
```

**Extract from a bundle file:**

```bash
./xamarin-assembly-extractor libmonodroid_bundle_app.so -o output/
```

### Advanced Options

**Specify preferred ABI when multiple are present:**

```bash
./xamarin-assembly-extractor app.apk -o output/ --arch arm64-v8a
```

**Available ABI options:** `arm64-v8a`, `armeabi-v7a`, `x86`, `x86_64`

### Output Structure

```
output/
├── libmonodroid_bundle_app.so   # Extracted bundle (APK mode only)
└── dlls/
    ├── mscorlib.dll
    ├── Mono.Android.dll
    ├── System.dll
    ├── YourApp.dll
    └── ...
```

## 🔍 How It Works

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   APK / .so     │ ──▶ │   ELF Parser    │ ──▶ │  DLL Output     │
│     Input       │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │ 1. Find symbols │
                        │ 2. Map VA → FO  │
                        │ 3. Extract blob │
                        │ 4. Decompress   │
                        └─────────────────┘
```

1. **Symbol Discovery** — Reads ELF symbol table and finds all `assembly_data_*` symbols
2. **Address Translation** — Converts symbol virtual addresses to file offsets
3. **Size Calculation** — Uses next symbol address to determine blob boundaries
4. **Extraction** — Writes each blob; automatically decompresses gzip to `.dll`


## 🔗 Related Tools

- [ILSpy](https://github.com/icsharpcode/ILSpy) — .NET assembly browser and decompiler
- [dnSpy](https://github.com/dnSpy/dnSpy) — .NET debugger and assembly editor
- [apktool](https://github.com/iBotPeaches/Apktool) — Android APK reverse engineering tool

---


**Keywords:** Xamarin, Mono, Android, APK, DLL, Assembly, Reverse Engineering, .NET, libmonodroid, AOT, Decompiler, Extractor, Security Research

