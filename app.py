import streamlit as st
import pandas as pd
import os
from model_engine import ToxicChatClassifier
from styles import apply_nord_theme, render_nord_highlights

st.set_page_config(page_title="Toxic Chat Classifier", layout="centered")
apply_nord_theme()

@st.cache_resource
def init_engine():
    model = ToxicChatClassifier()
    if os.path.exists('train.csv'):
        df = pd.read_csv('train.csv').head(20000)
        model.train(df)
    else:
        st.error("Training data (train.csv) not found in root directory.")
    return model

model = init_engine()

st.title("Toxic Chat Classifier")
st.markdown("<p style='opacity: 0.7; margin-bottom: 2rem;'>Automated classification system for detecting and flagging harmful language.</p>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Analyze", "Audit", "Dashboard"])

with tab1:
    st.write("")
    st.markdown("#### Real-time Analysis")
    st.caption("Verify specific strings to see how the system weights individual terms.")
    user_input = st.text_input("Input", placeholder="Paste text here...", label_visibility="collapsed")

    if user_input:
        result, scores = model.predict(user_input)
        render_nord_highlights(model.get_word_contributions(user_input))

        status_color = "#bf616a" if result == "TOXIC" else "#a3be8c"
        st.markdown(f"<h3 style='color: {status_color} !important; margin-top: 0;'>{result}</h3>", unsafe_allow_html=True)

        with st.expander("Confidence Metrics"):
            st.json(scores)

with tab2:
    st.write("")
    st.markdown("#### Batch Processing")
    st.markdown("<div class='stCaption'>Upload any CSV log. The system will attempt to auto-detect the message column.</div>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload CSV", type=['csv'], label_visibility="collapsed")

    if uploaded_file:
        try:
            # Load the data
            data = pd.read_csv(uploaded_file)

            # 1. Smart Column Detection
            all_columns = data.columns.tolist()
            potential_cols = [c for c in all_columns if any(k in str(c).lower() for k in ['text', 'msg', 'comment', 'content', 'chat', 'body'])]

            # 2. UI for Column Selection
            st.write("---")
            if potential_cols:
                # Default to the first "smart" guess
                selected_col = st.selectbox("Confirm the column containing messages:", all_columns, index=all_columns.index(potential_cols[0]))
            else:
                st.warning("Could not auto-detect the message column. Please select it manually below:")
                selected_col = st.selectbox("Select message column:", all_columns)

            if st.button("Run Batch Analysis"):
                with st.spinner('Analyzing sequences...'):
                    # Perform the analysis on the chosen column
                    data['Analysis'] = data[selected_col].astype(str).apply(lambda x: model.predict(x)[0])
                    st.session_state['audit_data'] = data
                    st.session_state['active_col'] = selected_col

                st.success(f"Analysis complete on column: **{selected_col}**")

                # Show a preview of flags
                toxic_only = data[data['Analysis'] == 'TOXIC']
                if not toxic_only.empty:
                    st.markdown("##### Detected Toxicity Preview")
                    st.dataframe(toxic_only[[selected_col]].head(10), use_container_width=True)
                else:
                    st.info("No toxicity detected in this file.")

        except Exception as e:
            st.error(f"Error: The uploaded file could not be processed. Details: {e}")

with tab3:
    st.write("")
    st.markdown("#### Community Health")
    st.caption("Data visualization showing the safety ratio of your audited community.")
    if 'audit_data' in st.session_state:
        df = st.session_state['audit_data']
        toxic_count = (df['Analysis'] == 'TOXIC').sum()
        total = len(df)

        col1, col2 = st.columns(2)
        col1.metric("Messages Scanned", total)
        col2.metric("Toxicity Rate", f"{(toxic_count/total)*100:.2f}%")

        chart_df = pd.DataFrame({'Status': ['TOXIC', 'CLEAN'], 'Count': [toxic_count, total - toxic_count]})
        st.bar_chart(chart_df, x='Status', y='Count', color="#81a1c1")
    else:
        st.info("Process a file in the Audit tab to view metrics.")

st.write("")
st.write("---")
st.markdown("""
### System Overview
This tool evaluates text using a probabilistic frequency engine.

#### Operational Logic
* **Probability Engine:** The system calculates the likelihood of a message being toxic based on word patterns found in verified datasets.
* **Underlining Visuals:** Terms underlined in **Red** indicate a high toxic weight; **Green** indicates a clean weight.
* **Metric Interpretation:** Under 'Confidence Metrics', a more negative value represents a higher probability for that specific class.

#### Key Considerations
* **Context Blindness:** The model treats words as independent units. It does not natively detect sarcasm or complex cultural slang.
* **Data Dependency:** Accuracy is limited by the diversity and volume of the training data provided in the root directory.
""", unsafe_allow_html=True)