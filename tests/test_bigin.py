"""Tests for bin/bigin. Run: python3 -m unittest discover tests"""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BIGIN = Path(__file__).resolve().parent.parent / "bin" / "bigin"


class VaultCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.vault = Path(self.tmp.name).resolve()
        self.run_ok("init")

    def tearDown(self):
        self.tmp.cleanup()

    def run_cmd(self, *args, stdin=None):
        return subprocess.run([sys.executable, str(BIGIN), *args], cwd=self.vault,
                              input=stdin, capture_output=True, text=True)

    def run_ok(self, *args):
        result = self.run_cmd(*args)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result.stdout

    def new(self, *args):
        """Create a file; return its path."""
        return self.vault / self.run_ok("new", *args).split(maxsplit=1)[1].strip()

    def edit(self, path, old, new):
        text = path.read_text()
        self.assertIn(old, text)
        path.write_text(text.replace(old, new))

    def add_signal(self, note, row):
        self.edit(note, "|---|------|--------|-------|---------|--------|----------|",
                  "|---|------|--------|-------|---------|--------|----------|\n" + row)

    def test_init_is_safe_to_repeat(self):
        (self.vault / "bigin.md").write_text("---\ntype: config\nclient: Acme\n---\n")
        self.run_ok("init")
        self.assertIn("Acme", (self.vault / "bigin.md").read_text())
        self.assertTrue((self.vault / "INDEX.md").exists())

    def test_new_gives_the_next_id(self):
        self.new("feature", "Slot Booking")
        first = self.new("uc", "Book a slot", "--feature", "slot-booking")
        second = self.new("uc", "Cancel a booking", "--feature", "slot-booking")
        self.assertEqual(first.name, "UC-001-book-a-slot.md")
        self.assertEqual(second.name, "UC-002-cancel-a-booking.md")
        self.assertIn("feature: slot-booking", first.read_text())
        self.assertNotIn("{{", first.read_text())

    def test_client_profile_is_created_by_name(self):
        profile = self.new("client", "Anna Trần")
        self.assertEqual(profile.relative_to(self.vault).as_posix(), "04-clients/anna-tran.md")
        self.assertIn("# Client view — Anna Trần", profile.read_text())
        self.assertNotIn("ERROR", self.run_ok("check"))

    def test_new_refuses_an_unknown_feature(self):
        self.assertEqual(self.run_cmd("new", "uc", "X", "--feature", "nope").returncode, 2)

    def test_story_lands_in_its_epic_folder(self):
        self.new("feature", "Slot Booking")
        epic = self.new("ep", "Members book online", "--feature", "slot-booking")
        story = self.new("us", "Book a free slot", "--epic", "EP-001")
        self.assertEqual(story.parent, epic.parent)
        self.assertIn("feature: slot-booking", story.read_text())

    def test_fresh_templates_pass_the_check(self):
        self.new("feature", "Slot Booking")
        self.new("int", "Kickoff call")
        self.new("uc", "Book a slot", "--feature", "slot-booking")
        self.new("br", "No double booking", "--feature", "slot-booking")
        self.new("entity", "Booking")
        self.new("ux", "Slot Booking", "--feature", "slot-booking")
        self.new("ep", "Members book online", "--feature", "slot-booking")
        self.new("us", "Book a free slot", "--epic", "EP-001")
        out = self.run_ok("check")
        self.assertNotIn("ERROR", out)

    def test_check_finds_broken_link_and_bad_status(self):
        self.new("feature", "Slot Booking")
        uc = self.new("uc", "Book a slot", "--feature", "slot-booking")
        self.edit(uc, "status: draft", "status: finished")
        self.edit(uc, "## Rules", "## Rules\nSee BR-009.")
        result = self.run_cmd("check")
        self.assertEqual(result.returncode, 1)
        self.assertIn("BR-009, which does not exist", result.stdout)
        self.assertIn("status 'finished'", result.stdout)

    def test_approve_needs_no_open_question(self):
        self.new("feature", "Slot Booking")
        self.new("int", "Kickoff call")
        uc = self.new("uc", "Book a slot", "--feature", "slot-booking")
        self.edit(uc, "sources: []", "sources: [INT-001]")
        self.edit(uc, "## Open questions", "## Open questions\n- [ ] Q: Can a member book twice a day? (owner: client)\n  A:")
        self.assertEqual(self.run_cmd("approve", "UC-001", "--by", "An").returncode, 1)
        self.assertIn("[client] Can a member book twice a day?", self.run_ok("questions"))
        self.edit(uc, "- [ ] Q:", "- [x] Q:")
        self.run_ok("approve", "UC-001", "--by", "An")
        text = uc.read_text()
        self.assertIn("status: approved", text)
        self.assertIn("approved_version: 1", text)
        self.assertIn("approved by An", text)
        self.run_ok("check")

    def test_answer_waits_until_it_is_applied(self):
        self.new("feature", "Slot Booking")
        uc = self.new("uc", "Book a slot", "--feature", "slot-booking")
        self.edit(uc, "sources: []", "sources: [INT-001]")
        self.new("int", "Kickoff")
        self.edit(uc, "## Open questions\n", "## Open questions\n\n- [ ] Q: Can a slot be shared? (owner: client)\n  A:\n")
        self.assertIn("client: 1 in UC-001", self.run_ok("status"))
        self.edit(uc, "  A:\n", "  A: No (Anna, 2026-01-05)\n")  # answered, box not ticked
        status = self.run_ok("status")
        self.assertIn("UC-001: 1 answer(s)", status)
        self.assertNotIn("approve", status)
        self.assertNotEqual(self.run_cmd("approve", "UC-001", "--by", "Nam").returncode, 0)
        self.edit(uc, "- [ ] Q: Can", "- [x] Q: Can")
        self.edit(uc, "2026-01-05)\n", "2026-01-05) (applied v2)\n")
        self.run_ok("approve", "UC-001", "--by", "Nam")

    def test_feature_question_holds_the_use_cases_it_names(self):
        feature = self.new("feature", "Slot Booking")
        uc = self.new("uc", "Book a slot", "--feature", "slot-booking")
        self.new("uc", "Cancel a booking", "--feature", "slot-booking")
        self.new("int", "Kickoff")
        self.edit(uc, "sources: []", "sources: [INT-001]")
        self.edit(feature, "## Open questions\n",
                  "## Open questions\n\n- [ ] Q: Which time zone do slots use? (owner: client) (ref: UC-001)\n  A:\n")
        blocked = self.run_cmd("approve", "UC-001", "--by", "Nam")
        self.assertNotEqual(blocked.returncode, 0)
        self.assertIn("in slot-booking", blocked.stderr)
        status = self.run_ok("status")
        self.assertNotIn("UC-001 Book a slot", status.split("approve")[1])
        self.assertIn("UC-002 Cancel a booking", status.split("approve")[1])
        self.assertIn("holds: UC-001", self.run_ok("questions", "--feature", "UC-001"))
        # one answer on the feature page frees the use case
        self.edit(feature, "(ref: UC-001)\n  A:\n", "(ref: UC-001)\n  A: UTC (Anna) (applied)\n")
        self.edit(feature, "- [ ] Q: Which", "- [x] Q: Which")
        self.run_ok("approve", "UC-001", "--by", "Nam")

    def test_proposal_to_confirm_warns_and_only_stops_stories(self):
        self.new("feature", "Slot Booking")
        self.new("int", "Kickoff")
        uc = self.new("uc", "Book a slot", "--feature", "slot-booking")
        self.edit(uc, "sources: []", "sources: [INT-001]")
        self.edit(uc, "## Open questions\n", "## Open questions\n\n- [ ] Q: We plan to let a member book "
                  "one slot a day, because the gym is small. Is that right? (owner: client) (confirm)\n  A:\n")
        status = json.loads(self.run_ok("status", "--json"))
        self.assertEqual(status["answer"], [])
        self.assertEqual(status["confirm"], ["client: 1 in UC-001"])
        self.assertEqual(status["approve"], ["UC-001 Book a slot"])
        self.assertIn("[client, confirm] We plan", self.run_ok("questions", "--kind", "confirm"))
        self.assertNotIn("We plan", self.run_ok("questions", "--kind", "ask"))
        # a person may approve the use case; the design may go on
        self.assertIn("not confirmed by the client yet", self.run_ok("approve", "UC-001", "--by", "Nam"))
        self.run_ok("check")
        status = json.loads(self.run_ok("status", "--json"))
        self.assertEqual(len(status["design"]), 1)
        self.assertEqual(status["stories"], [])
        ux = self.new("ux", "Slot Booking", "--feature", "slot-booking")
        self.edit(ux, "built_from: []", "built_from: [UC-001@1]")
        self.run_ok("approve", "UX-001", "--by", "Nam")
        # stories wait
        self.new("ep", "Members book online", "--feature", "slot-booking")
        story = self.new("us", "Book a free slot", "--epic", "EP-001")
        self.edit(story, "built_from: []", "built_from: [UC-001@1]")
        self.assertIn("has a proposal the client has not confirmed", self.run_cmd("check").stdout)
        self.assertNotEqual(self.run_cmd("approve", "US-001", "--by", "Nam").returncode, 0)
        # the client says yes: the stories are free
        self.edit(uc, "(confirm)\n  A:\n", "(confirm)\n  A: Yes (Anna, 2026-01-05) (applied)\n")
        self.run_ok("check")
        self.assertEqual(len(json.loads(self.run_ok("status", "--json"))["stories"]), 0)
        self.run_ok("approve", "US-001", "--by", "Nam")

    def test_build_pack_holds_approved_use_cases_and_goes_stale(self):
        self.new("feature", "Slot Booking")
        self.new("int", "Kickoff")
        uc = self.new("uc", "Book a slot", "--feature", "slot-booking")
        other = self.new("uc", "Cancel a booking", "--feature", "slot-booking")
        rule = self.new("br", "One slot a day", "--feature", "slot-booking")
        for f in (uc, other, rule):
            self.edit(f, "sources: []", "sources: [INT-001]")
        self.edit(uc, "rules: []", "rules: [BR-001]")
        self.edit(uc, "## Open questions\n", "- A1: A slot lasts one hour — why: the usual length (S1) (owner: client)\n\n"
                  "## Open questions\n\n- [ ] Q: We plan to allow one slot a day. Is that right? (owner: client) (confirm)\n  A:\n")
        self.assertNotEqual(self.run_cmd("pack", "slot-booking").returncode, 0)  # nothing approved yet
        self.run_ok("approve", "UC-001", "--by", "Nam")
        code = Path(self.tmp.name) / ".." / (Path(self.tmp.name).name + "-code")
        out = self.run_ok("pack", "slot-booking", "--to", str(code))
        self.assertIn("1 use case(s), 1 rule(s), 1 proposal(s) not confirmed, 1 assumption(s)", out)
        self.assertIn("left out: UC-002", out)
        pack = self.vault / "05-handoff" / "slot-booking"
        self.assertIn("UC-001 Book a slot", (pack / "use-cases.md").read_text())
        self.assertIn("a person has not approved this yet", (pack / "use-cases.md").read_text())
        self.assertNotIn("Cancel a booking", (pack / "use-cases.md").read_text())
        items = (pack / "open-items.md").read_text()
        self.assertIn("We plan to allow one slot a day", items)
        self.assertIn("UC-001 A1 [client]: A slot lasts one hour", items)
        self.assertIn("built_from: [UC-001@1, BR-001@1]", (pack / "README.md").read_text())
        self.assertTrue((code.resolve() / "slot-booking" / "brief.md").exists())
        import shutil
        shutil.rmtree(code.resolve())
        self.run_ok("check")
        self.edit(rule, "\nversion: 1", "\nversion: 2")
        self.assertIn("build pack slot-booking holds BR-001@1", self.run_ok("status"))

    def test_review_card_shows_only_what_a_person_must_read(self):
        self.new("feature", "Slot Booking")
        self.new("int", "Kickoff")
        uc = self.new("uc", "Book a slot", "--feature", "slot-booking")
        self.edit(uc, "sources: []", "sources: [INT-001]")
        self.edit(uc, "## Summary\n", "## Summary\n\nA member picks a free slot and books it.\n")
        self.edit(uc, "| S1 | | | |", "| S1 | Picks a slot | Shows it | INT-001 #1 |\n| S2 | Confirms | Books it | assumed A1 |")
        self.edit(uc, "## Open questions\n", "- A1: A slot lasts one hour — why: the usual length (S2) (owner: client)\n\n"
                  "## Open questions\n\n- [ ] Q: May a member book for a guest? (owner: client)\n"
                  "  Options: a) No (recommended) · b) Yes, one guest\n  A:\n")
        card = self.run_ok("card", "UC-001")
        self.assertIn("A member picks a free slot", card)
        self.assertIn("options: a) No (recommended)", card)
        self.assertIn("A1 [client] A slot lasts one hour", card)
        self.assertIn("Steps: 2, not shown here. 1 name a source note", card)
        self.assertIn("no source at all - read these: S2", card)
        self.assertNotIn("Picks a slot", card)
        self.assertIn("options: a) No", self.run_ok("questions"))
        self.assertIn("UC-001 Book a slot [use-case, v1, held] 1 question(s), 1 assumption(s)", self.run_ok("card", "slot-booking"))
        # the answer sits under the Options line
        self.edit(uc, "one guest\n  A:\n", "one guest\n  A: a (Nam, 2026-01-05) (applied v2)\n")
        self.edit(uc, "\nversion: 1", "\nversion: 2")
        self.edit(uc, "- v1 (", "- v2 (2026-01-05) — no guests\n- v1 (")
        self.run_ok("approve", "UC-001", "--by", "Nam")
        self.edit(uc, "\nversion: 2", "\nversion: 3")
        self.edit(uc, "status: approved", "status: draft")
        self.edit(uc, "- v2 (", "- v3 (2026-01-06) — slot length is now 30 minutes\n- v2 (")
        card = self.run_ok("card", "UC-001")
        self.assertIn("Changed since version 2", card)
        self.assertIn("slot length is now 30 minutes", card)
        self.assertNotIn("no guests", card)

    def test_same_question_in_two_files_is_reported(self):
        feature = self.new("feature", "Slot Booking")
        uc = self.new("uc", "Book a slot", "--feature", "slot-booking")
        q = "- [ ] Q: Can two students share one booked slot in the same room? (owner: client)\n  A:\n"
        self.edit(feature, "## Open questions\n", "## Open questions\n\n" + q)
        self.edit(uc, "## Open questions\n", "## Open questions\n\n" + q)
        self.assertIn("same question is also open in", self.run_cmd("check").stdout)
        self.edit(uc, "(owner: client)\n  A:\n", "(owner: client)\n  A: No (Anna) (applied v2)\n")
        self.edit(uc, "- [ ] Q:", "- [x] Q:")
        out = self.run_cmd("check").stdout
        self.assertIn("same question is already answered in UC-001", out)

    def test_source_file_is_copied_not_retyped(self):
        src = self.vault / "call.txt"
        src.write_text("Anna: see UC-999\n## Signals\n- [ ] Q: not ours\n")
        out = self.run_ok("new", "int", "Client call", "--file", str(src))
        note = self.vault / out.splitlines()[-1].split(maxsplit=1)[1]
        copy = self.vault / "00-inbox" / "files" / "INT-001-call.txt"
        self.assertEqual(copy.read_bytes(), src.read_bytes())
        self.assertIn("### SRC-1 · file · call.txt", note.read_text())
        src.write_text("second file\n")
        self.assertIn("SRC-2", self.run_ok("attach", "INT-001", str(src)))
        self.assertTrue((self.vault / "00-inbox" / "files" / "INT-001-call-2.txt").exists())
        self.run_ok("check")

    def test_quote_must_be_in_the_source(self):
        self.new("feature", "Slot Booking")
        note = self.new("int", "Pasted note")
        self.edit(note, "## Signals", "### SRC-1 · note · Anna\n\nWe need to book a slot, “fast”.\n\n## Signals")
        self.add_signal(note, '| 1 | requirement | Book a slot | SRC-1: "need to book ... fast" | slot-booking | new | |')
        self.assertNotIn("quote", self.run_ok("check"))
        self.add_signal(note, '| 2 | requirement | Pay online | SRC-1: "we want online payment" | slot-booking | new | |')
        self.assertIn("signal #2: its quote is not in the source", self.run_ok("check"))

    def test_assumptions_are_listed_and_too_many_questions_warn(self):
        self.new("feature", "Slot Booking")
        uc = self.new("uc", "Book a slot", "--feature", "slot-booking")
        self.edit(uc, "## Open questions\n", "- A1: A slot lasts 30 minutes — why: the old sheet uses 30 (S1) (owner: client)\n"
                  "- A2: Rejected — slots are per room (Anna, 2026-01-05)\n\n## Open questions\n")
        out = self.run_ok("assumptions", "--owner", "client")
        self.assertIn("A slot lasts 30 minutes", out)
        self.assertIn("1 assumption(s)", out)
        self.assertNotIn("open client questions", self.run_ok("check"))
        many = "".join(f"- [ ] Q: Decision number {i} about slots? (owner: client)\n  A:\n" for i in range(6))
        self.edit(uc, "## Open questions\n", "## Open questions\n\n" + many)
        self.assertIn("6 open client questions (at most 5)", self.run_ok("check"))

    def test_raw_text_is_not_checked(self):
        note = self.new("int", "Pasted note")
        self.edit(note, "## Signals", "### SRC-1 · note · Nam\n\nSee UX-012 and UC-777.\n- [ ] Q: copied from the mail\n\n## Signals")
        self.run_ok("check")
        self.assertIn("0 unsettled", self.run_ok("questions"))

    def test_change_after_approval_is_an_error(self):
        self.new("feature", "Slot Booking")
        uc = self.new("uc", "Book a slot", "--feature", "slot-booking")
        self.run_ok("approve", "UC-001", "--by", "An")
        self.edit(uc, "\nversion: 1", "\nversion: 2")
        result = self.run_cmd("check")
        self.assertEqual(result.returncode, 1)
        self.assertIn("changed after approval", result.stdout)

    def test_status_follows_the_workflow(self):
        self.new("feature", "Slot Booking")
        note = self.new("int", "Kickoff call")
        self.assertIn("INT-001 Kickoff call", self.run_ok("status"))
        self.edit(note, "status: raw", "status: extracted")
        self.add_signal(note, '| 1 | requirement | Members book a free slot | SRC-1: "book online" | slot-booking | new | |')
        self.assertIn("slot-booking: 1 from INT-001", self.run_ok("status"))
        uc = self.new("uc", "Book a slot", "--feature", "slot-booking")
        self.edit(uc, "sources: []", "sources: [INT-001]")
        self.edit(note, "| new | |", "| drafted | UC-001 S1 |")
        status = json.loads(self.run_ok("status", "--json"))
        self.assertEqual(status["draft"], [])
        self.assertEqual(status["approve"], ["UC-001 Book a slot"])
        self.run_ok("approve", "UC-001", "--by", "An")
        status = json.loads(self.run_ok("status", "--json"))
        self.assertEqual(len(status["design"]), 1)
        self.assertEqual(len(status["stories"]), 1)

    def test_stale_design_is_reported(self):
        self.new("feature", "Slot Booking")
        uc = self.new("uc", "Book a slot", "--feature", "slot-booking")
        ux = self.new("ux", "Slot Booking", "--feature", "slot-booking")
        self.edit(ux, "built_from: []", "built_from: [UC-001@1]")
        self.assertNotIn("stale", self.run_ok("check"))
        self.edit(uc, "\nversion: 1", "\nversion: 2")
        self.assertIn("stale: built from UC-001@1", self.run_ok("check"))
        self.assertIn("UX-001 was built from UC-001@1", self.run_ok("status"))

    def test_signal_rows_are_checked(self):
        self.new("feature", "Slot Booking")
        note = self.new("int", "Kickoff call")
        self.add_signal(note, '| 1 | wish | Something | SRC-1: "x" | slot-booking | drafted | |')
        out = self.run_cmd("check").stdout
        self.assertIn("type 'wish' is not valid", out)
        self.assertIn("'Lands in' names no UC or BR", out)

    def test_trace_shows_both_directions(self):
        self.new("feature", "Slot Booking")
        self.new("int", "Kickoff call")
        uc = self.new("uc", "Book a slot", "--feature", "slot-booking")
        self.edit(uc, "sources: []", "sources: [INT-001]")
        self.assertRegex(self.run_ok("trace", "UC-001"), r"Uses \(mentions\):\n\s+INT-001")
        self.assertRegex(self.run_ok("trace", "INT-001"), r"Used by \(mentioned in\):\n\s+UC-001")
        self.assertIn("UC-001", self.run_ok("trace", "slot-booking"))

    def hook(self, path):
        payload = json.dumps({"tool_input": {"file_path": str(path)}, "cwd": str(self.vault)})
        return self.run_cmd("hook", stdin=payload)

    def test_hook_blocks_a_bad_write_and_refreshes_the_index(self):
        self.new("feature", "Slot Booking")
        uc = self.new("uc", "Book a slot", "--feature", "slot-booking")
        good = self.hook(uc)
        self.assertEqual((good.returncode, good.stdout), (0, ""))
        self.edit(uc, "title: Book a slot", "title: Reserve a slot")
        self.edit(uc, "status: draft", "status: approved")
        bad = self.hook(uc)
        self.assertEqual(bad.returncode, 0)
        self.assertEqual(json.loads(bad.stdout)["decision"], "block")
        self.assertIn("Reserve a slot", (self.vault / "INDEX.md").read_text())

    def test_hook_finds_a_vault_inside_the_project_folder(self):
        with tempfile.TemporaryDirectory() as project:
            vault = Path(project).resolve() / "brain"
            subprocess.run([sys.executable, str(BIGIN), "init", str(vault)], check=True, capture_output=True)
            note = vault / "00-inbox" / "INT-001-call.md"
            note.write_text("---\nid: INT-001\ntype: intake\ntitle: Call\nstatus: nonsense\n---\n\n## Raw\n\n## Signals\n")
            result = subprocess.run([sys.executable, str(BIGIN), "hook"], cwd=project, capture_output=True, text=True,
                                    input=json.dumps({"tool_input": {"file_path": str(note)}, "cwd": project}))
            self.assertEqual(json.loads(result.stdout)["decision"], "block")

    def test_hook_is_silent_outside_the_vault(self):
        with tempfile.TemporaryDirectory() as other:
            target = Path(other) / "notes.md"
            target.write_text("status: nonsense")
            result = subprocess.run([sys.executable, str(BIGIN), "hook"], cwd=other, capture_output=True, text=True,
                                    input=json.dumps({"tool_input": {"file_path": str(target)}, "cwd": other}))
            self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "", ""))


class TemplateCase(unittest.TestCase):
    def test_skills_point_at_real_files(self):
        root = BIGIN.parent.parent
        for skill in root.glob("skills/*/SKILL.md"):
            text = skill.read_text()
            self.assertTrue(text.startswith("---\nname: " + skill.parent.name + "\n"), skill)
            self.assertLess(len(text.splitlines()), 120, skill)
            for link in re.findall(r"\]\(([\w.-]+\.md)\)", text):
                self.assertTrue((skill.parent / link).exists(), f"{skill}: {link}")
            for ref in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([\w./-]+)", text):
                self.assertTrue((root / ref).exists(), f"{skill}: {ref}")


if __name__ == "__main__":
    unittest.main()
