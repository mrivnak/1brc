#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
from typing import List

from termcolor import colored


def bench(cmd: List[str], cwd: str) -> float:
    # TODO: run benchmark
    return 1.0


def test(cmd: List[str], cwd: str, expected: str) -> bool:
    result = subprocess.run(
        cmd, cwd=cwd, capture_output=True, env=os.environ.copy(), check=False
    )
    if result.returncode != 0:
        print(result.stderr.decode("utf-8"))
        return False
    return result.stdout.decode("utf-8").strip() == expected


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("test", "run"))
    parser.add_argument("--fail-fast", action="store_true")

    args = parser.parse_args()

    expected = "something"  # TODO

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
        }
    ]
    for config in configs:
        for build in config["build"]:
            subprocess.run(build, cwd=config["dir"], env=os.environ.copy(), check=True)

        name = config["name"]

        if test(config["run"], config["dir"], expected):
            print(f"{colored('', 'green')} {name} passed")
        else:
            print(f"{colored('', 'red')} {name} failed")
            if args.fail_fast:
                print("Test failed, exiting", file=sys.stderr)
                exit(1)
            else:
                continue

        if args.action == "run":
            print("TODO: run benchmark")
            bench(config["run"], config["dir"])
        else:
            raise Exception("Unknown action")


if __name__ == "__main__":
    main()
