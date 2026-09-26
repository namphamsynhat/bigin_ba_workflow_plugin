#!/usr/bin/env python3
"""
assemble_prototype.py - Design-system-agnostic engine for bigin-assemble-prototype.

Core Paradigm:
- Supports multiple Design Systems (Airbnb, IBM Carbon, Stripe, etc.) via Semantic Design Tokens.
- Supports multiple Layout Archetypes (Top-Nav / Horizontal Tabs vs. Side-Nav / Vertical Menu).
1. Follows the user type (role) and navigation map (04-UIUX/_ux/navigation-map.md).
2. Finds each frame (ux-###-scr-##-*.html) and places it directly into the application context.
3. Renders the authentic navigation shell (persistent side-nav) for that user type.
4. Enables the user to loop through all navigation items for that user type.
5. Enables moving to the next user type and looping through all its navigation items.
6. Repeats until all user types and their navigation trees are completely assembled and verified.
7. Zero developer spec inspectors or artificial module-accordion sidebars.
8. Idempotent: strictly updates index.html in place.
"""

import os
import re
import sys
import glob
import json
import argparse
from pathlib import Path

# Mapping of known aliases in navigation-map.md to specific screen filenames if names differ slightly
CANONICAL_ALIASES = {
    "portal requests queue": "ux-003-scr-08-my-requests.html",
    "request review": "ux-003-scr-07-submit-a-request.html",
    "parent account list": "ux-001-scr-03-registration-review.html",
    "family detail view": "ux-001-scr-05-portal-home.html",
    "spend chooser / hub screen": "ux-006-scr-02-payment-request-form.html",
    "spend chooser": "ux-006-scr-02-payment-request-form.html",
    "payment request review (admin)": "ux-006-scr-05-payment-request-review-admin.html",
    "payment request review": "ux-006-scr-05-payment-request-review-admin.html",
    "wallet detail & adjustment (admin)": "ux-004-scr-09-wallet-detail-adjustment-deactivation-admin.html",
    "wallet detail & adjustment & deactivation (admin)": "ux-004-scr-09-wallet-detail-adjustment-deactivation-admin.html",
    "amazon shopping requests queue (shop-03)": "ux-011-scr-03-amazon-shopping-requests-queue.html",
    "asin catalog & allowlist management (shop-04)": "ux-011-scr-04-asin-catalog-allowlist-management.html",
    "admin overview & dashboard": "ux-008-scr-01-admin-overview-dashboard.html",
    "cycle spend ledger (rpt-01)": "ux-008-scr-02-cycle-spend-ledger-rpt-01.html",
    "cycle spend ledger [rpt-01]": "ux-008-scr-02-cycle-spend-ledger-rpt-01.html",
    "usbe biannual sgo report (rpt-02)": "ux-008-scr-03-usbe-biannual-sgo-report-rpt-02.html",
    "school tuition reconciliation (rpt-03)": "ux-008-scr-04-school-tuition-reconciliation-rpt-03.html",
    "donor tax credit cap tracker (rpt-04)": "ux-008-scr-05-donor-tax-credit-cap-tracker-rpt-04.html",
    "reports catalog & ledgers": "ux-008-scr-02-cycle-spend-ledger-rpt-01.html",
    "vendor self-service portal": "ux-005-scr-06-vendor-self-service-portal.html",
    "received tuition payments": "ux-007-scr-01-received-tuition-payments.html",
    "assigned applicants list": "ux-007-scr-02-assigned-applicants-list.html",
    "applicant certification & fee review": "ux-007-scr-03-applicant-certification-fee-review.html",
    "tuition & fee schedule declaration": "ux-007-scr-04-tuition-fee-schedule-declaration.html",
    "mid-cycle tuition fee adjustment review": "ux-007-scr-05-mid-cycle-tuition-fee-adjustment-review.html",
    "parent fee adjustment request drawer": "ux-007-scr-06-parent-fee-adjustment-request-drawer.html",
    "universal messaging panel / drawer": "ux-009-scr-01-universal-messaging-panel-drawer.html",
    "universal messaging drawer": "ux-009-scr-01-universal-messaging-panel-drawer.html",
    "notification channel preferences": "ux-009-scr-02-notification-channel-preferences.html",
    "cycle management": "ux-010-scr-01-cycle-management.html",
    "attestation versions": "ux-010-scr-04-attestation-versions.html",
    "cycle detail": "ux-010-scr-02-cycle-detail.html",
    "award cycle status dashboard": "ux-010-scr-03-award-cycle-status-dashboard.html",
    "attestation re-acknowledgment prompt": "ux-010-scr-05-attestation-re-acknowledgment-prompt.html",
    "approved products catalog & cart": "ux-011-scr-01-approved-products-catalog-cart.html",
    "order confirmation & tracking": "ux-011-scr-02-order-confirmation-tracking.html",
    "donor dashboard": "ux-002-scr-05-donor-dashboard.html",
    "donor list": "ux-002-scr-02-donor-list.html",
    "unposted gifts queue": "ux-002-scr-03-unposted-gifts-queue.html",
    "record donation": "ux-002-scr-01-record-donation.html",
    "donor profile": "ux-002-scr-04-donor-profile.html"
}

# Canonical SVG icons for IBM Carbon Design System navigation items
CARBON_ICONS = {
    "Document": """<svg class="nav-icon" width="16" height="16" viewBox="0 0 32 32" fill="currentColor"><path d="M25.7,9.3l-7-7C18.5,2.1,18.3,2,18,2H8C6.9,2,6,2.9,6,4v24c0,1.1,0.9,2,2,2h16c1.1,0,2-0.9,2-2V10C26,9.7,25.9,9.5,25.7,9.3z M18,4.4l5.6,5.6H18V4.4z M24,28H8V4h8v7c0,0.6,0.4,1,1,1h7V28z"/><path d="M11 16H21V18H11zM11 22H21V24H11z"/></svg>""",
    "UserFollow": """<svg class="nav-icon" width="16" height="16" viewBox="0 0 32 32" fill="currentColor"><path d="M22 14c0-3.3-2.7-6-6-6s-6 2.7-6 6 2.7 6 6 6 6-2.7 6-6zm-10 0c0-2.2 1.8-4 4-4s4 1.8 4 4-1.8 4-4 4-4-1.8-4-4zm18 16h-2c0-4.4-3.6-8-8-8H12c-4.4 0-8 3.6-8 8H2c0-5.5 4.5-10 10-10h8c5.5 0 10 4.5 10 10z"/><path d="M27 12h-3V9h-2v3h-3v2h3v3h2v-3h3z"/></svg>""",
    "Wallet": """<svg class="nav-icon" width="16" height="16" viewBox="0 0 32 32" fill="currentColor"><path d="M26,6H6A2,2,0,0,0,4,8V24a2,2,0,0,0,2,2H26a2,2,0,0,0,2-2V8A2,2,0,0,0,26,6ZM6,8H26v2H6ZM26,24H6V12H26Zm-4-7a1.5,1.5,0,1,0,1.5,1.5A1.5,1.5,0,0,0,22,17Z"/></svg>""",
    "Badge": """<svg class="nav-icon" width="16" height="16" viewBox="0 0 32 32" fill="currentColor"><path d="M16 2L4 7v8c0 7.8 5.1 14.5 12 17 6.9-2.5 12-9.2 12-17V7L16 2zm10 13c0 6.6-4.3 12.4-10 14.7C10.3 27.4 6 21.6 6 15V8.5l10-4.2 10 4.2V15z"/></svg>""",
    "Receipt": """<svg class="nav-icon" width="16" height="16" viewBox="0 0 32 32" fill="currentColor"><path d="M25 4H7a2 2 0 0 0-2 2v22l4-2 4 2 4-2 4 2 4-2 4 2V6a2 2 0 0 0-2-2zm0 21.6-2-1-4 2-4-2-4 2-2-1V6h16z"/><path d="M10 10H22V12H10zM10 15H22V17H10zM10 20H18V22H10z"/></svg>""",
    "ShoppingCart": """<svg class="nav-icon" width="16" height="16" viewBox="0 0 32 32" fill="currentColor"><path d="M28.8 8.4A1.9 1.9 0 0 0 27.2 7.6H7.1L6.3 3.8A2 2 0 0 0 4.3 2.2H2v2h2.3l3.6 17.5A2 2 0 0 0 9.9 23.3H25v-2H9.9l-.6-3H26a2 2 0 0 0 1.9-1.4l2-7.4a2 2 0 0 0-1.1-1.1zM26 16.3H8.9l-1.4-6.7h19.7zM10.5 25a2.5 2.5 0 1 0 2.5 2.5 2.5 2.5 0 0 0-2.5-2.5zm12 0a2.5 2.5 0 1 0 2.5 2.5 2.5 2.5 0 0 0-2.5-2.5z"/></svg>""",
    "Finance": """<svg class="nav-icon" width="16" height="16" viewBox="0 0 32 32" fill="currentColor"><path d="M26 4H6a2 2 0 0 0-2 2v20a2 2 0 0 0 2 2h20a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 2v4H6V6zm0 20H6V12h20zm-8-6h6v2h-6zm0-4h6v2h-6z"/></svg>""",
    "UserMultiple": """<svg class="nav-icon" width="16" height="16" viewBox="0 0 32 32" fill="currentColor"><path d="M30 24h-2c0-3.3-2.7-6-6-6h-3.4c1.5-1.1 2.4-2.9 2.4-5 0-3.3-2.7-6-6-6s-6 2.7-6 6c0 2.1 1 3.9 2.4 5H8c-3.3 0-6 2.7-6 6H0c0-4.4 3.6-8 8-8h1.2C8.4 16.1 8 14.6 8 13c0-3.9 3.1-7 7-7s7 3.1 7 7c0 1.6-.4 3.1-1.2 4.4H22c4.4 0 8 3.6 8 8z"/></svg>""",
    "Events": """<svg class="nav-icon" width="16" height="16" viewBox="0 0 32 32" fill="currentColor"><path d="M26 4h-4V2h-2v2h-8V2h-2v2H6a2 2 0 0 0-2 2v20a2 2 0 0 0 2 2h20a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 22H6V10h20zm0-18H6V6h4v2h2V6h8v2h2V6h4z"/></svg>""",
    "Store": """<svg class="nav-icon" width="16" height="16" viewBox="0 0 32 32" fill="currentColor"><path d="M28 8H4a2 2 0 0 0-2 2v4a4 4 0 0 0 2 3.5V26a2 2 0 0 0 2 2h20a2 2 0 0 0 2-2v-8.5A4 4 0 0 0 30 14v-4a2 2 0 0 0-2-2zM4 10h24v4a2 2 0 0 1-4 0v-1h-2v1a2 2 0 0 1-4 0v-1h-2v1a2 2 0 0 1-4 0v-1h-2v1a2 2 0 0 1-4 0zm22 16H6V18.8a4 4 0 0 0 2 .2 4 4 0 0 0 3.2-1.6 4 4 0 0 0 6.4 0 4 4 0 0 0 6.4 0A4 4 0 0 0 26 19z"/></svg>""",
    "Favorite": """<svg class="nav-icon" width="16" height="16" viewBox="0 0 32 32" fill="currentColor"><path d="M22.5 4c-2.7 0-5.1 1.4-6.5 3.5C14.6 5.4 12.2 4 9.5 4 4.8 4 1 7.8 1 12.5c0 6.7 9.1 13.9 14.5 17.1.3.2.7.2 1 0 5.4-3.2 14.5-10.4 14.5-17.1C31 7.8 27.2 4 22.5 4z"/></svg>""",
    "Identification": """<svg class="nav-icon" width="16" height="16" viewBox="0 0 32 32" fill="currentColor"><path d="M26 4H6a2 2 0 0 0-2 2v20a2 2 0 0 0 2 2h20a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 22H6V6h20z"/><path d="M10 10h4v4h-4zm0 8h12v2H10zm0-4h12v2H10z"/></svg>""",
    "Analytics": """<svg class="nav-icon" width="16" height="16" viewBox="0 0 32 32" fill="currentColor"><path d="M4 28V4H2v25a1 1 0 0 0 1 1h27v-2zm6-4H8V14h2zm6 0h-2V8h2zm6 0h-2V18h2zm6 0h-2V11h2z"/></svg>""",
    "Settings": """<svg class="nav-icon" width="16" height="16" viewBox="0 0 32 32" fill="currentColor"><path d="M29.5 14.4l-2.7-.5c-.2-.7-.5-1.4-.9-2.1l1.6-2.2c.4-.6.3-1.4-.2-1.9l-2.3-2.3c-.5-.5-1.3-.6-1.9-.2l-2.2 1.6c-.7-.4-1.4-.7-2.1-.9l-.5-2.7c-.1-.7-.7-1.2-1.4-1.2h-3.2c-.7 0-1.3.5-1.4 1.2l-.5 2.7c-.7.2-1.4.5-2.1.9L8 5.2c-.6-.4-1.4-.3-1.9.2L3.8 7.7c-.5.5-.6 1.3-.2 1.9l1.6 2.2c-.4.7-.7 1.4-.9 2.1l-2.7.5c-.7.1-1.2.7-1.2 1.4v3.2c0 .7.5 1.3 1.2 1.4l2.7.5c.2.7.5 1.4.9 2.1L3.6 25c-.4.6-.3 1.4.2 1.9l2.3 2.3c.5.5 1.3.6 1.9.2l2.2-1.6c.7.4 1.4.7 2.1.9l.5 2.7c.1.7.7 1.2 1.4 1.2h3.2c.7 0 1.3-.5 1.4-1.2l.5-2.7c.7-.2 1.4-.5 2.1-.9l2.2 1.6c.6.4 1.4.3 1.9-.2l2.3-2.3c.5-.5.6-1.3.2-1.9l-1.6-2.2c.4-.7.7-1.4.9-2.1l2.7-.5c.7-.1 1.2-.7 1.2-1.4v-3.2c0-.7-.5-1.3-1.2-1.4zM16 21c-2.8 0-5-2.2-5-5s2.2-5 5-5 5 2.2 5 5-2.2 5-5 5z"/></svg>""",
    "DocumentAdd": """<svg class="nav-icon" width="16" height="16" viewBox="0 0 32 32" fill="currentColor"><path d="M25.7 9.3l-7-7C18.5 2.1 18.3 2 18 2H8C6.9 2 6 2.9 6 4v24c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V10c0-.3-.1-.5-.3-.7zM18 4.4l5.6 5.6H18V4.4z M24 28H8V4h8v7c0 .6.4 1 1 1h7v16z"/><path d="M15 16h2v4h4v2h-4v4h-2v-4h-4v-2h4z"/></svg>""",
    "Catalog": """<svg class="nav-icon" width="16" height="16" viewBox="0 0 32 32" fill="currentColor"><path d="M26 4H6a2 2 0 0 0-2 2v20a2 2 0 0 0 2 2h20a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 2v4H6V6zm0 20H6V12h20z"/><path d="M10 16h6v2h-6zm0 5h12v2H10z"/></svg>""",
    "Purchase": """<svg class="nav-icon" width="16" height="16" viewBox="0 0 32 32" fill="currentColor"><path d="M26 6H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2zm0 2v3H6V8zm0 16H6V13h20z"/><circle cx="10" cy="18" r="2"/></svg>""",
    "Chat": """<svg class="nav-icon" width="16" height="16" viewBox="0 0 32 32" fill="currentColor"><path d="M17.7 24H6V8h20v9h2V8a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h11.7l5.3 4.4V26h3a2 2 0 0 0 2-2v-5h-2v5h-3.7l-4.6-4z"/></svg>""",
    "UserProfile": """<svg class="nav-icon" width="16" height="16" viewBox="0 0 32 32" fill="currentColor"><path d="M16 4a6 6 0 1 0 6 6 6 6 0 0 0-6-6zm0 10a4 4 0 1 1 4-4 4 4 0 0 1-4 4zm10 14h-2a8 8 0 0 0-16 0H6a10 10 0 0 1 20 0z"/></svg>""",
    "Table": """<svg class="nav-icon" width="16" height="16" viewBox="0 0 32 32" fill="currentColor"><path d="M28 4H4a2 2 0 0 0-2 2v20a2 2 0 0 0 2 2h24a2 2 0 0 0 2-2V6a2 2 0 0 0-2-2zm0 2v4H4V6zm-13 6v14H4V12zm13 14H17V12h11z"/></svg>"""
}

DEFAULT_ICON = """<svg class="nav-icon" width="16" height="16" viewBox="0 0 32 32" fill="currentColor"><circle cx="16" cy="16" r="4"/></svg>"""

def parse_screen_frames(project_dir):
    """Scans and parses all modular frame files matching ux-###-scr-##-*.html."""
    frames = []
    pattern = os.path.join(project_dir, "ux-*-scr-*.html")
    files = sorted(glob.glob(pattern))

    # Deduplicate -2.html duplicates
    unique_files = {}
    for f in files:
        fn = os.path.basename(f)
        if fn.endswith("-2.html"):
            base = fn[:-7] + ".html"
            if base not in unique_files:
                unique_files[base] = f
        else:
            unique_files[fn] = f

    for filename, filepath in sorted(unique_files.items()):
        with open(filepath, "r", encoding="utf-8") as f:
            html = f.read()

        # Extract attributes from <section ...>
        sec_match = re.search(r'<section\s+([^>]+)>', html, re.IGNORECASE)
        attrs = {}
        if sec_match:
            attr_str = sec_match.group(1)
            for k, v in re.findall(r'([\w\-]+)=["\']([^"\']+)["\']', attr_str):
                attrs[k] = v

        view_id = attrs.get("id", f"view-{filename.replace('.html','')}")
        ux_id = attrs.get("data-ux", "")
        screen_id = attrs.get("data-screen-id", "")
        screen_name = attrs.get("data-screen", "")
        role = attrs.get("data-role", "")
        screen_type = attrs.get("data-type", "Primary")

        # Extract title if missing
        if not screen_name:
            t_match = re.search(r'<title>([^<]+)</title>', html, re.IGNORECASE)
            screen_name = t_match.group(1).strip() if t_match else filename

        if not ux_id:
            m = re.search(r'(ux-\d+)', filename, re.IGNORECASE)
            if m:
                ux_id = m.group(1).upper()

        if not screen_id:
            m = re.search(r'scr-(\d+)', filename, re.IGNORECASE)
            if m:
                screen_id = f"SCR-{int(m.group(1)):02d}"

        styles = []
        for s in re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL | re.IGNORECASE):
            clean_css = s.replace("body {", ".frame-body-override {")
            styles.append(clean_css)

        body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL | re.IGNORECASE)
        inner_content = body_match.group(1) if body_match else html

        frames.append({
            "filename": filename,
            "filepath": filepath,
            "view_id": view_id,
            "ux_id": ux_id,
            "screen_id": screen_id,
            "screen_name": screen_name,
            "role": role,
            "screen_type": screen_type,
            "styles": "\n".join(styles),
            "inner_content": inner_content
        })

    return frames

def match_frame(target_name, frames):
    """Matches a declared screen target name from navigation-map to an ingested frame."""
    if not target_name:
        return None
    
    clean_target = re.sub(r'\s*\(Landing\)', '', target_name, flags=re.I)
    clean_target = re.sub(r'\s*\(Drill-down\)', '', clean_target, flags=re.I)
    clean_target = re.sub(r'\s*\[.*?\]', '', clean_target)
    clean_target = clean_target.strip().lower()

    # Check canonical alias table
    if clean_target in CANONICAL_ALIASES:
        target_fn = CANONICAL_ALIASES[clean_target]
        for fr in frames:
            if fr["filename"] == target_fn:
                return fr

    # Exact name match
    for fr in frames:
        if fr["screen_name"].lower() == clean_target:
            return fr

    # Substring match
    for fr in frames:
        sn = fr["screen_name"].lower()
        if clean_target in sn or sn in clean_target:
            return fr

    # Token match
    tokens = [t for t in clean_target.split() if len(t) > 3]
    if tokens:
        for fr in frames:
            sn = fr["screen_name"].lower()
            if all(t in sn for t in tokens):
                return fr

    return None

def parse_navigation_map(nav_map_path, frames):
    """
    Parses navigation-map.md into structured User Types (Roles),
    extracting sections, navigation items, landing frames, and drill-down frames.
    """
    if not os.path.exists(nav_map_path):
        return {}

    with open(nav_map_path, "r", encoding="utf-8") as f:
        content = f.read()

    struct_match = re.search(r'## Structure.*?\n(\|.*?)(?=\n##|\Z)', content, re.DOTALL)
    if not struct_match:
        return {}

    lines = [l.strip() for l in struct_match.group(1).strip().split("\n") if l.strip().startswith("|")]
    if len(lines) < 3:
        return {}

    raw_rows = []
    for line in lines[2:]:
        cols = [c.strip() for c in line.split("|")[1:-1]]
        if len(cols) >= 5:
            raw_rows.append({
                "order": cols[0],
                "id": cols[1].strip("`"),
                "label": cols[2],
                "points_to": cols[3],
                "role": cols[4],
                "icon": cols[6] if len(cols) > 6 else ""
            })

    # Group into canonical roles
    role_specs = {
        "Admin / CFEF Staff": {
            "title": "Operations Console",
            "persona": "Travis Manning • Program Director",
            "is_grouped": True,
            "sections": []
        },
        "Family / Parent": {
            "title": "Family & Parent Portal",
            "persona": "Maria Chen • 2 Awarded Students",
            "is_grouped": False,
            "items": []
        },
        "Private School": {
            "title": "School Provider Portal",
            "persona": "Sister Mary Catherine • St. Jude Academy",
            "is_grouped": False,
            "items": []
        },
        "Vendor / Provider": {
            "title": "Vendor Partner Portal",
            "persona": "David Vance • Apex Tutoring Services",
            "is_grouped": False,
            "items": []
        },
        "Donor": {
            "title": "Donor Impact Portal",
            "persona": "Arthur Larson • Larson Family Trust",
            "is_grouped": False,
            "items": []
        },
        "Public Portal Gateway": {
            "title": "Scholarship Gateway",
            "persona": "Prospective Applicant / User",
            "is_grouped": False,
            "items": []
        }
    }

    # Map raw rows
    current_admin_section = None

    for row in raw_rows:
        rid = row["id"]
        label = row["label"]
        pts = row["points_to"]
        role_field = row["role"]
        icon_name = row["icon"]

        # Parse targets
        targets = [t.strip() for t in pts.split(", ") if t.strip()] if pts != "—" else []
        landing_frame = None
        drilldowns = []

        for t in targets:
            mf = match_frame(t, frames)
            if "(landing)" in t.lower() or landing_frame is None:
                if landing_frame is None:
                    landing_frame = mf
            else:
                if mf:
                    drilldowns.append(mf)

        nav_item = {
            "id": rid,
            "label": label,
            "icon_name": icon_name,
            "landing_frame": landing_frame,
            "drilldowns": drilldowns,
            "points_to_raw": pts
        }

        # Admin grouping logic
        if "Admin" in role_field:
            if pts == "—":
                current_admin_section = {
                    "id": rid,
                    "label": label,
                    "items": []
                }
                role_specs["Admin / CFEF Staff"]["sections"].append(current_admin_section)
            else:
                if current_admin_section is None:
                    current_admin_section = {
                        "id": "general",
                        "label": "General",
                        "items": []
                    }
                    role_specs["Admin / CFEF Staff"]["sections"].append(current_admin_section)
                current_admin_section["items"].append(nav_item)

        elif "Parent" in role_field or "Family" in role_field:
            role_specs["Family / Parent"]["items"].append(nav_item)

        elif "School-type only" in role_field or "Private School" in role_field:
            role_specs["Private School"]["items"].append(nav_item)

        elif "School or Vendor" in role_field or "Vendor" in role_field:
            role_specs["Vendor / Provider"]["items"].append(nav_item)
            role_specs["Private School"]["items"].append(nav_item)

        elif "Donor" in role_field:
            role_specs["Donor"]["items"].append(nav_item)

    # Public gateway items (UX-001)
    for fr in frames:
        if fr["ux_id"] == "UX-001":
            role_specs["Public Portal Gateway"]["items"].append({
                "id": fr["view_id"],
                "label": fr["screen_name"],
                "icon_name": "Document",
                "landing_frame": fr,
                "drilldowns": [],
                "points_to_raw": fr["screen_name"]
            })

    return role_specs

def audit_spec_vault(vault_dir, frames):
    """Audits frames against UX specs in 04-UIUX/ to calculate requirement coverage."""
    audit_report = {
        "features": {},
        "total_declared": 0,
        "total_assembled": len(frames),
        "missing_screens": [],
        "coverage_pct": 0.0
    }

    ux_files = glob.glob(os.path.join(vault_dir, "04-UIUX", "UX-*.md"))
    for uxf in sorted(ux_files):
        ux_name = os.path.basename(uxf)
        ux_id_match = re.search(r'(UX-\d+)', ux_name)
        if not ux_id_match:
            continue
        ux_id = ux_id_match.group(1)
        
        with open(uxf, "r", encoding="utf-8") as f:
            content = f.read()

        inv_match = re.search(r'## 2\.\s*Screen Inventory(.*?)(?:## 3|\Z)', content, re.DOTALL)
        declared_screens = []
        if inv_match:
            inv_text = inv_match.group(1).strip()
            lines = [l.strip() for l in inv_text.split("\n") if l.strip().startswith("|")]
            if len(lines) >= 3:
                headers = [h.strip().lower() for h in lines[0].split("|")[1:-1]]
                scr_idx = next((idx for idx, h in enumerate(headers) if "screen" in h), 0)

                for seq, line in enumerate(lines[2:], start=1):
                    parts = [p.strip() for p in line.split("|")[1:-1]]
                    if parts and len(parts) > scr_idx and parts[scr_idx]:
                        s_name = parts[scr_idx]
                        declared_screens.append({
                            "seq": seq,
                            "screen_id": f"SCR-{seq:02d}",
                            "name": s_name
                        })

        assembled_for_ux = [fr for fr in frames if fr.get("ux_id") == ux_id]
        assembled_names = {fr.get("screen_name", "").lower() for fr in assembled_for_ux}
        assembled_ids = {fr.get("screen_id", "") for fr in assembled_for_ux}

        missing = []
        for ds in declared_screens:
            name_clean = ds["name"].lower()
            matched = False
            if ds["screen_id"] in assembled_ids:
                matched = True
            else:
                for an in assembled_names:
                    if name_clean in an or an in name_clean:
                        matched = True
                        break
            if not matched:
                missing.append(f"{ux_id} {ds['screen_id']}: {ds['name']}")

        audit_report["features"][ux_id] = {
            "declared_count": len(declared_screens),
            "assembled_count": len(assembled_for_ux),
            "missing": missing
        }
        audit_report["total_declared"] += len(declared_screens)
        audit_report["missing_screens"].extend(missing)

    if audit_report["total_declared"] > 0:
        audit_report["coverage_pct"] = (len(frames) / audit_report["total_declared"]) * 100.0
    else:
        audit_report["coverage_pct"] = 100.0 if len(frames) > 0 else 0.0

    return audit_report

def assemble_master_prototype(project_dir, frames, role_specs, target_file="index.html"):
    """
    Synthesizes the authentic multi-portal application prototype following:
    User Type -> Navigation Map -> Frame in Context -> Loop all Navigation -> Move to next User Type -> Repeat.
    """
    out_path = os.path.join(project_dir, target_file)

    # Collect all frame styles
    combined_styles = "\n\n".join([f"/* Frame: {fr['filename']} */\n" + fr["styles"] for fr in frames if fr["styles"].strip()])

    # Mount all frame view containers
    views_html = []
    for fr in frames:
        views_html.append(f"""
    <!-- FRAME: {fr['filename']} ({fr['screen_id']}: {fr['screen_name']}) -->
    <div id="{fr['view_id']}" class="screen-view-container" data-ux="{fr['ux_id']}" data-screen-id="{fr['screen_id']}" data-role="{fr['role']}" data-type="{fr['screen_type']}" style="display: none;">
      {fr['inner_content']}
    </div>
""")

    # Build Top-Nav Tabs and Side-Nav Menus for each Role
    role_nav_blocks = []
    role_top_nav_blocks = []
    role_flat_nav_map = {} # role_name -> list of target view_ids for navigation looping

    for role_name, spec in role_specs.items():
        menu_items_html = []
        top_tabs_html = []
        nav_loop_views = []

        if spec.get("is_grouped", False):
            # Grouped sections (e.g. Admin)
            for sec in spec.get("sections", []):
                sec_label = sec["label"]
                child_links = []
                for it in sec.get("items", []):
                    landing_v = it["landing_frame"]["view_id"] if it["landing_frame"] else ""
                    if landing_v:
                        nav_loop_views.append({
                            "view_id": landing_v,
                            "label": it["label"],
                            "section": sec_label
                        })
                    icon_svg = CARBON_ICONS.get(it["icon_name"], DEFAULT_ICON)
                    child_links.append(f"""
              <a class="cds-side-nav-link" href="#{landing_v}" data-target="{landing_v}" title="{it['label']}">
                {icon_svg}
                <span class="cds-link-text">{it['label']}</span>
              </a>
""")
                    top_tabs_html.append(f"""
            <button class="top-nav-tab" data-target="{landing_v}" title="{it['label']}">
              {icon_svg}
              <span>{it['label']}</span>
            </button>
""")
                menu_items_html.append(f"""
            <div class="cds-nav-group">
              <div class="cds-nav-group-header">
                <span>{sec_label.upper()}</span>
              </div>
              <div class="cds-nav-group-items">
                {"".join(child_links)}
              </div>
            </div>
""")
        else:
            # Flat items (Family, School, Vendor, Donor, Gateway)
            child_links = []
            for it in spec.get("items", []):
                landing_v = it["landing_frame"]["view_id"] if it["landing_frame"] else ""
                if landing_v:
                    nav_loop_views.append({
                        "view_id": landing_v,
                        "label": it["label"],
                        "section": role_name
                    })
                icon_svg = CARBON_ICONS.get(it["icon_name"], DEFAULT_ICON)
                child_links.append(f"""
            <a class="cds-side-nav-link" href="#{landing_v}" data-target="{landing_v}" title="{it['label']}">
              {icon_svg}
              <span class="cds-link-text">{it['label']}</span>
            </a>
""")
                top_tabs_html.append(f"""
            <button class="top-nav-tab" data-target="{landing_v}" title="{it['label']}">
              {icon_svg}
              <span>{it['label']}</span>
            </button>
""")
            menu_items_html.append(f"""
          <div class="cds-nav-flat-items">
            {"".join(child_links)}
          </div>
""")

        role_flat_nav_map[role_name] = nav_loop_views

        role_nav_blocks.append(f"""
        <!-- Navigation Tree for {role_name} -->
        <div class="cds-role-side-nav" data-role="{role_name}" style="display: none;">
          <div class="cds-portal-subhead">
            <span class="cds-portal-title">{spec['title']}</span>
            <span class="cds-portal-persona">{spec['persona']}</span>
          </div>
          {"".join(menu_items_html)}
        </div>
""")
        role_top_nav_blocks.append(f"""
        <!-- Top Navigation Tabs for {role_name} -->
        <div class="role-top-nav-tabs" data-role="{role_name}" style="display: none;">
          {"".join(top_tabs_html)}
        </div>
""")

    role_loop_json = json.dumps(role_flat_nav_map)

    # Build file-to-view lookup table
    file_to_view = {}
    for fr in frames:
        file_to_view[fr["filename"]] = fr["view_id"]
        clean_name = re.sub(r"-2\.html$", ".html", fr["filename"])
        file_to_view[clean_name] = fr["view_id"]
    file_to_view_json = json.dumps(file_to_view)

    # Master Application Shell HTML
    master_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Children's First Education Fund · Unified Portal</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
  
  <style>
    /* ==========================================================================
       IBM CARBON DESIGN SYSTEM MASTER APPLICATION SHELL
       ========================================================================== */
    :root {{
      /* Semantic Design Tokens - Agnostic Architecture */
      --bg: #ffffff;
      --surface: #f7f7f7;
      --surface-hover: #efefef;
      --fg: #222222;
      --fg-muted: #717171;
      --border: #dddddd;
      --border-soft: #eaeaea;
      --accent: #ff385c; /* Default: Airbnb Rausch coral */
      --accent-hover: #e00b41;
      --accent-subtle: rgba(255, 56, 92, 0.08);
      --font-display: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      --font-body:    -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      --font-mono:    ui-monospace, SFMono-Regular, monospace;
      --radius-sm: 6px;
      --radius-md: 12px;
      --radius-lg: 16px;
      --radius-pill: 9999px;
      
      --header-bg: #ffffff;
      --header-fg: #222222;
      --header-border: #ebebeb;
      --header-height: 56px;
      --top-nav-height: 46px;
      --tour-height: 40px;
      --side-nav-width: 260px;

      /* Fallback Carbon mappings for frame compatibility */
      --cds-gray-100: var(--fg);
      --cds-gray-90:  var(--fg);
      --cds-gray-80:  var(--fg-muted);
      --cds-gray-70:  var(--fg-muted);
      --cds-gray-60:  var(--fg-muted);
      --cds-gray-50:  var(--fg-muted);
      --cds-gray-20:  var(--border);
      --cds-gray-10:  var(--surface);
      --cds-white:    #ffffff;
      --cds-blue-60:  var(--accent);
      --cds-blue-70:  var(--accent-hover);
      --cds-blue-10:  var(--accent-subtle);
      --cds-green-50: #008a05;
      --cds-red-60:   #c13515;
      --cds-yellow-30:#e07912;
    }}

    /* PRESET: Airbnb (Top-Nav, Rounded, Coral Accent) */
    [data-design-system="airbnb"] {{
      --bg: #ffffff;
      --surface: #f7f7f7;
      --surface-hover: #f0f0f0;
      --fg: #222222;
      --fg-muted: #717171;
      --border: #dddddd;
      --border-soft: #eaeaea;
      --accent: #ff385c;
      --accent-hover: #e00b41;
      --accent-subtle: rgba(255, 56, 92, 0.08);
      --radius-sm: 6px;
      --radius-md: 12px;
      --radius-lg: 16px;
      --radius-pill: 9999px;
      --header-bg: #ffffff;
      --header-fg: #222222;
      --header-border: #ebebeb;
    }}

    /* PRESET: IBM Carbon (Side-Nav, Sharp, Blue Accent) */
    [data-design-system="ibm"], [data-design-system="carbon"] {{
      --bg: #f4f4f4;
      --surface: #ffffff;
      --surface-hover: #e8e8e8;
      --fg: #161616;
      --fg-muted: #525252;
      --border: #e0e0e0;
      --border-soft: #f4f4f4;
      --accent: #0f62fe;
      --accent-hover: #0353e9;
      --accent-subtle: #edf5ff;
      --font-display: 'IBM Plex Sans', -apple-system, sans-serif;
      --font-body:    'IBM Plex Sans', -apple-system, sans-serif;
      --font-mono:    'IBM Plex Mono', monospace;
      --radius-sm: 0px;
      --radius-md: 0px;
      --radius-lg: 0px;
      --radius-pill: 0px;
      --header-bg: #161616;
      --header-fg: #ffffff;
      --header-border: #393939;
    }}

    /* PRESET: Stripe (Modern SaaS) */
    [data-design-system="stripe"] {{
      --bg: #f8fafc;
      --surface: #ffffff;
      --surface-hover: #f1f5f9;
      --fg: #0f172a;
      --fg-muted: #64748b;
      --border: #e2e8f0;
      --accent: #635bff;
      --accent-hover: #5851ea;
      --accent-subtle: #eff6ff;
      --radius-sm: 4px;
      --radius-md: 8px;
      --radius-lg: 12px;
      --radius-pill: 9999px;
      --header-bg: #ffffff;
      --header-fg: #0f172a;
      --header-border: #e2e8f0;
    }}

    /* Archetype Layout Rules */
    #app-top-nav-bar {{
      display: none;
      height: var(--top-nav-height);
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      padding: 0 16px;
      align-items: center;
      overflow-x: auto;
      z-index: 950;
    }}
    .role-top-nav-tabs {{
      display: flex;
      align-items: center;
      gap: 6px;
      width: 100%;
    }}
    .top-nav-tab {{
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 6px 14px;
      background: transparent;
      border: 1px solid transparent;
      border-radius: var(--radius-pill);
      color: var(--fg-muted);
      font-family: var(--font-body);
      font-size: 12px;
      font-weight: 500;
      cursor: pointer;
      white-space: nowrap;
      transition: all 0.15s ease;
    }}
    .top-nav-tab:hover {{
      color: var(--fg);
      background: var(--surface-hover);
    }}
    .top-nav-tab.active {{
      color: #ffffff;
      background: var(--accent);
      font-weight: 600;
    }}

    [data-layout="top-nav"] #app-top-nav-bar {{
      display: flex;
    }}
    [data-layout="top-nav"] #app-side-nav {{
      display: none !important;
    }}
    [data-layout="side-nav"] #app-top-nav-bar {{
      display: none !important;
    }}
    [data-layout="side-nav"] #app-side-nav {{
      display: flex;
    }}
    [data-layout="top-nav"] #app-body {{
      height: calc(100vh - var(--header-height) - var(--top-nav-height) - var(--tour-height));
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html, body {{
      height: 100%;
      width: 100%;
      font-family: var(--font-body);
      background: var(--cds-gray-10);
      color: var(--cds-gray-100);
      overflow: hidden;
    }}

    #app-container {{
      display: flex;
      flex-direction: column;
      height: 100vh;
      width: 100vw;
    }}

    /* Global Header (Carbon Masthead) */
    #app-masthead {{
      height: var(--header-height);
      background: var(--header-bg);
      color: var(--header-fg);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 16px;
      z-index: 1000;
      border-bottom: 1px solid var(--header-border);
      transition: background 0.2s ease, border-color 0.2s ease;
    }}

    .masthead-left {{
      display: flex;
      align-items: center;
      gap: 16px;
    }}

    .nav-toggle-btn {{
      background: transparent;
      border: none;
      color: #c6c6c6;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 6px;
    }}
    .nav-toggle-btn:hover {{ color: #ffffff; }}

    .brand-section {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 14px;
      letter-spacing: 0.16px;
    }}
    .brand-badge {{
      background: var(--cds-blue-60);
      color: var(--cds-white);
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 600;
      padding: 2px 6px;
      letter-spacing: 0.5px;
    }}
    .brand-org {{
      font-weight: 600;
      color: #ffffff;
    }}
    .brand-divider {{
      color: var(--cds-gray-60);
    }}
    .brand-subtitle {{
      color: #c6c6c6;
      font-size: 13px;
    }}

    /* Masthead Controls: Role Switcher & User Profile */
    .masthead-right {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .role-switcher-container {{
      display: flex;
      align-items: center;
      background: var(--cds-gray-90);
      border: 1px solid var(--cds-gray-80);
      padding: 2px 8px;
    }}
    .role-label {{
      font-size: 11px;
      color: #a8a8a8;
      margin-right: 6px;
      font-family: var(--font-mono);
      text-transform: uppercase;
    }}
    .role-dropdown {{
      background: transparent;
      border: none;
      color: #ffffff;
      font-family: var(--font-body);
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      outline: none;
    }}
    .role-dropdown option {{
      background: var(--cds-gray-90);
      color: #ffffff;
    }}

    .user-pill {{
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 4px 10px;
      background: var(--cds-gray-90);
      border: 1px solid var(--cds-gray-80);
      font-size: 12px;
      color: #e0e0e0;
    }}
    .user-avatar {{
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: var(--cds-blue-60);
      color: #ffffff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 10px;
      font-weight: 600;
      font-family: var(--font-mono);
    }}

    /* Interactive Guided Role Navigation Loop Bar */
    #nav-tour-bar {{
      height: var(--tour-height);
      background: #1e1e1e;
      border-bottom: 1px solid var(--cds-gray-80);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 16px;
      z-index: 999;
      font-size: 12px;
      color: #c6c6c6;
    }}

    .tour-left {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .tour-badge {{
      background: #393939;
      color: #78a9ff;
      font-family: var(--font-mono);
      font-size: 11px;
      padding: 2px 8px;
      font-weight: 500;
    }}
    .tour-role-title {{
      font-weight: 600;
      color: #ffffff;
    }}
    .tour-step-info {{
      color: #a8a8a8;
      font-family: var(--font-mono);
      font-size: 11px;
    }}

    .tour-center {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .tour-btn {{
      background: #262626;
      border: 1px solid #393939;
      color: #ffffff;
      padding: 3px 12px;
      font-size: 11px;
      font-family: var(--font-body);
      cursor: pointer;
      transition: all 0.15s ease;
      display: flex;
      align-items: center;
      gap: 4px;
    }}
    .tour-btn:hover {{
      background: #393939;
      border-color: #525252;
    }}
    .tour-btn.btn-primary {{
      background: var(--cds-blue-60);
      border-color: var(--cds-blue-60);
    }}
    .tour-btn.btn-primary:hover {{
      background: var(--cds-blue-70);
    }}

    .tour-right {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .scenario-pill-mini {{
      background: transparent;
      border: 1px solid var(--cds-gray-80);
      color: #c6c6c6;
      padding: 2px 8px;
      font-size: 11px;
      cursor: pointer;
    }}
    .scenario-pill-mini.active {{
      background: var(--cds-blue-60);
      border-color: var(--cds-blue-60);
      color: #ffffff;
      font-weight: 600;
    }}

    /* Main Application Body Split */
    #app-body {{
      display: flex;
      flex: 1;
      height: calc(100vh - var(--header-height) - var(--tour-height));
      overflow: hidden;
      position: relative;
    }}

    /* Persistent Carbon Side Navigation */
    #app-side-nav {{
      width: var(--side-nav-width);
      min-width: var(--side-nav-width);
      background: var(--cds-white);
      border-right: 1px solid var(--cds-gray-20);
      display: flex;
      flex-direction: column;
      overflow-y: auto;
      z-index: 900;
      transition: width 0.2s ease, min-width 0.2s ease, transform 0.2s ease;
    }}
    #app-side-nav.collapsed {{
      width: 0;
      min-width: 0;
      transform: translateX(-100%);
    }}

    .cds-portal-subhead {{
      padding: 14px 16px;
      background: var(--cds-gray-10);
      border-bottom: 1px solid var(--cds-gray-20);
    }}
    .cds-portal-title {{
      display: block;
      font-size: 12px;
      font-weight: 600;
      color: var(--cds-gray-100);
      text-transform: uppercase;
      letter-spacing: 0.32px;
    }}
    .cds-portal-persona {{
      display: block;
      font-size: 11px;
      color: var(--cds-gray-60);
      margin-top: 2px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    .cds-nav-group {{
      border-bottom: 1px solid var(--cds-gray-10);
    }}
    .cds-nav-group-header {{
      padding: 12px 16px 6px;
      font-size: 10px;
      font-family: var(--font-mono);
      font-weight: 600;
      color: var(--cds-gray-60);
      letter-spacing: 0.5px;
    }}
    .cds-nav-group-items, .cds-nav-flat-items {{
      display: flex;
      flex-direction: column;
    }}

    .cds-side-nav-link {{
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 9px 16px;
      color: var(--cds-gray-100);
      text-decoration: none;
      font-size: 13px;
      border-left: 4px solid transparent;
      transition: all 0.15s ease;
    }}
    .cds-side-nav-link:hover {{
      background: var(--cds-gray-10);
      color: var(--cds-blue-60);
    }}
    .cds-side-nav-link.active {{
      background: var(--cds-blue-10);
      border-left-color: var(--cds-blue-60);
      color: var(--cds-blue-70);
      font-weight: 600;
    }}
    .cds-side-nav-link .nav-icon {{
      width: 16px;
      height: 16px;
      color: var(--cds-gray-60);
      flex-shrink: 0;
    }}
    .cds-side-nav-link.active .nav-icon {{
      color: var(--cds-blue-60);
    }}
    .cds-link-text {{
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}

    /* Central Context Workspace Viewport */
    #app-workspace {{
      flex: 1;
      background: var(--cds-gray-10);
      overflow-y: auto;
      position: relative;
      height: 100%;
    }}

    .screen-view-container {{
      min-height: 100%;
    }}

    /* State Simulation Helpers */
    [data-simulated-state="empty"] .data-populated-section,
    [data-simulated-state="empty"] .cds-table-container {{
      display: none !important;
    }}
    [data-simulated-state="empty"] .cds-empty-state-override {{
      display: block !important;
    }}
    .cds-empty-state-override {{
      display: none;
      padding: 48px 24px;
      text-align: center;
      background: #ffffff;
      border: 1px dashed #c6c6c6;
      margin: 24px 0;
    }}

    [data-simulated-state="loading"] .screen-frame {{
      opacity: 0.6;
      pointer-events: none;
      position: relative;
    }}

    /* Injected Scoped Frame Styles */
    {combined_styles}
  </style>
</head>
<body data-design-system="airbnb" data-layout="top-nav">
  <div id="app-container">
    
    <!-- Masthead -->
    <header id="app-masthead">
      <div class="masthead-left">
        <button id="btn-toggle-nav" class="nav-toggle-btn" title="Toggle Navigation Sidebar">
          <svg width="20" height="20" viewBox="0 0 32 32" fill="currentColor">
            <path d="M4 6h24v2H4zm0 9h24v2H4zm0 9h24v2H4z"/>
          </svg>
        </button>
        <div class="brand-section">
          <span class="brand-badge">CFEF</span>
          <span class="brand-org">Children's First Education Fund</span>
          <span class="brand-divider">/</span>
          <span class="brand-subtitle">Utah Fits All Scholarship Program</span>
        </div>
      </div>

      <div class="masthead-right">
        <div class="role-switcher-container">
          <span class="role-label">Portal:</span>
          <select id="role-select" class="role-dropdown">
            <option value="Admin / CFEF Staff">Admin / CFEF Staff</option>
            <option value="Family / Parent">Family / Parent</option>
            <option value="Private School">Private School Provider</option>
            <option value="Vendor / Provider">Vendor / Provider</option>
            <option value="Donor">Corporate & Individual Donor</option>
            <option value="Public Portal Gateway">Public Portal Gateway</option>
          </select>
        </div>

        <div class="user-pill">
          <div id="user-avatar-initials" class="user-avatar">TM</div>
          <span id="user-display-name">Travis Manning</span>
        </div>

        <button id="btn-logout" class="tour-btn" style="border-color:#525252;">Sign Out</button>
      </div>
    </header>

    <!-- Interactive Role Navigation Tour & Loop Controller -->
    <div id="nav-tour-bar">
      <div class="tour-left">
        <span class="tour-badge">NAVIGATION LOOP</span>
        <span id="tour-role-name" class="tour-role-title">Admin / CFEF Staff</span>
        <span id="tour-step-info" class="tour-step-info">Nav Item 1 of 6: Applications Queue</span>
      </div>

      <div class="tour-center">
        <button id="btn-tour-prev" class="tour-btn">◀ Prev Nav</button>
        <button id="btn-tour-next" class="tour-btn">Next Nav ▶</button>
        <button id="btn-tour-next-role" class="tour-btn btn-primary">Next User Type ⏭️</button>
      </div>

      <div class="tour-right">
        <select id="design-system-select" style="background:#2a2a2a; border:1px solid #444; color:#fff; padding:2px 8px; font-size:11px; border-radius:4px; cursor:pointer;" title="Design System Theme">
          <option value="airbnb" selected>Theme: Airbnb (Top-Nav)</option>
          <option value="ibm">Theme: IBM Carbon (Side-Nav)</option>
          <option value="stripe">Theme: Stripe (Modern)</option>
        </select>
        <select id="layout-select" style="background:#2a2a2a; border:1px solid #444; color:#fff; padding:2px 8px; font-size:11px; border-radius:4px; cursor:pointer;" title="Layout Archetype">
          <option value="top-nav" selected>Layout: Top-Nav</option>
          <option value="side-nav">Layout: Side-Nav</option>
        </select>
        <button class="scenario-pill-mini active" data-state="active">Populated</button>
        <button class="scenario-pill-mini" data-state="empty">Empty</button>
        <button class="scenario-pill-mini" data-state="loading">Loading</button>
      </div>
    </div>

    <!-- Top Navigation Bar (Archetype A: Top-Nav Tabs) -->
    <nav id="app-top-nav-bar">
      {"".join(role_top_nav_blocks)}
    </nav>

    <!-- Main Viewport Body -->
    <div id="app-body">
      <!-- Persistent Carbon Side Navigation -->
      <nav id="app-side-nav">
        {"".join(role_nav_blocks)}
      </nav>

      <!-- Central Context Workspace -->
      <main id="app-workspace">
        {"".join(views_html)}
      </main>
    </div>

  </div>

  <!-- Central Client-Side Router & Role Navigation Controller -->
  <script>
    (function() {{
      const roleNavMap = {role_loop_json};
      const fileToViewMap = {file_to_view_json};
      const roleOrder = [
        "Admin / CFEF Staff",
        "Family / Parent",
        "Private School",
        "Vendor / Provider",
        "Donor",
        "Public Portal Gateway"
      ];

      const personas = {{
        "Admin / CFEF Staff": {{ name: "Travis Manning", initials: "TM", title: "Program Director" }},
        "Family / Parent": {{ name: "Maria Chen", initials: "MC", title: "Parent (2 Students)" }},
        "Private School": {{ name: "Sister Mary Catherine", initials: "MC", title: "St. Jude Academy" }},
        "Vendor / Provider": {{ name: "David Vance", initials: "DV", title: "Apex Tutoring" }},
        "Donor": {{ name: "Arthur Larson", initials: "AL", title: "Larson Family Trust" }},
        "Public Portal Gateway": {{ name: "Prospective User", initials: "PU", title: "Public Applicant" }}
      }};

      const app = {{
        activeRole: 'Admin / CFEF Staff',
        activeViewId: null,
        activeNavIndex: 0,
        simulatedState: 'active',

        init() {{
          try {{
            const urlParams = new URLSearchParams(window.location.search);
            const themeParam = urlParams.get('theme');
            if (themeParam && ['airbnb', 'ibm', 'stripe', 'carbon'].includes(themeParam)) {{
              const normalizedTheme = themeParam === 'carbon' ? 'ibm' : themeParam;
              document.body.setAttribute('data-design-system', normalizedTheme);
              const dsSelect = document.getElementById('design-system-select');
              if (dsSelect) dsSelect.value = normalizedTheme;
              if (normalizedTheme === 'ibm') {{
                document.body.setAttribute('data-layout', 'side-nav');
                const layoutSelect = document.getElementById('layout-select');
                if (layoutSelect) layoutSelect.value = 'side-nav';
              }} else {{
                document.body.setAttribute('data-layout', 'top-nav');
                const layoutSelect = document.getElementById('layout-select');
                if (layoutSelect) layoutSelect.value = 'top-nav';
              }}
            }}
            const layoutParam = urlParams.get('layout');
            if (layoutParam && ['top-nav', 'side-nav'].includes(layoutParam)) {{
              document.body.setAttribute('data-layout', layoutParam);
              const layoutSelect = document.getElementById('layout-select');
              if (layoutSelect) layoutSelect.value = layoutParam;
            }}
          }} catch(e) {{}}
          this.bindEvents();
          this.handleHashChange();
        }},

        setRole(roleName) {{
          if (!roleNavMap[roleName]) {{
            roleName = "Admin / CFEF Staff";
          }}
          this.activeRole = roleName;
          this.activeNavIndex = 0;

          // Update header dropdown
          const select = document.getElementById('role-select');
          if (select) select.value = roleName;

          // Update persona details
          const persona = personas[roleName] || {{ name: roleName, initials: "CF", title: "" }};
          document.getElementById('user-display-name').textContent = persona.name;
          document.getElementById('user-avatar-initials').textContent = persona.initials;
          document.getElementById('tour-role-name').textContent = roleName;

          // Show matching navigation tree in side-nav and top-nav
          document.querySelectorAll('.cds-role-side-nav').forEach(el => {{
            el.style.display = el.getAttribute('data-role') === roleName ? 'block' : 'none';
          }});
          document.querySelectorAll('.role-top-nav-tabs').forEach(el => {{
            el.style.display = el.getAttribute('data-role') === roleName ? 'flex' : 'none';
          }});

          // Route to first landing view for this role
          const items = roleNavMap[roleName] || [];
          if (items.length > 0) {{
            this.navigateTo(items[0].view_id);
          }}
          this.updateTourBar();
        }},

        navigateTo(viewId) {{
          if (!viewId) return;
          const target = document.getElementById(viewId);
          if (!target) return;

          // Hide all view containers
          document.querySelectorAll('.screen-view-container').forEach(v => v.style.display = 'none');

          if (this.activeViewId && this.activeViewId !== viewId) {{
            this.previousViewId = this.activeViewId;
          }}
          // Show target view container
          target.style.display = 'block';
          this.activeViewId = viewId;
          window.location.hash = '#' + viewId;

          // Update active link in side-nav
          document.querySelectorAll('.cds-side-nav-link').forEach(a => {{
            if (a.getAttribute('data-target') === viewId) {{
              a.classList.add('active');
            }} else {{
              a.classList.remove('active');
            }}
          }});

          // Update active tab in top-nav
          document.querySelectorAll('.top-nav-tab').forEach(btn => {{
            if (btn.getAttribute('data-target') === viewId) {{
              btn.classList.add('active');
            }} else {{
              btn.classList.remove('active');
            }}
          }});

          // Update nav index for tour
          const items = roleNavMap[this.activeRole] || [];
          const idx = items.findIndex(it => it.view_id === viewId);
          if (idx !== -1) {{
            this.activeNavIndex = idx;
          }}
          this.updateTourBar();

          // Scroll workspace to top
          document.getElementById('app-workspace').scrollTop = 0;
        }},

        updateTourBar() {{
          const items = roleNavMap[this.activeRole] || [];
          const total = items.length;
          const current = total > 0 ? this.activeNavIndex + 1 : 0;
          const itemLabel = total > 0 ? items[this.activeNavIndex].label : "Overview";
          
          document.getElementById('tour-step-info').textContent = `Nav Item ${{current}} of ${{total}}: ${{itemLabel}}`;

          // Determine next role label
          const currentRoleIdx = roleOrder.indexOf(this.activeRole);
          const nextRoleIdx = (currentRoleIdx + 1) % roleOrder.length;
          const nextRoleName = roleOrder[nextRoleIdx];
          document.getElementById('btn-tour-next-role').textContent = `Next User Type (${{nextRoleName}}) ⏭️`;
        }},

        prevNav() {{
          const items = roleNavMap[this.activeRole] || [];
          if (items.length === 0) return;
          this.activeNavIndex = (this.activeNavIndex - 1 + items.length) % items.length;
          this.navigateTo(items[this.activeNavIndex].view_id);
        }},

        nextNav() {{
          const items = roleNavMap[this.activeRole] || [];
          if (items.length === 0) return;
          this.activeNavIndex = (this.activeNavIndex + 1) % items.length;
          this.navigateTo(items[this.activeNavIndex].view_id);
        }},

        nextRole() {{
          const currentRoleIdx = roleOrder.indexOf(this.activeRole);
          const nextRoleIdx = (currentRoleIdx + 1) % roleOrder.length;
          this.setRole(roleOrder[nextRoleIdx]);
        }},

        handleHashChange() {{
          const hash = window.location.hash.replace('#', '').trim();
          if (hash && document.getElementById(hash)) {{
            // Find which role this view belongs to
            let foundRole = null;
            for (const [r, items] of Object.entries(roleNavMap)) {{
              if (items.some(it => it.view_id === hash)) {{
                foundRole = r;
                break;
              }}
            }}
            const targetRole = foundRole || this.activeRole;
            this.activeRole = targetRole;
            const select = document.getElementById('role-select');
            if (select) select.value = targetRole;
            const persona = personas[targetRole] || {{ name: targetRole, initials: "CF", title: "" }};
            document.getElementById('user-display-name').textContent = persona.name;
            document.getElementById('user-avatar-initials').textContent = persona.initials;
            document.getElementById('tour-role-name').textContent = targetRole;
            document.querySelectorAll('.cds-role-side-nav').forEach(el => {{
              el.style.display = el.getAttribute('data-role') === targetRole ? 'block' : 'none';
            }});
            document.querySelectorAll('.role-top-nav-tabs').forEach(el => {{
              el.style.display = el.getAttribute('data-role') === targetRole ? 'flex' : 'none';
            }});
            this.navigateTo(hash);
          }} else {{
            this.setRole('Admin / CFEF Staff');
          }}
        }},

        bindEvents() {{
          window.addEventListener('hashchange', () => this.handleHashChange());

          // Role dropdown switcher
          document.getElementById('role-select').addEventListener('change', (e) => {{
            this.setRole(e.target.value);
          }});

          // Design System Theme Switcher
          const dsSelect = document.getElementById('design-system-select');
          if (dsSelect) {{
            dsSelect.addEventListener('change', (e) => {{
              const ds = e.target.value;
              document.body.setAttribute('data-design-system', ds);
              const layoutSelect = document.getElementById('layout-select');
              if (ds === 'ibm') {{
                document.body.setAttribute('data-layout', 'side-nav');
                if (layoutSelect) layoutSelect.value = 'side-nav';
              }} else {{
                document.body.setAttribute('data-layout', 'top-nav');
                if (layoutSelect) layoutSelect.value = 'top-nav';
              }}
            }});
          }}

          // Layout Switcher
          const layoutSelect = document.getElementById('layout-select');
          if (layoutSelect) {{
            layoutSelect.addEventListener('change', (e) => {{
              document.body.setAttribute('data-layout', e.target.value);
            }});
          }}

          // Toggle sidebar
          document.getElementById('btn-toggle-nav').addEventListener('click', () => {{
            document.getElementById('app-side-nav').classList.toggle('collapsed');
          }});

          // Tour bar buttons
          document.getElementById('btn-tour-prev').addEventListener('click', () => this.prevNav());
          document.getElementById('btn-tour-next').addEventListener('click', () => this.nextNav());
          document.getElementById('btn-tour-next-role').addEventListener('click', () => this.nextRole());

          // Logout
          document.getElementById('btn-logout').addEventListener('click', () => {{
            this.setRole('Public Portal Gateway');
          }});

          // Scenario pills
          document.querySelectorAll('.scenario-pill-mini').forEach(btn => {{
            btn.addEventListener('click', (e) => {{
              document.querySelectorAll('.scenario-pill-mini').forEach(b => b.classList.remove('active'));
              btn.classList.add('active');
              const state = btn.getAttribute('data-state');
              document.getElementById('app-workspace').setAttribute('data-simulated-state', state);
            }});
          }});

          // Global click handler for in-screen routing & drill-downs
          document.addEventListener('click', (e) => {{
            // Side nav link or top nav tab
            const navLink = e.target.closest('.cds-side-nav-link, .top-nav-tab');
            if (navLink) {{
              e.preventDefault();
              const target = navLink.getAttribute('data-target');
              this.navigateTo(target);
              return;
            }}

            // In-frame back button or breadcrumb
            const backBtn = e.target.closest('.btn-back, [data-action="back"], .cds-breadcrumb-link, button.btn-close, .cds-modal-close');
            if (backBtn) {{
              e.preventDefault();
              const target = backBtn.getAttribute('data-target');
              if (target && document.getElementById(target)) {{
                this.navigateTo(target);
              }} else if (this.previousViewId && document.getElementById(this.previousViewId)) {{
                this.navigateTo(this.previousViewId);
              }} else {{
                const items = roleNavMap[this.activeRole] || [];
                if (items.length > 0) this.navigateTo(items[0].view_id);
              }}
              return;
            }}

            // In-frame action buttons or table rows with data-target
            const actionTarget = e.target.closest('[data-target]');
            if (actionTarget && !actionTarget.classList.contains('cds-side-nav-link')) {{
              const rawTarget = actionTarget.getAttribute('data-target');
              if (rawTarget) {{
                const target = fileToViewMap[rawTarget] || rawTarget;
                if (document.getElementById(target)) {{
                  e.preventDefault();
                  this.navigateTo(target);
                  return;
                }}
              }}
            }}

            // Standard in-frame anchor links
            const anchor = e.target.closest('a[href]');
            if (anchor) {{
              const href = anchor.getAttribute('href');
              if (href.startsWith('#')) {{
                const targetId = href.substring(1);
                if (document.getElementById(targetId)) {{
                  e.preventDefault();
                  this.navigateTo(targetId);
                  return;
                }}
              }} else if (href.includes('.html')) {{
                const cleanHref = href.split('#')[0].split('?')[0].split('/').pop();
                if (fileToViewMap[cleanHref]) {{
                  e.preventDefault();
                  this.navigateTo(fileToViewMap[cleanHref]);
                  return;
                }}
              }}
            }}
          }});
        }}
      }};

      window.app = app;
      if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', () => app.init());
      }} else {{
        app.init();
      }}
    }})();
  </script>
</body>
</html>
"""

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(master_html)

    print(f"Master prototype successfully assembled/updated at: {out_path}")
    print(f"Total modular screen frames mounted: {len(frames)}")

def main():
    parser = argparse.ArgumentParser(description="Assemble modular UX screen frames into an authentic role-driven prototype.")
    parser.add_argument("--project", "-p", default=".", help="Path to project directory containing frames.")
    parser.add_argument("--vault", "-v", default=".", help="Path to requirements vault containing 04-UIUX/.")
    parser.add_argument("--target", "-t", default="index.html", help="Target prototype filename (defaults to index.html).")
    parser.add_argument("--audit-only", action="store_true", help="Run spec vault coverage audit without assembling.")

    args = parser.parse_args()

    project_dir = os.path.abspath(args.project)
    vault_dir = os.path.abspath(args.vault)

    print(f"==> Ingesting modular frames from: {project_dir}")
    frames = parse_screen_frames(project_dir)
    print(f"Found {len(frames)} modular frame files.")

    # Parse Navigation Map
    nav_map_path = os.path.join(vault_dir, "04-UIUX", "_ux", "navigation-map.md")
    if not os.path.exists(nav_map_path):
        nav_map_path = os.path.join(project_dir, "navigation-map.md")

    role_specs = parse_navigation_map(nav_map_path, frames)
    print(f"Loaded {len(role_specs)} user types / roles from navigation map.")

    # Audit Coverage
    audit = audit_spec_vault(vault_dir, frames)
    print("\n--- Requirement Coverage Audit ---")
    print(f"Total Declared Screens in Spec Vault: {audit['total_declared']}")
    print(f"Total Modular Frames Assembled:      {audit['total_assembled']}")
    print(f"Requirement Coverage Score:          {audit['coverage_pct']:.1f}%")

    if audit['missing_screens']:
        print(f"\nMissing Screens ({len(audit['missing_screens'])}):")
        for ms in audit['missing_screens']:
            print(f"  ❌ {ms}")
    else:
        print("\n✅ 100% of declared vault screens are covered by artifact frames!")

    if args.audit_only:
        return

    # Assemble Prototype
    print(f"\n==> Assembling master interactive prototype...")
    assemble_master_prototype(project_dir, frames, role_specs, target_file=args.target)

if __name__ == "__main__":
    main()
