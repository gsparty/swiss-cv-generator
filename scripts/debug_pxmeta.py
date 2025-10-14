from pxwebpy.table import PxTable
import sys

def inspect_table(table_id: str, language: str = "en"):
    url = f"https://www.pxweb.bfs.admin.ch/pxweb/{language}/{table_id}/{table_id}.px"
    print("Inspecting:", url)
    tbl = PxTable(url=url)
    vars = tbl.get_table_variables()
    print("Found", len(vars), "variables.")
    for k, v in vars.items():
        print(f"== {k} ({len(v)} values) ==")
        # print up to first 12 items to keep output readable
        for item in v[:12]:
            print("   ", repr(item))
        print()

if __name__ == "__main__":
    # try languages in order
    for lang in ("en", "de", "fr", "it"):
        try:
            print("\\n--- LANG:", lang, "---")
            inspect_table("px-x-0102010000_101", language=lang)
        except Exception as e:
            print("Error inspecting table for language", lang, ":", e)
            import traceback
            traceback.print_exc()
