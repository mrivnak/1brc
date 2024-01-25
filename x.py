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
        ["hyperfine", "--warmup", "3", "--runs", "10", "-n", name, " ".join(cmd + [filename])],
        cwd=cwd,
        env=os.environ.copy(),
        check=True,
    )


def test(cmd: List[str], cwd: str) -> bool:
    test_files = glob.glob(os.path.join(os.getcwd(), "res", "data", "test", "*.in.txt"))
    if len(test_files) == 0:
        print("No test files found", file=sys.stderr)
        return False

    for test_file in test_files:
        expected = json.loads(test_file.replace(".in.txt", ".out.json"))
        if not test_single(cmd + [os.path.join("..", test_file)], cwd, expected):
            return False
    return True


def test_single(cmd: List[str], cwd: str, expected: dict) -> bool:
    result = subprocess.run(
        cmd, cwd=cwd, capture_output=True, env=os.environ.copy(), check=False
    )
    if result.returncode != 0:
        print(result.stderr.decode("utf-8"))
        return False
    return json.loads(result.stdout.decode("utf-8").strip()) == expected


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
        {
            "name": "C++",
            "dir": "cpp",
            "build": [
                ["cmake", ".", "-B", "build", "-DCMAKE_BUILD_TYPE=Release"],
                ["cmake", "--build", "build"],
            ],
            "run": ["./build/one-billion-rows"],
        },
        {
            "name": "Rust",
            "dir": "rust",
            "build": [["cargo", "build", "--release"]],
            "run": ["./target/release/one-billion-rows"],
        },
        {
            "name": "C#",
            "dir": "csharp",
            "build": [["dotnet", "build", "-c", "Release"]],
            "run": ["./bin/Release/net8.0/OneBillionRows"],
        },
        {
            "name": "Zig",
            "dir": "zig",
            "build": [["zig", "build", "-Doptimize=ReleaseFast"]],
            "run": ["./zig-out/bin/one-billion-rows"],
        },
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
