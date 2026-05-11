"""
Запуск всех расчётов для задачи вихре-потенциального течения в канале с уступом.
- Конвертация .msh в .xdmf
- Расчёты для разных сеток, степеней p, циркуляций
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


def plot_and_save(psi, mesh, file_prefix, title=""):
    """
    Рисует и сохраняет графики: цветовую карту psi и изолинии с границами области.
    """
    V = psi.function_space()
    psi_vals_all = psi.vector().get_local()

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

    # Рисуем контур области (границы канала и уступа)
    # Канал: x1 от 0 до 4, x2 от -1 до 1 (с учётом уступа)
    L, H = 4.0, 1.0
    l, h = 1.0, 1.0

    # Внешний контур области
    outline_x = [0, l, l, L, L, 0, 0]
    outline_y = [0, 0, -h, -h, H, H, 0]
    ax.plot(outline_x, outline_y, 'k-', linewidth=2.0, label='Граница области')

    # Уступ (жирная линия)
    ax.plot([l, l], [0, -h], 'k-', linewidth=3.0)
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
    ax.plot([l, l], [0, -h], 'k-', linewidth=3.0)
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


# ============================================================
# ОСНОВНОЙ ЦИКЛ РАСЧЁТОВ
# ============================================================

if __name__ == "__main__":
    levels = ["level2", "level1"]  # level3 слишком медленный, пока пропускаем
    degrees = [1, 2, 3]

    all_results = []

    # --- Базовый вариант: Gamma = -2, h = 1.0 ---
    Gamma_base = -2.0

    print("=" * 60)
    print("БАЗОВЫЙ ВАРИАНТ: Gamma = -2, h = 1.0")
    print("=" * 60)

    for level in levels:
        msh_path = os.path.join(MESH_DIR, f"channel_step_mesh_{level}.msh")
        xdmf_path = os.path.join(MESH_DIR, f"channel_step_mesh_{level}.xdmf")

        if not os.path.exists(msh_path):
            print(f"Файл не найден: {msh_path}, пропускаем.")
            continue

        if not os.path.exists(xdmf_path):
            convert_msh_to_xdmf(msh_path, xdmf_path)

        mesh = Mesh()
        with XDMFFile(xdmf_path) as infile:
            infile.read(mesh)

        boundaries = create_boundary_markers(mesh, msh_path)

        # Отладка: считаем грани
        from collections import Counter
        tag_counts = Counter()
        for f in facets(mesh):
            tag_counts[boundaries.array()[f.index()]] += 1
        print(f"  Грани: {dict(tag_counts)}")

        for p in degrees:
            print(f"\n--- Расчёт: {level}, p={p} ---")

            results = solve_vortex_channel(
                mesh, boundaries, degree=p,
                Gamma=Gamma_base, H=H,
                max_iter=100, tol=1e-6
            )

            file_prefix = f"base_{level}_p{p}"
            psi_path, stream_path = plot_and_save(
                results["psi"], mesh, file_prefix,
                title=f"$\\Gamma={Gamma_base}$, {level}, $p={p}$"
            )

            if len(results["error_history"]) > 0:
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.semilogy(range(1, len(results["error_history"]) + 1),
                            results["error_history"], 'o-', markersize=4)
                ax.set_xlabel('Итерация')
                ax.set_ylabel('Относительная ошибка')
                ax.set_title(f'Сходимость: $\\Gamma={Gamma_base}$, {level}, $p={p}$')
                ax.grid(True)
                fig.tight_layout()
                conv_path = os.path.join(RESULTS_DIR, f"{file_prefix}_convergence.png")
                fig.savefig(conv_path, dpi=150)
                plt.close(fig)
            else:
                conv_path = ""

            all_results.append({
                "variant": "base",
                "Gamma": Gamma_base,
                "h": 1.0,
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
            })

            print(f"  omega = {results['omega']:.6f}, S = {results['S']:.6f}, "
                  f"итераций = {results['n_iterations']}")

    # --- Дополнительные варианты циркуляции ---
    gamma_values = [-1.0, -4.0]
    level_mid = "level2"
    p_mid = 2

    for Gamma_var in gamma_values:
        print(f"\n{'=' * 60}")
        print(f"ВАРИАНТ: Gamma = {Gamma_var}, h = 1.0")
        print("=" * 60)

        msh_path = os.path.join(MESH_DIR, f"channel_step_mesh_{level_mid}.msh")
        xdmf_path = os.path.join(MESH_DIR, f"channel_step_mesh_{level_mid}.xdmf")

        if not os.path.exists(xdmf_path):
            convert_msh_to_xdmf(msh_path, xdmf_path)

        mesh = Mesh()
        with XDMFFile(xdmf_path) as infile:
            infile.read(mesh)

        boundaries = create_boundary_markers(mesh, msh_path)

        print(f"\n--- Расчёт: {level_mid}, p={p_mid} ---")

        results = solve_vortex_channel(
            mesh, boundaries, degree=p_mid,
            Gamma=Gamma_var, H=H,
            max_iter=100, tol=1e-6
        )

        file_prefix = f"Gamma_{Gamma_var}_{level_mid}_p{p_mid}"
        psi_path, stream_path = plot_and_save(
            results["psi"], mesh, file_prefix,
            title=f"$\\Gamma={Gamma_var}$, {level_mid}, $p={p_mid}$"
        )

        if len(results["error_history"]) > 0:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.semilogy(range(1, len(results["error_history"]) + 1),
                        results["error_history"], 'o-', markersize=4)
            ax.set_xlabel('Итерация')
            ax.set_ylabel('Относительная ошибка')
            ax.set_title(f'Сходимость: $\\Gamma={Gamma_var}$, {level_mid}, $p={p_mid}$')
            ax.grid(True)
            fig.tight_layout()
            conv_path = os.path.join(RESULTS_DIR, f"{file_prefix}_convergence.png")
            fig.savefig(conv_path, dpi=150)
            plt.close(fig)
        else:
            conv_path = ""

        all_results.append({
            "variant": f"Gamma_{Gamma_var}",
            "Gamma": Gamma_var,
            "h": 1.0,
            "level": level_mid,
            "degree": p_mid,
            "nodes": mesh.num_vertices(),
            "cells": mesh.num_cells(),
            "omega": results["omega"],
            "S": results["S"],
            "n_iterations": results["n_iterations"],
            "converged": results["converged"],
            "psi_path": psi_path,
            "stream_path": stream_path,
            "conv_path": conv_path
        })

        print(f"  omega = {results['omega']:.6f}, S = {results['S']:.6f}, "
              f"итераций = {results['n_iterations']}")

    save_results_json(all_results)

    print("\n" + "=" * 60)
    print("ВСЕ РАСЧЁТЫ ЗАВЕРШЕНЫ")
    print("=" * 60)