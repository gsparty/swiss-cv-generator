import csv, sys, codecs
p = "data/cantons.csv"
print("Reading file:", p)
try:
    # try to detect encoding by reading BOM
    with open(p, "rb") as fh:
        raw = fh.read(64)
    print("First 64 bytes (hex):", raw[:64].hex())
except Exception as e:
    print("Could not read raw bytes:", e)
try:
    with open(p, newline="", encoding="utf-8") as fh:
        lines = [next(fh) for _ in range(5)]
    print("--- Raw first 5 text lines ---")
    for i,l in enumerate(lines):
        print(i, repr(l))
except Exception as e:
    print("Error reading text lines:", e)
try:
    with open(p, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        print("DictReader.fieldnames:", reader.fieldnames)
        print("First 3 rows as dicts:")
        for i, r in enumerate(reader):
            print("ROW", i, r)
            if i >= 2:
                break
except Exception as e:
    print("Error using csv.DictReader:", e)
