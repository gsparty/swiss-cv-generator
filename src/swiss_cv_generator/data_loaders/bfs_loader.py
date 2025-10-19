"""
BFS / PxWeb loader using pxwebpy (more robust than raw requests).

This loader:
 - creates a PxTable for the target table
 - inspects available variables and values
 - builds a "select all" query automatically
 - fetches the data and returns a pandas DataFrame
 - writes a CSV to out_csv

Usage:
    from swiss_cv.data_loaders.bfs_loader import fetch_bfs_table_by_id
    df = fetch_bfs_table_by_id("px-x-0102010000_101", "data/raw/canton_population.csv", language="en")

Note: pxwebpy will request JSON-stat2 and parse metadata properly.
"""
from typing import Optional
from pxwebpy.table import PxTable
import pandas as pd
import os
import logging
import time

logger = logging.getLogger(__name__)

def _build_select_all_query(tbl: PxTable):
    """
    Given a PxTable with metadata loaded, return a dict mapping variable->list(values)
    that selects all available values for each variable. This can be passed to tbl.create_query().
    """
    variables = tbl.get_table_variables()  # returns dict var_name -> [value labels or codes]
    # pxwebpy returns values as strings (labels). We'll pass them directly.
    query = {}
    for var, values in variables.items():
        # Some variables include an entry like 'tabellinnehåll' that is not desirable; keep everything for full export
        query[var] = values
    return query

def fetch_px_table_to_csv(px_table_url: str, out_csv: str, retry: int = 2):
    """
    Fetch a PxWeb table defined by full PX .px URL using pxwebpy.
    Example px_table_url:
      'https://www.pxweb.bfs.admin.ch/pxweb/en/px-x-0102010000_101/px-x-0102010000_101.px'
    """
    attempt = 0
    last_exc = None
    while attempt <= retry:
        try:
            tbl = PxTable(url=px_table_url)
            # get_table_variables will populate metadata
            variables = tbl.get_table_variables()
            if not variables:
                raise RuntimeError("No variables discovered for table; table may be protected or URL invalid.")
            # Build a full query selecting all values for each variable
            select_all = _build_select_all_query(tbl)
            tbl.create_query(select_all)
            tbl.get_data()  # populates tbl.dataset and tbl.metadata
            df = pd.DataFrame(tbl.dataset)
            os.makedirs(os.path.dirname(out_csv), exist_ok=True)
            df.to_csv(out_csv, index=False, encoding="utf-8")
            logger.info("Saved %d rows to %s", len(df), out_csv)
            return df
        except Exception as e:
            last_exc = e
            logger.warning("Attempt %d: error fetching px table: %s", attempt+1, e)
            attempt += 1
            time.sleep(1 + attempt*1.5)
    # after retries, re-raise with helpful message
    raise RuntimeError(f"Failed to fetch px table after {retry+1} attempts. Last error: {last_exc}")

def build_px_url_from_id(table_id: str, language: str = 'en') -> str:
    """
    Build the pxweb URL for BFS STAT-TAB table id.
    """
    # pattern: https://www.pxweb.bfs.admin.ch/pxweb/{lang}/{table_id}/{table_id}.px
    return f"https://www.pxweb.bfs.admin.ch/pxweb/{language}/{table_id}/{table_id}.px"

def fetch_bfs_table_by_id(table_id: str, out_csv: str, language: str = 'en', retry: int = 2):
    url = build_px_url_from_id(table_id, language=language)
    return fetch_px_table_to_csv(url, out_csv, retry=retry)

if __name__ == '__main__':
    example_out = os.path.join(os.getcwd(), 'data', 'raw', 'canton_population_pxwebpy.csv')
    # Try common languages in order if the default returns server error
    tried = []
    for lang in ['en','de','fr','it']:
        try:
            print(f"Trying language {lang} ...")
            fetch_bfs_table_by_id('px-x-0102010000_101', example_out, language=lang)
            print("success")
            break
        except Exception as e:
            tried.append((lang, str(e)))
            print(f"failed for {lang}: {e}")
    if len(tried) == 4:
        print("All language attempts failed; see exceptions above for details.")



