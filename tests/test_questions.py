"""W2 — question tracking and the outbox: tags, age/blocked ranking, packs per Jira key, sent stamping, answer pre-match."""
import json
import os

from helpers import fresh, read, run, write_json

from bigin.edit import question_block
from bigin.vault import q_tag


def _j(root, *a):
    code, out = run(root, "--json", *a)
    assert code == 0, out
    return json.loads(out)


def test_tag_is_stable_across_tags_and_whitespace_and_asked_is_stamped():
    a = "Is there a maximum amount a parent may request? (owner: client) (ref: INT-001 #2)"
    b = "Is  there a maximum amount a parent may request?   (owner: dev) (asked: 2026-01-01) (sent: 2026-01-02 via X)"
    assert q_tag(a) == q_tag(b) and len(q_tag(a)) == 6
    assert "(asked: 2026-09-27)" in question_block("Is it?", owner="client")[0]
    assert "(asked:" not in question_block("Is it?", checked=True)[0]


def test_list_ranks_blocked_first_and_ages_from_asked():
    root, _ = fresh("comm-vault")
    items = _j(root, "questions", "list")
    assert items and items[0]["blocks"] == ["UC-001"], items          # the one holding a UC at needs-clarification
    assert all(i["blocks"] == [] for i in items[1:]), items
    # age counts days from (asked:), and the filter narrows by owner
    p = os.path.join(root, "01-Requirements/_ucs")
    uc = os.path.join(p, [f for f in os.listdir(p) if f.startswith("UC-001")][0])
    s = open(uc, encoding="utf-8").read()
    s = s.replace("(owner: client) (ref: INT-001 #2)", "(owner: client) (ref: INT-001 #2) (asked: 2026-09-20)")
    open(uc, "w", encoding="utf-8", newline="\n").write(s)
    items = _j(root, "questions", "list", "--owner", "client")
    assert items[0]["age"] == 7, items
    assert _j(root, "questions", "list", "--owner", "dev") == []


def test_pack_groups_by_jira_key_stamps_sent_and_does_not_resend():
    root, _ = fresh("comm-vault")
    note = os.path.join(root, "00-Inbox/INT-001.md")
    s = open(note, encoding="utf-8").read().replace("\nid: INT-001\n", "\nid: INT-001\njira_key: GRANT-12\n", 1)
    open(note, "w", encoding="utf-8", newline="\n").write(s)
    packs = {p["target"]: p for p in _j(root, "questions", "pack", "--owner", "client")}
    assert set(packs) == {"GRANT-12", "client"}, packs
    assert len(packs["GRANT-12"]["questions"]) == 1 and len(packs["client"]["questions"]) == 2, packs
    text = read(root, packs["GRANT-12"]["pack"])
    assert "[q:" + packs["GRANT-12"]["questions"][0] + "] Is there a maximum amount" in text
    assert "(owner:" not in text and "(ref:" not in text and "INT-001" not in text      # nothing from vault vocabulary
    res = _j(root, "questions", "sent", packs["GRANT-12"]["pack"])
    assert res["stamped"] >= 1 and res["target"] == "GRANT-12", res
    assert "(sent: 2026-09-27 via GRANT-12)" in read(root, "01-Requirements/_ucs/" + [
        f for f in os.listdir(os.path.join(root, "01-Requirements/_ucs")) if f.startswith("UC-001")][0])
    again = {p["target"] for p in _j(root, "questions", "pack", "--owner", "client")}
    assert "GRANT-12" not in again, again                                                 # already sent
    assert any(i["sent"] for i in _j(root, "questions", "list"))


def test_tagged_reply_is_prematched_untagged_is_not():
    from bigin.intake import communication
    from bigin import questions
    root, v = fresh("comm-vault")
    tag = _j(root, "questions", "list")[0]["tag"]
    spec = write_json(root, "spec.json", {"title": "Reply", "kind": "requirement", "source": "email", "source_ref": "Dana",
                                          "blocks": [{"kind": "email", "ref": "Dana 2026-09-28",
                                                      "text": f"[q:{tag}] Yes, 5000 maximum.\n\nAlso unrelated."}]})
    nid = communication.scaffold(v, spec)["id"]
    d = v.load_id(nid)
    assert d.fm_list("prematched_answers") == [f"q:{tag} @ SRC-1"], d.fm_list("prematched_answers")
    pm = questions.prematched(v, d)
    assert pm and pm[0]["tag"] == tag and "maximum amount" in pm[0]["question"], pm
    spec2 = write_json(root, "spec2.json", {"title": "Reply2", "kind": "requirement", "source": "email", "source_ref": "Dana",
                                            "blocks": [{"kind": "email", "ref": "Dana", "text": "Yes, five thousand."}]})
    d2 = v.load_id(communication.scaffold(v, spec2)["id"])
    assert d2.fm_list("prematched_answers") == []


def test_dev_and_client_questions_never_share_a_pack():
    root, _ = fresh("comm-vault")
    note = os.path.join(root, "00-Inbox/INT-001.md")
    s = open(note, encoding="utf-8").read().replace("\nid: INT-001\n", "\nid: INT-001\njira_key: GRANT-12\n", 1)
    open(note, "w", encoding="utf-8", newline="\n").write(s)
    ucp = os.path.join(root, "01-Requirements/_ucs", [f for f in os.listdir(os.path.join(root, "01-Requirements/_ucs")) if f.startswith("UC-001")][0])
    s = open(ucp, encoding="utf-8").read().replace("## 6.", "- [ ] Q: Does table PAY_TX store cents? (owner: dev) (ref: INT-001 #2)\n\n## 6.", 1)
    open(ucp, "w", encoding="utf-8", newline="\n").write(s)
    a = _j(root, "questions", "pack", "--owner", "client")
    b = _j(root, "questions", "pack", "--owner", "dev")
    files = {p["pack"] for p in a + b}
    assert len(files) == len({p["pack"] for p in a}) + len({p["pack"] for p in b}), (a, b)
    for p in a:
        assert "PAY_TX" not in read(root, p["pack"])
    assert any("PAY_TX" in read(root, p["pack"]) for p in b)
    assert all(os.path.exists(os.path.join(root, p["pack"])) for p in a + b)          # none overwritten


def test_same_words_on_unrelated_ucs_are_two_questions_and_feature_filter_is_exact():
    root, _ = fresh("comm-vault")
    d = os.path.join(root, "01-Requirements/_ucs")
    for uc in ("UC-002", "UC-003"):
        p = os.path.join(d, [f for f in os.listdir(d) if f.startswith(uc)][0])
        s = open(p, encoding="utf-8").read().replace("## 6.", "- [ ] Q: Who must approve this? (owner: client)\n\n## 6.", 1)
        open(p, "w", encoding="utf-8", newline="\n").write(s)
    items = [i for i in _j(root, "questions", "list") if i["text"] == "Who must approve this?"]
    assert len(items) == 2 and items[0]["tag"] != items[1]["tag"], items
    assert _j(root, "questions", "list", "--feature", "grant") == []                      # a prefix matches nothing
    assert _j(root, "questions", "list", "--feature", "grant-intake")


def test_tag_matches_through_markdown_escaping():
    from bigin.questions import TAG_RE
    for form in ("[q:3fa9c1]", "\\[q:3fa9c1\\]", "q:3fa9c1", "[Q:3FA9C1]"):
        assert TAG_RE.findall("Yes. " + form + " 5000")[0].lower() == "3fa9c1", form
