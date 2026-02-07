# ARCHAI (Autonomous Research for Computer Hardware using AI)
ARCHAI is an autonomous pre-silicon co-design platform that uses Gemini 3 to explore, evaluate, and optimize microarchitectural configurations using gem5 simulations and targeted RTL implementations. It iteratively runs performance experiments, analyzes cache and pipeline tradeoffs (IPC, CPI, miss rates), and proposes new designs using long-horizon reasoning rather than single-prompt generation. ARCHAI bridges high-level architecture exploration and SystemVerilog-level verification, enabling data-driven hardware design decisions before committing to silicon.

# Steps for setup
// 1. Clone the GitHub repository https://github.com/TanoojMadhuvan/ARCHAI--Autonomous-Research-for-Computer-Hardware-using-AI-# into a new folder on your computer

// 2. Open Powershell (on Windows) and cd into the new folder that should have files named "Dockerfile", "main.py", etc

// 3. Pull a docker image from GitHub Container Registry that has gem5 baked-in using the following powershell command
docker pull ghcr.io/tanoojmadhuvan/archai-gem5:latest

// 4. Run a docker container and copy the program files like "main.py", "uarch_specs.py", etc into a new folder inside the container called "archai"
docker run -it --rm `
  -v ${PWD}:/gem5/configs/example/gem5_library/archai `
  ghcr.io/tanoojmadhuvan/archai-gem5:latest

// 5. Go into the archai folder
cd /gem5/configs/example/gem5_library/archai/

// 6. Export Gemini API Key to enable requests to the GenAI models (REPLACE "YOUR API KEY" with your own API key. You can create one for free at: https://aistudio.google.com/api-keys)
export GEMINI_API_KEY="YOUR API KEY"

// 7. Install these necessary Python packages
pip install google-genai
pip install streamlit
pip install matplotlib
pip install streamlit-autorefresh

// 8. Install aarch64 to assemble a C program into ARM assembly
apt update
apt install -y gcc-aarch64-linux-gnu

// 9. Run the following command to actually assemble the C code
aarch64-linux-gnu-gcc uarch_stressor.c -static -o microbench.arm

// 10. Run the main python program
python3 main.py

// 11. Run the streamlit front-end, new terminal
streamlit run presilicon_dashboard.py

//Run a gem5 simulation
build/ARM/gem5.opt configs/example/gem5_library/arm-hello.py