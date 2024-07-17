import questionary
from pipa.common.hardware.cpu import get_cpu_cores
from rich import print
from io import TextIOWrapper
from datetime import datetime


import os
import yaml


def ask_number(question: str, default: int) -> int:
    """
    Asks the user to input a number based on the given question and default value.

    Args:
        question (str): The question to ask the user.
        default (int): The default value to return if the user doesn't input anything.

    Returns:
        int: The number inputted by the user or the default value.
    """
    result = questionary.text(question, str(default)).ask().strip()

    if result == "":
        return default
    elif result.isdigit():
        return int(result)
    else:
        print("Please input a number.")
        exit(1)


CORES_ALL = get_cpu_cores()


def quest_basic():
    workspace = questionary.text(
        "Where do you want to store your data? (Default: ./)\n", "./"
    ).ask()

    if workspace == "":
        workspace = "./"

    if not os.path.exists(workspace):
        os.makedirs(workspace)

    freq_record = ask_number(
        "What's the frequency of perf-record? (Default: 999)\n", 999
    )
    events_record = questionary.text(
        "What's the event of perf-record? (Default: {cycles,instructions}:S)\n",
        "{cycles,instructions}:S",
    ).ask()

    annotete = questionary.select(
        "Whether to use perf-annotate?\n", choices=["Yes", "No"], default="No"
    ).ask()
    annotete = True if annotete == "Yes" else False

    stat = questionary.select(
        "Do you want to use perf-stat or emon?\n",
        choices=["perf-stat", "emon"],
        default="perf-stat",
    ).ask()

    if stat == "perf-stat":
        freq_stat = ask_number(
            "What's count deltas of perf-stat? (Default: 1000 milliseconds)\n", 1000
        )
        events_stat = questionary.text(
            "What's the event of perf-stat?\n",
            "cycles,instructions,branch-misses,L1-dcache-load-misses,L1-icache-load-misses",
        ).ask()
        return {
            "workspace": workspace,
            "freq_record": freq_record,
            "events_record": events_record,
            "use_emon": False,
            "count_delta_stat": freq_stat,
            "events_stat": events_stat,
            "annotete": annotete,
        }
    elif stat == "emon":
        mpp = questionary.text(
            "Where is the mpp?\n",
            "/mnt/hdd/share/emon/system_health_monitor",
        ).ask()
        return {
            "workspace": workspace,
            "freq_record": freq_record,
            "events_record": events_record,
            "use_emon": True,
            "mpp": mpp,
            "annotete": annotete,
        }

    raise ValueError("Invalid choice.")


def write_title(file: TextIOWrapper):
    current_time = datetime.now().isoformat()
    file.write(
        f"""#!/bin/bash
# The script generated by PIPA-TREE is used to collect performance data.
# Please check whether it meets expectations before running.
# ZJU SPAIL(https://github.com/ZJU-SPAIL) reserves all rights.
# Generated at {current_time}

# Check if sar and perf are available
if ! command -v sar &> /dev/null; then
echo "sar command not found. Please install sar."
exit 1
fi

if ! command -v perf &> /dev/null; then
echo "perf command not found. Please install perf."
exit 1
fi\n\n"""
    )


def load_yaml_config(file_path: str = "config-pipa-shu.yaml") -> dict:
    """
    Parses a YAML file and returns the contents as a dictionary.

    Args:
        file_path (str): The path to the YAML file.

    Returns:
        dict: The contents of the YAML file as a dictionary.
    """
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)
    return data


def opener(path, flags):
    descriptor = os.open(path=path, flags=flags, mode=0o755)
    return descriptor


def parse_basic(data: dict):
    workspace = data["workspace"]
    freq_record = data["freq_record"]
    events_record = data["events_record"]
    freq_stat = data["count_delta_stat"]
    events_stat = data["events_stat"]
    annotete = data["annotete"]
    run_by_perf = data["run_by_perf"]
    return (
        workspace,
        freq_record,
        events_record,
        freq_stat,
        events_stat,
        annotete,
        run_by_perf,
    )


def parse_run_by_pipa(data: dict):
    use_taskset = data["use_taskset"]
    core_range = data["core_range"]
    command = data["command"]
    return use_taskset, core_range, command


def parse_run_by_user(data: dict):
    duration_record = data["duration_record"]
    duration_stat = data["duration_stat"]
    return duration_record, duration_stat
