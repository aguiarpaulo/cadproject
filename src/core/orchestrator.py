# Main orchestrator for the agent pipeline
from src.agents.parser import ParserAgent
from src.agents.planner import PlannerAgent
from src.agents.geometry import GeometryAgent
from src.agents.generator import DXFGeneratorAgent
from src.schemas.data_models import StructuredPlanSchema

MAX_CLARIFICATION_ROUNDS = 3


class Orchestrator:
    """
    Manages the flow of data between agents and handles the overall process.
    """

    def __init__(self, template_path="templates/template.dxf"):
        self.parser = ParserAgent()
        self.planner = PlannerAgent()
        self.geometry = GeometryAgent()
        self.generator = DXFGeneratorAgent()
        self.template_path = template_path
        print("Orchestrator initialized.")

    def run(self, text_input: str, output_filename: str = "output.dxf"):
        """
        Executes the full pipeline from natural language to DXF file.
        """
        # 1. Parse
        raw_schema = self.parser.run(text_input)

        # 2. Plan
        plan_or_question = self.planner.run(raw_schema)

        # 3. Handle feedback loop if necessary (with a retry limit)
        retries = 0
        while isinstance(plan_or_question, str) and retries < MAX_CLARIFICATION_ROUNDS:
            retries += 1
            print(f"\n--- Clarification Required ({retries}/{MAX_CLARIFICATION_ROUNDS}) ---")
            user_response = input(f"Agent: {plan_or_question}\nYou: ")

            if not user_response.strip():
                continue

            # Combine original request with the clarification for a re-parse
            combined_input = f"{text_input}. Informação adicional: {user_response}"
            text_input = combined_input

            print("\n--- Re-running Pipeline with New Information ---")
            raw_schema = self.parser.run(combined_input)
            plan_or_question = self.planner.run(raw_schema)

        # Ensure we have a valid plan
        if not isinstance(plan_or_question, StructuredPlanSchema):
            print(f"Could not derive a valid plan after {retries} attempts. Aborting.")
            if isinstance(plan_or_question, str):
                print(f"Last issue: {plan_or_question}")
            return

        # 4. Calculate Geometry
        final_geometry = self.geometry.run(plan_or_question)

        # 5. Generate DXF
        self.generator.run(final_geometry, self.template_path, output_filename)
