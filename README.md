# 🎛️ MEE 316 — Filter Frequency Response Lab

**Complete Interactive Filter Analyzer** for Network Analysis & Synthesis

## 📋 Project Overview

A professional interactive web application for analyzing and visualizing the frequency response of electrical filters. Built for **MEE 316 Network Analysis & Synthesis** course.

### Features

✅ **Four Filter Types**
- Low-Pass Filter (LPF)
- High-Pass Filter (HPF)
- Band-Pass Filter (BPF)
- Band-Stop Filter (BSF)

✅ **Flexible Filter Orders**
- 1st, 2nd, 4th, 6th, 8th order Butterworth filters
- Compare how order affects cutoff sharpness

✅ **Complete Analysis Plots**
- Linear magnitude response
- Bode plot (dB) with **multi-dB reference lines**
  - −1 dB, −3 dB (half power), −6 dB, −10 dB, −20 dB
- Phase response (degrees)
- dB vs Phase (Nyquist-style)

 

✅ **Educational Content**
- Step-by-step filter derivation
- Transfer function formulas
- Cutoff frequency explanation
- −3dB rule (half-power point)

---

## 🧮 Mathematical Foundation

All filters derived from **Normalized Low-Pass Filter (NLPF):**
```
H(s) = 1 / (s + 1)
```

Filter types created using frequency substitutions:
- **LPF**: s → s/Wc
- **HPF**: s → Wc/s
- **BPF**: s → (s²+W₁W₂)/(BW·s)
- **BSF**: s → BW·s/(s²+W₁W₂)

**Key Formula:**
```
Magnitude: |H(jω)| = 1 / √(1 + (ω/Wc)^(2n))   [for LPF, nth order]
dB:        |H(jω)|_dB = 20 × log₁₀(|H(jω)|)
Phase:     ∠H(jω) = phase shift in degrees
```

**−3dB Rule (Standard):**
```
At cutoff frequency: |H(jω)| = 1/√2 = 0.70711
This equals −3.01 dB = half power point
```
 

## 📁 File Structure

```
MEE316-Filter-Lab/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

---

## 🎓 How to Use (Quick Guide)

1. **Select Filter Type** — LPF, HPF, BPF, or BSF
2. **Choose Order** — 1st through 8th order
3. **Set Cutoff** — Wc or Wc1/Wc2 (in rad/s)
4. **Adjust View** — Frequency sweep range (ω min/max)
5. **Select Plots** — Show/hide any of 4 response plots
6. **Enable dB Lines** — Toggle −1, −3, −6, −10, −20 dB references
7. **Explore** — Use Plotly tools to zoom, pan, reset
8. **Export** — Download table as CSV or graph as PNG

---

## 🔍 Key Concepts Explained

### **Cutoff Frequency (Wc)**
The frequency where filter transitions from pass to stop, marked by:
- |H(jω)| = 0.70711 (1/√2)
- dB = −3.01 dB
- **Half power point**

### **Filter Order**
- **1st order**: Gentle roll-off (−20 dB/decade)
- **2nd order**: Sharper (−40 dB/decade)
- **4th order**: Very sharp (−80 dB/decade)
- **Higher order**: Even sharper cutoff

### **−3dB Rule**
Standard definition in ALL engineering:
- At cutoff, power drops to 50%
- Magnitude drops to 0.70711
- Always equals −3.01 dB (not −3.00)

### **Phase Response**
Shows how much each frequency gets delayed:
- LPF: Phase shifts 0° to −90°×n
- HPF: Phase shifts +90°×n to 0°
- BPF: Maximum shift at center frequency

---

## 🛠️ Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **Math**: NumPy (numerical computing)
- **Data**: Pandas (tables and CSV export)
- **Plotting**: Plotly (interactive graphs)
- **Deployment**: Streamlit Cloud (free hosting)

---
 
 
## 🎯 Learning Outcomes

After using this lab, you should understand:

✅ How to transform filters using frequency substitution
✅ Why cutoff frequency = −3dB = 0.70711 (always)
✅ How filter order affects roll-off sharpness
✅ Phase shift behavior across frequency range
✅ How to read Bode plots (magnitude + phase)
✅ Real-world filter design tradeoffs

---
 
