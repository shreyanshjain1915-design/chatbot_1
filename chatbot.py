# ============================================================
#  chatbot.py  —  SiteBot AI  |  3-Mode Logic
#  Mode 1 : Website Builder   (guided 5-step plan)
#  Mode 2 : SEO & Marketing   (guided SEO strategy report)
#  Mode 3 : Generate Website  (full HTML site from 5 inputs)
# ============================================================

import os
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL   = "llama-3.1-8b-instant"

# ── Startup warning (shown in Render/terminal logs) ─────────
if not GROQ_API_KEY:
    print("=" * 60)
    print("  WARNING: GROQ_API_KEY is not set!")
    print("  Get a free key at : https://console.groq.com")
    print("  Local  → create .env file → add: GROQ_API_KEY=your_key")
    print("  Render → Dashboard → Environment → Add variable")
    print("=" * 60)


# ============================================================
#  GROQ HELPER  —  single place for all API calls
# ============================================================
def ask_groq(messages: list, max_tokens: int = 2048) -> str:

    # ── No API key set ──────────────────────────────────────
    if not GROQ_API_KEY:
        return (
            "⚠️ API key not configured.\n\n"
            "To fix this:\n"
            "• Local: create a .env file and add:\n"
            "  GROQ_API_KEY=your_key_here\n\n"
            "• Render: go to your service → Environment tab → "
            "Add variable: GROQ_API_KEY\n\n"
            "Get a free key at: https://console.groq.com"
        )

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model":      GROQ_MODEL,
                "messages":   messages,
                "max_tokens": max_tokens,
            },
            timeout=30,
        )

        # ── Invalid or expired key ──────────────────────────
        if response.status_code == 401:
            return (
                "⚠️ Invalid or expired API key.\n\n"
                "Please check your GROQ_API_KEY at https://console.groq.com\n"
                "and update it in your .env file or Render environment variables."
            )

        # ── Rate limited ────────────────────────────────────
        if response.status_code == 429:
            return (
                "⚠️ Rate limit reached.\n\n"
                "The free Groq tier has usage limits.\n"
                "Please wait a moment and try again."
            )

        # ── Other HTTP error ────────────────────────────────
        if response.status_code not in (200, 201):
            return (
                f"⚠️ Groq API returned an error (HTTP {response.status_code}).\n"
                "Please try again in a moment."
            )

        data = response.json()

        if "choices" not in data:
            return f"⚠️ Unexpected API response: {data}"

        return data["choices"][0]["message"]["content"]

    except requests.exceptions.Timeout:
        return (
            "⚠️ Request timed out.\n"
            "Groq API is taking too long — please try again."
        )

    except requests.exceptions.ConnectionError:
        return (
            "⚠️ Cannot connect to Groq API.\n"
            "Check your internet connection and try again."
        )

    except Exception as e:
        return f"⚠️ Unexpected server error: {str(e)}"


# ============================================================
#  MAIN DISPATCHER  —  routes every message to correct mode
# ============================================================
def chatbot_logic(session: dict, message: str) -> str:

    session["chat_history"].append(message)
    mode = session.get("mode")

    # ── First message → detect mode ─────────────────────────
    if mode is None:
        msg = message.lower()

        seo_keywords = [
            "seo", "marketing", "rank", "traffic",
            "keyword", "google", "strategy", "leads",
        ]
        gen_keywords = [
            "generate", "create website", "build website",
            "make website", "full website", "html site",
            "generate website", "build me a website",
        ]

        if any(w in msg for w in seo_keywords):
            session["mode"] = "seo"
            return _seo_start(session)

        if any(w in msg for w in gen_keywords):
            session["mode"] = "generate"
            return _generate_start(session)

        # Default → website builder
        session["mode"] = "builder"
        return _builder_step(session, message)

    if mode == "builder":
        return _builder_step(session, message)

    if mode == "seo":
        return _seo_step(session, message)

    if mode == "generate":
        return _generate_step(session, message)

    return "Something went wrong. Please reset and try again."


# ============================================================
#  MODE 1 — WEBSITE BUILDER  (5-step guided plan)
# ============================================================
def _builder_step(session: dict, message: str) -> str:

    # Step 1 — business type
    if session["business_type"] is None:
        session["business_type"] = message
        return (
            "Great choice! 🎯\n\n"
            "What is the main goal of your website?\n"
            "(e.g. sell products, get leads, show portfolio, book appointments)"
        )

    # Step 2 — website goal
    elif session["website_goal"] is None:
        session["website_goal"] = message
        return (
            "Perfect! 📄\n\n"
            "Which pages do you need?\n"
            "(e.g. Home, About, Services, Contact, Menu, Shop, Blog)"
        )

    # Step 3 — pages needed
    elif session["pages_needed"] is None:
        session["pages_needed"] = message
        return (
            "Got it! 💻\n\n"
            "Which technology do you prefer?\n"
            "• WordPress  — easy to manage, no coding\n"
            "• React      — fast, modern web app\n"
            "• HTML/CSS   — simple, lightweight static site"
        )

    # Step 4 — tech stack
    elif session["tech_stack"] is None:
        session["tech_stack"] = message
        return (
            "Almost done! 🎨\n\n"
            "What design style do you like?\n"
            "• Modern & minimal\n"
            "• Bold & colorful\n"
            "• Professional & corporate\n"
            "• Playful & creative"
        )

    # Step 5 — design style → generate plan + AI recommendations
    elif session["design_style"] is None:
        session["design_style"] = message
        plan_text = _build_plan_text(session)

        ai_reply = ask_groq(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert website consultant. "
                        "Given the user's website plan, provide exactly:\n"
                        "1) 3 must-have features for this type of site\n"
                        "2) 5 targeted SEO keywords\n"
                        "3) One actionable marketing tip\n"
                        "Be concise, friendly, and specific. "
                        "No markdown asterisks or symbols."
                    ),
                },
                {
                    "role": "user",
                    "content": f"My website plan:\n{plan_text}",
                },
            ],
            max_tokens=600,
        )

        return f"WEBSITE_PLAN_READY\n{plan_text}\n\nAI RECOMMENDATIONS:\n{ai_reply}"

    # After plan is done → free-form follow-up chat
    else:
        return ask_groq(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a friendly website consultant. "
                        "The user already has their website plan. "
                        "Answer follow-up questions helpfully and concisely. "
                        "No markdown asterisks."
                    ),
                },
                {"role": "user", "content": message},
            ],
            max_tokens=500,
        )


def _build_plan_text(session: dict) -> str:
    return (
        f"Business Type: {session['business_type']}\n"
        f"Goal: {session['website_goal']}\n"
        f"Pages: {session['pages_needed']}\n"
        f"Tech Stack: {session['tech_stack']}\n"
        f"Design Style: {session['design_style']}"
    )


# ============================================================
#  MODE 2 — SEO & DIGITAL MARKETING  (5-step strategy report)
# ============================================================

SEO_STEPS = [
    (
        "business_name",
        "What is your business name or website URL?",
    ),
    (
        "business_niche",
        "What is your business niche or industry?\n(e.g. fitness, restaurant, SaaS, e-commerce, education)",
    ),
    (
        "target_audience",
        "Who is your target audience?\n(e.g. young professionals, parents, small business owners, students)",
    ),
    (
        "location",
        "Are you targeting a local area, national, or global audience?",
    ),
    (
        "current_problem",
        "What is your biggest marketing challenge right now?\n(e.g. low traffic, poor Google rankings, no leads, low sales)",
    ),
]


def _seo_start(session: dict) -> str:
    session["seo_step"] = 0
    session["seo_data"] = {}
    return (
        "📊 Let's build your complete SEO & Digital Marketing Strategy!\n\n"
        f"I'll ask you 5 quick questions then generate a full report.\n\n"
        f"Question 1: {SEO_STEPS[0][1]}"
    )


def _seo_step(session: dict, message: str) -> str:
    step = session.get("seo_step", 0)
    data = session.setdefault("seo_data", {})

    if step < len(SEO_STEPS):
        # Save current answer
        key = SEO_STEPS[step][0]
        data[key] = message
        session["seo_step"] = step + 1

        # More questions remaining
        if session["seo_step"] < len(SEO_STEPS):
            next_index    = session["seo_step"]
            next_question = SEO_STEPS[next_index][1]
            return f"Question {next_index + 1}: {next_question}"

        # All 5 answered → generate full strategy
        return _generate_seo_strategy(data)

    # Strategy already delivered → free-form follow-up
    return ask_groq(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert SEO and digital marketing consultant. "
                    "Answer follow-up questions with specific, actionable advice. "
                    "No markdown asterisks."
                ),
            },
            {"role": "user", "content": message},
        ],
        max_tokens=600,
    )


def _generate_seo_strategy(data: dict) -> str:
    prompt = f"""
You are a world-class SEO and digital marketing consultant.

Client Information:
- Business / URL  : {data.get('business_name', 'N/A')}
- Industry / Niche: {data.get('business_niche', 'N/A')}
- Target Audience : {data.get('target_audience', 'N/A')}
- Geographic Focus: {data.get('location', 'N/A')}
- Main Challenge  : {data.get('current_problem', 'N/A')}

Generate a complete, actionable SEO & Digital Marketing Strategy Report.
Include ALL of the following sections:

1. TOP 10 SEO KEYWORDS
   - List each keyword with its search intent (informational / transactional / navigational)

2. ON-PAGE SEO CHECKLIST
   - 5 specific action items to improve the website's on-page SEO

3. CONTENT MARKETING PLAN
   - 3 blog post ideas with full titles and a one-line description each

4. SOCIAL MEDIA STRATEGY
   - Best platforms for this business and recommended posting frequency

5. LOCAL SEO TIPS
   - If the business targets a local or national area, give 3 local SEO actions
   - If global, give 3 international SEO tips instead

6. QUICK WINS — DO THESE THIS WEEK
   - 3 fast, specific actions the client can take immediately

Rules:
- Use CAPS for section headers
- Use numbered or lettered lists inside each section
- No markdown asterisks or hashtags
- Be specific to this client's business — do not give generic advice
- Keep tone professional but friendly
"""

    result = ask_groq(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2000,
    )
    return f"SEO_STRATEGY_READY\n{result}"


# ============================================================
#  MODE 3 — GENERATE FULL HTML WEBSITE  (5 inputs → full site)
# ============================================================

GEN_STEPS = [
    (
        "business_name",
        "What is the name of your business or website?",
    ),
    (
        "tagline",
        "Write a short tagline or description.\n(1-2 sentences explaining what you do and who you help)",
    ),
    (
        "pages_list",
        "Which pages / sections do you want?\n(e.g. Home, About, Services, Portfolio, Testimonials, Contact)",
    ),
    (
        "color_scheme",
        "Choose a color scheme:\n• Dark  • Light  • Blue  • Green  • Orange  • Purple\nOr describe your brand colors (e.g. navy blue and gold)",
    ),
    (
        "extra_sections",
        "Any special sections to include?\n(e.g. pricing table, FAQ, team, gallery, newsletter signup)\nType 'none' to skip.",
    ),
]


def _generate_start(session: dict) -> str:
    session["gen_step"] = 0
    session["gen_data"] = {}
    return (
        "⚡ Let's build your complete website!\n\n"
        "I'll ask 5 quick questions then generate a full, "
        "ready-to-download HTML website for you.\n\n"
        f"Question 1: {GEN_STEPS[0][1]}"
    )


def _generate_step(session: dict, message: str) -> str:
    step = session.get("gen_step", 0)
    data = session.setdefault("gen_data", {})

    if step < len(GEN_STEPS):
        key = GEN_STEPS[step][0]
        data[key] = message
        session["gen_step"] = step + 1

        if session["gen_step"] < len(GEN_STEPS):
            next_index    = session["gen_step"]
            next_question = GEN_STEPS[next_index][1]
            return f"Question {next_index + 1}: {next_question}"

        # All 5 answered → generate the website
        return _generate_full_website(data)

    # Website already generated → free-form follow-up
    return ask_groq(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful web developer assistant. "
                    "The user's website has already been generated. "
                    "Answer questions about it or suggest improvements clearly."
                ),
            },
            {"role": "user", "content": message},
        ],
        max_tokens=500,
    )


def _generate_full_website(data: dict) -> str:
    name    = data.get("business_name", "My Business")
    tagline = data.get("tagline",       "Welcome to our website")
    pages   = data.get("pages_list",    "Home, About, Services, Contact")
    colors  = data.get("color_scheme",  "Dark")
    extras  = data.get("extra_sections","none")

    prompt = f"""
You are a senior frontend web developer.
Generate a COMPLETE, BEAUTIFUL, PRODUCTION-READY single-page HTML website.

Business Details:
- Name          : {name}
- Tagline       : {tagline}
- Pages/Sections: {pages}
- Color Scheme  : {colors}
- Extra Sections: {extras}

STRICT REQUIREMENTS:
1.  Output a single HTML file — all CSS and JavaScript must be inline (no external files)
2.  Fully responsive — works perfectly on mobile, tablet, and desktop
3.  Sticky navigation bar with smooth scroll links to each section
4.  Hero section with a strong headline, subheadline, and a call-to-action button
5.  Each requested page becomes its own full section with real placeholder content
6.  Professional footer with business name, links, and copyright year
7.  Use Google Fonts — choose fonts that match the color scheme and style
8.  Smooth CSS animations: fade-in on scroll, hover effects on buttons and cards
9.  All placeholder content must sound real and professional (not "Lorem ipsum")
10. SEO meta tags in <head>: title, description, keywords, og:title, og:description
11. Use a clean, modern layout — cards, sections with alternating backgrounds
12. If extras include pricing: show 3 pricing tiers (Basic, Pro, Enterprise)
13. If extras include FAQ: show 5 realistic question-answer pairs
14. If extras include testimonials: show 3 realistic customer reviews with names
15. If extras include team: show 4 team member cards with name and role
16. Mobile hamburger menu that toggles navigation on small screens

OUTPUT RULES:
- Output ONLY the raw HTML code
- Do NOT include any explanation, commentary, or markdown code fences
- Do NOT start with ``` or end with ```
- Start directly with <!DOCTYPE html>

Generate the complete HTML website now:
"""

    html_code = ask_groq(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000,
    )

    # ── Clean up accidental markdown fences ─────────────────
    html_code = html_code.strip()

    if html_code.startswith("```"):
        # Remove opening fence (``` or ```html)
        first_newline = html_code.find("\n")
        if first_newline != -1:
            html_code = html_code[first_newline + 1:]
        else:
            html_code = html_code[3:]

    if html_code.endswith("```"):
        html_code = html_code[: html_code.rfind("```")]

    html_code = html_code.strip()

    # ── Safety check — make sure it looks like HTML ──────────
    if not html_code.lower().startswith("<!doctype") and "<html" not in html_code.lower():
        return (
            "⚠️ The website could not be generated correctly this time.\n\n"
            "Please try again — this sometimes happens with complex prompts.\n"
            "You can also try simplifying your page list or color scheme."
        )

    return f"WEBSITE_GENERATED\n{html_code}"