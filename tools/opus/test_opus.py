#!/usr/bin/env python3
"""Offline tests for the Opus harness. No network and no real key."""

from __future__ import annotations

import ast
import json
import os
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import budget  # noqa: E402
import cadtools  # noqa: E402
import opus  # noqa: E402
import sandbox  # noqa: E402
import tasks  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
TASKS = Path(__file__).resolve().parent / "tasks"


def _png(width: int, height: int) -> bytes:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = b"".join(b"\x00" + (b"\x7f" * 3 * width) for _ in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )


class PriceTests(unittest.TestCase):
    def test_buckets_are_priced_once(self) -> None:
        prices = budget.Prices(4, 20, 5, 8, 0.2)
        usage = budget.parse_usage(
            {
                "input_tokens": 1000,
                "output_tokens": 500,
                "cache_creation_input_tokens": 2000,
                "cache_creation": {"ephemeral_5m_input_tokens": 1500, "ephemeral_1h_input_tokens": 500},
                "cache_read_input_tokens": 3000,
            }
        )
        self.assertEqual(usage["cache_write_5m_tokens"], 1500)
        self.assertEqual(usage["cache_write_1h_tokens"], 500)
        cost = prices.cost(**usage)
        expected = (1000 * 4 + 500 * 20 + 1500 * 5 + 500 * 8 + 3000 * 0.2) / 1_000_000
        self.assertAlmostEqual(cost, expected)

    def test_missing_split_is_a_five_minute_write(self) -> None:
        usage = budget.parse_usage(
            {"input_tokens": 10, "output_tokens": 5, "cache_creation_input_tokens": 2000, "cache_read_input_tokens": 0}
        )
        self.assertEqual(usage["cache_write_5m_tokens"], 2000)
        self.assertEqual(usage["cache_write_1h_tokens"], 0)

    def test_ledger_stops_on_a_corrupt_line_and_accumulates(self) -> None:
        prices = budget.load_prices()
        self.assertEqual(prices.input, 4.0)
        self.assertEqual(prices.output, 20.0)
        self.assertEqual(prices.cache_read, 0.2)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            ledger = budget.Ledger(path, 21)
            first = ledger.charge({"cost_usd": 0.25, "task": "a"})
            self.assertAlmostEqual(first["spent_usd"], 0.25)
            self.assertAlmostEqual(first["remaining_usd"], 20.75)
            second = ledger.charge({"cost_usd": 0.5, "task": "b"})
            self.assertAlmostEqual(second["spent_usd"], 0.75)
            path.write_text(path.read_text(encoding="utf-8") + "{not json}\n", encoding="utf-8")
            with self.assertRaises(budget.BudgetError):
                ledger.spent()

    def test_probe_refuses_above_five_cents(self) -> None:
        prices = budget.load_prices()
        self.assertLess(opus.probe_cost_usd(prices, 16), 0.05)
        self.assertGreater(opus.probe_cost_usd(prices, 100_000), 0.05)


class ModelAndRequestTests(unittest.TestCase):
    def test_exact_opus_55_wins_over_dated_and_other_opus(self) -> None:
        chosen = opus.select_opus_55(
            [
                {"id": "claude-opus-5"},
                {"id": "claude-opus-4-5"},
                {"id": "claude-sonnet-5-5"},
                {"id": "claude-opus-5-5-20260922"},
                {"id": "claude-opus-5-5"},
            ]
        )
        self.assertEqual(chosen, "claude-opus-5-5")

    def test_latest_dated_snapshot_when_the_bare_id_is_absent(self) -> None:
        chosen = opus.select_opus_55(
            [{"id": "claude-opus-5-5-20260801"}, {"id": "claude-opus-5-5-20260922"}]
        )
        self.assertEqual(chosen, "claude-opus-5-5-20260922")

    def test_missing_opus_55_names_the_opus_ids(self) -> None:
        with self.assertRaises(RuntimeError) as caught:
            opus.select_opus_55([{"id": "claude-opus-5"}, {"id": "claude-haiku-5-5"}])
        self.assertIn("claude-opus-5", str(caught.exception))
        self.assertNotIn("haiku", str(caught.exception))

    def test_model_list_follows_has_more(self) -> None:
        def transport(method, url, body, timeout, key):
            self.assertEqual(method, "GET")
            self.assertNotIn(key, url)
            if "after_id" not in url:
                return 200, json.dumps(
                    {"data": [{"id": "claude-opus-5"}], "has_more": True, "last_id": "claude-opus-5"}
                )
            return 200, json.dumps({"data": [{"id": "claude-opus-5-5"}], "has_more": False})

        models = opus.list_models(transport, "test-key")
        self.assertEqual(opus.select_opus_55(models), "claude-opus-5-5")

    def test_request_caches_system_and_tools_and_does_not_force_a_tool(self) -> None:
        body = opus.build_request(
            model="claude-opus-5-5",
            messages=[{"role": "user", "content": "measure the oven"}],
            max_tokens=8000,
            effort="medium",
            ttl="5m",
        )
        self.assertEqual(body["cache_control"], {"type": "ephemeral"})
        self.assertEqual(body["system"][0]["cache_control"], {"type": "ephemeral"})
        self.assertNotIn("cache_control", body["tools"][0])
        self.assertEqual(body["tools"][-1]["cache_control"], {"type": "ephemeral"})
        self.assertNotIn("tool_choice", body)
        self.assertNotIn("temperature", body)
        self.assertNotIn("thinking", body)
        self.assertEqual(body["output_config"], {"effort": "medium"})
        self.assertNotIn("ANTHROPIC", opus.SYSTEM_PROMPT)

    def test_retries_stop_on_400_and_repeat_on_429(self) -> None:
        secret = "sk-ant-test-key-do-not-leak"

        def bad(method, url, body, timeout, key):
            return 400, f"invalid {secret}"

        with self.assertRaises(RuntimeError) as caught:
            opus.post_message(bad, {}, secret, 5, 3, lambda _s: None)
        self.assertNotIn(secret, str(caught.exception))
        self.assertIn("[REDACTED]", str(caught.exception))

        calls = {"n": 0}

        def flaky(method, url, body, timeout, key):
            calls["n"] += 1
            if calls["n"] == 1:
                return 429, "slow down"
            return 200, json.dumps({"content": [], "usage": {"input_tokens": 1, "output_tokens": 1}})

        delays = []
        payload = opus.post_message(flaky, {}, secret, 5, 3, delays.append)
        self.assertEqual(calls["n"], 2)
        self.assertEqual(delays, [1.0])
        self.assertEqual(payload["usage"]["output_tokens"], 1)

    def test_missing_key_fails_before_a_request(self) -> None:
        old = os.environ.pop("ANTHROPIC_API_KEY", None)
        try:
            with self.assertRaises(RuntimeError) as caught:
                opus.api_key()
            self.assertIn("ANTHROPIC_API_KEY", str(caught.exception))
        finally:
            if old is not None:
                os.environ["ANTHROPIC_API_KEY"] = old


class SandboxTests(unittest.TestCase):
    def test_bash_strips_the_key_and_rejects_escapes(self) -> None:
        secret = "sk-ant-sandbox-secret"
        old = os.environ.get("ANTHROPIC_API_KEY")
        os.environ["ANTHROPIC_API_KEY"] = secret
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                clean = sandbox.run_bash(
                    root,
                    'python3 -c "import os; print(\'clean\' if \'sk-ant-sandbox-secret\' not in str(list(os.environ.values())) else \'LEAK\')"',
                )
                self.assertTrue(clean["ok"], clean)
                self.assertIn("clean", clean["output"])
                self.assertNotIn(secret, clean["output"])
                for command in ("printenv", "cat /etc/passwd", "ls ../", "echo tools/opus"):
                    blocked = sandbox.run_bash(root, command)
                    self.assertFalse(blocked["ok"], command)
                    self.assertIn("jail", blocked["error"])
                written = sandbox.write_file(root, "design/note.txt", "hello")
                self.assertTrue(written["ok"])
                refused = sandbox.write_file(root, "tools/opus/ledger.jsonl", "0")
                self.assertFalse(refused["ok"])
                escaped = sandbox.read_file(root, "../etc/passwd")
                self.assertFalse(escaped["ok"])
        finally:
            if old is None:
                os.environ.pop("ANTHROPIC_API_KEY", None)
            else:
                os.environ["ANTHROPIC_API_KEY"] = old


class TaskAndGateTests(unittest.TestCase):
    def test_three_starter_tasks_have_a_goal_a_gate_and_a_cap(self) -> None:
        loaded = [tasks.load_task(path) for path in sorted(TASKS.glob("*.yaml"))]
        self.assertEqual([item["id"] for item in loaded], ["build-doc", "mass-under-20kg", "render-textured"])
        for item in loaded:
            self.assertTrue(item["goal"].strip())
            self.assertIsInstance(item["acceptance"], dict)
            self.assertGreater(item["max_budget_usd"], 0)
            self.assertLessEqual(item["max_budget_usd"], 21)

    def test_png_and_manifest_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            spec = tasks.load_task(TASKS / "render-textured.yaml")
            png = root / "design" / "renders" / "morning-jarrah.png"
            png.parent.mkdir(parents=True)
            png.write_bytes(_png(1280, 720))
            # The synthetic PNG is small. Lower the byte floor for this fixture.
            spec["acceptance"]["png"]["min_bytes"] = 32
            manifest = {
                "variant": "morning",
                "finish": "jarrah",
                "backdrop": "light",
                "hdri": "design/renders/textures/studio.hdr",
                "texture_maps": {"albedo": "design/renders/textures/jarrah.jpg"},
            }
            (root / "design" / "renders" / "morning-jarrah.json").write_text(json.dumps(manifest), encoding="utf-8")
            (root / "design" / "renders" / "textures").mkdir()
            (root / "design" / "renders" / "textures" / "studio.hdr").write_bytes(b"hdr")
            (root / "design" / "renders" / "textures" / "jarrah.jpg").write_bytes(b"jpg")
            receipts = cadtools.Receipts()
            failed = cadtools.check(spec, root, receipts)
            self.assertFalse(failed["ok"])
            self.assertTrue(any("receipt" in item for item in failed["failures"]))
            receipts.add(
                "cad_render",
                {
                    "ok": True,
                    "kind": "blender",
                    "variant": "morning",
                    "finish": "jarrah",
                    "output": "design/renders/morning-jarrah.png",
                },
            )
            passed = cadtools.check(spec, root, receipts)
            self.assertTrue(passed["ok"], passed["failures"])
            self.assertEqual(cadtools.png_size(png), (1280, 720))

    def test_mass_gate_uses_masslib_numbers(self) -> None:
        sys.path.insert(0, str(REPO))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            variant_dir = root / "design" / "variants"
            variant_dir.mkdir(parents=True)
            (variant_dir / "optimizer.json").write_text(
                (REPO / "design" / "variants" / "optimizer.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            for name in ("morning", "moondancer"):
                source = REPO / "design" / "variants" / name / "freecad-mass.json"
                dest = variant_dir / name
                dest.mkdir()
                (dest / "freecad-mass.json").write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            receipts = cadtools.Receipts()
            measured = cadtools.cad_mass(root, "moondancer", "evaluate", receipts)
            self.assertTrue(measured["ok"])
            self.assertLessEqual(measured["ready_kg"], 20)
            record = {
                "variant": "moondancer",
                "parameter": "skin_t",
                "decision": "kept",
                "ready_kg": measured["ready_kg"],
            }
            (variant_dir / "opus-mass-iteration.json").write_text(json.dumps(record), encoding="utf-8")
            receipts.add("cad_interference", {"variant": "moondancer", "available": False, "ok": False})
            spec = tasks.load_task(TASKS / "mass-under-20kg.yaml")
            spec["acceptance"].pop("unittest", None)
            result = cadtools.check(spec, root, receipts)
            self.assertTrue(result["ok"], result["failures"])

    def test_interference_script_parses_and_missing_freecad_is_honest(self) -> None:
        ast.parse(cadtools._interference_code(Path("/tmp/oven.FCStd"), "moondancer"))
        receipts = cadtools.Receipts()
        result = cadtools.cad_interference(REPO, "moondancer", receipts)
        if cadtools.freecad_available():
            self.assertIn("report", result)
        else:
            self.assertFalse(result["available"])
            self.assertIn("freecadcmd", result["error"])
            self.assertNotIn("overlap_mm3", json.dumps(result.get("report")))

    def test_build_doc_gate(self) -> None:
        sys.path.insert(0, str(REPO))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            variants = root / "design" / "variants"
            variants.mkdir(parents=True)
            (variants / "optimizer.json").write_text(
                (REPO / "design" / "variants" / "optimizer.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            receipts = cadtools.Receipts()
            measured = cadtools.cad_mass(root, "moondancer", "evaluate", receipts)
            mass_text = f"{measured['ready_kg']:.2f}"
            (variants / "BUILD.md").write_text(
                f"# Build\n\n## Tools\n\n## Sequence\n\n## Safety\n\n## Materials\n\nReady {mass_text} kg. Stone 420 mm.\n",
                encoding="utf-8",
            )
            templates = variants / "templates"
            templates.mkdir()
            (templates / "peel-landing.svg").write_text(
                '<svg xmlns="http://www.w3.org/2000/svg"><!-- CUT outline for the 420 mm stone, peel landing blank. '
                + ("sheet " * 40)
                + '--><g id="CUT"><path d="M0 0 L420 0 L420 40 L0 40 Z"/></g></svg>\n',
                encoding="utf-8",
            )
            spec = tasks.load_task(TASKS / "build-doc.yaml")
            result = cadtools.check(spec, root, receipts)
            self.assertTrue(result["ok"], result["failures"])


class LoopTests(unittest.TestCase):
    def _task(self) -> dict:
        task = tasks.load_task(TASKS / "render-textured.yaml")
        task["max_turns"] = 4
        return task

    def test_done_without_a_passing_check_is_not_verified(self) -> None:
        calls = {"n": 0}

        def transport(method, url, body, timeout, key):
            calls["n"] += 1
            if calls["n"] == 1:
                content = [
                    {"type": "tool_use", "id": "toolu_1", "name": "declare_done", "input": {"summary": "ship it"}}
                ]
                stop = "tool_use"
            else:
                content = [{"type": "text", "text": "stopping"}]
                stop = "end_turn"
            return 200, json.dumps(
                {
                    "stop_reason": stop,
                    "content": content,
                    "usage": {"input_tokens": 0, "output_tokens": 0},
                }
            )

        summary = opus.run_session(
            self._task(),
            transport=transport,
            key="sk-ant-test",
            ledger=None,
            prices=budget.load_prices(),
            model="claude-opus-5-5",
            effort="low",
            max_tokens=800,
            ttl="5m",
            timeout_s=5,
            attempts=1,
            sleep=lambda _s: None,
            root=REPO,
            task_cap=5,
            echo=lambda _text: None,
        )
        self.assertTrue(summary["done"])
        self.assertFalse(summary["verified"])
        self.assertEqual(summary["status"], "done_unverified")
        self.assertGreaterEqual(calls["n"], 2)

    def test_verified_requires_the_gate_and_keeps_thinking_blocks(self) -> None:
        seen = {}

        def transport(method, url, body, timeout, key):
            if "first" not in seen:
                seen["first"] = body
                content = [
                    {"type": "thinking", "thinking": "", "signature": "sig-keep"},
                    {"type": "tool_use", "id": "toolu_b", "name": "bash", "input": {"command": "echo hi"}},
                ]
                return 200, json.dumps(
                    {"stop_reason": "tool_use", "content": content, "usage": {"input_tokens": 3, "output_tokens": 4}}
                )
            seen["second"] = body
            return 200, json.dumps(
                {
                    "stop_reason": "tool_use",
                    "content": [
                        {"type": "tool_use", "id": "toolu_d", "name": "declare_done", "input": {"summary": "measured"}}
                    ],
                    "usage": {"input_tokens": 3, "output_tokens": 4},
                }
            )

        original = opus.check

        def passing(task, root, receipts):
            return {"ok": True, "failures": [], "measured": {}}

        opus.check = passing
        try:
            with tempfile.TemporaryDirectory() as tmp:
                summary = opus.run_session(
                    self._task(),
                    transport=transport,
                    key="sk-ant-test",
                    ledger=None,
                    prices=budget.load_prices(),
                    model="claude-opus-5-5",
                    effort="medium",
                    max_tokens=800,
                    ttl="5m",
                    timeout_s=5,
                    attempts=1,
                    sleep=lambda _s: None,
                    root=Path(tmp),
                    task_cap=5,
                    echo=lambda _text: None,
                )
        finally:
            opus.check = original
        self.assertTrue(summary["done"])
        self.assertTrue(summary["verified"])
        assistant = seen["second"]["messages"][1]
        self.assertEqual(assistant["content"][0]["signature"], "sig-keep")
        self.assertEqual(assistant["content"][0]["thinking"], "")

    def test_task_cap_stops_after_the_response_that_crosses_it(self) -> None:
        calls = {"n": 0}

        def transport(method, url, body, timeout, key):
            calls["n"] += 1
            return 200, json.dumps(
                {
                    "stop_reason": "end_turn",
                    "content": [{"type": "text", "text": "still going"}],
                    "usage": {"input_tokens": 0, "output_tokens": 1000},
                }
            )

        with tempfile.TemporaryDirectory() as tmp:
            ledger = budget.Ledger(Path(tmp) / "ledger.jsonl", 21)
            lines = []
            summary = opus.run_session(
                self._task(),
                transport=transport,
                key="sk-ant-test",
                ledger=ledger,
                prices=budget.Prices(4, 20, 5, 8, 0.2),
                model="claude-opus-5-5",
                effort="low",
                max_tokens=800,
                ttl="5m",
                timeout_s=5,
                attempts=1,
                sleep=lambda _s: None,
                root=REPO,
                task_cap=0.01,
                echo=lines.append,
            )
        self.assertEqual(calls["n"], 1)
        self.assertEqual(summary["status"], "budget_stop")
        self.assertFalse(summary["verified"])
        self.assertTrue(any("remaining" in line for line in lines))
        self.assertNotIn("sk-ant-test", "\n".join(lines))

    def test_dry_run_makes_no_model_request(self) -> None:
        task = tasks.load_task(TASKS / "render-textured.yaml")
        code = opus.cmd_dry_run(task, budget.load_prices(), "medium", 8000, "5m")
        self.assertEqual(code, 0)

    def test_old_tool_results_shrink_and_thinking_does_not(self) -> None:
        messages = [
            {"role": "assistant", "content": [{"type": "thinking", "thinking": "", "signature": "sig"}]},
            {
                "role": "user",
                "content": [
                    {"type": "tool_result", "tool_use_id": "a", "content": "x" * 5000},
                    {"type": "tool_result", "tool_use_id": "b", "content": "y" * 5000},
                    {"type": "tool_result", "tool_use_id": "c", "content": "keep-me"},
                ],
            },
        ]
        opus.compact_messages(messages, max_chars=1000, keep_recent=1)
        self.assertEqual(messages[0]["content"][0]["signature"], "sig")
        self.assertIn("summarised", messages[1]["content"][0]["content"])
        self.assertEqual(messages[1]["content"][2]["content"], "keep-me")


if __name__ == "__main__":
    unittest.main()
