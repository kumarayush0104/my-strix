#!/usr/bin/env python3
"""
Convenience launcher for Strix scans and live viewer.
Usage:
    python scan.py --target https://example.com
    python scan.py --target https://example.com --mode deep --budget 10
"""

import argparse
import os
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description="Launch a Strix pentest scan without client verification.")
    parser.add_argument(
        "--target", "-t",
        required=True,
        help="Target URL, domain, IP, or local repository path (e.g. https://your-staging.com)"
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["quick", "deep"],
        default="quick",
        help="Scan mode: quick (default, faster) or deep (thorough)"
    )
    parser.add_argument(
        "--budget", "-b",
        type=float,
        default=5.0,
        help="Maximum LLM spend budget in USD (default: $5.00)"
    )
    parser.add_argument(
        "--view",
        action="store_true",
        default=True,
        help="Launch the web viewer after completion (default: True)"
    )
    args = parser.parse_args()

    # Check environment variables
    llm = os.environ.get("STRIX_LLM")
    key = os.environ.get("LLM_API_KEY") or os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY")

    if not llm or not key:
        print("\n[!] Error: AI Model configuration missing.")
        print("Please set your AI environment variables first:")
        print("  export STRIX_LLM=\"gemini/gemini-2.5-flash\"  # or gemini/gemini-2.5-pro")
        print("  export LLM_API_KEY=\"your-gemini-key-here\"\n")
        sys.exit(1)

    # Ensure LLM_API_KEY is exported for Strix
    if key and "LLM_API_KEY" not in os.environ:
        os.environ["LLM_API_KEY"] = key

    print("\n" + "=" * 60)
    print(f"🚀 Starting Strix scan on: {args.target}")
    print(f"   Mode:   {args.mode}")
    print(f"   Budget: ${args.budget:.2f} USD")
    print(f"   Model:  {llm}")
    print("=" * 60 + "\n")

    import shutil
    from pathlib import Path

    # Find the appropriate strix command prefix
    if shutil.which("strix"):
        strix_base = ["strix"]
    elif Path(".venv/bin/strix").exists():
        strix_base = [str(Path(".venv/bin/strix").resolve())]
    elif Path(".venv/Scripts/strix.exe").exists():
        strix_base = [str(Path(".venv/Scripts/strix.exe").resolve())]
    else:
        # Check for uv
        uv_path = shutil.which("uv")
        if not uv_path:
            for p in [Path.home() / ".local/bin/uv", Path.home() / ".cargo/bin/uv"]:
                if p.exists():
                    uv_path = str(p)
                    break
        if uv_path:
            strix_base = [uv_path, "run", "strix"]
        else:
            print("\n[!] Error: 'strix' executable or 'uv' not found in PATH.")
            print("Please ensure you have run 'uv sync' or are running via:")
            print("    uv run python scan.py ...")
            sys.exit(1)

    cmd = strix_base + [
        "-n",
        "--target", args.target,
        "--scan-mode", args.mode,
        "--max-budget", str(args.budget),
    ]

    try:
        # Run scan
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n[!] Scan finished with exit code {e.returncode}")
    except KeyboardInterrupt:
        print("\n[!] Scan cancelled by user.")
        sys.exit(0)

    if args.view:
        print("\n📊 Launching web viewer for results...")
        try:
            view_cmd = strix_base + ["view", "--host", "0.0.0.0", "--port", "8000"]
            subprocess.run(view_cmd)
        except KeyboardInterrupt:
            print("\nViewer stopped.")


if __name__ == "__main__":
    main()
