import re
import struct
import sys

if len(sys.argv) < 2:
    print("Usage: python clean_mtk_dump.py <RAW_BE_FILE.bin> [IMEI1] [IMEI2]")
    sys.exit(1)

raw_path = sys.argv[1]
imeis = sys.argv[2:]

with open(raw_path, "rb") as f:
    raw = f.read()

# 1. Convert 32-bit big-endian words to little-endian ARM flash layout
words = struct.unpack(f">{len(raw)//4}I", raw)
data = bytearray(struct.pack(f"<{len(words)}I", *words))

assert data[:7] == b"SF_BOOT", f"Invalid header: {data[:16]}"

# 2. Auto-detect model (ASCII or UTF-16LE), software version, and Product Code
model_m = re.search(b"(?:TA|RM)-\\d{4}", data)
if not model_m:
    u16_m = re.search(b"(?:T\x00A\x00|R\x00M\x00)-\x00(?:\\d\x00){4}", data)
    model = u16_m.group(0).decode("utf-16le") if u16_m else "UNKNOWN"
else:
    model = model_m.group(0).decode("ascii")

ver_m = re.search(b"\\d{2}\\.\\d{2}\\.\\d{2}", data)
code_m = re.search(b"(?:059[0-9A-Z]{4}|23G[0-9A-Z]{8})", data)

ver = ver_m.group(0).decode("ascii") if ver_m else "00.00.00"
code = code_m.group(0).decode("ascii") if code_m else "NOCODE"

print(f"Detected: Model={model} | Version={ver} | ProductCode={code} | Size={len(data)//(1024*1024)}MB")

# 3. Save private full backup
personal_out = f"{model}_{code}_{ver}_PERSONAL_FULL.bin"
with open(personal_out, "wb") as f:
    f.write(data)

# 4. Scrub IMEIs (ASCII & BCD)
def imei_to_bcd(imei):
    padded = imei + "F"
    return bytes((int(padded[i+1], 16) << 4) | int(padded[i], 16) for i in range(0, 16, 2))

for imei in imeis:
    if not imei.isdigit() or len(imei) != 15:
        print(f"  Skipping non-15-digit argument: {imei}")
        continue
    for pat, label in [(imei.encode("ascii"), "ASCII"), (imei_to_bcd(imei), "BCD")]:
        idx = 0
        while (idx := data.find(pat, idx)) != -1:
            print(f"  Scrubbing {label} IMEI match at 0x{idx:08X}")
            data[idx:idx+len(pat)] = b"\xFF" * len(pat)
            idx += len(pat)

# 5. Wipe writable FAT/NVRAM region in the upper half of flash
half = len(data) // 2
fat_offset = data.find(b"\xEB\x58\x90", half)
if fat_offset == -1:
    fat_offset = data.find(b"FAT12", half)
if fat_offset != -1:
    block_start = fat_offset & ~0xFFFF
    print(f"  Wiping writable FAT/NVRAM partition from 0x{block_start:08X} to 0x{len(data):08X}")
    data[block_start:] = b"\xFF" * (len(data) - block_start)

clean_out = f"{model}_{code}_{ver}_CLEAN.bin"
with open(clean_out, "wb") as f:
    f.write(data)

print(f"Saved: {clean_out} (and private {personal_out})")
