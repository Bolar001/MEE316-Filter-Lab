 # =============================================================================
#  MEE 316 — NETWORK ANALYSIS & SYNTHESIS
#  COMPLETE FILTER FREQUENCY RESPONSE ANALYSER
#  Features: LPF · HPF · BPF · BSF | Orders 1,2,4,6,8 | Phase Response | Multi-dB
#  Built with: Python · NumPy · Plotly · Streamlit
#
#  HOW TO RUN:
#    python -m streamlit run app.py
# =============================================================================

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="EEE 316 · Filter Lab", page_icon="🎛️", layout="wide")

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0a0f1e; color: #e2e8f0; font-family: 'Segoe UI', sans-serif; }
    button, select, div[data-baseweb="select"], div[data-baseweb="select"] *,
    div[data-baseweb="radio"] *, .stRadio label, .stSelectbox label,
    [role="option"], [role="listbox"], .stButton > button,
    div[data-testid="stNumberInput"] button { cursor: pointer !important; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1f2d 0%, #0a1628 100%);
        border-right: 2px solid #0891b2;
    }
    [data-testid="stSidebar"] * { color: #cbd5e1 !important; }
    .page-banner {
        background: linear-gradient(135deg, #0891b2 0%, #0f172a 60%);
        border-radius: 12px; padding: 20px 28px; margin-bottom: 20px;
        border-left: 5px solid #22d3ee;
    }
    .page-banner h1 { color: #fff !important; margin: 0; font-size: 26px; }
    .page-banner p  { color: #94a3b8; margin: 4px 0 0; font-size: 13px; }
    .info-box {
        background: #0f172a; border: 1px solid #1e3a5f; border-left: 4px solid #22d3ee;
        border-radius: 8px; padding: 14px 18px; margin: 10px 0;
        font-family: 'Courier New', monospace; font-size: 13px;
    }
    .step-box {
        background: #0f2218; border: 1px solid #166534; border-left: 4px solid #22c55e;
        border-radius: 8px; padding: 12px 16px; margin: 7px 0; font-size: 13px;
    }
    .warn-box {
        background: #1c1407; border: 1px solid #854d0e; border-left: 4px solid #f59e0b;
        border-radius: 8px; padding: 12px 16px; margin: 10px 0; font-size: 13px;
    }
    [data-testid="metric-container"] {
        background: #0f172a; border: 1px solid #1e3a5f; border-top: 3px solid #0891b2;
        border-radius: 10px; padding: 14px;
    }
    .section-title {
        color: #22d3ee; font-size: 16px; font-weight: 700; letter-spacing: 1px;
        text-transform: uppercase; border-bottom: 1px solid #1e3a5f;
        padding-bottom: 6px; margin: 16px 0 10px;
    }
    hr { border-color: #1e3a5f; }
</style>
""", unsafe_allow_html=True)


# =============================================================================
#  MATHEMATICS
# =============================================================================

sqrt2 = np.sqrt(2)

def butterworth_LPF(w, wc, n):
    return 1.0 / np.sqrt(1 + (w / wc) ** (2 * n))

def butterworth_LPF_phase(w, wc, n):
    return -n * np.degrees(np.arctan(w / wc))

def butterworth_HPF(w, wc, n):
    return (w / wc) ** n / np.sqrt(1 + (w / wc) ** (2 * n))

def butterworth_HPF_phase(w, wc, n):
    w = np.asarray(w, dtype=float)
    return 90 - n * np.degrees(np.arctan(wc / np.where(w == 0, 1e-12, w)))

def butterworth_BPF(w, wc1, wc2, n):
    bw   = wc2 - wc1
    prod = wc1 * wc2
    w    = np.asarray(w, dtype=float)
    u    = np.abs((w**2 - prod) / (bw * np.where(w == 0, 1e-12, w)))
    return 1.0 / np.sqrt(1 + u ** (2 * n))

def butterworth_BPF_phase(w, wc1, wc2, n):
    bw   = wc2 - wc1
    prod = wc1 * wc2
    w    = np.asarray(w, dtype=float)
    return np.degrees(np.arctan(bw * w / (prod - w**2 + 1e-12)))

def butterworth_BSF(w, wc1, wc2, n):
    bw   = wc2 - wc1
    prod = wc1 * wc2
    w    = np.asarray(w, dtype=float)
    u    = np.abs((w**2 - prod) / (bw * np.where(w == 0, 1e-12, w)))
    return u**n / np.sqrt(1 + u ** (2 * n))

def butterworth_BSF_phase(w, wc1, wc2, n):
    bw   = wc2 - wc1
    prod = wc1 * wc2
    w    = np.asarray(w, dtype=float)
    return np.degrees(np.arctan((prod - w**2) / (bw * w + 1e-12)))

def to_dB(mag):
    return 20 * np.log10(np.where(mag > 0, mag, 1e-12))


# =============================================================================
#  SIDEBAR
# =============================================================================

with st.sidebar:
    st.markdown("### 🎛️ Filter Lab Controls")
    st.markdown("---")

    st.markdown("**① Select Filter Type**")
    filter_type = st.selectbox(
        "Filter", ["LPF — Low-Pass", "HPF — High-Pass", "BPF — Band-Pass", "BSF — Band-Stop"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("**② Select Filter Order**")
    order_options = ["1st", "2nd", "4th", "6th", "8th"]
    order_select = st.selectbox("Order", order_options, index=0, label_visibility="collapsed")
    order_n = int(order_select.replace("st", "").replace("nd", "").replace("rd", "").replace("th", ""))
    order_label = order_select + " Order"

    st.markdown("---")
    st.markdown("**③ Cutoff Frequencies**")
    is_band = filter_type in ["BPF — Band-Pass", "BSF — Band-Stop"]

    if not is_band:
        wc  = st.number_input("Wc (rad/s)", value=1.0, step=0.5, min_value=0.1)
        wc1 = wc2 = None
        st.markdown(f"""
        <div class='info-box'>
        Wc = <b style='color:#22d3ee'>{wc} rad/s</b>
        </div>""", unsafe_allow_html=True)
    else:
        wc1 = st.number_input("Wc1 — Lower (rad/s)", value=4.0, step=0.5, min_value=0.1)
        wc2 = st.number_input("Wc2 — Upper (rad/s)", value=10.0, step=0.5, min_value=0.1)
        wc  = None
        bw_s   = wc2 - wc1
        prod_s = wc1 * wc2
        st.markdown(f"""
        <div class='info-box'>
        Wc1 = <b style='color:#22d3ee'>{wc1}</b><br>
        Wc2 = <b style='color:#22d3ee'>{wc2}</b><br>
        BW = <b style='color:#22c55e'>{bw_s:.1f}</b><br>
        W1×W2 = <b style='color:#22c55e'>{prod_s:.1f}</b>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**④ Frequency Sweep**")
    w_min = st.number_input("ω min", value=0.2, step=0.1, min_value=0.01)
    w_max = st.number_input("ω max", value=100.0, step=10.0)
    plot_scale = st.radio("X-axis scale", ["Linear", "Log"], horizontal=True)

    st.markdown("---")
    st.markdown("**⑤ Multi-dB Reference Lines**")
    show_db_minus1 = st.checkbox("−1 dB", value=True)
    show_db_minus3 = st.checkbox("−3 dB (half power)", value=True)
    show_db_minus6 = st.checkbox("−6 dB", value=True)
    show_db_minus10 = st.checkbox("−10 dB", value=True)
    show_db_minus20 = st.checkbox("−20 dB", value=True)

    st.markdown("---")
    st.markdown("""
    <small style='color:#64748b;'>
    MEE 316 · Network Analysis<br>
    Python · NumPy · Plotly · Streamlit
    </small>""", unsafe_allow_html=True)


# =============================================================================
#  ACTIVE FILTER
# =============================================================================

COLORS = {
    "LPF — Low-Pass" : "#22d3ee",
    "HPF — High-Pass": "#22c55e",
    "BPF — Band-Pass": "#a78bfa",
    "BSF — Band-Stop": "#fb923c",
}
ac = COLORS[filter_type]
sname = filter_type.split("—")[0].strip()

if filter_type == "LPF — Low-Pass":
    Hfn_mag   = lambda w: butterworth_LPF(w, wc, order_n)
    Hfn_phase = lambda w: butterworth_LPF_phase(w, wc, order_n)
    ref_x     = [wc]
elif filter_type == "HPF — High-Pass":
    Hfn_mag   = lambda w: butterworth_HPF(w, wc, order_n)
    Hfn_phase = lambda w: butterworth_HPF_phase(w, wc, order_n)
    ref_x     = [wc]
elif filter_type == "BPF — Band-Pass":
    Hfn_mag   = lambda w: butterworth_BPF(w, wc1, wc2, order_n)
    Hfn_phase = lambda w: butterworth_BPF_phase(w, wc1, wc2, order_n)
    ref_x     = [wc1, wc2]
else:  # BSF
    Hfn_mag   = lambda w: butterworth_BSF(w, wc1, wc2, order_n)
    Hfn_phase = lambda w: butterworth_BSF_phase(w, wc1, wc2, order_n)
    ref_x     = [wc1, wc2]


# =============================================================================
#  MAIN PAGE
# =============================================================================

st.markdown(f"""
<div class='page-banner'>
<h1>🎛️ MEE 316 — Filter Frequency Response Lab</h1>
<p>Network Analysis & Synthesis &nbsp;·&nbsp;
NLPF: H(s) = 1/(s+1) &nbsp;·&nbsp;
Active: <b style='color:#22d3ee'>{filter_type} · {order_label}</b></p>
</div>
""", unsafe_allow_html=True)

# Filter type cards
st.markdown('<div class="section-title">Filter Types</div>', unsafe_allow_html=True)
cols = st.columns(4)
cards_info = [
    ("LPF — Low-Pass",  "#22d3ee", "LPF", "Passes: LOW"),
    ("HPF — High-Pass", "#22c55e", "HPF", "Passes: HIGH"),
    ("BPF — Band-Pass", "#a78bfa", "BPF", "Passes: W1-W2"),
    ("BSF — Band-Stop", "#fb923c", "BSF", "Blocks: W1-W2"),
]
for col, (fname, color, abbr, desc) in zip(cols, cards_info):
    is_active = fname == filter_type
    bg = f"background:{'#0e2a3a' if is_active else '#0f172a'}"
    border = f"border:2px solid {color if is_active else '#1e3a5f'}"
    with col:
        st.markdown(f"""
        <div style='{bg};{border};border-radius:10px;padding:12px;text-align:center;'>
        <div style='font-size:16px;font-weight:800;color:{color};'>{abbr}</div>
        <div style='font-size:10px;color:#94a3b8;margin:6px 0;'>{desc}</div>
        {'<div style="margin-top:4px;font-size:9px;background:'+color+';color:#000;border-radius:10px;padding:1px 8px;">✅ ACTIVE</div>' if is_active else ''}
        </div>""", unsafe_allow_html=True)

st.markdown("&nbsp;")
st.markdown(f"<small style='color:#94a3b8;'>Order: **{order_label}**</small>", unsafe_allow_html=True)
st.markdown("---")

# Metrics
st.markdown('<div class="section-title">Key Values at Cutoff</div>', unsafe_allow_html=True)
mcols = st.columns(len(ref_x) + 2)
for i, wr in enumerate(ref_x):
    mag = float(Hfn_mag(np.array([float(wr)]))[0])
    with mcols[i]:
        st.metric(f"|H| at ω={wr}", f"{mag:.5f}", f"{to_dB(mag):.2f} dB")
with mcols[len(ref_x)]:
    st.metric("−3 dB ref", "0.70711", "= 1/√2")
with mcols[len(ref_x)+1]:
    bw_display = (wc2-wc1) if is_band else wc
    st.metric("BW / Wc", f"{bw_display:.1f} rad/s")

st.markdown("""
<div class='warn-box'>
⚠️ <b>−3 dB Rule:</b> At cutoff, |H(jω)| = 0.70711 (half power). 
Higher orders have sharper roll-off. Phase shifts 45°/decade for LPF/HPF near cutoff.
</div>""", unsafe_allow_html=True)

st.markdown("---")

# ===== GENERATE ALL DATA =====
omega_plot = np.linspace(w_min, w_max, 2000)
mag_plot   = Hfn_mag(omega_plot)
db_plot    = np.clip(to_dB(mag_plot), -80, 5)
phase_plot = Hfn_phase(omega_plot)
xtype      = "log" if plot_scale == "Log" else "linear"

st.markdown('<div class="section-title">Frequency Response Plots</div>', unsafe_allow_html=True)
st.info("💡 **Mobile tip:** Scroll down to see all 4 graphs")

# Create 4 separate figures
config = {
    "responsive": True, "displayModeBar": True, "displaylogo": False,
    "modeBarButtonsToRemove": ["lasso2d", "select2d"]
}

# Plot 1: Linear Magnitude
fig1 = go.Figure()
fig1.add_trace(go.Scatter(x=omega_plot, y=mag_plot, name="|H(jω)|",
    line=dict(color=ac, width=2.5), hovertemplate="ω=%{x:.2f}<br>|H|=%{y:.5f}<extra></extra>"))
for xval in ref_x:
    fig1.add_vline(x=xval, line_dash="dot", line_color="#f59e0b", line_width=1.5)
fig1.add_hline(y=1/sqrt2, line_dash="dash", line_color="#f87171", line_width=1.5,
    annotation_text="−3dB (0.707)", annotation_font_color="#f87171")
fig1.update_layout(
    title=f"{sname} {order_label} — Linear Magnitude |H(jω)|",
    xaxis_title="ω (rad/s)", yaxis_title="|H(jω)|",
    height=400, paper_bgcolor="#0a0f1e", plot_bgcolor="#0f172a",
    font=dict(color="#e2e8f0"), xaxis_type=xtype, xaxis=dict(gridcolor="#1e293b"),
    yaxis=dict(gridcolor="#1e293b"), hovermode="x unified"
)

# Plot 2: dB Magnitude
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=omega_plot, y=db_plot, name="dB",
    line=dict(color=ac, width=2.5), hovertemplate="ω=%{x:.2f}<br>dB=%{y:.3f}<extra></extra>"))
for xval in ref_x:
    fig2.add_vline(x=xval, line_dash="dot", line_color="#f59e0b", line_width=1.5)
# Add dB reference lines
if show_db_minus1:
    fig2.add_hline(y=-1, line_dash="dash", line_color="#94a3b8", line_width=1)
if show_db_minus3:
    fig2.add_hline(y=-3, line_dash="dash", line_color="#f87171", line_width=1.5,
        annotation_text="−3 dB", annotation_font_color="#f87171")
if show_db_minus6:
    fig2.add_hline(y=-6, line_dash="dash", line_color="#fbbf24", line_width=1)
if show_db_minus10:
    fig2.add_hline(y=-10, line_dash="dash", line_color="#60a5fa", line_width=1)
if show_db_minus20:
    fig2.add_hline(y=-20, line_dash="dash", line_color="#818cf8", line_width=1)
fig2.update_layout(
    title=f"{sname} {order_label} — Bode Plot (dB)",
    xaxis_title="ω (rad/s)", yaxis_title="dB",
    height=400, paper_bgcolor="#0a0f1e", plot_bgcolor="#0f172a",
    font=dict(color="#e2e8f0"), xaxis_type=xtype, xaxis=dict(gridcolor="#1e293b"),
    yaxis=dict(gridcolor="#1e293b"), hovermode="x unified"
)

# Plot 3: Phase Response
fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=omega_plot, y=phase_plot, name="Phase",
    line=dict(color="#f59e0b", width=2.5), hovertemplate="ω=%{x:.2f}<br>Phase=%{y:.1f}°<extra></extra>"))
for xval in ref_x:
    fig3.add_vline(x=xval, line_dash="dot", line_color="#f59e0b", line_width=1.5)
fig3.add_hline(y=0, line_dash="dash", line_color="#64748b", line_width=1)
fig3.update_layout(
    title=f"{sname} {order_label} — Phase Response",
    xaxis_title="ω (rad/s)", yaxis_title="Phase (°)",
    height=400, paper_bgcolor="#0a0f1e", plot_bgcolor="#0f172a",
    font=dict(color="#e2e8f0"), xaxis_type=xtype, xaxis=dict(gridcolor="#1e293b"),
    yaxis=dict(gridcolor="#1e293b"), hovermode="x unified"
)

# Plot 4: dB vs Phase
fig4 = go.Figure()
fig4.add_trace(go.Scatter(x=phase_plot, y=db_plot, name="dB vs Phase",
    line=dict(color=ac, width=2.5), hovertemplate="Phase=%{x:.1f}°<br>dB=%{y:.3f}<extra></extra>"))
fig4.update_layout(
    title=f"{sname} {order_label} — dB vs Phase (Nyquist-style)",
    xaxis_title="Phase (°)", yaxis_title="dB",
    height=400, paper_bgcolor="#0a0f1e", plot_bgcolor="#0f172a",
    font=dict(color="#e2e8f0"), xaxis=dict(gridcolor="#1e293b"),
    yaxis=dict(gridcolor="#1e293b"), hovermode="x unified"
)

# Display plots in responsive 2-column layout
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig1, use_container_width=True, config=config)
with col2:
    st.plotly_chart(fig2, use_container_width=True, config=config)

col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(fig3, use_container_width=True, config=config)
with col4:
    st.plotly_chart(fig4, use_container_width=True, config=config)

st.markdown("---")

# ===== TABLE =====
st.markdown('<div class="section-title">Frequency Response Table (ω = 1 → 100)</div>', unsafe_allow_html=True)

omega_table = np.arange(1, 102, 1, dtype=float)
mag_table   = Hfn_mag(omega_table)
phase_table = Hfn_phase(omega_table)
db_table    = to_dB(mag_table)

def region(w):
    if filter_type == "LPF — Low-Pass":
        return "Passband ✅" if w <= wc else "Stopband"
    elif filter_type == "HPF — High-Pass":
        return "Passband ✅" if w >= wc else "Stopband"
    elif filter_type == "BPF — Band-Pass":
        return "Passband ✅" if wc1 <= w <= wc2 else "Stopband"
    else:
        return "Stopband" if wc1 <= w <= wc2 else "Passband ✅"

df = pd.DataFrame({
    "ω (rad/s)"    : omega_table,
    "|H(jω)|"      : np.round(mag_table, 5),
    "|H(jω)| dB"   : np.round(db_table, 3),
    "Phase (°)"    : np.round(phase_table, 2),
    "Region"       : [region(w) for w in omega_table]
})

def highlight(row):
    if "Passband" in str(row["Region"]):
        return ["background-color:#0e2a3a; color:#67e8f9"] * len(row)
    return [""] * len(row)

st.dataframe(df.style.apply(highlight, axis=1), use_container_width=True, height=600)

st.download_button(
    label=f"⬇ Download {sname} {order_label} Table as CSV",
    data=df.to_csv(index=False),
    file_name=f"{sname}_{order_label}_table.csv",
    mime="text/csv"
)

st.markdown("---")

# ===== FORMULAS =====
with st.expander("📖 Filter Formulas & Key Concepts"):
    st.markdown(f"""
    **{sname} {order_label} — Transfer Function:**
    - All derived from NLPF: H(s) = 1/(s+1)
    - Magnitude: |H(jω)| = 1 / √(1 + (ω/Wc)^{2*order_n})
    - dB: |H(jω)|_dB = 20 × log₁₀(|H(jω)|)
    - Phase: ∠H(jω) in degrees

    **Multi-dB Reference Levels (Always):**
    - −1 dB = 0.891 magnitude
    - −3 dB = 0.707 magnitude ← **STANDARD (half power)**
    - −6 dB = 0.501 magnitude
    - −10 dB = 0.316 magnitude
    - −20 dB = 0.1 magnitude
    """)

st.markdown("""
<div style='text-align:center;color:#334155;font-size:11px;margin-top:24px;padding:10px;border-top:1px solid #1e3a5f;'>
MEE 316 · Network Analysis & Synthesis ·
LPF · HPF · BPF · BSF · Magnitude · Phase · Multi-dB ·
Python · NumPy · Plotly · Streamlit
</div>
""", unsafe_allow_html=True)
