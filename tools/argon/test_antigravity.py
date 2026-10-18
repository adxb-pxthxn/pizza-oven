#!/usr/bin/env python3
"""Offline tests for the Antigravity wrapper. No network and no real key."""

from __future__ import annotations

import base64
import json
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import antigravity  # noqa: E402


class RedactAndConfigTests(unittest.TestCase):
    def test_redacts_the_key(self) -> None:
        secret = "AIzaSY-TEST-KEY-DO-NOT-LEAK"
        cleaned = antigravity.redact(f"header {secret} failed", secret)
        self.assertNotIn(secret, cleaned)
        self.assertIn("[REDACTED]", cleaned)

    def test_missing_key_raises_before_a_request(self) -> None:
        old = os.environ.pop("GEMINI_API_KEY", None)
        try:
            with self.assertRaises(antigravity.AntigravityError) as caught:
                antigravity.api_key()
            self.assertIn("GEMINI_API_KEY", str(caught.exception))
        finally:
            if old is not None:
                os.environ["GEMINI_API_KEY"] = old

    def test_default_config_is_the_highest_accepted_model(self) -> None:
        config = antigravity.agent_config()
        self.assertEqual(config, {"type": "antigravity", "model": "gemini-4-argon"})
        self.assertNotIn("thinking_level", config)

    def test_thinking_level_is_sent_when_asked_and_not_stripped(self) -> None:
        config = antigravity.agent_config(thinking_level="high", effort="high", max_total_tokens=1000)
        self.assertEqual(config["thinking_level"], "high")
        self.assertEqual(config["effort"], "high")
        self.assertEqual(config["max_total_tokens"], 1000)
        self.assertEqual(config["model"], "gemini-4-argon")

    def test_body_uses_the_managed_agent(self) -> None:
        body = antigravity.build_body("fix the oven", sources=[{"type": "inline", "target": "/workspace/a.py", "content": "x"}])
        self.assertEqual(body["agent"], "antigravity-preview-09-2026")
        self.assertEqual(body["agent_config"]["model"], "gemini-4-argon")
        self.assertTrue(body["background"])
        self.assertTrue(body["store"])
        self.assertEqual(body["environment"]["sources"][0]["target"], "/workspace/a.py")
        self.assertNotIn("model", body)


class HttpTests(unittest.TestCase):
    def setUp(self) -> None:
        self.old = os.environ.get("GEMINI_API_KEY")
        os.environ["GEMINI_API_KEY"] = "AIzaSY-TEST-KEY-DO-NOT-LEAK"

    def tearDown(self) -> None:
        if self.old is None:
            os.environ.pop("GEMINI_API_KEY", None)
        else:
            os.environ["GEMINI_API_KEY"] = self.old

    def test_http_400_is_raised_with_the_body_and_not_retried(self) -> None:
        calls = {"n": 0}

        def transport(method, url, body, timeout, key):
            calls["n"] += 1
            self.assertEqual(method, "POST")
            self.assertIn("interactions", url)
            self.assertEqual(body["agent_config"]["thinking_level"], "high")
            raise antigravity.AntigravityError(
                "HTTP 400: {\"error\":{\"message\":\"Unknown parameter 'thinking_level' at 'agent_config'.\",\"code\":\"invalid_request\"}}"
            )

        with self.assertRaises(antigravity.AntigravityError) as caught:
            antigravity.create("ping", thinking_level="high", transport=transport)
        self.assertIn("Unknown parameter 'thinking_level' at 'agent_config'", str(caught.exception))
        self.assertNotIn("AIzaSY-TEST-KEY-DO-NOT-LEAK", str(caught.exception))
        self.assertEqual(calls["n"], 1)

    def test_poll_stops_when_completed(self) -> None:
        seen = {"n": 0}

        def transport(method, url, body, timeout, key):
            seen["n"] += 1
            self.assertEqual(method, "GET")
            if seen["n"] == 1:
                payload = {"id": "abc", "status": "in_progress", "steps": []}
            else:
                payload = {
                    "id": "abc",
                    "status": "completed",
                    "agent": "antigravity-preview-09-2026",
                    "environment_id": "env",
                    "steps": [{"type": "model_output", "content": [{"type": "text", "text": "done"}]}],
                    "usage": {"total_tokens": 3, "total_thought_tokens": 1},
                }
            return 200, json.dumps(payload)

        finished = antigravity.poll("abc", timeout_s=5, interval_s=0, transport=transport)
        self.assertEqual(finished["status"], "completed")
        self.assertEqual(antigravity.output_text(finished), "done")
        self.assertEqual(seen["n"], 2)


class FileMarkerTests(unittest.TestCase):
    def test_extracts_text_and_base64_files(self) -> None:
        encoded = base64.b64encode(b"png-bytes").decode("ascii")
        text = (
            "report\n"
            "===== FILE cad/freecad/build_variant.py =====\n"
            "print('oven')\n"
            "===== END FILE =====\n"
            "===== B64 design/variants/morning/front.png =====\n"
            f"{encoded}\n"
            "===== END B64 =====\n"
        )
        files = dict(antigravity.extract_files(text))
        self.assertEqual(files["cad/freecad/build_variant.py"], b"print('oven')")
        self.assertEqual(files["design/variants/morning/front.png"], b"png-bytes")

    def test_later_copy_wins_and_a_truncated_block_is_skipped(self) -> None:
        encoded = base64.b64encode(b"png-bytes").decode("ascii")
        text = (
            "===== B64 design/variants/morning/top.png =====\n"
            "AAAA\u2014not-closed\n"
            "===== FILE cad/freecad/build_variant.py =====\n"
            "first\n"
            "===== END FILE =====\n"
            "===== END B64 =====\n"
            "===== FILE cad/freecad/build_variant.py =====\n"
            "second\n"
            "===== END FILE =====\n"
            "===== B64 design/variants/morning/top.png =====\n"
            f"{encoded}\n"
            "===== END B64 =====\n"
        )
        files = dict(antigravity.extract_files(text))
        self.assertEqual(files["cad/freecad/build_variant.py"], b"second")
        self.assertEqual(files["design/variants/morning/top.png"], b"png-bytes")

    def test_refuses_parent_paths(self) -> None:
        with self.assertRaises(antigravity.AntigravityError):
            antigravity.write_files([("../secret", b"no")], Path("/tmp"))


if __name__ == "__main__":
    unittest.main()
