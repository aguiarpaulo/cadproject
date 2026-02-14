# 04_parser_agent.md
# Parser Agent – Natural Language to Structured Schema

---

# 1. PURPOSE

The Parser Agent converts natural language input into the structured JSON schema defined in:

03_input_schema.md

It must:

- Extract objects
- Extract dimensions
- Normalize units
- Resolve ambiguities when possible
- Produce deterministic structured output
- NEVER generate geometry

Output must strictly follow the schema.

---

# 2. INPUT

User provides natural language description.

Example:

"Create a 4x3 meter bedroom with 15cm thick walls and one 90cm door on the left wall."

---

# 3. OUTPUT

Valid JSON following 03_input_schema.md.

No explanation.
No commentary.
Only structured JSON.

---

# 4. CORE RESPONSIBILITIES

Parser must:

1. Identify project type
2. Identify object types
3. Extract all numeric values
4. Detect units
5. Normalize to millimeters
6. Detect relationships (parent-child)
7. Apply defaults when allowed
8. Flag ambiguity when critical

---

# 5. UNIT NORMALIZATION RULES

## 5.1 Accepted Units

- mm
- millimeters
- cm
- m
- meters
- inches
- in

---

## 5.2 Conversion Rules

1 m = 1000 mm
1 cm = 10 mm
1 inch = 25.4 mm

If no unit specified:
→ Assume millimeters.

If mixed units:
→ Normalize everything to mm.

All numeric outputs must be integers unless precision required.

---

# 6. PROJECT TYPE DETECTION

If text contains:

Room, wall, window, door → architectural
Plate, hole, bolt, diameter → mechanical
Circuit, cable, outlet → electrical

If unclear:
→ Default to architectural.

---

# 7. OBJECT EXTRACTION STRATEGY

## Step 1 – Identify Main Object

Look for:

- Room
- Plate
- Assembly
- Drawing
- Layout

Create top-level object first.

---

## Step 2 – Identify Sub-Objects

Search for:

Doors
Windows
Holes
Slots
Walls

Attach sub-objects using parent_id logic.

---

# 8. DIMENSION EXTRACTION RULES

## 8.1 Formats to Support

4x3 m
4 x 3 meters
4000 by 3000 mm
Width 4000, height 3000
Ø20
Diameter 20 mm
20mm thick

---

## 8.2 Multiplicative Format

If pattern matches:

A x B

Then:

width = first value
height = second value

Unless explicitly reversed.

---

## 8.3 Thickness Detection

Keywords:

thick
thickness
deep
depth (mechanical context)

---

# 9. POSITION INTERPRETATION

Keywords:

left wall
right wall
top wall
bottom wall
centered
middle
100 mm from edge
offset 200 mm

Map to constraints when exact coordinate not provided.

Example:

"centered door"
→ constraints: { "centered": true }

---

# 10. DEFAULT APPLICATION RULES

Defaults allowed only when safe.

Architectural defaults:

- wall thickness → global_settings.default_wall_thickness
- door height → default_door_height
- swing_angle → 90°

Mechanical defaults:

- hole depth → through-hole (if not specified)
- slot end_radius → width / 2

If missing critical dimension:
→ Return structured error.

---

# 11. AMBIGUITY HANDLING

## Critical Ambiguity

Must request clarification if:

- Width and height both missing
- Object size undefined
- Parent object missing

---

## Non-Critical Ambiguity

Can apply default if:

- Door height missing
- Wall thickness missing
- Orientation implied

---

# 12. PARENT-CHILD LOGIC

Rules:

- Doors and windows must belong to a wall.
- Walls may belong to room.
- Holes must belong to plate.

If user describes:

"Room 4x3 with door on left wall"

Parser must:

1. Create room
2. Create walls
3. Attach door to correct wall

---

# 13. WALL AUTO-CREATION LOGIC

If user defines:

Room 4000x3000

Parser must automatically create:

4 walls as child objects

Even if not explicitly stated.

---

# 14. ORIENTATION INFERENCE

If user says:

Door on left wall

Then:

Identify which wall corresponds to left boundary of room.

Planner will compute coordinates later.

Parser only sets:

constraints: { "wall_position": "left" }

---

# 15. NUMBER ROUNDING RULE

After conversion:

Round to nearest integer millimeter.

Unless tolerance explicitly provided.

---

# 16. STRUCTURED ERROR FORMAT

If parsing fails:

```json
{
  "error": {
    "type": "MISSING_DIMENSION",
    "message": "Room width not specified.",
    "field": "width"
  }
}
