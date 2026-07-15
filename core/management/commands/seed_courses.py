"""
Seed the five GSD HQ courses.

The 5-Day AI Strategist Masterclass goes live with its real lessons and
worksheets; the other four offers are created as draft ("coming soon")
records so their content can be added later with zero rework.

Idempotent: safe to run on every deploy. Existing video URLs, release dates
and uploaded worksheets are never overwritten.
"""
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from core.models import Course, Lesson

SEED_WORKSHEETS = Path(settings.BASE_DIR) / "seed" / "worksheets"

COURSES = [
    {
        "slug": "ai-strategist-masterclass",
        "title": "The 5-Day AI Strategist Masterclass",
        "tagline": "Five days. One skill stack. Go from generalist VA to the AI Strategist clients pay a premium for.",
        "description": (
            "Every day is hands-on: you build alongside, ship one tangible win, and unlock the "
            "next day by completing the worksheet. By Day 5 you leave with a prompt library, a "
            "working automation, a demo-ready agent, and an offer you can pitch."
        ),
        "status": Course.Status.LIVE,
        "order": 1,
    },
    {
        "slug": "personal-branding-2026",
        "title": "Personal Branding in 2026",
        "tagline": "Positioning first, content second. Become the one thing the right client is looking for.",
        "description": "Full course coming soon.",
        "status": Course.Status.DRAFT,
        "order": 2,
    },
    {
        "slug": "ai-and-automation",
        "title": "AI and Automation",
        "tagline": "Stop selling hours. Build systems that do the work on a trigger instead of on your time.",
        "description": "Full course coming soon.",
        "status": Course.Status.DRAFT,
        "order": 3,
    },
    {
        "slug": "conversion",
        "title": "Conversion",
        "tagline": "Turn attention into action — pages, offers, and follow-ups that actually close.",
        "description": "Full course coming soon.",
        "status": Course.Status.DRAFT,
        "order": 4,
    },
    {
        "slug": "sales-psychology",
        "title": "Sales Psychology",
        "tagline": "Understand why people buy, so you never have to push.",
        "description": "Full course coming soon.",
        "status": Course.Status.DRAFT,
        "order": 5,
    },
]

LESSONS = [
    {
        "order": 1,
        "slug": "day-1-ai-strategist-mindset",
        "title": "Day 1 — The AI Strategist Mindset + Claude Ecosystem",
        "worksheet": "Day1-Worksheet.pdf",
        "objectives": (
            "Understand the AI Strategist role — the person who runs the AI, not the one replaced by it\n"
            "Map the whole Claude ecosystem: Chat, Projects, Artifacts, Skills, Cowork, Connectors\n"
            "Know which tool to reach for, and when\n"
            "Ship your first client-grade deliverable: a polished one-page content brief from messy notes"
        ),
        "content": """
<h2>The mindset shift</h2>
<p>The person who uses AI will replace the person who refuses to. Tonight you become the first kind.
Clients aren't looking for programmers — they're looking for someone who can direct AI to produce
client-quality work reliably, and who knows when the output is good enough to send. That person is
the <strong>AI Strategist</strong>. That's the identity this week builds, and Day 5 teaches you to
charge for it.</p>

<h2>The map: six tools, one sentence</h2>
<p>You talk in <strong>Chat</strong>, you organize by client in <strong>Projects</strong>, Claude hands
you deliverables as <strong>Artifacts</strong>, you teach it your method with <strong>Skills</strong>,
it does whole jobs in <strong>Cowork</strong>, and it plugs into your other apps through
<strong>Connectors</strong>.</p>
<ul>
<li><strong>Chat</strong> — the workbench. Within one conversation Claude remembers everything said so far.
But every new chat starts fresh — so keep one task per chat.</li>
<li><strong>Projects</strong> — labeled drawers per client. Custom instructions (standing rules) plus
knowledge files (brand guide, past work) mean you explain the client once, then every chat already knows.</li>
<li><strong>Artifacts</strong> — the finished piece beside the chat. That's the thing you'd actually send
a client: editable, iterable, downloadable.</li>
<li><strong>Skills</strong> — a saved procedure that teaches Claude to do a task <em>your way</em>, every
time. A Project is <em>where</em> you work; a Skill is <em>how</em> a task gets done.</li>
<li><strong>Cowork</strong> — the desktop app where Claude completes whole multi-step jobs on your real
files while you supervise the result. We use it on Day 3 — don't buy anything tonight.</li>
<li><strong>Connectors</strong> — secure, revocable links to Gmail, Drive, Calendar, Notion, Slack. The
backbone of Day 3's automations.</li>
</ul>
<p>You don't need all six to start earning. You need the map, so nothing this week feels random.</p>

<h2>The build: messy notes → client-grade brief</h2>
<p>In the session we turn a client's messy dump into a polished one-page content brief — a real
deliverable you could bill for. The steps, and what each teaches:</p>
<ol>
<li><strong>Set the context.</strong> Tell Claude who it is and who the work is for before the task.
Context is the difference between generic and client-ready.</li>
<li><strong>Paste the raw material.</strong> You don't clean input — that's Claude's job.</li>
<li><strong>Specify the format.</strong> Name the sections you want (Objective, Target Audience, Key
Messages, Deliverables, Tone, Offer/CTA). Vague ask = vague result.</li>
<li><strong>Watch it land as an Artifact.</strong> That's a deliverable, not a chat.</li>
<li><strong>Refine live.</strong> First output is a draft. Iterating is the skill — and it's easy.</li>
<li><strong>Save it into a Project.</strong> Create "My First Client" and drop the brief in.</li>
</ol>

<h2>Watch-outs</h2>
<ul>
<li>Output too generic? You skipped context or format. Fix that step — don't just re-roll.</li>
<li>Yours looks different from the demo? Expected. Different isn't wrong; this is Day 1.</li>
<li>Always review before you'd send anything to a client. Claude drafts, the human verifies —
that's part of what clients pay you for.</li>
</ul>

<h2>Your move</h2>
<p>Download the Day 1 worksheet below, complete the build, and upload it. Day 2 unlocks
when it's approved. Twenty minutes from now you'll have turned a messy dump into a brief you
could charge for — that's the entire job, and it only gets bigger from here.</p>
""",
    },
    {
        "order": 2,
        "slug": "day-2-prompt-mastery",
        "title": "Day 2 — Prompt Mastery + Client-Grade Deliverables",
        "worksheet": "Day2-Worksheet.pdf",
        "objectives": (
            "Internalize the core truth: a prompt is a brief, not a wish\n"
            "Master the 6-part framework: Role, Context, Task, Format, Constraints, Examples\n"
            "Turn one-off prompts into reusable templates with fill-in blanks\n"
            "Build your 10-prompt library across the five services clients actually pay for"
        ),
        "content": """
<h2>A prompt is a brief, not a wish</h2>
<p>When "write a follow up email" comes back generic, the model didn't fail — the brief did. Claude
responds to exactly what you give it; every detail you leave out is a decision it has to guess at, and
guesses average toward generic. You already know how to brief a human assistant. Tonight you learn
that briefing a model is the same discipline with a more literal recipient.</p>

<h2>The 6-part framework</h2>
<ol>
<li><strong>Role</strong> — assign a perspective: "You are my email assistant for a real-estate client."
The cheapest quality boost there is.</li>
<li><strong>Context</strong> — the background it can't know: who the client is, who the audience is,
the goal. The part beginners skip most, and the one that matters most.</li>
<li><strong>Task</strong> — one specific action. Precise verbs ("write", "summarize", "rewrite")
beat vague ones ("help with", "do").</li>
<li><strong>Format</strong> — the shape of the output: sections, length, bullets vs paragraphs,
subject line. Naming the structure is what makes output look professional.</li>
<li><strong>Constraints</strong> — tone, word count, things to avoid. This is where brand voice lives.</li>
<li><strong>Examples</strong> — show one sample of "good". The most powerful and most underused lever:
the model imitates patterns far better than descriptions.</li>
</ol>
<p>Two habits that separate practitioners from tourists: when output misses, fix the weakest part
(usually context or format) instead of starting over — and remember longer isn't better,
<em>clearer</em> is. Cut every word that doesn't remove ambiguity.</p>

<h2>The reusability move</h2>
<p>A prompt written once for one client is a note; a prompt with blanks is an asset. Generalize your
best prompts with <code>[client]</code>, <code>[audience]</code>, <code>[tone]</code>,
<code>[offer]</code> — one well-built prompt then serves every client you'll ever have.</p>

<h2>The build: your 10-prompt library</h2>
<p>Fill a five-section library with two prompts per category, each built with the framework and
finished with fill-in blanks:</p>
<ul>
<li><strong>Email</strong> — replies, follow-ups, outreach, the awkward ones.</li>
<li><strong>Research</strong> — summarize an article, competitor scan, "explain this for a client".</li>
<li><strong>Content</strong> — captions, blog outlines, repurpose one post into five.</li>
<li><strong>Admin / Ops</strong> — minutes from messy notes, SOP drafting, transcript → action items.</li>
<li><strong>Reporting</strong> — the weekly update, raw numbers → plain-English summary.</li>
</ul>
<p>Copying the demo prompt and changing the specifics is a legitimate first step. There's no single
right prompt — only clear vs vague.</p>

<h2>Your move</h2>
<p>Complete the Day 2 worksheet — your full 10-prompt library — and upload it. Most freelancers
never build this. You'll have it tonight, and you'll paste from it for years.</p>
""",
    },
    {
        "order": 3,
        "slug": "day-3-ai-automations",
        "title": "Day 3 — AI Automations for Real Workflows",
        "worksheet": "Day3-Worksheet.pdf",
        "objectives": (
            "Make the shift from doing tasks faster to designing systems that run without you\n"
            "Read any automation as Trigger → Brain → Action\n"
            "Use connectors and APIs without fear — connect an app, paste a key, done\n"
            "Ship one working automation: email triage with drafted replies, human-approved"
        ),
        "content": """
<h2>From doing to designing</h2>
<p>Days 1–2 were Claude helping you do a task. Tonight Claude does the task <em>without you sitting
there</em>. Automation = work that happens on a trigger instead of on your time. This is the shift
from selling hours to owning systems — and it's exactly what clients pay a premium for.</p>

<h2>The universal anatomy: Trigger → Brain → Action</h2>
<p>Every automation, in every tool, is three parts:</p>
<ul>
<li><strong>Trigger</strong> — what kicks it off: a new email arrives, a form is submitted, it's 9am Monday.</li>
<li><strong>Brain</strong> — Claude does the thinking: read this, categorize it, draft a reply, summarize it.</li>
<li><strong>Action</strong> — the result goes somewhere: a draft saved, a row added, a message posted.</li>
</ul>
<p>Here's the connection that makes the week cohere: <strong>the brain step is a prompt.</strong> The
instruction that tells Claude what to do with each email is the same 6-part framework from Day 2.
Automation isn't a new skill — it's prompting installed into a pipeline.</p>

<h2>APIs without fear</h2>
<p>An API is a doorway that lets two apps talk to each other automatically. In no-code automation,
"using APIs" means two mundane actions: clicking "authorize" to connect an app, and occasionally
pasting an <strong>API key</strong> — a special password proving you're allowed to make the
connection. Generate it, paste it once, done. You're not writing code; you're plugging apps into
each other and letting Claude be the brain in the middle.</p>

<h2>Connectors vs Cowork</h2>
<p>A connector automation is a <em>train on rails</em>: a defined route, utterly repeatable, runs
itself. Cowork is a <em>driver with a destination</em>: hand it a whole messy job ("go through this
folder and build me an expense summary") and it plans the steps itself while you review the result.
Recurring and predictable belongs on rails; messy and multi-step belongs with the driver.
(Cowork needs the Pro plan — if that's not you yet, build along from the replay. Expected and fine.)</p>

<h2>The build: email triage that drafts your replies</h2>
<ol>
<li><strong>Map your manual workflow first.</strong> You can't automate what you can't describe.</li>
<li><strong>Name the trigger.</strong> "A new unread email arrives."</li>
<li><strong>Write the brain.</strong> "Categorize as lead / admin / ignore, draft a warm reply for
leads" — a 6-part prompt.</li>
<li><strong>Connect the apps.</strong> Authorize Gmail; paste the key if you're in a no-code tool.</li>
<li><strong>Set the action: save as draft.</strong> Never auto-send. The automation prepares —
<strong>you approve</strong>. That's the professional standard that keeps a client's trust.</li>
<li><strong>Run it once, fix one thing.</strong> Automations are tuned into reliability, not born perfect.</li>
</ol>

<h2>Your move</h2>
<p>Complete the Day 3 worksheet — your workflow map, your trigger-brain-action design, and your run
log — and upload it. You just built a system that works while you sleep. That's the difference
between selling your hours and selling your systems.</p>
""",
    },
    {
        "order": 4,
        "slug": "day-4-ai-agents",
        "title": "Day 4 — Build AI Agents for Client Work",
        "worksheet": "Day4-Worksheet.pdf",
        "objectives": (
            "Nail the three-way distinction: chat vs automation vs agent\n"
            "Assemble an agent from pieces you already own: Skills (training), Connectors (hands), Cowork (worker)\n"
            "Design an AI team — narrow specialists beat one overloaded generalist\n"
            "Build the demo-ready agent that becomes your portfolio centerpiece"
        ),
        "content": """
<h2>What an agent actually is</h2>
<p>An agent is the jump from "AI that responds" to "AI that pursues a goal." You name the outcome;
it plans the steps, uses tools, adapts to what it finds, and works until the job is done.</p>
<p>The three-way distinction — the heart of tonight:</p>
<ul>
<li><strong>Chat</strong> — you ask, it answers. You drive every step. (Days 1–2.)</li>
<li><strong>Automation</strong> — a fixed trigger→action route, the same every time. A train on rails. (Day 3.)</li>
<li><strong>Agent</strong> — you give a destination; it picks the route and handles the detours.
A driver, not a train.</li>
</ul>
<p>Neither is better — they suit different work. Predictable and recurring belongs on rails;
variable and multi-step belongs with the driver.</p>

<h2>What it's made of</h2>
<p>For a non-developer, an agent isn't something you program — it's an assembly of pieces you built
this week: <strong>Skills are the training, Connectors are the hands, Cowork is the worker.</strong>
"Build an agent" means combining Tuesday's prompt library with Wednesday's connections. Every night
was quietly manufacturing a component of tonight.</p>

<h2>The AI team</h2>
<p>Instead of one do-everything agent, chain narrow specialists: a research step gathers, a writing
step drafts, a QA step checks against the client's standards. Focused instructions produce focused
work, and a dedicated QA pass catches what a generalist misses. The line for client conversations:
"I don't run one AI — I run a small AI team with a quality-control layer."</p>

<h2>Human in the loop — as identity</h2>
<p>Agents produce volume; <strong>you supply judgment.</strong> Taste, context, the client
relationship, the final quality call — that last mile is what clients pay a premium for, and no agent
covers it. The agent handles volume. You handle judgment. That's why you're the strategist, not the
one being replaced. (And agents work within the task, tools, and permissions you give them — scoped
and supervised, not loose in the world.)</p>

<h2>The build: a demo-ready agent</h2>
<ol>
<li><strong>Define the goal, not the steps.</strong> "Take a client brief and produce a week of
on-brand social posts." You own the <em>what</em>; the agent works out the <em>how</em>.</li>
<li><strong>Encode your method as a Skill.</strong> Your Day 2 voice rules and formats become the
agent's training.</li>
<li><strong>Connect its tools.</strong> The brief, the destination doc — connectors are the hands.</li>
<li><strong>Let it run.</strong> Watch a sequence of work — reading, drafting, formatting, checking —
execute without you driving each move.</li>
<li><strong>Review and correct one thing.</strong> The agent produces; the strategist decides.</li>
<li><strong>Save it as reusable.</strong> A service you run again for every future client.</li>
</ol>

<h2>Your move</h2>
<p>Complete the Day 4 worksheet — your agent's goal statement, method, tools, and run review — and
upload it. What you built tonight is something you can put in front of a client and say "I made
this." Tomorrow it gets a name and a price.</p>
""",
    },
    {
        "order": 5,
        "slug": "day-5-brand-offer-pitch",
        "title": "Day 5 — Personal Brand 2026 + Packaging, Pricing & Landing Clients",
        "worksheet": "Day5-Worksheet.pdf",
        "objectives": (
            "Rewrite your positioning from job title to outcome\n"
            "Package one of this week's builds into a named, productized offer\n"
            "Price with the ROI frame — name the number, then stop talking\n"
            "Draft the pitch (problem → proof → offer → CTA) and commit to sending one in 48 hours"
        ),
        "content": """
<h2>The night the skill becomes a business</h2>
<p>Four nights built capability. Capability without positioning stays invisible and underpaid.
Tonight converts the week into income: a name, a package, a price, and a path to the people who'll
pay. The skill makes you capable — <strong>the positioning makes you chosen.</strong></p>

<h2>Personal branding in 2026, stripped of the fluff</h2>
<p>A brand isn't a logo or an aesthetic — it's <strong>positioning</strong>: the one specific thing
you're known for, stated so clearly the right client recognizes themselves instantly. "Virtual
assistant" is a category; "I help e-commerce founders reclaim ten hours a week with AI-run inbox and
reporting systems" is a position. Specific gets hired; general gets scrolled past.</p>
<p>The second rule: <strong>proof over claims.</strong> "I know AI" is noise — everyone says it. The
automation and the agent you built this week, shown, is signal. Rewrite the profile: headline from
job title to outcome, bio leading with the client's problem, pinned item = your proof.</p>

<h2>Packaging: from skill to productized offer</h2>
<p>Hourly billing caps your income and punishes the efficiency you just gained — when AI collapses an
hour's task to five minutes, the hourly biller earns one-twelfth as much. The escape is the
productized offer. Its anatomy, five parts:</p>
<ol>
<li><strong>Name</strong> — "The AI Inbox System"</li>
<li><strong>Who it's for</strong> — "coaches and consultants drowning in email"</li>
<li><strong>Outcome</strong> — "inbox triaged and replies drafted daily; reclaim an hour a day"</li>
<li><strong>What's included</strong> — setup, your custom reply voice, two weeks of tuning, handoff guide</li>
<li><strong>Price</strong></li>
</ol>
<p>You're not inventing an offer tonight — you're <strong>naming what you already built</strong>.
Monday through Thursday was product development; you just didn't know it at the time.</p>

<h2>Pricing: the fear and the frame</h2>
<p>Anchor to ROI, not effort. If your automation saves a client five hours a week, price against that
recovered value — not the afternoon the setup took. The efficiency AI gives you is yours to keep as
margin. And the behavioral half: <strong>name the number, then stop talking.</strong> Apologizing,
justifying, or pre-discounting signals doubt, and clients price doubt accordingly.</p>

<h2>Landing clients: the pitch</h2>
<p>Warmest market first: existing and past clients ("I've added AI systems to what I do — here's what
that could look like for you"). The pitch shape is the same discipline as a good prompt:
<strong>problem → proof → offer → call to action.</strong> Most freelancers pitch with adjectives.
You pitch with a working system they can watch run. That asymmetry closes.</p>

<h2>Your move</h2>
<p>Complete the Day 5 worksheet — positioning line, full offer anatomy with a price, and your drafted
pitch — and upload it. Then the real assignment: <strong>send one pitch within 48 hours.</strong>
Five days ago some of you were nervous to even open Claude. Tonight you have a skill, a portfolio,
an offer, and a pitch. Now go get sh*t done.</p>
""",
    },
]


class Command(BaseCommand):
    help = "Seed the five GSD courses (Masterclass live with lessons; others as drafts)."

    def handle(self, *args, **options):
        for data in COURSES:
            course, created = Course.objects.update_or_create(
                slug=data["slug"],
                defaults={k: v for k, v in data.items() if k != "slug"},
            )
            self.stdout.write(f"{'Created' if created else 'Updated'} course: {course.title}")

        masterclass = Course.objects.get(slug="ai-strategist-masterclass")
        previous = None
        for data in LESSONS:
            lesson, created = Lesson.objects.update_or_create(
                course=masterclass,
                slug=data["slug"],
                defaults={
                    "order": data["order"],
                    "title": data["title"],
                    "objectives": data["objectives"],
                    "content": data["content"].strip(),
                },
            )
            # Chain the gate: each lesson requires the previous one approved.
            if lesson.prerequisite_id != (previous.pk if previous else None):
                lesson.prerequisite = previous
                lesson.save(update_fields=["prerequisite"])

            # Attach the seeded worksheet PDF unless an admin already uploaded one.
            seed_pdf = SEED_WORKSHEETS / data["worksheet"]
            if not lesson.worksheet_file and seed_pdf.exists():
                with seed_pdf.open("rb") as fh:
                    lesson.worksheet_file.save(data["worksheet"], File(fh), save=True)
                self.stdout.write(f"  attached worksheet {data['worksheet']}")

            self.stdout.write(f"{'Created' if created else 'Updated'} lesson: {lesson.title}")
            previous = lesson

        self.stdout.write(self.style.SUCCESS("Seed complete."))
