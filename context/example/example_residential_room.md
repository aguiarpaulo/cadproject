# example_residential_room.md
# End-to-End Example – Residential Room with Door and Window

---

# 1. USER INPUT (Natural Language)

"Create a 4x3 meter bedroom with 15 cm thick walls,
one 90 cm door on the left wall,
and one 120 cm window centered on the top wall."

---

# 2. PARSER OUTPUT (Structured Schema)

{
  "project_metadata": {
    "project_type": "architectural",
    "project_name": "Bedroom_4x3",
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
      "id": "room_1",
      "type": "room",
      "parent_id": null,
      "position": { "x": 0, "y": 0 },
      "rotation": 0,
      "parameters": {
        "width": 4000,
        "height": 3000
      }
    },
    {
      "id": "door_1",
      "type": "door",
      "parent_id": "room_1",
      "position": { "x": 0, "y": 0 },
      "rotation": 0,
      "parameters": {
        "width": 900,
        "height": 2100,
        "swing_direction": "left",
        "swing_angle": 90
      },
      "constraints": {
        "wall_position": "left"
      }
    },
    {
      "id": "window_1",
      "type": "window",
      "parent_id": "room_1",
      "position": { "x": 0, "y": 0 },
      "rotation": 0,
      "parameters": {
        "width": 1200,
        "height": 1000
      },
      "constraints": {
        "wall_position": "top",
        "centered": true
      }
    }
  ]
}

---

# 3. PLANNER OUTPUT (Geometric Plan Model)

## 3.1 Room Expansion

Room 4000 x 3000 mm
Origin: (0,0)

Generated walls:

- wall_bottom_room_1 (length 4000)
- wall_right_room_1 (length 3000)
- wall_top_room_1 (length 4000)
- wall_left_room_1 (length 3000)

Thickness: 150 mm

---

## 3.2 Door Placement

Door belongs to:
wall_left_room_1

Door width: 900 mm

Placement logic:
offset_from_bottom = 100 mm (default margin)
cut_required = true

---

## 3.3 Window Placement

Window belongs to:
wall_top_room_1

Window width: 1200 mm

Centered on wall:

center = 4000 / 2 = 2000 mm
window_start = 2000 - 600 = 1400 mm
window_end = 2600 mm

cut_required = true

---

## 3.4 Construction Sequence

1. room_1
2. wall_bottom_room_1
3. wall_right_room_1
4. wall_top_room_1
5. wall_left_room_1
6. door_1
7. window_1

---

# 4. GEOMETRY OUTPUT (Primitive Model)

## 4.1 Room Boundary

LWPOLYLINE (closed)

Vertices:
(0,0)
(4000,0)
(4000,3000)
(0,3000)

---

## 4.2 Wall Thickness Offset

Thickness = 150 mm
Offset = 75 mm

Walls become rectangular polylines.

Example: Left wall

Centerline:
(0,0) → (0,3000)

After offset:

Outer boundary:
(-75,0)
(-75,3000)

Inner boundary:
(75,0)
(75,3000)

Closed polyline created.

---

## 4.3 Door Geometry

Door cut region:

Left wall axis vertical.
Door opening from y = 100 to y = 1000.

Swing arc:

Hinge point:
(75,100)

Radius = 900

Start angle = 0°
End angle = 90°

Primitive:
ARC

---

## 4.4 Window Geometry

Top wall:
(0,3000) → (4000,3000)

Opening from x = 1400 to 2600.

Opening depth:
Full wall thickness (150 mm)

Internal window lines created inside wall thickness.

---

# 5. DXF OUTPUT (Simplified Snippet)

0
SECTION
2
HEADER
9
$INSUNITS
70
4
0
ENDSEC

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
75
20
100
40
900
50
0
51
90

0
ENDSEC
0
EOF

---

# 6. FINAL OUTPUT METADATA (API Mode)

{
  "status": "SUCCESS",
  "output": {
    "file_name": "ARCH_BEDROOM_4x3_V1.dxf",
    "file_format": "DXF",
    "dxf_version": "R2010",
    "unit": "mm",
    "entity_count": 18,
    "bounding_box": {
      "min_x": -75,
      "min_y": 0,
      "max_x": 4000,
      "max_y": 3000
    },
    "hash": "sha256_generated_hash"
  }
}

---

# 7. VALIDATION CHECKS PASSED

✓ No self-intersection  
✓ No degenerate lines  
✓ Door fully inside wall  
✓ Window fully inside wall  
✓ No overlapping entities  
✓ DXF structure valid  
✓ Deterministic output  

---

# 8. SYSTEM TRACE SUMMARY

Parser: 11 ms  
Planner: 4 ms  
Geometry: 8 ms  
Generator: 3 ms  
Validation: 2 ms  
Total: 28 ms  

---

# END OF END-TO-END EXAMPLE
