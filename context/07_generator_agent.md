# 07_generator_agent.md
# Generator Agent – Primitive Geometry to DXF File

---

# 1. PURPOSE

The Generator Agent converts the Primitive Geometry Model
(output of Geometry Agent) into a valid DXF file.

It must:

- Write valid DXF structure
- Map primitives to DXF entities
- Assign layers according to 02_cad_standards.md
- Respect DXF version rules
- Produce syntactically correct output

It must NOT:

- Modify geometry
- Perform geometric calculations
- Reinterpret semantics
- Add extra objects

---

# 2. INPUT

Valid Primitive Geometry Model.

Assumptions:

- All coordinates resolved
- All boolean operations already processed or flagged
- No geometry conflicts
- Units in mm

---

# 3. OUTPUT

Plain text DXF file.

Must end with:

0
EOF

No commentary.
No explanation.
Only DXF content.

---

# 4. DXF FILE STRUCTURE (R2010)

Minimal structure:

0
SECTION
2
HEADER
0
ENDSEC

0
SECTION
2
TABLES
...
0
ENDSEC

0
SECTION
2
ENTITIES
...
0
ENDSEC

0
EOF

---

# 5. HEADER CONFIGURATION

Must define units:

9
$INSUNITS
70
4

(4 = millimeters)

---

# 6. LAYER TABLE GENERATION

For each layer defined in 02_cad_standards.md,
Generator must write:

0
LAYER
2
LayerName
70
0
62
ColorIndex
6
Continuous

All mandatory layers must exist,
even if unused.

---

# 7. ENTITY MAPPING

---

## 7.1 LINE

Primitive:

```json
{
  "type": "LINE",
  "coordinates": {
    "start": {"x": x1, "y": y1},
    "end": {"x": x2, "y": y2}
  }
}
