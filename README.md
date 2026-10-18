# Open-Source Pizza Oven Development

An open-source physical engineering and mechanical hardware workspace for developing a pizza oven under Open Source Hardware Association (OSHWA) standards.

---

## Project Status

The repository provides the complete open-source mechanical engineering foundation, skills suite, and cross-agent coordination tools. **No premature design assumptions have been imposed**—dimensions, fuel types (wood, gas, pellet, electric, charcoal), materials (sheet metal, refractory brick, castable refractory, stone), and construction methods will be developed based on explicit project requirements.

---

## Repository Structure

```
pizza-oven/
├── .agents/
│   ├── skills/                  # Installed engineering & workflow skills
│   │   ├── anatomy/             # Isometric technical figures & visual explainers
│   │   ├── code-cad/            # Parametric CAD modeling & export pipelines
│   │   ├── cross-agent-coordination/ # Multi-agent state machine & handover tools
│   │   ├── cursor-sync/         # Synchronization between Antigravity, Cursor, and Claude Code
│   │   ├── material-sourcing/   # Local classifieds, scrap, and vendor scraping
│   │   ├── mechanical-engineering/ # Sheet metal DFM, bend allowance, thermal expansion
│   │   ├── multi-agent-review/  # Maker/Critic dual-agent peer review harness
│   │   ├── oshwa-hardware/      # OSHWA compliance auditing & licensing
│   │   └── oven-thermodynamics/ # High-temperature physics & insulation sizing
│   └── state/
│       └── TASK_BOARD.md        # Cross-agent Kanban task board
├── .cursor/
│   └── rules/                   # Scoped Cursor IDE rules (.mdc)
├── bom/
│   └── bom.csv                  # Bill of Materials template
├── cad/
│   ├── parts/                   # Individual part models
│   ├── assemblies/              # Master assembly models
│   └── exports/                 # Manufacturing exports (STEP, DXF, STL)
├── docs/
│   └── HANDOVER.md              # Cross-agent session handover document
├── .cursorrules                 # Cursor root configuration
├── .gitignore                   # CAD and OS ignore rules
├── AGENTS.md / GEMINI.md        # Core engineering guidelines
├── CLAUDE.md                    # Claude Code link to AGENTS.md
├── LICENSE-HARDWARE             # CERN-OHL-P v2 (Permissive Open Hardware)
├── LICENSE-DOCS                 # CC-BY-4.0 International
├── OSHWA.md                     # Open Source Hardware Statement & Checklist
└── README.md                    # Project overview
```

---

## Installed Skills & Capabilities

This workspace includes specialized skills in `.agents/skills/`:

| Skill | Purpose & Capabilities | How to Use |
| :--- | :--- | :--- |
| **`anatomy`** | Isometric cutaways and interactive animated technical figures. | Upstream skill from [skills.wheresryan.sh/anatomy](https://skills.wheresryan.sh/anatomy) |
| **`mechanical-engineering`** | DFM for sheet metal, bend allowance calculations, differential thermal expansion, and food contact safety. | `python3 .agents/skills/mechanical-engineering/scripts/bend_allowance.py --help` |
| **`code-cad`** | Parametric CAD modeling rules, tab-and-slot joinery, and DXF/STEP/STL pipelines. | See `.agents/skills/code-cad/SKILL.md` |
| **`oven-thermodynamics`** | High-temp thermal modeling, heat loss through multi-layer insulation, and preheat dynamics. | `python3 .agents/skills/oven-thermodynamics/scripts/thermal_model.py --help` |
| **`material-sourcing`** | Search and scrape local vendors, classifieds (Gumtree, Facebook Marketplace, Google), and scrap yards for BOM materials. | `python3 .agents/skills/material-sourcing/scripts/cli.py --help` |
| **`oshwa-hardware`** | Open Source Hardware Association compliance auditor and release checklist. | `python3 .agents/skills/oshwa-hardware/scripts/validate_oshwa.py` |
| **`cross-agent-coordination`** | Multi-agent state machine, 10-second situational awareness briefing, and handover protocol. | `python3 .agents/skills/cross-agent-coordination/scripts/agent_handover.py --summary` |
| **`cursor-sync`** | Keeps Cursor `.cursor/rules/*.mdc` and Antigravity rules in lockstep. | `python3 .agents/skills/cursor-sync/scripts/sync_cursor.py --check` |
| **`multi-agent-review`** | Dual-agent "Maker / Critic" review harness. | `python3 .agents/skills/multi-agent-review/scripts/agent_review.py --maker <name>` |

---

## Licensing

- **Hardware Design & Schematics:** [CERN-OHL-P v2](LICENSE-HARDWARE)
- **Documentation:** [CC-BY-4.0](LICENSE-DOCS)
