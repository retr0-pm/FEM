"""
Решатель стационарных уравнений Навье-Стокса для течения в канале с уступом.
Метод Пикара (линеаризованные уравнения) с итерациями.
"""
import numpy as np
from dolfin import *


def solve_navier_stokes_channel(mesh, boundaries, Re=100.0, H=1.0,
                                max_iter=50, tol=1e-6):
    """
    Решение стационарных уравнений Навье-Стокса.
    """
    nu = Constant(H / Re)

    # Пространства
    V = VectorFunctionSpace(mesh, 'P', 2)
    Q = FunctionSpace(mesh, 'P', 1)

    # Смешанное пространство
    W_elem = MixedElement([V.ufl_element(), Q.ufl_element()])
    W = FunctionSpace(mesh, W_elem)

    # Пробные и тестовые функции
    u, p = TrialFunctions(W)
    v, q = TestFunctions(W)

    # Начальное приближение
    w = Function(W)
    u_k = Function(V)

    # --- Краевые условия ---
    zero_vec = Constant((0.0, 0.0))
    bc_walls_1 = DirichletBC(W.sub(0), zero_vec, boundaries, 1)
    bc_walls_2 = DirichletBC(W.sub(0), zero_vec, boundaries, 2)

    # Вход (Gamma3): параболический профиль Пуазейля
    inflow_ux = Expression('6.0 * x[1]/H * (1.0 - x[1]/H)', H=H, degree=3)
    inflow_uy = Constant(0.0)
    inflow_func = Function(V)
    inflow_func.assign(project(as_vector((inflow_ux, inflow_uy)), V))
    bc_inflow = DirichletBC(W.sub(0), inflow_func, boundaries, 3)

    bcs = [bc_walls_1, bc_walls_2, bc_inflow]

    # --- Вариационная форма (Пикар) ---
    F = (nu * inner(grad(u), grad(v)) * dx
         + inner(grad(u) * u_k, v) * dx
         - p * div(v) * dx
         - q * div(u) * dx)

    a, L = lhs(F), rhs(F)

    # Начальное приближение
    w.vector()[:] = 0.0

    # --- Итерации Пикара ---
    error_history = []
    converged = False
    n_iter = 0

    for k in range(max_iter):
        n_iter = k + 1

        solve(a == L, w, bcs,
              solver_parameters={"linear_solver": "mumps"})

        u_new, p_new = w.split(deepcopy=True)

        if k > 0:
            diff_u = Function(V)
            diff_u.vector().set_local(
                u_new.vector().get_local() - u_old.vector().get_local())
            diff_u.vector().apply("insert")

            norm_diff = norm(diff_u, 'L2')
            norm_u = norm(u_new, 'L2')
            error = norm_diff / norm_u if norm_u > 1e-14 else norm_diff
            error_history.append(error)
            print(f"  Итерация Пикара {k+1}: error = {error:.3e}")

            if error < tol:
                converged = True
                break

        u_old = Function(V)
        u_old.assign(u_new)
        u_k.assign(u_new)

    if not converged and n_iter > 0:
        print(f"  Внимание: не сошлось за {max_iter} итераций!")

    u_final, p_final = w.split(deepcopy=True)

    # Функция тока
    psi = compute_stream_function(u_final, mesh)

    # Площадь вихревой зоны
    S_vortex = 0.0
    dofmap_psi = psi.function_space().dofmap()
    psi_vals_all = psi.vector().get_local()

    for cell in cells(mesh):
        dofs = dofmap_psi.cell_dofs(cell.index())
        if len(dofs) > 0:
            if np.min(psi_vals_all[dofs]) < 0:
                S_vortex += cell.volume()

    print(f"  Площадь вихревой зоны: S = {S_vortex:.6f}")

    return {
        "velocity": u_final,
        "pressure": p_final,
        "psi": psi,
        "Re": Re,
        "S_vortex": S_vortex,
        "n_iterations": n_iter,
        "error_history": error_history,
        "converged": converged
    }


def compute_stream_function(u, mesh):
    """
    Вычисляет функцию тока psi из поля скорости u
    путём интегрирования u1 по вертикали.

    psi(x1, x2) = int_{x2_bottom}^{x2} u1(x1, xi) dxi + psi_bottom(x1)
    """
    V_psi = FunctionSpace(mesh, 'P', 2)
    psi_func = Function(V_psi)

    # Получаем координаты и значения скорости
    coords = V_psi.tabulate_dof_coordinates()
    u_vals = np.array([u(coord) for coord in coords])

    # Находим границы
    x2_min = mesh.coordinates()[:, 1].min()
    l = 1.0  # длина уступа (геометрический параметр)

    # Для каждой точки интегрируем u1 от нижней стенки до текущей высоты
    psi_vals = np.zeros(len(coords))

    for i, (x1, x2) in enumerate(coords):
        # Нижняя граница для данного x1
        if x1 <= l:
            x2_bottom = 0.0  # до уступа: нижняя стенка на x2 = 0
        else:
            x2_bottom = x2_min  # после уступа: нижняя стенка на x2 = -h

        # Интегрируем u1 по вертикали от x2_bottom до x2
        n_pts = 50  # точек для численного интегрирования
        xi_vals = np.linspace(x2_bottom, x2, n_pts)
        dx = (x2 - x2_bottom) / (n_pts - 1)

        integral = 0.0
        for xi in xi_vals:
            u1_val = u(np.array([x1, xi]))[0]
            integral += u1_val * dx

        # Трапецеидальное правило (уточнение концов)
        u1_start = u(np.array([x1, x2_bottom]))[0]
        u1_end = u(np.array([x1, x2]))[0]
        integral = integral - 0.5 * dx * (u1_start + u1_end) + 0.5 * dx * (u1_start + u1_end)
        # Проще: используем правило трапеций явно
        integral = 0.0
        for j in range(n_pts - 1):
            xi_a = xi_vals[j]
            xi_b = xi_vals[j + 1]
            u_a = u(np.array([x1, xi_a]))[0]
            u_b = u(np.array([x1, xi_b]))[0]
            integral += 0.5 * (u_a + u_b) * (xi_b - xi_a)

        psi_vals[i] = integral

    psi_func.vector().set_local(psi_vals)
    psi_func.vector().apply("insert")

    return psi_func