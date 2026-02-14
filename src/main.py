# Main entry point for the CAD Agent application.
import os
import sys
import subprocess

# Resolve project root relative to this file (src/main.py -> project root)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add project root to path so 'from src...' imports work
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.orchestrator import Orchestrator


def setup_template():
    """Ensure the template.dxf file exists."""
    template_path = os.path.join(PROJECT_ROOT, "templates", "template.dxf")
    if not os.path.exists(template_path):
        print("Template file not found. Running creation script...")
        script_path = os.path.join(PROJECT_ROOT, "create_template.py")
        try:
            subprocess.run(
                [sys.executable, script_path],
                check=True,
                cwd=PROJECT_ROOT,
            )
            print("Template created successfully.")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error: Could not create template file automatically: {e}")
            print("Please run 'python create_template.py' from the project root.")
            sys.exit(1)
    return template_path


def main():
    """
    Main function to run the interactive CAD agent.
    """
    print("Initializing CAD Agent...")
    template_path = setup_template()
    orchestrator = Orchestrator(template_path=template_path)

    print("\n--- AI Architecture Assistant ---")
    print("Describe the floor plan you want to create. Type 'exit' to close.")

    while True:
        try:
            user_prompt = input("\nYou: ")
            if user_prompt.lower() == 'exit':
                print("Exiting. Goodbye!")
                break

            output_file = os.path.join(PROJECT_ROOT, "output.dxf")
            orchestrator.run(user_prompt, output_filename=output_file)

        except KeyboardInterrupt:
            print("\nExiting. Goodbye!")
            break
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
            print("Please try again.")


if __name__ == "__main__":
    main()
