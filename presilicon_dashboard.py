import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import html
import json
from main import *
from pathlib import Path

st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    /* ===== Global Background ===== */
    .stApp {
        background: radial-gradient(circle at 20% 20%, #111827, #020617);
        color: #e5e7eb;
    }

    /* ===== Subtle Chip-Grid Texture ===== */
    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        background-image:
            linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
        background-size: 40px 40px;
        pointer-events: none;
        z-index: 0;
    }

    /* ===== Sidebar ===== */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #020617, #020617);
        border-right: 1px solid #334155;
    }

    /* ===== Buttons ===== */
    button {
        background: linear-gradient(135deg, #1e293b, #020617);
        border: 1px solid #334155;
        border-radius: 10px;
        color: #e5e7eb;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    button:hover {
        border-color: #38bdf8;
        box-shadow: 0 0 12px rgba(56,189,248,0.45);
        transform: translateY(-1px);
    }

    /* ===== Inputs ===== */
    textarea, input {
        background-color: #020617 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: #e5e7eb !important;
        font-family: monospace;
    }

    /* ===== Headers ===== */
    h1, h2, h3 {
        letter-spacing: 0.04em;
    }

    /* ===== Panels ===== */
    .archai-panel {
        background: rgba(2,6,23,0.85);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: inset 0 0 30px rgba(0,0,0,0.4);
    }

    .archai-panel-title {
        color: #38bdf8;
        font-weight: 700;
        margin-bottom: 10px;
        font-size: 1.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# Global setup
# --------------------------------------------------
st.set_page_config(layout="wide")

PARAM_FILE = Path(__file__).parent / "params.json"

with open(PARAM_FILE) as f:
    params = json.load(f)
PARAMS = [
    k for k, v in params["vars"].items()
    if isinstance(v, (str, int))
]

# --------------------------------------------------
# Session state initialization
# --------------------------------------------------
if "current_phase" not in st.session_state:
    st.session_state.current_phase = "Pre-Experiment"

if "experiment_started" not in st.session_state:
    st.session_state.experiment_started = False

if "selected_params" not in st.session_state:
    st.session_state.selected_params = {p: False for p in PARAMS}

if "param_ranges" not in st.session_state:
    st.session_state.param_ranges = {}

if "start_or_load_prompt" not in st.session_state:
    st.session_state.start_or_load_prompt = update_start_or_load_prompt(0)

# --- Testing data ---
if "exp_id" not in st.session_state:
    st.session_state.exp_id = 0

if "ipc_data" not in st.session_state:
    st.session_state.ipc_data = {
        "Experiment ID": [],
        "IPC": []
    }

if "echo_messages" not in st.session_state:
    st.session_state.echo_messages = []

if "outline_messages" not in st.session_state:
    st.session_state.outline_messages = []

if "user_outline_input" not in st.session_state:
    st.session_state.user_outline_input = ""

# --------------------------------------------------
# Sidebar (Tab Selector)
# --------------------------------------------------
st.sidebar.title("ARCHAI Live Dashboard")

selected_tab = st.sidebar.radio(
    "Navigate",
    ["Pre-Experiment", "Testing", "Results and Analysis"],
    index=["Pre-Experiment", "Testing", "Results and Analysis"].index(
        st.session_state.current_phase
    )
)

st.session_state.current_phase = selected_tab

# ==================================================
# PRE-EXPERIMENT
# ==================================================
if st.session_state.current_phase == "Pre-Experiment":

    st.title("Pre-Experiment Setup")

    st.info(
        st.session_state.start_or_load_prompt
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Start New Experiment"):
            st.session_state.experiment_started = False
            st.session_state.start_or_load_prompt = update_start_or_load_prompt(1)

    with col2:
        if st.button("Load Existing Experiment"):
            st.session_state.experiment_started = False
            st.session_state.start_or_load_prompt = update_start_or_load_prompt(2)

    st.divider()

    st.write(
        "### Select the parameters to change during the experiment"
    )

    # Parameter checklist with min/max
    for param in PARAMS:
        cols = st.columns([1, 2, 2, 1])

        with cols[0]:
            checked = st.checkbox(
                param,
                value=st.session_state.selected_params[param],
                key=f"check_{param}"
            )
            st.session_state.selected_params[param] = checked

        if checked:
            with cols[1]:
                min_val = st.text_input(
                    "Min",
                    key=f"{param}_min"
                )

            with cols[2]:
                max_val = st.text_input(
                    "Max",
                    key=f"{param}_max"
                )

            with cols[3]:
                if st.button("Change", key=f"change_{param}"):
                    st.session_state.param_ranges[param] = {
                        "min": min_val,
                        "max": max_val
                    }
                    printS(st.session_state.param_ranges[param])
                    
                    intParams = ["l1i_assoc", "l1d_assoc", "l2_assoc", "num_cores"]
                    if(param in intParams):
                        if(min_val != ""):
                            min_val = int(min_val)
                        if(max_val != ""):
                            max_val = int(max_val)

                    if(min_val != ""):
                        params["min"][param] = min_val
                    if(max_val != ""):
                        params["max"][param] = max_val
                    with open(PARAM_FILE, "w") as f:
                        json.dump(params, f, indent=2)

    st.divider()

    st.write(
        "### Phase Outline"
    )

    st.info(
        "ARCHAI will use Gemini 3 to conduct the experiment on the parameters in 'phases', which are **dynamic, sequential steps** independently executed and interpreted before further execution. Click to generate an initial **Phase Outline**. You can modify the outline (feature engineering) with prompts.\n\nNote: This is only an initial outline to give an overview of the 'general flow' of the experiment. Gemini 3 will usually modify this outline during runtime for optimization."
    )

    #Outline
    for msg in st.session_state.outline_messages:
        safe_msg = html.escape(msg)
        st.markdown(
            f"""<div style="
                background-color: #1f2937;
                color: #f9fafb;
                padding: 12px;
                border-radius: 10px;
                margin-bottom: 10px;
                white-space: pre-wrap;
                border-left: 4px solid #3b82f6;
                font-family: monospace;
            ">{safe_msg}</div>""",
            unsafe_allow_html=True
        )


   # ---- Clear input if requested (must happen BEFORE widget) ----
    if st.session_state.pop("__clear_outline_input__", False):
        st.session_state.user_outline_input = ""

    user_message = st.text_area(
        "Enter modifications",
        height=120,
        placeholder="Examples:\nSplit phase 1 into two parts...\nParameter X is costly...",
        key="user_outline_input"
    )

    if st.button("Generate / Modify"):
        msg = st.session_state.user_outline_input.strip() or "Generate"
        outline = generateOutline(msg)
        st.session_state.outline_messages = outline
        st.session_state["__clear_outline_input__"] = True
        st.rerun()

       

    st.divider()

    if st.button("Submit Experiment Configuration"):
        st.success("Experiment started")
        st.session_state.experiment_started = True
        st.session_state.current_phase = "Testing"
        st.rerun()

# ==================================================
# TESTING
# ==================================================
if st.session_state.current_phase == "Testing":

    st.title("Testing Phase")

    # ---------------- Graph Input ----------------
    st.subheader("Manual IPC Input")

    ipc_input = st.text_input("Enter IPC value (e.g. 1.12)")

    if st.button("Add Experiment"):
        try:
            ipc_value = float(ipc_input)
            st.session_state.exp_id += 1

            st.session_state.ipc_data["Experiment ID"].append(
                st.session_state.exp_id
            )
            st.session_state.ipc_data["IPC"].append(ipc_value)

        except ValueError:
            st.error("Invalid IPC value")

    # ---------------- Plot ----------------
    df = pd.DataFrame(st.session_state.ipc_data)

    fig, ax = plt.subplots()
    ax.plot(df["Experiment ID"], df["IPC"], marker="o")
    ax.set_xlabel("Experiment ID")
    ax.set_ylabel("IPC")
    ax.set_title("IPC Results")
    ax.set_ylim(0.6, 1.6)
    ax.grid(True)

    st.pyplot(fig)

    st.divider()

    # ---------------- Param checklist (graph selection) ----------------
    st.subheader("Parameters to Display")

    for param in PARAMS:
        st.checkbox(
            param,
            value=st.session_state.selected_params[param],
            key=f"testing_{param}"
        )

    st.divider()

    # ---------------- Echo Console ----------------
    st.subheader("Echo Console")

    user_message = st.text_area(
        "Type message",
        height=120,
        placeholder="Type multiple lines here..."
    )

    if st.button("Echo"):
        if user_message.strip():
            st.session_state.echo_messages.insert(0, user_message)
            st.session_state.echo_messages = st.session_state.echo_messages[:3]

    st.markdown("### Echo Output")

    for msg in st.session_state.echo_messages:
        safe_msg = html.escape(msg)
        st.markdown(
            f"""
            <div style="
                background-color: #1f2937;
                color: #f9fafb;
                padding: 12px;
                border-radius: 10px;
                margin-bottom: 10px;
                white-space: pre-wrap;
                border-left: 4px solid #3b82f6;
                font-family: monospace;
            ">
            {safe_msg}
            </div>
            """,
            unsafe_allow_html=True
        )

# ==================================================
# RESULTS & ANALYSIS
# ==================================================
if st.session_state.current_phase == "Results and Analysis":

    st.title("Results and Analysis")

    st.subheader("Experiment Visualization")
    st.image(
        "https://via.placeholder.com/900x400?text=Experiment+Results",
        use_column_width=True
    )

    st.divider()

    st.subheader("Analysis Console")

    analysis_message = st.text_area(
        "Ask about results or bottlenecks",
        height=120
    )

    if st.button("Submit Analysis Query"):
        st.info("Query submitted")

    st.text_area(
        "Extend Existing Experiment",
        height=100,
        placeholder="Describe how you want to extend the experiment..."
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Extend Experiment"):
            st.success("Experiment extended")

    with col2:
        if st.button("Save Results"):
            st.success("Results saved")
