# example_residential_apartment.md
# End-to-End Example – Residential Apartment Layout

---

# 1. USER INPUT (Natural Language)

"Create a small apartment with:

- Living room 4x3 meters
- Bedroom 3x3 meters
- Bathroom 2x1.5 meters

Walls 15 cm thick.
Each room must have one 80 cm door.
Bathroom door should open inward.
Add one 1.2 meter window centered in the living room external wall."

---

# 2. PARSER OUTPUT (Structured Schema)

{
  "project_metadata": {
    "project_type": "architectural",
    "project_name": "Apartment_Small",
    "version": "1.0.0",
    "author": "Parser_Agent",
    "timestamp": "AUTO_GENERATED"
  },
  "global_settings": {
    "unit": "mm",
    "origin": { "x": 0, "y": 0 },
    "default_wall_thickness": 150,
    "default_door_height": 2100
  },
  "objects": [
    {
      "id": "living_room",
      "type": "room",
      "parent_id": null,
      "position": { "x": 0, "y": 0 },
      "rotation": 0,
      "parameters": { "width": 4000, "height": 3000 }
    },
    {
      "id": "bedroom",
      "type": "room",
      "parent_id": null,
      "position": { "x": 4000, "y": 0 },
      "rotation": 0,
      "parameters": { "width": 3000, "height": 3000 }
    },
    {
      "id": "bathroom",
      "type": "room",
      "parent_id": null,
      "position": { "x": 0, "y": 3000 },
      "rotation": 0,
      "parameters": { "width": 2000, "height": 1500 }
    }
  ]
}

(Note: Doors and window defined separately below.)

---

# 3. PLANNER OUTPUT (Geometric Plan Model)

---

# 3.1 Global Layout Logic

Apartment organized as:

Top View:

Bathroom above living room.
Bedroom to the right of living room.

Coordinates:

Living room: (0,0) to (4000,3000)
Bedroom: (4000,0) to (7000,3000)
Bathroom: (0,3000) to (2000,4500)

---

# 3.2 Wall Expansion

Each room expanded into 4 walls.

Total walls generated: 12
(Shared walls optionally merged in advanced mode.)

Thickness: 150 mm

---

# 3.3 Door Placement

Each room receives:

Door width: 800 mm

Placement rules:

Living room:
Door on right wall, centered.

Bedroom:
Door on left wall, centered.

Bathroom:
Door on bottom wall,
Swing direction inward.

Planner marks:
requires_boolean_operation = true

---

# 3.4 Window Placement

Living room external wall:

External wall identified as bottom wall.

Window width: 1200 mm
Centered.

Opening range:
4000 / 2 = 2000 mm center
Start = 1400 mm
End = 2600 mm

---

# 3.5 Construction Sequence

1. living_room
2. bedroom
3. bathroom
4. All walls
5. Doors
6. Window

---

# 4. GEOMETRY OUTPUT (Primitive Summary)

---

# 4.1 Room Boundaries

Living room:

(0,0)
(4000,0)
(4000,3000)
(0,3000)

Bedroom:

(4000,0)
(7000,0)
(7000,3000)
(4000,3000)

Bathroom:

(0,3000)
(2000,3000)
(2000,4500)
(0,4500)

All closed LWPOLYLINE.

---

# 4.2 Door Geometry Example (Bedroom)

Wall axis vertical at x=4000.

Door center:
y = 1500

Door cut:
from 1100 to 1900.

Swing arc:
radius = 800
start_angle = 180°
end_angle = 270°

---

# 4.3 Window Geometry

Bottom living room wall:
y = 0

Window opening:
x = 1400 → 2600

Subtraction region:
Depth = 150 mm

---

# 5. DXF SNIPPET (Simplified)

0
SECTION
2
ENTITIES

0
LWPOLYLINE
8
WALLS
90
4
70
1
10
0
20
0
10
4000
20
0
10
4000
20
3000
10
0
20
3000

0
ARC
8
DOORS
10
4000
20
1100
40
800
50
180
51
270

0
ENDSEC
0
EOF

---

# 6. FINAL OUTPUT METADATA

{
  "status": "SUCCESS",
  "output": {
    "file_name": "ARCH_APARTMENT_SMALL_V1.dxf",
    "file_format": "DXF",
    "dxf_version": "R2010",
    "unit": "mm",
    "entity_count": 46,
    "bounding_box": {
      "min_x": -75,
      "min_y": 0,
      "max_x": 7000,
      "max_y": 4500
    },
    "hash": "sha256_generated_hash"
  }
}

---

# 7. VALIDATION CHECKS

✓ No overlapping rooms  
✓ All doors inside walls  
✓ Bathroom door inward swing validated  
✓ Window inside boundary  
✓ No self-intersecting walls  
✓ No degenerate primitives  
✓ DXF structurally valid  

---

# 8. PERFORMANCE TRACE

Parser: 18 ms  
Planner: 9 ms  
Geometry: 14 ms  
Generator: 6 ms  
Validation: 5 ms  
Total: 52 ms  

---

# 9. COMPLEXITY LEVEL

Compared to single-room example:

- Multi-room adjacency
- Door direction handling
- External wall detection
- Increased boolean operations
- Expanded bounding box validation

This represents a production-level residential layout test.

---

# END OF EXAMPLE
