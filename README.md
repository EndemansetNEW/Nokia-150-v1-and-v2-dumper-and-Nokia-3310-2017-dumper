# Nokia-150-v1-and-v2-dumper-and-Nokia-3310-2017-dumper

BootROM SPI NOR flash dumper and IMEI/NVRAM sanitizer for MediaTek Series 30+ Nokia feature phones:
- **Nokia 3310 (2017)** (`TA-1030` — MT6260A, 16MB)
- **Nokia 150 (2016 / v1)** (`RM-1189` / `RM-1190` — MT6260A, 4MB)
- **Nokia 150 (2020 / v2)** (`TA-1235` — MT6261D, 4MB)

## Requirements
- **Python 3.8+**
- **`pyserial`**:
  ```bash
  pip install pyserial
  ```
- **MediaTek / Nokia USB Serial Driver** (check Windows **Device Manager > Ports (COM & LPT)** when plugging in the powered-off phone to see which `COM` port is assigned, e.g., `COM6`).

## How to Use

1. **Dump the SPI NOR flash (`dump_mtk_nokia.py`):**
   - Pull the battery out of your phone.
   - Run the dumper (defaults to `COM6`, or pass your `COM` port as the first argument):
     ```bash
     python dump_mtk_nokia.py COM6
     ```
   - Plug in the micro-USB cable and drop the battery back in (no button hold is usually needed, though holding the **Top-Left Softkey** or **`0`** works if it goes straight to the charging screen).
   - The script automatically detects `4MB`, `8MB`, or `16MB` flash boundaries and saves `Nokia_MTK_RAW.bin`.

2. **Byte-swap & sanitize before sharing (`clean_mtk_dump.py`):**
   - Dial `*#06#` on your phone to get your 15-digit IMEI(s), then run:
     ```bash
     python clean_mtk_dump.py Nokia_MTK_RAW.bin <IMEI1> <IMEI2>
     ```
   - This converts the big-endian BootROM words into standard little-endian ARM layout (`SF_BOOT`) and outputs two files:
     - `*_PERSONAL_FULL.bin` — Full 1:1 backup with your IMEI and NVRAM intact (**keep private!**).
     - `*_CLEAN.bin` — Sanitized public image with your IMEI(s) and writable FAT/NVRAM partition wiped to `0xFF`.

## Example Output

```text
C:\mtk_dump-win64>python dump_mtk_nokia.py COM6
Waiting for Nokia USB Serial Port on COM6... Plug in powered-off phone now.
Connected to COM6! Sending MT6260/MT6261 BootROM handshake...
Handshake OK! Disabling watchdog & mapping SPI flash...
  Read 0 MB...
  Read 1 MB...
  Read 2 MB...
  Read 3 MB...
Detected exact flash boundary at 4 MB! Stopping cleanly.
Done! Saved Nokia_MTK_RAW.bin

C:\mtk_dump-win64>python clean_mtk_dump.py Nokia_MTK_RAW.bin 350000000000000 350000000000001
Detected: Model=UNKNOWN | Version=40.00.11 | ProductCode=059X998 | Size=4MB
  Wiping writable FAT/NVRAM partition from 0x00210000 to 0x00400000
Saved: UNKNOWN_059X998_40.00.11_CLEAN.bin (and private UNKNOWN_059X998_40.00.11_PERSONAL_FULL.bin)
```
Remember : 
- replace 350000000000000 and 350000000000001 with your actual IMEI(s)
  
