"""
Предварительные расчеты для задачи обтекания шара
Запускать отдельно: python run_calculations.py
"""

from dolfin import *
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json
import os

# Папки
MESH_DIR = "meshes"
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

def create_boundary_markers(mesh, R=5.0):
    """Создание маркеров границ с параметрическим радиусом"""
    boundaries = MeshFunction("size_t", mesh, mesh.topology().dim() - 1)
    boundaries.set_all(0)

    class SphereBoundary(SubDomain):
        def inside(self, x, on_boundary):
            r = x[1]
            z = x[0]
            return on_boundary and near(r*r + z*z, 1.0, 1e-2) and r > 0

    class OuterBoundary(SubDomain):
        def inside(self, x, on_boundary):
            r = x[1]
            z = x[0]
            return on_boundary and near(r*r + z*z, R*R, 5e-1) and r > 0

    class SymmetryAxis(SubDomain):
        def inside(self, x, on_boundary):
            return on_boundary and near(x[1], 0.0, 1e-3)

    sphere_bd = SphereBoundary()
    outer_bd = OuterBoundary()
    sym_bd = SymmetryAxis()

    sphere_bd.mark(boundaries, 1)
    outer_bd.mark(boundaries, 2)
    sym_bd.mark(boundaries, 3)

    return boundaries

def solve_potential_flow(mesh_file, degree=1, u_inf=1.0, R=5.0):
    """Решение уравнения Лапласа для потенциала скорости"""

    mesh = Mesh()
    with XDMFFile(mesh_file) as infile:
        infile.read(mesh)

    boundaries = create_boundary_markers(mesh, R)
    V = FunctionSpace(mesh, 'P', degree)

    outer_value = Expression('u_inf * x[0]', u_inf=u_inf, degree=degree)
    bc_outer = DirichletBC(V, outer_value, boundaries, 2)
    bcs = [bc_outer]

    phi = TrialFunction(V)
    v = TestFunction(V)
    x = SpatialCoordinate(mesh)
    r = x[1]

    a = (phi.dx(0) * v.dx(0) + phi.dx(1) * v.dx(1)) * r * dx
    L = Constant(0.0) * v * dx

    phi = Function(V)
    solve(a == L, phi, bcs)

    return phi, V, mesh

def compute_velocity_field(phi, V):
    """Вычисление поля скорости"""
    degree = V.ufl_element().degree()
    W = VectorFunctionSpace(V.mesh(), 'P', degree)
    velocity = project(grad(phi), W)
    return velocity

def compute_surface_velocity(phi, V, a=1.0, u_inf=1.0):
    """Вычисление касательной скорости на поверхности шара"""
    mesh = V.mesh()
    velocity = compute_velocity_field(phi, V)

    coords = mesh.coordinates()
    theta_vals = []
    v_vals = []

    for x in coords:
        r = x[1]
        z = x[0]
        if near(r*r + z*z, a*a, 1e-2) and r > 0.05:
            try:
                vel = velocity(x)
                v_z, v_r = vel[0], vel[1]
                t_z, t_r = r / a, -z / a
                v_t = v_z * t_z + v_r * t_r

                theta = np.arccos(np.clip(-z / a, -1.0, 1.0))
                theta_vals.append(theta)
                v_vals.append(v_t)
            except:
                pass

    if len(theta_vals) == 0:
        return np.array([]), np.array([]), np.array([])

    theta = np.array(theta_vals)
    v_num = np.array(v_vals)
    v_exact = 1.5 * u_inf * np.sin(theta)

    return theta, v_num, v_exact

def plot_velocity_field(velocity, mesh, R, degree, filename):
    """Создание графика поля скорости"""
    coords = mesh.coordinates()

    # Сетка для векторов
    z_vals = np.linspace(-R+0.5, R-0.5, 25)
    r_vals = np.linspace(0.1, R-0.5, 15)
    Z, R_mesh = np.meshgrid(z_vals, r_vals)

    mask = (Z**2 + R_mesh**2) > 1.05
    Z_plot = Z[mask]
    R_plot = R_mesh[mask]

    U_z = np.zeros_like(Z_plot)
    U_r = np.zeros_like(R_plot)

    for i, (z, r) in enumerate(zip(Z_plot, R_plot)):
        try:
            vel = velocity(Point(z, r))
            U_z[i] = vel[0]
            U_r[i] = vel[1]
        except:
            pass

    # Нормализация
    mag = np.sqrt(U_z**2 + U_r**2)
    max_mag = np.max(mag)
    if max_mag > 0:
        U_z = U_z / max_mag * 0.4
        U_r = U_r / max_mag * 0.4

    fig, ax = plt.subplots(1, 1, figsize=(10, 8))

    theta = np.linspace(0, np.pi, 50)
    z_sphere = np.cos(theta)
    r_sphere = np.sin(theta)
    z_outer = R * np.cos(theta)
    r_outer = R * np.sin(theta)

    ax.quiver(Z_plot, R_plot, U_z, U_r, angles='xy', scale_units='xy', scale=1, alpha=0.6, width=0.002)
    ax.plot(z_sphere, r_sphere, 'r-', linewidth=2, label='Шар (a=1)')
    ax.plot(z_outer, r_outer, 'k--', linewidth=1, alpha=0.5, label=f'Внешняя граница (R={R})')

    ax.set_xlabel('z')
    ax.set_ylabel('r')
    ax.set_title(f'Поле скорости (R={R}, p={degree})')
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()

def run_all_calculations():
    """Запуск всех расчетов"""
    print("="*70)
    print("ЗАПУСК РАСЧЕТОВ ДЛЯ ОБТЕКАНИЯ ШАРА")
    print("="*70)

    with open(f"{MESH_DIR}/stats.json", 'r') as f:
        mesh_stats = json.load(f)

    all_results = []

    R_values = [3.0, 5.0, 7.0]
    levels = ["level1", "level2", "level3"]
    degrees = [1, 2, 3]

    total_cases = len(R_values) * len(levels) * len(degrees)
    current = 0

    for R in R_values:
        for level in levels:
            for degree in degrees:
                current += 1
                print(f"\n[{current}/{total_cases}] R={R}, {level}, p={degree}")

                mesh_file = f"{MESH_DIR}/mesh_a1.0_R{R}_{level}.xdmf"

                if not os.path.exists(mesh_file):
                    print(f"  Пропуск: сетка не найдена")
                    continue

                try:
                    phi, V, mesh = solve_potential_flow(mesh_file, degree=degree, R=R)
                    theta, v_num, v_exact = compute_surface_velocity(phi, V)

                    if len(v_num) > 0:
                        error = np.abs(v_num - v_exact)
                        l2_error = np.sqrt(np.mean(error**2))
                        max_error = np.max(error)

                        # Сохраняем данные
                        result_file = f"{RESULTS_DIR}/data_R{R}_{level}_p{degree}.npz"
                        np.savez(result_file, theta=theta, v_num=v_num, v_exact=v_exact)

                        # Создаем поле скорости для лучших случаев
                        if level == "level2" and degree == 2:
                            velocity = compute_velocity_field(phi, V)
                            vel_file = f"{RESULTS_DIR}/velocity_R{R}_{level}_p{degree}.png"
                            plot_velocity_field(velocity, mesh, R, degree, vel_file)

                        all_results.append({
                            'R': R,
                            'level': level,
                            'degree': degree,
                            'nodes': mesh.num_vertices(),
                            'cells': mesh.num_cells(),
                            'h_max': mesh.hmax(),
                            'L2_error': l2_error,
                            'max_error': max_error
                        })

                        print(f"  L2_error: {l2_error:.2e}, Max_error: {max_error:.2e}")

                except Exception as e:
                    print(f"  Ошибка: {e}")

    df = pd.DataFrame(all_results)
    df.to_csv(f"{RESULTS_DIR}/all_results.csv", index=False)

    with open(f"{RESULTS_DIR}/all_results.json", 'w') as f:
        json.dump(all_results, f, indent=2)

    print("\n" + "="*70)
    print(f"РАСЧЕТЫ ЗАВЕРШЕНЫ! Всего: {len(all_results)}")
    print("="*70)

    return df

def create_summary_plots():
    """Создание сводных графиков"""
    df = pd.read_csv(f"{RESULTS_DIR}/all_results.csv")

    # 1. Сходимость по сетке для R=5 (все p)
    plt.figure(figsize=(10, 6))
    df_R5 = df[df['R'] == 5.0]

    for p in [1, 2, 3]:
        df_p = df_R5[df_R5['degree'] == p]
        if len(df_p) > 0:
            plt.loglog(df_p['h_max'], df_p['L2_error'], 'o-', label=f'p={p}')

    plt.xlabel('h_max')
    plt.ylabel('L2 ошибка')
    plt.title('Сходимость по сетке (R=5)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig(f"{RESULTS_DIR}/convergence_R5.png", dpi=150, bbox_inches='tight')
    plt.close()

    # 2. Сравнение уровней сетки (R=5, p=2)
    plt.figure(figsize=(12, 6))

    for i, level in enumerate(['level1', 'level2', 'level3']):
        try:
            data = np.load(f"{RESULTS_DIR}/data_R5.0_{level}_p2.npz")
            theta = data['theta']
            v_num = data['v_num']

            sort_idx = np.argsort(theta)
            plt.plot(theta[sort_idx], v_num[sort_idx], 'o', markersize=3,
                    label=f'{level}', alpha=0.6)
        except:
            pass

    theta_plot = np.linspace(0, np.pi, 100)
    plt.plot(theta_plot, 1.5*np.sin(theta_plot), 'k-', linewidth=2, label='Точное')

    plt.xlabel('θ (рад)')
    plt.ylabel('u_θ / u_∞')
    plt.title('Сравнение уровней сетки (R=5, p=2)')
    plt.xlim([0, np.pi])
    plt.ylim([0, 1.6])
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig(f"{RESULTS_DIR}/mesh_level_comparison.png", dpi=150, bbox_inches='tight')
    plt.close()

    # 3. Сравнение p=1,2,3 для R=5, level2
    plt.figure(figsize=(12, 6))

    colors = ['blue', 'green', 'red']
    for i, p in enumerate([1, 2, 3]):
        try:
            data = np.load(f"{RESULTS_DIR}/data_R5.0_level2_p{p}.npz")
            theta = data['theta']
            v_num = data['v_num']

            sort_idx = np.argsort(theta)
            plt.plot(theta[sort_idx], v_num[sort_idx], 'o', color=colors[i],
                    markersize=3, label=f'p={p}', alpha=0.6)
        except:
            pass

    theta_plot = np.linspace(0, np.pi, 100)
    plt.plot(theta_plot, 1.5*np.sin(theta_plot), 'k-', linewidth=2, label='Точное')

    plt.xlabel('θ (рад)')
    plt.ylabel('u_θ / u_∞')
    plt.title('Сравнение аппроксимаций p=1,2,3 (R=5, level2)')
    plt.xlim([0, np.pi])
    plt.ylim([0, 1.6])
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.savefig(f"{RESULTS_DIR}/degree_comparison.png", dpi=150, bbox_inches='tight')
    plt.close()

    # 4. Таблица ошибок по максимальному отклонению
    pivot_table = df.pivot_table(values='max_error', index=['R', 'level'], columns='degree')
    print("\nТаблица максимальных ошибок (max_error):")
    print(pivot_table)

    print(f"\nГрафики сохранены в {RESULTS_DIR}/")

if __name__ == "__main__":
    df = run_all_calculations()
    create_summary_plots()
    print("\nГОТОВО!")