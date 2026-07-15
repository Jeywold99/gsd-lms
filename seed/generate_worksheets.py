"""
Generate the five branded student worksheets (PDF) for the 5-Day AI Strategist
Masterclass into seed/worksheets/.

Run once at build time (the generated PDFs ship with the repo and are attached
to lessons by `manage.py seed_courses`):

    python seed/generate_worksheets.py

Requires: pip install fpdf2  (dev-only dependency, not needed in production)
"""
from pathlib import Path

from fpdf import FPDF

HERE = Path(__file__).resolve().parent
OUT = HERE / "worksheets"
FONTS = HERE / "fonts"

ORANGE = (255, 92, 0)
OBSIDIAN = (26, 26, 26)
MIDNIGHT = (30, 30, 46)
CREAM = (245, 240, 235)
INK60 = (90, 90, 90)

PAGE_W = 210
MARGIN = 16
CONTENT_W = PAGE_W - 2 * MARGIN


class Worksheet(FPDF):
    def __init__(self, day, title, tagline):
        super().__init__(format="A4")
        self.day = day
        self.doc_title = title
        self.tagline = tagline
        self.set_margins(MARGIN, 18, MARGIN)
        self.set_auto_page_break(True, margin=22)
        self.add_font("Bebas", "", FONTS / "BebasNeue-Regular.ttf")
        self.add_font("Outfit", "", FONTS / "Outfit-Variable.ttf")
        self.add_font("Outfit", "B", FONTS / "Outfit-Variable.ttf")
        self.add_page()
        self._cover_header()

    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Outfit", "B", 8)
        self.set_text_color(*INK60)
        self.set_y(8)
        self.cell(0, 5, f"GET SH*T DONE HQ  ·  DAY {self.day} WORKSHEET", align="L")
        self.set_text_color(*ORANGE)
        self.cell(0, 5, "THE AI STRATEGIST MASTERCLASS", align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_y(18)

    def footer(self):
        self.set_y(-14)
        self.set_font("Outfit", "", 8)
        self.set_text_color(*INK60)
        self.cell(0, 5, "Complete every section, save as PDF, and upload it in the lesson to unlock the next day.", align="L")
        self.set_text_color(*ORANGE)
        self.cell(0, 5, f"PAGE {self.page_no()}", align="R")

    # ------------------------------------------------------------ building blocks
    def _cover_header(self):
        # Orange banner
        self.set_fill_color(*ORANGE)
        self.rect(0, 0, PAGE_W, 46, "F")
        self.set_xy(MARGIN, 9)
        self.set_font("Outfit", "B", 9)
        self.set_text_color(255, 232, 214)
        self.cell(0, 5, "GET SH*T DONE HQ  ·  THE AI STRATEGIST MASTERCLASS", new_x="LMARGIN", new_y="NEXT")
        self.set_x(MARGIN)
        self.set_font("Bebas", "", 30)
        self.set_text_color(255, 255, 255)
        self.cell(0, 13, f"DAY {self.day} WORKSHEET — {self.doc_title.upper()}", new_x="LMARGIN", new_y="NEXT")
        self.set_x(MARGIN)
        self.set_font("Outfit", "", 10)
        self.set_text_color(255, 255, 255)
        self.multi_cell(CONTENT_W, 5, self.tagline)
        self.set_y(52)
        # Name / date row
        self.set_font("Outfit", "B", 10)
        self.set_text_color(*OBSIDIAN)
        self.cell(24, 8, "NAME:")
        self._line_to(self.get_x() + 96)
        self.cell(100, 8, "")
        self.cell(16, 8, "DATE:")
        self._line_to(PAGE_W - MARGIN)
        self.ln(12)

    def _line_to(self, x_end):
        y = self.get_y() + 7
        self.set_draw_color(*OBSIDIAN)
        self.set_line_width(0.3)
        self.line(self.get_x(), y, x_end, y)

    def section(self, number, title, sub=None):
        if self.get_y() > 240:
            self.add_page()
        self.ln(3)
        y = self.get_y()
        self.set_fill_color(*ORANGE)
        self.rect(MARGIN, y, 2.2, 9, "F")
        self.set_xy(MARGIN + 6, y)
        self.set_font("Bebas", "", 17)
        self.set_text_color(*OBSIDIAN)
        self.cell(0, 9, f"{number}   {title.upper()}", new_x="LMARGIN", new_y="NEXT")
        if sub:
            self.set_x(MARGIN + 6)
            self.set_font("Outfit", "", 9.5)
            self.set_text_color(*INK60)
            self.multi_cell(CONTENT_W - 6, 4.6, sub)
        self.ln(2)

    def field(self, label, lines=2, line_gap=9):
        if self.get_y() + 6 + lines * line_gap > 272:
            self.add_page()
        self.set_font("Outfit", "B", 10)
        self.set_text_color(*OBSIDIAN)
        self.multi_cell(CONTENT_W, 5.4, label)
        self.set_draw_color(120, 120, 120)
        self.set_line_width(0.25)
        y = self.get_y() + line_gap - 3
        for _ in range(lines):
            self.line(MARGIN, y, PAGE_W - MARGIN, y)
            y += line_gap
        self.set_y(y - line_gap + 4)

    def checklist(self, items):
        self.set_font("Outfit", "", 10)
        self.set_text_color(*OBSIDIAN)
        for item in items:
            if self.get_y() > 265:
                self.add_page()
            y = self.get_y() + 1
            self.set_draw_color(*ORANGE)
            self.set_line_width(0.5)
            self.rect(MARGIN, y, 4, 4)
            self.set_xy(MARGIN + 7, y - 1.2)
            self.multi_cell(CONTENT_W - 7, 5.2, item)
            self.ln(1.5)

    def tip(self, text):
        if self.get_y() > 250:
            self.add_page()
        self.ln(1)
        y = self.get_y()
        self.set_fill_color(*CREAM)
        self.set_font("Outfit", "", 9.5)
        self.set_text_color(*MIDNIGHT)
        self.set_xy(MARGIN, y)
        self.multi_cell(CONTENT_W, 5.2, f"COACH'S NOTE — {text}", fill=True)
        self.ln(2)


def day1():
    pdf = Worksheet(
        1, "The AI Strategist Mindset",
        "Map the Claude ecosystem, then ship your first client-grade deliverable: "
        "a polished one-page content brief built from messy notes.",
    )
    pdf.section("01", "Know the map", "Write the job of each tool in your own words — one line each. If you can explain it, you own it.")
    for tool in ["Chat", "Projects", "Artifacts", "Skills", "Cowork", "Connectors"]:
        pdf.field(f"{tool}:", lines=1)
    pdf.section("02", "Match the tool to the job", "Which tool would you reach for? Write one of: Chat, Projects, Artifacts, Skills, Cowork, Connectors.")
    for q in [
        "You're tired of re-explaining the same client's brand voice every single time.",
        "You want the deliverable as a clean, editable document you can send.",
        "You want Claude to read your actual inbox instead of pasted copies.",
        "You want a whole folder of receipts turned into an expense summary while you supervise.",
        "You want a task done YOUR way, the same way, every time.",
    ]:
        pdf.field(q, lines=1)
    pdf.section("03", "The build — messy notes to client brief", "Do the Day 1 build in Claude, then record it here.")
    pdf.field("The opening line you gave Claude (role + audience):", lines=2)
    pdf.field("The sections you asked for in the brief (format):", lines=2)
    pdf.field("The one refinement you asked for — and what changed:", lines=2)
    pdf.checklist([
        "I pasted the messy notes without cleaning them first — that's Claude's job.",
        "The brief opened as an Artifact (a deliverable, not a chat).",
        "I created a Project called “My First Client” and saved the brief into it.",
        "I reviewed the output like a strategist before calling it done.",
    ])
    pdf.section("04", "Lock it in")
    pdf.field("Twenty minutes ago vs now: what's one thing you believed about AI that changed tonight?", lines=3)
    pdf.field("One task from your real work you'll hand to Claude this week:", lines=2)
    pdf.tip("Attach or paste your finished content brief when you upload this worksheet — the brief IS the win.")
    return pdf


def day2():
    pdf = Worksheet(
        2, "Prompt Mastery — The 10-Prompt Library",
        "A prompt is a brief, not a wish. Build two prompts per category with the 6-part framework "
        "(Role · Context · Task · Format · Constraints · Examples) and finish them with fill-in blanks.",
    )
    pdf.section("01", "The framework, from memory", "No peeking. Name the six parts of a professional prompt and what each removes guesswork about.")
    for i in range(1, 7):
        pdf.field(f"Part {i}:", lines=1)
    categories = [
        ("Email", "Replies, follow-ups, outreach, the awkward ones."),
        ("Research", "Summarize an article, competitor scan, explain a topic for a client."),
        ("Content", "Captions, blog outlines, repurpose one post into five."),
        ("Admin / Ops", "Minutes from messy notes, SOP drafting, transcript to action items."),
        ("Reporting", "The weekly client update, raw numbers to plain English."),
    ]
    for idx, (name, sub) in enumerate(categories, start=2):
        pdf.section(f"{idx:02d}", f"Category — {name}", sub + " Write both prompts in full, with [fill-in] blanks.")
        pdf.field("Prompt 1:", lines=4)
        pdf.field("Prompt 2:", lines=4)
    pdf.section("07", "Quality check")
    pdf.checklist([
        "Every prompt names a Role and gives real Context (the two most-skipped parts).",
        "Every prompt asks for ONE task with a precise verb.",
        "Every prompt names its output Format.",
        "Every prompt has at least two [fill-in] blanks so it works for any client.",
        "I saved the finished library where I'll actually reuse it (doc or Project).",
    ])
    pdf.field("Which prompt will you use FIRST tomorrow, on what real task?", lines=2)
    pdf.tip("There's no single right prompt — only clear vs vague. Copying the demo and changing the specifics is a legitimate first step.")
    return pdf


def day3():
    pdf = Worksheet(
        3, "Your First Automation",
        "Automation = work that happens on a trigger instead of on your time. "
        "Design it as Trigger → Brain → Action, run it once, and keep yourself in the loop.",
    )
    pdf.section("01", "Map the manual workflow", "You can't automate what you can't describe. Pick one repetitive task (email triage is tonight's build) and write how you do it by hand today, step by step.")
    pdf.field("The task I'm automating:", lines=1)
    pdf.field("How I currently do it manually (every step):", lines=4)
    pdf.field("Roughly how much time it eats per week:", lines=1)
    pdf.section("02", "Design it — Trigger / Brain / Action")
    pdf.field("TRIGGER — what kicks it off:", lines=1)
    pdf.field("BRAIN — the full instruction you give Claude (yes, it's a 6-part prompt — Day 2 pays off here):", lines=5)
    pdf.field("ACTION — where the result goes (remember: draft for approval, never auto-send):", lines=2)
    pdf.section("03", "Connect and run")
    pdf.checklist([
        "I connected the app(s) — authorized the connector or pasted the API key.",
        "The API key moment happened and nobody had to write code.",
        "I ran the automation once, end to end.",
        "The output landed as a DRAFT for my approval — human-in-the-loop, always.",
    ])
    pdf.field("What the first run produced (and one thing you fixed after it):", lines=3)
    pdf.section("04", "The strategist's answer", "A client asks: “So is the AI just sending emails as you?” Write the answer that keeps their trust.")
    pdf.field("Your answer:", lines=2)
    pdf.field("Next automation you'd build with the same Trigger → Brain → Action shape:", lines=2)
    pdf.tip("If your plan gates you from running it live tonight, design everything here and execute from the replay — the design IS the skill.")
    return pdf


def day4():
    pdf = Worksheet(
        4, "Build a Demo-Ready Agent",
        "An agent pursues a goal: you own the WHAT, it works out the HOW. "
        "Skills are the training, Connectors are the hands, Cowork is the worker.",
    )
    pdf.section("01", "The three-way distinction", "One sentence each, your own words.")
    pdf.field("Chat is…", lines=1)
    pdf.field("An automation is…", lines=1)
    pdf.field("An agent is…", lines=1)
    pdf.section("02", "Define the goal, not the steps", "A vague goal produces wandering work — same discipline as a good prompt.")
    pdf.field("My agent's goal statement (outcome, not steps):", lines=2)
    pdf.field("Who this is for / the client scenario it demos:", lines=2)
    pdf.section("03", "Assemble it")
    pdf.field("SKILL (the training) — the method it must follow, promoted from your Day 2 work:", lines=4)
    pdf.field("CONNECTORS / FILES (the hands) — what it needs access to:", lines=2)
    pdf.field("WORKER — where it runs (Cowork or your setup tonight):", lines=1)
    pdf.section("04", "Run, review, correct", "Let it run. Then do the strategist's job.")
    pdf.checklist([
        "I watched it work through a SEQUENCE of steps, not just one answer.",
        "I reviewed the output before accepting it — the review step IS the job.",
        "I corrected at least one thing and ran it again.",
        "I saved the assembly so I can rerun it for any future client.",
    ])
    pdf.field("What it produced, and the one correction you made:", lines=3)
    pdf.section("05", "The portfolio line")
    pdf.field("Finish the sentence you'll say to a prospect: “I built an AI agent that…”", lines=2)
    pdf.field("(Optional — AI team upgrade) Which two specialists would you chain, and who hands off to whom?", lines=2)
    pdf.tip("The agent handles volume. You handle judgment. That's why you're the strategist — and tomorrow this build gets a name and a price.")
    return pdf


def day5():
    pdf = Worksheet(
        5, "Offer, Pricing & Pitch",
        "Graduation night. The skill makes you capable — the positioning makes you chosen. "
        "Package what you built, price it on ROI, and send one pitch within 48 hours.",
    )
    pdf.section("01", "Rewrite your positioning", "From job title to outcome. Specific gets hired; general gets scrolled past.")
    pdf.field("Old headline (what your profile says today):", lines=1)
    pdf.field("New positioning line — “I help [who] get [result] using AI and automation”:", lines=2)
    pdf.field("Your proof — which of this week's builds gets pinned to your profile?", lines=1)
    pdf.section("02", "Name your offer", "Pick ONE build from the week (prompt system, automation, agent) and package it. You're not inventing — you're naming what you already made.")
    pdf.field("1 · Name — “The ______ System”:", lines=1)
    pdf.field("2 · Who it's for:", lines=1)
    pdf.field("3 · The outcome it delivers:", lines=2)
    pdf.field("4 · What's included:", lines=3)
    pdf.field("5 · The price:", lines=1)
    pdf.section("03", "Price it with the ROI frame")
    pdf.field("Hours per week this saves the client:", lines=1)
    pdf.field("What that time is worth to them (per month):", lines=1)
    pdf.field("Your price, anchored to that value — write the number. Then practice saying it out loud, followed by silence:", lines=1)
    pdf.section("04", "Draft the pitch", "Problem → Proof → Offer → CTA. Aim it at a real person.")
    pdf.field("PROBLEM — the pain you lead with:", lines=2)
    pdf.field("PROOF — the build you'll show (“happy to demo it live”):", lines=2)
    pdf.field("OFFER — one clear package:", lines=2)
    pdf.field("CTA — one clear ask:", lines=1)
    pdf.section("05", "The 48-hour commitment")
    pdf.field("WHO receives this pitch (a real name — warm contacts first):", lines=1)
    pdf.field("WHEN you'll send it (within 48 hours — date and time):", lines=1)
    pdf.checklist([
        "My positioning line names one WHO and one RESULT.",
        "My offer has all five parts, including a price I didn't apologize for.",
        "My pitch leads with the client's problem, not my biography.",
        "I committed to the send — publicly, in the crew.",
    ])
    pdf.tip("Five days ago some of you were nervous to open Claude. Tonight you have a skill, a portfolio, an offer, and a pitch. Go get sh*t done.")
    return pdf


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for day, build in [(1, day1), (2, day2), (3, day3), (4, day4), (5, day5)]:
        pdf = build()
        path = OUT / f"Day{day}-Worksheet.pdf"
        pdf.output(str(path))
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
