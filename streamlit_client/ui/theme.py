"""
UI theming utilities to match the dark/teal palette from the PRD.
"""

import streamlit as st


GLOBAL_CSS = """
<style>
:root {
  --bg: #0e141b;
  --card: #131c24;
  --card-strong: #16222c;
  --border: #1f2c36;
  --text: #d7e0e7;
  --muted: #7b8a92;
  --accent-start: #0ad7b3;
  --accent-end: #05b883;
  --danger: #e05c57;
  --warn: #f7a736;
}
body, .block-container {
  background: radial-gradient(circle at 20% 20%, rgba(10,215,179,0.05), transparent 25%), var(--bg) !important;
  color: var(--text);
}
.block-container {padding: 2rem 2.5rem;}
.stButton>button, .stDownloadButton>button {
  background: linear-gradient(90deg, var(--accent-start), var(--accent-end));
  color: #0b1219;
  border: none;
  font-weight: 700;
  letter-spacing: .6px;
  text-transform: uppercase;
  padding: 0.65rem 1rem;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0,0,0,0.35);
}
.stButton>button:hover {filter: brightness(1.05);}
.ghost-btn>button {
  background: transparent;
  color: var(--text);
  border: 1px solid var(--accent-start);
}
.metric-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1rem 1.25rem;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
}
.pill {
  display: inline-block;
  padding: 0.35rem 0.65rem;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: #0f181f;
  color: var(--text);
  font-size: 0.8rem;
  letter-spacing: .4px;
}
.status-pr {color: #0ad7b3;}
.status-outlier {color: var(--warn);}
.status-suspicious_low {color: #e0b65c;}
.status-normal {color: var(--muted);}
.card-surface {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1rem;
}
.stDataFrame, .stTable, .stDataFrame>div {
  color: var(--text) !important;
}
input, textarea, select {
  color: var(--text) !important;
}
</style>
"""


def apply_theme() -> None:
    """Inject global CSS into the Streamlit page."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

