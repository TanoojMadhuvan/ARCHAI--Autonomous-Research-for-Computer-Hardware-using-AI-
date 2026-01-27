import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
import time

st.title("Design Space Exploration – Live Experiment View")

st.write(
    "Simulating ongoing microarchitecture experiments. "
    "Each point represents a completed configuration."
)

# Placeholder for the plot
plot_placeholder = st.empty()

# Data storage
data = {
    "Experiment ID": [],
    "IPC": []
}

# Sliding window size (how much x-axis we show)
WINDOW_SIZE = 20

# Initialize experiment counter
exp_id = 0

# Run continuously
while True:
    # Simulate new experiment result
    exp_id += 1
    ipc = random.uniform(0.8, 1.4)

    data["Experiment ID"].append(exp_id)
    data["IPC"].append(ipc)

    df = pd.DataFrame(data)

    # Apply sliding window
    if len(df) > WINDOW_SIZE:
        df_visible = df.iloc[-WINDOW_SIZE:]
    else:
        df_visible = df

    # Plot
    fig, ax = plt.subplots()
    ax.plot(
        df_visible["Experiment ID"],
        df_visible["IPC"],
        marker="o"
    )

    ax.set_xlabel("Experiment ID")
    ax.set_ylabel("IPC")
    ax.set_title("Live IPC Results (Sliding Window)")
    ax.set_ylim(0.6, 1.6)
    ax.grid(True)

    # Render plot
    plot_placeholder.pyplot(fig)

    # Slow down updates (simulate runtime)
    time.sleep(1)
