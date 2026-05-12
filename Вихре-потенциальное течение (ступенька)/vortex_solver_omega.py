"""
Решатель задачи вихре-потенциального течения с зависимостью omega(psi).
Поддерживает:
- omega = const (обычная модель)
- omega(psi) = omega0 * (1 + psi/psi_ref) (линейная)
- omega(psi) = omega0 * exp(psi/psi_ref) (экспоненциальная)
"""
import numpy as np
from dolfin import *


def solve_vortex_channel_omega(mesh, boundaries, degree=1, Gamma=-2.0, H=1.0, h=1.0,
                               omega_model="const", psi_ref=None,
                               max_iter=100, tol=1e-6):
    """
    Итерационное решение с заданной зависимостью omega(psi).
    """
    V = FunctionSpace(mesh, 'P', degree)
    psi = TrialFunction(V)
    phi = TestFunction(V)

    bc_G1 = DirichletBC(V, Constant(0.0), boundaries, 1)
    bc_G2 = DirichletBC(V, Constant(H), boundaries, 2)
    inflow_expr = Expression('H * x[1]', H=H, degree=degree)
    bc_G3 = DirichletBC(V, inflow_expr, boundaries, 3)
    bcs = [bc_G1, bc_G2, bc_G3]

    a = dot(grad(psi), grad(phi)) * dx
    dx_custom = Measure("dx", domain=mesh)
    DG0 = FunctionSpace(mesh, 'DG', 0)

    # Начальное приближение: Лаплас
    L0 = Constant(0.0) * phi * dx
    psi_k = Function(V)
    print("  Вычисление начального приближения (уравнение Лапласа)...")
    solve(a == L0, psi_k, bcs)

    # Проверка наличия вихря
    psi_vals = psi_k.vector().get_local()
    dofmap = V.dofmap()
    has_vortex = False
    for c in cells(mesh):
        dofs = dofmap.cell_dofs(c.index())
        if len(dofs) > 0 and np.min(psi_vals[dofs]) < 0:
            has_vortex = True
            break

    if not has_vortex:
        print("  В начальном приближении вихря нет — задаём принудительную вихревую зону.")
        marker_vals = np.zeros(DG0.dim())
        coords_DG = DG0.tabulate_dof_coordinates()
        for i, coord in enumerate(coords_DG):
            if 1.0 <= coord[0] <= 2.0 and -h <= coord[1] <= 0.0:
                marker_vals[i] = 1.0

        S_init = np.sum(marker_vals) * (1.0 * h / DG0.dim())
        if S_init < 1e-14:
            S_init = 0.3 * h

        omega_init = Gamma / S_init
        print(f"  Начальная площадь (оценка): {S_init:.6f}, omega = {omega_init:.6f}")

        f_func = Function(DG0)
        f_func.vector().set_local(marker_vals * omega_init)
        f_func.vector().apply("insert")
        L_rhs = f_func * phi * dx
        psi_new = Function(V)
        solve(a == L_rhs, psi_new, bcs)
        psi_k.assign(psi_new)
        error_history = [1.0]
        start_k = 1
    else:
        print("  Вихрь обнаружен в начальном приближении.")
        error_history = []
        start_k = 0

    # Итерационный процесс
    converged = False
    n_iter = start_k
    S_k = None
    omega_scale = 0.0
    psi_ref_val = 0.0

    for k in range(start_k, max_iter):
        n_iter = k + 1

        # Шаг 1: Определяем вихревую зону (psi < 0)
        psi_vals = psi_k.vector().get_local()
        marker_vals = np.zeros(DG0.dim())

        for cell in cells(mesh):
            cell_index = cell.index()
            dofs = dofmap.cell_dofs(cell_index)
            if len(dofs) > 0 and np.min(psi_vals[dofs]) < 0:
                marker_vals[cell_index] = 1.0

        vortex_marker = Function(DG0)
        vortex_marker.vector().set_local(marker_vals)
        vortex_marker.vector().apply("insert")

        # Шаг 2: Площадь вихревой зоны
        S_k = assemble(vortex_marker * dx_custom)
        if abs(S_k) < 1e-14:
            print(f"  Итерация {k+1}: вихревая зона исчезла (S = 0).")
            break

        # Шаг 3: Вычисляем omega(psi)
        # Находим минимальное psi среди вихревых элементов
        psi_min_vals = []
        for cell in cells(mesh):
            cell_index = cell.index()
            if marker_vals[cell_index] > 0:
                dofs = dofmap.cell_dofs(cell_index)
                if len(dofs) > 0:
                    psi_min_vals.append(np.min(psi_vals[dofs]))

        psi_min = min(psi_min_vals) if psi_min_vals else 0.0

        if psi_ref is None:
            psi_ref_val = abs(psi_min) if abs(psi_min) > 1e-14 else 0.1
        else:
            psi_ref_val = psi_ref

        # Вычисляем omega в каждом вихревом элементе
        coords_DG = DG0.tabulate_dof_coordinates()
        omega_vals = np.zeros(DG0.dim())

        # Для вычисления psi в центрах элементов интерполируем psi_k
        V_CG = FunctionSpace(mesh, 'P', degree)
        psi_interp = interpolate(psi_k, V_CG)

        for i in range(DG0.dim()):
            if marker_vals[i] > 0:
                psi_i = psi_interp(coords_DG[i])
                # Значение psi_i отрицательно, psi_ref_val > 0
                if omega_model == "const":
                    omega_vals[i] = 1.0
                elif omega_model == "linear":
                    # omega = omega0 * (1 - alpha * |psi|/psi_ref)
                    # где alpha и psi_ref — фиксированные параметры
                    alpha = 0.5
                    psi_ref_fixed = 0.3
                    omega_vals[i] = max(1.0 - alpha * abs(psi_i) / psi_ref_fixed, 0.2)
                elif omega_model == "exp":
                    # omega = omega0 * exp(psi/psi_ref)
                    omega_vals[i] = np.exp(0.5 * psi_i / psi_ref_val)
                else:
                    raise ValueError(f"Неизвестная модель: {omega_model}")

        # Нормируем так, чтобы интеграл по вихревой зоне равнялся Gamma
        omega_func = Function(DG0)
        omega_func.vector().set_local(omega_vals)
        omega_func.vector().apply("insert")

        integral_omega = assemble(omega_func * dx_custom)

        if abs(integral_omega) < 1e-14:
            print(f"  Итерация {k+1}: нулевой интеграл omega.")
            break

        omega_scale = Gamma / integral_omega
        omega_func.vector().set_local(omega_vals * omega_scale)
        omega_func.vector().apply("insert")

        # Шаг 4-5: Правая часть и решение
        L_rhs = omega_func * phi * dx
        psi_new = Function(V)
        solve(a == L_rhs, psi_new, bcs)

        # Шаг 6: Сходимость
        diff = Function(V)
        diff.vector().set_local(psi_new.vector().get_local() - psi_k.vector().get_local())
        diff.vector().apply("insert")
        norm_diff = norm(diff, 'L2')
        norm_psi = norm(psi_new, 'L2')
        error = norm_diff / norm_psi if norm_psi > 1e-14 else norm_diff
        error_history.append(error)
        print(f"  Итерация {k+1}: S = {S_k:.6f}, integral = {integral_omega:.6f}, "
              f"scale = {omega_scale:.6f}, error = {error:.3e}")

        psi_k.assign(psi_new)

        if error < tol:
            converged = True
            break

    if not converged and n_iter > 0:
        print(f"  Внимание: не сошлось за {max_iter} итераций!")

    results = {
        "psi": psi_k,
        "omega_scale": omega_scale,
        "S": S_k if S_k is not None else 0.0,
        "n_iterations": n_iter,
        "error_history": error_history,
        "converged": converged,
        "omega_model": omega_model,
        "psi_ref": psi_ref_val
    }

    print(f"  Готово: {n_iter} итераций, модель={omega_model}, S={S_k:.6f}")
    return results