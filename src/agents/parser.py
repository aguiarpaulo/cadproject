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
              "description": "string (MUST include the room dimensions, e.g., 'uma sala de 6 por 4 metros')",
              "objects": [
                {{
                  "type": "string (the type of object, e.g., 'porta', 'janela', 'tomada')",
                  "description": "string (full description including wall and positioning, e.g., 'uma porta de 80cm centralizada na parede maior')",
                  "quantity": "integer (the number of identical objects, default 1)",
                  "width": "float (the width of the object in the project's units)",
                  "height": "float (the height of the object, optional)",
                  "positioning": {{
                    "on_wall": "string (REQUIRED - which wall, e.g., 'parede maior', 'parede menor', 'parede de 4 metros', 'parede da esquerda', 'parede da direita', 'parede de baixo', 'parede de cima')",
                    "centered": "boolean (true if the object is centered on the wall)",
                    "distance": "float (the distance from a reference point)",
                    "from_": "string (the reference point, e.g., 'canto esquerdo', 'canto direito')"
                  }}
                }}
              ]
            }}
          ]
        }}
        ```

        **CRITICAL RULES:**

        1. **`positioning.on_wall` is REQUIRED for every object.** You MUST always specify which wall an object belongs to. Use one of these standard terms:
           - "parede maior" (the longer wall of the room)
           - "parede menor" (the shorter wall of the room)
           - "parede de baixo", "parede de cima", "parede da esquerda", "parede da direita"
           - "parede de Xm" or "parede de X metros" (wall by its dimension)
           If the user does NOT specify a wall, use "parede maior" as the default for doors and "parede menor" for windows.

        2. **`positioning.centered`**: Set to `true` if the user says "centralizada", "no centro", "no meio". If the user does not specify positioning, default to `true`.

        3. **`description` for environments**: MUST always contain the room dimensions in the format "NxN metros" or "N por N metros". Copy the dimensions from the user input.

        4. **`width`**: Always extract the object width as a float in the project's unit. Convert cm to meters (divide by 100). For example, "80cm" = 0.8, "1,5m" = 1.5.

        5. **`description` for objects**: Include ALL placement information from the user input (wall, positioning, distance).

        **Example:**

        *User Request:*
        "Quero um apartamento com sala de 5x4 metros com porta de 80cm e janela de 1.5m centralizada, e um quarto de 3x3 com porta de 70cm"

        *Expected JSON Output:*
        ```json
        {{
            "settings": {{ "units": "metros" }},
            "environments": [
                {{
                    "name": "sala",
                    "description": "sala de 5x4 metros",
                    "objects": [
                        {{
                            "type": "porta",
                            "description": "porta de 80cm na parede maior",
                            "quantity": 1,
                            "width": 0.8,
                            "positioning": {{
                                "on_wall": "parede maior",
                                "centered": true
                            }}
                        }},
                        {{
                            "type": "janela",
                            "description": "janela de 1.5m centralizada na parede menor",
                            "quantity": 1,
                            "width": 1.5,
                            "positioning": {{
                                "on_wall": "parede menor",
                                "centered": true
                            }}
                        }}
                    ]
                }},
                {{
                    "name": "quarto",
                    "description": "quarto de 3x3 metros",
                    "objects": [
                        {{
                            "type": "porta",
                            "description": "porta de 70cm na parede maior",
                            "quantity": 1,
                            "width": 0.7,
                            "positioning": {{
                                "on_wall": "parede maior",
                                "centered": true
                            }}
                        }}
                    ]
                }}
            ]
        }}
        ```

        **Analysis of User Input:**
        Now, analyze the following user request and convert it into the JSON format described above. Remember: every object MUST have `positioning.on_wall` filled in.

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
