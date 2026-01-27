import os
import subprocess
from google import genai

# --- Gemini API part ---
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents="Explain how AI works in a few words"
)
print("AI Response:", response.text)



# --- Run the gem5 command ---
# Note: split the command into a list: first is executable, rest are arguments
command1 = ["aarch64-linux-gnu-gcc", "uarch_stressor.c", "-static", "-o", "microbench.arm"]
command2 = ["build/ARM/gem5.opt", "configs/example/gem5_library/archai/uarch_spec.py"]

result1 = subprocess.run(command1, capture_output=True, text=True)

# --- Change directory to /gem5 ---
os.chdir("/gem5")
print("Current directory:", os.getcwd())

result2 = subprocess.run(command2, capture_output=True, text=True)

# --- Print output and errors ---
print("Output 2:")
print(result2.stdout)
print("Errors 2 (if any):")
print(result2.stderr)
print("Return 2 code:", result2.returncode)
