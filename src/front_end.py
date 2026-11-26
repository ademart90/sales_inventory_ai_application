import os
import json
from datetime import datetime

import requests
import streamlit as st

FASTAPI_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
SALES_SUMMARY_ROUTE = os.getenv('report_router', '/latest_summary')
SALES_JSON_PATH = os.path.join("json_uploads", "sales_summary.json")

CACHE_SECONDS = 30      # how long a fetched result is reused
AUTO_REFRESH = "60s"    # how often the KPI cards re-check for new data
REQUEST_TIMEOUT = 30


@st.cache_data(ttl=CACHE_SECONDS, show_spinner=False)
def _fetch_live_summary() -> dict:
    """GET the latest summary from the FastAPI backend."""
    res = requests.get(f"{FASTAPI_URL}{SALES_SUMMARY_ROUTE}", 
                       headers={'Cache-control':'no-cache'},
                       timeout=REQUEST_TIMEOUT)
    res.raise_for_status()
    return res.json()


def _read_json_file() -> tuple[dict, float]:
    """Fallback: read the local JSON file. Returns (data, last-modified timestamp)."""
    with open(SALES_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data, os.path.getmtime(SALES_JSON_PATH)


def _load_summary() -> tuple[dict, str]:
    """Return (summary, source label). Tries the backend first, then the JSON file."""
    try:
        data = _fetch_live_summary()
        return data.get("summary", data), "live from backend"
    except Exception:
        if not os.path.exists(SALES_JSON_PATH):
            raise FileNotFoundError(
                f"Backend unreachable and no fallback file at `{SALES_JSON_PATH}`."
            )
        data, mtime = _read_json_file()
        stamp = datetime.fromtimestamp(mtime).strftime("%d %b %Y, %H:%M")
        return data.get("summary", data), f"saved file (last updated {stamp})"


def _totals(block: dict) -> tuple[float, float]:
    products = block.get("products", [])
    revenue = sum(p.get("total_revenue", 0) for p in products)
    profit = sum(p.get("profit", 0) for p in products)
    return revenue, profit


@st.fragment(run_every=AUTO_REFRESH)
def render_kpi_banner():
    """Show 4 store KPI cards with the latest sales data.

    Pulls from the backend's /sales_summary endpoint, falls back to
    json_uploads/sales_summary.json, and re-checks every minute without
    rerunning the rest of the page.
    """
    try:
        summary, source = _load_summary()
    except Exception as e:
        st.warning(f"Could not load KPI summary: {e}")
        return

    curr = summary.get("last_recorded_sales", {})
    w7 = summary.get("last_7_days", {})
    m30 = summary.get("last_30_days", {})

    curr_rev, curr_prof = _totals(curr)
    w7_rev, w7_prof = _totals(w7)
    m30_rev, m30_prof = _totals(m30)

    # Highest-revenue product over the last 30 days
    products_30d = m30.get("products", [])
    if products_30d:
        top_item = max(products_30d, key=lambda x: x.get("total_revenue", 0))
        top_sku = str(top_item.get("product_name", "N/A")).title()
        top_sku_rev = f"₦{top_item.get('total_revenue', 0):,.2f} (30d)"
    else:
        top_sku = "N/A"
        top_sku_rev = "No sales data"

    k1, k2, k3, k4 = st.columns(4)
    k1.metric(
        label="Latest Day Revenue",
        value=f"₦{curr_rev:,.2f}",
        delta=f"Date: {curr.get('end_date', 'N/A')}",
        delta_color="off",
    )
    k2.metric(
        label="Last 7 Days Revenue",
        value=f"₦{w7_rev:,.2f}",
        delta=f"Profit: ₦{w7_prof:,.2f}",
    )
    k3.metric(
        label="Last 30 Days Revenue",
        value=f"₦{m30_rev:,.2f}",
        delta=f"Profit: ₦{m30_prof:,.2f}",
    )
    k4.metric(
        label="Top Performing SKU",
        value=top_sku,
        delta=top_sku_rev,
    )

    # Freshness line + manual refresh (kept outside st.columns so the
    # starter-tile button styling in app.py doesn't apply to it)
    st.caption(f"Data: {source} • checked {datetime.now().strftime('%H:%M:%S')}")
    if st.button("Refresh data", key="kpi_refresh"):
        _fetch_live_summary.clear()
        st.rerun(scope="fragment")

    st.divider()