# Copyright (c) 2021 The Regents of the University of California
# All rights reserved.
#
# This file configures and runs a gem5 simulation using
# parameterized microarchitecture settings loaded from JSON.

import json
from pathlib import Path

# gem5 imports for ISA checking and simulation components
from gem5.isas import ISA
from gem5.utils.requires import requires
from gem5.resources.resource import CustomResource

# Memory system components
from gem5.components.memory import SingleChannelDDR3_1600

# Processor-related imports
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor

# Board and simulation control
from gem5.components.boards.simple_board import SimpleBoard
from gem5.simulate.simulator import Simulator

# Cache hierarchy (private L1, shared L2)
from gem5.components.cachehierarchies.classic.private_l1_shared_l2_cache_hierarchy import (
    PrivateL1SharedL2CacheHierarchy,
)

# ---------------------------------------------------------------------
# Load Microarchitecture Parameters
# ---------------------------------------------------------------------

# Path to the JSON file containing architectural parameters
PARAM_FILE = Path(__file__).parent / "params.json"

# Load parameter values from JSON
# Expected format:
# {
#   "vars": {
#       "l1i_size": "...",
#       "l1i_assoc": ...,
#       "l1d_size": "...",
#       "l1d_assoc": ...,
#       "l2_size": "...",
#       "l2_assoc": ...,
#       "DDR_memory_size": "...",
#       "num_cores": ...
#   }
# }
with open(PARAM_FILE) as f:
    params = json.load(f)["vars"]

# ---------------------------------------------------------------------
# ISA Requirement Check
# ---------------------------------------------------------------------

# Ensure this simulation only runs if gem5 supports ARM ISA
requires(isa_required=ISA.ARM)

# ---------------------------------------------------------------------
# Cache Hierarchy Configuration
# ---------------------------------------------------------------------

# Create a cache hierarchy with:
# - Private L1 instruction and data caches per core
# - A shared L2 cache across all cores
cache_hierarchy = PrivateL1SharedL2CacheHierarchy(
    l1i_size=params["l1i_size"],
    l1i_assoc=params["l1i_assoc"],
    l1d_size=params["l1d_size"],
    l1d_assoc=params["l1d_assoc"],
    l2_size=params["l2_size"],
    l2_assoc=params["l2_assoc"],
)

# ---------------------------------------------------------------------
# Memory System Configuration
# ---------------------------------------------------------------------

# Create a single-channel DDR3 memory system
# The memory size is parameterized via params.json
memory = SingleChannelDDR3_1600(
    size=params["DDR_memory_size"]
)

# ---------------------------------------------------------------------
# Processor Configuration
# ---------------------------------------------------------------------

# Create a simple timing CPU model
# - TIMING CPU models cache and memory latency
# - Number of cores is configurable
processor = SimpleProcessor(
    cpu_type=CPUTypes.TIMING,
    isa=ISA.ARM,
    num_cores=params["num_cores"],
)

# ---------------------------------------------------------------------
# Board Configuration
# ---------------------------------------------------------------------

# The board ties together:
# - Clock frequency
# - Processor
# - Memory system
# - Cache hierarchy
board = SimpleBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
)

# ---------------------------------------------------------------------
# Workload Configuration
# ---------------------------------------------------------------------

# Load the ARM binary to be executed by gem5
# This binary is typically compiled using aarch64-linux-gnu-gcc
binary = CustomResource(
    local_path=str(Path(__file__).parent / "microbench.arm")
)

# Set the binary as the workload for the board
board.set_se_binary_workload(binary)

# ---------------------------------------------------------------------
# Simulation Execution
# ---------------------------------------------------------------------

# Create the simulator with the configured board
simulator = Simulator(board=board)

# Run the simulation until completion
simulator.run()

# Print simulation exit information
print(
    f"Exiting @ tick {simulator.get_current_tick()} "
    f"because {simulator.get_last_exit_event_cause()}."
)
