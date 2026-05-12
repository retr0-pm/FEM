"""
Запуск расчётов для расширенной вихре-потенциальной модели с omega(psi).
Сравнение моделей: const, linear, exp.
"""
import os
import json
import numpy as np
import meshio
from dolfin import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from vortex_solver_omega import solve_vortex_channel_omega

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MESH_DIR = os.path.join(PROJECT_DIR, "meshes")
RESULTS_DIR = os.path.join(PROJECT_DIR, "results_omega")
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
    """Рисует графики с двухцветной картой (белый в нуле)."""
    mesh_coords = mesh.coordinates()
    tri = np.array([cell.entities(0) for cell in cells(mesh)], dtype=int)
    psi_verts = psi.compute_vertex_values(mesh)
    psi_min, psi_max = psi_verts.min(), psi_verts.max()

    # --- Цветовая карта psi ---
    fig, ax = plt.subplots(figsize=(10, 4))

    vmin = psi_min * 1.05
    vmax = psi_max * 1.05
    norm = plt.matplotlib.colors.TwoSlopeNorm(vmin=vmin, vcenter=0, vmax=vmax)

    tcf = ax.tripcolor(mesh_coords[:, 0], mesh_coords[:, 1], tri, psi_verts,
                       shading='flat', cmap='RdBu_r', norm=norm)
    cbar = fig.colorbar(tcf, ax=ax, label=r'$\psi$', extend='both')

    ticks = []
    if psi_min < 0:
        ticks.extend([psi_min, psi_min / 2, 0])
    else:
        ticks.append(0)
    if psi_max > 0:
        ticks.extend([psi_max / 2, psi_max])
    cbar.set_ticks(ticks)
    cbar.set_ticklabels([f'{t:.2f}' for t in ticks])

    if psi_min < 0 < psi_max:
        ax.tricontour(mesh_coords[:, 0], mesh_coords[:, 1], tri, psi_verts,
                      levels=[0], colors='black', linewidths=2.5, linestyles='-')

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

    return psi_path, stream_path


def plot_profiles(all_results, RESULTS_DIR):
    """Строит графики профилей psi и omega для всех моделей."""
    colors = {'const': '#2196F3', 'linear': '#4CAF50', 'exp': '#FF9800'}
    model_names = {'const': 'const', 'linear': 'linear', 'exp': 'exp'}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    for res in all_results:
        model = res['model']
        profiles = res['profiles']
        x2 = np.array(profiles['x2'])
        psi_vals = np.array(profiles['psi'])
        omega_vals = np.array(profiles['omega'])

        ax1.plot(x2, psi_vals, color=colors[model], linewidth=2, label=model)
        ax2.plot(x2, omega_vals, color=colors[model], linewidth=2, label=model)

    ax1.set_xlabel('x₂')
    ax1.set_ylabel('ψ')
    ax1.set_title('Профиль ψ(x₂) при x₁ = 1.5')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2.set_xlabel('x₂')
    ax2.set_ylabel('ω')
    ax2.set_title('Профиль ω(x₂) при x₁ = 1.5')
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    profiles_path = os.path.join(RESULTS_DIR, "profiles_comparison.png")
    fig.savefig(profiles_path, dpi=150)
    plt.close(fig)
    print(f"  Сохранено: {profiles_path}")
    return profiles_path


if __name__ == "__main__":
    h_val = 1.0
    level = "level3"
    Gamma_val = -2.0
    p = 2

    models = ["const", "linear", "exp"]
    all_results = []

    print("=" * 60)
    print("РАСШИРЕННАЯ МОДЕЛЬ: omega(psi)")
    print(f"h = {h_val}, {level}, p = {p}, Gamma = {Gamma_val}")
    print(f"Модели: {models}")
    print("=" * 60)

    msh_name = f"channel_step_mesh_h{h_val}_{level}.msh"
    msh_path = os.path.join(MESH_DIR, msh_name)
    xdmf_path = msh_path.replace(".msh", ".xdmf")

    if not os.path.exists(xdmf_path):
        convert_msh_to_xdmf(msh_path, xdmf_path)

    mesh = Mesh()
    with XDMFFile(xdmf_path) as infile:
        infile.read(mesh)
    boundaries = create_boundary_markers(mesh, msh_path)

    print(f"  Сетка: {mesh.num_vertices()} узлов, {mesh.num_cells()} ячеек")

    for model in models:
        print(f"\n{'='*60}")
        print(f"Модель: omega(psi) = {model}")
        print(f"{'='*60}")

        results = solve_vortex_channel_omega(
            mesh, boundaries, degree=p,
            Gamma=Gamma_val, H=H, h=h_val,
            omega_model=model, psi_ref=None,
            max_iter=100, tol=1e-6
        )

        file_prefix = f"omega_{model}_h{h_val}_{level}_p{p}"
        psi_path, stream_path = plot_and_save(
            results["psi"], mesh, file_prefix, h_val,
            title=f"omega model: {model}, h={h_val}, Gamma={Gamma_val}"
        )

        if len(results["error_history"]) > 0:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.semilogy(range(1, len(results["error_history"]) + 1),
                        results["error_history"], 'o-', markersize=4)
            ax.set_xlabel('Итерация')
            ax.set_ylabel('Относительная ошибка')
            ax.set_title(f'Сходимость: модель {model}')
            ax.grid(True)
            fig.tight_layout()
            conv_path = os.path.join(RESULTS_DIR, f"{file_prefix}_convergence.png")
            fig.savefig(conv_path, dpi=150)
            plt.close(fig)
        else:
            conv_path = ""

        all_results.append({
            "model": model,
            "Gamma": Gamma_val,
            "h": h_val,
            "level": level,
            "degree": p,
            "nodes": mesh.num_vertices(),
            "cells": mesh.num_cells(),
            "S": results["S"],
            "omega_scale": results["omega_scale"],
            "psi_min": results["psi_min"],
            "x_attach": results["x_attach"],
            "y_max_vortex": results["y_max_vortex"],
            "x_vortex_center": results["x_vortex_center"],
            "y_vortex_center": results["y_vortex_center"],
            "n_iterations": results["n_iterations"],
            "converged": results["converged"],
            "psi_path": psi_path,
            "stream_path": stream_path,
            "conv_path": conv_path,
            "profiles": results["profiles"]
        })

        print(f"  S = {results['S']:.6f}, scale = {results['omega_scale']:.6f}, "
              f"итераций = {results['n_iterations']}")

    # Строим профили
    profiles_path = plot_profiles(all_results, RESULTS_DIR)

    # Сохраняем результаты
    df_data = []
    for res in all_results:
        row = {k: v for k, v in res.items() if k != 'profiles'}
        df_data.append(row)

    import pandas as pd
    df = pd.DataFrame(df_data)
    csv_path = os.path.join(RESULTS_DIR, "omega_results.csv")
    df.to_csv(csv_path, index=False)

    # Сохраняем профили в JSON
    profiles_data = {res['model']: res['profiles'] for res in all_results}
    profiles_json_path = os.path.join(RESULTS_DIR, "profiles.json")
    with open(profiles_json_path, 'w') as f:
        json.dump(profiles_data, f, indent=2)

    print(f"\nРезультаты сохранены: {csv_path}")
    print(f"Профили сохранены: {profiles_json_path}")
    print(f"Всего вариантов: {len(all_results)}")