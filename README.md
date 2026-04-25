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

✅ **Interactive Controls**
- Selectable plots (show/hide any subplot)
- Custom cutoff frequencies
- Adjustable frequency sweep range
- Linear or logarithmic x-axis scale

✅ **Data Export**
- Interactive frequency response table (ω = 1 to 100 rad/s)
- CSV download for all data
- PNG download of plots

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

---

## 🚀 Deployment Instructions

### **Option 1: Deploy to Streamlit Cloud (RECOMMENDED — FREE)**

#### Prerequisites
- GitHub account (free at github.com)
- Streamlit account (free at streamlit.io/cloud)

#### Steps

**1. Create GitHub Repository**
```
1. Go to github.com
2. Click "+" → "New repository"
3. Name: MEE316-Filter-Lab
4. Click "Create repository"
```

**2. Upload Files to GitHub**
```
1. Click "Add file" → "Upload files"
2. Upload these three files:
   - app.py (rename from bandpass_streamlit.py)
   - requirements.txt
   - README.md (this file)
3. Click "Commit changes"
```

**3. Deploy on Streamlit Cloud**
```
1. Go to streamlit.io/cloud
2. Click "New app"
3. Select:
   - GitHub repo: MEE316-Filter-Lab
   - Branch: main
   - File: app.py
4. Click "Deploy"
```

**Your app is LIVE!** 🎉
```
https://meee316-filter-lab.streamlit.app
```

Share this link with your lecturer!

---

### **Option 2: Run Locally (For Testing)**

```bash
# Install Python packages
pip install -r requirements.txt

# Run the app
streamlit run app.py

# App opens at: http://localhost:8501
```

---

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

## 📊 Example Use Cases

**1. Design a noise filter**
```
Want to remove frequencies above 10 rad/s?
→ Set LPF with Wc = 10
→ Higher order = sharper cutoff = better filtering
```

**2. Compare filter types**
```
Same cutoff, different filter?
→ Switch between LPF/HPF/BPF/BSF
→ See how each responds
```

**3. Understand phase delay**
```
Why does my signal get delayed?
→ Check Phase Response plot
→ Higher frequencies shift more
```

**4. Homework/Report**
```
Need to show filter analysis?
→ Download CSV table
→ Download PNG plot
→ Include in report
```

---

## 📝 What to Tell Your Lecturer

> *"I built an interactive web app using Python and Streamlit that analyzes all four filter types with multiple orders. The app includes magnitude response in both linear and dB scales, phase response, a multi-dB reference system, and exportable data. Features include step-by-step derivations, cutoff frequency analysis, and the −3dB rule explanation. It's deployed to the cloud so anyone can access it with a link."*

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

## 📞 Support

**Having issues?**
1. Refresh the browser (Ctrl+R)
2. Check that all files are uploaded to GitHub
3. Check `requirements.txt` has all dependencies
4. Verify `app.py` filename (not `bandpass_streamlit.py`)

---

## 📈 Future Enhancements

Potential additions:
- Chebyshev filter type (passband ripple)
- Butterworth filter comparison
- Step response and impulse response
- Group delay visualization
- Pole-zero diagram (s-plane)
- Filter synthesis (design tool)

---

## 📄 License

Educational project for MEE 316 course.

---

**Built with ❤️ for Network Analysis & Synthesis**

*Last updated: April 2026*

---

### Quick Links
- **Streamlit Docs**: https://docs.streamlit.io
- **Plotly Docs**: https://plotly.com/python/
- **NumPy Docs**: https://numpy.org/doc/
- **MEE 316 Course**: Network Analysis & Synthesis
