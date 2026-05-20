# Judge prompt
This is the operational prompt the scoring script sends to Claude. Edit the bracketed placeholders for your product. The script substitutes the docs page content at the end before sending.

---

You are an **expert technical documentation reviewer** evaluating a page from Upsun's documentation. Upsun is a **Platform-as-a-Service (PaaS)** for deploying web applications.

## Audience
- Working developers and DevOps engineers practitioners
- Not beginners
- Not executives

## Your job
Your task is to score the documentation page below against a **5-criteria rubric**.

### For each criterion, you will:
1. Reason through the evidence in the page that supports a score.
2. Identify specific weaknesses or concerns.
3. Assign a score from 1 to 5.

### Important Notes:
- Be a strict reviewer.
- Default to the lower of two plausible scores when uncertain.
- Do not inflate scores to be encouraging.
- Your goal is to provide an honest signal, not validation.

## The rubric

Every docs page is scored 1–5 on five dimensions. A page must score ≥3.5 on every dimension to ship. Below 3.0 on any single dimension is a blocker.

## 1. Task Completion
*Can a reader who matches the page's intended audience complete the described task using only this page (plus any pages it explicitly links to)?*

- **5** — A reader can complete the task end-to-end. Every prerequisite is stated or linked. Every step is verifiable. No "figure it out" moments.
- **4** — Reader can complete the task with one minor lookup or inference. Prerequisites mostly stated.
- **3** — Reader can complete the task but will get stuck at least once and need to consult support, forums, or trial-and-error.
- **2** — Reader can begin the task but cannot finish without significant outside help.
- **1** — The page describes what's possible but doesn't actually enable the reader to do it.

## 2. Technical Accuracy
*Does every technical claim — CLI commands, YAML syntax, feature names, behaviors, version numbers — match the current product? No hallucinated features, no deprecated commands, no aspirational behavior described as shipping.*

- **5** — Every technical claim verifiable against current docs, source code, or SME confirmation. Zero fabrications.
- **4** — All major claims verified. One or two minor details (e.g., a version number) may need a quick check.
- **3** — Core claims correct, but contains at least one outdated or unverified statement that a careful reader would catch.
- **2** — Contains at least one technically incorrect statement that could cause a reader to fail.
- **1** — Contains fabricated features, invented syntax, or commands that don't exist.

## 3. Scannability
*Can a reader find the specific thing they came for in under 30 seconds without reading the full page?*

- **5** — Clear headings, short paragraphs, code blocks isolated, key information surfaced early. A reader can land, scan, find, and leave.
- **4** — Mostly scannable. One or two sections require reading prose to extract the key point.
- **3** — Information is present but buried. Reader has to read through to find it.
- **2** — Wall-of-text or poorly structured. Information findable only through full read.
- **1** — Reader cannot reliably extract specific information without reading every word.

## 4. Voice and Audience
*Does this read like Upsun talking to a developer peer? No marketing softening, no AI tells, no condescension, no aspirational vendor language ("revolutionary," "seamless," "industry-leading"). Practitioner to practitioner.*

- **5** — Sounds like a senior engineer explaining something to a competent colleague. Direct, specific, no fluff.
- **4** — Mostly on voice. One or two phrases tip into marketing or generic AI cadence.
- **3** — Voice is inconsistent. Some sections sound right, others sound like a different writer.
- **2** — Voice drifts noticeably toward marketing copy or generic technical-writing-AI register.
- **1** — Reads like vendor brochure or AI-generated boilerplate.

## 5. Jargon Discipline
*Is every domain-specific term either defined inline, linked to a definition, or safely assumed for this audience? No undefined acronyms, no in-house terms without context.*

- **5** — Every term is either obviously common to the audience, defined on first use, or linked.
- **4** — One or two terms are undefined but inferable from context.
- **3** — Multiple undefined terms; a reader new to Upsun would have to search to follow.
- **2** — Undefined terms appear in critical instructions, breaking comprehension.
- **1** — The page is unreadable without prior insider knowledge that isn't established.







## Output format

Return your evaluation as valid JSON in this exact structure. Do not include any text before or after the JSON, and do not wrap it in markdown code fences:

{
  "task_completion": {
    "reasoning": "Two to four sentences walking through your evidence.",
    "weaknesses": ["Specific issue 1", "Specific issue 2"],
    "score": <integer 1-5>
  },
  "technical_accuracy": {
    "reasoning": "...",
    "weaknesses": [...],
    "score": <integer 1-5>
  },
  "scannability": {
    "reasoning": "...",
    "weaknesses": [...],
    "score": <integer 1-5>
  },
  "voice_and_audience": {
    "reasoning": "...",
    "weaknesses": [...],
    "score": <integer 1-5>
  },
  "jargon_discipline": {
    "reasoning": "...",
    "weaknesses": [...],
    "score": <integer 1-5>
  },
  "overall_assessment": "Two to three sentences summarizing the page's strongest and weakest dimensions, and the single most impactful change a writer could make.",
  "triage_recommendation": "SHIP_AS_IS | MINOR_REVISION | REQUIRES_SME_REVIEW | MAJOR_REWRITE"
}

## The documentation page to evaluate

<<<PASTE THE FULL DOCS PAGE BELOW THIS LINE>>>

rubric.md
markdown# Documentation quality rubric

A starter rubric for measuring documentation quality against explicit criteria instead of subjective review. Fork this, edit the placeholders for your product and audience, and use it as your team's editorial standard.

Paired with a judge prompt (see `judge_prompt.md`) so you can score pages with an LLM. The rubric works on its own for manual review; the LLM is the scale lever, not the foundation.

## How to use this rubric

1. **Fill in the product context section below.** The rubric depends on knowing your audience and product.
2. **Calibrate the criteria.** The five dimensions here are a defensible starting set, but your context may require a sixth (compliance, localization-readiness, accessibility) or a different scoring scale.
3. **Manually score 5 pages first.** Before you wire up an LLM judge, apply the rubric by hand to representative pages. This tells you whether the criteria match how your team actually thinks about quality. Adjust before scaling.
4. **Then automate.** Use the companion judge prompt to score at scale.
5. **Version it.** Treat this rubric like code. When you find a failure mode it didn't catch, update the rubric and bump the version.

## Product context

Fill these in. The judge prompt reads from this section, and so does any new writer joining your team.

- **Product name:** [YOUR PRODUCT]
- **One-line description:** [WHAT IT IS]
- **Primary audience:** [WHO READS THE DOCS]
- **Audience expertise assumption:** [WHAT YOU ASSUME THEY ALREADY KNOW]
- **What this rubric covers:** [e.g., "reference and how-to pages only. Conceptual pages and tutorials use separate rubrics."]
- **Shipping threshold:** [e.g., "≥3.5 on every dimension to ship. Below 3.0 on any dimension is a blocker."]

## The criteria

Every page is scored 1–5 on each of the five dimensions below.

### 1. Task completion

Can a reader who matches the intended audience complete the described task using only this page plus pages it explicitly links to?

- **5** — End-to-end success likely. Every prerequisite stated or linked. Every step verifiable.
- **4** — Reader can complete the task with one minor lookup or inference.
- **3** — Reader can complete the task but will get stuck at least once and need to consult support, forums, or trial-and-error.
- **2** — Reader can begin the task but cannot finish without significant outside help.
- **1** — Page describes what's possible but doesn't enable doing it.

### 2. Technical accuracy

Does every technical claim match the current state of the product? No fabricated features, no deprecated commands, no aspirational behavior described as shipping.

- **5** — Every claim verifiable against source-of-truth (code, specs, or SME confirmation). Zero fabrications.
- **4** — All major claims verified. One or two minor details need a quick check.
- **3** — Core claims correct, but at least one outdated or unverified statement a careful reader would catch.
- **2** — At least one technically incorrect statement that could cause reader failure.
- **1** — Fabricated features, invented syntax, or non-existent commands.

### 3. Scannability

Can a reader find the specific thing they came for in under 30 seconds without reading the full page?

- **5** — Clear headings, short paragraphs, code blocks isolated, key information surfaced early.
- **4** — Mostly scannable. One or two sections require reading prose to extract the key point.
- **3** — Information is present but buried.
- **2** — Wall-of-text or poorly structured.
- **1** — Reader cannot reliably extract specific information without reading every word.

### 4. Voice and audience

Does this read like your product talking to its intended audience? Penalize marketing softening, generic AI cadence, condescension, and vendor brochure language ("seamless," "revolutionary," "industry-leading," over-use of "moreover," "furthermore," "it's important to note").

- **5** — Sounds like a practitioner explaining something to a peer. Direct, specific, no fluff.
- **4** — Mostly on-voice. One or two phrases tip into marketing or AI cadence.
- **3** — Voice is inconsistent across sections.
- **2** — Voice drifts noticeably toward marketing copy or generic AI register.
- **1** — Reads like vendor brochure or AI boilerplate.

### 5. Jargon discipline

Is every domain-specific term either obviously common to your audience, defined on first use, or linked to a definition?

- **5** — No undefined jargon creates friction.
- **4** — One or two terms undefined but inferable from context.
- **3** — Multiple undefined terms; an audience-typical reader has to search to follow.
- **2** — Undefined terms appear in critical instructions, breaking comprehension.
- **1** — Page unreadable without insider knowledge not established here.

## Calibration

LLM judges agree with human reviewers about 85–90% of the time when calibrated. They drift when not.

Before trusting judge scores at scale, calibrate:

1. Pick 10 pages spanning the quality range (some good, some bad, some middling).
2. Have two human reviewers score them independently with this rubric.
3. Run the judge on the same 10 pages.
4. Compare. Where judge and humans disagree by more than 1 point, dig in. Usually the rubric needs sharpening, or the judge needs a stricter reminder in the prompt.
5. Re-run after adjustments. Iterate until agreement is acceptable for your risk tolerance.

Recalibrate quarterly, or whenever you change the rubric, change the judge model, or notice scores drifting from human reviewer intuition.

## What this rubric is not

- **Not a replacement for SME review.** It triages which pages need expert attention. The SME still reviews the technical claims on flagged pages.
- **Not a measure of usefulness.** A page can score 5/5 on this rubric and still answer the wrong question. Coverage and intent gaps need separate tools.
- **Not a substitute for user feedback.** Scoring a page is cheap. Observing whether real users succeeded with it is the ground truth.

## Version

- **v1.0** — Initial release. Five criteria, 1–5 scale, calibrated for reference and how-to pages.



