# Planner Agent – Structured Schema to Geometric Plan

---

# 1. PURPOSE

The Planner Agent converts validated structured input (03_input_schema.md)
into a deterministic geometric construction plan.

It must:

- Resolve hierarchy
- Resolve spatial relationships
- Compute relative positioning logic
- Determine drawing order
- Convert constraints into explicit spatial instructions

It must NOT:

- Generate DXF
- Generate primitive entities (LINE, ARC, etc.)
- Apply CAD layer formatting

Output is an intermediate "Geometric Plan Model".

---

# 2. INPUT

Valid JSON from Parser Agent.

Assumptions:
- All units normalized to mm
- Schema validated
- No missing mandatory parameters

---

# 3. OUTPUT STRUCTURE

```json
{
  "plan_metadata": {},
  "construction_sequence": [],
  "resolved_objects": []
}
