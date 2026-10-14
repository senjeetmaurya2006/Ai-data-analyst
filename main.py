import argparse
import subprocess
import sys
from agents.orchestrator_agent import OrchestratorAgent


def main():
    parser = argparse.ArgumentParser(description="AI End-to-End Data Analyst")
    parser.add_argument(
        "--file", type=str, help="Path to CSV or XLSX file for CLI execution"
    )
    parser.add_argument("--sheet", type=str, default=None, help="Optional Excel sheet")
    parser.add_argument(
        "--ui", action="store_true", help="Launch Streamlit interactive application"
    )
    args = parser.parse_args()

    if args.ui or not args.file:
        subprocess.run(
            [sys.executable, "-m", "streamlit", "run", "app/streamlit_app.py"],
            check=True,
        )
    else:
        orch = OrchestratorAgent()
        context = orch.run_full_pipeline(
            args.file,
            sheet_name=args.sheet,
            progress_callback=lambda msg, pct: print(f"[{int(pct * 100):3d}%] {msg}"),
        )
        artifacts = context.artifacts
        print("\n=== ANALYSIS COMPLETE ===")
        print(f"Executive PDF  : {artifacts.pdf_path}")
        print(f"PowerPoint Deck: {artifacts.pptx_path}")
        print(f"HTML Dashboard : {artifacts.html_path}")


if __name__ == "__main__":
    main()
