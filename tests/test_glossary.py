"""The glossary: one hand-edited table of terms, proposed by the filer, fed to agents, checked by lint."""
import json
import os

from helpers import fresh, lint_clean, read, run

from bigin import glossary

G = "01-Requirements/GLOSSARY.md"


def _write(root, rel, text):
    p = os.path.join(root, rel)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


def _file(root, terms):
    p = _write(root, "fil.json", json.dumps({"kind": "filing", "int": "INT-003", "rows": [], "terms": terms}))
    code, out = run(root, "file", "apply", p)
    assert code == 0, out
    return out


def _glossary(root, *rows):
    _write(root, G, "---\ntype: glossary\nupdated:\n---\n\n# Glossary\n\n| Term | Meaning | Also called | Source |\n"
                    "|------|---------|-------------|--------|\n" + "".join(r + "\n" for r in rows))


def test_matching_is_whole_word_plural_and_unicode():
    rows = glossary.parse("| Term | Meaning | Also called | Source |\n|---|---|---|---|\n"
                          "| Grant application | A request for funding | đơn xin tài trợ, submission | Nam |\n"
                          "| Reviewer |  | assessor | |\n")
    assert rows[0]["also"] == ["đơn xin tài trợ", "submission"] and rows[1]["meaning"] == ""
    assert [r["term"] for r in glossary.find(rows, "Two submissions and one Đơn xin tài trợ")] == ["Grant application"]
    assert glossary.find(rows, "resubmission, reassessors") == []
    assert glossary.other_names_used(rows, 'The assessor opens it. Client said "submission".') == [("assessor", "Reviewer")]


def test_file_apply_adds_merges_and_never_overwrites_a_human():
    root, _ = fresh("comm-vault")
    out = _file(root, [{"term": "Reviewer", "also": ["assessor"], "n": 1}])
    assert '"Reviewer"' in out
    assert "| Reviewer |  | assessor | INT-003 #1 |" in read(root, G)
    # a human fills the meaning by hand; a later note brings a new name and a different meaning
    _write(root, G, read(root, G).replace("| Reviewer |  |", "| Reviewer | Staff member who decides an application |"))
    _file(root, [{"term": "panel member", "also": ["Assessor"], "meaning": "anyone on the panel"},
                 {"term": "Appeal", "meaning": "A request to re-decide a rejection"}])
    g = read(root, G)
    assert "| Reviewer | Staff member who decides an application | assessor; panel member | INT-003 #1 |" in g
    assert "| Appeal | A request to re-decide a rejection |  | INT-003 |" in g
    assert g.count("| Reviewer |") == 1
    before = read(root, G)
    _file(root, [{"term": "assessor"}])  # nothing new → the file is untouched
    assert read(root, G) == before
    lint_clean(root)


def test_worklists_carry_only_the_matching_terms():
    root, _ = fresh("comm-vault")
    code, out = run(root, "--json", "worklist", "file", "INT-003")
    assert code == 0 and "terms[]" in json.loads(out)["glossary"]["rule"], out  # the filer is always told how to propose
    code, out = run(root, "--json", "worklist", "route", "payments")
    assert code == 0 and "glossary" not in json.loads(out), out  # no glossary file → nothing added
    _glossary(root, "| Applicant | Person asking for a grant | grantee | Nam |", "| Wallet | Unused here | | Nam |",
              "| Assessor | Staff member who decides | reviewer | Nam |")
    code, out = run(root, "--json", "worklist", "route", "payments")
    g = json.loads(out).get("glossary")
    assert code == 0 and g and [t["term"] for t in g["terms"]] == ["Applicant"], out
    assert "terms[]" not in g["rule"]
    code, out = run(root, "--json", "worklist", "design", "grant-intake")  # matched through another name
    assert [t["term"] for t in json.loads(out)["glossary"]["terms"]] == ["Assessor"], out


def test_lint_flags_another_name_and_an_ambiguous_one_as_advisory():
    root, _ = fresh("comm-vault")
    _glossary(root, "| Assessor | Staff member who decides | reviewer | Nam |", "| Panel | | Reviewer | Nam |")
    code, out = run(root, "lint", "--full")
    assert code == 0, out  # advisory: listed, never blocking
    assert "glossary term not used" in out and "says 'reviewer' — the glossary term is 'Assessor'" in out
    assert "glossary name is ambiguous" in out and "listed under both 'Assessor' and 'Panel'" in out
