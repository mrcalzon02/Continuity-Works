from pathlib import Path
from urllib.request import urlopen

URL = "https://donjon.bin.sh/code/dungeon/dungeon.pl"
TARGET = Path(__file__).with_name("dungeon.pl")

with urlopen(URL, timeout=30) as response:
    data = response.read()
if b"Creative Commons Attribution-NonCommercial 3.0" not in data:
    raise SystemExit("Upstream license marker was not found; refusing to save an unverified source response")
TARGET.write_bytes(data)
print(f"Saved {len(data)} bytes to {TARGET}")
