import os
import json
import streamlit as st
from datetime import datetime
def render_kpi_banner():
    """Reads generated sales_summary.json and displays 4 live store KPI cards."""
    sales_path = "./json_uploads/sales_summary.json"
    if not os.path.exists(sales_path):
        return

    try:
        with open(sales_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        summary = data.get('summary', {})
        curr = summary.get("last_recorded_sales", {})
        w7 = summary.get("last_7_days", {})
        m30 = summary.get("last_30_days", {})

        curr_rev = sum(p.get('total_revenue', 0) for p in curr.get('products', []))
        curr_prof = sum(p.get('profit', 0) for p in curr.get('products', []))
        w7_rev = sum(p.get('total_revenue', 0) for p in w7.get('products', []))
        w7_prof = sum(p.get('profit', 0) for p in w7.get('products', []))
        m30_rev = sum(p.get('total_revenue', 0) for p in m30.get('products', []))
        m30_prof = sum(p.get('profit', 0) for p in m30.get('products', []))


        # Identify highest-revenue product over the last 30 days
        products_30d = m30.get("products", [])
        if products_30d:
            top_item = max(products_30d, key=lambda x: x.get("total_revenue", 0))
            top_sku = top_item.get("product_name", "N/A").title()
            top_sku_rev = f"₦{top_item.get('total_revenue', 0):,.2f} (30d)"
        else:
            top_sku = "N/A"
            top_sku_rev = "No sales data"

        k1, k2, k3, k4 = st.columns(4)
        k1.metric(
            label="Today's Revenue",
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
        st.divider()
    except Exception:
        # Silently skip banner if JSON is still being written
        pass
