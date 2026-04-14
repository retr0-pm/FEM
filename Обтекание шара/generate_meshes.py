"""
Генерация всех сеток для задачи обтекания шара
Запускать отдельно: python generate_meshes.py
"""

import gmsh
import meshio
import os
import json
import numpy as np
import matplotlib.pyplot as plt

# Параметры
a = 1.0
R_values = [3.0, 5.0, 7.0]
mesh_factors = [1.5, 0.8, 0.4]
levels = ["level1", "level2", "level3"]

MESH_DIR = "meshes"
os.makedirs(MESH_DIR, exist_ok=True)

def create_mesh_for_sphere(a=1.0, R=5.0, mesh_size_factor=1.0, output_file="mesh"):
    """Создание расчетной сетки для обтекания шара"""

    gmsh.initialize()
    gmsh.model.add("sphere_flow")

    base_size = 0.15 * mesh_size_factor

    # Точки
    center = gmsh.model.geo.addPoint(0, 0, 0, base_size)
    p1 = gmsh.model.geo.addPoint(-a, 0, 0, base_size)
    p2 = gmsh.model.geo.addPoint(0, a, 0, base_size)
    p3 = gmsh.model.geo.addPoint(a, 0, 0, base_size)
    p4 = gmsh.model.geo.addPoint(-R, 0, 0, base_size * 3)
    p5 = gmsh.model.geo.addPoint(0, R, 0, base_size * 3)
    p6 = gmsh.model.geo.addPoint(R, 0, 0, base_size * 3)

    # Кривые
    circle1 = gmsh.model.geo.addCircleArc(p1, center, p2)
    circle2 = gmsh.model.geo.addCircleArc(p2, center, p3)
    outer1 = gmsh.model.geo.addCircleArc(p6, center, p5)
    outer2 = gmsh.model.geo.addCircleArc(p5, center, p4)
    sym_left = gmsh.model.geo.addLine(p4, p1)
    sym_right = gmsh.model.geo.addLine(p3, p6)

    # Контур и поверхность
    cl1 = gmsh.model.geo.addCurveLoop([sym_left, circle1, circle2,
                                       sym_right, outer1, outer2])
    surf1 = gmsh.model.geo.addPlaneSurface([cl1])

    gmsh.model.geo.synchronize()

    # Физические группы
    gmsh.model.addPhysicalGroup(1, [circle1, circle2], tag=1)
    gmsh.model.addPhysicalGroup(1, [outer1, outer2], tag=2)
    gmsh.model.addPhysicalGroup(1, [sym_left, sym_right], tag=3)
    gmsh.model.addPhysicalGroup(2, [surf1], tag=4)

    # Генерация сетки
    gmsh.option.setNumber("Mesh.CharacteristicLengthFactor", mesh_size_factor)
    gmsh.model.mesh.generate(2)

    # Сохранение
    msh_file = f"{output_file}.msh"
    gmsh.write(msh_file)

    # Статистика
    node_tags, _, _ = gmsh.model.mesh.getNodes()
    element_types, element_tags, _ = gmsh.model.mesh.getElements()
    num_nodes = len(node_tags)
    num_elements = sum(len(tags) for tags in element_tags)

    gmsh.finalize()

    # Конвертация в XDMF
    mesh = meshio.read(msh_file)
    triangles = None
    for cell_type in mesh.cells_dict:
        if "triangle" in str(cell_type):
            triangles = mesh.cells_dict[cell_type]
            break

    if triangles is not None:
        mesh_only_triangles = meshio.Mesh(
            points=mesh.points[:, :2],
            cells={"triangle": triangles}
        )
        xdmf_file = f"{output_file}.xdmf"
        meshio.write(xdmf_file, mesh_only_triangles)

    os.remove(msh_file)

    return num_nodes, num_elements

def visualize_and_save(mesh_file, a=1.0, R=5.0):
    """Визуализация и сохранение изображения сетки"""
    mesh = meshio.read(mesh_file)
    points = mesh.points[:, :2]

    cells = None
    for cell_type in mesh.cells_dict:
        if "triangle" in str(cell_type):
            cells = mesh.cells_dict[cell_type]
            break

    if cells is None:
        return None

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Полная сетка
    ax1.triplot(points[:, 0], points[:, 1], cells, 'b-', linewidth=0.5, alpha=0.6)
    theta = np.linspace(0, np.pi, 50)
    ax1.plot(a*np.cos(theta), a*np.sin(theta), 'g-', linewidth=2)
    ax1.plot(R*np.cos(theta), R*np.sin(theta), 'k--', linewidth=1, alpha=0.5)
    ax1.set_aspect('equal')
    ax1.set_xlabel('z')
    ax1.set_ylabel('r')
    ax1.set_title(f'Полная область (R={R})')
    ax1.grid(True, alpha=0.3)

    # Увеличенная область
    zoom = min(2.5, R/2)
    mask = (abs(points[:, 0]) <= zoom) & (points[:, 1] <= zoom)
    filtered_cells = [cell for cell in cells if all(mask[idx] for idx in cell)]

    if filtered_cells:
        ax2.triplot(points[:, 0], points[:, 1], filtered_cells, 'b-', linewidth=0.5, alpha=0.6)
    ax2.plot(a*np.cos(theta), a*np.sin(theta), 'g-', linewidth=2)
    ax2.set_aspect('equal')
    ax2.set_xlabel('z')
    ax2.set_ylabel('r')
    ax2.set_title('Увеличенная область')
    ax2.set_xlim([-zoom, zoom])
    ax2.set_ylim([0, zoom])
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    png_file = mesh_file.replace('.xdmf', '.png')
    plt.savefig(png_file, dpi=150, bbox_inches='tight')
    plt.close()

    return png_file

if __name__ == "__main__":
    print("="*60)
    print("ГЕНЕРАЦИЯ СЕТОК ДЛЯ ОБТЕКАНИЯ ШАРА")
    print("="*60)

    stats = []

    for R in R_values:
        print(f"\n{'='*50}")
        print(f"Радиус внешней границы R = {R}")
        print(f"{'='*50}")

        for i, factor in enumerate(mesh_factors):
            level = levels[i]
            print(f"\n  Сетка {level} (фактор {factor})...")

            output_file = f"{MESH_DIR}/mesh_a{a}_R{R}_{level}"

            nodes, elements = create_mesh_for_sphere(a, R, factor, output_file)

            xdmf_file = f"{output_file}.xdmf"
            png_file = visualize_and_save(xdmf_file, a, R)

            stats.append({
                'R': R,
                'level': level,
                'factor': factor,
                'nodes': nodes,
                'elements': elements,
                'xdmf': xdmf_file,
                'png': png_file
            })

            print(f"    Узлов: {nodes}, элементов: {elements}")

    # Сохранение статистики
    stats_file = f"{MESH_DIR}/stats.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    print("\n" + "="*60)
    print("ВСЕ СЕТКИ СГЕНЕРИРОВАНЫ УСПЕШНО!")
    print("="*60)
    print(f"\nСтатистика сохранена в {stats_file}")
    print(f"Всего сеток: {len(stats)}")