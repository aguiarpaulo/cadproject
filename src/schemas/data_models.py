# Pydantic models for data validation and structure.
# Based on the schemas defined in DATA_MODEL.md

from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import List, Optional, Literal, Dict, Any, Tuple, Union

# --- RawInputSchema ---
# Captures the user's request in a semi-structured way.

class RawPositioning(BaseModel):
    """Raw positioning information extracted by the parser."""
    on_wall: Optional[str] = Field(None, description="The wall or walls the object is on (e.g., 'parede maior').")
    centered: Optional[bool] = Field(None, description="Whether the object is centered on the wall.")
    distance: Optional[float] = Field(None, description="Distance from a reference point.")
    from_: Optional[str] = Field(None, alias="from", description="The reference point (e.g., 'canto esquerdo').")

class RawObject(BaseModel):
    """A raw object description extracted from the user prompt."""
    type: Optional[str] = Field(None, description="Type of the object (e.g., 'porta', 'janela', 'tomada').")
    description: str = Field(..., description="Full description of the object (e.g., 'uma porta de 80cm a 1m do canto').")
    quantity: Optional[int] = Field(1, description="Number of identical objects.")
    width: Optional[float] = Field(None, description="Width of the object.")
    height: Optional[float] = Field(None, description="Height of the object.")
    positioning: Optional[RawPositioning] = Field(None, description="Positioning details for the object.")

class RawEnvironment(BaseModel):
    """A raw environment description extracted from the user prompt."""
    name: Optional[str] = Field(None, description="Name of the environment (e.g., 'sala', 'cozinha').")
    description: str = Field(..., description="Full description of the environment (e.g., 'uma sala de 5 por 4 metros').")
    objects: List[RawObject] = []

class RawSettings(BaseModel):
    """Raw settings mentioned by the user."""
    units: Optional[str] = Field(None, description="Main measurement unit mentioned (e.g., 'metros', 'cm').")

class RawInputSchema(BaseModel):
    """The overall semi-structured output from the Parser Agent."""
    project_name: Optional[str] = Field(None, description="Suggested project name.")
    settings: Optional[RawSettings] = None
    environments: List[RawEnvironment] = []


# --- StructuredPlanSchema ---
# Represents a validated, unambiguous plan for the drawing.

class DrawingSettings(BaseModel):
    """Global settings for the drawing."""
    units: Literal["meters", "centimeters", "millimeters"] = "meters"
    default_wall_thickness: float = 0.15

class RoomDimensions(BaseModel):
    """Internal dimensions of a room."""
    width: float
    length: float

class Wall(BaseModel):
    """Represents a single wall of a room."""
    id: str = Field(..., description="Unique ID for the wall, e.g., 'room_0_wall_0'.")
    room_id: str = Field(..., description="ID of the room this wall belongs to.")
    start: Tuple[float, float] = Field(..., description="[x, y] coordinates of the wall's start point (internal face).")
    end: Tuple[float, float] = Field(..., description="[x, y] coordinates of the wall's end point (internal face).")
    thickness: float
    length: float

class Room(BaseModel):
    """A single room in the drawing plan."""
    id: str = Field(..., description="Unique ID for the room, e.g., 'room_0'.")
    shape: Literal["rectangle"] = "rectangle"
    internal_dimensions: RoomDimensions
    origin_point: Tuple[float, float] = Field(..., description="[x, y] of the bottom-left internal corner.")
    walls: List[Wall] = Field([], description="List of walls defining the room, populated by the planner.")

class ObjectPlacement(BaseModel):
    """Defines where an object is to be placed."""
    on_wall_id: str = Field(..., description="ID of the wall (e.g., 'room_0_wall_3').")
    position_type: Literal["CENTERED", "FROM_CORNER"]
    distance_from_corner: Optional[float] = Field(None, description="Distance from the object's center to the corner.")
    corner_reference: Optional[Literal["START", "END"]] = Field(None, description="Reference corner of the wall (start or end vertex).")

    @field_validator('distance_from_corner', 'corner_reference')
    def check_from_corner_placement(cls, v: Optional[float], info: ValidationInfo) -> Optional[float]:
        if info.data.get('position_type') == 'FROM_CORNER' and v is None:
            raise ValueError(f"'{info.field_name}' must be provided when position_type is 'FROM_CORNER'")
        return v

class PlannedObject(BaseModel):
    """An object to be inserted into the drawing."""
    type: Literal["DOOR", "WINDOW", "POWER_SOCKET"]
    block_name: str = Field(..., description="Name of the block to be used in DXF.")
    width: float
    height: Optional[float] = None
    placement: ObjectPlacement

class StructuredPlanSchema(BaseModel):
    """The complete, validated plan from the Planner Agent."""
    drawing_settings: DrawingSettings
    rooms: List[Room]
    objects: List[PlannedObject] = []


# --- FinalGeometrySchema ---
# Contains explicit geometric data ready for DXF generation.

class GeometryParams(BaseModel):
    """Base model for geometry parameters."""
    pass

class LWPolylineParams(GeometryParams):
    """Parameters for an LWPOLYLINE entity."""
    points: List[Tuple[float, float]]
    is_closed: bool = True

class BlockInsertParams(GeometryParams):
    """Parameters for a BLOCK_INSERT entity."""
    block_name: str
    insertion_point: Tuple[float, float]
    rotation: float = 0
    scale: Dict[str, float] = Field(default_factory=lambda: {"x": 1.0, "y": 1.0, "z": 1.0})

class LinearDimParams(GeometryParams):
    """Parameters for a LINEAR_DIMENSION entity."""
    p1: Tuple[float, float]
    p2: Tuple[float, float]
    location: Tuple[float, float]
    angle: float = 0

class Geometry(BaseModel):
    """A single geometric entity to be drawn."""
    type: Literal["LWPOLYLINE", "BLOCK_INSERT", "LINEAR_DIM"]
    layer: str
    params: Union[LWPolylineParams, BlockInsertParams, LinearDimParams]

class FinalGeometrySchema(BaseModel):
    """The final, detailed geometry data for the DXF Generator."""
    drawing_units: str
    geometries: List[Geometry]
