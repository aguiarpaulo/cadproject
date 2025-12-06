# Agent responsible for generating the DXF file
import ezdxf
from ezdxf.document import Drawing
from ezdxf.layouts import Modelspace
from ezdxf import DXFError
from src.schemas.data_models import (
    FinalGeometrySchema,
    Geometry,
    LWPolylineParams,
    BlockInsertParams,
)

class DXFGeneratorAgent:
    """
    Takes the final, explicit geometric data and writes it to a DXF file,
    leveraging a predefined template.
    """

    def run(
        self,
        geometry_schema: FinalGeometrySchema,
        template_path: str,
        output_path: str,
    ) -> None:
        """
        Generates the DXF file by loading a template, drawing geometries,
        and saving the final result.

        Args:
            geometry_schema: The schema containing all geometric data.
            template_path: Path to the DXF template file.
            output_path: Path to save the generated DXF file.
        """
        print("--- Running DXF Generator Agent ---")
        try:
            # Load the template. A template is required.
            doc = ezdxf.readfile(template_path)
            msp = doc.modelspace()
            print(f"Loaded template: '{template_path}'")

        except (IOError, FileNotFoundError, DXFError) as e:
            print(f"[DXF Generation Error] Could not read template file: {e}")
            # As a fallback, create a new document
            print("Creating a new DXF document as a fallback.")
            doc = ezdxf.new()
            msp = doc.modelspace()
            self._create_default_layers(doc)

        try:
            # Process and draw each geometry defined in the schema
            for geom in geometry_schema.geometries:
                self._draw_geometry(msp, geom)

            # Save the final file
            doc.saveas(output_path)
            print(f"Successfully generated DXF file: {output_path}")

        except DXFError as e:
            print(f"[DXF Generation Error] An error occurred during file writing: {e}")
            raise
        except Exception as e:
            print(f"[DXF Generation Error] An unexpected error occurred: {e}")
            raise

    def _draw_geometry(self, msp: Modelspace, geom: Geometry) -> None:
        """
        Dispatches the drawing command based on the geometry's type.

        Args:
            msp: The modelspace of the DXF document.
            geom: The geometry object to draw.
        """
        params = geom.params
        dxfattribs = {"layer": geom.layer}

        if isinstance(params, LWPolylineParams):
            msp.add_lwpolyline(
                points=params.points,
                close=params.is_closed,
                dxfattribs=dxfattribs,
            )
            print(f"Drew LWPOLYLINE on layer '{geom.layer}' with {len(params.points)} points.")
        
        elif isinstance(params, BlockInsertParams):
            msp.add_blockref(
                name=params.block_name,
                insert=params.insertion_point,
                dxfattribs={
                    **dxfattribs,
                    "rotation": params.rotation,
                    "xscale": params.scale.get("x", 1.0),
                    "yscale": params.scale.get("y", 1.0),
                    "zscale": params.scale.get("z", 1.0),
                },
            )
            print(f"Inserted block '{params.block_name}' on layer '{geom.layer}'.")

        # Add other geometry types like LINEAR_DIM here in the future

    def _create_default_layers(self, doc: Drawing) -> None:
        """
        Creates a default set of layers if no template is provided or fails to load.
        This is based on the layers defined in CONTEXT.md.
        """
        print("Creating default layers as no template was used.")
        layers = {
            "AR-PAREDES": {"color": 1},    # Red
            "AR-PORTAS": {"color": 2},     # Yellow
            "AR-JANELAS": {"color": 3},    # Green
            "EL-TOMADAS": {"color": 4},    # Cyan
            "AR-COTAS": {"color": 5},      # Blue
            "AR-TEXTOS": {"color": 7},     # White/Black
            "AR-MOBILIARIO": {"color": 8}, # Grey
        }
        for name, attribs in layers.items():
            if name not in doc.layers:
                doc.layers.new(name, dxfattribs=attribs)
