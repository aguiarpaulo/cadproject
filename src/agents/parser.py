# Agent responsible for parsing natural language into a structured schema.
import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv
from src.schemas.data_models import RawInputSchema

# Load environment variables from a .env file if one exists
load_dotenv()

# --- Gemini API Configuration ---
try:
    # Attempt to get the API key from an environment variable
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable not found.")
    genai.configure(api_key=GEMINI_API_KEY)
    print("Gemini API configured successfully.")
except ValueError as e:
    print(f"[Parser Agent Error] {e}")
    print("Please set the GEMINI_API_KEY environment variable or create a .env file with it.")
    # You might want to exit or handle this more gracefully
    GEMINI_API_KEY = None # Ensure it's None if not found

class ParserAgent:
    """
    Uses a Large Language Model (Gemini) to parse natural language input
    from the user into a structured RawInputSchema.
    """

    def __init__(self, model_name="gemini-2.5-flash"):
        """Initializes the ParserAgent with a specific Gemini model."""
        if not GEMINI_API_KEY:
            raise ConnectionError("Gemini API key is not configured. Cannot initialize ParserAgent.")
        self.model = genai.GenerativeModel(model_name)
        print(f"ParserAgent initialized with model '{model_name}'.")

    def run(self, text_input: str) -> RawInputSchema:
        """
        Parses the user's text input by calling the Gemini API and validating
        the response against the RawInputSchema.
        """
        print("--- Running Parser Agent ---")
        prompt = self._get_llm_prompt(text_input)
        
        try:
            # Call the LLM
            response = self.model.generate_content(prompt)
            
            # Extract and clean the JSON from the response
            json_string = self._extract_json(response.text)
            
            # Parse the JSON string into a dictionary
            parsed_dict = json.loads(json_string)
            
            # Validate the dictionary with Pydantic
            schema = RawInputSchema.model_validate(parsed_dict)
            
            print(f"Successfully parsed input into RawInputSchema.")
            print(f"Parsed Schema: {schema.model_dump_json(indent=2)}")
            return schema

        except json.JSONDecodeError as e:
            print(f"[Parser Agent Error] Failed to decode JSON from LLM response: {e}")
            print(f"LLM Raw Response:\n---\n{response.text}\n---")
            raise ValueError("Could not parse a valid JSON response from the language model.")
        except Exception as e:
            print(f"[Parser Agent Error] An unexpected error occurred: {e}")
            raise

    def _extract_json(self, text: str) -> str:
        """
        Extracts a JSON string from the LLM's markdown-formatted response.
        Handles ```json ... ``` code blocks.
        """
        # Use regex to find content between ```json and ```
        match = re.search(r"```json\s*([\s\S]+?)\s*```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        # Fallback if no markdown block is found
        return text.strip()

    def _get_llm_prompt(self, text_input: str) -> str:
        """
        Generates the full, detailed prompt to be sent to the Gemini LLM.
        This prompt is crucial for getting a reliable JSON output.
        """
        # This prompt is engineered to guide the LLM's output.
        # It includes the task description, the desired JSON schema, and the user's input.
        prompt = f"""
        **Your Task:**
        You are an expert architectural assistant. Your primary function is to analyze a user's description of a building layout and extract key information into a structured JSON format.

        **JSON Output Schema:**
        You MUST output a single JSON object that adheres to the following structure. Do not add any extra commentary or text outside of the JSON block.

        ```json
        {{
          "project_name": "string (optional, name for the whole project)",
          "settings": {{
            "units": "string (optional, e.g., 'metros', 'cm', 'milimetros')"
          }},
          "environments": [
            {{
              "name": "string (the name of the room, e.g., 'sala', 'cozinha', 'quarto')",
              "description": "string (the full, original description of the room and its dimensions, e.g., 'uma sala de 6 por 4 metros')",
              "objects": [
                {{
                  "type": "string (the type of object, e.g., 'porta', 'janela', 'tomada')",
                  "description": "string (the full, original description of the object, e.g., 'uma porta de 80cm centralizada na parede maior')",
                  "quantity": "integer (the number of identical objects, e.g., 2)",
                  "width": "float (the width of the object in the project's units)",
                  "height": "float (the height of the object, optional)",
                  "positioning": {{
                    "on_wall": "string (e.g., 'parede maior', 'parede de 4 metros', 'qualquer parede')",
                    "centered": "boolean (true if the object is centered on the wall)",
                    "distance": "float (the distance from a reference point)",
                    "from_": "string (the reference point, e.g., 'canto esquerdo', 'centro')"
                  }}
                }}
              ]
            }}
          ]
        }}
        ```

        **Object Details Extraction:**
        - **quantity**: If the user mentions multiple identical items (e.g., "2 portas", "três janelas"), capture this number. Default is 1.
        - **width/height**: Extract dimensions. Assume the unit is the one defined in `settings.units`. If a different unit is explicitly mentioned (e.g., "80cm" when `settings.units` is "metros"), try to convert it to the `settings.units` or at least capture the numerical value if conversion is not straightforward.
        - **positioning**:
          - `on_wall`: Identify which wall the object is on. Use descriptive terms from the prompt ("parede maior", "parede menor", "parede de 6m").
          - `centered`: Set to `true` if the prompt says "centralizada" or "no meio da parede".
          - `distance`: Capture the numerical value of the distance from a reference point (e.g., "a 1 metro" -> 1.0, "a 20 cm" -> 0.2 if units are meters).
          - `from`: Capture the reference point (e.g., "canto esquerdo", "canto", "lado esquerdo", "centro").

        **Example:**

        *User Request:*
        "Uma sala retangular de 5x4 metros. Na parede maior, adicione 2 portas de 80cm, cada uma a 1 metro do canto mais próximo. Adicione também uma tomada centralizada em cada uma das paredes menores."

        *Expected JSON Output:*
        ```json
        {{
            "settings": {{ "units": "metros" }},
            "environments": [
                {{
                    "name": "sala",
                    "description": "Uma sala retangular de 5x4 metros",
                    "objects": [
                        {{
                            "type": "porta",
                            "description": "2 portas de 80cm, cada uma a 1 metro do canto mais próximo",
                            "quantity": 2,
                            "width": 0.8,
                            "positioning": {{
                                "on_wall": "parede maior",
                                "distance": 1.0,
                                "from_": "canto mais próximo"
                            }}
                        }},
                        {{
                            "type": "tomada",
                            "description": "uma tomada centralizada em cada uma das paredes menores",
                            "quantity": 2,
                            "positioning": {{
                                "on_wall": "paredes menores",
                                "centered": true
                            }}
                        }}
                    ]
                }}
            ]
        }}
        ```

        **Analysis of User Input:**
        Now, analyze the following user request and convert it into the JSON format described above.

        **User Request:**
        "{text_input}"

        **JSON Output:**
        """
        return prompt.strip()

# Example usage for testing
if __name__ == '__main__':
    # Make sure to set your GEMINI_API_KEY as an environment variable
    if not GEMINI_API_KEY:
        print("Skipping example: GEMINI_API_KEY not set.")
    else:
        parser = ParserAgent()
        # test_prompt = "uma sala retangular de 6 metros por 4 metros. Na parede maior de baixo, adicione uma porta de 90cm que fica a 1 metro do canto esquerdo. Na parede da direita, adicione uma janela de 2 metros, centralizada."
        test_prompt = "Quero uma sala de 6x4m, com uma porta de 80cm na parede maior"
        
        try:
            raw_schema = parser.run(test_prompt)
            print("\n--- Parser Ran Successfully ---")
        except (ValueError, ConnectionError) as e:
            print(f"\n--- Parser Failed ---")
            print(e)
