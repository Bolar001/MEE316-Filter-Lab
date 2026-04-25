 # =============================================================================
#  MEE 316 — NETWORK ANALYSIS & SYNTHESIS
#  COMPLETE FILTER FREQUENCY RESPONSE ANALYSER
#  Features: LPF · HPF · BPF · BSF | Orders 1,2,4,6,8 | Phase Response | Multi-dB
#  Built with: Python · NumPy · Plotly · Streamlit
#
#  HOW TO RUN:
#    python -m streamlit run bandpass_streamlit.py
# =============================================================================

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="MEE 316 · Filter Lab", page_icon="🎛️", layout="wide")

# ── Custom CSS ─────────────────────────────────────────────────────────────────
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
#  MATHEMATICS — Butterworth filters with phase response
# =============================================================================

sqrt2 = np.sqrt(2)

def butterworth_LPF(w, wc, n):
    return 1.0 / np.sqrt(1 + (w / wc) ** (2 * n))

def butterworth_LPF_phase(w, wc, n):
    """Phase in degrees: -n * arctan(w/Wc)"""
    return -n * np.degrees(np.arctan(w / wc))

def butterworth_HPF(w, wc, n):
    return (w / wc) ** n / np.sqrt(1 + (w / wc) ** (2 * n))

def butterworth_HPF_phase(w, wc, n):
    """Phase in degrees: 90 - n * arctan(Wc/w)"""
    w = np.asarray(w, dtype=float)
    return 90 - n * np.degrees(np.arctan(wc / np.where(w == 0, 1e-12, w)))

def butterworth_BPF(w, wc1, wc2, n):
    bw   = wc2 - wc1
    prod = wc1 * wc2
    w    = np.asarray(w, dtype=float)
    u    = np.abs((w**2 - prod) / (bw * np.where(w == 0, 1e-12, w)))
    return 1.0 / np.sqrt(1 + u ** (2 * n))

def butterworth_BPF_phase(w, wc1, wc2, n):
    """BPF phase: numerator phase - denominator phase"""
    bw   = wc2 - wc1
    prod = wc1 * wc2
    w    = np.asarray(w, dtype=float)
    # Simplified: phase goes from 0 at low freq through 90° at center to 180° at high freq
    numerator_phase = np.degrees(np.arctan(bw * w / (prod - w**2 + 1e-12)))
    return numerator_phase

def butterworth_BSF(w, wc1, wc2, n):
    bw   = wc2 - wc1
    prod = wc1 * wc2
    w    = np.asarray(w, dtype=float)
    u    = np.abs((w**2 - prod) / (bw * np.where(w == 0, 1e-12, w)))
    return u**n / np.sqrt(1 + u ** (2 * n))

def butterworth_BSF_phase(w, wc1, wc2, n):
    """BSF phase: inverse of BPF"""
    bw   = wc2 - wc1
    prod = wc1 * wc2
    w    = np.asarray(w, dtype=float)
    numerator_phase = np.degrees(np.arctan((prod - w**2) / (bw * w + 1e-12)))
    return numerator_phase

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
    st.markdown("**⑤ Select Plots to Display**")
    show_linear = st.checkbox("Linear Magnitude", value=True)
    show_bode = st.checkbox("Bode (dB)", value=True)
    show_phase = st.checkbox("Phase Response", value=True)
    show_nyquist = st.checkbox("dB vs Phase", value=True)

    st.markdown("---")
    st.markdown("**⑥ Multi-dB Reference Lines**")
    st.write("<small>Check which dB levels to show:</small>", unsafe_allow_html=True)
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
    tf        = f"H(s) = 1 / (Butterworth {order_label} LPF, Wc={wc})"
    mag_eq    = f"|H(jω)| = 1 / √(1 + (ω/{wc})^{2*order_n})"
    sub_rule  = "s → s/Wc"
    ref_x     = [wc]
elif filter_type == "HPF — High-Pass":
    Hfn_mag   = lambda w: butterworth_HPF(w, wc, order_n)
    Hfn_phase = lambda w: butterworth_HPF_phase(w, wc, order_n)
    tf        = f"H(s) = {order_label} HPF, Wc={wc}"
    mag_eq    = f"|H(jω)| = (ω/{wc})^{order_n} / √(1 + (ω/{wc})^{2*order_n})"
    sub_rule  = "s → Wc/s"
    ref_x     = [wc]
elif filter_type == "BPF — Band-Pass":
    bw, prod = wc2 - wc1, wc1 * wc2
    Hfn_mag   = lambda w: butterworth_BPF(w, wc1, wc2, order_n)
    Hfn_phase = lambda w: butterworth_BPF_phase(w, wc1, wc2, order_n)
    tf        = f"H(s) = {order_label} BPF | Wc1={wc1}, Wc2={wc2}"
    mag_eq    = f"|H(jω)| = 1 / √(1 + u^{2*order_n})  [u = |(ω²−{prod:.0f})|/({bw:.0f}ω)]"
    sub_rule  = f"s → (s²+{prod:.0f}) / ({bw:.0f}s)"
    ref_x     = [wc1, wc2]
else:  # BSF
    bw, prod = wc2 - wc1, wc1 * wc2
    Hfn_mag   = lambda w: butterworth_BSF(w, wc1, wc2, order_n)
    Hfn_phase = lambda w: butterworth_BSF_phase(w, wc1, wc2, order_n)
    tf        = f"H(s) = {order_label} BSF | Wc1={wc1}, Wc2={wc2}"
    mag_eq    = f"|H(jω)| = u^{order_n} / √(1 + u^{2*order_n})  [u = |(ω²−{prod:.0f})|/({bw:.0f}ω)]"
    sub_rule  = f"s → {bw:.0f}s / (s²+{prod:.0f})"
    ref_x     = [wc1, wc2]


# =============================================================================
#  MAIN PAGE
# =============================================================================

st.markdown(f"""
<div class='page-banner'>
<h1>🎛️ MEE 316 — Filter Frequency Response Lab</h1>
<p>Network Analysis & Synthesis &nbsp;·&nbsp;
NLPF: H(s) = 1/(s+1) &nbsp;·&nbsp;
Active: <b style='color:#22d3ee'>{filter_type} · {order_label}</b> &nbsp;·&nbsp;
dB = 20·log₁₀|H(jω)| &nbsp;·&nbsp; Phase in degrees</p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-title">Filter Types</div>', unsafe_allow_html=True)
cols = st.columns(4)
cards_info = [
    ("LPF — Low-Pass",  "#22d3ee", "LPF", "s → s/Wc",          "Passes: LOW"),
    ("HPF — High-Pass", "#22c55e", "HPF", "s → Wc/s",           "Passes: HIGH"),
    ("BPF — Band-Pass", "#a78bfa", "BPF", "s → (s²+W₁W₂)/BW·s","Passes: W1-W2"),
    ("BSF — Band-Stop", "#fb923c", "BSF", "s → BW·s/(s²+W₁W₂)","Blocks: W1-W2"),
]
for col, (fname, color, abbr, sub, desc) in zip(cols, cards_info):
    is_active = fname == filter_type
    bg = f"background:{'#0e2a3a' if is_active else '#0f172a'}"
    border = f"border:2px solid {color if is_active else '#1e3a5f'}"
    with col:
        st.markdown(f"""
        <div style='{bg};{border};border-radius:10px;padding:14px;text-align:center;'>
        <div style='font-size:20px;font-weight:800;color:{color};'>{abbr}</div>
        <div style='font-size:10px;color:#64748b;margin:4px 0;'>{sub}</div>
        <div style='font-size:11px;color:#94a3b8;'>{desc}</div>
        {'<div style="margin-top:6px;font-size:10px;background:'+color+';color:#000;border-radius:10px;padding:1px 8px;">ACTIVE</div>' if is_active else ''}
        </div>""", unsafe_allow_html=True)

st.markdown("&nbsp;")
badge_html = '<div style="margin:8px 0;"><span style="color:#94a3b8;font-size:13px;">Order: </span>'
for opt in ["1st", "2nd", "4th", "6th", "8th"]:
    opt_n = int(opt.replace("st", "").replace("nd", "").replace("rd", "").replace("th", ""))
    badge_html += f"<span style='display:inline-block;background:#0e7490;color:#fff;border-radius:20px;padding:3px 12px;font-size:12px;margin:2px;'>{'✅ ' if order_n==opt_n else ''}{opt}</span>"
badge_html += "</div>"
st.markdown(badge_html, unsafe_allow_html=True)
st.markdown("---")

st.markdown('<div class="section-title">Transfer Function & Formula</div>', unsafe_allow_html=True)
col_a, col_b = st.columns(2)
with col_a:
    st.markdown(f"""
    <div class='info-box'>
    <b style='color:#f59e0b;'>NLPF (Starting Point)</b><br>
    H(s) = 1 / (s + 1)<br><br>
    <b style='color:#f59e0b;'>Frequency Substitution ({sname})</b><br>
    {sub_rule}<br><br>
    <b style='color:#f59e0b;'>Resulting {sname} ({order_label})</b><br>
    {tf}
    </div>""", unsafe_allow_html=True)
with col_b:
    st.markdown(f"""
    <div class='info-box'>
    <b style='color:#22d3ee;'>Magnitude Formula</b><br>
    {mag_eq}<br><br>
    <b style='color:#22d3ee;'>dB Formula</b><br>
    |H(jω)|_dB = 20 × log₁₀( |H(jω)| )<br><br>
    <b style='color:#22d3ee;'>Phase Formula</b><br>
    ∠H(jω) = phase in degrees
    </div>""", unsafe_allow_html=True)

st.markdown("---")

with st.expander(f"📐 Step-by-Step Derivation — {sname} {order_label}", expanded=False):
    st.markdown(f"""
    <div class='step-box'><b style='color:#22c55e;'>Step 1 — NLPF</b><br>H(s) = 1/(s+1)</div>
    <div class='step-box'><b style='color:#22c55e;'>Step 2 — {sname} substitution</b><br>{sub_rule}</div>
    <div class='step-box'><b style='color:#22c55e;'>Step 3 — Transfer Function</b><br>{tf}</div>
    <div class='step-box'><b style='color:#22c55e;'>Step 4 — Frequency Response</b><br>{mag_eq}</div>
    <div class='step-box'><b style='color:#22c55e;'>Step 5 — Phase & dB</b><br>
    Phase = ∠H(jω) in degrees &nbsp;|&nbsp; dB = 20·log₁₀(|H(jω)|)</div>
    """, unsafe_allow_html=True)

st.markdown("---")

st.markdown('<div class="section-title">Key Values at Cutoff</div>', unsafe_allow_html=True)
mcols = st.columns(len(ref_x) + 2)
for i, wr in enumerate(ref_x):
    mag = float(Hfn_mag(np.array([float(wr)]))[0])
    phase = float(Hfn_phase(np.array([float(wr)]))[0])
    with mcols[i]:
        st.metric(f"|H| at ω={wr}", f"{mag:.5f}", f"{to_dB(mag):.2f} dB")

with mcols[len(ref_x)]:
    st.metric("−3 dB ref", "0.70711", "= 1/√2")
with mcols[len(ref_x)+1]:
    bw_display = (wc2-wc1) if is_band else wc
    st.metric("BW / Wc", f"{bw_display:.1f} rad/s")

st.markdown("""
<div class='warn-box'>
⚠️ <b>−3 dB Rule:</b> At cutoff, |H(jω)| = 0.70711 (half power). Higher orders have sharper roll-off.
For LPF/HPF: phase shifts 45°/decade near cutoff. BPF shifts 90° at center frequency.
</div>""", unsafe_allow_html=True)

st.markdown("---")

# Calculate data BEFORE tabs
omega_plot = np.linspace(w_min, w_max, 2000)
mag_plot   = Hfn_mag(omega_plot)
db_plot    = np.clip(to_dB(mag_plot), -80, 5)
phase_plot = Hfn_phase(omega_plot)
xtype      = "log" if plot_scale == "Log" else "linear"

# Create full figure for "All Plots" tab
fig = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        f"{sname} {order_label} — Linear |H(jω)|",
        f"{sname} {order_label} — Bode Plot (Magnitude)",
        f"{sname} {order_label} — Phase Response",
        f"dB vs Phase (Nyquist-style)"
    ),
    specs=[[{"secondary_y": False}, {"secondary_y": False}],
           [{"secondary_y": False}, {"secondary_y": False}]],
    vertical_spacing=0.12, horizontal_spacing=0.1
)

# Add traces to full figure
if show_linear:
    fig.add_trace(go.Scatter(
        x=omega_plot, y=mag_plot, name="|H(jω)|",
        line=dict(color=ac, width=2.5),
        hovertemplate="ω=%{x:.2f}<br>|H|=%{y:.5f}<extra></extra>"
    ), row=1, col=1)

if show_bode:
    fig.add_trace(go.Scatter(
        x=omega_plot, y=db_plot, name="dB",
        line=dict(color=ac, width=2.5),
        hovertemplate="ω=%{x:.2f}<br>dB=%{y:.3f}<extra></extra>"
    ), row=1, col=2)

if show_phase:
    fig.add_trace(go.Scatter(
        x=omega_plot, y=phase_plot, name="Phase",
        line=dict(color="#f59e0b", width=2.5),
        hovertemplate="ω=%{x:.2f}<br>Phase=%{y:.1f}°<extra></extra>"
    ), row=2, col=1)

if show_nyquist:
    fig.add_trace(go.Scatter(
        x=phase_plot, y=db_plot, name="dB vs Phase",
        mode="lines", line=dict(color=ac, width=2.5),
        hovertemplate="Phase=%{x:.1f}°<br>dB=%{y:.3f}<extra></extra>"
    ), row=2, col=2)

# Add reference lines
for xval in ref_x:
    fig.add_vline(x=xval, line_dash="dot", line_color="#f59e0b", line_width=1.5, row=1, col=1)  # type: ignore
    fig.add_vline(x=xval, line_dash="dot", line_color="#f59e0b", line_width=1.5, row=1, col=2)  # type: ignore
    fig.add_vline(x=xval, line_dash="dot", line_color="#f59e0b", line_width=1.5, row=2, col=1)  # type: ignore

# Add dB reference lines
db_refs_to_show = []
if show_db_minus1:
    db_refs_to_show.append((-1, "−1 dB", "#94a3b8"))
if show_db_minus3:
    db_refs_to_show.append((-3, "−3 dB (half power)", "#f87171"))
if show_db_minus6:
    db_refs_to_show.append((-6, "−6 dB", "#fbbf24"))
if show_db_minus10:
    db_refs_to_show.append((-10, "−10 dB", "#60a5fa"))
if show_db_minus20:
    db_refs_to_show.append((-20, "−20 dB", "#818cf8"))

for db_val, label, color in db_refs_to_show:
    fig.add_hline(
        y=db_val, line_dash="dash", line_color=color, line_width=1.2,
        row=1, col=2,  # type: ignore
        annotation_text=label, annotation_font_color=color, annotation_font_size=9
    )

fig.add_hline(y=1/sqrt2, line_dash="dash", line_color="#f87171", line_width=1.2, row=1, col=1,  # type: ignore
              annotation_text="−3dB (0.707)", annotation_font_color="#f87171")

fig.add_hline(y=0, line_dash="dash", line_color="#64748b", line_width=0.8, row=2, col=1)  # type: ignore

fig.update_layout(
    height=780, paper_bgcolor="#0a0f1e", plot_bgcolor="#0f172a",
    font=dict(color="#e2e8f0", family="Segoe UI"), showlegend=True,
    legend=dict(bgcolor="#0f172a", bordercolor="#1e3a5f", borderwidth=1, x=1.02, y=1),
    margin=dict(t=60, b=40, r=180)
)
fig.update_xaxes(title_text="ω (rad/s)", type=xtype, gridcolor="#1e293b", zerolinecolor="#1e3a5f", autorange=True, row=1, col=1)
fig.update_xaxes(title_text="ω (rad/s)", type=xtype, gridcolor="#1e293b", zerolinecolor="#1e3a5f", autorange=True, row=1, col=2)
fig.update_xaxes(title_text="ω (rad/s)", type=xtype, gridcolor="#1e293b", zerolinecolor="#1e3a5f", autorange=True, row=2, col=1)
fig.update_xaxes(title_text="Phase (degrees)", gridcolor="#1e293b", zerolinecolor="#1e3a5f", autorange=True, row=2, col=2)
fig.update_yaxes(title_text="|H(jω)|", gridcolor="#1e293b", zerolinecolor="#1e3a5f", autorange=True, row=1, col=1)
fig.update_yaxes(title_text="dB", gridcolor="#1e293b", zerolinecolor="#1e3a5f", autorange=True, row=1, col=2)
fig.update_yaxes(title_text="Phase (°)", gridcolor="#1e293b", zerolinecolor="#1e3a5f", autorange=True, row=2, col=1)
fig.update_yaxes(title_text="dB", gridcolor="#1e293b", zerolinecolor="#1e3a5f", autorange=True, row=2, col=2)

st.markdown('<div class="section-title">Frequency Response Plots — Magnitude & Phase</div>', unsafe_allow_html=True)

# Add tabs for better mobile viewing
tab_mag, tab_phase, tab_both = st.tabs(["📊 Magnitude Response", "🎯 Phase Response", "📈 All Plots"])

with tab_mag:
    st.markdown("**Linear & dB Magnitude Response**")
    
    fig_mag = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            f"{sname} {order_label} — Linear |H(jω)|",
            f"{sname} {order_label} — Bode Plot (dB)"
        ),
        horizontal_spacing=0.12
    )
    
    # Magnitude Linear Plot
    if show_linear:
        fig_mag.add_trace(go.Scatter(
            x=omega_plot, y=mag_plot, name="|H(jω)|",
            line=dict(color=ac, width=2.5),
            hovertemplate="ω=%{x:.2f}<br>|H|=%{y:.5f}<extra></extra>"
        ), row=1, col=1)
    
    # Magnitude dB Plot
    if show_bode:
        fig_mag.add_trace(go.Scatter(
            x=omega_plot, y=db_plot, name="dB",
            line=dict(color=ac, width=2.5),
            hovertemplate="ω=%{x:.2f}<br>dB=%{y:.3f}<extra></extra>"
        ), row=1, col=2)
    
    # Add dB reference lines
    db_refs_to_show = []
    if show_db_minus1:
        db_refs_to_show.append((-1, "−1 dB", "#94a3b8"))
    if show_db_minus3:
        db_refs_to_show.append((-3, "−3 dB (half power)", "#f87171"))
    if show_db_minus6:
        db_refs_to_show.append((-6, "−6 dB", "#fbbf24"))
    if show_db_minus10:
        db_refs_to_show.append((-10, "−10 dB", "#60a5fa"))
    if show_db_minus20:
        db_refs_to_show.append((-20, "−20 dB", "#818cf8"))
    
    for db_val, label, color in db_refs_to_show:
        fig_mag.add_hline(
            y=db_val, line_dash="dash", line_color=color, line_width=1.2,
            row=1, col=2,  # type: ignore
            annotation_text=label, annotation_font_color=color, annotation_font_size=8
        )
    
    # Add cutoff reference lines
    for xval in ref_x:
        fig_mag.add_vline(x=xval, line_dash="dot", line_color="#f59e0b",
                          line_width=1.5, row=1, col=1)  # type: ignore
        fig_mag.add_vline(x=xval, line_dash="dot", line_color="#f59e0b",
                          line_width=1.5, row=1, col=2)  # type: ignore
    
    # -3dB on linear plot
    fig_mag.add_hline(y=1/sqrt2, line_dash="dash", line_color="#f87171", line_width=1.2, row=1, col=1,  # type: ignore
                      annotation_text="−3dB (0.707)", annotation_font_color="#f87171")
    
    fig_mag.update_layout(
        height=450, paper_bgcolor="#0a0f1e", plot_bgcolor="#0f172a",
        font=dict(color="#e2e8f0", family="Segoe UI"), showlegend=True,
        legend=dict(bgcolor="#0f172a", bordercolor="#1e3a5f", borderwidth=1),
        margin=dict(t=60, b=40, l=60, r=60)
    )
    fig_mag.update_xaxes(title_text="ω (rad/s)", type=xtype, gridcolor="#1e293b", 
                        zerolinecolor="#1e3a5f", autorange=True, row=1, col=1)
    fig_mag.update_xaxes(title_text="ω (rad/s)", type=xtype, gridcolor="#1e293b", 
                        zerolinecolor="#1e3a5f", autorange=True, row=1, col=2)
    fig_mag.update_yaxes(title_text="|H(jω)|", gridcolor="#1e293b", zerolinecolor="#1e3a5f", 
                        autorange=True, row=1, col=1)
    fig_mag.update_yaxes(title_text="dB", gridcolor="#1e293b", zerolinecolor="#1e3a5f", 
                        autorange=True, row=1, col=2)
    
    config = {
        "responsive": True, "displayModeBar": True, "displaylogo": False,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        "toImageButtonOptions": {"format": "png", "filename": f"{sname}_{order_label}_magnitude.png",
                                 "height": 800, "width": 1200, "scale": 2}
    }
    st.plotly_chart(fig_mag, use_container_width=True, config=config)

with tab_phase:
    st.markdown("**Phase Response & dB vs Phase**")
    
    fig_phase = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            f"{sname} {order_label} — Phase Response",
            f"{sname} {order_label} — dB vs Phase (Nyquist-style)"
        ),
        horizontal_spacing=0.12
    )
    
    # Phase Plot
    if show_phase:
        fig_phase.add_trace(go.Scatter(
            x=omega_plot, y=phase_plot, name="Phase",
            line=dict(color="#f59e0b", width=2.5),
            hovertemplate="ω=%{x:.2f}<br>Phase=%{y:.1f}°<extra></extra>"
        ), row=1, col=1)
    
    # dB vs Phase
    if show_nyquist:
        fig_phase.add_trace(go.Scatter(
            x=phase_plot, y=db_plot, name="dB vs Phase",
            mode="lines", line=dict(color=ac, width=2.5),
            hovertemplate="Phase=%{x:.1f}°<br>dB=%{y:.3f}<extra></extra>"
        ), row=1, col=2)
    
    # Add reference lines
    fig_phase.add_vline(x=ref_x[0] if len(ref_x) > 0 else 1, line_dash="dot", line_color="#f59e0b",
                       line_width=1.5, row=1, col=1)  # type: ignore
    fig_phase.add_hline(y=0, line_dash="dash", line_color="#64748b", line_width=0.8, row=1, col=1)  # type: ignore
    
    fig_phase.update_layout(
        height=450, paper_bgcolor="#0a0f1e", plot_bgcolor="#0f172a",
        font=dict(color="#e2e8f0", family="Segoe UI"), showlegend=True,
        legend=dict(bgcolor="#0f172a", bordercolor="#1e3a5f", borderwidth=1),
        margin=dict(t=60, b=40, l=60, r=60)
    )
    fig_phase.update_xaxes(title_text="ω (rad/s)", type=xtype, gridcolor="#1e293b",
                          zerolinecolor="#1e3a5f", autorange=True, row=1, col=1)
    fig_phase.update_xaxes(title_text="Phase (degrees)", gridcolor="#1e293b", 
                          zerolinecolor="#1e3a5f", autorange=True, row=1, col=2)
    fig_phase.update_yaxes(title_text="Phase (°)", gridcolor="#1e293b", zerolinecolor="#1e3a5f",
                          autorange=True, row=1, col=1)
    fig_phase.update_yaxes(title_text="dB", gridcolor="#1e293b", zerolinecolor="#1e3a5f", 
                          autorange=True, row=1, col=2)
    
    config = {
        "responsive": True, "displayModeBar": True, "displaylogo": False,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        "toImageButtonOptions": {"format": "png", "filename": f"{sname}_{order_label}_phase.png",
                                 "height": 800, "width": 1200, "scale": 2}
    }
    st.plotly_chart(fig_phase, use_container_width=True, config=config)

with tab_both:
    st.markdown("**All Four Response Plots**")
    st.info("💡 **Tip:** For better viewing on mobile, use the Magnitude Response or Phase Response tabs instead")
    
    config = {
        "responsive": True, "displayModeBar": True, "displaylogo": False,
        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        "toImageButtonOptions": {"format": "png", "filename": f"{sname}_{order_label}_all.png",
                                 "height": 1000, "width": 1400, "scale": 2}
    }
    st.plotly_chart(fig, use_container_width=True, config=config)
st.markdown("---")

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

with st.expander("📖 All Filter Formulas — Quick Reference"):
    st.markdown("""
    **Standard Butterworth Magnitude Formula:**
    ```
    |H(jω)| = 1 / √(1 + (ω/Wc)^(2n))     for LPF
    |H(jω)| = (ω/Wc)^n / √(1 + (ω/Wc)^(2n))     for HPF
    ```
    
    **Key dB Values (Always):**
    - **−1 dB** = 0.891 magnitude (10% drop)
    - **−3 dB** = 0.707 magnitude (50% power drop) ← STANDARD
    - **−6 dB** = 0.501 magnitude (75% drop)
    - **−10 dB** = 0.316 magnitude (90% drop)
    - **−20 dB** = 0.1 magnitude (99% drop)
    
    **Phase behavior:**
    - LPF: Phase shifts from 0° to −90°×n at high freq
    - HPF: Phase shifts from +90°×n at low freq to 0°
    - BPF: Phase ≈ 0° at center frequency, ±90° at edges
    """)

st.markdown("""
<div style='text-align:center;color:#334155;font-size:11px;margin-top:24px;padding:10px;border-top:1px solid #1e3a5f;'>
MEE 316 · Network Analysis & Synthesis ·
LPF · HPF · BPF · BSF · Magnitude · Phase · Multi-dB ·
Python · NumPy · Plotly · Streamlit
</div>
""", unsafe_allow_html=True)
