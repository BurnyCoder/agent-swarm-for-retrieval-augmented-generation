# Running the study

The end-of-day release records a shortened held-out panel. The [cutoff manifest](../protocol/closeout.json) identifies every included question and every completed record outside the panel. The [experiment inventory](../reports/experiments/inventory.md) gives original targets and the status of each condition. On the study machine, a local stop record prevents the experiment commands from dispatching more model requests. Reporting, the dashboard, and private archival remain available.

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

For upstream capacity errors, the study controller stops dispatch and resumes the frozen phase with a gradual increase in the number of concurrent questions. Use `scripts/study.ps1 -StartAt test -RecoverCapacity` after an interruption. `uv run folderrag reconcile test` uses the provider's free token counter to certify a tighter worst-case charge for stale reservations. The reserved amount still covers the full possible output, and the raw attempts are retained. [Recovery protocol](../reports/provider-overload.md)

In the explorer, choose a corpus and switch between answer quality, mean inference cost and median answer time. The swarm-size chart includes a question only after sizes 1, 2, 4 and 8 have all scored it. The paper and explorer use the same matched measurements. The answer table below includes each completed condition as it arrives.

On WSL, an optional `FOLDERRAG_ARCTIC_VENV` can point to a Linux-native environment containing the same locked Arctic dependencies. This avoids repeated library imports across the Windows filesystem boundary for the comparator. The model, tool configuration and deadlines are identical.

The grounding audit records verbatim passages in prompts and the tool output present in subsequent model requests, including native shell output. It recovers contiguous runs of at least six whitespace-separated words from annotated news articles and sends up to 10,000 recovered characters per fact to the blinded support judge. Excerpts shorter than this threshold or beyond that audit window can be missed. Filename recall and source-support judgments are reported separately.

For unattended reproduction on this machine, `scripts/study.ps1` runs development, publishes the size and sample freeze, verifies its Git blob, runs the paired test, and releases the evidence audit and controls. Use `-StartAt freeze`, `test`, or `diagnostics` to resume at a phase boundary. The optional `-ArcticVenv` points to the locked Linux comparator environment. The release contains archived benchmark logs, source, answers and provider usage. Interactive questions asked with `ask` stay local. The local dashboard displays settled upper estimates and in-flight reservations separately.

Text and UTF-8 source, text-layer PDFs, HTML, Word DOCX paragraphs/tables, PowerPoint PPTX slide text, and Excel XLSX rows are supported. PDF images require prior OCR. Binary files, symlinks, private configuration files, hidden directories, notebooks and files larger than five MiB are excluded from the mounted folder. The JSON response links to both the original and the exact normalized text view. On Windows, the launcher emits native drive paths.
