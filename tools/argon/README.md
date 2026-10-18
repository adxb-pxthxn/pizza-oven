# Argon orchestrator

Small, stdlib-only runner for Google Gemini. It is the way this repository
asks `gemini-4-argon` to do research, design reasoning, and drafting, and
asks a cheap model to summarise or format.

The script never reads an API key from a file and never prints one. Set
`GEMINI_API_KEY` in the environment (Cursor secrets, or a shell profile that
is not committed).

## Mac (Apple Silicon)

Python 3.10+ from python.org, Homebrew, or the Xcode CLT is enough. No
virtualenv and no pip packages.

```bash
export GEMINI_API_KEY="..."   # do not commit this
python3 tools/argon/argon.py ping
```

`ping` must print `ARGON_OK`.

## One call

```bash
python3 tools/argon/argon.py call \
  --model gemini-4-argon \
  --prompt-file research/argon-anatomy/prompts/geometry.md \
  --out research/argon-anatomy/argon/geometry.md
```

`gemini-4-argon` defaults to thinking level `HIGH`, the highest named
level. That is the setting for research, design reasoning, analysis, CAD
drafting, and report sections. The API accepts either a thinking level or
a thinking budget, not both. A budget is an integer from `-1` (dynamic) to
`65535` (the maximum). `65535` can consume the whole answer window, so the
default stays on `HIGH`, which still thinks hard and then writes the answer.

```bash
# Default: thinking level HIGH
python3 tools/argon/argon.py call --prompt-file brief.md --out out.md

# Explicit maximum budget instead of the level
python3 tools/argon/argon.py call --thinking-budget 65535 --prompt-file brief.md --out out.md

# Grunt call on the reasoning model
python3 tools/argon/argon.py call --no-thinking --prompt-file format.md --out table.md
```

Use `--model gemini-2.5-flash-lite` for grunt work (summaries, formatting).
That model does not get a thinking config unless the job sets one.
Do not use the cheap model for the engineering argument.

A job may set `thinking_level`, `thinking_budget`, or `"thinking": false`.

## Managed Antigravity agent

Modelling rounds use `tools/argon/antigravity.py`. That script calls the
Interactions API agent `antigravity-preview-09-2026` with
`agent_config.model` set to `gemini-4-argon`. It does not call
`generateContent`.

The agent config accepts `type`, `model`, and `max_total_tokens`. The
endpoint rejects `thinking_level`, `generation_config`, and `effort`.
Passing `--thinking-level` still sends the field and surfaces the HTTP
error. It does not retry on a cheaper model.

```bash
python3 tools/argon/antigravity.py ping
python3 tools/argon/antigravity.py run \
  --prompt-file design/variants/prompts/06-antigravity-interference.md \
  --source cad/freecad/build_variant.py:/workspace/cad/freecad/build_variant.py \
  --text-out design/variants/antigravity/answer.md
```

`--json` sets Gemini JSON mode.

## Parallel workers

`jobs.json` is either a list or `{"jobs": [...]}`. Paths are relative to
`--root` (default `.`).

```json
{
  "jobs": [
    {
      "id": "geometry",
      "model": "gemini-4-argon",
      "prompt_file": "research/argon-anatomy/prompts/geometry.md",
      "out": "research/argon-anatomy/argon/geometry.md",
      "temperature": 0.3
    },
    {
      "id": "format-table",
      "model": "gemini-2.5-flash-lite",
      "prompt_file": "research/argon-anatomy/prompts/format.md",
      "out": "research/argon-anatomy/argon/table.md"
    }
  ]
}
```

```bash
python3 tools/argon/argon.py batch \
  --jobs research/argon-anatomy/prompts/jobs.json \
  --workers 4 \
  --summary research/argon-anatomy/argon/batch-summary.json
```

Each job may set `system`, `json`, `temperature`, `max_output_tokens`,
`timeout_s`, and `retries`. Failures are redacted and collected. The process
exits 1 if any job failed.

## Tests

```bash
python3 tools/argon/test_argon.py
```

The tests do not call the network. They check key redaction, job loading,
and that a missing key stops the run.
