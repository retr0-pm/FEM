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

def plot_potential_field(phi, mesh, R, degree, filename):
    """Создание цветного графика потенциала скорости (только вне шара)"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))

    coords = mesh.coordinates()
    z = coords[:, 0]
    r = coords[:, 1]

    # Маскируем точки внутри шара
    mask = (z**2 + r**2) >= 1.0

    z_plot = z[mask]
    r_plot = r[mask]

    # Значения потенциала только для точек вне шара
    phi_vals_all = phi.compute_vertex_values(mesh)
    phi_vals = phi_vals_all[mask]

    import matplotlib.tri as tri
    triang = tri.Triangulation(z_plot, r_plot)

    levels = 50
    contour = ax.tricontourf(triang, phi_vals, levels=levels, cmap='RdYlBu_r', extend='both')
    plt.colorbar(contour, ax=ax, label='Потенциал φ', shrink=0.8)

    # Контур шара (закрашенный)
    theta = np.linspace(0, np.pi, 50)
    z_sphere = np.cos(theta)
    r_sphere = np.sin(theta)
    ax.fill(z_sphere, r_sphere, 'white', edgecolor='black', linewidth=2, label='Шар (a=1)')

    # Внешняя граница
    z_outer = R * np.cos(theta)
    r_outer = R * np.sin(theta)
    ax.plot(z_outer, r_outer, 'k--', linewidth=1, alpha=0.5, label=f'Граница (R={R})')

    ax.set_xlabel('z', fontsize=12)
    ax.set_ylabel('r', fontsize=12)
    ax.set_title(f'Потенциал скорости φ (R={R}, p={degree})', fontsize=14)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()

def plot_velocity_magnitude(velocity, mesh, R, degree, u_inf=1.0, filename="velocity_mag.png"):
    """Создание цветного графика модуля скорости (только вне шара)"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))

    coords = mesh.coordinates()
    z = coords[:, 0]
    r = coords[:, 1]

    # Маскируем точки внутри шара
    mask = (z**2 + r**2) >= 1.0

    z_plot = z[mask]
    r_plot = r[mask]

    # Вычисление модуля скорости только вне шара
    V_mag = np.zeros(len(z_plot))
    for i, (zi, ri) in enumerate(zip(z_plot, r_plot)):
        try:
            vel = velocity(Point(zi, ri))
            V_mag[i] = np.sqrt(vel[0]**2 + vel[1]**2) / u_inf
        except:
            V_mag[i] = 0

    import matplotlib.tri as tri
    triang = tri.Triangulation(z_plot, r_plot)

    levels = 50
    contour = ax.tricontourf(triang, V_mag, levels=levels, cmap='viridis', vmin=0, vmax=1.8, extend='both')
    plt.colorbar(contour, ax=ax, label='|u| / u_∞', shrink=0.8)

    # Контур шара (закрашенный)
    theta = np.linspace(0, np.pi, 50)
    z_sphere = np.cos(theta)
    r_sphere = np.sin(theta)
    ax.fill(z_sphere, r_sphere, 'white', edgecolor='red', linewidth=2, label='Шар (a=1)')

    # Внешняя граница
    z_outer = R * np.cos(theta)
    r_outer = R * np.sin(theta)
    ax.plot(z_outer, r_outer, 'k--', linewidth=1, alpha=0.5, label=f'Граница (R={R})')

    ax.set_xlabel('z', fontsize=12)
    ax.set_ylabel('r', fontsize=12)
    ax.set_title(f'Модуль скорости |u|/u_∞ (R={R}, p={degree})', fontsize=14)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()

def plot_velocity_field(velocity, mesh, R, degree, filename):
    """Создание графика векторного поля скорости"""
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

    # Закрашенный шар
    ax.fill(z_sphere, r_sphere, 'white', edgecolor='red', linewidth=2, label='Шар (a=1)')
    ax.plot(z_outer, r_outer, 'k--', linewidth=1, alpha=0.5, label=f'Граница (R={R})')

    ax.set_xlabel('z', fontsize=12)
    ax.set_ylabel('r', fontsize=12)
    ax.set_title(f'Поле скорости (R={R}, p={degree})', fontsize=14)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()

def plot_streamlines(phi, mesh, R, degree, filename):
    """Создание графика линий тока (только вне шара)"""
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))

    # Сетка для линий тока
    z_vals = np.linspace(-R, R, 100)
    r_vals = np.linspace(0, R, 50)
    Z, R_mesh = np.meshgrid(z_vals, r_vals)

    # Маскируем область внутри шара
    mask = (Z**2 + R_mesh**2) >= 1.0

    # Значения потенциала на сетке
    PHI = np.full_like(Z, np.nan)
    for i in range(Z.shape[0]):
        for j in range(Z.shape[1]):
            if mask[i, j]:
                try:
                    PHI[i, j] = phi(Point(Z[i, j], R_mesh[i, j]))
                except:
                    pass

    # Эквипотенциали
    levels = 20
    contour = ax.contour(Z, R_mesh, PHI, levels=levels, colors='blue', alpha=0.6, linewidths=1)
    ax.clabel(contour, inline=True, fontsize=8, fmt='%.2f')

    # Контур шара (закрашенный)
    theta = np.linspace(0, np.pi, 50)
    z_sphere = np.cos(theta)
    r_sphere = np.sin(theta)
    ax.fill(z_sphere, r_sphere, 'lightgray', edgecolor='black', linewidth=2, label='Шар (a=1)')

    # Внешняя граница
    z_outer = R * np.cos(theta)
    r_outer = R * np.sin(theta)
    ax.plot(z_outer, r_outer, 'k--', linewidth=1, alpha=0.5, label=f'Граница (R={R})')

    ax.set_xlabel('z', fontsize=12)
    ax.set_ylabel('r', fontsize=12)
    ax.set_title(f'Эквипотенциали / Линии тока (R={R}, p={degree})', fontsize=14)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.legend()

    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()

def check_potential_properties(phi, mesh, R=5.0):
    """Проверка свойств потенциала (для отладки)"""
    print("\n=== Проверка потенциала ===")

    phi_min = phi.vector().min()
    phi_max = phi.vector().max()
    print(f"φ ∈ [{phi_min:.3f}, {phi_max:.3f}]")
    print(f"Ожидаемый диапазон: [{-R:.3f}, {R:.3f}]")

    test_points = [(2.0, 1.0), (3.0, 2.0), (1.5, 1.5)]
    print("\nПроверка антисимметрии φ(-z, r) = -φ(z, r):")
    for z, r in test_points:
        try:
            val_plus = phi(Point(z, r))
            val_minus = phi(Point(-z, r))
            print(f"  z={z:.1f}, r={r:.1f}: φ={val_plus:.3f}, φ(-z)={val_minus:.3f}, сумма={val_plus+val_minus:.2e}")
        except:
            pass

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

                    # Проверка потенциала для одного случая
                    if R == 5.0 and level == "level2" and degree == 2:
                        check_potential_properties(phi, mesh, R)

                    theta, v_num, v_exact = compute_surface_velocity(phi, V)

                    if len(v_num) > 0:
                        error = np.abs(v_num - v_exact)
                        l2_error = np.sqrt(np.mean(error**2))
                        max_error = np.max(error)

                        # Сохраняем данные
                        result_file = f"{RESULTS_DIR}/data_R{R}_{level}_p{degree}.npz"
                        np.savez(result_file, theta=theta, v_num=v_num, v_exact=v_exact)

                        # Создаем графики
                        velocity = compute_velocity_field(phi, V)

                        pot_file = f"{RESULTS_DIR}/potential_R{R}_{level}_p{degree}.png"
                        plot_potential_field(phi, mesh, R, degree, pot_file)

                        mag_file = f"{RESULTS_DIR}/velocity_mag_R{R}_{level}_p{degree}.png"
                        plot_velocity_magnitude(velocity, mesh, R, degree, filename=mag_file)

                        vel_file = f"{RESULTS_DIR}/velocity_field_R{R}_{level}_p{degree}.png"
                        plot_velocity_field(velocity, mesh, R, degree, vel_file)

                        str_file = f"{RESULTS_DIR}/streamlines_R{R}_{level}_p{degree}.png"
                        plot_streamlines(phi, mesh, R, degree, str_file)

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

    # 1. Сходимость по сетке для R=5
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

    print(f"\nГрафики сохранены в {RESULTS_DIR}/")

if __name__ == "__main__":
    df = run_all_calculations()
    create_summary_plots()
    print("\nГОТОВО!")