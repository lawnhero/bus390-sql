"""Shared UI components for the BUS 390 SQL Virtual TA.

Markdown helpers, route provenance metadata, status/badge/feedback renderers,
starter prompts, and quick-action chips. All course-facing strings live here.
"""

import streamlit as st

TA_AVATAR = ":material/school:"
TA_NAME = "Peyton"

INSTRUCTOR_NAME = "Dr. Wenjun Gu"
INSTRUCTOR_EMAIL = "wenjun.gu@emory.edu"
COURSE_LABEL = "BUS 390 · SQL Toolkit"

# ---------------------------------------------------------------------------
# Markdown helpers
# ---------------------------------------------------------------------------

def escape_md_dollars(text: str) -> str:
    """Escape $ so Streamlit markdown does not treat it as LaTeX."""
    if not text:
        return text
    placeholder = ""
    protected = text.replace("\\$", placeholder)
    return protected.replace("$", "\\$").replace(placeholder, "\\$")


def md(text, container=None):
    (container or st).markdown(escape_md_dollars(text))


def write_stream_md(stream, container=None):
    """Stream LLM tokens into one placeholder, escaping $ as we go."""
    placeholder = (container or st).empty()
    chunks = []
    for chunk in stream:
        text = chunk if isinstance(chunk, str) else getattr(chunk, "content", None) or str(chunk)
        chunks.append(text)
        placeholder.markdown(escape_md_dollars("".join(chunks)))
    return "".join(chunks)


# ---------------------------------------------------------------------------
# Route provenance: three tenses of the same fact, from one table
# ---------------------------------------------------------------------------
# Color semantics: blue = grounded in course materials, violet = model's SQL
# knowledge, green = generated practice, gray = no lookup, orange = fallback.

ROUTE_META = {
    "course": {
        "working": "Looking through the course materials",
        "done": "Checked the course materials",
        "badge": "Course materials",
        "icon": ":material/menu_book:",
        "color": "blue",
        "help": "Answered from the syllabus and course content for BUS 390.",
    },
    "explain": {
        "working": "Writing a plain-English explanation",
        "done": "Explained the concept",
        "badge": "SQL explanation",
        "icon": ":material/lightbulb:",
        "color": "violet",
        "help": "A general SQL explanation from the tutor's knowledge, with a business example.",
    },
    "exercise": {
        "working": "Building a practice question for you",
        "done": "Built a practice question",
        "badge": "Practice question",
        "icon": ":material/quiz:",
        "color": "green",
        "help": "A practice question generated for you. Try it before asking for the answer.",
    },
    "debug": {
        "working": "Reading your SQL and the error",
        "done": "Reviewed your SQL",
        "badge": "Debugging help",
        "icon": ":material/build:",
        "color": "violet",
        "help": "Debugging suggestions based on the SQL and error you shared.",
    },
    "chat": {
        "working": "Thinking about your message",
        "done": "Answered directly",
        "badge": "General chat",
        "icon": ":material/chat:",
        "color": "gray",
        "help": "A conversational reply — no course lookup was needed.",
    },
    "fallback": {
        "working": "Trying a general answer",
        "done": "Answered without a course lookup",
        "badge": "Not from course materials",
        "icon": ":material/warning:",
        "color": "orange",
        "help": "Something went wrong with the usual route, so this is a general answer. "
                "Double-check it against the course materials.",
    },
}
DEFAULT_ROUTE = "chat"


def route_meta(label):
    return ROUTE_META.get(label or "", ROUTE_META[DEFAULT_ROUTE])


def working_label(route_label):
    return route_meta(route_label)["working"]


def completion_label(route_label, *, seconds=0.0):
    parts = [route_meta(route_label)["done"]]
    if seconds:
        parts.append(f"{seconds:.1f}s")
    return " · ".join(parts)


# ---------------------------------------------------------------------------
# Per-message renderers (replayed from message_meta on every rerun)
# ---------------------------------------------------------------------------

def render_progress(record):
    if not record:
        return
    st.status(
        record.get("label") or "Answer complete",
        state=record.get("state") or "complete",
        type="compact",
        expanded=False,
    )


def render_provenance(route_label):
    meta = route_meta(route_label)
    st.badge(meta["badge"], icon=meta["icon"], color=meta["color"], help=meta["help"])


def render_answer_footer(route_label, *, trailing=None):
    """One horizontal line under the answer: badge · feedback thumbs."""
    with st.container(horizontal=True, vertical_alignment="center", gap="small"):
        render_provenance(route_label)
        if trailing is not None:
            trailing()


# ---------------------------------------------------------------------------
# Feedback thumbs — callback, no extra rerun
# ---------------------------------------------------------------------------

def _record_feedback(store_feedback, interaction_id, key):
    value = st.session_state.get(key)
    if value is None:
        return
    try:
        store_feedback(interaction_id=interaction_id,
                       helpful="Helpful" if value == 1 else "Not helpful")
    except Exception:
        pass  # never let feedback logging break a student's session
    st.session_state.setdefault("feedback_submitted_ids", []).append(interaction_id)
    st.toast("Thanks — that helps improve the tutor.", icon=":material/favorite:")


def feedback_widget(interaction_id, store_feedback):
    """Return a callable that draws the thumbs, for use as a footer `trailing`."""
    if not interaction_id:
        return None

    def draw():
        submitted = st.session_state.get("feedback_submitted_ids", [])
        if interaction_id in submitted:
            st.caption("Rating recorded.")
            return
        key = f"feedback_{interaction_id}"
        st.feedback("thumbs", key=key, on_change=_record_feedback,
                    args=(store_feedback, interaction_id, key))

    return draw


# ---------------------------------------------------------------------------
# Starter prompts, quick actions, curriculum
# ---------------------------------------------------------------------------
# Every starter must be answerable by the current chains — a first click that
# flops is worse than none. Pitched at M0/M1, where a new student starts.

STARTER_PROMPTS = [
    "What do rows, columns, and grain mean in a table?",
    "What does SELECT * actually do?",
    "How do I filter rows with WHERE?",
    "Give me an easy practice question on filtering",
]

# The nine toolkit modules — one source of truth that drives the topic pills,
# the sidebar outline, and the curriculum block in the LLM prompts, so they
# can never disagree.
MODULES = [
    {"code": "M0", "title": "Tables & first query",
     "covers": "rows, columns, and grain; your first SELECT *"},
    {"code": "M1", "title": "Choosing & filtering",
     "covers": "SELECT, WHERE, AND/OR with numbers, text, and dates"},
    {"code": "M2", "title": "Sorting & shaping",
     "covers": "ORDER BY, LIMIT, DISTINCT, LIKE"},
    {"code": "M3", "title": "Calculations & totals",
     "covers": "arithmetic, aliases, COUNT/SUM/AVG/MIN/MAX"},
    {"code": "M4", "title": "Grouping",
     "covers": "GROUP BY, the grain of the result, HAVING"},
    {"code": "M5", "title": "Inner joins",
     "covers": "why tables are split; JOIN ... ON with two tables"},
    {"code": "M6", "title": "Left joins & missing rows",
     "covers": "LEFT JOIN, IS NULL, questions like \"customers who never ordered\""},
    {"code": "M7", "title": "Joins + groups together",
     "covers": "the synthesis pattern: join first, then group"},
    {"code": "M8", "title": "Capstone check",
     "covers": "business questions on an unseen dataset, mixing every topic"},
]

# Topic pills: M0–M7 are learnable topics; the capstone becomes a mixed-review pill.
TOPICS = [m["title"] for m in MODULES[:-1]] + ["Capstone prep (mix of everything)"]

# Injected into the explain/exercise system prompts so the TA teaches to the
# module ladder instead of wandering beyond course scope.
CURRICULUM_PROMPT = (
    "The course is a nine-module SQLite toolkit for business students with no "
    "prior coding experience. The modules, in learning order:\n"
    + "\n".join(f"- {m['code']} {m['title']}: {m['covers']}" for m in MODULES)
)

# Intent chips: "query" sends value directly; "intent" starts a clarifying turn.
QUICK_ACTIONS = [
    {"label": "Explain a concept", "icon": ":material/menu_book:", "kind": "intent",
     "value": "explain", "needs": "topic",
     "clarify": "Happy to explain! Pick a topic below, or type the concept you're curious about."},
    {"label": "Practice question", "icon": ":material/quiz:", "kind": "intent",
     "value": "practice", "needs": "topic",
     "clarify": "Let's practice. Pick a topic below, or type the one you want to drill."},
    {"label": "Fix my error", "icon": ":material/build:", "kind": "intent",
     "value": "debug", "needs": "attempt",
     "clarify": "Paste your SQL and the error message into the chat, and I'll help you fix it."},
]

FOLLOW_UPS = [
    {"label": "Explain it more simply", "icon": ":material/lightbulb:", "kind": "query",
     "value": "Can you explain that again more simply, for a complete beginner?"},
    {"label": "Give me a practice question", "icon": ":material/quiz:", "kind": "query",
     "value": "Give me a practice question on what we just discussed."},
    {"label": "Show a business example", "icon": ":material/storefront:", "kind": "query",
     "value": "Can you show a short business example of what we just discussed?"},
]

INTENT_QUERY_TEMPLATES = {
    "explain": "Explain {topic} for a complete beginner, with a short business example.",
    "practice": "Give me a beginner practice question on {topic}.",
}


def render_action_row(actions, *, key_prefix):
    """Horizontal row of chip buttons; returns the clicked action or None."""
    clicked = None
    with st.container(horizontal=True, horizontal_alignment="distribute"):
        for idx, action in enumerate(actions):
            if st.button(action["label"], icon=action.get("icon"),
                         key=f"{key_prefix}_{idx}", width="stretch"):
                clicked = action
    return clicked


# ---------------------------------------------------------------------------
# Help dialog
# ---------------------------------------------------------------------------

@st.dialog("How this tutor works", width="large")
def show_help_dialog():
    st.subheader("Where answers come from")
    st.markdown(
        "- :blue-badge[Course materials] — answered from the BUS 390 syllabus and course content\n"
        "- :violet-badge[SQL explanation] · :violet-badge[Debugging help] — the tutor's general "
        "SQL knowledge, not course-specific\n"
        "- :green-badge[Practice question] — generated for you to try\n"
        "- :gray-badge[General chat] — conversation, no lookup needed\n"
        "- :orange-badge[Not from course materials] — a fallback answer; double-check it"
    )
    st.subheader("Getting better results")
    st.markdown(
        "- Tell me which module you're on (M0–M8) so I can pitch answers at the right level\n"
        "- Paste your table structure when asking about a query\n"
        "- For JOIN questions, describe how the tables relate\n"
        "- Paste the exact error message when something breaks"
    )
    st.subheader("Good to know")
    st.markdown(
        "- This tutor can make mistakes — verify anything that affects your grade\n"
        "- Don't include personal information in your questions\n"
        "- Questions are logged (anonymously) to improve the course\n"
        f"- Stuck? Email {INSTRUCTOR_NAME}: [{INSTRUCTOR_EMAIL}](mailto:{INSTRUCTOR_EMAIL})"
    )
