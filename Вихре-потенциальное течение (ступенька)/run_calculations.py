"""
Запуск расчётов вихре-потенциального течения.
- Верификация по сеткам: все степени p на всех сетках (базовый h=1.0, Gamma=-2)
- Влияние параметров: только на level3, p=2
"""
import os
import numpy as np
import meshio
from dolfin import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from vortex_solver import solve_vortex_channel

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MESH_DIR = os.path.join(PROJECT_DIR, "meshes")
RESULTS_DIR = os.path.join(PROJECT_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

L, H, l = 4.0, 1.0, 1.0


def convert_msh_to_xdmf(msh_path, xdmf_path):
    """Конвертация Gmsh .msh в XDMF для dolfin."""
    mesh_data = meshio.read(msh_path)
    triangles = mesh_data.cells_dict["triangle"]

    mesh = Mesh()
    editor = MeshEditor()
    editor.open(mesh, "triangle", 2, 2)
    editor.init_vertices(mesh_data.points.shape[0])
    editor.init_cells(triangles.shape[0])
    for i, pt in enumerate(mesh_data.points):
        editor.add_vertex(i, [pt[0], pt[1]])
    for i, tri in enumerate(triangles):
        editor.add_cell(i, [tri[0], tri[1], tri[2]])
    editor.close()

    with XDMFFile(xdmf_path) as f:
        f.write(mesh)
    print(f"  Конвертировано: {os.path.basename(msh_path)} -> {os.path.basename(xdmf_path)}")


def create_boundary_markers(mesh, msh_path):
    """Создаёт маркеры границ."""
    mesh_data = meshio.read(msh_path)
    boundaries = MeshFunction("size_t", mesh, mesh.topology().dim() - 1)
    boundaries.set_all(0)

    if "line" not in mesh_data.cells_dict:
        return boundaries

    lines = mesh_data.cells_dict["line"]
    line_tags = mesh_data.cell_data_dict.get("gmsh:physical", {}).get("line",
                                np.zeros(len(lines), dtype=int))
    points = mesh_data.points[:, :2]
    coords = mesh.coordinates()

    for f in facets(mesh):
        v0, v1 = f.entities(0)[0], f.entities(0)[1]
        p0, p1 = coords[v0], coords[v1]
        for line_idx, line in enumerate(lines):
            lp0, lp1 = points[line[0]], points[line[1]]
            if (np.linalg.norm(p0 - lp0) + np.linalg.norm(p1 - lp1) < 1e-6 or
                np.linalg.norm(p0 - lp1) + np.linalg.norm(p1 - lp0) < 1e-6):
                boundaries.array()[f.index()] = int(line_tags[line_idx])
                break
    return boundaries


def plot_and_save(psi, mesh, file_prefix, h_val, title=""):
    """Рисует графики с двухцветной картой и colorbar."""
    mesh_coords = mesh.coordinates()
    tri = np.array([cell.entities(0) for cell in cells(mesh)], dtype=int)
    psi_verts = psi.compute_vertex_values(mesh)
    psi_min, psi_max = psi_verts.min(), psi_verts.max()

    n_neg, n_pos = 12, 12
    # Отрицательные: синий (центр) -> красный (0)
    neg_cmap = plt.cm.coolwarm_r
    neg_colors = neg_cmap(np.linspace(0.15, 0.85, n_neg))
    # Положительные: зелёный (0) -> жёлтый
    pos_cmap = plt.cm.YlGn
    pos_colors = pos_cmap(np.linspace(0.2, 1.0, n_pos))

    colors = np.vstack([neg_colors, pos_colors])
    cmap = plt.matplotlib.colors.ListedColormap(colors)

    # Границы для нормировки
    if psi_min < 0 < psi_max:
        neg_boundaries = np.linspace(psi_min, 0, n_neg + 1)
        pos_boundaries = np.linspace(0, psi_max, n_pos + 1)
        boundaries = np.concatenate([neg_boundaries[:-1], pos_boundaries])
        norm = plt.matplotlib.colors.BoundaryNorm(boundaries, n_neg + n_pos)
    elif psi_max <= 0:
        boundaries = np.linspace(psi_min, 0, n_neg + 1)
        norm = plt.matplotlib.colors.BoundaryNorm(boundaries, n_neg)
    else:
        boundaries = np.linspace(0, psi_max, n_pos + 1)
        norm = plt.matplotlib.colors.BoundaryNorm(boundaries, n_pos)

    # --- Цветовая карта psi (divergent, белый в нуле, усиленный контраст) ---
    fig, ax = plt.subplots(figsize=(10, 4))

    # Используем TwoSlopeNorm с независимыми vmin, vmax и резким переходом
    # Делаем vmin и vmax независимыми, с запасом на отрицательную часть
    vmin = psi_min * 1.05  # чуть больше диапазон для контраста
    vmax = psi_max * 1.05

    # TwoSlopeNorm с центром в 0 — белый цвет в нуле
    norm = plt.matplotlib.colors.TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)

    tcf = ax.tripcolor(mesh_coords[:, 0], mesh_coords[:, 1], tri, psi_verts,
                       shading='flat', cmap='RdBu_r', norm=norm)
    cbar = fig.colorbar(tcf, ax=ax, label=r'$\psi$', extend='both')

    # Подписи тиков
    ticks = []
    if psi_min < 0:
        ticks.extend([psi_min, psi_min / 2, 0])
    else:
        ticks.append(0)
    if psi_max > 0:
        ticks.extend([psi_max / 2, psi_max])
    cbar.set_ticks(ticks)
    cbar.set_ticklabels([f'{t:.2f}' for t in ticks])

    # Нулевая изолиния (жирная чёрная)
    if psi_min < 0 < psi_max:
        ax.tricontour(mesh_coords[:, 0], mesh_coords[:, 1], tri, psi_verts,
                      levels=[0], colors='black', linewidths=2.5, linestyles='-')

    # Контур области и уступ
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

    # --- Изолинии ---
    fig, ax = plt.subplots(figsize=(10, 4))
    if psi_max > 0:
        ax.tricontour(mesh_coords[:, 0], mesh_coords[:, 1], tri, psi_verts,
                      levels=np.linspace(0, psi_max, 15)[1:], colors='blue', linewidths=0.6)
    if psi_min < 0:
        ax.tricontour(mesh_coords[:, 0], mesh_coords[:, 1], tri, psi_verts,
                      levels=np.linspace(psi_min, 0, 10)[:-1], colors='red', linewidths=0.6)
        ax.tricontourf(mesh_coords[:, 0], mesh_coords[:, 1], tri, psi_verts,
                       levels=[psi_min, 0], colors=['#ffcccc'], alpha=0.3)
    if psi_min < 0 < psi_max:
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

    return psi_path, stream_path


def run_calc(mesh, boundaries, level, p, Gamma_val, h_val, label):
    """Один расчёт."""
    print(f"\n--- Расчёт: h={h_val}, {level}, p={p}, Gamma={Gamma_val} ---")
    r = solve_vortex_channel(mesh, boundaries, degree=p, Gamma=Gamma_val, H=H, h=h_val)
    prefix = f"{label}_h{h_val}_{level}_p{p}"
    psi_p, str_p = plot_and_save(r["psi"], mesh, prefix, h_val,
                                 title=f"$h={h_val}$, $\\Gamma={Gamma_val}$, {level}, $p={p}$")
    conv_p = ""
    if len(r["error_history"]) > 0:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.semilogy(range(1, len(r["error_history"]) + 1), r["error_history"], 'o-', markersize=4)
        ax.set_xlabel('Итерация'); ax.set_ylabel('Относительная ошибка')
        ax.grid(True); fig.tight_layout()
        conv_p = os.path.join(RESULTS_DIR, f"{prefix}_convergence.png")
        fig.savefig(conv_p, dpi=150); plt.close(fig)

    return {"variant": label, "Gamma": Gamma_val, "h": h_val, "level": level,
            "degree": p, "nodes": mesh.num_vertices(), "cells": mesh.num_cells(),
            "omega": r["omega"], "S": r["S"],
            "psi_min": r["psi_min"], "x_attach": r["x_attach"],
            "y_max_vortex": r["y_max_vortex"],
            "x_vortex_center": r["x_vortex_center"],
            "y_vortex_center": r["y_vortex_center"],
            "n_iterations": r["n_iterations"], "converged": r["converged"],
            "psi_path": psi_p, "stream_path": str_p, "conv_path": conv_p}


def load_mesh(h_val, level):
    msh = os.path.join(MESH_DIR, f"channel_step_mesh_h{h_val}_{level}.msh")
    xdmf = msh.replace(".msh", ".xdmf")
    if not os.path.exists(msh):
        return None, None
    if not os.path.exists(xdmf):
        convert_msh_to_xdmf(msh, xdmf)
    mesh = Mesh()
    with XDMFFile(xdmf) as f:
        f.read(mesh)
    return mesh, create_boundary_markers(mesh, msh)


if __name__ == "__main__":
    all_results = []

    # === БЛОК 1: ВЕРИФИКАЦИЯ ПО СЕТКАМ ===
    # h=1.0, Gamma=-2, все сетки, все степени p
    print("=" * 60)
    print("БЛОК 1: ВЕРИФИКАЦИЯ ПО СЕТКАМ (h=1.0, Gamma=-2)")
    print("=" * 60)
    for level in ["level1", "level2", "level3"]:
        mesh, bnd = load_mesh(1.0, level)
        if mesh is None:
            continue
        for p in [1, 2, 3]:
            all_results.append(run_calc(mesh, bnd, level, p, -2.0, 1.0, "verification"))

    # === БЛОК 2: ВЛИЯНИЕ ПАРАМЕТРОВ (level3, p=2) ===
    print("\n" + "=" * 60)
    print("БЛОК 2: ВЛИЯНИЕ ПАРАМЕТРОВ (level3, p=2)")
    print("=" * 60)

    # Влияние циркуляции: h=1.0, level3, p=2, Gamma=-1,-2,-4
    print("\n--- Влияние Gamma ---")
    mesh, bnd = load_mesh(1.0, "level3")
    if mesh is not None:
        for Gamma_val in [-1.0, -2.0, -4.0]:
            all_results.append(run_calc(mesh, bnd, "level3", 2, Gamma_val, 1.0,
                                        f"Gamma_{Gamma_val}"))

    # Влияние высоты уступа: level3, p=2, Gamma=-2, h=0.5,1.0,1.5
    print("\n--- Влияние h ---")
    for h_val in [0.5, 1.0, 1.5]:
        mesh, bnd = load_mesh(h_val, "level3")
        if mesh is None:
            continue
        all_results.append(run_calc(mesh, bnd, "level3", 2, -2.0, h_val,
                                    f"h_{h_val}"))

    import pandas as pd
    df = pd.DataFrame(all_results)
    csv_path = os.path.join(RESULTS_DIR, "all_results.csv")
    df.to_csv(csv_path, index=False)
    print(f"\nСводная таблица сохранена: {csv_path}")
    print(f"Всего вариантов: {len(all_results)}")