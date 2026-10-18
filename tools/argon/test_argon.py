#!/usr/bin/env python3
"""Offline tests for the Argon orchestrator. No network, no real key."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import argon  # noqa: E402


class RedactTests(unittest.TestCase):
    def test_redacts_key_and_does_not_keep_it_in_the_message(self) -> None:
        secret = "AIzaSY-TEST-KEY-DO-NOT-LEAK"
        raw = f"HTTP 403: request ?key={secret} failed for {secret}"
        cleaned = argon.redact(raw, secret)
        self.assertNotIn(secret, cleaned)
        self.assertIn("[REDACTED]", cleaned)

    def test_missing_key_raises_before_any_request(self) -> None:
        old = os.environ.pop("GEMINI_API_KEY", None)
        try:
            with self.assertRaises(argon.ArgonError) as caught:
                argon.api_key()
            self.assertIn("GEMINI_API_KEY", str(caught.exception))
        finally:
            if old is not None:
                os.environ["GEMINI_API_KEY"] = old

    def test_extract_text_skips_thought_parts(self) -> None:
        payload = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"thought": True, "text": "hidden"},
                            {"text": "visible"},
                        ]
                    }
                }
            ]
        }
        self.assertEqual(argon._extract_text(payload), "visible")

    def test_batch_loader_accepts_object_or_list(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            listed = root / "list.json"
            listed.write_text(json.dumps([{"id": "a", "prompt": "hi"}]), encoding="utf-8")
            wrapped = root / "wrap.json"
            wrapped.write_text(json.dumps({"jobs": [{"id": "b", "prompt": "yo"}]}), encoding="utf-8")
            self.assertEqual(argon._load_jobs(listed)[0]["id"], "a")
            self.assertEqual(argon._load_jobs(wrapped)[0]["id"], "b")

    def test_reasoning_model_defaults_to_high_thinking_level(self) -> None:
        config = argon.resolve_thinking("gemini-4-argon")
        self.assertEqual(config, {"thinkingLevel": "HIGH"})

    def test_cheap_model_defaults_to_no_thinking(self) -> None:
        self.assertIsNone(argon.resolve_thinking("gemini-2.5-flash-lite"))

    def test_no_thinking_flag_overrides_the_argon_default(self) -> None:
        self.assertIsNone(argon.resolve_thinking("gemini-4-argon", enabled=False))

    def test_budget_replaces_the_level_and_rejects_both(self) -> None:
        self.assertEqual(
            argon.resolve_thinking("gemini-4-argon", thinking_budget=65535),
            {"thinkingBudget": 65535},
        )
        with self.assertRaises(argon.ArgonError):
            argon.resolve_thinking("gemini-4-argon", thinking_level="HIGH", thinking_budget=1024)

    def test_budget_must_stay_inside_the_api_range(self) -> None:
        with self.assertRaises(argon.ArgonError):
            argon.resolve_thinking("gemini-4-argon", thinking_budget=65536)
        self.assertEqual(
            argon.resolve_thinking("gemini-2.5-flash-lite", thinking_level="low"),
            {"thinkingLevel": "LOW"},
        )

    def test_run_job_writes_output_without_network_when_generate_is_stubbed(self) -> None:
        original = argon.generate
        def _stub(*args, **kwargs):
            self.assertEqual(kwargs.get("thinking_level"), "HIGH")
            return {
                "text": "draft",
                "model": "stub",
                "usage": {"promptTokenCount": 3, "candidatesTokenCount": 1},
                "attempts": 1,
                "thinking": {"thinkingLevel": "HIGH"},
            }

        argon.generate = _stub  # type: ignore[assignment]
        try:
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                summary = argon.run_job(
                    {
                        "id": "one",
                        "prompt": "hello",
                        "out": "out/one.md",
                        "model": "gemini-4-argon",
                        "thinking_level": "HIGH",
                    },
                    root,
                )
                self.assertEqual((root / "out" / "one.md").read_text(encoding="utf-8"), "draft\n")
                self.assertEqual(summary["id"], "one")
                self.assertNotIn("key", json.dumps(summary).lower())
        finally:
            argon.generate = original  # type: ignore[assignment]


if __name__ == "__main__":
    raise SystemExit(unittest.main())
