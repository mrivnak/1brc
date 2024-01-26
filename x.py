#!/usr/bin/env python3

import argparse
import glob
import json
import os
import subprocess
import sys
from typing import List

from termcolor import colored


def bench(cmd: List[str], cwd: str, filename: str, name: str):
    subprocess.run(
        ["hyperfine", "--shell=none", "--warmup", "3", "--runs", "10", "-n", name, " ".join(cmd + [filename])],
        cwd=cwd,
        env=os.environ.copy(),
        check=True,
    )
    print("\x1b[1A", end="") # move cursor up one line (hyper fine prints an extra newline)
    mem_result = subprocess.run(["/usr/bin/time", "-f", "%M"] + cmd + [filename], cwd=cwd, capture_output=True, check=True)
    mem = int(mem_result.stderr.decode("utf-8").splitlines()[-1])
    if mem < 4096:
        print(f"  Max memory usage: {colored(round(float(mem), 2), 'green')} KiB")
    elif mem < 4096 * 1024:
        print(f"  Max memory usage: {colored(round(float(mem) / 1024.0, 2), 'green')} MiB")
    else:
        print(f"  Max memory usage: {colored(round(float(mem) / 1024.0 / 1024.0, 2), 'green')} GiB")
    print('')

def print_diff(expected: dict, actual: dict):
    for key in expected.keys():
        if key not in actual:
            print(f"{colored('ERROR:', 'red')} Missing key: {key}")
            continue
        if expected[key] != actual[key]:
            print(f"{colored('ERROR:', 'red')} Key: {key}")
            print(f"  Expected: {expected[key]}")
            print(f"  Actual: {actual[key]}")


def test(cmd: List[str], cwd: str) -> bool:
    test_files = glob.glob(os.path.join(os.getcwd(), "res", "data", "test", "*.in.txt"))
    if len(test_files) == 0:
        print("No test files found", file=sys.stderr)
        return False

    for test_file in test_files:
        file = open(test_file.replace(".in.txt", ".out.json"), "r", encoding="utf-8")
        expected = json.loads(file.read())
        file.close()

        if not test_single(cmd + [os.path.join("..", test_file)], cwd, expected):
            print(f"Test failed for {test_file}", file=sys.stderr)
            return False
    return True


def test_single(cmd: List[str], cwd: str, expected: dict) -> bool:
    result = subprocess.run(
        cmd, cwd=cwd, capture_output=True, env=os.environ.copy(), check=False
    )
    if result.returncode != 0:
        print(result.stderr.decode("utf-8"))
        return False
    result_json = result.stdout.decode("utf-8").strip()
    actual = json.loads(result_json)
    if actual == expected:
        return True
    else:
        print_diff(expected, actual)
        return False


def generate_input(size: int) -> str:
    filename = os.path.join(os.getcwd(), "res", "data", "input.txt")

    if not os.path.exists(filename):
        print("Generating input file")
        generator_dir = os.path.join(os.getcwd(), "res", "data", "generator")
        result = subprocess.run(
            ["cargo", "run", "--release", "--", filename, str(size)],
            cwd=generator_dir,
            capture_output=True,
            check=True,
        )
        if result.returncode != 0:
            print(result.stderr.decode("utf-8"))
            exit(1)

    return filename


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("test", "run"))
    parser.add_argument("--fail-fast", "-f", action="store_true")
    parser.add_argument("--size", "-s", type=int, default=1000000000)

    args = parser.parse_args()

    configs = [
        # {
        #     "name": "C++",
        #     "dir": "cpp",
        #     "build": [
        #         ["cmake", ".", "-B", "build", "-DCMAKE_BUILD_TYPE=Release"],
        #         ["cmake", "--build", "build"],
        #     ],
        #     "run": ["./build/one-billion-rows"],
        # },
        # {
        #     "name": "Rust",
        #     "dir": "rust",
        #     "build": [["cargo", "build", "--release"]],
        #     "run": ["./target/release/one-billion-rows"],
        # },
        {
            "name": "C#",
            "dir": "csharp",
            "build": [["dotnet", "build", "-c", "Release"]],
            "run": ["./bin/Release/net8.0/OneBillionRows"],
        },
        # {
        #     "name": "Zig",
        #     "dir": "zig",
        #     "build": [["zig", "build", "-Doptimize=ReleaseFast"]],
        #     "run": ["./zig-out/bin/one-billion-rows"],
        # },
    ]
    for config in configs:
        for build in config["build"]:
            result = subprocess.run(
                build,
                cwd=config["dir"],
                env=os.environ.copy(),
                capture_output=True,
                check=True,
            )
            if result.returncode != 0:
                print(result.stderr.decode("utf-8"))
                exit(1)

        name = config["name"]

        if test(config["run"], config["dir"]):
            print(f"{colored('', 'green')} {name} passed")
        else:
            print(f"{colored('', 'red')} {name} failed")
            if args.fail_fast:
                print("Test failed, exiting", file=sys.stderr)
                exit(1)
            else:
                continue

        if args.action == "run":
            filename = generate_input(args.size)
            bench(config["run"], config["dir"], filename, config["name"])


if __name__ == "__main__":
    main()
