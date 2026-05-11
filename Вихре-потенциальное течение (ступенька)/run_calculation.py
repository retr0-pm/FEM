"""
Запуск всех расчётов для задачи вихре-потенциального течения в канале с уступом.
- Конвертация .msh в .xdmf
- Расчёты для разных сеток, степеней p, циркуляций, высот уступа
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

from vortex_solver import solve_vortex_channel


# Пути
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MESH_DIR = os.path.join(PROJECT_DIR, "meshes")
RESULTS_DIR = os.path.join(PROJECT_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# Параметры геометрии
L = 4.0
H = 1.0
l = 1.0


def convert_msh_to_xdmf(msh_path, xdmf_path):
    """
    Конвертация Gmsh .msh в XDMF для dolfin.
    Использует dolfin.MeshEditor для создания сетки напрямую.
    """
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
    """
    Создаёт маркеры границ на основе данных из .msh файла.
    Возвращает MeshFunction с теми же тегами, что в Gmsh:
        1 — Gamma1, 2 — Gamma2, 3 — Gamma3, 4 — Gamma4.
    """
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


def save_results_json(all_results):
    """Сохраняет сводную таблицу результатов в CSV."""
    import pandas as pd
    df = pd.DataFrame(all_results)
    csv_path = os.path.join(RESULTS_DIR, "all_results.csv")
    df.to_csv(csv_path, index=False)
    print(f"\nСводная таблица сохранена: {csv_path}")


def plot_and_save(psi, mesh, file_prefix, h_val, title=""):
    """
    Рисует и сохраняет графики: цветовую карту psi и изолинии с границами области.
    """
    V = psi.function_space()

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
    ax.plot(outline_x, outline_y, 'k-', linewidth=2.0, label='Граница области')

    # Уступ (жирная линия)
    ax.plot([l, l], [0, -h_val], 'k-', linewidth=3.0)
    ax.plot([0, l], [0, 0], 'k-', linewidth=3.0)

    ax.set_xlabel(r'$x_1$')
    ax.set_ylabel(r'$x_2$')
    ax.set_aspect('equal')
    ax.set_title(title)
    ax.legend(loc='upper right')
    fig.tight_layout()
    psi_path = os.path.join(RESULTS_DIR, f"{file_prefix}_psi.png")
    fig.savefig(psi_path, dpi=150)
    plt.close(fig)
    print(f"  Сохранено: {psi_path}")

    # --- Изолинии (линии тока) ---
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

    # Контур области
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

    return psi_path, stream_path


def run_single_calculation(mesh, boundaries, level, p, Gamma_val, h_val, variant_label):
    """Выполняет один расчёт и сохраняет результаты."""
    print(f"\n--- Расчёт: h={h_val}, {level}, p={p}, Gamma={Gamma_val} ---")

    results = solve_vortex_channel(
        mesh, boundaries, degree=p,
        Gamma=Gamma_val, H=H, h=h_val,
        max_iter=100, tol=1e-6
    )

    file_prefix = f"{variant_label}_h{h_val}_{level}_p{p}"
    psi_path, stream_path = plot_and_save(
        results["psi"], mesh, file_prefix, h_val,
        title=f"$h={h_val}$, $\\Gamma={Gamma_val}$, {level}, $p={p}$"
    )

    if len(results["error_history"]) > 0:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.semilogy(range(1, len(results["error_history"]) + 1),
                    results["error_history"], 'o-', markersize=4)
        ax.set_xlabel('Итерация')
        ax.set_ylabel('Относительная ошибка')
        ax.set_title(f'Сходимость: $h={h_val}$, $\\Gamma={Gamma_val}$, {level}, $p={p}$')
        ax.grid(True)
        fig.tight_layout()
        conv_path = os.path.join(RESULTS_DIR, f"{file_prefix}_convergence.png")
        fig.savefig(conv_path, dpi=150)
        plt.close(fig)
    else:
        conv_path = ""

    return {
        "variant": variant_label,
        "Gamma": Gamma_val,
        "h": h_val,
        "level": level,
        "degree": p,
        "nodes": mesh.num_vertices(),
        "cells": mesh.num_cells(),
        "omega": results["omega"],
        "S": results["S"],
        "n_iterations": results["n_iterations"],
        "converged": results["converged"],
        "psi_path": psi_path,
        "stream_path": stream_path,
        "conv_path": conv_path
    }


def load_or_convert_mesh(h_val, level):
    """Загружает или конвертирует сетку для заданных h и уровня."""
    msh_name = f"channel_step_mesh_h{h_val}_{level}.msh"
    msh_path = os.path.join(MESH_DIR, msh_name)
    xdmf_path = msh_path.replace(".msh", ".xdmf")

    if not os.path.exists(msh_path):
        print(f"Файл не найден: {msh_path}, пропускаем.")
        return None, None, None

    if not os.path.exists(xdmf_path):
        convert_msh_to_xdmf(msh_path, xdmf_path)

    mesh = Mesh()
    with XDMFFile(xdmf_path) as infile:
        infile.read(mesh)

    boundaries = create_boundary_markers(mesh, msh_path)
    return mesh, boundaries, msh_name


# ============================================================
# ОСНОВНОЙ ЦИКЛ РАСЧЁТОВ
# ============================================================

if __name__ == "__main__":
    all_results = []

    # Все параметры
    h_values = [0.5, 1.0, 1.5]
    levels = ["level1", "level2", "level3"]
    degrees = [1, 2, 3]
    gamma_values = [-1.0, -2.0, -4.0]

    total = len(h_values) * len(levels) * len(degrees) * len(gamma_values)
    count = 0

    print("=" * 60)
    print(f"ПОЛНЫЙ ПЕРЕБОР: {total} вариантов")
    print("=" * 60)

    for h_val in h_values:
        for level in levels:
            mesh, boundaries, msh_name = load_or_convert_mesh(h_val, level)
            if mesh is None:
                continue

            for p in degrees:
                for Gamma_val in gamma_values:
                    count += 1
                    variant_label = f"h{h_val}_G{Gamma_val}"
                    print(f"\n{'='*60}")
                    print(f"[{count}/{total}] h={h_val}, {level}, p={p}, Gamma={Gamma_val}")
                    print(f"{'='*60}")

                    result = run_single_calculation(
                        mesh, boundaries, level, p,
                        Gamma_val, h_val, variant_label
                    )
                    all_results.append(result)
                    print(f"  omega = {result['omega']:.6f}, S = {result['S']:.6f}, "
                          f"итераций = {result['n_iterations']}")

    save_results_json(all_results)

    print("\n" + "=" * 60)
    print("ВСЕ РАСЧЁТЫ ЗАВЕРШЕНЫ")
    print(f"Всего вариантов: {len(all_results)}")
    print("=" * 60)