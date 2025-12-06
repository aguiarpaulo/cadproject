# Main entry point for the CAD Agent application.
import os
import sys

# Add src to path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.orchestrator import Orchestrator
import subprocess

def setup_template():
    """Ensure the template.dxf file exists."""
    template_path = "templates/template.dxf"
    if not os.path.exists(template_path):
        print("Template file not found. Running creation script...")
        try:
            # It's better to run this as a separate process
            subprocess.run([sys.executable, "create_template.py"], check=True)
            print("Template created successfully.")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error: Could not create template file automatically: {e}")
            print("Please run 'python create_template.py' manually.")
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

            output_file = "output.dxf" # Static name for simplicity
            orchestrator.run(user_prompt, output_filename=output_file)

        except KeyboardInterrupt:
            print("\nExiting. Goodbye!")
            break
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main()
