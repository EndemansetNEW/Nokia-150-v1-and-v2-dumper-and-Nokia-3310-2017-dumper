import struct

PRODUCT_CODE = "23GMN35VN00"  # Replace with the 059... code (for v1) and 23GMN... code for v2 from under the battery
RAW_BE_FILE = "Nokia150v1_RAW.bin"
PERSONAL_LE_FILE = f"RM-1190_{PRODUCT_CODE}_40.00.11_PERSONAL_FULL.bin"
PUBLIC_CLEAN_FILE = f"RM-1190_{PRODUCT_CODE}_40.00.11_CLEAN.bin"

# Replace with your actual 15-digit IMEIs from dialing *#06# on the Nokia 150
IMEIS = [
    "350000000000000",  # IMEI 1
    "350000000000000",  # IMEI 2
]

with open(RAW_BE_FILE, "rb") as f:
    raw = f.read()

assert len(raw) == 0x400000, f"Unexpected size: {len(raw)}"

# 1. Convert 32-bit big-endian words to standard little-endian ARM flash layout
words = struct.unpack(f">{len(raw)//4}I", raw)
data = bytearray(struct.pack(f"<{len(words)}I", *words))

with open(PERSONAL_LE_FILE, "wb") as f:
    f.write(data)

print("First 16 bytes (little-endian):", data[:16])

# 2. Verify TA-1235 firmware strings
for tag in ["20.08.11", "TA-1235", PRODUCT_CODE, "Nokia", "MMM"]:
    pos_a = data.find(tag.encode("ascii"))
    pos_u = data.find(tag.encode("utf-16le"))
    print(f"  {tag:12s} -> ASCII: {hex(pos_a) if pos_a != -1 else 'no'} | UTF-16LE: {hex(pos_u) if pos_u != -1 else 'no'}")

# 3. Scrub IMEIs (ASCII & BCD)
def imei_to_bcd(imei):
    padded = imei + "F"
    return bytes((int(padded[i+1], 16) << 4) | int(padded[i], 16) for i in range(0, 16, 2))

for imei in IMEIS:
    if imei.startswith("35000000000000"):
        continue
    for pat, label in [(imei.encode("ascii"), "ASCII"), (imei_to_bcd(imei), "BCD")]:
        idx = 0
        while (idx := data.find(pat, idx)) != -1:
            print(f"  Scrubbing {label} IMEI match at 0x{idx:08X}")
            data[idx:idx+len(pat)] = b"\xFF" * len(pat)
            idx += len(pat)

# 4. Wipe writable FAT/NVRAM region (0x003A0000 - 0x00400000)
fat_offset = data.find(b"\xEB\x58\x90", 0x00200000)
if fat_offset == -1:
    fat_offset = data.find(b"FAT12", 0x00200000)
if fat_offset != -1:
    block_start = fat_offset & ~0xFFFF
    print(f"  Wiping writable FAT/NVRAM partition from 0x{block_start:08X} to 0x00400000")
    data[block_start:0x00400000] = b"\xFF" * (0x00400000 - block_start)

with open(PUBLIC_CLEAN_FILE, "wb") as f:
    f.write(data)

print(f"Saved public sanitized dump: {PUBLIC_CLEAN_FILE}")