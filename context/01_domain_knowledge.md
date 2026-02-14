# 01_domain_knowledge.md
# Domain Knowledge – CAD Project Generation System

---

# 1. PURPOSE

This document defines the technical domain knowledge required for generating CAD drawings from structured data.

It contains:
- Technical drawing fundamentals
- Coordinate systems
- Units and scale conventions
- CAD object taxonomy
- Architectural and mechanical standards
- Constraints and geometric logic
- Layer semantics
- Hierarchical modeling concepts

This file is the foundational technical reference for all agents.

---

# 2. DRAWING TYPES SUPPORTED

## 2.1 Architectural
- Floor plans
- Elevations
- Sections
- Site plans

## 2.2 Mechanical
- 2D part drawings
- Assembly drawings
- Technical detail drawings

## 2.3 Electrical (Basic)
- Layout diagrams
- Symbol placement
- Conduit paths

---

# 3. COORDINATE SYSTEMS

## 3.1 Cartesian Coordinate System

All geometry must use Cartesian coordinates:

- X-axis → Horizontal
- Y-axis → Vertical
- Z-axis → Depth (optional for 2D system)

Default origin:
(0,0) at bottom-left of drawing area.

All objects must be positioned relative to either:
- Global origin
- Parent object origin

---

# 4. UNITS AND SCALE

## 4.1 Default Unit

Millimeters (mm)

If no unit is specified:
→ Assume millimeters.

## 4.2 Accepted Units

- mm
- cm
- m
- inches

All units must be normalized to millimeters before geometry generation.

## 4.3 Scale

Model Space must always be 1:1.

Plot scaling is external and must not affect geometry coordinates.

---

# 5. CAD OBJECT TAXONOMY

## 5.1 Primitive Geometry

These are the atomic elements:

- LINE
- POLYLINE
- LWPOLYLINE
- ARC
- CIRCLE
- SPLINE
- TEXT
- HATCH

All complex objects must resolve into primitives.

---

## 5.2 Composite Objects (Architectural)

### Wall
- Represented as offset polyline
- Has thickness
- Has start and end coordinates

### Door
- Opening in wall
- Represented by arc + lines
- Must subtract wall geometry

### Window
- Opening in wall
- Represented by thin parallel lines
- Centered in wall thickness

### Room
- Closed polyline
- Must be geometrically valid (no open edges)

---

## 5.3 Composite Objects (Mechanical)

### Plate
- Closed polyline
- Optional holes

### Hole
- Circle entity
- Must be fully contained inside parent object

### Slot
- Two arcs + two lines
- Must have fillet radius

---

# 6. GEOMETRIC CONSTRAINTS

## 6.1 Valid Geometry Rules

- No negative dimensions
- No self-intersecting polylines
- All rooms must be closed
- All holes must be inside boundary

## 6.2 Orthogonality

For architectural drawings:
- Default angle: 0° or 90°
- Diagonal walls must be explicitly requested

## 6.3 Wall Thickness Logic

Wall thickness must:
- Offset equally from centerline
OR
- Be offset internally (defined by planner)

---

# 7. LAYER SEMANTICS

Layers define logical separation of objects.

## Standard Layers

WALLS
DOORS
WINDOWS
STRUCTURE
DIMENSIONS
TEXT
CENTERLINES
HATCH

Each object must belong to exactly one primary layer.

---

# 8. DIMENSIONS AND ANNOTATIONS

## 8.1 Dimension Types

- Linear
- Aligned
- Radial
- Angular

Dimensions must:
- Reference geometric entities
- Not intersect with geometry
- Be placed outside object boundary

---

# 9. DRAWING ORDER LOGIC

Rendering priority:

1. Structural elements
2. Openings
3. Details
4. Hatches
5. Dimensions
6. Text

---

# 10. HIERARCHICAL MODELING

Objects may contain sub-objects.

Example:

Room
 ├── Wall
 ├── Door
 ├── Window

Parent object defines coordinate reference.

Child object coordinates must be local to parent unless specified otherwise.

---

# 11. STANDARD CONVENTIONS (ARCHITECTURAL)

## Wall Representation


::contentReference[oaicite:0]{index=0}


- Walls are represented by two parall
