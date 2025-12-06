# Agent responsible for geometric calculations
import math
import numpy as np
from typing import List, Tuple
from src.schemas.data_models import (
    StructuredPlanSchema,
    FinalGeometrySchema,
    Geometry,
    LWPolylineParams,
    BlockInsertParams,
    Room,
    PlannedObject,
    Wall,
)

class GeometryAgent:
    """
    Takes a structured and validated plan and converts it into a set of
    explicit geometric data (coordinates, layers, etc.) ready for DXF generation.
    """

    def run(self, plan: StructuredPlanSchema) -> FinalGeometrySchema:
        """
        Processes the structured plan to generate final geometric data.
        The origin (0,0) is the internal corner of the first room.
        """
        print("--- Running Geometry Agent ---")
        geometries: List[Geometry] = []
        
        # Create geometries for all rooms and their walls
        for room in plan.rooms:
            geometries.extend(self._create_room_geometry(room))

        # Create geometries for all objects (doors, windows, etc.)
        # A map is used for efficient wall lookups
        wall_map = {wall.id: wall for room in plan.rooms for wall in room.walls}
        for obj in plan.objects:
            wall = wall_map.get(obj.placement.on_wall_id)
            if wall:
                geometries.append(self._create_object_geometry(obj, wall))

        final_schema = FinalGeometrySchema(
            drawing_units=plan.drawing_settings.units,
            geometries=geometries
        )
        print(f"Generated {len(geometries)} geometric entities.")
        return final_schema

    def _create_room_geometry(self, room: Room) -> List[Geometry]:
        """Creates the LWPOLYLINE geometries for the walls of a single room."""
        # For a rectangular room, walls are drawn as thick polygons.
        # The room's dimensions are internal, so walls are drawn outwards.
        return [
            Geometry(type="LWPOLYLINE", layer="AR-PAREDES", params=LWPolylineParams(points=wall['points'], is_closed=True))
            for wall in self._get_rectangular_wall_polygons(room)
        ]

    def _get_rectangular_wall_polygons(self, room: Room) -> List[dict]:
        """
        Calculates the four polygons for a rectangular room's walls with mitered corners.
        """
        w = room.internal_dimensions.width
        l = room.internal_dimensions.length
        t = room.walls[0].thickness # Assume uniform thickness
        ox, oy = room.origin_point

        # Define internal corners
        c_bl = (ox, oy)          # Internal Bottom-Left
        c_br = (ox + w, oy)      # Internal Bottom-Right
        c_tr = (ox + w, oy + l)  # Internal Top-Right
        c_tl = (ox, oy + l)      # Internal Top-Left

        # Define external corners (mitered)
        e_bl = (ox - t, oy - t)  # External Bottom-Left
        e_br = (ox + w + t, oy - t)  # External Bottom-Right
        e_tr = (ox + w + t, oy + l + t)  # External Top-Right
        e_tl = (ox - t, oy + l + t)  # External Top-Left

        # Create closed polygons for each wall
        walls = [
            # Bottom Wall
            {'points': [c_bl, c_br, e_br, e_bl]},
            # Right Wall
            {'points': [c_br, c_tr, e_tr, e_br]},
            # Top Wall
            {'points': [c_tr, c_tl, e_tl, e_tr]},
            # Left Wall
            {'points': [c_tl, c_bl, e_bl, e_tl]},
        ]
        return walls

    def _create_object_geometry(self, obj: PlannedObject, wall: Wall) -> Geometry:
        """Calculates the insertion point and rotation for an object on a wall."""
        
        wall_start = np.array(wall.start)
        wall_end = np.array(wall.end)
        wall_vector = wall_end - wall_start
        wall_length = np.linalg.norm(wall_vector)
        wall_direction = wall_vector / wall_length if wall_length > 0 else np.array([0, 0])

        # --- Calculate Insertion Point ---
        if obj.placement.position_type == "CENTERED":
            # Place at the midpoint of the wall
            insertion_point = wall_start + wall_direction * (wall_length / 2)
        
        elif obj.placement.position_type == "FROM_CORNER":
            distance = obj.placement.distance_from_corner
            if obj.placement.corner_reference == "START":
                insertion_point = wall_start + wall_direction * distance
            else: # END
                insertion_point = wall_end - wall_direction * distance
        
        else: # Fallback
            insertion_point = wall_start

        # --- Calculate Rotation ---
        # Angle of the wall vector in radians, converted to degrees
        rotation_deg = math.degrees(math.atan2(wall_direction[1], wall_direction[0]))

        # --- Determine Layer ---
        layer_map = {
            "DOOR": "AR-PORTAS",
            "WINDOW": "AR-JANELAS",
            "POWER_SOCKET": "EL-TOMADAS",
        }
        layer = layer_map.get(obj.type, "AR-TEXTOS") # Default layer

        # Adjust rotation for specific objects like power sockets on vertical walls
        if obj.type == "POWER_SOCKET":
            # Vertical walls will have rotation 90 or -90 (270)
            if abs(abs(rotation_deg) - 90) < 1:
                rotation_deg = 0
            elif abs(abs(rotation_deg) - 180) < 1: # top wall
                 rotation_deg = 180
            else: # bottom wall
                rotation_deg = 0


        params = BlockInsertParams(
            block_name=obj.block_name,
            insertion_point=tuple(insertion_point),
            rotation=rotation_deg,
        )
        print(f"Placing '{obj.block_name}' on wall '{wall.id}' at {params.insertion_point} with {params.rotation}° rotation.")
        
        return Geometry(type="BLOCK_INSERT", layer=layer, params=params)
