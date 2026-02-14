# CAD Project - Natural Language to DXF Generator

## Project Overview

AI-powered system that converts natural language descriptions (Portuguese) of architectural floor plans into DXF CAD files. Uses a multi-agent pipeline orchestrated sequentially.

## Architecture

```
User Input (PT-BR) → Parser → Planner → Geometry → Generator → output.dxf
```

### Agent Pipeline

1. **Parser** (`src/agents/parser.py`) - Uses Gemini LLM to extract structured data from natural language into `RawInputSchema`
2. **Planner** (`src/agents/planner.py`) - Resolves spatial relationships, creates walls, places objects, returns `StructuredPlanSchema` or asks clarification questions
3. **Geometry** (`src/agents/geometry.py`) - Computes coordinates, wall polygons with mitered corners, object insertion points/rotations into `FinalGeometrySchema`
4. **Generator** (`src/agents/generator.py`) - Writes DXF file using `ezdxf`, loads from template, draws LWPOLYLINE walls and BLOCK_INSERT objects

### Key Files

- `src/main.py` - Entry point, interactive CLI loop
- `src/core/orchestrator.py` - Pipeline orchestration with clarification loop
- `src/schemas/data_models.py` - All Pydantic models (RawInputSchema → StructuredPlanSchema → FinalGeometrySchema)
- `templates/template.dxf` - DXF template with predefined layers and blocks
- `create_template.py` - Script to generate the template DXF

## Tech Stack

- **Language**: Python 3.12
- **LLM**: Google Gemini (gemini-2.5-flash) via `google-generativeai`
- **CAD**: `ezdxf` for DXF file generation
- **Validation**: Pydantic v2 models with field validators
- **Math**: NumPy for geometric calculations
- **Config**: `python-dotenv` for env vars
- **Venv**: `.venv/` directory

## Environment

- Requires `GEMINI_API_KEY` environment variable
- Install: `pip install -r requirements.txt`
- Run: `python src/main.py`
- Input language: Portuguese (PT-BR)

## Data Flow & Schemas

- `RawInputSchema` → Parser output (environments with objects, raw positioning)
- `StructuredPlanSchema` → Planner output (rooms with walls, planned objects with placement)
- `FinalGeometrySchema` → Geometry output (explicit LWPOLYLINE and BLOCK_INSERT primitives)

## CAD Conventions

- Units: meters (internally), DXF at 1:1 scale
- Walls: closed LWPOLYLINE polygons with thickness offset outward from internal dimensions
- Objects: BLOCK_INSERT references (doors, windows, power sockets)
- Wall IDs: `room_{i}_wall_{j}` where j=0(bottom), 1(right), 2(top), 3(left)
- Layers: `AR-PAREDES`, `AR-PORTAS`, `AR-JANELAS`, `EL-TOMADAS`, `AR-COTAS`, `AR-TEXTOS`, `AR-MOBILIARIO`

## Context Documents

Detailed domain knowledge and agent specs live in `context/`:
- `00_system_overview.md` - High-level architecture
- `01_domain_knowledge.md` - CAD fundamentals, object taxonomy, layer semantics
- `02_cad_standards.md` - DXF standards, layer naming, entity rules
- `03_input_schema.md` - Canonical JSON schema after parsing
- `04_parser_agent.md` - Parser responsibilities, unit normalization, ambiguity handling
- `05_planner_agent.md` - Spatial resolution, construction sequencing
- `06_geometry_agent.md` - Coordinate expansion, boolean operations
- `07_generator_agent.md` - DXF file structure, entity mapping
- `08_validation_rules.md` - Multi-stage validation (schema, spatial, geometric, DXF)
- `09_error_handling.md` - Error classification, structured error format
- `10_output_spec.md` - Output contract (file mode + API mode)
- `context/example/` - End-to-end examples (single room, apartment layout)
