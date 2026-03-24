#!/usr/bin/env python
import sys
import subprocess

def main():
    if len(sys.argv) < 2:
        print("Usage: python run.py [test|generate|run]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "test":
        subprocess.run(["python", "test_runner.py"])
    elif cmd == "generate":
        subprocess.run(["python", "test_runner.py", "--generate"])
    elif cmd == "run":
        subprocess.run(["python", "-m", "src.cli", "lex", "--input", "examples/hello.src"])
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()