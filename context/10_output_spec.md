# 10_output_spec.md
# Output Specification – Natural Language to CAD System

---

# 1. PURPOSE

This document defines the official output contract of the CAD generation system.

It specifies:

- DXF output format
- API response structure
- Metadata packaging
- Error vs Success response model
- Deterministic guarantees
- Versioning strategy

This file represents the public contract of the system.

---

# 2. OUTPUT MODES

The system supports two output modes:

1. File Mode (DXF file only)
2. API Mode (Structured JSON response with embedded file)

---

# 3. SUCCESS RESPONSE (API MODE)

```json
{
  "status": "SUCCESS",
  "output": {
    "file_name": "ARCH_ROOM_4x3_V1.dxf",
    "file_format": "DXF",
    "dxf_version": "R2010",
    "unit": "mm",
    "entity_count": 42,
    "bounding_box": {
      "min_x": 0,
      "min_y": 0,
      "max_x": 4000,
      "max_y": 3000
    },
    "hash": "sha256_file_hash",
    "generated_at": "ISO-8601 UTC timestamp"
  },
  "performance": {
    "parser_ms": 12,
    "planner_ms": 5,
    "geometry_ms": 9,
    "generator_ms": 4,
    "validation_ms": 3,
    "total_ms": 33
  }
}
