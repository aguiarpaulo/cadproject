# Used to create a placeholder template file.
import ezdxf

# Create a new DXF document
doc = ezdxf.new()

# Get the modelspace
msp = doc.modelspace()

# Define some layers as specified in CONTEXT.md
doc.layers.new(name="AR-PAREDES", dxfattribs={"color": 1})
doc.layers.new(name="AR-PORTAS", dxfattribs={"color": 2})
doc.layers.new(name="AR-JANELAS", dxfattribs={"color": 3})
doc.layers.new(name="EL-TOMADAS", dxfattribs={"color": 4})
doc.layers.new(name="AR-COTAS", dxfattribs={"color": 5})
doc.layers.new(name="AR-TEXTOS", dxfattribs={"color": 7})

# Define a simple block for a door
door_block = doc.blocks.new(name="porta_80", base_point=(0, 0))
door_block.add_line((0, 0), (0, 0.8))
door_block.add_line((0, 0.8), (0.05, 0.8))
door_block.add_line((0.05, 0.8), (0.05, 0))
door_block.add_line((0.05, 0), (0, 0))
# Arc to show opening
door_block.add_arc(center=(0,0), radius=0.8, start_angle=0, end_angle=90)

# Door 70cm
door_block_70 = doc.blocks.new(name="porta_70", base_point=(0, 0))
door_block_70.add_line((0, 0), (0, 0.7))
door_block_70.add_line((0, 0.7), (0.05, 0.7))
door_block_70.add_line((0.05, 0.7), (0.05, 0))
door_block_70.add_line((0.05, 0), (0, 0))
door_block_70.add_arc(center=(0,0), radius=0.7, start_angle=0, end_angle=90)

# Door 90cm
door_block_90 = doc.blocks.new(name="porta_90", base_point=(0, 0))
door_block_90.add_line((0, 0), (0, 0.9))
door_block_90.add_line((0, 0.9), (0.05, 0.9))
door_block_90.add_line((0.05, 0.9), (0.05, 0))
door_block_90.add_line((0.05, 0), (0, 0))
door_block_90.add_arc(center=(0,0), radius=0.9, start_angle=0, end_angle=90)


# Define a simple block for a window
window_block = doc.blocks.new(name="janela_150", base_point=(0, 0))
window_block.add_line((0, -0.075), (0, 0.075))
window_block.add_line((1.5, -0.075), (1.5, 0.075))
window_block.add_line((0, 0), (1.5, 0))

# Window 100cm
window_block_100 = doc.blocks.new(name="janela_100", base_point=(0, 0))
window_block_100.add_line((0, -0.075), (0, 0.075))
window_block_100.add_line((1.0, -0.075), (1.0, 0.075))
window_block_100.add_line((0, 0), (1.0, 0))

# Window 200cm
window_block_200 = doc.blocks.new(name="janela_200", base_point=(0, 0))
window_block_200.add_line((0, -0.075), (0, 0.075))
window_block_200.add_line((2.0, -0.075), (2.0, 0.075))
window_block_200.add_line((0, 0), (2.0, 0))


# Define a simple block for a socket
socket_block = doc.blocks.new(name="tomada_dupla", base_point=(0, 0))
socket_block.add_circle((0,0), 0.05)


# Save the DXF file
try:
    doc.saveas("templates/template.dxf")
except FileNotFoundError:
    import os
    os.makedirs("templates", exist_ok=True)
    doc.saveas("templates/template.dxf")

