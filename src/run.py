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
    elif args.command == 'semantic':
        cmd = ['python', '-m', 'src.cli', 'semantic', '--input', args.input]
        if args.output:
            cmd.extend(['--output', args.output])
        if args.symbols:
            cmd.append('--symbols')
        subprocess.run(cmd)
    elif args.command == 'test-semantic':
        subprocess.run(['python', 'test_semantic.py', '--verbose'] if args.verbose else ['python', 'test_semantic.py'])
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()