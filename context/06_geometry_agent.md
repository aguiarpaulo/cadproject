# 06_geometry_agent.md
# Geometry Agent – Geometric Plan to Primitive Geometry Model

---

# 1. PURPOSE

The Geometry Agent converts the Geometric Plan Model (output of Planner Agent)
into explicit geometric primitives with fully resolved coordinates.

It performs:

- Coordinate expansion
- Wall thickness offsets
- Boolean subtraction logic (logical representation only)
- Arc calculations
- Slot geometry resolution
- Rotation matrix application
- Intersection calculations

It must NOT:

- Write DXF format
- Assign CAD layers
- Add dimension annotations
- Modify semantic hierarchy

Output is a Primitive Geometry Model.

---

# 2. INPUT

Valid Geometric Plan Model.

Assumptions:

- All constraints resolved
- Construction sequence defined
- No logical conflicts
- Units in mm

---

# 3. OUTPUT STRUCTURE

```json
{
  "geometry_metadata": {},
  "primitives": []
}
