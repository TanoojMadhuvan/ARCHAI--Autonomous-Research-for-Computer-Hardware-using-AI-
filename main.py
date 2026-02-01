import os
import subprocess
from google import genai

def printS(message):
    print(message)

# --- Gemini API part ---
# client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# response = client.models.generate_content(
#     model="gemini-3-flash-preview",
#     contents="Explain how AI works in a few words"
# )
# print("AI Response:", response.text)

# --- Run the gem5 command ---
# Note: split the command into a list: first is executable, rest are arguments

commands = [
    ["aarch64-linux-gnu-gcc", "uarch_stressor.c", "-static", "-o", "microbench.arm"],
    ["build/ARM/gem5.opt", "configs/example/gem5_library/archai/uarch_spec.py"],
]

start_or_load_prompt = "\n\nClick **Start New Experiment** or **Load Existing Experiment**."

def update_start_or_load_prompt(buttonType):
    global start_or_load_prompt
    if(buttonType == 0):
        start_or_load_prompt = "Double Click **Start New Experiment** or **Load Existing Experiment**."
    elif(buttonType == 1):
        start_or_load_prompt = "**Started New Experiment** \nAble to read the C program you are trying to optimize. Continue to choose parameters."
    elif(buttonType == 2):
        start_or_load_prompt = "**Loaded Existing Experiment** \nAble to recover the previous logs. Continue to choose parameters."
    return start_or_load_prompt

def assemblyProgram():
    subprocess.run(commands[0], capture_output=True, text=True)

def runTrial():
    # --- Change directory to /gem5 ---
    os.chdir("/gem5")
    simulation_result = subprocess.run(commands[1], capture_output=True, text=True)

    # --- Print output and errors ---
    print("-" * 100)
    print("Output of the gem5 simulation:")
    print("-" * 30 + "\n")
    print(simulation_result.stdout)
    print("Errors 2 (if any):")
    print(simulation_result.stderr)
    print("-" * 100)
    print("Return 2 code:", simulation_result.returncode)
    print("-" * 100)

def viewTrialStats():
    os.chdir("/gem5/m5out")
    with open("stats.txt", "r") as f:
        content = f.read(3000)
    print(content)