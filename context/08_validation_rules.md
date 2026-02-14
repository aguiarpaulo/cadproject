# 08_validation_rules.md
# Validation Rules – Multi-Agent CAD Generation System

---

# 1. PURPOSE

This document defines all validation layers across the system.

Validation must occur at:

1. Post-Parser stage
2. Post-Planner stage
3. Post-Geometry stage
4. Pre-DXF generation stage

The goal is to guarantee:

- Deterministic output
- No corrupted DXF files
- No invalid geometry
- No logical inconsistencies
- Production-level reliability

Validation must be strict and explicit.

---

# 2. VALIDATION LAYERS OVERVIEW

| Stage | Validation Type |
|--------|-----------------|
| Parser | Schema + semantic validation |
| Planner | Spatial + relational validation |
| Geometry | Numeric + topological validation |
| Generator | DXF structural validation |

If any validation fails:
→ Abort pipeline
→ Return structured error
→ Do NOT attempt correction silently

---

# 3. SCHEMA VALIDATION (POST-PARSER)

---

## 3.1 Structural Validation

Must verify:

- project_metadata exists
- global_settings exists
- objects array exists
- Each object has:
  - id
  - type
  - position
  - parameters

No additional unexpected root fields allowed.

---

## 3.2 ID Validation

Rules:

- IDs must be unique
- No empty string
- No whitespace
- No circular parent references

Algorithm:

1. Build ID set
2. Check duplicates
3. Traverse parent tree
4. Detect cycles

If cycle detected:
→ Error: CIRCULAR_REFERENCE

---

## 3.3 Parameter Validation

For each object type:

Room:
- width > 0
- height > 0

Wall:
- length > 0
- thickness > 0

Door:
- width > 0
- swing_angle > 0

Hole:
- diameter > 0

Slot:
- length > width
- end_radius = width / 2 (if not specified)

---

## 3.4 Unit Validation

Must confirm:

- unit == "mm"
- No mixed unit remnants
- All numeric fields are numbers (not strings)

---

# 4. PLANNER VALIDATION

---

## 4.1 Parent Integrity

Door must have wall as parent.
Window must have wall as parent.
Hole must have plate as parent.

If mismatch:
→ INVALID_PARENT_TYPE

---

## 4.2 Spatial Logic Validation

Door width < wall length
Window width < wall length
Hole fully inside plate boundary

Must validate logically even before numeric expansion.

---

## 4.3 Constraint Resolution Check

If object has:

"centered": true

Ensure parent length defined.

If offset_from_edge defined:
Ensure offset < parent length.

---

## 4.4 Boundary Overlap Detection (Logical)

For same parent:

Check overlapping placements.

Example:

Two doors overlapping on same wall.
Two holes intersecting.

If detected:
→ OBJECT_COLLISION

---

# 5. GEOMETRY VALIDATION

This is critical.

---

## 5.1 Numeric Validity

All coordinates must:

- Be finite numbers
- Not NaN
- Not Infinity

---

## 5.2 Degenerate Geometry Detection

Reject:

- Lines where start == end
- Circle radius ≤ 0
- Arc with identical start and end angle
- Polyline with < 3 vertices (if closed)

---

## 5.3 Self-Intersection Detection

Closed polylines must not self-intersect.

Use segment intersection algorithm:

For each segment pair:
Check intersection excluding adjacent edges.

Tolerance:
0.001 mm

---

## 5.4 Wall Corner Integrity

Perpendicular walls must:

- Meet exactly at endpoints
- Not overlap
- Not leave gap > 0.001 mm

---

## 5.5 Boolean Integrity

If subtraction required:

Ensure subtraction area:

- Is fully contained within parent
- Does not remove entire boundary

Example:

Hole diameter > plate width
→ INVALID_BOOLEAN_OPERATION

---

# 6. GLOBAL GEOMETRY VALIDATION

---

## 6.1 Bounding Box Check

Compute global bounding box.

Rules:

- No coordinate > 1,000,000 mm
- No coordinate < -1,000,000 mm

If outside:
→ OUT_OF_RANGE_GEOMETRY

---

## 6.2 Duplicate Primitive Detection

Two identical lines:
→ Remove duplicate OR error (strict mode)

Strict industrial mode:
→ Raise DUPLICATE_ENTITY

---

# 7. DXF STRUCTURAL VALIDATION (PRE-OUTPUT)

---

## 7.1 Required Sections

Must contain:

HEADER
TABLES
ENTITIES

---

## 7.2 Layer Integrity

Every entity must reference existing layer.

If entity references unknown layer:
→ INVALID_LAYER_REFERENCE

---

## 7.3 Group Code Validation

Each entity must include required group codes:

LINE:
10,20,11,21

CIRCLE:
10,20,40

ARC:
10,20,40,50,51

LWPOLYLINE:
90, 10/20 pairs

Missing group code:
→ DXF_STRUCTURE_ERROR

---

## 7.4 File Termination

Last lines must be:

0
ENDSEC
0
EOF

No trailing content allowed.

---

# 8. PERFORMANCE VALIDATION

---

## 8.1 Entity Count Threshold

Default limit:

10,000 entities

If exceeded:
→ ENTITY_LIMIT_EXCEEDED

(Prevents runaway geometry generation)

---

## 8.2 Complexity Guard

If:

Nested hierarchy depth > 10
OR
Total boolean operations > 500

→ SYSTEM_COMPLEXITY_LIMIT

---

# 9. ERROR RESPONSE STANDARD

All errors must follow:

```json
{
  "error": {
    "stage": "Parser | Planner | Geometry | Generator",
    "type": "ERROR_CODE",
    "message": "Human-readable explanation",
    "object_id": "optional"
  }
}
