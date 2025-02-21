import struct
import math
import Tkinter as tk
import tkFileDialog

# Global variables
angle_x = 0
angle_y = 0
angle_z = 0
scale = 50
offset_x = 0
offset_y = 0

last_mouse_x = 0
last_mouse_y = 0

vertices = []
edges = set()

def open_file():
    global vertices, edges
    filename = tkFileDialog.askopenfilename(title="Select STL File", filetypes=[("STL files", "*.stl")])
    vertices, edges = read_stl_binary(filename)

def read_stl_binary(_filename):
    _vertices = []
    _edges = set()

    f = open(_filename, "rb")
    f.seek(80)
    num_triangles = struct.unpack('<I', f.read(4))[0]

    for i in range(num_triangles):
        f.read(12)
        v1 = struct.unpack('<3f', f.read(12))
        v2 = struct.unpack('<3f', f.read(12))
        v3 = struct.unpack('<3f', f.read(12))
        _vertices.extend([v1, v2, v3])

        v1_index = len(_vertices) - 3
        v2_index = len(_vertices) - 2
        v3_index = len(_vertices) - 1

        _edges.add(tuple(sorted([v1_index, v2_index])))
        _edges.add(tuple(sorted([v2_index, v3_index])))
        _edges.add(tuple(sorted([v3_index, v1_index])))

        f.read(2)

    return _vertices, _edges

def reset_pos():
    global angle_x, angle_y, angle_z
    angle_x = angle_z = angle_y = 0

def rotate_point (x, y, z, angle_x, angle_y, angle_z):
    cos_x, sin_x = math.cos(angle_x), math.sin(angle_x)
    y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x

    cos_y, sin_y = math.cos(angle_y), math.sin(angle_y)
    x, z = x * cos_y + z * sin_y, -x * sin_y + z * cos_y

    cos_z, sin_z = math.cos(angle_z), math.sin(angle_z)
    x, y = x * cos_z - y * sin_z, x * sin_z + y * cos_z

    return x, y, z

def on_mouse_press(event):
    global last_mouse_x, last_mouse_y
    last_mouse_x = event.x
    last_mouse_y = event.y

def on_mouse_drag_left(event):
    global angle_x, angle_y, last_mouse_x, last_mouse_y
    dx = event.x - last_mouse_x
    dy = event.y - last_mouse_y
    angle_y -= dx * 0.01
    angle_x += dy * 0.01
    last_mouse_x = event.x
    last_mouse_y = event.y

def on_mouse_drag_right(event):
    global offset_x, offset_y, last_mouse_x, last_mouse_y
    dx = event.x - last_mouse_x
    dy = event.y - last_mouse_y
    offset_x += dx
    offset_y += dy
    last_mouse_x = event.x
    last_mouse_y = event.y    

def on_mouse_wheel(event):
    global scale
    scale += event.delta * 10
    scale = max(10, min(300, scale))

def project (x, y, z):
    global scale, offset_x, offset_y
    factor = scale / (z + 50)
    return x * factor + 200 + offset_x, -y * factor + 200 + offset_y

def update():
    global cube_edge, vertices
    canvas.delete("all")

    projected_vertices = [project(*rotate_point(x, y, z, angle_x, angle_y, angle_z)) for x, y, z in vertices]

    for v1, v2 in edges:
        x1, y1 = projected_vertices[v1]
        x2, y2 = projected_vertices[v2]
        canvas.create_line(x1, y1, x2, y2, fill="green")

    name, vert_count = get_file_data()
    name_text = "File Name:", name
    canvas.create_text(200, 375, text=name_text, fill="green")
    vert_count_text = "Vertices Count:", vert_count
    canvas.create_text(200, 390, text=vert_count_text, fill="green")

    root.after(50, update)

def get_file_data():
    return stl_file, len(vertices)

stl_file = "bulbasaur.stl"
open_file()

root = tk.Tk()
root.title("3D STL Visualizer")

navbar = tk.Frame(root, bg="gray", height=40)
navbar.pack(fill="x", side="top")

open_button = tk.Button(navbar, text="Open", command=open_file)
reset_button = tk.Button(navbar, text="Reset", command=reset_pos)

open_button.pack(side="left", padx=5, pady=5)
reset_button.pack(side="left", padx=5, pady=5)

canvas = tk.Canvas(root, width=400, height=400, bg="black")
canvas.pack()

canvas.bind("<ButtonPress-1>", on_mouse_press)
canvas.bind("<B1-Motion>", on_mouse_drag_left)
canvas.bind("<ButtonPress-3>", on_mouse_press)
canvas.bind("<B3-Motion>", on_mouse_drag_right)
canvas.bind("<MouseWheel>", on_mouse_wheel)

update()
root.mainloop()
