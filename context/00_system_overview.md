# System Overview – Natural Language to CAD Generator

## Objective
Convert natural language specifications into structured CAD drawing (.dxf).

## Architecture

Orchestrator → Parser → Planner → Geometry → Generator → DXF

## Agent Responsibilities

Parser:
- Extract dimensions
- Extract object types
- Extract constraints

Planner:
- Define drawing order
- Define coordinate system
- Define dependencies

Geometry:
- Convert plan into geometric primitives
- Resolve intersections

Generator:
- Translate primitives to DXF entities
