import serial
import struct
import time

PORT = "COM6"
OUT_FILE = "TA-1030_059Z0C5_11.02.11_RAW.bin"
FLASH_SIZE = 0x1000000  # 16MB NOR flash on TA-1030

print(f"Waiting for Nokia USB Serial Port on {PORT}... Plug in powered-off phone now.")

while True:
    try:
        ser = serial.Serial(PORT, baudrate=115200, timeout=0.05)
        break
    except serial.SerialException:
        time.sleep(0.01)

print(f"Connected to {PORT}! Sending MT6260 BootROM handshake...")

# Standard MTK BROM start sequence: A0 -> 5F, 0A -> F5, 50 -> AF, 05 -> FA
for b, expected in [(0xA0, 0x5F), (0x0A, 0xF5), (0x50, 0xAF), (0x05, 0xFA)]:
    while True:
        ser.write(bytes([b]))
        resp = ser.read(1)
        if resp == bytes([expected]):
            break

print("Handshake OK! Disabling watchdog & mapping SPI flash to 0x00000000...")
ser.timeout = 2.0

def write32(addr, val):
    ser.write(b"\xD4" + struct.pack(">II", addr, 1))
    assert ser.read(9) == b"\xD4" + struct.pack(">II", addr, 1)
    assert ser.read(2) == b"\x00\x01"
    ser.write(struct.pack(">I", val))
    assert ser.read(4) == struct.pack(">I", val)
    assert ser.read(2) == b"\x00\x01"

# Disable WDT (0xA0030000 = 0x2200) & map SPI flash to address 0 (0xA0510000 = 2)
write32(0xA0030000, 0x2200)
write32(0xA0510000, 2)

print(f"Dumping {FLASH_SIZE // (1024*1024)}MB to {OUT_FILE}...")
CHUNK_WORDS = 0x400  # 4KB per read32 request
CHUNK_BYTES = CHUNK_WORDS * 4

with open(OUT_FILE, "wb") as f:
    for addr in range(0, FLASH_SIZE, CHUNK_BYTES):
        ser.write(b"\xD1" + struct.pack(">II", addr, CHUNK_WORDS))
        echo = ser.read(9)
        status1 = ser.read(2)
        data = ser.read(CHUNK_BYTES)
        status2 = ser.read(2)
        if len(data) != CHUNK_BYTES:
            raise RuntimeError(f"Short read at 0x{addr:08X}: got {len(data)} bytes")
        f.write(data)
        if addr % 0x100000 == 0:
            print(f"  Read {addr // (1024*1024)} / {FLASH_SIZE // (1024*1024)} MB...")

print("Done! Saved full 16MB dump.")
ser.close()
