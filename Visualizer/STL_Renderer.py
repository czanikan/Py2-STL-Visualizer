import struct
import Tkinter as tk
import math
import tkFileDialog

def read_stl_binary():
    filename = tkFileDialog.askopenfilename(title="Select STL File", filetypes=[("STL files", "*.stl")])
    
    vertices = []
    edges = set()

    f = open(filename, "rb")
    f.seek(80)
    num_triangles = struct.unpack('<I', f.read(4))[0]

    for i in range(num_triangles):
        f.read(12)
        v1 = struct.unpack('<3f', f.read(12))
        v2 = struct.unpack('<3f', f.read(12))
        v3 = struct.unpack('<3f', f.read(12))
        vertices.extend([v1, v2, v3])

        v1_index = len(vertices) - 3
        v2_index = len(vertices) - 2
        v3_index = len(vertices) - 1

        edges.add(tuple(sorted([v1_index, v2_index])))
        edges.add(tuple(sorted([v2_index, v3_index])))
        edges.add(tuple(sorted([v3_index, v1_index])))

        f.read(2)

    return vertices, edges

def rotate_point (x, y, z, angle_x, angle_y, angle_z):
    cos_x, sin_x = math.cos(angle_x), math.sin(angle_x)
    y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x

    cos_y, sin_y = math.cos(angle_y), math.sin(angle_y)
    x, z = x * cos_y + z * sin_y, -x * sin_y + z * cos_y

    cos_z, sin_z = math.cos(angle_z), math.sin(angle_z)
    x, y = x * cos_z - y * sin_z, x * sin_z + y * cos_z

    return x, y, z

def project (x, y, z):
    scale = scale_slider.get()
    distance = distance_slider.get()

    factor = scale / (z + distance)
    return x * factor + 200, -y * factor + 200

def update():
    global angle_x, angle_y, angle_z
    canvas.delete("all")

    projected_vertices = [project(*rotate_point(x, y, z, angle_x, angle_y, angle_z)) for x, y, z in cube_vertices]

    for v1, v2 in cube_edges:
        x1, y1 = projected_vertices[v1]
        x2, y2 = projected_vertices[v2]
        canvas.create_line(x1, y1, x2, y2, fill="green")

    name, vert_count = get_file_data()
    name_text = "File Name:", name
    canvas.create_text(200, 375, text=name_text, fill="green")
    vert_count_text = "Vertices Count:", vert_count
    canvas.create_text(200, 390, text=vert_count_text, fill="green")

    #angle_x += 0.05
    angle_y += 0.03
    #angle_z += 0.02

    root.after(50, update)

def get_file_data():
    return stl_file, len(cube_vertices)

stl_file = "bulbasaur.stl"
cube_vertices, cube_edges = read_stl_binary()

root = tk.Tk()
root.title("3D goes brrr")
canvas = tk.Canvas(root, width=400, height=400, bg="black")
canvas.pack()

scale_slider = tk.Scale(root, from_=50, to=200, orient="horizontal", label="Scale", length=400)
scale_slider.set(100)
scale_slider.pack()

distance_slider = tk.Scale(root, from_=5, to=50, orient="horizontal", label="Distance", length=400)
distance_slider.set(50)
distance_slider.pack()

angle_x = angle_y = angle_z = 0

angle_x = 30

print(cube_vertices[:5])
print(list(cube_edges)[:5])

update()
root.mainloop()