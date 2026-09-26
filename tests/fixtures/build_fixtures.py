#!/usr/bin/env python3
"""Regenerate tests/fixtures/{comm-vault,code-vault} — small, lint-clean v1.8.12-shaped vaults.

    python3 tests/fixtures/build_fixtures.py

comm-vault  3 INT notes (email / meeting / email-raw), 2 hubs, 4 UCs, 6 BRs, legacy staged
            ## Discussion entries (for migrate discussion-to-ledger) and v1.8 guidance comments
            (for migrate strip-guidance).
code-vault  1 codebase INT note carrying 20 rule cards as signal rows, 2 hubs, 3 UCs, plus
            cards.json / assignment.json for `bigin intake codebase`.
The v1.8 templates live in lib/bigin/legacy_templates/; the fixtures are built from them so the
guidance blocks match what real v1.8 vaults carry.
"""
import json
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
LEG = os.path.join(HERE, "..", "..", "lib", "bigin", "legacy_templates")
DATE = "2026-09-20"


def w(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text if text.endswith("\n") else text + "\n")


def legacy(name):
    with open(os.path.join(LEG, f"{name}.v1.8.md"), encoding="utf-8") as f:
        return f.read()


def body_of(tpl):
    return tpl[tpl.index("\n---", 4) + 4:].lstrip("\n")


def fm(d):
    out = ["---"]
    for k, v in d.items():
        if isinstance(v, list):
            out.append(f"{k}: [{', '.join(v)}]")
        elif isinstance(v, bool):
            out.append(f"{k}: {'true' if v else 'false'}")
        else:
            out.append(f"{k}: {v}")
    out.append("---")
    return "\n".join(out) + "\n\n"


def project(client, grounding, extra=""):
    return f"""---
type: config
client: {client}
client_emails: []
team_emails: []
intake_lookback_days: 14
email_provider: outlook
meeting_provider: fathom
project_mode: greenfield
platform: web
grounding: {grounding}
conflict_policy: {'code-first' if grounding != 'communication' else 'ask'}
{extra}workspace_version: 1.8.12
updated: {DATE}
---

# Vault settings — `{client}`

Fixture vault for the bigin engine tests.
"""


def features(rows):
    lines = ["---", "type: feature-map", "status: draft", "version: 1.0", f"updated: {DATE}", "---", "",
             "# Feature Map", "", "| Slug | Feature | Status | UC | Code areas | Sources | Notes |",
             "|------|---------|--------|----|------------|---------|-------|"]
    for r in rows:
        lines.append("| " + " | ".join(r) + " |")
    return "\n".join(lines) + "\n"


def uc(ident, title, primary, feats, brs, sources, status, s1, steps, flows, s4, still_open, discussion,
       changelog, version="1.0", legacy_comments=True):
    """A UC built on the v1.8 template body so its guidance comments are the real ones."""
    b = body_of(legacy("use-case"))
    b = re.sub(r"^# `UC-<NNN>[^`]*`", f"# `{ident} {title}`", b, count=1, flags=re.M)
    b = re.sub(r"\n> \[!summary\]-.*?(?=\n## )", "\n", b, count=1, flags=re.S)
    # § 1 fields
    for field, val in s1.items():
        if field in ("Pre-conditions", "Post-conditions (success)", "Post-conditions (failure)"):
            b = re.sub(rf"(\* \*\*{re.escape(field)}:\*\*\n)  \* `<[^\n]*>`", lambda m: m.group(1) + "\n".join(f"  * {x}" for x in val), b, count=1)
        else:
            b = re.sub(rf"(\* \*\*{re.escape(field)}:\*\*) `<[^\n]*>`", lambda m: m.group(1) + " " + val, b, count=1)
    b = b.replace("| **S1** | | |", "\n".join(f"| **{s}** | {a} | {r} |" for s, a, r in steps) or "| **S1** | | |")
    b = re.sub(r"### A1: `<name>`.*?(?=\n## 4\.)", flows.rstrip() + "\n" if flows else "", b, count=1, flags=re.S)
    b = b.replace("| :--- | :--- | :--- |\n\n## 5.", "| :--- | :--- | :--- |\n" + "".join(f"| {x} | {y} | {z} |\n" for x, y, z in s4) + "\n## 5.")
    b = b.replace("**Still open**\n", "**Still open**\n\n" + "".join(f"- [ ] Q: {q}\n  A:\n" for q in still_open), 1)
    if discussion:
        b = re.sub(r"(## Discussion\n<!--.*?-->\n)", lambda m: m.group(1) + "\n" + discussion.rstrip() + "\n", b, count=1, flags=re.S)
    b = re.sub(r"(## Changelog\n)- 1\.0 \(YYYY-MM-DD\) — created from `<INT-###>`", lambda m: m.group(1) + changelog.rstrip(), b, count=1)
    head = fm({"id": ident, "type": "use-case", "title": f'"{title}"', "status": status, "version": version,
               "synced": True, "level": "user-goal", "scope": "Acme Grants Portal", "primary_feature": primary,
               "features": feats, "brs": brs, "entities": [], "pain_points": [], "sources": sources, "links": [],
               "attachments": [], "absorbs": [], "owner": "team", "updated": DATE})
    if not legacy_comments:
        b = re.sub(r"<!--.*?-->\n?", "", b, flags=re.S)
        b = re.sub(r"\n{3,}", "\n\n", b)
    return head.rstrip("\n") + "\n\n" + b


def br(ident, title, feature, ucs, sources, status, statement, discussion="", questions=(), changelog=None):
    b = body_of(legacy("br"))
    b = re.sub(r"^# `BR-<NNN>[^`]*`", f"# `{ident} {title}`", b, count=1, flags=re.M)
    b = re.sub(r"(^# [^\n]*\n)(.*?)(?=^## )", lambda m: m.group(1) + "\n" + statement + "\n\n", b, count=1, flags=re.S | re.M)
    if discussion:
        b = re.sub(r"(## Discussion\n<!--.*?-->\n)", lambda m: m.group(1) + "\n" + discussion.rstrip() + "\n", b, count=1, flags=re.S)
    if questions:
        b = re.sub(r"(## Open Questions\n<!--.*?-->\n)", lambda m: m.group(1) + "\n" + "".join(f"- [ ] Q: {q}\n  A:\n" for q in questions), b, count=1, flags=re.S)
    b = re.sub(r"(## Changelog\n)- 1\.0 \(YYYY-MM-DD\) — created from `<INT-###>`",
               lambda m: m.group(1) + (changelog or f"- 1.0 ({DATE}) — created from {', '.join(sources)}"), b, count=1)
    head = fm({"id": ident, "type": "business-rule", "title": f'"{title}"', "status": status, "version": "1.0",
               "feature": feature, "uc": ucs, "fr": [], "sources": sources, "links": [], "owner": "team", "updated": DATE})
    return head.rstrip("\n") + "\n\n" + b


def hub(slug, name, status, ucs, brs, sources, desc, signal_rows, uc_rows, ready_rows, gates, coverage_rows=()):
    b = body_of(legacy("feature-hub"))
    b = re.sub(r"^# `<Feature Name>`\n\n`<one-line description[^\n]*`", f"# {name}\n\n{desc}", b, count=1, flags=re.M)
    b = b.replace("| # | Signal | Type | Source | Status | Destination | Notes |\n|---|--------|------|--------|--------|--------------|-------|",
                  "| # | Signal | Type | Source | Status | Destination | Notes |\n|---|--------|------|--------|--------|--------------|-------|\n"
                  + "\n".join("| " + " | ".join(r) + " |" for r in signal_rows))
    b = b.replace("| UC | Goal | Role | Status |\n|----|------|------|--------|",
                  "| UC | Goal | Role | Status |\n|----|------|------|--------|\n" + "\n".join("| " + " | ".join(r) + " |" for r in uc_rows))
    b = b.replace("| # | Gap | Lens | Raised | Status | Notes |\n|---|-----|------|--------|--------|-------|",
                  "| # | Gap | Lens | Raised | Status | Notes |\n|---|-----|------|--------|--------|-------|"
                  + "".join("\n| " + " | ".join(r) + " |" for r in coverage_rows))
    b = b.replace("| — no UC/BR yet — | — | No | Human decision: brainstorm now / draft the use case directly / hold |",
                  "\n".join("| " + " | ".join(r) + " |" for r in ready_rows))
    b = re.sub(r"(## Open Questions / Gates\n<!--.*?-->\n)", lambda m: m.group(1) + "\n" + "".join(f"- [ ] Q: {q}\n  A:\n" for q in gates), b, count=1, flags=re.S)
    b = b.replace("- (YYYY-MM-DD) — hub created", f"- ({DATE}) — hub created")
    head = fm({"type": "feature-hub", "feature": slug, "name": f'"{name}"', "status": status, "uc": ucs, "br": brs,
               "fr": [], "code_areas": [], "sources": sources, "prd": "", "epics": [], "stories": [], "uiux": "",
               "entities": [], "updated": DATE}).replace("prd: \n", "prd:\n").replace("uiux: \n", "uiux:\n")
    return head.rstrip("\n") + "\n\n" + b


def note(ident, kind, title, source, source_ref, status, raw_blocks, rows, questions=(), declared=()):
    lines = [f"id: {ident}", "type: intake", f"kind: {kind}", f'title: "{title}"', f"status: {status}",
             f"source: {source}", f'source_ref: "{source_ref}"', "source_ids: []", "attachments: []",
             "raw_sources: [" + ", ".join(f'"SRC-{i + 1} · {k} · {r}"' for i, (k, r, _) in enumerate(raw_blocks)) + "]",
             "participants: []", "declared_features: [" + ", ".join(declared) + "]", "feature:", "links: []", "tags: []",
             f"updated: {DATE}"]
    raw = "\n\n".join(f"### SRC-{i + 1} · {k} · {r}\n\n{t}" for i, (k, r, t) in enumerate(raw_blocks))
    table = ["| # | Type | Signal | Why | Source | Feature | Status | Notes |",
             "|---|------|--------|-----|--------|---------|--------|-------|"] + ["| " + " | ".join(r) + " |" for r in rows]
    qs = "".join(f"- [ ] Q: {q}\n  A:\n" for q in questions)
    return ("---\n" + "\n".join(lines) + "\n---\n\n## Raw\n<!-- ALL captured source material, verbatim. -->\n\n" + raw
            + "\n\n## Capture history\n- " + DATE + " (attempt 1) — captured\n\n## Referenced but not captured\n\n"
            + "## Extracted signals\n<!-- populated by /extract-signal -->\n\n" + ("\n".join(table) if rows else "\n".join(table[:2]))
            + "\n\n## Open Questions\n<!-- - [ ] Q: ... (owner: client|team) ↦ UC-### -->\n" + (("\n" + qs) if qs else ""))


def register(name, header, sep, rows=()):
    return (f"---\ntype: register\nupdated: {DATE}\n---\n\n# {name}\n\n{header}\n{sep}\n"
            + "".join("| " + " | ".join(r) + " |\n" for r in rows))


# ============================================================================ comm-vault

def build_comm(root):
    shutil.rmtree(root, ignore_errors=True)
    w(root, "_bigin/system/project.md", project("Acme Grants", "communication"))
    w(root, "01-Requirements/FEATURES.md", features([
        ["grant-intake", "Apply for a grant", "committed", "UC-001 · UC-002", "", "INT-001, INT-002", ""],
        ["payments", "Pay approved grants", "committed", "UC-003 · UC-004", "", "INT-002", ""],
        ["reporting", "Report on grants", "proposed", "", "", "", "no hub yet"],
    ]))
    w(root, "01-Requirements/PAIN-POINTS.md", register("Pain Point Register",
      "| PP-### | Statement | Status | Proposed solution | Resolved by | Feature |",
      "|--------|-----------|--------|--------------------|--------------|---------|",
      [["PP-001", "Applicants re-type the same school details every year", "open", "", "", "grant-intake"]]))
    w(root, "01-Requirements/ENTITIES.md", register("Entities",
      "| EN-### | Entity | Status | Fields (so far) | Features | Notes |",
      "|--------|--------|--------|------------------|----------|-------|",
      [["EN-001", "Application", "proposed", "School name; Amount requested", "grant-intake", "from INT-001 #2"]]))
    w(root, "01-Requirements/DESIGN-PRINCIPLES.md", register("Design Principles",
      "| # | Principle | Why | Category | Source | Status | Notes |",
      "|---|-----------|-----|----------|--------|--------|-------|"))

    w(root, "00-Inbox/INT-001.md", note("INT-001", "requirement", "Grant intake requirements (email)", "email",
      "Re: grant portal scope", "in-review",
      [("email", "Dana Client 2026-09-01", "We need parents to apply online. The application must capture the school name and the amount requested. Amounts over $5,000 need a second reviewer. Applicants hate re-typing school details every year.")],
      [["1", "requirement", "Parents apply for a grant online", "not stated", "Dana Client 2026-09-01", "grant-intake", "new", ""],
       ["2", "requirement", "The application captures the school name and the amount requested", "not stated", "Dana Client 2026-09-01", "grant-intake", "new", "EN-001"],
       ["3", "constraint", "Amounts over $5,000 need a second reviewer", "not stated", "Dana Client 2026-09-01", "grant-intake", "new", ""],
       ["4", "pain-point", "Applicants re-type school details every year", "", "Dana Client 2026-09-01", "grant-intake", "new", "PP-001"]],
      declared=["grant-intake"]))
    w(root, "00-Inbox/INT-002.md", note("INT-002", "requirement", "Kick-off meeting", "meeting",
      "Kick-off 2026-09-05", "in-review",
      [("transcript", "Fathom kick-off 2026-09-05", "[00:01] Dana: A reviewer approves or rejects each application. [00:04] Dana: Approved grants are paid by bank transfer within 10 days. [00:06] Sam: A rejected applicant can appeal once. [00:09] Dana: Payments over $10,000 need finance sign-off. [00:11] Sam: Should partial payments be allowed? [00:13] Dana: The applicant must confirm their bank details before payment.")],
      [["1", "requirement", "A reviewer approves or rejects each application", "not stated", "[00:01]", "grant-intake", "new", ""],
       ["2", "requirement", "Approved grants are paid by bank transfer within 10 days", "not stated", "[00:04]", "payments", "new", ""],
       ["3", "requirement", "A rejected applicant can appeal once", "not stated", "[00:06]", "grant-intake", "new", ""],
       ["4", "constraint", "Payments over $10,000 need finance sign-off", "not stated", "[00:09]", "payments", "new", ""],
       ["5", "question", "Should partial payments be allowed?", "", "[00:11]", "payments", "question", ""],
       ["6", "requirement", "The applicant confirms their bank details before payment", "not stated", "[00:13]", "payments", "new", ""]],
      declared=["grant-intake", "payments"]))
    w(root, "00-Inbox/INT-003.md", note("INT-003", "feedback", "Follow-up email on appeals", "email",
      "Re: appeals", "raw",
      [("email", "Dana Client 2026-09-12", "Appeals must be filed within 14 days of the rejection. Also, reviewers want to see the applicant's previous grants when reviewing.")],
      []))

    s1_001 = {"Primary Actor": "Parent", "Secondary Actor(s)": "Reviewer", "Business Need / Goal": "Apply for a school grant online",
              "Trigger": "not stated", "Pre-conditions": ["The parent has an account"],
              "Post-conditions (success)": ["An application is recorded and awaiting review"],
              "Post-conditions (failure)": ["No partial application is kept"]}
    disc_001 = (f"- **INT-002** (staged {DATE}): \"A rejected applicant can appeal once\" (grant-intake hub row #5) → proposed: new step after S4: Parent appeals a rejection once || System records the appeal and returns the application to review.\n"
                f"- **INT-001** (staged {DATE}): \"Parents apply online\" (grant-intake hub row #1) → proposed: § 1 Trigger becomes: The parent opens the grant application.\n")
    w(root, "01-Requirements/_ucs/UC-001 Submit a grant application.md", uc(
        "UC-001", "Submit a grant application", "grant-intake", ["grant-intake", "payments"], ["BR-001", "BR-002"],
        ["INT-001", "INT-002"], "needs-clarification", s1_001,
        [("S1", "Parent starts a grant application.", "System opens a new draft application."),
         ("S2", "Parent provides the school name and the amount requested.", "System validates both are present."),
         ("S3", "Parent submits the application.", "System records it and routes it to a reviewer."),
         ("S4", "Reviewer approves or rejects the application.", "System records the decision and notifies the parent.")],
        "### E1: The amount is missing\n* **Branch point:** S2\n* **Failure condition:** The amount requested is blank.\n1. System asks for the amount.\n2. **Ends:** the parent stays on the draft.\n",
        [("BR-001", "If the amount requested exceeds $5,000, then a second reviewer must approve the application.", "S4"),
         ("BR-002", "If an application is submitted, then the school name and the amount requested must both be present.", "S2")],
        ["Is there a maximum amount a parent may request? (owner: client) (ref: INT-001 #2)"],
        disc_001,
        f"- 1.0 ({DATE}) — created from INT-001\n- 1.1 ({DATE}) — INT-002: reviewer decision added as S4"))
    w(root, "01-Requirements/_ucs/UC-002 Review an application.md", uc(
        "UC-002", "Review an application", "grant-intake", ["grant-intake"], [], ["INT-002"], "draft",
        {"Primary Actor": "Reviewer", "Secondary Actor(s)": "none", "Business Need / Goal": "Decide on each application",
         "Trigger": "An application is routed to the reviewer", "Pre-conditions": ["An application is awaiting review"],
         "Post-conditions (success)": ["The application is approved or rejected"], "Post-conditions (failure)": ["The application stays awaiting review"]},
        [("S1", "Reviewer opens the next application awaiting review.", "System shows the application."),
         ("S2", "Reviewer approves or rejects it.", "System records the decision.")],
        "", [], [], "", f"- 1.0 ({DATE}) — created from INT-002"))
    w(root, "01-Requirements/_ucs/UC-003 Pay an approved grant.md", uc(
        "UC-003", "Pay an approved grant", "payments", ["payments", "grant-intake"], ["BR-004", "BR-005"], ["INT-002"],
        "draft",
        {"Primary Actor": "Finance officer", "Secondary Actor(s)": "Bank", "Business Need / Goal": "Pay approved grants on time",
         "Trigger": "An application is approved", "Pre-conditions": ["The application is approved"],
         "Post-conditions (success)": ["The payment is sent and recorded"], "Post-conditions (failure)": ["No payment is recorded as sent"]},
        [("S1", "Finance officer opens the approved grants awaiting payment.", "System lists them oldest first."),
         ("S2", "Finance officer releases the payment.", "System sends a bank transfer and records it.")],
        "", [("BR-004", "If an approved grant is not paid within 10 days, then it must be flagged as overdue.", "S2"),
             ("BR-005", "If a payment exceeds $10,000, then finance must sign it off before release.", "S2")],
        [], "", f"- 1.0 ({DATE}) — created from INT-002"))
    w(root, "01-Requirements/_ucs/UC-004 Refund an overpayment.md", uc(
        "UC-004", "Refund an overpayment", "payments", ["payments"], [], ["INT-002"], "draft",
        {}, [], "", [], [], "", f"- 1.0 ({DATE}) — created from INT-002"))

    w(root, "01-Requirements/_brs/BR-001 Second reviewer over 5000.md", br(
        "BR-001", "Second reviewer over 5000", "grant-intake", ["UC-001"], ["INT-001"], "draft",
        "If the amount requested exceeds $5,000, then a second reviewer must approve the application."))
    w(root, "01-Requirements/_brs/BR-002 School and amount are required.md", br(
        "BR-002", "School and amount are required", "grant-intake", ["UC-001"], ["INT-001"], "draft",
        "If an application is submitted, then the school name and the amount requested must both be present."))
    w(root, "01-Requirements/_brs/BR-003 One appeal per rejection.md", br(
        "BR-003", "One appeal per rejection", "grant-intake", [], ["INT-002"], "needs-clarification",
        "If an application is rejected, then the applicant may appeal it once.",
        questions=["Is there a deadline for filing an appeal? (owner: client) (ref: INT-002 #3)"]))
    w(root, "01-Requirements/_brs/BR-004 Pay within 10 days.md", br(
        "BR-004", "Pay within 10 days", "payments", ["UC-003"], ["INT-002"], "draft",
        "If an approved grant is not paid within 10 days, then it must be flagged as overdue."))
    w(root, "01-Requirements/_brs/BR-005 Finance sign-off over 10000.md", br(
        "BR-005", "Finance sign-off over 10000", "payments", ["UC-003"], ["INT-002"], "draft",
        "If a payment exceeds $10,000, then finance must sign it off before release.",
        discussion=f"- **INT-002** (staged {DATE}): \"Payments over $10,000 need finance sign-off\" (payments hub row #3) → proposed: rule becomes: If a payment exceeds $10,000, then finance must sign it off before release, and the sign-off is recorded with the approver's name.\n"))
    w(root, "01-Requirements/_brs/BR-006 Bank details confirmed.md", br(
        "BR-006", "Bank details confirmed", "payments", [], ["INT-002"], "draft",
        "If a payment is released, then the applicant must have confirmed their bank details first."))

    w(root, "01-Requirements/_features/grant-intake.md", hub(
        "grant-intake", "Apply for a grant", "committed", ["UC-001", "UC-002", "UC-003"], ["BR-001", "BR-002", "BR-003"],
        ["INT-001", "INT-002"], "Parents apply online for a school grant; reviewers decide.",
        [["1", "**Online application** — parents apply online; the application captures school name and amount", "requirement", "INT-001 #1, #2 — Dana Client 2026-09-01", "applied", "UC-001 S1 · UC-001 S2", ""],
         ["2", "Amounts over $5,000 need a second reviewer", "constraint", "INT-001 #3 — Dana Client 2026-09-01", "applied", "BR-001", ""],
         ["3", "Applicants re-type school details every year", "pain-point", "INT-001 #4 — Dana Client 2026-09-01", "applied", "PP-001", "PP-001"],
         ["4", "A reviewer approves or rejects each application", "requirement", "INT-002 #1 — [00:01]", "applied", "UC-001 S4 · UC-002 S2", ""],
         ["5", "A rejected applicant can appeal once", "requirement", "INT-002 #3 — [00:06]", "staged", "UC-001 · BR-003", ""]],
        [["UC-001", "Submit a grant application", "owns", "needs-clarification"],
         ["UC-002", "Review an application", "owns", "draft"],
         ["UC-003", "Pay an approved grant", "participates", "draft"]],
        [["UC-001", "needs-clarification", "No", "1 open question"], ["UC-002", "draft", "Yes", ""],
         ["UC-003", "draft", "Yes", ""], ["BR-001", "draft", "Yes", ""], ["BR-002", "draft", "Yes", ""],
         ["BR-003", "needs-clarification", "No", "1 open question"]],
        ["Is there a maximum amount a parent may request? (owner: client) (ref: UC-001)"],
        [["1", "Nothing describes how a parent withdraws an application they no longer want.", "lifecycle", DATE, "open", ""]]))
    w(root, "01-Requirements/_features/payments.md", hub(
        "payments", "Pay approved grants", "committed", ["UC-001", "UC-003", "UC-004"], ["BR-004", "BR-005", "BR-006"],
        ["INT-002"], "Finance pays approved grants by bank transfer.",
        [["1", "Approved grants are paid by bank transfer within 10 days", "requirement", "INT-002 #2 — [00:04]", "applied", "UC-003 S2 · BR-004", ""],
         ["2", "Should partial payments be allowed?", "question", "INT-002 #5 — [00:11]", "question", "", ""],
         ["3", "Payments over $10,000 need finance sign-off", "constraint", "INT-002 #4 — [00:09]", "staged", "BR-005", ""],
         ["4", "The applicant confirms their bank details before payment", "requirement", "INT-002 #6 — [00:13]", "new", "", ""]],
        [["UC-001", "Submit a grant application", "participates", "needs-clarification"],
         ["UC-003", "Pay an approved grant", "owns", "draft"],
         ["UC-004", "Refund an overpayment", "owns", "draft"]],
        [["UC-001", "needs-clarification", "No", "1 open question"], ["UC-003", "draft", "Yes", ""],
         ["UC-004", "draft", "No", "not yet drafted"], ["BR-004", "draft", "Yes", ""], ["BR-005", "draft", "No", "staged content awaiting fold-in"],
         ["BR-006", "draft", "Yes", ""]],
        ["Should partial payments be allowed? (owner: client) (ref: INT-002 #5)"]))


# ============================================================================ code-vault

CARDS = [
    ("XR-CALC-001", "Rate is weight times tariff", "Calculation", "P0", "backend/Rates/Calc.php:10-30", "rates", "C1.1",
     "The shipment price is the weight in hundredweight multiplied by the lane tariff.", "", ""),
    ("XR-CALC-002", "Minimum charge applies", "Calculation", "P1", "backend/Rates/Calc.php:31-40", "rates", "C1.1",
     "A shipment is never priced below the lane's minimum charge.", "", ""),
    ("XR-CALC-003", "Fuel surcharge percentage", "Calculation", "P1", "backend/Rates/Fuel.php:5-22", "rates", "C1.1",
     "A fuel surcharge is added as a percentage of the base price, read from settings.", "", ""),
    ("XR-VALI-004", "Tariff import rejects negative values", "Validation", "P1", "backend/Rates/Import.php:44-60", "rates", "C1.2",
     "A tariff import is refused when any cell holds a negative number.", "", ""),
    ("XR-VALI-005", "Tariff import accepts blank cells", "Validation", "P2", "backend/Rates/Import.php:61-70", "rates", "C1.2",
     "Blank tariff cells are imported as zero.", "Blank cells silently price a lane at zero.", "Should a blank tariff cell block the import?"),
    ("XR-POLI-006", "Only staff edit tariffs", "Policy", "P0", "backend/Rates/Routes.php:12", "rates", "C1.2",
     "Only staff accounts may edit a tariff.", "", ""),
    ("XR-LIFE-007", "Tariff versions are kept", "Lifecycle", "P1", "backend/Rates/Tariff.php:80-99", "rates", "C1.2",
     "Saving a tariff creates a new version and keeps the old one.", "", ""),
    ("XR-CALC-008", "Discount codes cap at 20%", "Calculation", "P1", "backend/Rates/Discount.php:14-30", "rates", "C1.3",
     "A discount code can reduce the price by at most 20%.", "", ""),
    ("XR-VALI-009", "Discount code must be active", "Validation", "P1", "backend/Rates/Discount.php:31-44", "rates", "C1.3",
     "An inactive or expired discount code is refused at checkout.", "", ""),
    ("XR-LIFE-010", "Discount code expiry", "Lifecycle", "P2", "backend/Rates/Discount.php:45-60", "rates", "C1.3",
     "A discount code stops working at midnight on its expiry date.", "", ""),
    ("XR-VALI-011", "Booking needs a move date", "Validation", "P0", "backend/Booking/Request.php:10-22", "bookings", "C2.1",
     "A booking request is refused without a move date.", "", ""),
    ("XR-VALI-012", "Move date not in the past", "Validation", "P0", "backend/Booking/Request.php:23-30", "bookings", "C2.1",
     "A move date in the past is refused.", "", ""),
    ("XR-LIFE-013", "Booking starts as draft", "Lifecycle", "P1", "backend/Booking/Booking.php:40-52", "bookings", "C2.1",
     "A new booking is saved with status draft.", "", ""),
    ("XR-LIFE-014", "Draft becomes confirmed on payment", "Lifecycle", "P0", "backend/Booking/Pay.php:60-88", "bookings", "C2.2",
     "A draft booking becomes confirmed when its deposit is paid.", "", ""),
    ("XR-POLI-015", "Consumer sees own bookings only", "Policy", "P0", "backend/Booking/Routes.php:5-18", "bookings", "C2.2",
     "A consumer can list and open only their own bookings.", "", ""),
    ("XR-CALC-016", "Deposit is 10 percent", "Calculation", "P0", "backend/Booking/Pay.php:20-40", "bookings", "C2.2",
     "The deposit is 10% of the quoted price, rounded to cents.", "", ""),
    ("XR-LIFE-017", "Cancelled booking frees the mover", "Lifecycle", "P1", "backend/Booking/Cancel.php:10-50", "bookings", "C2.3",
     "Cancelling a booking releases the mover's calendar slot.", "", ""),
    ("XR-POLI-018", "No refund after the move date", "Policy", "P1", "backend/Booking/Cancel.php:51-70", "bookings", "C2.3",
     "A booking cancelled on or after its move date gets no refund.", "", "Is the no-refund rule intended for moves cancelled on the day?"),
    ("XR-VALI-019", "Cancel reason is optional", "Validation", "P2", "backend/Booking/Cancel.php:5-9", "bookings", "C2.3",
     "A cancellation may be submitted without a reason.", "", ""),
    ("XR-CALC-020", "Late cancellation fee", "Calculation", "P1", "backend/Booking/Cancel.php:71-90", "bookings", "C2.3",
     "Cancelling within 48 hours of the move charges 25% of the deposit.", "The fee is taken from the deposit even when it was refunded.", ""),
]


def cards_store():
    rules = {}
    for i, (xr, name, cat, pri, src, slug, cap, plain, defect, q) in enumerate(CARDS):
        r = {"name": name, "category": cat, "priority": pri, "source": f"repos/{src}", "plainEnglish": plain,
             "given": "", "when": "", "then": "", "confidence": "High", "_xr": xr, "_run": "fixture"}
        if defect:
            r["suspectedDefect"] = defect
        if q:
            r["smeQuestion"] = q
        rules[f"k{i:03d}"] = r
    return {"rules": rules, "dataObjects": {}, "runs": []}


def assignment():
    return {xr: {"slug": slug, "cap": cap, "lane": "BR", "surface": "backend"} for xr, _n, _c, _p, _s, slug, cap, *_ in CARDS}


def build_code(root):
    shutil.rmtree(root, ignore_errors=True)
    w(root, "_bigin/system/project.md", project("MoveCo", "codebase", "repos: [repos/backend]\ncoverage_id_pattern: \"XR-[A-Z]+-\\\\d{3}\"\n"))
    w(root, "01-Requirements/FEATURES.md", features([
        ["rates", "Configure rates", "built", "UC-001 · UC-002", "backend", "INT-001", "`C1`"],
        ["bookings", "Book a move", "built", "UC-003", "backend", "INT-001", "`C2`"],
    ]))
    w(root, "01-Requirements/PAIN-POINTS.md", register("Pain Point Register",
      "| PP-### | Statement | Status | Proposed solution | Resolved by | Feature |",
      "|--------|-----------|--------|--------------------|--------------|---------|"))
    w(root, "01-Requirements/ENTITIES.md", register("Entities",
      "| EN-### | Entity | Status | Fields (so far) | Features | Notes |",
      "|--------|--------|--------|------------------|----------|-------|"))
    rows = []
    for i, (xr, name, cat, pri, src, slug, cap, plain, defect, q) in enumerate(CARDS[:12]):
        rows.append([str(i + 1), "decision", f"`{xr}` — {plain}", "", f"SRC-1 · rule pack · `repos/{src}`", slug, "new", ""])
    w(root, "00-Inbox/INT-001.md", note("INT-001", "requirement", "Mined business rules (first 12 of 20)", "direct",
      "analysis/rule-pack.md", "in-review", [("attachment", "00-Inbox/_attachments/INT-001/rule-pack.md",
      "Rule pack — see attachment.")], rows, declared=["rates", "bookings"]).replace("source: direct", "source: codebase"))
    uc_rows_rates = [["UC-001", "Price a shipment", "owns", "draft"], ["UC-002", "Maintain tariffs as staff", "owns", "draft"]]
    w(root, "01-Requirements/_features/rates.md", hub(
        "rates", "Configure rates", "built", ["UC-001", "UC-002"], [], ["INT-001"], "Tariffs, surcharges and discount codes.",
        [["1", "**Pricing** — price is weight × tariff; minimum charge; fuel surcharge (`XR-CALC-001`, `XR-CALC-002`, `XR-CALC-003`)", "decision", "INT-001 #1, #2, #3 — SRC-1", "applied", "UC-001 S1 · UC-001 S2", ""],
         ["2", "**Tariff import** — negative values refused; blank cells import as zero (`XR-VALI-004`, `XR-VALI-005`)", "decision", "INT-001 #4, #5 — SRC-1", "new", "", ""],
         ["3", "**Tariff editing** — staff only; versions kept (`XR-POLI-006`, `XR-LIFE-007`)", "decision", "INT-001 #6, #7 — SRC-1", "new", "", ""],
         ["4", "**Discount codes** — cap 20%; must be active; expire at midnight (`XR-CALC-008`, `XR-VALI-009`, `XR-LIFE-010`)", "decision", "INT-001 #8, #9, #10 — SRC-1", "held", "", ""]],
        uc_rows_rates, [["UC-001", "draft", "Yes", ""], ["UC-002", "draft", "Yes", ""]], []))
    w(root, "01-Requirements/_features/bookings.md", hub(
        "bookings", "Book a move", "built", ["UC-003"], [], ["INT-001"], "Consumers book and pay for a move.",
        [["1", "**Booking request** — move date required and not in the past (`XR-VALI-011`, `XR-VALI-012`)", "decision", "INT-001 #11, #12 — SRC-1", "new", "", ""]],
        [["UC-003", "Book a move", "owns", "draft"]], [["UC-003", "draft", "Yes", ""]], []))
    w(root, "01-Requirements/_ucs/UC-001 Price a shipment.md", uc(
        "UC-001", "Price a shipment", "rates", ["rates"], [], ["INT-001"], "draft",
        {"Primary Actor": "Consumer", "Secondary Actor(s)": "none", "Business Need / Goal": "See the price of a move",
         "Trigger": "The consumer asks for a quote", "Pre-conditions": ["A tariff exists for the lane"],
         "Post-conditions (success)": ["A price is shown"], "Post-conditions (failure)": ["No price is shown"]},
        [("S1", "Consumer asks for a quote for a shipment.", "System prices it as weight in hundredweight times the lane tariff (`XR-CALC-001`), never below the lane minimum (`XR-CALC-002`)."),
         ("S2", "—", "System adds the fuel surcharge percentage from settings (`XR-CALC-003`).")],
        "", [], [], "", f"- 1.0 ({DATE}) — created from INT-001", legacy_comments=False))
    w(root, "01-Requirements/_ucs/UC-002 Maintain tariffs as staff.md", uc(
        "UC-002", "Maintain tariffs as staff", "rates", ["rates"], [], ["INT-001"], "draft",
        {"Primary Actor": "Staff", "Secondary Actor(s)": "none", "Business Need / Goal": "Keep tariffs current",
         "Trigger": "not stated", "Pre-conditions": ["The user is signed in as staff"],
         "Post-conditions (success)": ["The tariff is saved"], "Post-conditions (failure)": ["The previous tariff stays live"]},
        [("S1", "Staff uploads a tariff file.", "System imports it.")], "", [], [], "", f"- 1.0 ({DATE}) — created from INT-001",
        legacy_comments=False))
    w(root, "01-Requirements/_ucs/UC-003 Book a move.md", uc(
        "UC-003", "Book a move", "bookings", ["bookings"], [], ["INT-001"], "draft",
        {"Primary Actor": "Consumer", "Secondary Actor(s)": "none", "Business Need / Goal": "Book a mover",
         "Trigger": "The consumer accepts a quote", "Pre-conditions": ["A quote exists"],
         "Post-conditions (success)": ["A booking is saved"], "Post-conditions (failure)": ["No booking is saved"]},
        [("S1", "Consumer submits a booking request.", "System saves the booking.")], "", [], [], "",
        f"- 1.0 ({DATE}) — created from INT-001", legacy_comments=False))
    w(root, "cards.json", json.dumps(cards_store(), indent=2))
    w(root, "assignment.json", json.dumps(assignment(), indent=2))


if __name__ == "__main__":
    build_comm(os.path.join(HERE, "comm-vault"))
    build_code(os.path.join(HERE, "code-vault"))
    print("fixtures rebuilt")
