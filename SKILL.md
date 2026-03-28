---
name: job-application-tailor
description: >
  Tailors a resume and cover letter to a specific job description to pass ATS 
  screening (~80% keyword alignment), with each section/paragraph tied to why 
  the candidate wants to work at this specific company. Also crafts a personalized 
  LinkedIn message to the recruiter or hiring manager.
triggers:
  - "tailor my resume"
  - "update my resume for this job"
  - "help me apply to"
  - "ATS optimize"
  - "rewrite my cover letter for"
  - "LinkedIn recruiter message"
---

# Job Application Tailor

A skill for tailoring resumes and cover letters to specific job descriptions, 
optimizing for ATS keyword alignment (~80%) while making every section feel 
authentic and company-specific. Includes a LinkedIn recruiter outreach message.

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

Structure every cover letter the same way, with company-tie baked into each paragraph:

### Paragraph 1 — The Hook (Why This Company, Specifically)
- Open with a specific detail about the company (product, mission, recent news, culture)
- NOT: "I'm excited to apply for the [role] at [Company]"
- YES: "When [Company] launched [X], I immediately understood why — [specific insight about their approach or market]"
- End with: a one-line statement of why you're the right fit

### Paragraph 2 — Proof of Relevant Experience
- Lead with the most relevant experience from the resume
- Tie it explicitly to what the role needs (use JD language)
- Include at least one metric/result
- End with: a bridge sentence connecting your past to their future

### Paragraph 3 — Why You + Why Them = Unique Fit
- What specifically about this company's mission, product, or approach resonates with you?
- What do you bring that most candidates won't? (your unfair advantage)
- Avoid generic statements like "I'm passionate about innovation"
- Be specific: "Your approach to [X] mirrors how I've been thinking about [Y]"

### Paragraph 4 — Call to Action
- One sentence about what you'd want to explore in a conversation
- Forward-looking and confident — not apologetic or hedging
- "I'd love to talk about how I can bring [specific thing] to [Company]'s [team/product/mission]."

### Cover Letter Rules
- Max 4 paragraphs, ~300 words
- No paragraph should be able to copy-paste into a letter for a different company
- Tone should match company culture (startup = more casual/energetic; enterprise = more formal)

---

## Step 5: LinkedIn Recruiter Message

Craft a short, specific outreach message (max 300 characters for InMail, or ~5 sentences for a connection request note).

### Formula
1. **Specific opener**: Mention the role by name + one specific thing about the company
2. **Why you**: One sentence with your most relevant credential or win
3. **Ask**: Clear, low-friction ask — "Would love to connect" or "Happy to share more"

### Tone Rules
- Warm but not desperate
- Specific but not exhaustive (leave them wanting to learn more)
- Don't recap your entire resume — that's what the application is for
- Never start with "I hope this message finds you well"

### Two Versions
Provide two versions:
- **Version A — Connection Request Note** (short, <300 chars)
- **Version B — InMail / Direct Message** (longer, 3–5 sentences)

---

## Output Format

Deliver in this order:

1. **ATS Scorecard** — Before/after keyword alignment score
2. **Tailored Resume** — Full resume rewrite, clearly formatted
3. **Tailored Cover Letter** — Full letter with paragraph labels
4. **LinkedIn Message** — Both versions (A and B)
5. **What Changed** — A brief bullet list of the key changes made and why

---

## Integrity Rules — Do Not Hallucinate

These rules are non-negotiable. The resume and cover letter represent a real person applying for a real job. Fabricating anything — even small details — can damage their credibility or get them caught in an interview.

- **Never invent experience**: Only use roles, projects, and responsibilities that exist in the original resume. Do not add jobs, companies, or titles that weren't there.
- **Never fabricate metrics**: If the original resume says "improved pipeline efficiency," do not rewrite it as "improved pipeline efficiency by 40%" unless the user provided that number. Flag missing metrics and ask the user to fill them in.
- **Never add skills the user didn't claim**: If a keyword from the JD doesn't appear in the resume and the user hasn't confirmed they have that skill, do NOT add it. Instead, flag it: "The JD mentions [X] — do you have experience with this? If so, add it and I'll incorporate it."
- **Never invent company knowledge**: Don't fabricate specific product details, company milestones, or quotes about the company's mission unless they came from the JD or from what the user shared.
- **Rewrite, don't replace**: Your job is to reframe and reorder what's already there — not to create a new person. Every sentence in the output must be traceable back to something in the original resume or something the user explicitly told you.
- **When in doubt, ask**: If a bullet is vague and could be interpreted multiple ways, ask the user what they actually did before rewriting it with specifics.

> **Reminder**: A strong application is an honest one. The goal is to help the user present their real experience in the most compelling, relevant way — not to manufacture a candidate who doesn't exist.

---

## Voice Preservation — Make It Sound Like They Wrote It

This is one of the most important and most overlooked parts of a good rewrite. A resume or cover letter that sounds like a different, more polished person will hurt the candidate in interviews — they won't be able to live up to the version of themselves on paper.

- **Capture their voice first**: Before rewriting, note the user's natural writing style from their original resume and cover letter. Are they direct or warm? Formal or conversational? Do they write long bullets or short ones? Do they use "I" or avoid it? Match that register.
- **Don't over-polish**: Resist the urge to make everything sound maximally corporate or impressive. If the user writes plainly, rewrite plainly — just more precisely.
- **Preserve their word choices where possible**: If they use a specific phrase or framing that's authentic to them, keep it unless it actively hurts clarity or ATS alignment.
- **Flag when you've had to deviate**: If a rewritten section sounds noticeably different from their original voice, note it: "I rewrote this bullet more formally to match the JD's tone — let me know if you'd like to dial it back."
- **Never replace their personality with polish**: The goal is their best self on paper, not a generic high-performer template.

### Target Tone
The writing should feel like it came from a real, confident human — not a LinkedIn influencer or a corporate PR bot. Aim for:
- **Honest**: Says what's true, doesn't oversell or hedge. Confident without being arrogant.
- **Professional**: Polished enough to take seriously, but not stiff or stuffy.
- **A little witty**: A dry observation, a clever turn of phrase, a moment of self-awareness — not jokes, just personality. Think "smart person who's also fun to work with."
- **Genuinely excited**: Not "I am passionate about synergizing cross-functional outcomes." More like "I've been following [Company]'s work on [X] for a while — this role feels like the obvious next move."

If the writing comes out sounding like it was generated by a robot or written by a committee, rewrite it. A hiring manager should finish reading and think: *I want to meet this person.*

> **Watch out for**: "leverage", "synergy", "results-driven", "passionate about", "dynamic", "self-starter", "thought leader", "move the needle", "circle back", "deep dive." These phrases are the enemy. Flag and replace them every time.

---

## Additional Guardrails

### Title & Employment Integrity
- **Never upgrade job titles**: Do not change "Marketing Coordinator" to "Marketing Manager" or "Lead" to "Director" — even if the JD uses that language. Use the user's actual title, always.
- **Never obscure or reorder employment dates**: If there are gaps in employment, do not rearrange the timeline to hide them. Flag the gap and let the user decide how to address it (e.g., freelance, caregiving, job searching — their call to disclose).
- **Never infer responsibilities**: If the user listed "supported product launches," do not rewrite it as "owned product launches" unless they confirm that's accurate. Scope inflation is a form of fabrication.

### Cover Letter Authenticity
- **Never fabricate personal anecdotes**: Do not invent a story about why the user loves the company, a moment they had with the product, or a connection to the mission — unless the user provided it.
- **Never claim product usage or attendance**: Don't write "as a long-time user of your platform" or "I attended your keynote" unless the user said so.
- **Never invent a personal connection**: Don't imply familiarity ("your team has always stood out to me") without something to back it up.

### LinkedIn Message Honesty
- **Never claim mutual connections**: Don't reference shared contacts, alma maters, or communities unless the user confirmed them.
- **Never imply false urgency or leverage**: Don't suggest the user has competing offers or a tight timeline unless that's true and the user wants to use it.

### ATS Ethics
- **No black-hat ATS tricks**: Do not recommend hiding keywords in white text, invisible characters, or metadata. These are detectable and can get an application flagged or rejected.
- **No keyword stuffing**: Don't add keywords in ways that would read as unnatural to a human reviewer. If it sounds weird out loud, rewrite it.

---

## Edge Cases

- **No cover letter provided**: Draft one from scratch using the resume + JD + any company insight the user shares
- **Very long resume (4+ pages)**: Flag this and ask if they want to trim to 1–2 pages as part of the rewrite
- **JD is vague or short**: Ask the user for 2–3 things they know about the role beyond the JD
- **User doesn't know the recruiter's name**: Use a generic but warm opener ("Hi [Company] Recruiting Team,") and note they can personalize it
- **Role is a stretch/career pivot**: Acknowledge this and focus the rewrite on transferable skills + strong company-tie to compensate

---

## Quality Check (Run Before Delivering)

Before presenting the output, verify:
- [ ] ATS alignment is at or above 80% in the rewritten resume
- [ ] No paragraph in the cover letter could be copy-pasted to a different company's application
- [ ] Every major resume section has at least one element tied to this company's context
- [ ] LinkedIn message is specific, warm, and under the character limit (Version A)
- [ ] No clichés: "passionate", "team player", "results-driven", "detail-oriented" used without specifics
- [ ] All metrics are preserved from the original resume (never remove quantified wins)
- [ ] Every sentence in the rewritten resume traces back to something in the original or something the user explicitly confirmed
- [ ] No skills, metrics, or experiences were added that the user didn't provide
- [ ] Any gaps between the JD keywords and the resume are flagged to the user rather than silently filled in
- [ ] No job titles were upgraded or modified from the original
- [ ] Employment dates and gaps are preserved as-is (not reordered or hidden)
- [ ] The output sounds like the user wrote it — not a generic polished template
- [ ] Tone is honest, professional, and has a little wit/excitement — reads like a real person, not a PR bot
- [ ] No banned corporate buzzwords: "leverage", "synergy", "results-driven", "passionate about", "dynamic", "self-starter", "thought leader", "move the needle"
- [ ] No personal anecdotes, product usage claims, or connections were invented in the cover letter
- [ ] LinkedIn message contains no fabricated mutual connections or false urgency
- [ ] No black-hat ATS tactics (hidden text, keyword stuffing) were used or suggested
