# Nokia-150-v1-and-v2-dumper-and-Nokia-3310-2017-dumper

how to use :
requires python 3.14+
have pyserial installed

and run python dumpnokia150.py / dumpnokia33102017.py (for your device)
then run clean_mtk_dump.py to get both clean and personal dumps
------------------------------------------------------------------------------------------------------------------------
example :
```sh
C:\Users\Endemanset (Gooner)\Downloads\mtk_dump-win64>python dump_mtk_nokia.py
Waiting for Nokia USB Serial Port on COM6... Plug in powered-off phone now.
Connected to COM6! Sending MT6260/MT6261 BootROM handshake...
Handshake OK! Disabling watchdog & mapping SPI flash...
  Read 0 MB...
  Read 1 MB...
  Read 2 MB...
  Read 3 MB...
Detected exact flash boundary at 4 MB! Stopping cleanly.
Done! Saved Nokia_MTK_RAW.bin

C:\Users\Endemanset (Gooner)\Downloads\mtk_dump-win64>python clean_mtk_dump.py Nokia_MTK_RAW.bin "put imei1 here" "put imei 2 here"
Detected: Model=UNKNOWN | Version=40.00.11 | ProductCode=059X998 | Size=4MB
  Wiping writable FAT/NVRAM partition from 0x00210000 to 0x00400000
Saved: UNKNOWN_059X998_40.00.11_CLEAN.bin (and private UNKNOWN_059X998_40.00.11_PERSONAL_FULL.bin)

C:\Users\Endemanset (Gooner)\Downloads\mtk_dump-win64>
```
