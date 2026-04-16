import streamlit as st

def apply_nord_theme():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Source+Code+Pro:wght@300;400;600&display=swap');

        :root {
            --nord0: #2e3440; /* Content Background */
            --nord1: #3b4252;
            --nord3: #4c566a;
            --nord4: #d8dee9;
            --nord6: #eceff4;
            --nord8: #88c0d0;
            --nord11: #bf616a;
            --nord14: #a3be8c;
            --margin-bg: #242933; /* Side Margin Background */
        }

        .stApp {
            background: linear-gradient(
                90deg,
                var(--margin-bg) 0%,
                var(--margin-bg) calc(50% - 425px),
                var(--nord0) calc(50% - 425px),
                var(--nord0) calc(50% + 425px),
                var(--margin-bg) calc(50% + 425px),
                var(--margin-bg) 100%
            ) !important;
            font-family: 'Source Code Pro', monospace;
        }

        .block-container {
            background-color: transparent !important;
            max-width: 850px !important;
            padding: 3rem 3.5rem 8rem 3.5rem !important;
            margin: 0 auto !important;
        }

        h1 { font-size: 2.25rem !important; font-weight: 600 !important; margin-bottom: 1rem !important; }
        h2 { font-size: 1.5rem !important; font-weight: 600 !important; }
        p, li, span, label { font-size: 1rem !important; line-height: 1.6 !important; color: var(--nord6) !important; }

        div[data-testid="stMetric"], .stTabs, [data-testid="stExpander"], .stAlert {
            background-color: var(--nord1) !important;
            border: 1px solid var(--nord3) !important;
            border-radius: 0px !important;
        }

        .stTextInput input {
            background-color: var(--nord1) !important;
            color: var(--nord8) !important;
            border: 1px solid var(--nord3) !important;
            border-radius: 0px !important;
            padding: 0.75rem !important;
        }

        .word-node { display: inline-block; margin: 0 4px; padding: 2px 0px; font-size: 0.95rem; }
        .word-toxic { border-bottom: 2px solid var(--nord11); color: var(--nord11); }
        .word-clean { border-bottom: 2px solid var(--nord14); color: var(--nord14); }

        #MainMenu, footer, header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

def render_nord_highlights(contributions):
    html_str = "<div style='margin: 1.5rem 0; line-height: 2.5;'>"
    for word, weight in contributions:
        cls = "word-toxic" if weight > 0.5 else ("word-clean" if weight < -0.5 else "")
        html_str += f'<span class="word-node {cls}">{word}</span>'
    st.markdown(html_str + "</div>", unsafe_allow_html=True)