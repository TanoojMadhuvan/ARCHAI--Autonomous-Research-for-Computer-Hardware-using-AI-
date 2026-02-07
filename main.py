import os
import subprocess
from google import genai
import re
import ctypes
import json
from pathlib import Path


SYSTEM_INSTRUCTION = """You are ARCHAI, an autonomous pre-silicon microarchitecture research assistant.
Your role is to:
- Analyze gem5 simulation results
- Reason about cache, pipeline, and memory tradeoffs
- Optimize IPC, CPI, cache miss rates, and memory latency
- Ultimately maximize the execution speed of a particular C program by modifying microarchitecture paramters
- Propose structured experiment phases, with specific subgoals and hypotheses
- Avoid brute-force sweeps across entire parameter space (all combinations of parameters)
- Justify decisions using evidence from prior results (dynammically generating phases)

Think step-by-step like a hardware architect.
You must reason step-by-step and justify each decision using evidence from prior experiments."""

def printS(message):
    print(message)

# --- Gemini API part ---
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

# --- Run the gem5 command ---
# Note: split the command into a list: first is executable, rest are arguments

commands = [
    ["aarch64-linux-gnu-gcc", "uarch_stressor.c", "-static", "-o", "microbench.arm"],
    ["build/ARM/gem5.opt", "configs/example/gem5_library/archai/uarch_spec.py"],
    ["gcc", "-shared", "-fPIC", "uarch_stressor.c", "-o", "libstressor.so"]
]

PARAM_FILE = Path(__file__).parent / "params.json"
with open(PARAM_FILE) as f:
    params = json.load(f)
PARAMS = [
    k for k, v in params["vars"].items()
    if isinstance(v, (str, int))
]

with open("/gem5/configs/example/gem5_library/archai/uarch_stressor.c", "r", encoding="utf-8") as f:
    c_program_contents = f.read()

def storeParams():
    with open(PARAM_FILE, "w") as f:
        json.dump(params, f, indent=2)

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

def resetAll():
    with open(Path(__file__).parent / "defaultparams.json") as f:
        params2 = json.load(f)
    for key in params2:
        params[key] = params2[key]
    storeParams()

def printTrialStats():
    os.chdir("/gem5/m5out")
    with open("stats.txt", "r") as f:
        content = f.read(3000)
    print(content)

def extractTrialStats():
    os.chdir("/gem5/m5out")
    with open("stats.txt", "r") as f:
        text = f.read()
    numbers = re.findall(r'-?\d+(?:\.\d+)?', text)
    return [float(n) if '.' in n else int(n) for n in numbers]

# def setStressorWorkloadSize():
#     subprocess.run(commands[2], capture_output=True, text=True)
#     lib = ctypes.CDLL("./libstressor.so")
#     lib.set_N.argtypes = [ctypes.c_int]
#     with open(PARAM_FILE) as f:
#         params = json.load(f)
#         N = params["stressor_c"]["N"]
#         lib.set_N(N)


currentOutline = ["1. Do this", "2. Do that"]

def maybeInt(val):
    return int(val) if val.isdigit() else val

def parseOutlineResponse(outline_str):
    """
    Parses Gemini-generated phase outline text into a 2D array.

    Returns:
    [
      [
        phase_goal (str),
        phase_hypothesis (str),
        [param1, param2, ...],
        [[min1, max1], [min2, max2], ...],
        num_trials (int)
      ],
      ...
    ]
    """

    rows = []

    # Split by lines, ignore empty ones
    lines = [l.strip() for l in outline_str.strip().splitlines() if l.strip()]

    for line in lines:
        # Extract quoted strings
        quoted = re.findall(r'"([^"]*)"', line)

        # Extract all numbers (outside quotes)
        numbers = re.findall(r'\b\d+\b', re.sub(r'"[^"]*"', '', line))
        numbers = list(map(int, numbers))

        phase_goal = quoted[0]
        phase_hypothesis = quoted[1]

        num_params = numbers[1]  # second number = NumParamsChanging

        # Parameter names
        params = quoted[2 : 2 + num_params]

        # Min values
        mins = quoted[2 + num_params : 2 + 2 * num_params]

        # Max values
        maxs = quoted[2 + 2 * num_params : 2 + 3 * num_params]

        param_ranges = [
            [maybeInt(mins[i]), maybeInt(maxs[i])]
            for i in range(num_params)
        ]


        num_trials = numbers[-1]

        rows.append([
            phase_goal,
            phase_hypothesis,
            params,
            param_ranges,
            num_trials
        ])

    return rows

def generateOutline(modification):
    
    # response = client.models.generate_content(
    #     model="gemini-3-flash-preview",
    #     contents="Explain how AI works in a few words"
    # )
    # print("AI Response:", response.text)

    if(modification != "Generate" and params["outline"]["phases"] != ""):
        currentOutline.append(modification)  
        if(modification not in params["outline"]["user_modifications"]):
            params["outline"]["user_modifications"].append(modification)

        modify_prompt = "The C stressor program you are trying to optimize is: \n" + c_program_contents + "\n\nThink about the nature of the taskload, like how the stressor algorithm's use of memory might affect cache hit-rate/execution speed"
        modify_prompt += "\n\nFor each phase, specify a small goal, a hypothesis, the 1 to 3 parameters you want to change in that phase, the start and endpoint for each parameter you are changing, the number of steps (trials) you are going to take to reach from start to end" 
        modify_prompt += "\n\nRemember, you are not simply maximizing the cache size or number of cores as that would obviously result in maximum speed. Instead, you can slowly linearly interpolate a parameter over 10-20 trials, and identify exactly when a bottleneck is reached, when no further progress is made even though cache size is increasing and making microarchitecture more costly."
        modify_prompt += "You can modify the following params: "
        for i in PARAMS:
            if(params["min"][i] != params["max"][i]):
                modify_prompt += ("\n" + str(i) + " in range " + str(params["min"][i]) + " to " + str(params["max"][i]))
        
        modify_prompt += "\nYou already generated an initial outline of 4-6 phases, tailored to the context of optimizing microarchitecture params for the C program's execution\nWhen changing from one memory size to another, you can only go in powers of 2. So 16MB to 128MB should have: 16MB, 32MB, 64MB, 128MB, with the number of steps being 4"
        modify_prompt += "\n\n The Formatting is as follows:\n"
        modify_prompt += """PhaseNumber "PhaseGoal" "PhaseHypothesis" NumParamsChanging "PhaseParam1" ... "PhaseParamN" "PhaseParam1Min" ... "PhaseParamNMin" "PhaseParam1Max" ... "PhaseParamNMax" PhaseNumTrials
            e.g.
            0 "Determine IPC sensitivity to L1D capacity, since the C program has 40000+ sequential array elements for data that can be cached efficiently spacially" "Cache hitrate will improve >10% proving L1D capacity is a bottleneck, now fixed and move to phase 1" 1 "l1d_size" "16kB" "64kB" 10
            1 "Find minimum L1 associativity required to minimize hardware costs, because L1D capacity was increased in phase 0" "IPC will flatline at one of the trials, and the inflection point associativity value can be found" 1 "l1d_assoc" "1" "5" 5
            etc
            """
        modify_prompt += "\n\nHere was your proposed outline response: " + params["outline"]["phases"]
        modify_prompt += "\n\nIMPORTANT, you need to modify parts of the outline based on this feedback request: " + modification
        modify_prompt += "\nReturn the output in the same format. Always start your answer from phase 0"
       
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[
                {
                    "role": "system",
                    "parts": [{"text": SYSTEM_INSTRUCTION}]
                },
                {
                    "role": "user",
                    "parts": [{"text": modify_prompt}]
                }
            ]
        )
        print("Modify Prompt:", modify_prompt)
        print("\n\nAI Modify Response:", response.text)

        summary_modified = ""
        if(modification[0] == '*' or modification[0] == '&'):
            summary_prompt = "This was your original outline: " + params["outline"]["phases"]
            summary_prompt = "This was the modification I asked you to make: " + modification
            summary_prompt += "\n\nThis is the new outline you generated: " + response.text
            summary_prompt += "\n\nGive a 2 sentence response detailing how you incorporated my advice exactly in the modified outline, exactly what you modified. 1 sentence on how it can change performance of computer architecture."
            response2 = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=[
                    {
                        "role": "system",
                        "parts": [{"text": SYSTEM_INSTRUCTION}]
                    },
                    {
                        "role": "user",
                        "parts": [{"text": summary_prompt}]
                    }
                ]
            )
            summary_modified = response2.text
            if(modification[0] == '*' and (summary_modified not in params["outline"]["modif_summary"])):
                params["outline"]["modif_summary"].append(summary_modified)
            elif(modification[0] == '&' and (summary_modified not in params["outline"]["runtime_modifications"])):
                params["outline"]["runtime_modifications"].append(summary_modified)

        params["outline"]["phases"] = response.text

    elif params["outline"]["phases"] == "":
        initial_prompt = "The C stressor program you are trying to optimize is: \n" + c_program_contents + "\n\nThink about the nature of the taskload, like how the stressor algorithm's use of memory might affect cache hit-rate/execution speed"
        initial_prompt += "Generate an initial outline of 4-6 phases, tailored to the context of optimizing microarchitecture params for the C program's execution"
        initial_prompt += "You can modify the following params: "
        for i in PARAMS:
            if(params["min"][i] != params["max"][i]):
                initial_prompt += ("\n" + str(i) + " in range " + str(params["min"][i]) + " to " + str(params["max"][i]))
        
        initial_prompt += "\n\nFor each phase, specify a small goal, a hypothesis, the 1 to 3 parameters you want to change in that phase, the start and endpoint for each parameter you are changing, the number of steps (trials) you are going to take to reach from start to end" 
        initial_prompt += "\n\nRemember, you are not simply maximizing the cache size or number of cores as that would obviously result in maximum speed. Instead, you can slowly linearly interpolate a parameter over 10-20 trials, and identify exactly when a bottleneck is reached, when no further progress is made even though cache size is increasing and making microarchitecture more costly.\nWhen changing from one memory size to another, you can only go in powers of 2. So 16MB to 128MB should have: 16MB, 32MB, 64MB, 128MB, with the number of steps being 4"
        initial_prompt += "\n\n Format as follows:\n"
        initial_prompt += """PhaseNumber "PhaseGoal" "PhaseHypothesis" NumParamsChanging "PhaseParam1" ... "PhaseParamN" "PhaseParam1Min" ... "PhaseParamNMin" "PhaseParam1Max" ... "PhaseParamNMax" PhaseNumTrials
            e.g.
            0 "Determine IPC sensitivity to L1D capacity, since the C program has 40000+ sequential array elements for data that can be cached efficiently spacially" "Cache hitrate will improve >10% proving L1D capacity is a bottleneck, now fixed and move to phase 1" 1 "l1d_size" "16kB" "64kB" 10
            1 "Find minimum L1 associativity required to minimize hardware costs, because L1D capacity was increased in phase 0" "IPC will flatline at one of the trials, and the inflection point associativity value can be found" 1 "l1d_assoc" "1" "5" 5
            etc
            """

        # response = client.models.generate_content(
        #     model="gemini-3-flash-preview",
        #     contents=[
        #         {
        #             "role": "system",
        #             "parts": [{"text": SYSTEM_INSTRUCTION}]
        #         },
        #         {
        #             "role": "user",
        #             "parts": [{"text": initial_prompt}]
        #         }
        #     ]
        # )
        # print("Generate Prompt:", initial_prompt)
        # print("\n\nGenerate AI Response:", response.text)
    
        out = """0 "Determine L1D capacity sensitivity to minimize data-access stalls during array manipulation" "The sorting algorithms (especially Merge Sort with auxiliary buffers and Bubble Sort's repeated passes) will show significant IPC gains as L1D size increases, until the working set of the array and stack fits entirely within the cache" 1 "l1d_size" "2kB" "32kB" 15
    1 "Evaluate L1I capacity requirements for recursive kernels and library overhead" "The instruction footprint includes recursion logic and C standard library calls (malloc, printf, rand); IPC will improve initially but hit a plateau early (likely around 16kB-32kB) as the core loops are small" 1 "l1i_size" "1kB" "64kB" 15
    2 "Optimize L1I associativity to mitigate conflict misses during deep recursion" "The recursive nature of Quick Sort and Merge Sort involves frequent jumps between the sorting logic and the partition/merge subroutines; higher associativity will reduce conflict misses in the instruction cache, stabilizing IPC" 1 "l1i_assoc" "3" "7" 5
    3 "Assess DDR capacity impact on execution time to identify the minimum viable memory footprint" "Since the workload is primarily CPU and cache-bound with a small data footprint (N=100), increasing DDR size beyond the initial threshold will yield negligible performance gains, allowing for cost-reduction" 1 "DDR_memory_size" "16MB" "128MB" 8"""
        params["outline"]["phases"] = out
    
    storeParams()
    
    parsedOutline = parseOutlineResponse(params["outline"]["phases"])
    frontEndPrinting = []
    num = 0
    for p in parsedOutline:
        st = "Phase " + str(num) + ": " + p[0]
        st += "\n\nHypothesis: " + p[1] + "\n"
        
        paramNum = 0
        for k in p[2]:
            st += "\nChanging " + k + " from " + str(p[3][paramNum][0]) + " to " + str(p[3][paramNum][1])
            paramNum += 1

        st += "\nNumber of steps (trials): " + str(p[4])
        frontEndPrinting.append(st)
        num += 1

    return frontEndPrinting

def log2_int(n: int) -> int:
    return n.bit_length() - 1

def lerp(frac, low1, high1, low2, high2):
    if high1 == low1:
        raise ValueError("high1 and low1 cannot be equal")

    t = (frac - low1) / (high1 - low1)
    return int(low2 + t * (high2 - low2))

def runExperiment():
    if(params["outline"]["phases"] == ""):
        return "NOT READY"
    
    p = params["runtime"]["status"]["current_phase"]
    t = params["runtime"]["status"]["current_trial"]

    if(("phase_"+str(p)) in params["runtime"]["phase_history"]):
        phaseInfo = params["runtime"]["phase_history"][("phase_"+str(p))]
        if(phaseInfo["num_trials"] == t):
            params["runtime"]["status"]["current_trial"] = 0
            modif_prompt = "&You just finished running phase " + str(p) +" with the following info: " + json.dumps(params["runtime"]["phase_history"]["phase_" + str(p)], indent=2)
            modif_prompt += "\n\nHere are raw trial logs: " + str(params["runtime"]["raw_trials"])
            modif_prompt += "\n\nTrial logs are in the format 'trial_phasenumber_trialnumber'. Analyze all the trials of the phase you just ran and identify if the hypothesis was correct. If correct, don't modify the outline much. If incorrect, update the outline from the next phase onward to improve the experiment dynammically now that you see what the experiment results are producing."
            generateOutline(modif_prompt)
            params["runtime"]["phase_history"]["phase_" + str(p)]["embedding_branch_decision"] = params["runtime"]["outline"]["runtime_modifications"][-1]
            params["runtime"]["status"]["current_phase"] += 1
        else:
            ind = 0
            arrayToLog = []
            for par in phaseInfo["params_changed"]:
                mini = str(params["min"][par])
                maxi = str(params["max"][par])
                arrayToLog.append(par)
                if(mini.isdigit()):
                    params["vars"][par] = lerp(t, 0, phaseInfo["num_trials"], maybeInt(mini), maybeInt(maxi))
                    arrayToLog.append(params["vars"][par])
                else:
                    unit = mini[-2:]
                    mini = mini[:-2]
                    maxi = maxi[:-2]

                    params["vars"][par] = str(1 << lerp(t, 0, phaseInfo["num_trials"]-1, log2_int(maybeInt(mini)), log2_int(maybeInt(maxi)))) + unit
                    arrayToLog.append(params["vars"][par])
                ind += 1
            storeParams()
            runTrial()
            stats = extractTrialStats()
            params["runtime"]["raw_trials"][("trial_"+str(p)+"_"+str(t))] = {
                "param_values" : arrayToLog,
                "results" : ["Sim Secs", stats[0], "Used Memory Bytes", stats[6], "Instr Rate", stats[9]]
            }
            params["runtime"]["status"]["current_trial"] += 1
            return stats
    else:
        outline = params["outline"]["phases"]
        parsedOutline = parseOutlineResponse(outline)
        if(p >= len(parsedOutline)):
            print("Done Experimenting")
        else:
            row = parsedOutline[p]
            params["runtime"]["phase_history"][("phase_"+str(p))] = {
                "goal": row[0],
                "hypothesis": row[1],
                "params_changed": row[2],
                "num_trials": row[4],
                "param_ranges": row[3],
                "embedding_branch_decision": ""
            }
            params["runtime"]["status"]["current_trial"] = 0
    storeParams()

    return "NULL"

# setStressorWorkloadSize()
# assemblyProgram()
# runTrial()
# printTrialStats()
# print(extractTrialStats())