# Structured Input Schema – Natural Language to CAD System

---

# 1. PURPOSE

This document defines the canonical structured schema used after the Parser Agent stage.

It represents the normalized, validated, unit-consistent version of user input.

This schema is the ONLY accepted input for the Planner Agent.

All dimensions must already be converted to millimeters.

---

# 2. SCHEMA DESIGN PRINCIPLES

- Deterministic
- Explicit units (always mm)
- Hierarchical
- Extensible
- CAD-compatible
- Machine-validatable (JSON Schema compatible)

---

# 3. ROOT STRUCTURE

```json
{
  "project_metadata": {},
  "global_settings": {},
  "objects": []
}
