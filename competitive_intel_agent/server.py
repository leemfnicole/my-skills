"""
Flask web UI for the Competitive Intelligence Agent.

Run directly (not as a module):
    python3 /path/to/competitive_intel_agent/server.py

The server is self-contained: it adds the Skills root to sys.path so it can
import the competitive_intel_agent package regardless of cwd.
"""

import sys
import json
import asyncio
import os
from pathlib import Path
from datetime import datetime

# ── Make package importable from any cwd ──────────────────────────────────
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from flask import Flask, render_template_string, request, Response, stream_with_context

app = Flask(__name__, instance_path="/tmp")
PORT = 5001

WATCH_FILE   = ROOT / "competitive_intel_agent" / "watch.json"
BATTLECARD_DIR = ROOT / "battlecards"
CHANGELOG_FILE = ROOT / "competitive-intel" / "changelog.md"

# ── HTML template ─────────────────────────────────────────────────────────
HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Competitive Intel</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #0f0f11; color: #e2e2e5; min-height: 100vh; }
  .header { background: #1a1a1f; border-bottom: 1px solid #2a2a30;
            padding: 18px 32px; display: flex; align-items: center; gap: 12px; }
  .header h1 { font-size: 1.1rem; font-weight: 600; color: #f0f0f3; }
  .badge { background: #7c3aed22; color: #a78bfa; border: 1px solid #7c3aed44;
           border-radius: 4px; padding: 2px 8px; font-size: 0.7rem; font-weight: 600; letter-spacing:.05em; }
  .main { max-width: 960px; margin: 0 auto; padding: 32px 24px; }
  h2 { font-size: 0.8rem; font-weight: 600; text-transform: uppercase;
       letter-spacing: .1em; color: #888; margin-bottom: 16px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 12px; margin-bottom: 40px; }
  .card { background: #1a1a1f; border: 1px solid #2a2a30; border-radius: 10px;
          padding: 20px; transition: border-color .15s; }
  .card:hover { border-color: #7c3aed55; }
  .card-title { font-size: 1rem; font-weight: 600; margin-bottom: 4px; color: #f0f0f3; }
  .card-sub { font-size: 0.8rem; color: #888; margin-bottom: 16px; }
  .btn { display: inline-block; padding: 8px 16px; border-radius: 6px; font-size: 0.82rem;
         font-weight: 500; cursor: pointer; border: none; text-decoration: none;
         transition: opacity .15s; }
  .btn:hover { opacity: .85; }
  .btn-primary { background: #7c3aed; color: #fff; }
  .btn-ghost { background: #2a2a30; color: #ccc; }
  .btn + .btn { margin-left: 8px; }
  .custom-form { background: #1a1a1f; border: 1px solid #2a2a30; border-radius: 10px;
                 padding: 24px; margin-bottom: 40px; }
  .row { display: flex; gap: 10px; flex-wrap: wrap; }
  input[type=text], textarea {
    background: #0f0f11; border: 1px solid #2a2a30; border-radius: 6px;
    color: #e2e2e5; padding: 9px 12px; font-size: 0.85rem; outline: none;
    transition: border-color .15s; }
  input[type=text]:focus, textarea:focus { border-color: #7c3aed; }
  input[type=text] { flex: 1; min-width: 140px; }
  textarea { width: 100%; min-height: 60px; resize: vertical; margin-top: 10px; font-family: inherit; }
  #output-box { display: none; background: #0a0a0d; border: 1px solid #2a2a30;
                border-radius: 8px; padding: 20px; margin-top: 20px; font-family: monospace;
                font-size: 0.8rem; white-space: pre-wrap; max-height: 520px; overflow-y: auto;
                color: #a0e0a0; line-height: 1.6; }
  .changelog-box { background: #1a1a1f; border: 1px solid #2a2a30; border-radius: 10px;
                   padding: 24px; }
  .changelog-content { font-size: 0.82rem; color: #c0c0c8; white-space: pre-wrap;
                       max-height: 400px; overflow-y: auto; line-height: 1.6; }
  .empty { color: #555; font-style: italic; font-size: 0.85rem; }
  .pill { display: inline-block; padding: 2px 7px; border-radius: 20px; font-size: 0.7rem;
          font-weight: 500; margin-left: 6px; }
  .pill-green { background: #14532d33; color: #4ade80; }
</style>
</head>
<body>
<div class="header">
  <h1>Competitive Intel</h1>
  <span class="badge">LIVE</span>
</div>
<div class="main">

  <!-- Watched competitors -->
  <h2>Watched Competitors</h2>
  <div class="grid">
    {% for w in watched %}
    <div class="card">
      <div class="card-title">{{ w.competitor }}</div>
      <div class="card-sub">vs {{ w.your_company }}</div>
      <a class="btn btn-primary" href="#" onclick="runBattlecard('{{ w.competitor }}','{{ w.your_company }}','{{ w.context|replace("'","\\'")|replace('"','\\"') }}')">
        Run Battlecard
      </a>
      {% if w.battlecard_exists %}
      <a class="btn btn-ghost" href="/battlecard/{{ w.slug }}">View <span class="pill pill-green">saved</span></a>
      {% endif %}
    </div>
    {% endfor %}
  </div>

  <!-- Custom run -->
  <h2>Custom Run</h2>
  <div class="custom-form">
    <div class="row">
      <input type="text" id="competitor" placeholder="Competitor name" />
      <input type="text" id="your_company" placeholder="Your company" />
      <button class="btn btn-primary" onclick="runCustom()">Run</button>
    </div>
    <textarea id="context" placeholder="Optional context about your product / ICP…"></textarea>
    <div id="output-box"></div>
  </div>

  <!-- Changelog -->
  <h2>Changelog</h2>
  <div class="changelog-box">
    {% if changelog %}
    <div class="changelog-content">{{ changelog }}</div>
    {% else %}
    <p class="empty">No changelog yet. Run the tracker to populate it.</p>
    {% endif %}
  </div>

</div>

<script>
function runBattlecard(competitor, company, context) {
  document.getElementById('competitor').value = competitor;
  document.getElementById('your_company').value = company;
  document.getElementById('context').value = context;
  runCustom();
}

function runCustom() {
  const competitor = document.getElementById('competitor').value.trim();
  const company    = document.getElementById('your_company').value.trim();
  const context    = document.getElementById('context').value.trim();
  if (!competitor || !company) { alert('Enter competitor and your company.'); return; }

  const box = document.getElementById('output-box');
  box.style.display = 'block';
  box.textContent = '⏳  Starting research (3 parallel agents)…\\n\\n';

  const params = new URLSearchParams({ competitor, your_company: company, context });
  const es = new EventSource('/stream?' + params);

  es.onmessage = e => {
    if (e.data === '[DONE]') { es.close(); box.textContent += '\\n✅  Done. Refresh to see in battlecards.'; return; }
    if (e.data === '[ERROR]') { es.close(); return; }
    box.textContent += e.data;
    box.scrollTop = box.scrollHeight;
  };
  es.onerror = () => { es.close(); };
}
</script>
</body>
</html>"""

BATTLECARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{{ title }} — Battlecard</title>
<style>
  * { box-sizing: border-box; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #0f0f11; color: #e2e2e5; padding: 32px 24px; max-width: 860px; margin: 0 auto; }
  a { color: #a78bfa; }
  h1 { font-size: 1.3rem; margin-bottom: 24px; color: #f0f0f3; }
  pre { background: #1a1a1f; border: 1px solid #2a2a30; border-radius: 8px;
        padding: 20px; white-space: pre-wrap; font-size: 0.82rem; line-height: 1.7; color: #c8c8d0; }
  .back { display: inline-block; margin-bottom: 20px; color: #a78bfa; text-decoration: none; font-size:.85rem; }
</style>
</head>
<body>
<a class="back" href="/">← Back</a>
<h1>{{ title }}</h1>
<pre>{{ content }}</pre>
</body>
</html>"""


# ── Routes ─────────────────────────────────────────────────────────────────

def _load_watched():
    if not WATCH_FILE.exists():
        return []
    items = json.loads(WATCH_FILE.read_text())
    result = []
    for w in items:
        slug = w.get("competitor", "").lower().replace(" ", "_")
        bf = BATTLECARD_DIR / f"{slug}.md"
        result.append({**w, "slug": slug, "battlecard_exists": bf.exists()})
    return result


def _load_changelog(lines: int = 80) -> str:
    if not CHANGELOG_FILE.exists():
        return ""
    text = CHANGELOG_FILE.read_text(encoding="utf-8")
    all_lines = text.splitlines()
    return "\n".join(all_lines[-lines:]) if len(all_lines) > lines else text


@app.route("/")
def index():
    return render_template_string(
        HTML,
        watched=_load_watched(),
        changelog=_load_changelog(),
    )


@app.route("/battlecard/<slug>")
def view_battlecard(slug: str):
    path = BATTLECARD_DIR / f"{slug}.md"
    if not path.exists():
        return f"Battlecard '{slug}' not found.", 404
    return render_template_string(
        BATTLECARD_HTML,
        title=slug.replace("_", " ").title(),
        content=path.read_text(encoding="utf-8"),
    )


@app.route("/stream")
def stream():
    competitor  = request.args.get("competitor", "").strip()
    your_company = request.args.get("your_company", "").strip()
    context     = request.args.get("context", "").strip()

    if not competitor or not your_company:
        return "Missing params", 400

    def generate():
        import io, contextlib
        buf = io.StringIO()

        def emit(text: str):
            # SSE format: each message on its own line prefixed with "data: "
            for line in text.split("\n"):
                yield f"data: {line}\n"
            yield "\n"

        try:
            # Capture stdout from the agent (it prints progress lines)
            from competitive_intel_agent.agent import build_battlecard
            from competitive_intel_agent.formatter import to_markdown

            yield from emit(f"🔍  Researching {competitor} (3 parallel agents)…\n")

            loop = asyncio.new_event_loop()
            card, raw_json = loop.run_until_complete(
                build_battlecard(competitor, your_company, context or None)
            )
            loop.close()

            yield from emit("\n✅  Research complete. Synthesizing battlecard…\n\n")

            md = to_markdown(card)
            yield from emit(md[:6000])  # stream first 6k chars

            # Save battlecard
            slug = competitor.lower().replace(" ", "_")
            BATTLECARD_DIR.mkdir(parents=True, exist_ok=True)
            (BATTLECARD_DIR / f"{slug}.md").write_text(md, encoding="utf-8")
            yield from emit(f"\n\n💾  Saved to battlecards/{slug}.md")
            yield "data: [DONE]\n\n"

        except Exception as exc:
            yield from emit(f"\n❌  Error: {exc}")
            yield "data: [ERROR]\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


if __name__ == "__main__":
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print("Warning: ANTHROPIC_API_KEY not set — battlecard generation will fail.")
        print("Export it: export ANTHROPIC_API_KEY=sk-ant-…\n")
    print(f"Starting Competitive Intel server on http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)
