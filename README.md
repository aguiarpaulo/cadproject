# AI Architecture Assistant CAD Project

This project is a CAD agent that can understand natural language and generate DXF files.

## How to run the project

1.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Set up your Gemini API Key:**
    This project uses the Gemini API to understand natural language. You need to have a Gemini API key to run the project.
    You can get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

    Set up your API key as an environment variable **in the same terminal you will run the application**.

    *   On Windows (Command Prompt):
        ```cmd
        set GEMINI_API_KEY=YOUR_API_KEY
        ```
    *   On Windows (PowerShell):
        ```powershell
        $env:GEMINI_API_KEY="YOUR_API_KEY"
        ```
    *   On macOS/Linux (and Git Bash on Windows):
        ```bash
        export GEMINI_API_KEY="YOUR_API_KEY"
        ```

3.  **Run the application:**
    ```bash
    python src/main.py
    ```
    The application will start in an interactive mode. You can type your requests and the agent will generate a `output.dxf` file in the root of the project.

    **Example prompt:**
    ```
    uma sala de 6 metros por 5 metros com uma porta de 80cm centralizada na parede maior e uma janela de 1.5m a 1 metro do canto esquerdo na parede menor
    ```

4.  **Exit the application:**
    Type `exit` to close the application.

## Troubleshooting

### `GEMINI_API_KEY environment variable not found`

If you see this error:
```
[Parser Agent Error] GEMINI_API_KEY environment variable not found.
```
It means you have not set your API key correctly. Make sure you have followed Step 2 and have set the environment variable in the **same terminal session** where you are trying to run `python src/main.py`.
