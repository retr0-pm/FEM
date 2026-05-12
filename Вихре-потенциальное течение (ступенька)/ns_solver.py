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

    # Площадь вихревой зоны (psi < 0)
    S_vortex = 0.0
    dofmap_psi = psi.function_space().dofmap()
    psi_vals_all = psi.vector().get_local()

    for cell in cells(mesh):
        dofs = dofmap_psi.cell_dofs(cell.index())
        if len(dofs) > 0:
            if np.min(psi_vals_all[dofs]) < 0:
                S_vortex += cell.volume()

    # Характеристики вихря
    vortex_chars = compute_vortex_characteristics_ns(psi, mesh)

    print(f"  Площадь вихревой зоны: S = {S_vortex:.6f}")
    print(f"  Характеристики вихря: psi_min = {vortex_chars['psi_min']:.4f}, "
          f"x_attach = {vortex_chars['x_attach']:.4f}, "
          f"высота = {vortex_chars['y_max_vortex']:.4f}")

    return {
        "velocity": u_final,
        "pressure": p_final,
        "psi": psi,
        "Re": Re,
        "S_vortex": S_vortex,
        "n_iterations": n_iter,
        "error_history": error_history,
        "converged": converged,
        "psi_min": vortex_chars["psi_min"],
        "x_attach": vortex_chars["x_attach"],
        "y_max_vortex": vortex_chars["y_max_vortex"],
        "x_vortex_center": vortex_chars["x_vortex_center"],
        "y_vortex_center": vortex_chars["y_vortex_center"]
    }


def compute_stream_function(u, mesh):
    """
    Вычисляет функцию тока psi из поля скорости u
    путём интегрирования u1 по вертикали.
    """
    V_psi = FunctionSpace(mesh, 'P', 2)
    psi_func = Function(V_psi)

    coords = V_psi.tabulate_dof_coordinates()
    psi_vals = np.zeros(len(coords))

    x2_min = mesh.coordinates()[:, 1].min()
    l = 1.0

    for i, (x1, x2) in enumerate(coords):
        if x1 <= l:
            x2_bottom = 0.0
        else:
            x2_bottom = x2_min

        n_pts = 100
        xi = np.linspace(x2_bottom, x2, n_pts)
        integral = 0.0

        for j in range(n_pts - 1):
            u_a = u(x1, xi[j])[0]
            u_b = u(x1, xi[j+1])[0]
            integral += 0.5 * (u_a + u_b) * (xi[j+1] - xi[j])

        psi_vals[i] = integral

    psi_func.vector().set_local(psi_vals)
    psi_func.vector().apply("insert")

    return psi_func


def compute_vortex_characteristics_ns(psi, mesh):
    """Вычисляет характеристики вихревой зоны для NS."""
    psi_verts = psi.compute_vertex_values(mesh)
    coords = mesh.coordinates()

    psi_min = np.min(psi_verts)
    idx_min = np.argmin(psi_verts)
    x_vortex_center = coords[idx_min, 0]
    y_vortex_center = coords[idx_min, 1]

    L, l = 4.0, 1.0
    x2_bottom = coords[:, 1].min()

    bottom_pts = []
    for i, (x1, x2) in enumerate(coords):
        if x1 >= l and near(x2, x2_bottom, 1e-4):
            bottom_pts.append((x1, psi_verts[i]))
    bottom_pts.sort()

    x_attach = l
    for j in range(len(bottom_pts) - 1):
        x1_a, psi_a = bottom_pts[j]
        x1_b, psi_b = bottom_pts[j + 1]
        if psi_a * psi_b <= 0 and x1_a > l:
            if abs(psi_b - psi_a) > 1e-14:
                x_attach = x1_a - psi_a * (x1_b - x1_a) / (psi_b - psi_a)
            else:
                x_attach = (x1_a + x1_b) / 2
            break
        elif psi_a > 0 and psi_b > 0 and x1_a > l:
            x_attach = x1_a
            break

    vortex_pts = [(x1, x2) for i, (x1, x2) in enumerate(coords) if psi_verts[i] < 0]
    y_max_vortex = max(pt[1] for pt in vortex_pts) if vortex_pts else x2_bottom

    return {
        "psi_min": psi_min,
        "x_attach": x_attach,
        "y_max_vortex": y_max_vortex,
        "x_vortex_center": x_vortex_center,
        "y_vortex_center": y_vortex_center
    }