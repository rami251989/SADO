import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure
from io import BytesIO
import textwrap
import re
import json

import arabic_reshaper
from bidi.algorithm import get_display


# ===============================
# 💎 إعداد صفحة ستريملت + ديزاين
# ===============================
st.set_page_config(
    page_title="Sado Web - BI & Data Cleaning",
    layout="wide"
)

dark_style = """
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --bg: #020617;
    --surface: rgba(12, 18, 34, 0.72);
    --border: rgba(148, 163, 184, 0.25);
    --primary: #5eead4;
    --primary-strong: #06b6d4;
    --accent: #facc15;
    --muted: #9ca3af;
}

* {
    font-family: 'Inter', "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
}

/* إزالة شريط Streamlit العلوي */
header[data-testid="stHeader"] {
    background: transparent;
}

/* خلفية التطبيق */
.stApp {
    background: radial-gradient(circle at 20% 20%, #111827 0, #020617 40%, #020617 100%),
                linear-gradient(135deg, rgba(6, 182, 212, 0.08), transparent 50%),
                linear-gradient(225deg, rgba(250, 204, 21, 0.07), transparent 45%);
    color: #f9fafb;
    position: relative;
}

.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background: linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px),
                linear-gradient(180deg, rgba(255,255,255,0.035) 1px, transparent 1px);
    background-size: 120px 120px;
    opacity: 0.35;
    pointer-events: none;
}

.block-container {
    padding-top: 1rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(2, 6, 23, 0.85), rgba(2, 6, 23, 0.95) 60%, rgba(11, 17, 32, 0.98));
    border-right: 1px solid #1e293b;
    backdrop-filter: blur(6px);
}
section[data-testid="stSidebar"] .css-1d391kg {
    padding-top: 2rem;
}

/* Navbar */
.navbar {
    background: linear-gradient(120deg, rgba(15,23,42,0.85), rgba(17,24,39,0.95)),
                radial-gradient(circle at 15% 20%, rgba(94,234,212,0.25), transparent 35%),
                radial-gradient(circle at 85% 20%, rgba(250,204,21,0.18), transparent 28%);
    padding: 14px 24px;
    border-radius: 18px;
    margin-bottom: 22px;
    border: 1px solid var(--border);
    box-shadow: 0 24px 60px rgba(15,23,42,0.88);
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: relative;
    overflow: hidden;
}
.navbar-left {
    display: flex;
    align-items: center;
    gap: 10px;
}
.nav-logo {
    width: 34px;
    height: 34px;
    border-radius: 999px;
    background: radial-gradient(circle at 30% 20%, #5eead4, #14b8a6, #0ea5e9);
    box-shadow: 0 0 25px rgba(94,234,212,0.55);
}
.nav-title-main {
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 0.03em;
}
.nav-title-sub {
    font-size: 11px;
    color: var(--muted);
}
.nav-badge {
    font-size: 10px;
    color: var(--bg);
    border-radius: 999px;
    padding: 2px 8px;
    border: 1px solid rgba(94,234,212,0.55);
    background: linear-gradient(120deg, #5eead4, #22d3ee);
}
.navbar-right {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 11px;
    color: var(--muted);
}

/* Stat cards */
.stat-card {
    background: linear-gradient(180deg, rgba(15,23,42,0.92), rgba(10,17,33,0.9)),
                radial-gradient(circle at 20% 0%, rgba(94,234,212,0.2), transparent 45%),
                radial-gradient(circle at 85% 15%, rgba(250,204,21,0.14), transparent 35%);
    padding: 20px 22px;
    border-radius: 20px;
    border: 1px solid rgba(94,234,212,0.3);
    box-shadow: 0 20px 55px rgba(8, 47, 73, 0.5);
    position: relative;
    overflow: hidden;
    backdrop-filter: blur(6px);
}
.stat-card::before {
    content: "";
    position: absolute;
    width: 320px;
    height: 320px;
    border-radius: 999px;
    background: radial-gradient(circle, rgba(96,165,250,0.18), transparent 60%);
    top: -160px;
    right: -120px;
    opacity: 0.8;
}
.stat-label {
    font-size: 11px;
    color: var(--muted);
    letter-spacing: 0.08em;
    text-transform: uppercase;
}
.stat-value {
    font-size: 30px;
    font-weight: 700;
    margin-top: 6px;
}
.stat-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 2px 7px;
    border-radius: 999px;
    font-size: 10px;
    border: 1px solid rgba(94,234,212,0.25);
    color: #e5e7eb;
    margin-top: 10px;
    background: rgba(94,234,212,0.08);
}

/* ألوان خاصة لكل كرت */
.stat-card.rows .stat-value { color: #22c55e; }
.stat-card.cols .stat-value { color: #eab308; }
.stat-card.mem  .stat-value { color: #38bdf8; }

/* أزرار عامة */
.stButton>button {
    background: linear-gradient(135deg, #22d3ee, #5eead4);
    color: #0b1224;
    border-radius: 14px;
    padding: 10px 22px;
    border: none;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.01em;
    box-shadow: 0 12px 30px rgba(34, 211, 238, 0.35);
    transition: all 0.18s ease-out;
}
.stButton>button:hover {
    transform: translateY(-1px) scale(1.02);
    box-shadow: 0 18px 45px rgba(34, 211, 238, 0.55);
}

/* Tabs */
.stTabs [role="tablist"] {
    border-bottom: 1px solid #1e293b;
    background: rgba(15,23,42,0.55);
    padding: 4px 8px;
    border-radius: 14px;
}
.stTabs [role="tab"] {
    color: var(--muted);
    padding-bottom: 12px;
    font-weight: 600;
    font-size: 13px;
}
.stTabs [role="tab"][aria-selected="true"] {
    color: #5eead4;
    border-bottom: 3px solid #5eead4;
}

/* Dataframe tables */
.dataframe {
    background-color: #020617 !important;
    color: #e5e7eb !important;
}
.dataframe th {
    background: rgba(15,23,42,0.65) !important;
    color: #e5e7eb !important;
    font-weight: 600 !important;
}
.dataframe td, .dataframe th {
    border-color: rgba(148,163,184,0.2) !important;
}

/* Inputs */
div[data-baseweb="input"]>div>input,
.stSelectbox>div>div>select,
.stTextInput>div>div>input {
    background-color: #020617 !important;
    border-radius: 12px !important;
    border: 1px solid #1e293b !important;
    color: #e5e7eb !important;
    box-shadow: 0 0 0 1px rgba(94,234,212,0.15);
}
.stTextArea textarea {
    background-color: #020617 !important;
    border-radius: 12px !important;
    border: 1px solid #1e293b !important;
    color: #e5e7eb !important;
    box-shadow: 0 0 0 1px rgba(94,234,212,0.15);
}

/* Expander */
details {
    background: rgba(15,23,42,0.85);
    border-radius: 14px;
    border: 1px solid #1e293b;
}

/* Small helper label */
.helper-label {
    font-size: 11px;
    color: #9ca3af;
}

/* Section title accent */
.section-title {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 4px;
}
.section-subtitle {
    font-size: 11px;
    color: #9ca3af;
    margin-bottom: 10px;
}

</style>
"""

st.markdown(dark_style, unsafe_allow_html=True)

# style for matplotlib
plt.style.use("dark_background")
matplotlib.rcParams['axes.facecolor'] = '#020617'
matplotlib.rcParams['figure.facecolor'] = '#020617'
matplotlib.rcParams['text.color'] = '#e5e7eb'
matplotlib.rcParams['axes.edgecolor'] = '#4b5563'
matplotlib.rcParams['axes.labelcolor'] = '#e5e7eb'
matplotlib.rcParams['xtick.color'] = '#9ca3af'
matplotlib.rcParams['ytick.color'] = '#9ca3af'
matplotlib.rcParams['axes.grid'] = True
matplotlib.rcParams['grid.color'] = '#1f2937'
matplotlib.rcParams['grid.alpha'] = 0.4

# ========================
# دالة مساعدة للعربي
# ========================
def ar(text):
    """تهيئة نص عربي ليظهر بشكل صحيح في matplotlib / PDF"""
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    reshaped = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped)
    return bidi_text


def sample_dataframe(rows: int = 50) -> pd.DataFrame:
    """بيانات تجريبية صغيرة لعرض مميزات التطبيق بسرعة."""
    np.random.seed(42)
    return pd.DataFrame(
        {
            "المنطقة": np.random.choice(["الرياض", "جدة", "الدمام", "أبها"], size=rows),
            "القسم": np.random.choice(["مبيعات", "عمليات", "مالية", "تقنية"], size=rows),
            "المبيعات": np.random.normal(loc=150_000, scale=25_000, size=rows).round(0),
            "الزيارات": np.random.poisson(lam=320, size=rows),
            "تاريخ الطلب": pd.date_range("2024-01-01", periods=rows, freq="D"),
            "ملاحظات": np.random.choice(["", "متابعة عاجلة", "عميل استراتيجي", "عرض موسمي"], size=rows),
        }
    )


# ========================
# Session State
# ========================
if "df" not in st.session_state:
    # تحميل بيانات تجريبية تلقائياً كي لا تظهر الصفحة فارغة عند التشغيل الأول
    st.session_state.df = sample_dataframe(120)
    st.session_state.show_sample_alert = True

if "dashboard_config" not in st.session_state:
    st.session_state.dashboard_config = []

if "dashboard_filter" not in st.session_state:
    st.session_state.dashboard_filter = None  # dict: {column, op, value}

if "last_report" not in st.session_state:
    st.session_state.last_report = None


# ========================
# Navbar
# ========================
st.markdown(
    """
<div class="navbar">
  <div class="navbar-left">
    <div class="nav-logo"></div>
    <div>
      <div class="nav-title-main">Sado Web – BI & Data Cleaning</div>
      <div class="nav-title-sub">Excel EDA • Data Cleaning • Dashboard • PDF Analytics</div>
    </div>
    <div class="nav-badge">v1.0 PRO</div>
  </div>
  <div class="navbar-right">
    <span>Built for Analysts · شبه Power BI</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)


# ========================
# دوال التحليل المتقدم
# ========================
def build_advanced_report(df: pd.DataFrame, config=None):
    cfg = config or {
        "basic": True,
        "missing": True,
        "unique": True,
        "numeric": True,
        "correlation": True,
        "text": True,
        "ml": True,
        "insights": True,
    }

    report = []
    report.append("===== 🧠 تقرير التحليل الإحصائي المتقدم (Advanced EDA Report) =====")
    report.append("=" * 90 + "\n")

    numeric_df = df.apply(pd.to_numeric, errors="coerce")
    numeric_df = numeric_df.dropna(axis=1, how="all")

    missing = df.isna().sum()
    percent_missing = (missing / len(df)) * 100
    missing_table = pd.DataFrame({
        "Missing Count": missing,
        "Missing %": percent_missing
    }).sort_values("Missing Count", ascending=False)

    skew_vals = numeric_df.skew() if not numeric_df.empty else pd.Series(dtype=float)
    kurt_vals = numeric_df.kurt() if not numeric_df.empty else pd.Series(dtype=float)
    corr = numeric_df.corr() if (not numeric_df.empty and numeric_df.shape[1] >= 2) else None

    if cfg.get("basic", True):
        report.append("■ 1) معلومات عامة عن البيانات")
        report.append("-" * 60)
        report.append(f"عدد الصفوف     : {len(df)}")
        report.append(f"عدد الأعمدة    : {len(df.columns)}")
        report.append(f"حجم الذاكرة    : {df.memory_usage(deep=True).sum()/1024:.2f} KB\n")
        report.append("أسماء الأعمدة وأنواعها:")
        report.append(str(df.dtypes))
        report.append("")

    if cfg.get("missing", True):
        report.append("■ 2) تحليل Missing Data")
        report.append("-" * 60)
        report.append(str(missing_table))
        report.append("")
        empty_cols = missing_table[missing_table["Missing Count"] == len(df)]
        if len(empty_cols) > 0:
            report.append("⚠️ أعمدة فارغة بالكامل:")
            report.append(str(empty_cols))
        else:
            report.append("✔ لا يوجد أعمدة فارغة بالكامل.")
        report.append("")

    if cfg.get("unique", True):
        report.append("■ 3) تحليل القيم الفريدة Unique Values")
        report.append("-" * 60)
        unique_counts = df.nunique()
        report.append(str(unique_counts.sort_values(ascending=False)))
        report.append("")
        report.append("Top 10 values لكل عمود:")
        for col in df.columns:
            report.append(f"\nعمود: {col}")
            try:
                report.append(str(df[col].value_counts().head(10)))
            except Exception:
                report.append("لا يمكن حساب التكرار.")

    if cfg.get("numeric", True):
        report.append("\n■ 4) التحليل الإحصائي للأعمدة الرقمية")
        report.append("-" * 60)
        if numeric_df.empty:
            report.append("لا يوجد أعمدة رقمية.")
        else:
            desc = numeric_df.describe().transpose()
            report.append(str(desc))
            report.append("")
            report.append("✦ Skewness (التواء التوزيع):")
            report.append(str(skew_vals))
            report.append("\n✦ Kurtosis (التفلطح):")
            report.append(str(kurt_vals))
            report.append("\n✦ Outliers باستخدام IQR (عدد القيم الشاذة في كل عمود):")
            outliers_report = {}
            for col in numeric_df.columns:
                Q1 = numeric_df[col].quantile(0.25)
                Q3 = numeric_df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
                outliers = numeric_df[(numeric_df[col] < lower) | (numeric_df[col] > upper)]
                outliers_report[col] = len(outliers)
            report.append(str(outliers_report))

    if cfg.get("correlation", True):
        report.append("\n■ 5) تحليل الارتباط بين الأعمدة (Correlation)")
        report.append("-" * 60)
        if corr is None or corr.empty:
            report.append("لا يوجد أعمدة رقمية كافية لعمل Correlation.")
        else:
            report.append(str(corr))
            report.append("")
            strong_info = []
            for i, c1 in enumerate(corr.columns):
                for j, c2 in enumerate(corr.columns):
                    if j <= i:
                        continue
                    val = corr.loc[c1, c2]
                    if abs(val) >= 0.7:
                        strong_info.append(f"{c1} ↔ {c2} : {val:.2f}")
            if strong_info:
                report.append("علاقات ارتباط قوية (|corr| ≥ 0.7):")
                report.extend(str(line) for line in strong_info)
            else:
                report.append("لا يوجد علاقات ارتباط قوية جدًا.")
        report.append("")

    text_cols = df.select_dtypes(include=["object", "string"])
    if cfg.get("text", True):
        report.append("■ 6) تحليل الأعمدة النصية")
        report.append("-" * 60)
        if text_cols.empty:
            report.append("لا يوجد أعمدة نصية.")
        else:
            for col in text_cols.columns:
                col_len = text_cols[col].astype(str).apply(len)
                report.append(f"\nعمود: {col}")
                report.append(f"متوسط طول النص : {col_len.mean():.2f}")
                report.append(f"أطول نص        : {col_len.max()}")
                report.append(f"أقصر نص        : {col_len.min()}")

    if cfg.get("ml", True):
        report.append("\n■ 7) جاهزية البيانات لبناء نموذج ML")
        report.append("-" * 60)
        report.append("الأعمدة التي تحتاج Encoding (تصنيفية / نصية):")
        report.append(str(text_cols.columns.tolist()))
        report.append("")
        report.append("الأعمدة التي تحتاج Scaling (رقمية):")
        report.append(str(numeric_df.columns.tolist()))
        report.append("")

    if cfg.get("insights", True):
        report.append("■ 8) لمحات ذكية عن البيانات (AI-style Insights)")
        report.append("-" * 60)
        insights = []
        heavy_missing = missing_table[missing_table["Missing %"] > 30]
        if not heavy_missing.empty:
            cols_list = ", ".join(heavy_missing.index.tolist())
            insights.append(f"- الأعمدة ({cols_list}) تحتوي على أكثر من 30% قيم ناقصة → مرشّحة للحذف أو للتعبئة المتقدمة.")
        id_candidates = []
        for col in df.columns:
            if len(df) > 0 and df[col].nunique() / len(df) > 0.9:
                id_candidates.append(col)
        if id_candidates:
            insights.append(f"- الأعمدة ({', '.join(id_candidates)}) تبدو مثل مفاتيح ID فريدة → غالبًا لا تفيد في النماذج مباشرة.")
        if not numeric_df.empty:
            for col, val in skew_vals.items():
                if abs(val) > 1:
                    direction = "يميني" if val > 0 else "يساري"
                    insights.append(
                        f"- العمود '{col}' توزيعُه ملتوي بقوة (Skew {direction} ≈ {val:.2f}) "
                        f"→ فكر في التحويل اللوغاريتمي أو Box-Cox."
                    )
        if corr is not None and not corr.empty:
            for i, c1 in enumerate(corr.columns):
                for j, c2 in enumerate(corr.columns):
                    if j <= i:
                        continue
                    val = corr.loc[c1, c2]
                    if abs(val) >= 0.85:
                        insights.append(
                            f"- العمودان '{c1}' و '{c2}' مرتبطان بقوة جدًا (corr ≈ {val:.2f}) "
                            f"→ قد يسببان Multicollinearity في النماذج الخطية."
                        )
        high_card = []
        for col in text_cols.columns:
            if df[col].nunique() > 50:
                high_card.append(col)
        if high_card:
            insights.append(
                f"- الأعمدة التصنيفية عالية التعدد ({', '.join(high_card)}) "
                f"→ الأفضل استخدام Target/Frequency Encoding بدل One-Hot."
            )
        if not insights:
            report.append("لم يتم اكتشاف ملاحظات خاصة إضافية.")
        else:
            report.extend(insights)

    return "\n".join(report), numeric_df, missing_table


def create_pdf_report(df: pd.DataFrame, config=None):
    report_str, numeric_df, _ = build_advanced_report(df, config)
    buf = BytesIO()

    with PdfPages(buf) as pdf:
        rows = len(df)
        cols = len(df.columns)
        mem_kb = df.memory_usage(deep=True).sum() / 1024
        dataset_name = "Dataset"

        fig, ax = plt.subplots(figsize=(8.27, 11.69))
        fig.patch.set_facecolor("#020617")
        ax.set_facecolor("#020617")
        ax.axis("off")

        ax.add_patch(
            plt.Rectangle((0, 0.85), 1, 0.15, transform=ax.transAxes,
                          color="#1f2937", alpha=0.98)
        )
        ax.text(0.5, 0.92, ar("تقرير التحليل الإحصائي المتقدم"),
                ha="center", va="center", fontsize=20, color="#f9fafb", fontweight="bold")
        ax.text(0.5, 0.87, ar("Sado Web - Advanced EDA Report"),
                ha="center", va="center", fontsize=10, color="#9ca3af")
        ax.text(0.5, 0.79, ar(f"ملف البيانات: {dataset_name}"),
                ha="center", va="center", fontsize=9, color="#9ca3af")

        card_specs = [
            (0.18, "#22c55e", f"{rows}", "عدد الصفوف"),
            (0.5, "#eab308", f"{cols}", "عدد الأعمدة"),
            (0.82, "#38bdf8", f"{mem_kb:.1f} KB", "حجم الذاكرة"),
        ]
        for x, color, value, label in card_specs:
            ax.add_patch(
                plt.Rectangle((x - 0.13, 0.53), 0.26, 0.17, transform=ax.transAxes,
                              color=color, alpha=0.12, linewidth=0)
            )
            ax.text(x, 0.63, value, ha="center", va="center",
                    fontsize=18, color="#f9fafb", fontweight="bold")
            ax.text(x, 0.55, ar(label), ha="center", va="center",
                    fontsize=10, color="#e5e7eb")

        ax.text(0.5, 0.30, ar("هذا التقرير يتضمن تحليلًا شاملاً لمفقودات البيانات، "
                              "القيم الفريدة، التوزيعات، الارتباطات، الجاهزية لنماذج ML، "
                              "وملاحظات ذكية آلية تدعم اتخاذ القرار."),
                ha="center", va="center", fontsize=9, color="#e5e7eb", wrap=True)

        ax.text(0.5, 0.05, "Sado Web EDA Report", ha="center", va="center",
                fontsize=8, color="#6b7280")
        pdf.savefig(fig)
        plt.close(fig)

        lines = report_str.split("\n")
        wrapped_lines = []
        for line in lines:
            if re.search(r'[\u0600-\u06FF]', line):
                line = ar(line)
            wrapped_lines.extend(textwrap.wrap(line, width=110) or [""])

        max_lines_per_page = 60
        for i in range(0, len(wrapped_lines), max_lines_per_page):
            page_lines = wrapped_lines[i:i + max_lines_per_page]
            fig = plt.figure(figsize=(8.27, 11.69))
            fig.patch.set_facecolor("white")
            txt_page = "\n".join(page_lines)
            plt.axis("off")
            fig.text(0.03, 0.97, txt_page, va="top", ha="left",
                     fontsize=7, family="DejaVu Sans", color="#111827")
            fig.text(0.5, 0.02, "Sado Web - Advanced EDA Text Report",
                     ha="center", va="center", fontsize=7, color="#6b7280")
            pdf.savefig(fig)
            plt.close(fig)

        missing_counts = df.isna().sum()
        fig, ax = plt.subplots(figsize=(8.27, 4))
        fig.patch.set_facecolor("white")
        colors = ["#f97316" if v > 0 else "#9ca3af" for v in missing_counts]
        ax.bar(range(len(missing_counts)), missing_counts.values, color=colors)
        ax.set_title(ar("عدد القيم الناقصة لكل عمود"), fontsize=12, color="#111827")
        ax.set_ylabel(ar("عدد القيم الناقصة"), fontsize=10, color="#111827")
        ax.set_xticks(range(len(missing_counts)))
        ax.set_xticklabels([ar(str(c)) for c in missing_counts.index],
                           rotation=45, ha="right", fontsize=7)
        ax.grid(axis="y", alpha=0.2)
        fig.tight_layout()
        pdf.savefig(fig)
        plt.close(fig)

        if not numeric_df.empty and numeric_df.shape[1] >= 2:
            corr = numeric_df.corr()
            fig, ax = plt.subplots(figsize=(8, 6))
            fig.patch.set_facecolor("white")
            cax = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
            fig.colorbar(cax, ax=ax, fraction=0.046, pad=0.04)
            ax.set_xticks(range(len(corr.columns)))
            ax.set_yticks(range(len(corr.columns)))
            ax.set_xticklabels(corr.columns, rotation=45, ha="right", fontsize=7)
            ax.set_yticklabels(corr.columns, fontsize=7)
            ax.set_title(ar("خريطة الارتباط بين المتغيرات"), fontsize=12, color="#111827")
            for i in range(len(corr.columns)):
                for j in range(len(corr.columns)):
                    ax.text(j, i, f"{corr.iloc[i, j]:.2f}",
                            ha="center", va="center", fontsize=5, color="black")
            fig.tight_layout()
            pdf.savefig(fig)
            plt.close(fig)

        if not numeric_df.empty:
            num_cols = list(numeric_df.columns)
            for i in range(0, len(num_cols), 4):
                subset = num_cols[i:i + 4]
                fig, axs = plt.subplots(2, 2, figsize=(8.27, 6))
                fig.patch.set_facecolor("white")
                axs = axs.flatten()
                for ax, col in zip(axs, subset):
                    numeric_df[col].dropna().hist(ax=ax, color="#2563eb", alpha=0.85)
                    ax.set_title(ar(str(col)), fontsize=9, color="#111827")
                    ax.grid(alpha=0.2)
                for j in range(len(subset), 4):
                    axs[j].axis("off")
                fig.suptitle(ar("توزيع الأعمدة الرقمية (Histogram)"),
                             fontsize=12, color="#111827")
                fig.tight_layout(rect=[0, 0.03, 1, 0.95])
                pdf.savefig(fig)
                plt.close(fig)

    buf.seek(0)
    return buf


# ========================
# Sidebar: رفع ملف + Templates
# ========================
st.sidebar.title("📂 ملف البيانات")

uploaded_file = st.sidebar.file_uploader("اختر ملف Excel", type=["xlsx", "xls"])

if st.sidebar.button("📦 تحميل بيانات تجريبية"):
    st.session_state.df = sample_dataframe(60)
    st.sidebar.success("تم تحميل بيانات تجريبية لإظهار الميزات ✨")

if uploaded_file is not None:
    try:
        st.session_state.df = pd.read_excel(uploaded_file)
        st.session_state.show_sample_alert = False
        st.sidebar.success("تم تحميل الملف بنجاح ✅")
    except Exception as e:
        st.sidebar.error(f"فشل في قراءة الملف: {e}")

df = st.session_state.df

if st.session_state.get("show_sample_alert"):
    st.info(
        "تم تحميل بيانات تجريبية تلقائياً لعرض الواجهة بشكل كامل. ارفع ملف Excel من القائمة الجانبية أو اضغط زر البيانات التجريبية لتبديلها.",
        icon="✨",
    )

    st.button(
        "إخفاء التنبيه",
        key="dismiss_sample_alert",
        help="إخفاء تنبيه البيانات التجريبية مع إبقائها محملة.",
        on_click=lambda: st.session_state.update(show_sample_alert=False),
    )

if df is not None:
    excel_buf = BytesIO()
    df.to_excel(excel_buf, index=False)
    excel_buf.seek(0)
    st.sidebar.download_button(
        "💾 تنزيل الملف الحالي (Excel)",
        data=excel_buf,
        file_name="cleaned_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

st.sidebar.markdown("---")
st.sidebar.subheader("📊 قوالب لوحة التحكم")

if st.session_state.dashboard_config:
    template = {
        "charts": st.session_state.dashboard_config,
        "filter": st.session_state.dashboard_filter
    }
    template_str = json.dumps(template, ensure_ascii=False, indent=2)
    st.sidebar.download_button(
        "💾 تنزيل قالب Dashboard (JSON)",
        data=template_str.encode("utf-8"),
        file_name="dashboard_template.json",
        mime="application/json",
    )

template_file = st.sidebar.file_uploader(
    "📂 تحميل قالب Dashboard (JSON)", type=["json"], key="tpl_uploader"
)
if template_file is not None:
    try:
        tpl = json.load(template_file)
        st.session_state.dashboard_config = tpl.get("charts", [])
        st.session_state.dashboard_filter = tpl.get("filter", None)
        st.sidebar.success("تم تحميل القالب وتطبيقه.")
    except Exception as e:
        st.sidebar.error(f"خطأ في قراءة القالب: {e}")


# ========================
# كروت سريعة فوق التبويبات
# ========================
if df is not None:
    rows, cols = df.shape
    mem_kb = df.memory_usage(deep=True).sum() / 1024

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""
            <div class="stat-card rows">
                <div class="stat-label">ROWS · الصفوف</div>
                <div class="stat-value">{rows:,}</div>
                <div class="stat-pill">
                    حجم البيانات: {mem_kb:.1f} KB
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="stat-card cols">
                <div class="stat-label">COLUMNS · الأعمدة</div>
                <div class="stat-value">{cols}</div>
                <div class="stat-pill">
                    أنواع مختلفة: {df.dtypes.nunique()}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        missing_pct = (df.isna().any(axis=1).sum() / rows * 100) if rows > 0 else 0
        st.markdown(
            f"""
            <div class="stat-card mem">
                <div class="stat-label">QUALITY · جودة البيانات</div>
                <div class="stat-value">{missing_pct:.1f}%</div>
                <div class="stat-pill">
                    نسبة الصفوف التي تحتوي NaN
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ========================
# Tabs رئيسية
# ========================
tab1, tab2, tab3, tab4 = st.tabs(
    ["🧹 البيانات والتنظيف", "📈 لوحة التحكم (Dashboard)", "📘 التقرير الإحصائي المتقدم", "📝 ملاحظات"]
)

# ========================
# TAB 1: البيانات والتنظيف
# ========================
with tab1:
    st.markdown('<div class="section-title">🧹 البيانات والتنظيف</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">تنظيف ذكي، تعديل أنواع، دمج أعمدة، وإعادة تسمية بشكل احترافي.</div>', unsafe_allow_html=True)

    if df is None:
        st.info("قم برفع ملف Excel من القائمة الجانبية أولاً.")
    else:
        st.write("### 👀 معاينة أولية للبيانات")
        st.dataframe(df.head(100), use_container_width=True)

        col_left, col_right = st.columns([2, 1])

        # --- يسار: عمليات على مستوى الجدول ---
        with col_left:
            st.markdown("#### ⚙️ عمليات عامة على الجدول")
            st.markdown('<span class="helper-label">إزالة التكرار، الصفوف الفارغة، وتعبئة NaN على مستوى الجدول.</span>', unsafe_allow_html=True)

            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("🧹 حذف المكرر"):
                    before = len(df)
                    df = df.drop_duplicates()
                    st.session_state.df = df
                    st.success(f"تم حذف {before - len(df)} صف مكرر.")
            with c2:
                if st.button("🧽 حذف الصفوف الفارغة كلياً"):
                    before = len(df)
                    df = df.dropna(how="all")
                    st.session_state.df = df
                    st.success(f"تم حذف {before - len(df)} صف فارغ بالكامل.")
            with c3:
                fill_val = st.text_input("قيمة تعبئة NaN (كل الجدول)", key="global_fillna")
                if st.button("🩹 تعبئة NaN (كل الجدول)"):
                    if fill_val == "":
                        st.warning("أدخل قيمة أولاً.")
                    else:
                        df = df.fillna(fill_val)
                        st.session_state.df = df
                        st.success("تم تعبئة كل القيم الفارغة.")

            st.markdown("---")
            st.markdown("#### 🔄 أنواع الأعمدة")
            st.write(df.dtypes.astype(str))

            col_change1, col_change2, col_change3 = st.columns(3)
            with col_change1:
                col_to_cast = st.selectbox("اختر عمود لتغيير نوعه", options=df.columns, key="cast_col")
            with col_change2:
                new_type = st.selectbox(
                    "نوع الهدف",
                    options=["string", "int", "float", "bool", "datetime"],
                    key="cast_type",
                )
            with col_change3:
                if st.button("تطبيق تغيير النوع"):
                    try:
                        if new_type == "string":
                            df[col_to_cast] = df[col_to_cast].astype(str)
                        elif new_type == "int":
                            df[col_to_cast] = pd.to_numeric(df[col_to_cast], errors="raise").astype("Int64")
                        elif new_type == "float":
                            df[col_to_cast] = pd.to_numeric(df[col_to_cast], errors="raise").astype(float)
                        elif new_type == "bool":
                            df[col_to_cast] = df[col_to_cast].astype(bool)
                        elif new_type == "datetime":
                            df[col_to_cast] = pd.to_datetime(df[col_to_cast], errors="raise")
                        st.session_state.df = df
                        st.success("تم تغيير النوع بنجاح.")
                    except Exception as e:
                        st.error(f"فشل في تغيير النوع: {e}")

        # --- يمين: تنظيف أعمدة + دمج + إعادة تسمية ---
        with col_right:
            with st.expander("✨ تنظيف عمود واحد", expanded=True):
                col_clean = st.selectbox("اختر عمود للتنظيف", options=df.columns, key="clean_col")
                op = st.selectbox(
                    "اختر العملية",
                    [
                        "Trim",
                        "Normalize Spaces",
                        "lower",
                        "UPPER",
                        "Title Case",
                        "Remove Symbols",
                        "Remove Digits",
                        "Keep Digits Only",
                        "Strip non letters (ع/إنجليزي)",
                        "Replace value",
                        "Drop rows where this column is NaN",
                        "Fill NaN (value)",
                        "Fill NaN (mean)",
                        "Fill NaN (median)",
                        "Fill NaN (mode)",
                    ],
                    key="clean_op",
                )

                extra_param = {}
                if op == "Remove Symbols":
                    extra_param["symbols"] = st.text_input("الرموز المراد حذفها", key="symb")
                if op == "Replace value":
                    extra_param["old"] = st.text_input("القيمة القديمة", key="oldv")
                    extra_param["new"] = st.text_input("القيمة الجديدة", key="newv")
                if op == "Fill NaN (value)":
                    extra_param["fill_value"] = st.text_input("قيمة تعبئة NaN", key="fillv")

                if st.button("تنفيذ تنظيف العمود"):
                    try:
                        if op == "Drop rows where this column is NaN":
                            before = len(df)
                            df = df[~df[col_clean].isna()]
                            st.session_state.df = df
                            st.success(f"تم حذف {before - len(df)} صف.")
                        elif op == "Fill NaN (value)":
                            v = extra_param.get("fill_value", "")
                            if v == "":
                                st.warning("أدخل قيمة.")
                            else:
                                df[col_clean] = df[col_clean].fillna(v)
                                st.session_state.df = df
                                st.success("تم تعبئة NaN بالقيمة المحددة.")
                        elif op == "Fill NaN (mean)":
                            s = pd.to_numeric(df[col_clean], errors="coerce")
                            mean_val = s.mean()
                            df[col_clean] = s.fillna(mean_val)
                            st.session_state.df = df
                            st.success(f"تم تعبئة NaN بالمتوسط: {mean_val}")
                        elif op == "Fill NaN (median)":
                            s = pd.to_numeric(df[col_clean], errors="coerce")
                            median_val = s.median()
                            df[col_clean] = s.fillna(median_val)
                            st.session_state.df = df
                            st.success(f"تم تعبئة NaN بالوسيط: {median_val}")
                        elif op == "Fill NaN (mode)":
                            mode_vals = df[col_clean].mode()
                            if mode_vals.empty:
                                st.warning("لا يوجد mode.")
                            else:
                                mv = mode_vals.iloc[0]
                                df[col_clean] = df[col_clean].fillna(mv)
                                st.session_state.df = df
                                st.success(f"تم تعبئة NaN بـ mode: {mv}")
                        else:
                            s = df[col_clean].astype(str)
                            if op == "Trim":
                                s = s.str.strip()
                            elif op == "Normalize Spaces":
                                s = s.str.replace(r"\s+", " ", regex=True).str.strip()
                            elif op == "lower":
                                s = s.str.lower()
                            elif op == "UPPER":
                                s = s.str.upper()
                            elif op == "Title Case":
                                s = s.str.title()
                            elif op == "Remove Symbols":
                                symbols = extra_param.get("symbols", "")
                                pattern = "[" + re.escape(symbols) + "]"
                                s = s.str.replace(pattern, "", regex=True)
                            elif op == "Remove Digits":
                                s = s.str.replace(r"\d+", "", regex=True)
                            elif op == "Keep Digits Only":
                                s = s.str.replace(r"\D+", "", regex=True)
                            elif op == "Strip non letters (ع/إنجليزي)":
                                s = s.str.replace(r"[^A-Za-z\u0600-\u06FF\s]+", "", regex=True)
                            elif op == "Replace value":
                                old = extra_param.get("old", "")
                                new = extra_param.get("new", "")
                                s = s.replace(old, new)
                            df[col_clean] = s
                            st.session_state.df = df
                            st.success("تم تنفيذ عملية التنظيف.")
                    except Exception as e:
                        st.error(f"خطأ أثناء التنظيف: {e}")

            with st.expander("🔗 دمج أعمدة متعددة", expanded=False):
                merge_cols = st.multiselect("اختر الأعمدة للدمج", options=df.columns, key="merge_cols")
                merge_mode = st.selectbox(
                    "نوع الدمج",
                    ["concat as text (نصي)", "sum as number (جمع رقمي)"],
                    key="merge_mode",
                )
                sep = st.text_input("الفاصل في الدمج النصي", key="merge_sep", value=" ")
                new_col_name = st.text_input("اسم العمود الجديد", key="merge_new")

                if st.button("تنفيذ الدمج"):
                    if len(merge_cols) < 2:
                        st.warning("اختر عمودين أو أكثر.")
                    else:
                        try:
                            if new_col_name.strip() == "":
                                new_col_name = "_".join(merge_cols) + "_merged"
                            if merge_mode.startswith("concat"):
                                res = df[merge_cols[0]].fillna("").astype(str)
                                for c in merge_cols[1:]:
                                    res = res + sep + df[c].fillna("").astype(str)
                                df[new_col_name] = res
                            else:
                                numeric_df = df[merge_cols].apply(pd.to_numeric, errors="coerce")
                                df[new_col_name] = numeric_df.sum(axis=1)
                            st.session_state.df = df
                            st.success(f"تم إنشاء العمود الجديد: {new_col_name}")
                        except Exception as e:
                            st.error(f"خطأ أثناء الدمج: {e}")

            with st.expander("✏️ إعادة تسمية الأعمدة", expanded=False):
                new_names = {}
                for c in df.columns:
                    new_names[c] = st.text_input(f"الاسم الجديد لـ {c}", value=c, key=f"rename_{c}")

                if st.button("تطبيق إعادة التسمية"):
                    mapping = {old: new for old, new in new_names.items() if old != new and new.strip() != ""}
                    if mapping:
                        df = df.rename(columns=mapping)
                        st.session_state.df = df
                        st.success("تم تعديل أسماء الأعمدة.")
                    else:
                        st.info("لا يوجد تغييرات في الأسماء.")


# ========================
# TAB 2: Dashboard
# ========================
with tab2:
    st.markdown('<div class="section-title">📈 لوحة التحكم (Dashboard)</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">ابنِ لوحتك الخاصة: Bar, Line, Pie, KPI مع فلترة ديناميكية وقوالب جاهزة.</div>', unsafe_allow_html=True)

    if df is None:
        st.info("قم برفع ملف Excel أولاً.")
    else:
        cols_all = list(df.columns)

        # فلتر (Slicer)
        st.markdown("### 🎛 فلترة البيانات (Slicer)")
        if cols_all:
            c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
            with c1:
                filter_col = st.selectbox("عمود الفلترة", options=["(لا يوجد)"] + cols_all, key="db_filter_col")
            with c2:
                filter_op = st.selectbox("نوع الشرط", options["=", "contains", ">", "<"], key="db_filter_op")
            with c3:
                filter_val = st.text_input("القيمة", key="db_filter_val")
            with c4:
                apply_filter = st.button("تطبيق الفلتر")
                clear_filter = st.button("مسح الفلتر")

            if apply_filter and filter_col != "(لا يوجد)":
                try:
                    if filter_op in [">", "<"]:
                        series = pd.to_numeric(df[filter_col], errors="coerce")
                        val_num = pd.to_numeric(filter_val, errors="coerce")
                        if np.isnan(val_num):
                            st.warning("قيمة المقارنة يجب أن تكون رقمية.")
                        else:
                            if filter_op == ">":
                                mask = series > val_num
                            else:
                                mask = series < val_num
                            st.session_state.dashboard_filter = {
                                "column": filter_col,
                                "op": filter_op,
                                "value": filter_val,
                            }
                            st.success("تم حفظ إعداد الفلتر.")
                    elif filter_op == "=":
                        _ = df[filter_col].astype(str) == filter_val
                        st.session_state.dashboard_filter = {
                            "column": filter_col,
                            "op": filter_op,
                            "value": filter_val,
                        }
                        st.success("تم حفظ إعداد الفلتر.")
                    elif filter_op == "contains":
                        _ = df[filter_col].astype(str).str.contains(filter_val, na=False)
                        st.session_state.dashboard_filter = {
                            "column": filter_col,
                            "op": filter_op,
                            "value": filter_val,
                        }
                        st.success("تم حفظ إعداد الفلتر.")
                except Exception as e:
                    st.error(f"خطأ في إعداد الفلتر: {e}")

            if clear_filter:
                st.session_state.dashboard_filter = None
                st.success("تم مسح الفلتر.")

        def apply_dashboard_filter(df, flt):
            if flt is None:
                return df
            col = flt.get("column")
            op = flt.get("op")
            val = flt.get("value", "")
            if col not in df.columns:
                return df
            try:
                if op in [">", "<"]:
                    series = pd.to_numeric(df[col], errors="coerce")
                    v = pd.to_numeric(val, errors="coerce")
                    if np.isnan(v):
                        return df
                    if op == ">":
                        return df[series > v]
                    else:
                        return df[series < v]
                elif op == "=":
                    return df[df[col].astype(str) == val]
                elif op == "contains":
                    return df[df[col].astype(str).str.contains(val, na=False)]
                else:
                    return df
            except Exception:
                return df

        db_df = apply_dashboard_filter(df, st.session_state.dashboard_filter)
        st.caption(f"عدد الصفوف بعد الفلتر في الداشبورد: {len(db_df)}")

        # إضافة عنصر جديد
        st.markdown("### ➕ إضافة عنصر جديد إلى لوحة التحكم")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            chart_type = st.selectbox(
                "نوع الشكل",
                [
                    "Bar (Category vs Value)",
                    "Line (Trend)",
                    "Pie (نسب مئوية)",
                    "Scatter (X vs Y)",
                    "Histogram (توزيع)",
                    "KPI (قيمة واحدة)",
                ],
            )
        with c2:
            x_col = st.selectbox("عمود X / الفئة", options=["(بدون)"] + list(db_df.columns))
        with c3:
            numeric_df_dash = db_df.apply(pd.to_numeric, errors="coerce")
            numeric_cols_dash = [c for c in db_df.columns if not numeric_df_dash[c].dropna().empty]
            y_col = st.selectbox("عمود القيمة (Y)", options=["(بدون)"] + numeric_cols_dash)
        with c4:
            agg = st.selectbox("نوع التجميع", options=["None", "sum", "mean", "count"])

        if st.button("➕ إضافة إلى اللوحة"):
            if chart_type != "KPI (قيمة واحدة)" and x_col == "(بدون)":
                st.warning("اختر عمود X.")
            elif chart_type not in ["Histogram (توزيع)", "KPI (قيمة واحدة)", "Pie (نسب مئوية)"] and y_col == "(بدون)":
                st.warning("اختر عمود Y.")
            else:
                st.session_state.dashboard_config.append(
                    {
                        "chart_type": chart_type,
                        "x_col": None if x_col == "(بدون)" else x_col,
                        "y_col": None if y_col == "(بدون)" else y_col,
                        "agg": agg,
                    }
                )
                st.success("تم إضافة العنصر إلى اللوحة.")

        if st.button("🧹 مسح كل عناصر اللوحة"):
            st.session_state.dashboard_config = []
            st.success("تم مسح اللوحة.")

        st.markdown("### 📊 العناصر الحالية في لوحة التحكم")
        if not st.session_state.dashboard_config:
            st.info("لا يوجد عناصر بعد. أضف عنصر من الأعلى.")
        else:
            for i, cfg in enumerate(st.session_state.dashboard_config):
                st.markdown(f"#### عنصر #{i+1}: {cfg['chart_type']}")

                chart_type = cfg["chart_type"]
                x_col = cfg["x_col"]
                y_col = cfg["y_col"]
                agg = cfg["agg"]

                fig = Figure(figsize=(5, 3))
                ax = fig.add_subplot(111)

                try:
                    ddf = apply_dashboard_filter(df, st.session_state.dashboard_filter)
                    if ddf.empty:
                        ax.text(0.5, 0.5, ar("لا يوجد بيانات بعد الفلتر"), ha="center", va="center")
                    else:
                        if chart_type == "Bar (Category vs Value)":
                            numeric_y = pd.to_numeric(ddf[y_col], errors="coerce")
                            data = pd.DataFrame({x_col: ddf[x_col], y_col: numeric_y})
                            if agg == "sum":
                                grouped = data.groupby(x_col)[y_col].sum()
                            elif agg == "mean":
                                grouped = data.groupby(x_col)[y_col].mean()
                            elif agg == "count":
                                grouped = data.groupby(x_col)[y_col].count()
                            else:
                                grouped = data.groupby(x_col)[y_col].mean()
                            ax.bar(grouped.index.astype(str), grouped.values)
                            ax.set_title(ar(f"Bar - {y_col} حسب {x_col} ({agg})"))
                            ax.set_xlabel(ar(x_col))
                            ax.set_ylabel(ar(y_col))
                            ax.tick_params(axis='x', rotation=45)

                        elif chart_type == "Line (Trend)":
                            numeric_y = pd.to_numeric(ddf[y_col], errors="coerce")
                            data = pd.DataFrame({x_col: ddf[x_col], y_col: numeric_y})
                            if agg in ["sum", "mean", "count"]:
                                grouped = getattr(data.groupby(x_col)[y_col], agg)()
                                ax.plot(grouped.index.astype(str), grouped.values, marker="o")
                                ax.set_title(ar(f"Line - {y_col} حسب {x_col} ({agg})"))
                            else:
                                ax.plot(data[x_col].astype(str), data[y_col], marker="o")
                                ax.set_title(ar(f"Line - {y_col} حسب {x_col}"))
                            ax.set_xlabel(ar(x_col))
                            ax.set_ylabel(ar(y_col))
                            ax.tick_params(axis='x', rotation=45)

                        elif chart_type == "Pie (نسب مئوية)":
                            if agg in ["sum", "mean"]:
                                numeric_y = pd.to_numeric(ddf[y_col], errors="coerce")
                                data = pd.DataFrame({x_col: ddf[x_col], y_col: numeric_y})
                                grouped = getattr(data.groupby(x_col)[y_col], agg)()
                            else:
                                grouped = ddf[x_col].value_counts()
                            ax.pie(
                                grouped.values,
                                labels=[ar(str(k)) for k in grouped.index],
                                autopct="%1.1f%%",
                            )
                            ax.set_title(ar(f"Pie - {x_col}"))

                        elif chart_type == "Scatter (X vs Y)":
                            x_num = pd.to_numeric(ddf[x_col], errors="coerce")
                            y_num = pd.to_numeric(ddf[y_col], errors="coerce")
                            mask = ~x_num.isna() & ~y_num.isna()
                            ax.scatter(x_num[mask], y_num[mask], alpha=0.7)
                            ax.set_title(ar(f"Scatter - {y_col} مقابل {x_col}"))
                            ax.set_xlabel(ar(x_col))
                            ax.set_ylabel(ar(y_col))

                        elif chart_type == "Histogram (توزيع)":
                            target = y_col or x_col
                            numeric_target = pd.to_numeric(ddf[target], errors="coerce")
                            numeric_target.dropna().hist(ax=ax, bins=20)
                            ax.set_title(ar(f"Histogram - {target}"))
                            ax.set_xlabel(ar(target))
                            ax.set_ylabel(ar("العدد"))

                        elif chart_type == "KPI (قيمة واحدة)":
                            target = y_col or x_col
                            numeric_target = pd.to_numeric(ddf[target], errors="coerce")
                            if agg == "sum":
                                val = numeric_target.sum()
                                label = "Sum"
                            elif agg == "mean":
                                val = numeric_target.mean()
                                label = "Mean"
                            elif agg == "count":
                                val = numeric_target.count()
                                label = "Count"
                            else:
                                val = numeric_target.mean()
                                label = "Mean"
                            ax.axis("off")
                            ax.text(0.5, 0.6, f"{val:,.2f}", ha="center", va="center",
                                    fontsize=24, fontweight="bold")
                            ax.text(0.5, 0.3, ar(f"{label} of {target}"),
                                    ha="center", va="center", fontsize=12)

                except Exception as e:
                    st.error(f"خطأ في رسم العنصر #{i+1}: {e}")

                st.pyplot(fig)


# ========================
# TAB 3: التقرير الإحصائي المتقدم
# ========================
with tab3:
    st.markdown('<div class="section-title">📘 التقرير الإحصائي المتقدم</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">تقرير شامل (EDA) مع نص عربي + Charts + ملف PDF جاهز للعرض.</div>', unsafe_allow_html=True)

    if df is None:
        st.info("قم برفع ملف Excel أولاً.")
    else:
        st.markdown("### ⚙️ إعدادات التقرير")
        c1, c2, c3 = st.columns(3)
        with c1:
            basic = st.checkbox("ملخص عام + معلومات أساسية", value=True)
            missing = st.checkbox("تحليل Missing Data", value=True)
            unique = st.checkbox("القيم الفريدة", value=True)
        with c2:
            numeric = st.checkbox("تحليل الأعمدة الرقمية", value=True)
            corr = st.checkbox("تحليل الارتباط", value=True)
            text_cols = st.checkbox("تحليل الأعمدة النصية", value=True)
        with c3:
            ml = st.checkbox("جاهزية ML", value=True)
            insights = st.checkbox("ملاحظات ذكية", value=True)

        config = {
            "basic": basic,
            "missing": missing,
            "unique": unique,
            "numeric": numeric,
            "correlation": corr,
            "text": text_cols,
            "ml": ml,
            "insights": insights,
        }

        if st.button("🔍 توليد التقرير"):
            report_str, numeric_df, missing_table = build_advanced_report(df, config)
            st.session_state["last_report"] = (report_str, numeric_df, missing_table)

        if st.session_state["last_report"] is not None:
            report_str, numeric_df, missing_table = st.session_state["last_report"]

            st.markdown("### 🧾 نص التقرير")
            st.text(report_str)

            st.markdown("### 📉 Charts سريعة")

            fig1, ax1 = plt.subplots(figsize=(6, 3))
            missing_counts = df.isna().sum()
            ax1.bar(missing_counts.index.astype(str), missing_counts.values)
            ax1.set_title(ar("عدد القيم الناقصة لكل عمود"))
            ax1.tick_params(axis='x', rotation=45)
            st.pyplot(fig1)

            if not numeric_df.empty and numeric_df.shape[1] >= 2:
                corr_mat = numeric_df.corr()
                fig2, ax2 = plt.subplots(figsize=(5, 4))
                cax = ax2.imshow(corr_mat, cmap="coolwarm", vmin=-1, vmax=1)
                fig2.colorbar(cax, ax=ax2, fraction=0.046, pad=0.04)
                ax2.set_xticks(range(len(corr_mat.columns)))
                ax2.set_yticks(range(len(corr_mat.columns)))
                ax2.set_xticklabels(corr_mat.columns, rotation=45, ha="right", fontsize=7)
                ax2.set_yticklabels(corr_mat.columns, fontsize=7)
                ax2.set_title(ar("خريطة الارتباط"))
                st.pyplot(fig2)

            st.markdown("### 📁 تنزيل التقرير كـ PDF")
            pdf_buf = create_pdf_report(df, config)
            st.download_button(
                "⬇️ تحميل PDF",
                data=pdf_buf,
                file_name="sado_eda_report.pdf",
                mime="application/pdf",
            )
        else:
            st.info("اضغط على زر (توليد التقرير) لعرض النتائج.")


# ========================
# TAB 4: ملاحظات
# ========================
with tab4:
    st.markdown('<div class="section-title">📝 ملاحظاتك على المشروع</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">اكتب أفكارك، insights، وخطة تطوير الـ BI الخاص بك.</div>', unsafe_allow_html=True)

    notes = st.text_area("اكتب ملاحظاتك / أفكارك / TODOs هنا:", height=300, key="notes")
    st.caption("هذه الملاحظات تبقى في الواجهة فقط (لا تُحفظ في ملف خارجي تلقائياً).")


