"""
Решатель задачи вихре-потенциального течения в канале с уступом.
Итерационный метод последовательных приближений для нелинейной правой части.
"""
import numpy as np
from dolfin import *


def solve_vortex_channel(mesh, boundaries, degree=1, Gamma=-2.0, H=1.0,
                         max_iter=100, tol=1e-6):
    """
    Итерационное решение задачи вихре-потенциального течения.

    Параметры:
        mesh: расчётная сетка (dolfin.Mesh)
        boundaries: маркеры границ (MeshFunction)
        degree: степень полиномов (1, 2, 3)
        Gamma: циркуляция (по умолчанию -2)
        H: высота канала (по умолчанию 1.0)
        max_iter: максимальное число итераций
        tol: допуск сходимости

    Возвращает:
        dict с результатами: psi, omega_final, S_final, iterations, error_history
    """
    # Функциональное пространство
    V = FunctionSpace(mesh, 'P', degree)

    # Пробная и тестовая функции
    psi = TrialFunction(V)
    phi = TestFunction(V)

    # --- Краевые условия ---
    bc_G1 = DirichletBC(V, Constant(0.0), boundaries, 1)
    bc_G2 = DirichletBC(V, Constant(H), boundaries, 2)
    inflow_expr = Expression('H * x[1]', H=H, degree=degree)
    bc_G3 = DirichletBC(V, inflow_expr, boundaries, 3)
    bcs = [bc_G1, bc_G2, bc_G3]

    # --- Вариационная форма ---
    a = dot(grad(psi), grad(phi)) * dx
    dx_custom = Measure("dx", domain=mesh)
    DG0 = FunctionSpace(mesh, 'DG', 0)

    # --- Начальное приближение: уравнение Лапласа ---
    L0 = Constant(0.0) * phi * dx
    psi_k = Function(V)
    print("  Вычисление начального приближения (уравнение Лапласа)...")
    solve(a == L0, psi_k, bcs)

    # Проверяем, есть ли вихрь (psi < 0) в начальном приближении
    psi_vals = psi_k.vector().get_local()
    dofmap = V.dofmap()
    has_vortex = False
    for cell in cells(mesh):
        dofs = dofmap.cell_dofs(cell.index())
        if len(dofs) > 0 and np.min(psi_vals[dofs]) < 0:
            has_vortex = True
            break

    if not has_vortex:
        print("  В начальном приближении вихря нет — задаём принудительную вихревую зону за уступом.")
        # Принудительная вихревая зона: прямоугольник x1 in [1.0, 2.0], x2 in [-1.0, 0.0]
        marker_vals = np.zeros(DG0.dim())
        coords_DG = DG0.tabulate_dof_coordinates()
        for i, coord in enumerate(coords_DG):
            if 1.0 <= coord[0] <= 2.0 and -1.0 <= coord[1] <= 0.0:
                marker_vals[i] = 1.0

        S_init = np.sum(marker_vals) * (2.0 * 1.0 / DG0.dim())  # грубая оценка площади
        if S_init < 1e-14:
            S_init = 0.3  # запасной вариант

        omega_init = Gamma / S_init
        print(f"  Начальная площадь вихря (оценка): {S_init:.6f}, omega = {omega_init:.6f}")

        # Первая итерация с принудительной зоной
        f_func = Function(DG0)
        f_func.vector().set_local(marker_vals * omega_init)
        f_func.vector().apply("insert")
        L_rhs = f_func * phi * dx
        psi_new = Function(V)
        solve(a == L_rhs, psi_new, bcs)
        psi_k.assign(psi_new)
        error_history = [1.0]  # фиктивная первая ошибка
        start_k = 1
    else:
        print("  Вихрь обнаружен в начальном приближении.")
        error_history = []
        start_k = 0

    # --- Итерационный процесс ---
    omega_k = None
    S_k = None
    converged = False
    n_iter = start_k

    for k in range(start_k, max_iter):
        n_iter = k + 1

        # Шаг 1: Определяем вихревую зону
        psi_vals = psi_k.vector().get_local()
        marker_vals = np.zeros(DG0.dim())

        for cell in cells(mesh):
            cell_index = cell.index()
            dofs = dofmap.cell_dofs(cell_index)
            if len(dofs) > 0:
                psi_min = np.min(psi_vals[dofs])
                if psi_min < 0:
                    marker_vals[cell_index] = 1.0
                else:
                    marker_vals[cell_index] = 0.0

        vortex_marker = Function(DG0)
        vortex_marker.vector().set_local(marker_vals)
        vortex_marker.vector().apply("insert")

        # Шаг 2: Площадь вихревой зоны
        S_k = assemble(vortex_marker * dx_custom)

        if abs(S_k) < 1e-14:
            print(f"  Итерация {k+1}: вихревая зона исчезла (S = 0). Останавливаемся.")
            omega_k = 0.0
            break

        # Шаг 3: Завихрённость
        omega_k = Gamma / S_k

        # Шаг 4-5: Правая часть и решение
        f_func = Function(DG0)
        f_func.vector().set_local(marker_vals * omega_k)
        f_func.vector().apply("insert")
        L_rhs = f_func * phi * dx
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
        print(f"  Итерация {k+1}: S = {S_k:.6f}, omega = {omega_k:.6f}, error = {error:.3e}")

        psi_k.assign(psi_new)

        if error < tol:
            converged = True
            break

    if not converged and n_iter > 0:
        print(f"  Внимание: не сошлось за {max_iter} итераций!")

    results = {
        "psi": psi_k,
        "omega": omega_k,
        "S": S_k if S_k is not None else 0.0,
        "n_iterations": n_iter,
        "error_history": error_history,
        "converged": converged
    }

    print(f"  Готово: {n_iter} итераций, omega = {omega_k:.6f}, S = {S_k:.6f}")
    return results