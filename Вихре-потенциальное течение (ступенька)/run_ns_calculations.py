"""
Запуск расчётов Навье-Стокса для течения в канале с уступом.
- Использует существующие сетки из папки meshes/
- Расчёты для разных Re на сетке level2, h = 1.0
- Сохранение результатов
"""
import os
import sys
import json
import numpy as np
import meshio
from dolfin import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from ns_solver import solve_navier_stokes_channel


# Пути
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MESH_DIR = os.path.join(PROJECT_DIR, "meshes")
RESULTS_DIR = os.path.join(PROJECT_DIR, "results_ns")
os.makedirs(RESULTS_DIR, exist_ok=True)

# Параметры геометрии
L = 4.0
H = 1.0
l = 1.0


def convert_msh_to_xdmf(msh_path, xdmf_path):
    """Конвертация Gmsh .msh в XDMF для dolfin."""
    mesh_data = meshio.read(msh_path)

    triangles = None
    for block in mesh_data.cells:
        if block.type == "triangle":
            triangles = block.data
            break

    if triangles is None:
        raise ValueError("Не найдены треугольники в .msh файле")

    mesh = Mesh()
    editor = MeshEditor()
    editor.open(mesh, "triangle", 2, 2)

    n_vertices = mesh_data.points.shape[0]
    n_cells = triangles.shape[0]

    editor.init_vertices(n_vertices)
    editor.init_cells(n_cells)

    for i, pt in enumerate(mesh_data.points):
        editor.add_vertex(i, [pt[0], pt[1]])

    for i, tri in enumerate(triangles):
        editor.add_cell(i, [tri[0], tri[1], tri[2]])

    editor.close()

    with XDMFFile(xdmf_path) as f:
        f.write(mesh)

    print(f"  Конвертировано: {os.path.basename(msh_path)} -> {os.path.basename(xdmf_path)}")


def create_boundary_markers(mesh, msh_path):
    """Создаёт маркеры границ на основе данных из .msh файла."""
    mesh_data = meshio.read(msh_path)

    boundaries = MeshFunction("size_t", mesh, mesh.topology().dim() - 1)
    boundaries.set_all(0)

    if "line" in mesh_data.cells_dict:
        lines = mesh_data.cells_dict["line"]
        if "gmsh:physical" in mesh_data.cell_data_dict:
            line_tags = mesh_data.cell_data_dict["gmsh:physical"]["line"]
        else:
            line_tags = np.zeros(len(lines), dtype=int)
    else:
        print("  Предупреждение: нет линий в .msh, границы не размечены")
        return boundaries

    points = mesh_data.points[:, :2]
    coords = mesh.coordinates()

    for f in facets(mesh):
        v0 = f.entities(0)[0]
        v1 = f.entities(0)[1]
        p0 = coords[v0]
        p1 = coords[v1]

        for line_idx, line in enumerate(lines):
            lp0 = points[line[0]]
            lp1 = points[line[1]]

            d1 = np.linalg.norm(p0 - lp0) + np.linalg.norm(p1 - lp1)
            d2 = np.linalg.norm(p0 - lp1) + np.linalg.norm(p1 - lp0)

            if d1 < 1e-6 or d2 < 1e-6:
                boundaries.array()[f.index()] = int(line_tags[line_idx])
                break

    return boundaries


def plot_and_save_ns(psi, u, mesh, file_prefix, h_val, title=""):
    """
    Рисует и сохраняет графики: функция тока, линии тока, поле скорости.
    """
    mesh_coords = mesh.coordinates()
    tri = np.zeros((mesh.num_cells(), 3), dtype=int)
    for i, cell in enumerate(cells(mesh)):
        tri[i] = cell.entities(0)

    psi_verts = psi.compute_vertex_values(mesh)

    # --- Цветовая карта psi ---
    fig, ax = plt.subplots(figsize=(10, 4))
    tcf = ax.tripcolor(mesh_coords[:, 0], mesh_coords[:, 1], tri, psi_verts,
                       shading='gouraud', cmap='RdBu_r')
    fig.colorbar(tcf, ax=ax, label=r'$\psi$')

    # Контур области
    outline_x = [0, l, l, L, L, 0, 0]
    outline_y = [0, 0, -h_val, -h_val, H, H, 0]
    ax.plot(outline_x, outline_y, 'k-', linewidth=2.0)
    ax.plot([l, l], [0, -h_val], 'k-', linewidth=3.0)
    ax.plot([0, l], [0, 0], 'k-', linewidth=3.0)

    ax.set_xlabel(r'$x_1$')
    ax.set_ylabel(r'$x_2$')
    ax.set_aspect('equal')
    ax.set_title(title)
    fig.tight_layout()
    psi_path = os.path.join(RESULTS_DIR, f"{file_prefix}_psi.png")
    fig.savefig(psi_path, dpi=150)
    plt.close(fig)
    print(f"  Сохранено: {psi_path}")

    # --- Изолинии с заливкой вихря ---
    fig, ax = plt.subplots(figsize=(10, 4))

    psi_min = psi_verts.min()
    psi_max = psi_verts.max()

    if psi_max > 0:
        levels_pos = np.linspace(0, psi_max, 15)
        ax.tricontour(mesh_coords[:, 0], mesh_coords[:, 1], tri, psi_verts,
                      levels=levels_pos[1:], colors='blue', linewidths=0.6, alpha=0.7)

    if psi_min < 0:
        levels_neg = np.linspace(psi_min, 0, 10)
        ax.tricontour(mesh_coords[:, 0], mesh_coords[:, 1], tri, psi_verts,
                      levels=levels_neg[:-1], colors='red', linewidths=0.6, alpha=0.7)
        ax.tricontourf(mesh_coords[:, 0], mesh_coords[:, 1], tri, psi_verts,
                       levels=[psi_min, 0], colors=['#ffcccc'], alpha=0.3)

    if psi_min < 0 and psi_max > 0:
        ax.tricontour(mesh_coords[:, 0], mesh_coords[:, 1], tri, psi_verts,
                      levels=[0], colors='black', linewidths=2.0)

    ax.plot(outline_x, outline_y, 'k-', linewidth=2.0)
    ax.plot([l, l], [0, -h_val], 'k-', linewidth=3.0)
    ax.plot([0, l], [0, 0], 'k-', linewidth=3.0)

    ax.set_xlabel(r'$x_1$')
    ax.set_ylabel(r'$x_2$')
    ax.set_aspect('equal')
    ax.set_title(title)
    fig.tight_layout()
    stream_path = os.path.join(RESULTS_DIR, f"{file_prefix}_streamlines.png")
    fig.savefig(stream_path, dpi=150)
    plt.close(fig)
    print(f"  Сохранено: {stream_path}")

    # --- Поле скорости (модуль) ---
    u_vals = np.array([u(x) for x in mesh_coords])
    u_mag = np.sqrt(u_vals[:, 0]**2 + u_vals[:, 1]**2)

    fig, ax = plt.subplots(figsize=(10, 4))
    tcf = ax.tripcolor(mesh_coords[:, 0], mesh_coords[:, 1], tri, u_mag,
                       shading='gouraud', cmap='viridis')
    fig.colorbar(tcf, ax=ax, label=r'$|\mathbf{u}|$')

    # Векторы скорости (каждый 10-й)
    stride = max(1, len(mesh_coords) // 200)
    ax.quiver(mesh_coords[::stride, 0], mesh_coords[::stride, 1],
              u_vals[::stride, 0], u_vals[::stride, 1],
              scale=5.0, alpha=0.6)

    ax.plot(outline_x, outline_y, 'k-', linewidth=2.0)
    ax.plot([l, l], [0, -h_val], 'k-', linewidth=3.0)
    ax.plot([0, l], [0, 0], 'k-', linewidth=3.0)

    ax.set_xlabel(r'$x_1$')
    ax.set_ylabel(r'$x_2$')
    ax.set_aspect('equal')
    ax.set_title(title)
    fig.tight_layout()
    vel_path = os.path.join(RESULTS_DIR, f"{file_prefix}_velocity.png")
    fig.savefig(vel_path, dpi=150)
    plt.close(fig)
    print(f"  Сохранено: {vel_path}")

    return psi_path, stream_path, vel_path


# ============================================================
# ОСНОВНОЙ ЦИКЛ РАСЧЁТОВ
# ============================================================

if __name__ == "__main__":
    # Расчёты только на level2, h = 1.0
    h_val = 1.0
    level = "level2"
    Re_values = [25, 50, 100]

    all_results = []

    print("=" * 60)
    print("РАСЧЁТЫ НАВЬЕ-СТОКСА")
    print(f"Сетка: {level}, h = {h_val}")
    print(f"Числа Рейнольдса: {Re_values}")
    print("=" * 60)

    # Загрузка сетки
    msh_name = f"channel_step_mesh_h{h_val}_{level}.msh"
    msh_path = os.path.join(MESH_DIR, msh_name)
    xdmf_path = msh_path.replace(".msh", ".xdmf")

    if not os.path.exists(msh_path):
        print(f"Файл не найден: {msh_path}")
        sys.exit(1)

    if not os.path.exists(xdmf_path):
        convert_msh_to_xdmf(msh_path, xdmf_path)

    mesh = Mesh()
    with XDMFFile(xdmf_path) as infile:
        infile.read(mesh)

    boundaries = create_boundary_markers(mesh, msh_path)

    print(f"  Сетка загружена: {mesh.num_vertices()} узлов, {mesh.num_cells()} ячеек")

    for Re in Re_values:
        print(f"\n{'='*60}")
        print(f"Re = {Re}")
        print(f"{'='*60}")

        results = solve_navier_stokes_channel(
            mesh, boundaries, Re=Re, H=H,
            max_iter=50, tol=1e-6
        )

        file_prefix = f"NS_Re{Re}_{level}_h{h_val}"

        psi_path, stream_path, vel_path = plot_and_save_ns(
            results["psi"], results["velocity"], mesh,
            file_prefix, h_val,
            title=f"Навье-Стокс: $Re={Re}$, $h={h_val}$, {level}"
        )

        # График сходимости Пикара
        if len(results["error_history"]) > 0:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.semilogy(range(1, len(results["error_history"]) + 1),
                        results["error_history"], 'o-', markersize=4)
            ax.set_xlabel('Итерация Пикара')
            ax.set_ylabel('Относительная ошибка')
            ax.set_title(f'Сходимость Пикара: $Re={Re}$, $h={h_val}$, {level}')
            ax.grid(True)
            fig.tight_layout()
            conv_path = os.path.join(RESULTS_DIR, f"{file_prefix}_convergence.png")
            fig.savefig(conv_path, dpi=150)
            plt.close(fig)
        else:
            conv_path = ""

        all_results.append({
            "model": "Navier-Stokes",
            "Re": Re,
            "h": h_val,
            "level": level,
            "nodes": mesh.num_vertices(),
            "cells": mesh.num_cells(),
            "S_vortex": results["S_vortex"],
            "n_iterations": results["n_iterations"],
            "converged": results["converged"],
            "psi_path": psi_path,
            "stream_path": stream_path,
            "vel_path": vel_path,
            "conv_path": conv_path
        })

        print(f"  S_vortex = {results['S_vortex']:.6f}, итераций = {results['n_iterations']}")

    # Сохраняем результаты
    import pandas as pd
    df = pd.DataFrame(all_results)
    csv_path = os.path.join(RESULTS_DIR, "ns_results.csv")
    df.to_csv(csv_path, index=False)
    print(f"\nРезультаты сохранены: {csv_path}")

    print("\n" + "=" * 60)
    print("РАСЧЁТЫ НАВЬЕ-СТОКСА ЗАВЕРШЕНЫ")
    print(f"Всего вариантов: {len(all_results)}")
    print("=" * 60)