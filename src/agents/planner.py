# Agent responsible for planning the drawing
import re
from typing import Union, List
from src.schemas.data_models import (
    RawInputSchema, RawEnvironment, RawObject,
    StructuredPlanSchema, DrawingSettings, Room, Wall, RoomDimensions,
    PlannedObject, ObjectPlacement
)

class PlannerAgent:
    """
    Validates the parsed input from the ParserAgent, enriches it with detailed
    information (like wall definitions), resolves ambiguities, and creates a
    structured, actionable plan for the GeometryAgent.
    """

    def run(self, raw_input: RawInputSchema) -> Union[StructuredPlanSchema, str]:
        """
        Processes the raw schema and returns either a structured plan or a
        clarification question.
        """
        print("--- Running Planner Agent ---")
        try:
            settings = DrawingSettings(units="meters", default_wall_thickness=0.15)
            planned_rooms: List[Room] = []
            planned_objects: List[PlannedObject] = []
            offset_x = 0.0

            if not raw_input.environments:
                return "Não consegui identificar nenhum ambiente no seu pedido. Poderia descrevê-lo?"

            # Create Room and Wall models
            for i, env in enumerate(raw_input.environments):
                dims = self._extract_dims_from_desc(env.description)
                if not dims:
                    return f"Não consegui determinar as dimensões para o ambiente '{env.name or i+1}'. Por favor, especifique como 'largura x comprimento'."
                
                room = Room(
                    id=f"room_{i}",
                    internal_dimensions=RoomDimensions(width=dims['width'], length=dims['length']),
                    origin_point=(offset_x, 0.0)
                )
                room.walls = self._create_room_walls(room)
                planned_rooms.append(room)

                # Update offset for the next room
                offset_x += dims['width'] + settings.default_wall_thickness

                # Plan objects for the current room (respecting quantity)
                for raw_obj in env.objects:
                    quantity = raw_obj.quantity or 1
                    for _ in range(quantity):
                        planned_obj = self._plan_object(raw_obj, room)
                        if isinstance(planned_obj, str): # It's a question
                            return planned_obj
                        planned_objects.append(planned_obj)
            
            plan = StructuredPlanSchema(
                drawing_settings=settings,
                rooms=planned_rooms,
                objects=planned_objects
            )
            print(f"Generated Plan: {plan.model_dump_json(indent=2)}")
            return plan

        except Exception as e:
            print(f"[Planner Error] {e}")
            return f"Ocorreu um erro ao planejar o seu projeto: {e}. Poderia reformular seu pedido?"

    def _create_room_walls(self, room: Room) -> List[Wall]:
        """Creates the four Wall objects for a rectangular room."""
        w = room.internal_dimensions.width
        l = room.internal_dimensions.length
        ox, oy = room.origin_point
        thickness = 0.15 # Default thickness

        walls = [
            Wall(id=f"{room.id}_wall_0", room_id=room.id, start=(ox, oy), end=(ox + w, oy), thickness=thickness, length=w), # Bottom
            Wall(id=f"{room.id}_wall_1", room_id=room.id, start=(ox + w, oy), end=(ox + w, oy + l), thickness=thickness, length=l), # Right
            Wall(id=f"{room.id}_wall_2", room_id=room.id, start=(ox + w, oy + l), end=(ox, oy + l), thickness=thickness, length=w), # Top
            Wall(id=f"{room.id}_wall_3", room_id=room.id, start=(ox, oy + l), end=(ox, oy), thickness=thickness, length=l), # Left
        ]
        return walls

    def _plan_object(self, raw_obj: RawObject, room: Room) -> Union[PlannedObject, str]:
        """Converts a RawObject into a PlannedObject with placement details."""

        # --- Type and Size ---
        obj_type_str = (raw_obj.type or "").lower()
        if "porta" in obj_type_str:
            obj_type = "DOOR"
        elif "janela" in obj_type_str:
            obj_type = "WINDOW"
        elif "tomada" in obj_type_str:
            obj_type = "POWER_SOCKET"
        else:
            return f"Tipo de objeto não reconhecido: '{raw_obj.type}'. Tipos suportados: porta, janela, tomada."

        # Use the width from the parser if available, otherwise extract/default it
        width = raw_obj.width
        if width is None:
            size_val = self._extract_size_from_desc(raw_obj.description)
            width = size_val
            if width is None:
                if obj_type == "DOOR":
                    width = 0.8  # Default door width
                elif obj_type == "WINDOW":
                    width = 1.5  # Default window width
                elif obj_type == "POWER_SOCKET":
                    width = 0.1  # Default outlet width

        # --- Placement ---
        # Try structured positioning data first, then fall back to description text
        pos = raw_obj.positioning
        wall_id = None
        if pos and pos.on_wall:
            wall_id = self._find_target_wall_id(pos.on_wall, room)
        if not wall_id:
            wall_id = self._find_target_wall_id(raw_obj.description, room)
        if not wall_id:
            # Smart default: doors on the longer wall, windows on shorter wall
            wall_id = self._default_wall_id(obj_type, room)
            print(f"No wall specified for '{raw_obj.description}', defaulting to '{wall_id}'.")

        # Check for positioning - prefer structured data over description text
        is_centered = (pos and pos.centered) or "centralizad" in raw_obj.description
        is_from_corner = (pos and pos.distance is not None) or "do canto" in raw_obj.description

        if is_centered:
            pos_type = "CENTERED"
            dist, corner = None, None
        elif is_from_corner:
            pos_type = "FROM_CORNER"

            dist = (pos.distance if pos else None) or self._extract_distance_from_desc(raw_obj.description)
            if dist is None:
                return f"Não consegui identificar a distância do canto para '{raw_obj.description}'."

            # Check for corner reference
            from_text = (pos.from_ if pos else None) or ""
            ref_text = raw_obj.description + " " + from_text
            if "esquerdo" in ref_text:
                corner = "START"
            elif "direito" in ref_text:
                corner = "END"
            else:
                return f"O objeto '{raw_obj.description}' está a {dist}m de qual canto (esquerdo ou direito)?"
        else:
            # If no position is specified, default to centered
            pos_type = "CENTERED"
            dist, corner = None, None

        placement = ObjectPlacement(
            on_wall_id=wall_id,
            position_type=pos_type,
            distance_from_corner=dist,
            corner_reference=corner
        )

        # Generate a block name
        block_name = f"{obj_type_str.lower()}_{int(width*100)}" if width else obj_type_str.lower()
        if obj_type == "POWER_SOCKET":
            block_name = "tomada_dupla"

        return PlannedObject(
            type=obj_type,
            block_name=block_name,
            width=width,
            placement=placement
        )

    def _default_wall_id(self, obj_type: str, room: Room) -> str:
        """Returns a sensible default wall when no wall is specified."""
        w = room.internal_dimensions.width
        l = room.internal_dimensions.length
        if obj_type == "DOOR":
            # Doors default to the longer wall (bottom if w >= l, else right)
            return f"{room.id}_wall_0" if w >= l else f"{room.id}_wall_1"
        elif obj_type == "WINDOW":
            # Windows default to the shorter wall
            return f"{room.id}_wall_1" if w >= l else f"{room.id}_wall_0"
        else:
            # Sockets etc. default to bottom wall
            return f"{room.id}_wall_0"

    def _find_target_wall_id(self, description: str, room: Room) -> str | None:
        """Finds a wall ID based on simple text cues."""
        if not description:
            return None

        desc = description.lower()
        w, l = room.internal_dimensions.width, room.internal_dimensions.length

        # Wall IDs: 0=bottom, 1=right, 2=top, 3=left
        if "parede maior" in desc:
            return f"{room.id}_wall_0" if w >= l else f"{room.id}_wall_1"
        if "parede menor" in desc:
            return f"{room.id}_wall_1" if w > l else f"{room.id}_wall_0"
        if "parede de baixo" in desc or "parede inferior" in desc:
            return f"{room.id}_wall_0"
        if "parede da direita" in desc or "parede direita" in desc:
            return f"{room.id}_wall_1"
        if "parede de cima" in desc or "parede superior" in desc:
            return f"{room.id}_wall_2"
        if "parede da esquerda" in desc or "parede esquerda" in desc:
            return f"{room.id}_wall_3"
        # "parede externa" / "parede de fundo" → treat as bottom wall (front-facing)
        if "parede externa" in desc or "parede de fundo" in desc or "parede frontal" in desc:
            return f"{room.id}_wall_0"

        # Try to match wall by dimension mentioned (e.g., "parede de 6m", "parede de 4 metros")
        dim_match = re.search(r"parede\s+(?:de\s+)?(\d+([,.]\d+)?)\s*(?:m|metros?)", desc)
        if dim_match:
            dim_val = self._str_to_float(dim_match.group(1))
            if abs(dim_val - w) < 0.01:
                return f"{room.id}_wall_0"  # Bottom (width wall)
            elif abs(dim_val - l) < 0.01:
                return f"{room.id}_wall_1"  # Right (length wall)

        return None

    def _str_to_float(self, s: str) -> float:
        """Converts a string with either a '.' or ',' decimal separator to a float."""
        return float(s.replace(",", "."))

    def _extract_dims_from_desc(self, desc: str) -> dict | None:
        """Extracts width and length like '6 por 4', '5x3', or '4,60 m x 3,05 m'."""
        # Regex to find two numbers separated by 'x' or 'por', allowing for decimals with ',' or '.'
        m = re.search(r"(\d+([,.]\d+)?)\s*(?:metros|m)?\s*(?:x|por)\s*(\d+([,.]\d+)?)", desc)
        if m:
            w = self._str_to_float(m.group(1))
            l = self._str_to_float(m.group(3))
            return {"width": w, "length": l}
        return None

    def _extract_size_from_desc(self, desc: str) -> float | None:
        """Extracts size like '80cm', '1.5m', 'de 0.90', etc."""
        # Look for cm
        m_cm = re.search(r"(\d+([,.]\d+)?)\s*cm", desc)
        if m_cm:
            return self._str_to_float(m_cm.group(1)) / 100.0
        
        # Look for meters, can be preceded by "de" or just the number
        m_m = re.search(r"(?:de\s*)?(\d+([,.]\d+)?)\s*m", desc)
        if m_m:
            return self._str_to_float(m_m.group(1))

        return None

    def _extract_distance_from_desc(self, desc: str) -> float | None:
        """Extracts distance like 'a 1m do canto' or 'a 2,5 metros'."""
        m = re.search(r"a (\d+([,.]\d+)?)\s*m", desc)
        return self._str_to_float(m.group(1)) if m else None

# Example usage for testing
if __name__ == '__main__':
    # This simulates the output from the ParserAgent
    sample_raw_input = RawInputSchema(
        project_name="Teste",
        environments=[
            RawEnvironment(
                name="sala",
                description="uma sala de 6 por 4 metros",
                objects=[
                    RawObject(
                        type="porta",
                        description="uma porta de 80cm centralizada na parede maior"
                    ),
                    RawObject(
                        type="janela",
                        description="uma janela de 1.5m a 1 metro do canto esquerdo na parede da direita"
                    )
                ]
            )
        ]
    )
    
    planner = PlannerAgent()
    result = planner.run(sample_raw_input)
    
    if isinstance(result, str):
        print(f"\nQuestion from Planner: {result}")
    else:
        print("\n--- Plan Generated Successfully ---")
        # print(result.model_dump_json(indent=2))
