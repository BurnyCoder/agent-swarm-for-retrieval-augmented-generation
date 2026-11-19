# Running the study

Clone the private repository recursively so the Arctic comparator is available. Install uv, Codex CLI, bubblewrap and ripgrep in Linux or the Ubuntu WSL2 distribution. Use Python 3.12. Place `OPENAI_API_KEY` in the project-root `.env`. Windows uses a lightweight local uv environment and dispatches to the same Linux runtime. The launcher stores large files under `D:\AI\luna-folderrag` when available. Native Linux users can set `FOLDERRAG_HOME` to an empty dedicated directory. [uv](https://docs.astral.sh/uv/) · [Codex CLI](https://learn.chatgpt.com/docs/non-interactive-mode)

```powershell
uv run folderrag ask --folder D:\documents --agents 4 "Which sources describe the change, and where do they disagree?"
uv run folderrag ask --folder D:\documents --agents 2 --json "Which setting controls the interval?"
uv run folderrag dashboard --port 8765
```

Open the local dashboard at [localhost, port 8765](http://localhost:8765). The equivalent native Linux entry is `sh scripts/linux-run folderrag`. The model runs in a fresh namespace with a read-only normalized text snapshot and a budgeted broker. Shell/Python reads use paths inside `/work`. Exact citations use character offsets in normalized text. PDF pages, slides, spreadsheet rows and Word paragraphs are labeled in those text views. Linux CLI source links open original files; page and row labels identify converted material.

```sh
sh scripts/linux-run folderrag prepare
sh scripts/linux-run pytest -q
sh scripts/linux-run folderrag run dev
sh scripts/linux-run folderrag historical
sh scripts/linux-run folderrag freeze
# Commit and push protocol/freeze.json before confirmation.
sh scripts/linux-run folderrag run test
sh scripts/linux-run folderrag run diagnostics
sh scripts/linux-run folderrag counterfactual
sh scripts/linux-run folderrag diagnostics-audit
sh scripts/linux-run folderrag report
```

Every generation logs its API-visible request and output to the terminal and timestamped private JSONL. Use terminal redirection for unattended runs. Completed condition records and intermediate answers are atomic and reusable after a restart. An ambiguous upstream bill retains the maximum reservation. The $50 ledger is shared across invocations on this machine. Keep the same data directory when resuming a study.

The reporting command regenerates tables, figures, summary reports, paper PDF, and explorer data. The release script verifies both Hugging Face repositories are private before uploading an allowlist. The live dashboard reads local records; the private hosted explorer shows the last released milestone.
