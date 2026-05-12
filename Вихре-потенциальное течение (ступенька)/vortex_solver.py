"""
Решатель задачи вихре-потенциального течения в канале с уступом.
Итерационный метод последовательных приближений для нелинейной правой части.
"""
import numpy as np
from dolfin import *


def solve_vortex_channel(mesh, boundaries, degree=1, Gamma=-2.0, H=1.0, h=1.0,
                         max_iter=100, tol=1e-6):
    """
    Итерационное решение задачи вихре-потенциального течения.
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

    L0 = Constant(0.0) * phi * dx
    psi_k = Function(V)
    print("  Вычисление начального приближения (уравнение Лапласа)...")
    solve(a == L0, psi_k, bcs)

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
        l = 1.0
        marker_vals = np.zeros(DG0.dim())
        coords_DG = DG0.tabulate_dof_coordinates()
        for i, coord in enumerate(coords_DG):
            if l <= coord[0] <= l + 1.0 and -h <= coord[1] <= 0.0:
                marker_vals[i] = 1.0

        S_init = np.sum(marker_vals) * (1.0 * h / DG0.dim())
        if S_init < 1e-14:
            S_init = 0.3 * h

        omega_init = Gamma / S_init
        print(f"  Начальная площадь вихря (оценка): {S_init:.6f}, omega = {omega_init:.6f}")

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

    omega_k = None
    S_k = None
    converged = False
    n_iter = start_k
    final_omega_func = None

    for k in range(start_k, max_iter):
        n_iter = k + 1

        psi_vals = psi_k.vector().get_local()
        marker_vals = np.zeros(DG0.dim())

        for cell in cells(mesh):
            cell_index = cell.index()
            dofs = dofmap.cell_dofs(cell_index)
            if len(dofs) > 0:
                if np.min(psi_vals[dofs]) < 0:
                    marker_vals[cell_index] = 1.0
                else:
                    marker_vals[cell_index] = 0.0

        vortex_marker = Function(DG0)
        vortex_marker.vector().set_local(marker_vals)
        vortex_marker.vector().apply("insert")

        S_k = assemble(vortex_marker * dx_custom)

        if abs(S_k) < 1e-14:
            print(f"  Итерация {k+1}: вихревая зона исчезла (S = 0). Останавливаемся.")
            omega_k = 0.0
            break

        omega_k = Gamma / S_k

        f_func = Function(DG0)
        f_func.vector().set_local(marker_vals * omega_k)
        f_func.vector().apply("insert")
        L_rhs = f_func * phi * dx
        psi_new = Function(V)
        solve(a == L_rhs, psi_new, bcs)

        diff = Function(V)
        diff.vector().set_local(psi_new.vector().get_local() - psi_k.vector().get_local())
        diff.vector().apply("insert")
        norm_diff = norm(diff, 'L2')
        norm_psi = norm(psi_new, 'L2')
        error = norm_diff / norm_psi if norm_psi > 1e-14 else norm_diff
        error_history.append(error)
        print(f"  Итерация {k+1}: S = {S_k:.6f}, omega = {omega_k:.6f}, error = {error:.3e}")

        psi_k.assign(psi_new)
        final_omega_func = f_func

        if error < tol:
            converged = True
            break

    if not converged and n_iter > 0:
        print(f"  Внимание: не сошлось за {max_iter} итераций!")

    # Характеристики вихря
    vortex_chars = compute_vortex_characteristics(psi_k, mesh)

    results = {
        "psi": psi_k,
        "omega": omega_k,
        "S": S_k if S_k is not None else 0.0,
        "n_iterations": n_iter,
        "error_history": error_history,
        "converged": converged,
        "psi_min": vortex_chars["psi_min"],
        "x_attach": vortex_chars["x_attach"],
        "y_max_vortex": vortex_chars["y_max_vortex"],
        "x_vortex_center": vortex_chars["x_vortex_center"],
        "y_vortex_center": vortex_chars["y_vortex_center"]
    }

    print(f"  Готово: {n_iter} итераций, omega = {omega_k:.6f}, S = {S_k:.6f}")
    print(f"  Характеристики вихря: psi_min = {vortex_chars['psi_min']:.4f}, "
          f"x_attach = {vortex_chars['x_attach']:.4f}, "
          f"высота = {vortex_chars['y_max_vortex']:.4f}")
    return results


def compute_vortex_characteristics(psi, mesh):
    """Вычисляет характеристики вихревой зоны."""
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