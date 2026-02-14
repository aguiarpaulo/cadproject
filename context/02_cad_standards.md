# CAD Standards – Natural Language to DXF Generation System

---

# 1. PURPOSE

This document defines mandatory CAD drafting standards for the automatic generation of DXF files.

It ensures:
- Visual consistency
- Professional technical representation
- Compatibility with AutoCAD and other CAD tools
- Deterministic layer and entity behavior

All agents must comply with this document.

---

# 2. GENERAL DRAWING SETTINGS

## 2.1 Units

Default: Millimeters (mm)

All geometry must be created in Model Space at 1:1 scale.

Never scale geometry to simulate plotting scale.

---

## 2.2 DXF Version

Default output: DXF R2010

Fallback mode (simple compatibility): DXF R12

If R12:
- Avoid SPLINE
- Avoid advanced dimension styles
- Prefer LWPOLYLINE over complex entities

---

# 3. LAYER STANDARDIZATION

All drawings must follow this exact layer naming convention.

Layer names must be uppercase.

---

## 3.1 Mandatory Layers

| Layer Name     | Color | Lineweight | Linetype     | Usage |
|---------------|-------|------------|-------------|-------|
| WALLS         | 7     | 0.50 mm    | Continuous  | Structural walls |
| DOORS         | 3     | 0.25 mm    | Continuous  | Doors |
| WINDOWS       | 4     | 0.25 mm    | Continuous  | Windows |
| STRUCTURE     | 1     | 0.35 mm    | Continuous  | Bea
