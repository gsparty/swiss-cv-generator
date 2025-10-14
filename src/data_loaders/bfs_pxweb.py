import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional

# Generic PXWeb client helpers for BFS / pxweb endpoints.
# Usage:
#   from src.data_loaders.bfs_pxweb import px_query, fetch_and_save_px
#   resp = px_query("https://pxweb.bfs.admin.ch/api/v1/en/px-x/...", {"query": [...], "response": {"format": "json"}})
#   fetch_and_save_px("https://pxweb.example/dataset", payload, out_dir="data/raw/")

def px_query(api_url: str, query: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
    """
    POST a PXWeb-style JSON query to a PX endpoint and return the parsed JSON response.
    The 'query' param should follow PXWeb JSON query conventions for the dataset.
    """
    headers = {"Content-Type": "application/json"}
    r = requests.post(api_url, json=query, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.json()

def save_px_response(resp: Dict[str, Any], prefix: str = "px_response", out_dir: str = "data/raw/") -> Path:
    """
    Save the JSON px response to a timestamped file in out_dir and return the Path.
    """
    p = Path(out_dir)
    p.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    fname = f"{prefix}_{ts}.json"
    out_path = p / fname
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(resp, f, ensure_ascii=False, indent=2)
    return out_path

def fetch_and_save_px(api_url: str, query: Dict[str, Any], prefix: Optional[str] = None, out_dir: str = "data/raw/") -> Path:
    """
    Convenience: POST the query to the provided api_url then save the response to out_dir.
    Returns the file Path of the saved JSON.
    """
    if prefix is None:
        prefix = "px_response"
    resp = px_query(api_url, query)
    return save_px_response(resp, prefix=prefix, out_dir=out_dir)

def try_extract_1d_series(px_resp: Dict[str, Any], suspect_dimension_names=None) -> Dict[str, float]:
    """
    Attempt to extract a simple 1D series of (label -> value) from a PX response.
    This helper only works if the PX response is effectively one-dimensional (or the value array
    can be reduced to a single dimension). It is a best-effort tool for quick inspection.
    Returns a mapping label -> numeric value when possible, otherwise raises ValueError.
    """
    if suspect_dimension_names is None:
        suspect_dimension_names = ["canton","kanton","geo","geography","region","geog","geo", "GEOGRAF", "GE"]

    dims = px_resp.get("dimension", {})
    values = px_resp.get("value")
    if values is None:
        raise ValueError("PX response has no 'value' key")

    # If values is a dict (some px outputs), try 'value' as mapping
    if isinstance(values, dict):
        # values already mapping of index -> value; try labels
        # Some px returns values keyed by category codes; this function will try best-effort mapping
        labels = {}
        for dname, ddata in dims.items():
            cats = ddata.get("category", {}).get("label", {})
            # choose the first dimension which has labels matching suspect names
            for candidate in suspect_dimension_names:
                if candidate.lower() in dname.lower():
                    # map category keys to labels
                    for k, lab in cats.items():
                        # value lookup might be direct by key
                        if k in values:
                            try:
                                labels[lab] = float(values[k])
                            except Exception:
                                labels[lab] = values[k]
                    if labels:
                        return labels
        # fallback: return values as-is (converted to numeric where possible)
        out = {}
        for k, v in values.items():
            try:
                out[k] = float(v)
            except Exception:
                out[k] = v
        return out

    # If values is a list/array (multi-dim), we try to reduce if one dimension is present
    if isinstance(values, list):
        # Build dims order and sizes
        dim_order = []
        dim_sizes = []
        dim_labels = []
        for dname, ddata in dims.items():
            cat = ddata.get("category", {})
            labels = cat.get("label")
            if labels:
                # label dict where keys are codes, values are labels - turn into list preserving insertion if possible
                lab_list = list(labels.values())
            else:
                lab_list = []
            dim_order.append(dname)
            dim_sizes.append(len(lab_list) or 0)
            dim_labels.append(lab_list)

        # If exactly one non-empty label dimension and values length matches, map directly
        non_empty_dims = [i for i, labs in enumerate(dim_labels) if labs]
        if len(non_empty_dims) == 1 and len(values) == len(dim_labels[non_empty_dims[0]]):
            lab_list = dim_labels[non_empty_dims[0]]
            out = {}
            for lab, val in zip(lab_list, values):
                try:
                    out[lab] = float(val)
                except Exception:
                    out[lab] = val
            return out

        raise ValueError("PX response appears multi-dimensional; try manual inspection of saved JSON.")

    raise ValueError("PX response 'value' has unexpected type.")
class BFSClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def fetch(self, table: str, params: dict) -> dict:
        pass

