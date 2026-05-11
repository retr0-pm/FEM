import gmsh
import sys
import os
import json
import meshio
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Пути
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MESH_DIR = os.path.join(PROJECT_DIR, "meshes")
os.makedirs(MESH_DIR, exist_ok=True)

gmsh.initialize()
gmsh.model.add("channel_with_step")

# ПАРАМЕТРЫ ГЕОМЕТРИИ
L = 4.0   # длина канала
H = 1.0   # высота канала
l = 1.0   # длина уступа
h = 1.0   # высота уступа

# Базовые размеры
lc_base = 0.6          # характерный размер элемента
size_min_base = 0.1   # минимальный размер вблизи уступа
dist_min_base = 0.1    # расстояние начала убывания размера
dist_max_base = 0.5    # расстояние полного перехода к SizeMax

# ГЕОМЕТРИЯ
p1 = gmsh.model.geo.addPoint(0, 0, 0, lc_base)
p2 = gmsh.model.geo.addPoint(l, 0, 0, lc_base)
p3 = gmsh.model.geo.addPoint(l, -h, 0, lc_base)
p4 = gmsh.model.geo.addPoint(L, -h, 0, lc_base)
p5 = gmsh.model.geo.addPoint(L, H, 0, lc_base)
p6 = gmsh.model.geo.addPoint(0, H, 0, lc_base)

l1 = gmsh.model.geo.addLine(p1, p2)   # нижняя стенка (часть до уступа)
l2 = gmsh.model.geo.addLine(p2, p3)   # вертикаль уступа
l3 = gmsh.model.geo.addLine(p3, p4)   # нижняя стенка (часть после уступа)
l4 = gmsh.model.geo.addLine(p4, p5)   # выход (Gamma4)
l5 = gmsh.model.geo.addLine(p5, p6)   # верхняя стенка (Gamma2)
l6 = gmsh.model.geo.addLine(p6, p1)   # вход (Gamma3)

curve_loop = gmsh.model.geo.addCurveLoop([l1, l2, l3, l4, l5, l6])
surface = gmsh.model.geo.addPlaneSurface([curve_loop])

gmsh.model.geo.synchronize()


# ФИЗИЧЕСКИЕ ГРУППЫ
gmsh.model.addPhysicalGroup(1, [l1, l2, l3], tag=1)
gmsh.model.setPhysicalName(1, 1, "Gamma1")

gmsh.model.addPhysicalGroup(1, [l5], tag=2)
gmsh.model.setPhysicalName(1, 2, "Gamma2")

gmsh.model.addPhysicalGroup(1, [l6], tag=3)
gmsh.model.setPhysicalName(1, 3, "Gamma3")

gmsh.model.addPhysicalGroup(1, [l4], tag=4)
gmsh.model.setPhysicalName(1, 4, "Gamma4")

gmsh.model.addPhysicalGroup(2, [surface], tag=5)
gmsh.model.setPhysicalName(2, 5, "Omega")

# ПОСЛЕДОВАТЕЛЬНАЯ ГЕНЕРАЦИЯ ТРЁХ СЕТОК
scales = [1.0, 0.25, 0.0625]
stats = []

for i, scale in enumerate(scales):
    level = f"level{i+1}"
    print(f"\n=== Сетка {level}: коэффициент масштаба = {scale} ===")

    # Очищаем предыдущую сетку и поля
    gmsh.model.mesh.clear()
    for fid in gmsh.model.mesh.field.list():
        gmsh.model.mesh.field.remove(fid)

    # Масштабируем все размеры
    lc_curr = lc_base * scale
    size_min = size_min_base * scale
    dist_min = dist_min_base * scale
    dist_max = dist_max_base * scale

    # Поле расстояния до стенок уступа (вертикальной и горизонтальной)
    distance_field = gmsh.model.mesh.field.add("Distance")
    gmsh.model.mesh.field.setNumbers(distance_field, "EdgesList", [l2, l3])

    # Пороговое поле, задающее размер от size_min до lc_curr
    threshold_field = gmsh.model.mesh.field.add("Threshold")
    gmsh.model.mesh.field.setNumber(threshold_field, "InField", distance_field)
    gmsh.model.mesh.field.setNumber(threshold_field, "SizeMin", size_min)
    gmsh.model.mesh.field.setNumber(threshold_field, "SizeMax", lc_curr)
    gmsh.model.mesh.field.setNumber(threshold_field, "DistMin", dist_min)
    gmsh.model.mesh.field.setNumber(threshold_field, "DistMax", dist_max)

    gmsh.model.mesh.field.setAsBackgroundMesh(threshold_field)

    # Генерация 2D сетки
    gmsh.model.mesh.generate(2)

    # Сохранение .msh
    msh_path = os.path.join(MESH_DIR, f"channel_step_mesh_{level}.msh")
    gmsh.write(msh_path)
    print(f"Сетка сохранена в {msh_path}")

    # === СТАТИСТИКА И ВИЗУАЛИЗАЦИЯ (добавлено для Streamlit) ===

    # Читаем сетку через meshio
    mesh = meshio.read(msh_path)
    points = mesh.points[:, :2]
    triangles = mesh.cells_dict["triangle"]
    lines = mesh.cells_dict["line"]
    line_data = mesh.cell_data_dict["gmsh:physical"]["line"]

    # Количество узлов и элементов
    nodes = points.shape[0]
    elements = triangles.shape[0]

    # Рисуем сетку с цветными границами
    x = points[:, 0]
    y = points[:, 1]

    fig, ax = plt.subplots(figsize=(10, 4))

    # Заливка области
    ax.tripcolor(x, y, triangles, np.ones(len(x)),
                 shading='flat', alpha=0.15, cmap='Blues')

    # Сетка
    ax.triplot(x, y, triangles, color='#4a6fa5', linewidth=0.5)

    # Цветные границы
    colors = {1: "red", 2: "green", 3: "blue", 4: "purple"}
    for line, tag in zip(lines, line_data):
        pts = points[line]
        ax.plot(pts[:, 0], pts[:, 1], color=colors.get(tag, "black"), linewidth=2.0)

    # Оси и подписи
    ax.set_xlabel(r"$x_1$", fontsize=12)
    ax.set_ylabel(r"$x_2$", fontsize=12)
    ax.text(2, 1.3, r"$\Gamma_2$", ha='center', fontsize=13)
    ax.text(2, -1.4, r"$\Gamma_1$", ha='center', fontsize=13)
    ax.text(-0.5, 0.5, r"$\Gamma_3$", rotation=90, va='center', fontsize=13)
    ax.text(4.5, 0.5, r"$\Gamma_4$", rotation=90, va='center', fontsize=13)
    ax.text(2, 0.3, r"$\Omega$", fontsize=16, alpha=0.6)
    ax.set_aspect('equal')
    ax.set_xlim(-0.6, 4.7)
    ax.set_ylim(-1.6, 1.6)
    ax.grid(False)
    fig.tight_layout()

    # Сохраняем PNG
    png_path = os.path.join(MESH_DIR, f"channel_step_mesh_{level}.png")
    fig.savefig(png_path, dpi=200)
    plt.close(fig)
    print(f"PNG сохранён: {png_path}")

    # Собираем статистику
    stats.append({
        "level": level,
        "factor": scale,
        "nodes": nodes,
        "elements": elements,
        "msh": msh_path,
        "png": png_path
    })

# Сохраняем stats.json для Streamlit
stats_path = os.path.join(MESH_DIR, "stats.json")
with open(stats_path, 'w', encoding='utf-8') as f:
    json.dump(stats, f, indent=2, ensure_ascii=False)
print(f"\nСтатистика сохранена: {stats_path}")

# запуск GUI (можно убрать)
#if '-nopopup' not in sys.argv:
#    gmsh.fltk.run()

gmsh.finalize()