# ARCHAI (Autonomous Research for Computer Hardware using AI)
ARCHAI is an autonomous pre-silicon co-design platform that uses Gemini 3 to explore, evaluate, and optimize microarchitectural configurations using gem5 simulations and targeted RTL implementations. It iteratively runs performance experiments, analyzes cache and pipeline tradeoffs (IPC, CPI, miss rates), and proposes new designs using long-horizon reasoning rather than single-prompt generation. ARCHAI bridges high-level architecture exploration and SystemVerilog-level verification, enabling data-driven hardware design decisions before committing to silicon.

# Pre-Requisites
1. Operating System

Windows 10/11, macOS, or Linux

Windows users must have WSL2 enabled (recommended for best Docker compatibility)

2. Docker (Required)

ARCHAI runs gem5 inside a Docker container.

Install Docker Desktop
https://www.docker.com/products/docker-desktop/

Create a free Docker account

Ensure Docker Engine is running before proceeding

Verify installation:

docker --version

3. Python

Used for orchestration logic, Gemini integration, and the Streamlit UI.

Python 3.9+ recommended

Verify installation:

python --version


or

python3 --version

4. Git

Used to clone the ARCHAI repository.

Install Git
https://git-scm.com/downloads

Verify installation:

git --version

5. Google Gemini API Access

ARCHAI uses Gemini 3 for autonomous reasoning and experiment orchestration.

Create a free Gemini API key
https://aistudio.google.com/api-keys

The key will be exported as an environment variable during setup

6. Visual Studio Code (Strongly Recommended)

Used for container interaction, debugging, and Streamlit execution.

Install Visual Studio Code
https://code.visualstudio.com/

Install the Dev Containers extension:

ms-vscode-remote.remote-containers

This enables seamless interaction with the running Docker container.

7. (Optional but Recommended) System Resources

gem5 simulations are compute-intensive.

8+ GB RAM recommended

Multi-core CPU preferred for parallel simulations

Sufficient disk space (several GB) for simulation outputs

8. Internet Connection

Required for:

Pulling Docker images

Accessing Gemini models

(Optional) Deep Research comparisons with online literature

# Steps for Setup and Running the Application
1. Clone the GitHub repository https://github.com/TanoojMadhuvan/ARCHAI--Autonomous-Research-for-Computer-Hardware-using-AI-# into a new folder on your computer

2. Open Powershell (on Windows) and cd into the new GitHub folder that should have files named "Dockerfile", "main.py", etc

3. Pull a docker image from GitHub Container Registry that has gem5 baked-in using the following powershell command

docker pull ghcr.io/tanoojmadhuvan/archai-gem5:latest

4. Run a docker container and copy the program files like "main.py", "uarch_specs.py", etc into a new folder inside the container called "archai"


docker run -it --rm `
  -v ${PWD}:/gem5/configs/example/gem5_library/archai `
  ghcr.io/tanoojmadhuvan/archai-gem5:latest

5. Go into the archai folder

cd /gem5/configs/example/gem5_library/archai/

6. Export Gemini API Key to enable requests to the GenAI models (REPLACE "YOUR API KEY" with your own API key, and enter the commmand in Powershell. You can create one for free at: https://aistudio.google.com/api-keys)

export GEMINI_API_KEY="YOUR API KEY"

7. Install these necessary Python packages
pip install google-genai
pip install streamlit
pip install matplotlib
pip install streamlit-autorefresh
pip install pandas

8. Install aarch64 to assemble a C program into ARM assembly
apt update
apt install -y gcc-aarch64-linux-gnu

9. Open Visual Studio Code and install the Dev Containers extension.

10. Press F1 to search for actively running containers. Connect to the right container (there should only be one). This step enables running streamlit through docker.

11. Run the streamlit front-end by entering this command in Powershell

streamlit run presilicon_dashboard.py


# Optional Additional Commands for Manual Experimentation 

A. Run a gem5 simulation

build/ARM/gem5.opt configs/example/gem5_library/arm-hello.py

B. Run the following command to actually assemble the C code

aarch64-linux-gnu-gcc uarch_stressor.c -static -o microbench.arm

# Programs / File Structure

### main.py
- Core orchestration logic for *ARCHAI*
- Handles all **Gemini 3 interactions**, including:
  - Assembling microarchitectural stressor code
  - Generating experimental phase outlines
  - Running gem5 simulation trials
  - Initiating Deep Research tasks
  - Generating Markdown reports from simulation results

---

### presilicon_dashboard.py
- Streamlit-based front-end for interacting with *ARCHAI*
- Allows users to:
  - Configure microarchitecture parameters
  - Edit experiment outlines using natural language
  - Monitor running trials
  - Visualize results locally via `localhost`

---

### uarch_spec.py
- Defines the **gem5 microarchitecture configuration**
- Specifies:
  - CPU configuration
  - Cache hierarchy
  - Memory system parameters
  - Other architectural components used during simulation

---

### uarch_stressor.c
- Microarchitectural stressor program compiled and executed within **gem5**
- Currently implements workloads such as:
  - Merge sort
  - Bubble sort
- Uses configurable input sizes to generate controlled:
  - Memory pressure
  - Compute pressure

---

### params.json
- Runtime experiment state file
- Stores:
  - Active configuration parameters
  - Experimental phase definitions
  - Trial metadata
  - Extracted simulation results during execution

---

### loadparams.json
- Serialized project snapshot
- Used to:
  - Reload a previously saved experiment into `params.json`
  - Continue or extend long-running research workflows

---

### defaultparams.json
- Baseline configuration template
- Used when:
  - Starting a new project
  - Overwriting `params.json` with default experiment settings
