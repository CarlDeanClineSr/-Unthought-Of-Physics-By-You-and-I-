#!/usr/bin/env python3
"""
Create a pretty HTML table of all capsule status. Paste in same repo.
Reads manifest_master_index.yaml, outputs docs/manifest_dashboard.html
"""

import yaml
from datetime import datetime

def color_status(status):
    return {
        "green": "#B7FBAB",
        "red": "#FDBCB9",
        "pending": "#FFF49C"
    }.get(status, "#EFF2F3")

def main(index_file="manifest_master_index.yaml", out_file="docs/manifest_dashboard.html"):
    with open(index_file, "r") as f:
        manifest = yaml.safe_load(f)
    rows = []
    for cid, capsule in manifest.items():
        rows.append(f"""
        <tr style='background:{color_status(capsule.get("status",""))};'>
            <td>{capsule.get("capsule_id","")}</td>
            <td>{capsule.get("timestamp_utc","")}</td>
            <td>{capsule.get("source_node","")}</td>
            <td>{capsule.get("event_type","")}</td>
            <td>{capsule.get("status","")}</td>
            <td>{capsule.get("inputs",{}).get("chi","")}</td>
            <td>{capsule.get("inputs",{}).get("density","")}</td>
            <td>{capsule.get("inputs",{}).get("speed","")}</td>
            <td>{', '.join(capsule.get('tags', []))}</td>
            <td><a href='{capsule.get("ledger_link","#")}' target='_blank'>Capsule</a></td>
        </tr>
        """)
    now = datetime.utcnow().isoformat()
    html = f"""
    <html>
    <head>
        <title>LUFT Master Capsule Dashboard</title>
        <style>
            body {{ font-family: Arial,sans-serif; background:#fcfcfc; }}
            th,td {{ padding:4px 8px; font-size:13px; }}
            th {{ background:#334555; color:#fff; }}
            table {{ border-collapse:collapse; width:100%; margin-top:20px; }}
            tr:hover {{ background:#d0edff; }}
        </style>
    </head>
    <body>
        <h2>LUFT Capsule Vault — Master Dashboard</h2>
        <p><b>Updated:</b> {now} UTC</p>
        <table border="1">
            <tr>
                <th>Capsule ID</th>
                <th>Timestamp (UTC)</th>
                <th>Source Node</th>
                <th>Event Type</th>
                <th>Status</th>
                <th>χ</th>
                <th>Density</th>
                <th>Speed</th>
                <th>Tags</th>
                <th>Capsule Link</th>
            </tr>
            {''.join(rows)}
        </table>
        <p style='color:#666;'>Green: confirmed | Red: failed/problem | Yellow: pending/review.</p>
    </body></html>
    """
    with open(out_file,"w") as f:
        f.write(html)
    print(f"Wrote dashboard to {out_file}")

if __name__ == "__main__":
    main()
