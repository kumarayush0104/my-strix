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
    key = os.environ.get("LLM_API_KEY")

    if not llm or not key:
        print("\n[!] Error: AI Model configuration missing.")
        print("Please set your AI environment variables first:")
        print("  export STRIX_LLM=\"openai/gpt-4o\"  # or anthropic/claude-3-7-sonnet, etc.")
        print("  export LLM_API_KEY=\"your-api-key\"\n")
        sys.exit(1)

    print("\n" + "=" * 60)
    print(f"🚀 Starting Strix scan on: {args.target}")
    print(f"   Mode:   {args.mode}")
    print(f"   Budget: ${args.budget:.2f} USD")
    print(f"   Model:  {llm}")
    print("=" * 60 + "\n")

    cmd = [
        "strix",
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
            subprocess.run(["strix", "view", "--host", "0.0.0.0", "--port", "8000"])
        except KeyboardInterrupt:
            print("\nViewer stopped.")


if __name__ == "__main__":
    main()
