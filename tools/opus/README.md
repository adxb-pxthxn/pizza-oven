# Opus harness

A small stdlib loop that asks Claude Opus 5.5 to do one CAD, render, or build-doc task in this repository, then measures the result itself. The key is `ANTHROPIC_API_KEY` in the environment. The script never reads a key from a file and never prints one.

The model id is not hardcoded. `ping`, `probe`, and `run` call `GET /v1/models` and take `claude-opus-5-5`, or the latest dated id that starts with that prefix. Anthropic's model page (22 September 2026) lists the Claude API id as `claude-opus-5-5`.

## Run

```bash
export ANTHROPIC_API_KEY="..."   # do not commit this
python3 tools/opus/opus.py estimate
python3 tools/opus/opus.py dry-run --task tools/opus/tasks/render-textured.yaml
python3 tools/opus/opus.py run --task tools/opus/tasks/render-textured.yaml
```

`dry-run` and `mock` make no network call. `mock` plays one `declare_done` and then stops, so you can see `done` and `verified` come apart. `probe` is the only command that sends a Messages request on purpose: at most 16 output tokens, effort `low`, and it refuses to send if the worst-case price is above $0.05.

```bash
python3 tools/opus/opus.py ping     # model id only
python3 tools/opus/opus.py probe    # model id plus one tiny usage sample
python3 tools/opus/opus.py ledger   # cumulative spend
```

Other flags: `--budget` (global cap, default 21), `--effort` (`low` through `max`, default `medium`), `--max-tokens` (default 8000), `--cache-ttl` (`5m` or `1h`).

Offline tests, no network:

```bash
python3 tools/opus/test_opus.py
```

## Budget

Prices are USD per million tokens in `pricing.json`, from the Claude API list on 7 October 2026:

| bucket | USD / MTok |
|---|---|
| input (tokens after the cache breakpoint) | 4 |
| output, including thinking | 20 |
| 5-minute cache write | 5 |
| 1-hour cache write | 8 |
| cache read | 0.20 |

`input_tokens`, cache writes, and cache reads are disjoint. A write with no 5-minute / 1-hour split is billed as a 5-minute write. Override a rate with `OPUS_PRICE_INPUT_PER_MTOK`, `OPUS_PRICE_OUTPUT_PER_MTOK`, `OPUS_PRICE_CACHE_WRITE_5M_PER_MTOK`, `OPUS_PRICE_CACHE_WRITE_1H_PER_MTOK`, or `OPUS_PRICE_CACHE_READ_PER_MTOK`. Override the global cap with `OPUS_BUDGET_USD`.

Each Messages response appends one line to `tools/opus/ledger.jsonl` (gitignored). The global cap is the sum of that file. The default is $21 of the roughly $22 on the account, so one in-flight response can still finish. A turn is not started once the cap is reached. Output is also bounded by `--max-tokens` (8000 tokens is $0.16 at the output rate). The task cap in the YAML applies to the current process only, and it is also limited by whatever global budget is left. A corrupt ledger line refuses further spending. The remaining budget is printed after every turn.

`estimate` prices the cached system prompt and tools (about 1500 tokens at a character/4 count), the task text, 1500 tokens of tool results, and an assumed 2000 output tokens per turn. It is a planning figure, not a quote. Current starter tasks:

| task | expected | cap | turns |
|---|---|---|---|
| `render-textured` | $0.40 | $5 | 8 expected, 14 max |
| `mass-under-20kg` | $0.30 | $6 | 6 expected, 12 max |
| `build-doc` | $0.25 | $4 | 5 expected, 10 max |

The three together are about $0.94 at that assumption. Re-run `estimate` after editing a prompt.

## Done and verified

`declare_done` sets **done**. **verified** becomes true only when `check()` passes. `check()` recomputes the acceptance block: PNG dimensions, manifest paths, a `cad_render` receipt from this process, `masslib.evaluate` against the same limits as `cad/tests/test_variants.py`, the FreeCAD mass file, the iteration record, and interference. A missing `freecadcmd` is recorded by `cad_interference` and is not turned into a fake overlap. The variant unittest runs when scipy imports; without scipy the analytical gate still runs. A text-only reply is not success. The loop sends at most two continuations, stops at 25 turns or the task's own cap (whichever is smaller), and after 15 unverified turns tells the model to change construction. The same tool failure twice gets the same instruction. Thinking blocks are passed back unchanged. Tool output is truncated, and old tool results are summarised once the transcript exceeds 60k characters.

## System prompt

The prompt is short and stable so it can sit in the prompt cache with the tool definitions (Opus 5.5 caches from 512 tokens; this prefix is about 1500). It says the harness measures and the model does not, because unattended CAD runs report features that are not in the solid. It tells the model to rebuild from `cad/freecad/` rather than patch an FCStd, and to abandon a construction that fails twice, because repeated edits rot a FreeCAD document. It forbids a text-only stop while the gate is open, which is how Opus 5.5 ends a turn early. It names the food-contact and licence rules that already govern the repo. Nothing in it changes per turn: the task, the acceptance JSON, and the remaining budget are in the user message, so the cached prefix stays valid. Effort stays `medium` for the same reason a mid-run change would bust the cache, and because thinking cannot be turned off and is billed as output. `medium` is the model's default and, on Anthropic's agentic coding evals, matches Opus 5 at `high`. Raise `--effort` only after a task fails for lack of reasoning.

The request omits `temperature`, `top_p`, and `thinking` (adaptive thinking is always on; disabling it is a 400). `tool_choice` is left at `auto`. Opus 5.5 rejects `any` and `tool`.

## Tools

`bash`, `read_file`, and `write_file` stay inside the repository. The child environment drops credential variables. `bash` rejects `..`, environment dumps, and writes into `tools/opus`. The CAD tools shell out to the scripts that already exist:

- `cad_build` runs `cad/freecad/drive.py` (freecadcmd via `tools/freecad_mcp`)
- `cad_interference` loads the variant FCStd and reports pairwise common volume
- `cad_thermal` runs `cad/freecad/thermal_fea.py`
- `cad_mass` calls `cad/freecad/masslib.evaluate`, or `optimize.py` when asked
- `cad_render` reports the GA PNGs from the build, or runs `blender --background --python`

## Tasks

`tools/opus/tasks/*.yaml`. Each file has a goal, inputs, an acceptance block, and `max_budget_usd`.

- `render-textured.yaml` — Morning, jarrah finish, CC0 PBR maps, studio HDRI, light backdrop. Copy the file for gidgee, brushed-aluminium, or blued-steel.
- `mass-under-20kg.yaml` — one iteration that stays under 20 kg, measured by `masslib`.
- `build-doc.yaml` — `design/variants/BUILD.md` plus a CUT template.

Launch one of them with `run --task` as above.
