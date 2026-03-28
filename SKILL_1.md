---
name: job-application-tailor
description: >
  Tailors a resume and cover letter to a specific job description to pass ATS 
  screening (~80% keyword alignment), with each section/paragraph tied to why 
  the candidate wants to work at this specific company. Also crafts a personalized 
  LinkedIn message to the recruiter or hiring manager. Outputs three separate documents, 
  including tailored resume, cover letter, and LinkedIn message.

---

# Job Application Tailor

A skill for tailoring resumes and cover letters to specific job descriptions, 
optimizing for ATS keyword alignment (~80%) while making every section feel 
authentic and company-specific. Always delivers three output documents: 
a tailored resume, a cover letter, and a LinkedIn outreach message.

---

## What You Need to Provide

To use this skill, the user should provide:
1. **Job description** (paste the full text)
2. **Resume** (paste current resume text or upload as file)
3. **Cover letter** (optional — if not provided, draft one from scratch)
4. **Company research notes** (optional — any info about why they want this role)

If the user only provides a job description and resume, ask for:
- One sentence about why they're excited about this specific company
- The recruiter or hiring manager's name (for the LinkedIn message), if known

---

## Step 1: Job Description Analysis

Parse the job description and extract:

### Keywords (for ATS)
Identify and categorize:
- **Hard skills** (tools, platforms, languages, methodologies)
- **Soft skills** (leadership, collaboration, communication, etc.)
- **Job title variants** (note the exact title used)
- **Industry-specific terms** (jargon the ATS may scan for)
- **Action verbs** used in the JD (these often signal what the company values)

### Company Signal Extraction
Identify:
- Company mission or stated values (from the JD or About section)
- Product/customer focus mentioned
- Culture signals (startup, enterprise, fast-paced, remote, etc.)
- What "success" looks like in this role (look for phrases like "you will", "you'll own", "we expect")

### Role Priority Stack
Rank the top 5–7 things this role is really about. These become the throughline 
for the tailored resume and cover letter.

---

## Step 2: ATS Alignment Scoring

Before rewriting, score the current resume against the JD:

1. List the top 20 keywords/phrases from the JD
2. Check how many appear (exact or close match) in the current resume
3. Calculate: `(matches / 20) × 100 = ATS alignment %`
4. If below 80%, flag which keywords are missing
5. Report: "Current ATS alignment: X%. Target: 80%+. Adding: [list of missing terms]"

Display this as a brief scorecard before presenting the rewrite.

---

## Step 3: Resume Rewrite

Rewrite the resume with these principles:

### Keyword Integration Rules
- Inject missing keywords naturally — never as a keyword dump
- Match the exact phrasing from the JD where possible (ATS is literal)
- Prioritize keywords in: headline/summary, first bullet of each role, skills section
- Use the job title from the JD in the resume headline if it's an honest match

### Company-Tie Principle (Critical)
Every major section should have at least one element that connects to THIS company:
- **Summary/Headline**: Reference the company's space, mission, or product type
- **Work experience bullets**: Emphasize experiences most relevant to this company's context
- **Skills section**: Lead with skills the JD explicitly mentions
- **Any "About Me" or summary paragraph**: Should feel like it was written specifically for this company

### Bullet Rewriting Formula
For each bullet, use: **Action verb + what you did + quantified result + relevance signal**

Example transformation:
- Before: "Managed product launches and worked with cross-functional teams"
- After: "Led go-to-market strategy for 3 AI product launches, partnering with engineering and sales to drive 40% faster time-to-market — directly applicable to [Company]'s focus on rapid deployment"

### ATS Formatting Rules
- Use standard section headers (Experience, Education, Skills — not creative names)
- Avoid tables, columns, text boxes, headers/footers (ATS can't parse these)
- Use standard fonts and bullet characters
- Spell out acronyms at least once

---

## Step 4: Cover Letter Rewrite

The cover letter follows a specific structure: one paragraph per job on the resume that's relevant to this role, bookended by a strong intro and a personal closing. Every paragraph must be company-specific — no paragraph should be copy-pasteable to a different application.

### Structure

**Paragraph 1 — The Hook: Why This Role + Why You**
- Open with a specific, genuine reason why this company or role caught your attention — a product detail, a mission statement, a market position, something real
- NOT: "I'm excited to apply for the [role] at [Company]"
- YES: "When [Company] launched [X], I immediately understood why — [specific insight about their approach or market]"
- Close the paragraph with a confident, one-line statement of why you're the right fit

**One Paragraph Per Relevant Job Experience**
- Write one paragraph for each job in the resume that's meaningfully relevant to this role
- Each paragraph should: name the role/company, describe the most relevant work done there, include at least one metric or concrete result, and end with a sentence connecting that experience directly to what this company needs
- Do not just summarize the bullet points — tell the story of what was accomplished and why it matters here
- If a job is not relevant to this role, skip it — don't force a connection
- Aim for 3–5 sentences per paragraph

**Final Paragraph — Who You Are + Why Here**
- This is the "human" paragraph — who is this person beyond the resume?
- What specifically about this company's mission, product, or approach resonates with them?
- What do they bring that most candidates won't? (their unfair advantage)
- Avoid generic statements like "I'm passionate about innovation"
- Be specific: "Your approach to [X] mirrors how I've been thinking about [Y]"
- End with a confident, forward-looking call to action: "I'd love to talk about how I can bring [specific thing] to [Company]'s [team/product/mission]."

### Cover Letter Rules
- No paragraph should be able to copy-paste into a letter for a different company
- Tone should match company culture (startup = more casual/energetic; enterprise = more formal)
- No apologetic or hedging language — confident throughout
- Max ~400 words total

---

## Step 5: LinkedIn Outreach Message

Craft a short, specific outreach message. Always produce **two versions** as part of the output.

### Formula
1. **Specific opener**: Mention the role by name + one specific thing about the company
2. **Why you**: One sentence with your most relevant credential or win
3. **Ask**: Clear, low-friction ask — "Would love to connect" or "Happy to share more"

### Tone Rules
- Warm but not desperate
- Specific but not exhaustive (leave them wanting to learn more)
- Don't recap the entire resume — that's what the application is for
- Never start with "I hope this message finds you well"

### Two Versions — Both Required in Output
- **Version A — Connection Request Note** (short, <300 characters)
- **Version B — InMail / Direct Message** (longer, 3–5 sentences)

---

## Output Format — Three Separate Documents

**Always deliver all three documents.** Do not skip or combine them. Present them clearly labeled and in this order:

---

### 📄 Document 1: Tailored Resume

Present the full rewritten resume. Before the resume, show a brief ATS scorecard:
> "ATS Alignment: X% → Y% after rewrite. Added keywords: [list]"

---

### 📄 Document 2: Cover Letter

Present the full cover letter, with each paragraph labeled in brackets for clarity during review:

> **[Intro — Why This Role + Why You]**
> ...
>
> **[Experience: [Job Title] at [Company]]**
> ...
>
> **[Experience: [Job Title] at [Company]]**
> ...
>
> **[Closing — Who I Am + Why Here]**
> ...

---

### 📄 Document 3: LinkedIn Message

Present both versions clearly:

> **Version A — Connection Request Note** (<300 characters)
> ...
>
> **Version B — InMail / Direct Message**
> ...

---

### 📝 What Changed
A brief note on the key changes made to the resume and why (2–5 bullets max). Keep it scannable.

---

## Integrity Rules — Do Not Hallucinate

These rules are non-negotiable. The resume and cover letter represent a real person applying for a real job.

- **Never invent experience**: Only use roles, projects, and responsibilities that exist in the original resume
- **Never fabricate metrics**: If the original says "improved pipeline efficiency," do not add a percentage unless the user provided it. Flag missing metrics and ask
- **Never add skills the user didn't claim**: Flag it instead — "The JD mentions [X] — do you have experience with this?"
- **Never invent company knowledge**: Don't fabricate product details or milestones unless they came from the JD or the user
- **Rewrite, don't replace**: Every sentence must trace back to the original resume or something the user confirmed
- **When in doubt, ask**: If a bullet is vague, ask before rewriting it with specifics

---

## Voice Preservation — Make It Sound Like Them

A resume or cover letter that sounds like a different, more polished person will hurt the candidate in interviews.

- **Capture their voice first**: Note the user's natural writing style — are they direct or warm? Formal or conversational? Match that register
- **Don't over-polish**: If they write plainly, rewrite plainly — just more precisely
- **Preserve their word choices where possible**
- **Flag when you've deviated**: "I rewrote this bullet more formally to match the JD's tone — let me know if you'd like to dial it back"

### Target Tone
Honest, professional, with a little wit. Reads like a real confident human — not a LinkedIn influencer or corporate PR bot.

> **Watch out for**: "leverage", "synergy", "results-driven", "passionate about", "dynamic", "self-starter", "thought leader", "move the needle", "circle back", "deep dive." Flag and replace every time.

---

## Additional Guardrails

- **Never upgrade job titles**: Use the user's actual title, always
- **Never reorder employment dates** to hide gaps — flag the gap and let the user decide how to address it
- **Never infer responsibilities**: Don't rewrite "supported product launches" as "owned product launches" without confirmation
- **Never fabricate personal anecdotes** for the cover letter
- **Never claim product usage or attendance** unless the user said so
- **No black-hat ATS tricks**: No hidden keywords, white text, or keyword stuffing

---

## Edge Cases

- **No cover letter provided**: Draft one from scratch using the resume + JD + any company insight the user shares
- **Very long resume (4+ pages)**: Flag and ask if they want to trim to 1–2 pages as part of the rewrite
- **JD is vague or short**: Ask the user for 2–3 things they know about the role beyond the JD
- **User doesn't know the recruiter's name**: Use a generic but warm opener ("Hi [Company] Recruiting Team,") and note they can personalize it
- **Role is a stretch/career pivot**: Acknowledge this and focus on transferable skills + strong company-tie to compensate
- **Resume only has 1–2 relevant jobs**: Cover letter will have fewer experience paragraphs — that's fine, don't pad it

---

## Quality Check (Run Before Delivering)

Before presenting output, verify:
- [ ] All three documents are present: resume, cover letter, LinkedIn message
- [ ] ATS alignment is at or above 80% in the rewritten resume
- [ ] Cover letter follows the correct structure: intro → one paragraph per relevant job → personal closing
- [ ] No paragraph in the cover letter could be copy-pasted to a different company's application
- [ ] LinkedIn message includes both Version A (<300 chars) and Version B (3–5 sentences)
- [ ] No clichés: "passionate", "team player", "results-driven", "detail-oriented" used without specifics
- [ ] All metrics from the original resume are preserved — never remove quantified wins
- [ ] No skills, metrics, or experiences were added that the user didn't provide
- [ ] Gaps between JD keywords and resume are flagged to the user rather than silently filled in
- [ ] No job titles were upgraded or modified from the original
- [ ] Employment dates and gaps are preserved as-is
- [ ] Output sounds like the user wrote it — not a generic polished template
- [ ] No banned corporate buzzwords: "leverage", "synergy", "results-driven", "passionate about", "dynamic", "self-starter", "thought leader", "move the needle"
- [ ] No personal anecdotes, product usage claims, or connections were invented
- [ ] LinkedIn message contains no fabricated mutual connections or false urgency
- [ ] No black-hat ATS tactics were used or suggested

## Triggers
  - "tailor my resume"
  - "update my resume for this job"
  - "help me apply to"
  - "ATS optimize"
  - "rewrite my cover letter for"
  - "LinkedIn recruiter message"
  - "job application"
  
