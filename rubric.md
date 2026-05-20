# Documentation Quality Scoring Criteria

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
- **5** — Every term is either obviously common to the audience,
defined on first use,
or linked.
- **4** — One or two terms are undefined but inferable from context.
- **3** — Multiple undefined terms; a reader new to Upsun would have to search to follow.
- **2** — Undefined terms appear in critical instructions, breaking comprehension.
- **1** — The page is unreadable without prior insider knowledge that isn't established.
