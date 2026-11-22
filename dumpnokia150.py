import serial
import struct
import time

PORT = "COM6"
OUT_FILE = "Nokia150v1_RAW.bin"  # Rename with your RM-1189/1190 & Product Code after
MAX_FLASH_SIZE = 0x1000000      # Checks 4MB, 8MB, up to 16MB automatically

print(f"Waiting for Nokia USB Serial Port on {PORT}... Plug in powered-off Nokia 150 v1 now.")

while True:
    try:
        ser = serial.Serial(PORT, baudrate=115200, timeout=0.05)
        break
    except serial.SerialException:
        time.sleep(0.01)

print(f"Connected to {PORT}! Sending MT6260 BootROM handshake...")

for b, expected in [(0xA0, 0x5F), (0x0A, 0xF5), (0x50, 0xAF), (0x05, 0xFA)]:
    while True:
        ser.write(bytes([b]))
        if ser.read(1) == bytes([expected]):
            break

print("Handshake OK! Disabling watchdog & mapping SPI flash...")
ser.timeout = 2.0

def write32(addr, val):
    ser.write(b"\xD4" + struct.pack(">II", addr, 1))
    assert ser.read(9) == b"\xD4" + struct.pack(">II", addr, 1)
    assert ser.read(2) == b"\x00\x01"
    ser.write(struct.pack(">I", val))
    assert ser.read(4) == struct.pack(">I", val)
    assert ser.read(2) == b"\x00\x01"

write32(0xA0030000, 0x2200)
write32(0xA0510000, 2)

CHUNK_WORDS = 0x400
CHUNK_BYTES = CHUNK_WORDS * 4
first_header = None

with open(OUT_FILE, "wb") as f:
    for addr in range(0, MAX_FLASH_SIZE, CHUNK_BYTES):
        ser.write(b"\xD1" + struct.pack(">II", addr, CHUNK_WORDS))
        ser.read(9)
        ser.read(2)
        data = ser.read(CHUNK_BYTES)
        ser.read(2)
        if len(data) != CHUNK_BYTES:
            raise RuntimeError(f"Short read at 0x{addr:08X}")
        if addr == 0:
            first_header = data[:32]
        elif addr in (0x400000, 0x800000) and data[:32] == first_header:
            print(f"Detected exact flash boundary at {addr // (1024*1024)} MB! Stopping cleanly.")
            break
        f.write(data)
        if addr % 0x100000 == 0:
            print(f"  Read {addr // (1024*1024)} MB...")

print(f"Done! Saved {OUT_FILE}")
ser.close()
