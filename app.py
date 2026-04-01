import streamlit as st

from matcher import extract_text_from_pdf, match_resume_jd


st.set_page_config(page_title="Resume Matcher", page_icon="AI", layout="wide")


def render_tags(items, tone="match"):
    if not items:
        message = "No aligned skills detected yet." if tone == "match" else "No gap signals detected."
        return f"<div class='chip-row'><span class='chip chip-empty'>{message}</span></div>"

    chip_class = "chip-positive" if tone == "match" else "chip-negative"
    chips = "".join(f"<span class='chip {chip_class}'>{skill}</span>" for skill in sorted(items))
    return f"<div class='chip-row'>{chips}</div>"


def build_summary(score, matched_count, missing_count):
    if matched_count == 0 and missing_count == 0:
        return "No measurable skill overlap was detected from the submitted job description."
    if score >= 80:
        return "Strong alignment. The resume already reflects most of the requested capabilities."
    if score >= 55:
        return "Promising fit. A few targeted resume updates could make the profile more competitive."
    return "Low alignment right now. The biggest opportunity is to surface role-relevant skills more clearly."


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Sora:wght@500;600;700&display=swap');

    :root {
        --bg-1: #07111f;
        --bg-2: #0d1728;
        --panel: rgba(8, 18, 34, 0.82);
        --panel-strong: rgba(10, 22, 40, 0.96);
        --panel-soft: rgba(15, 29, 52, 0.72);
        --line: rgba(158, 181, 214, 0.14);
        --text: #e8eefc;
        --muted: #8fa5c8;
        --accent: #4de2c5;
        --accent-2: #6aa6ff;
        --good: #56f0b6;
        --warn: #ffb55f;
        --bad: #ff7f96;
        --shadow: 0 24px 60px rgba(1, 7, 18, 0.45);
    }

    .stApp {
        background:
            radial-gradient(circle at 10% 12%, rgba(77, 226, 197, 0.12), transparent 24%),
            radial-gradient(circle at 88% 8%, rgba(106, 166, 255, 0.18), transparent 26%),
            radial-gradient(circle at 78% 78%, rgba(54, 91, 180, 0.18), transparent 30%),
            linear-gradient(160deg, var(--bg-1) 0%, var(--bg-2) 55%, #091220 100%);
        color: var(--text);
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    .main-shell {
        position: relative;
        overflow: hidden;
        border: 1px solid rgba(173, 198, 255, 0.10);
        border-radius: 30px;
        padding: 1.2rem;
        background: linear-gradient(180deg, rgba(7, 16, 30, 0.88), rgba(8, 17, 30, 0.72));
        box-shadow: var(--shadow);
        backdrop-filter: blur(16px);
    }

    .main-shell::before {
        content: "";
        position: absolute;
        inset: 0;
        background:
            linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px),
            linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px);
        background-size: 28px 28px;
        mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.35), rgba(0, 0, 0, 0));
        pointer-events: none;
    }

    .hero {
        position: relative;
        padding: 1.2rem 1.2rem 1.4rem;
        border-radius: 26px;
        border: 1px solid rgba(173, 198, 255, 0.10);
        background:
            radial-gradient(circle at top right, rgba(77, 226, 197, 0.16), transparent 22%),
            linear-gradient(135deg, rgba(14, 30, 54, 0.96), rgba(9, 19, 36, 0.92));
        overflow: hidden;
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 240px;
        height: 240px;
        right: -80px;
        top: -80px;
        background: radial-gradient(circle, rgba(77, 226, 197, 0.28), transparent 62%);
        filter: blur(8px);
    }

    .hero-grid {
        display: grid;
        grid-template-columns: 1.4fr 0.8fr;
        gap: 1rem;
        align-items: end;
        position: relative;
        z-index: 1;
    }

    .eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.4rem 0.8rem;
        border-radius: 999px;
        border: 1px solid rgba(77, 226, 197, 0.22);
        background: rgba(77, 226, 197, 0.08);
        color: var(--accent);
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
    }

    .hero-title {
        margin: 0.9rem 0 0.55rem;
        font-family: 'Sora', sans-serif;
        font-size: 3rem;
        line-height: 1.02;
        letter-spacing: -0.04em;
        color: #f7fbff;
    }

    .hero-copy {
        max-width: 660px;
        color: #aabedf;
        font-size: 1rem;
        line-height: 1.65;
    }

    .hero-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 0.65rem;
        margin-top: 1rem;
    }

    .hero-pill {
        padding: 0.58rem 0.9rem;
        border-radius: 14px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(173, 198, 255, 0.12);
        color: #d9e6fb;
        font-size: 0.88rem;
    }

    .signal-card {
        padding: 1rem;
        border-radius: 22px;
        background: linear-gradient(180deg, rgba(9, 19, 34, 0.96), rgba(11, 24, 44, 0.9));
        border: 1px solid rgba(173, 198, 255, 0.12);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
    }

    .signal-label {
        color: var(--muted);
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.14em;
    }

    .signal-number {
        margin-top: 0.4rem;
        font-family: 'Sora', sans-serif;
        font-size: 2.4rem;
        color: #f4fbff;
    }

    .signal-copy {
        margin-top: 0.45rem;
        color: #9cb2d4;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    .board {
        margin-top: 1rem;
        display: grid;
        grid-template-columns: minmax(0, 1.08fr) minmax(0, 0.92fr);
        gap: 1rem;
    }

    .panel {
        height: 100%;
        padding: 1.1rem;
        border-radius: 24px;
        border: 1px solid var(--line);
        background: linear-gradient(180deg, rgba(8, 18, 34, 0.94), rgba(11, 24, 43, 0.84));
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
    }

    .panel-kicker {
        color: var(--accent);
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
    }

    .panel-title {
        margin-top: 0.65rem;
        font-family: 'Sora', sans-serif;
        font-size: 1.28rem;
        color: #f6fbff;
    }

    .panel-copy {
        margin-top: 0.4rem;
        margin-bottom: 1rem;
        color: var(--muted);
        font-size: 0.93rem;
        line-height: 1.6;
    }

    .metric-strip {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.8rem;
        margin-bottom: 1rem;
    }

    .metric-card {
        padding: 0.85rem 0.9rem;
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(173, 198, 255, 0.10);
    }

    .metric-label {
        color: var(--muted);
        font-size: 0.76rem;
        text-transform: uppercase;
        letter-spacing: 0.12em;
    }

    .metric-value {
        margin-top: 0.45rem;
        font-family: 'Sora', sans-serif;
        font-size: 1.35rem;
        color: #f7fbff;
    }

    .score-card {
        position: relative;
        overflow: hidden;
        border-radius: 24px;
        padding: 1.15rem;
        background:
            radial-gradient(circle at top right, rgba(77, 226, 197, 0.14), transparent 28%),
            linear-gradient(135deg, rgba(17, 40, 70, 1), rgba(8, 22, 42, 0.98));
        border: 1px solid rgba(100, 162, 255, 0.18);
        margin-bottom: 1rem;
    }

    .score-label {
        color: #9bb6dc;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.16em;
    }

    .score-number {
        margin: 0.45rem 0 0.35rem;
        font-family: 'Sora', sans-serif;
        font-size: 3rem;
        line-height: 1;
        color: #f8fcff;
    }

    .score-copy {
        color: #b7cae7;
        font-size: 0.94rem;
        line-height: 1.55;
    }

    .section-label {
        margin: 1rem 0 0.55rem;
        font-family: 'Sora', sans-serif;
        font-size: 0.96rem;
        color: #eef5ff;
    }

    .chip-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
    }

    .chip {
        padding: 0.5rem 0.82rem;
        border-radius: 999px;
        font-size: 0.84rem;
        border: 1px solid transparent;
    }

    .chip-positive {
        color: #c6fff0;
        background: rgba(86, 240, 182, 0.12);
        border-color: rgba(86, 240, 182, 0.18);
    }

    .chip-negative {
        color: #ffd4db;
        background: rgba(255, 127, 150, 0.11);
        border-color: rgba(255, 127, 150, 0.16);
    }

    .chip-empty {
        color: #9fb2d3;
        background: rgba(255, 255, 255, 0.04);
        border-color: rgba(173, 198, 255, 0.10);
    }

    .insight {
        margin-top: 1rem;
        padding: 0.95rem 1rem;
        border-radius: 18px;
        border: 1px solid rgba(255, 181, 95, 0.18);
        background: rgba(255, 181, 95, 0.08);
        color: #ffd6a0;
        line-height: 1.6;
        font-size: 0.92rem;
    }

    .insight.good {
        border-color: rgba(86, 240, 182, 0.18);
        background: rgba(86, 240, 182, 0.08);
        color: #c7ffe9;
    }

    .placeholder {
        padding: 1.3rem 1rem;
        border-radius: 20px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px dashed rgba(173, 198, 255, 0.14);
        color: #9cb2d4;
        text-align: center;
        line-height: 1.6;
    }

    .workflow-list {
        display: grid;
        gap: 0.75rem;
        margin-top: 0.35rem;
    }

    .workflow-item {
        display: grid;
        grid-template-columns: 40px 1fr;
        gap: 0.85rem;
        align-items: start;
        padding: 0.8rem 0.9rem;
        border-radius: 18px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(173, 198, 255, 0.08);
    }

    .workflow-badge {
        width: 40px;
        height: 40px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, rgba(77, 226, 197, 0.18), rgba(106, 166, 255, 0.18));
        color: #eff8ff;
        font-weight: 700;
    }

    .workflow-title {
        color: #eef6ff;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .workflow-copy {
        color: var(--muted);
        font-size: 0.9rem;
        line-height: 1.55;
    }

    .stTextArea textarea {
        min-height: 270px;
        border-radius: 18px;
        padding-top: 0.8rem;
        background: rgba(4, 12, 24, 0.92);
        color: #edf5ff;
        border: 1px solid rgba(173, 198, 255, 0.12);
    }

    .stTextArea textarea::placeholder {
        color: #6f87ac;
    }

    .stFileUploader label, .stTextArea label {
        color: #eef6ff !important;
        font-weight: 700;
    }

    [data-testid="stFileUploader"] {
        border-radius: 18px;
        border: 1px dashed rgba(77, 226, 197, 0.26);
        background: rgba(4, 12, 24, 0.72);
        padding: 0.5rem;
    }

    [data-testid="stFileUploader"] section {
        background: transparent;
    }

    .stButton > button {
        width: 100%;
        height: 3.2rem;
        border: 1px solid rgba(110, 190, 255, 0.20);
        border-radius: 16px;
        font-weight: 800;
        color: #04111f;
        background: linear-gradient(135deg, #4de2c5, #72a8ff);
        box-shadow: 0 14px 30px rgba(77, 226, 197, 0.18);
    }

    .stButton > button:hover {
        border-color: rgba(110, 190, 255, 0.30);
    }

    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #4de2c5, #72a8ff);
    }

    div[data-testid="stAlert"] {
        border-radius: 16px;
    }

    @media (max-width: 980px) {
        .hero-grid,
        .board,
        .metric-strip {
            grid-template-columns: 1fr;
        }

        .hero-title {
            font-size: 2.35rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='main-shell'>", unsafe_allow_html=True)
st.markdown(
    """
    <div class="hero">
        <div class="hero-grid">
            <div>
                <div class="eyebrow">AI Talent Screening</div>
                <div class="hero-title">Professional resume intelligence with a modern AI/ML workspace feel.</div>
                <div class="hero-copy">
                    Compare resume evidence against role expectations, surface alignment signals, and expose missing
                    capabilities in a cleaner review environment built for recruiters, founders, and hiring teams.
                </div>
                <div class="hero-pills">
                    <div class="hero-pill">Signal-first match scoring</div>
                    <div class="hero-pill">Skills gap detection</div>
                    <div class="hero-pill">Ready for technical hiring workflows</div>
                </div>
            </div>
            <div class="signal-card">
                <div class="signal-label">Review Mode</div>
                <div class="signal-number">AIML</div>
                <div class="signal-copy">
                    Designed like an analysis console: darker palette, stronger hierarchy, and focused result cards for
                    a sharper recruiting experience.
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='board'>", unsafe_allow_html=True)

with st.container():
    left, right = st.columns([1.08, 0.92], gap="medium")

    with left:
        st.markdown(
            """
            <div class="panel">
                <div class="panel-kicker">Input Console</div>
                <div class="panel-title">Candidate and role context</div>
                <div class="panel-copy">
                    Upload a resume PDF, paste the target job description, and run a quick fit analysis against the
                    known skills library.
                </div>
            """,
            unsafe_allow_html=True,
        )
        resume_file = st.file_uploader("Resume PDF", type=["pdf"])
        jd = st.text_area(
            "Job Description",
            placeholder="Paste responsibilities, required skills, tech stack, domain expectations, and seniority cues here...",
        )
        analyze = st.button("Run Match Analysis")
        st.markdown(
            """
                <div class="workflow-list">
                    <div class="workflow-item">
                        <div class="workflow-badge">1</div>
                        <div>
                            <div class="workflow-title">Ingest</div>
                            <div class="workflow-copy">Resume text is extracted from the uploaded PDF for downstream comparison.</div>
                        </div>
                    </div>
                    <div class="workflow-item">
                        <div class="workflow-badge">2</div>
                        <div>
                            <div class="workflow-title">Compare</div>
                            <div class="workflow-copy">The role description is checked against the same skills vocabulary used for the resume.</div>
                        </div>
                    </div>
                    <div class="workflow-item">
                        <div class="workflow-badge">3</div>
                        <div>
                            <div class="workflow-title">Interpret</div>
                            <div class="workflow-copy">The app returns a score, overlapping skills, and the strongest missing-skill signals.</div>
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            """
            <div class="panel">
                <div class="panel-kicker">Output Board</div>
                <div class="panel-title">Fit assessment and recommendation</div>
                <div class="panel-copy">
                    Use the score as a fast screening signal, then inspect matched and missing skills before deciding how
                    to improve the resume or shortlist the candidate.
                </div>
            """,
            unsafe_allow_html=True,
        )

        if analyze:
            if resume_file and jd.strip():
                resume_text = extract_text_from_pdf(resume_file)
                score, matched, missing = match_resume_jd(resume_text, jd)
                summary = build_summary(score, len(matched), len(missing))

                st.markdown(
                    f"""
                    <div class="metric-strip">
                        <div class="metric-card">
                            <div class="metric-label">Matched</div>
                            <div class="metric-value">{len(matched)}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Missing</div>
                            <div class="metric-value">{len(missing)}</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-label">Readiness</div>
                            <div class="metric-value">{min(int(score), 100)}%</div>
                        </div>
                    </div>
                    <div class="score-card">
                        <div class="score-label">Match Score</div>
                        <div class="score-number">{score}%</div>
                        <div class="score-copy">
                            {summary}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.progress(min(int(score), 100))

                st.markdown("<div class='section-label'>Aligned Skills</div>", unsafe_allow_html=True)
                st.markdown(render_tags(matched, "match"), unsafe_allow_html=True)

                st.markdown("<div class='section-label'>Gap Signals</div>", unsafe_allow_html=True)
                st.markdown(render_tags(missing, "missing"), unsafe_allow_html=True)

                insight_class = "insight good" if not missing else "insight"
                insight_text = (
                    "The resume already reflects the primary skill signals found in the job description."
                    if not missing
                    else f"Best next step: add project evidence, outcomes, or explicit mentions for {', '.join(sorted(missing))}."
                )
                st.markdown(
                    f"<div class='{insight_class}'>{insight_text}</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.warning("Please upload a resume PDF and enter a job description.")
        else:
            st.markdown(
                """
                <div class="placeholder">
                    Upload a resume and run the analysis to populate this board with score, alignment signals, and
                    missing-skill recommendations.
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)
