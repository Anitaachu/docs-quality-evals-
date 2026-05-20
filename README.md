# Docs quality evals

A reference implementation for evaluating documentation quality using LLM-as-judge. Companion to my Write the Docs talk *Building Your Docs Strategy: Gaps, Playbooks, and Automation*.

## What's in here

- **`rubric.md`** — A five-criteria documentation quality rubric. The strategic artifact your team agrees on.
- **`judge_prompt.md`** — The operational prompt that turns the rubric into an LLM-runnable evaluator.
- **`.github/workflows/docs-quality.yml`** — A GitHub Actions workflow that runs the judge on every PR that touches docs.
- **`.github/scripts/score_docs.py`** — The Python script the workflow invokes.

## What this is

A reference implementation. It works as-is for small to medium docs sites (under ~500 pages). The code is annotated with comments showing where you'd add hardening for larger scale or more demanding production use.

## What this is not

A managed product, a maintained service, or production infrastructure. If you fork this and deploy it, you own the result. Test before relying on it. Adapt for your environment.

## How to use it

### As an artifact, not a tool

Read the rubric. Read the judge prompt. Adapt both for your product, your audience, your editorial standards. The rubric is the strategic work — the rest is execution.

### As a starting point for a pipeline

If you want to actually run this against your docs:

1. Fork the repo or copy the files into your own docs repo
2. Adjust the file paths in `docs-quality.yml` to point at where your docs live
3. Add an `ANTHROPIC_API_KEY` secret in your repo settings (Settings → Secrets and variables → Actions)
4. Edit `rubric.md` and `judge_prompt.md` to fit your product
5. Open a PR that touches a docs file and see what comes back

The first run will cost a few cents. A typical PR with two changed docs pages costs around $0.02 to score.

## Honest limitations

- **The judge can't see your live product.** It catches inconsistencies within and across your docs. It doesn't verify against running code.
- **LLM outputs are non-deterministic.** Scores may vary by half a point between runs. Use the scores as triage signal, not as a precise measurement.
- **Calibrate before trusting at scale.** Score ten pages manually, compare to what the judge says, sharpen the rubric until you agree.
- **This catches the obvious; SMEs catch the subtle.** The judge surfaces, humans decide. Keep the human in the loop on consequential calls.

## Calibration: do this first

Before scoring your whole docs corpus:

1. Pick ten representative pages — some you think are good, some weak, some middling.
2. Score them manually using the rubric.
3. Run them through the judge.
4. Where you and the judge disagree by more than a point, sharpen the rubric until you agree.

Skipping calibration means automating a rubric you haven't tested yet. The system will produce scores; you won't trust them.

## License

MIT. Fork, modify, ship. Attribution appreciated but not required.

## Status

This repo is an artifact of my Write the Docs 2026 talk. I may not actively maintain it. Issues are welcome but won't be triaged on any particular schedule. Feel free to fork and adapt to your context.
