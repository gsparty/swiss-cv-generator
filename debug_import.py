import sys, os, importlib, traceback
print("CWD:", os.getcwd())
print("First 10 sys.path entries:")
for p in sys.path[:10]:
    print(" -", p)
try:
    importlib.import_module("swisscv.cli.generate")
    print("Import swisscv.cli.generate: OK")
except Exception as e:
    print("IMPORT FAILED:")
    traceback.print_exc()
