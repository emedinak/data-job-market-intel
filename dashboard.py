import re
import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import create_engine

from src.config import DB_PATH
from src.skills import extract_skills


def style_bar(fig, *, height=380, x_title=None, y_title=None):
    fig.update_layout(
        template="simple_white",
        height=height,
        margin=dict(l=10, r=10, t=10, b=10),
        bargap=0.25,
        font=dict(size=14),
        xaxis_title=x_title,
        yaxis_title=y_title,
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(0,0,0,0.06)",
            zeroline=False,
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
        ),
    )
    fig.update_traces(
        textposition="outside",
        cliponaxis=False,
    )
    return fig


st.set_page_config(
    page_title="Spain Data Job Market",
    page_icon="📊",
    layout="wide",
)

st.markdown(
    """
    <style>
      .block-container { padding-top: 1.2rem; max-width: 1200px; }
      [data-testid="stMetricValue"] { font-size: 1.55rem; }
      [data-testid="stMetricDelta"] { font-size: 0.95rem; }
      .section-title { font-size: 1.1rem; font-weight: 700; margin-top: 0.25rem; }
      .muted { color: rgba(49, 51, 63, 0.65); margin-top: -6px; }
      hr { margin: 0.8rem 0 1.1rem 0; }

      .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 14px;
        margin: 8px 0 14px 0;
      }
      .kpi-card {
        border: 1px solid rgba(49, 51, 63, 0.12);
        border-radius: 14px;
        padding: 14px 16px;
        background: white;
        box-shadow: 0 6px 20px rgba(0,0,0,0.04);
      }
      .kpi-label {
        font-size: 0.85rem;
        color: rgba(49, 51, 63, 0.65);
        margin-bottom: 6px;
      }
      .kpi-value {
        font-size: 1.55rem;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 6px;
      }
      .kpi-sub {
        font-size: 0.85rem;
        color: rgba(49, 51, 63, 0.65);
      }
      .kpi-pill {
        display: inline-block;
        font-size: 0.8rem;
        padding: 3px 8px;
        border-radius: 999px;
        background: rgba(22, 163, 74, 0.12);
        color: rgb(22, 163, 74);
        font-weight: 600;
        margin-left: 6px;
        vertical-align: middle;
      }
      @media (max-width: 1100px) {
        .kpi-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      }

      .insights-card {
        border: 1px solid rgba(49, 51, 63, 0.12);
        border-radius: 14px;
        padding: 14px 16px;
        background: white;
        box-shadow: 0 6px 20px rgba(0,0,0,0.04);
        margin: 8px 0 14px 0;
      }
      .insights-title {
        font-size: 0.95rem;
        font-weight: 800;
        margin-bottom: 10px;
      }
      .insight-item {
        display: flex;
        gap: 10px;
        padding: 7px 0;
        border-top: 1px solid rgba(49, 51, 63, 0.08);
      }
      .insight-item:first-of-type { border-top: none; }
      .insight-dot {
        width: 9px;
        height: 9px;
        border-radius: 999px;
        background: #2563eb;
        margin-top: 7px;
        flex: 0 0 9px;
      }
      .insight-text { font-size: 0.95rem; }
      .insight-strong { font-weight: 800; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <h1 style='text-align:center; margin-bottom:0;'>Spain Data Job Market Intelligence</h1>
    <p class='muted' style='text-align:center; font-size:16px;'>
      Interactive snapshot of Data & BI job demand in Spain (Adzuna API)
    </p>
    """,
    unsafe_allow_html=True,
)

engine = create_engine(f"sqlite:///{DB_PATH}", future=True)
df = pd.read_sql("SELECT * FROM jobs", engine)

df = df[df["company"].notna()]
df = df[df["company"].astype(str).str.strip() != ""]
df = df[df["company"].astype(str).str.lower() != "unknown"]

df = df[~df["company"].fillna("").str.contains(r"\.com", case=False)]
job_boards = ["indeed", "linkedin", "infojobs", "jooble", "trabajos.com"]
df = df[~df["company"].fillna("").str.lower().isin(job_boards)]


def classify_company(name):
    if not name:
        return "Unknown"

    name_lower = str(name).lower()

    if ".com" in name_lower or "indeed" in name_lower or "linkedin" in name_lower:
        return "Job Board"

    staffing_keywords = [
        "ett",
        "trabajo temporal",
        "consult",
        "recruit",
        "talent",
        "personnel",
        "rrhh",
        "selección",
        "manpower",
        "adecco",
        "randstad",
        "page personnel",
    ]

    if any(k in name_lower for k in staffing_keywords):
        return "Staffing / Consulting"

    return "Direct Employer"


df["company_type"] = df["company"].apply(classify_company)
df = df[df["company_type"] == "Direct Employer"].copy()


def extract_city(location):
    if not location:
        return None
    return str(location).split(",")[0].strip()


def classify_role(title: str) -> str:
    t = (title or "").lower()

    patterns = [
        ("Data Engineer", r"\bdata engineer\b|\bdata engineering\b|\bingenier[oa] de datos\b|\bdata platform\b"),
        ("Data Scientist", r"\bdata scientist\b|\bcient[ií]fic[oa] de datos\b|\bml engineer\b|\bmachine learning\b"),
        ("BI Analyst", r"\bbi\b|\bbusiness intelligence\b|\bpower bi\b|\btableau\b|\bqlik\b"),
        ("Data Analyst", r"\bdata analyst\b|\banalista de datos\b|\banalyst\b|\banalista\b|\banalytics\b"),
    ]

    for role, pat in patterns:
        if re.search(pat, t):
            return role
    return "Other"


def safe_mode(series, default="—"):
    try:
        vc = series.value_counts()
        return vc.index[0] if len(vc) else default
    except Exception:
        return default


def remote_flag(text: str) -> bool:
    t = (text or "").lower()
    keywords = [
        "remote",
        "remoto",
        "teletrabajo",
        "work from home",
        "wfh",
        "fully remote",
        "100% remote",
        "híbrido",
        "hybrid",
    ]
    return any(k in t for k in keywords)


df["city"] = df["location"].apply(extract_city)

if "created" in df.columns:
    df["created_dt"] = pd.to_datetime(df["created"], errors="coerce")

df["text"] = (df["title"].fillna("") + " " + df["description"].fillna(""))
df["skills"] = df["text"].apply(extract_skills)
df["role"] = df["title"].apply(classify_role)

df = df[df["city"].fillna("").str.lower() != "españa"].copy()

f = df.copy()

total_offers = len(f)

skills_exploded = f.explode("skills")
top_skill = safe_mode(skills_exploded["skills"].dropna(), default="—")

top_company = safe_mode(f["company"].fillna("Unknown"), default="—")
top_city = safe_mode(f["city"].fillna("Unknown"), default="—")

top_city_count = f["city"].fillna("Unknown").value_counts().iloc[0] if len(f) else 0
top_city_pct = round(100 * top_city_count / len(f), 1) if len(f) else 0.0
delta_html = f"<span class='kpi-pill'>↑ {top_city_pct}% of offers</span>" if len(f) else ""

st.markdown(
    f"""
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-label">Total offers</div>
        <div class="kpi-value">{total_offers}</div>
        <div class="kpi-sub">Current dataset</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-label">Top skill</div>
        <div class="kpi-value">{top_skill}</div>
        <div class="kpi-sub">Most mentioned</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-label">Top company</div>
        <div class="kpi-value">{top_company}</div>
        <div class="kpi-sub">Most listings</div>
      </div>

      <div class="kpi-card">
        <div class="kpi-label">Top city</div>
        <div class="kpi-value">{top_city}{delta_html}</div>
        <div class="kpi-sub">Share of offers</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

f = f.copy()
f["is_remote"] = f["text"].apply(remote_flag) if "text" in f.columns else False
remote_share = round(100 * f["is_remote"].mean(), 1) if len(f) else 0.0

role_series = f["role"].dropna()
role_series = role_series[role_series != "Other"]
top_role = safe_mode(role_series, default="—")
most_skill = safe_mode(f.explode("skills")["skills"].dropna(), default="—")

city_counts_all = f["city"].fillna("").str.strip().str.lower().value_counts()
madrid_share = round(100 * city_counts_all.get("madrid", 0) / max(1, len(f)), 1) if len(f) else 0.0
barcelona_share = round(100 * city_counts_all.get("barcelona", 0) / max(1, len(f)), 1) if len(f) else 0.0

st.markdown(
    f"""
    <div class="insights-card">
      <div class="insights-title">Key insights</div>

      <div class="insight-item">
        <div class="insight-dot"></div>
        <div class="insight-text">
          <span class="insight-strong">Madrid</span> concentrates <span class="insight-strong">{madrid_share}%</span> of offers.
        </div>
      </div>

      <div class="insight-item">
        <div class="insight-dot"></div>
        <div class="insight-text">
          <span class="insight-strong">Barcelona</span> concentrates <span class="insight-strong">{barcelona_share}%</span> of offers.
        </div>
      </div>

      <div class="insight-item">
        <div class="insight-dot"></div>
        <div class="insight-text">
          Top role is <span class="insight-strong">{top_role}</span>.
        </div>
      </div>

      <div class="insight-item">
        <div class="insight-dot"></div>
        <div class="insight-text">
          Most demanded skill is <span class="insight-strong">{most_skill}</span>.
        </div>
      </div>

      <div class="insight-item">
        <div class="insight-dot"></div>
        <div class="insight-text">
          Remote / hybrid mentions appear in <span class="insight-strong">{remote_share}%</span> of offers.
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<hr/>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Companies", "Skills", "Salary", "Data"])

with tab1:
    st.markdown('<div class="section-title">Market snapshot</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">High-level view based on the current dataset.</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="section-title">Top skills</div><div class="muted">Top 10</div>', unsafe_allow_html=True)
        top_skills_df = (
            f.explode("skills")["skills"]
            .value_counts()
            .head(10)
            .reset_index()
        )
        top_skills_df.columns = ["skill", "count"]

        if len(top_skills_df):
            fig = px.bar(top_skills_df.sort_values("count", ascending=True), x="count", y="skill", orientation="h")
            fig.update_traces(texttemplate="%{x:,}")
            fig = style_bar(fig, height=420, x_title="count", y_title="")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No skills available for the current dataset.")

    with c2:
        st.markdown('<div class="section-title">Top cities</div><div class="muted">Top 10</div>', unsafe_allow_html=True)
        top_cities_df = (
            f["city"].fillna("Unknown")
            .value_counts()
            .head(10)
            .reset_index()
        )
        top_cities_df.columns = ["city", "count"]

        if len(top_cities_df):
            fig = px.bar(top_cities_df.sort_values("count", ascending=True), x="count", y="city", orientation="h")
            fig.update_traces(texttemplate="%{x:,}")
            fig = style_bar(fig, height=420, x_title="count", y_title="")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No city data available for the current dataset.")

    st.markdown("<hr/>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Posting trend</div><div class="muted">Daily volume</div>', unsafe_allow_html=True)
    if "created_dt" in f.columns and f["created_dt"].notna().any():
        trend = (
            f.dropna(subset=["created_dt"])
            .groupby(f["created_dt"].dt.date)
            .size()
            .reset_index(name="offers")
        )
        trend.columns = ["date", "offers"]
        fig = px.line(trend, x="date", y="offers")
        fig.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10), template="simple_white")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No valid dates found to plot the trend.")

with tab2:
    st.markdown('<div class="section-title">Top companies</div><div class="muted">Direct employers with the most listings</div>', unsafe_allow_html=True)

    top_companies_df = (
        f["company"].fillna("Unknown")
        .value_counts()
        .head(20)
        .reset_index()
    )
    top_companies_df.columns = ["company", "offers"]

    if len(top_companies_df):
        fig = px.bar(top_companies_df.sort_values("offers", ascending=True), x="offers", y="company", orientation="h")
        fig.update_traces(texttemplate="%{x:,}")
        fig = style_bar(fig, height=520, x_title="offers", y_title="")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No company data available for the current dataset.")

    st.markdown("<hr/>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Company breakdown</div><div class="muted">Offers + top skills (Top 5)</div>', unsafe_allow_html=True)

    company_skills = f.explode("skills")
    company_summary = (
        company_skills
        .groupby(["company", "skills"])
        .size()
        .reset_index(name="count")
        .sort_values(["company", "count"], ascending=[True, False])
    )

    top_skills_per_company = company_summary.groupby("company").head(5)
    skills_agg = (
        top_skills_per_company
        .groupby("company")["skills"]
        .apply(lambda x: ", ".join([s for s in x if pd.notna(s)]))
        .reset_index()
    )

    company_counts = f["company"].value_counts().reset_index()
    company_counts.columns = ["company", "offers"]

    final_table = company_counts.merge(skills_agg, on="company", how="left")
    final_table["skills"] = final_table["skills"].fillna("—")

    st.dataframe(final_table.head(50), use_container_width=True, hide_index=True)

with tab3:
    st.markdown('<div class="section-title">Explore skills</div><div class="muted">What skills appear most in the dataset</div>', unsafe_allow_html=True)

    top_skills15 = (
        f.explode("skills")["skills"]
        .value_counts()
        .head(15)
        .reset_index()
    )
    top_skills15.columns = ["skill", "count"]

    if len(top_skills15):
        fig = px.bar(top_skills15.sort_values("count", ascending=True), x="count", y="skill", orientation="h")
        fig.update_traces(texttemplate="%{x:,}")
        fig = style_bar(fig, height=560, x_title="count", y_title="")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No skills available for the current dataset.")

    st.markdown("<hr/>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Skill coverage</div><div class="muted">How many offers mention at least one tracked skill</div>', unsafe_allow_html=True)
    has_any_skill = f["skills"].apply(lambda x: isinstance(x, list) and len(x) > 0).mean() if len(f) else 0
    st.metric("Offers with ≥1 tracked skill", f"{round(has_any_skill * 100, 1)}%")

with tab4:
    st.markdown(
        '<div class="section-title">Salary intelligence</div>'
        '<div class="muted">Based on Adzuna salary fields when available</div>',
        unsafe_allow_html=True,
    )

    needed = {"salary_min", "salary_max"}
    if not needed.issubset(set(f.columns)):
        st.warning(
            "Salary columns not found in the database yet. "
            "Make sure you added them to db.py, updated ingest.py, and re-ingested."
        )
    else:
        s = f.copy()
        s["salary_value"] = s[["salary_min", "salary_max"]].mean(axis=1, skipna=True)
        s = s[s["salary_value"].notna() & (s["salary_value"] > 0)]

        pct_with_salary = round(100 * len(s) / max(1, len(f)), 1)
        avg_salary = s["salary_value"].mean() if len(s) else None
        med_salary = s["salary_value"].median() if len(s) else None

        c1, c2, c3 = st.columns(3)
        c1.metric("Offers with salary", f"{pct_with_salary}%")
        c2.metric("Average salary", f"{avg_salary:,.0f}" if avg_salary else "—")
        c3.metric("Median salary", f"{med_salary:,.0f}" if med_salary else "—")

        st.markdown("<hr/>", unsafe_allow_html=True)

        st.markdown(
            '<div class="section-title">Average salary by city</div>'
            '<div class="muted">Top cities with enough salary data</div>',
            unsafe_allow_html=True,
        )

        city_salary = (
            s.groupby("city")
            .agg(avg_salary=("salary_value", "mean"), n=("salary_value", "size"))
            .reset_index()
        )

        min_n = st.slider("Minimum salary observations per city", 5, 50, 10, step=5)
        city_salary = city_salary[city_salary["n"] >= min_n].sort_values("avg_salary", ascending=False).head(10)

        if len(city_salary):
            fig = px.bar(
                city_salary.sort_values("avg_salary", ascending=True),
                x="avg_salary",
                y="city",
                orientation="h",
                hover_data=["n"],
            )
            fig.update_traces(
                texttemplate="€%{x:,.0f}",
                hovertemplate="%{y}<br><b>€%{x:,.0f}</b><br>n=%{customdata[0]}<extra></extra>",
            )
            fig = style_bar(fig, height=420, x_title="avg_salary (€)", y_title="")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough salary data per city yet. Try lowering the minimum observations slider.")

        st.markdown("<hr/>", unsafe_allow_html=True)

        st.markdown(
            '<div class="section-title">Offers by role</div>'
            '<div class="muted">All offers (not only salary)</div>',
            unsafe_allow_html=True,
        )

        role_counts = f["role"].value_counts().reset_index()
        role_counts.columns = ["role", "offers"]

        fig = px.bar(
            role_counts.sort_values("offers", ascending=True),
            x="offers",
            y="role",
            orientation="h",
        )
        fig.update_traces(texttemplate="%{x:,}", hovertemplate="%{y}<br><b>%{x:,}</b><extra></extra>")
        fig = style_bar(fig, height=380, x_title="offers", y_title="")
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("<hr/>", unsafe_allow_html=True)

        st.markdown(
            '<div class="section-title">Average salary by role</div>'
            '<div class="muted">Only offers with salary</div>',
            unsafe_allow_html=True,
        )

        role_salary = (
            s.groupby("role")
            .agg(
                avg_salary=("salary_value", "mean"),
                median_salary=("salary_value", "median"),
                n=("salary_value", "size"),
            )
            .reset_index()
        )

        min_role_n = st.slider("Minimum salary observations per role", 5, 100, 10, step=5)
        role_salary = role_salary[role_salary["n"] >= min_role_n].sort_values("avg_salary", ascending=False)

        if len(role_salary):
            fig = px.bar(
                role_salary.sort_values("avg_salary", ascending=True),
                x="avg_salary",
                y="role",
                orientation="h",
                hover_data=["median_salary", "n"],
            )
            fig.update_traces(
                texttemplate="€%{x:,.0f}",
                hovertemplate="%{y}<br><b>€%{x:,.0f}</b><br>n=%{customdata[1]}<extra></extra>",
            )
            fig = style_bar(fig, height=380, x_title="avg_salary (€)", y_title="")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough salary data per role yet. Try lowering the minimum observations slider.")

with tab5:
    st.markdown('<div class="section-title">Latest offers</div><div class="muted">Raw data view</div>', unsafe_allow_html=True)

    cols = ["created", "title", "company", "city", "category", "url"]
    cols = [c for c in cols if c in f.columns]

    n_rows = st.slider(
        "Rows to display",
        min_value=50,
        max_value=min(5000, len(f)) if len(f) else 50,
        value=200,
        step=50,
    )

    st.dataframe(
        f.sort_values("created", ascending=False)[cols].head(n_rows),
        use_container_width=True,
        hide_index=True,
    )

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; padding: 20px 0; color: #6c757d; font-size: 14px;'>
        <p>Built by <strong>Eduardo Medina Krumholz</strong></p>
        <p>
            <a href="https://www.linkedin.com/in/eduardo-medina-krumholz-3b756b243/" target="_blank" style="text-decoration: none; margin-right: 15px;">
                🔗 LinkedIn
            </a>
            <a href="https://github.com/emedinak" target="_blank" style="text-decoration: none;">
                💻 GitHub
            </a>
        </p>
        <p style="font-size:12px; color:#adb5bd;">
            Spain Data Job Market Intelligence · Powered by Adzuna API
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)