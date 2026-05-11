import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Результаты расчетов", layout="wide")

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")

menu = st.sidebar.radio('***',
                        ("Сводная таблица",
                         "Верификация по сетке",
                         "Влияние циркуляции",
                         "Влияние высоты уступа",
                         "Поля функции тока",
                         "Сходимость итераций",
                         "Код решателя",
                         "Код расчётов",
                         "Выводы")
                        )

# Загрузка данных
csv_file = os.path.join(RESULTS_DIR, "all_results.csv")
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
else:
    df = None

if menu == "Сводная таблица":
    st.markdown("##### Сводная таблица результатов")

    if df is not None:
        st.markdown(f"**Всего расчётов: {len(df)}**")

        # Фильтры
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            h_filter = st.selectbox("Высота уступа $h$",
                                    ["Все"] + sorted(df['h'].unique().tolist()))
        with col2:
            level_filter = st.selectbox("Сетка",
                                        ["Все"] + sorted(df['level'].unique().tolist()))
        with col3:
            p_filter = st.selectbox("Степень $p$",
                                    ["Все"] + sorted(df['degree'].unique().tolist()))
        with col4:
            gamma_filter = st.selectbox("$\Gamma$",
                                        ["Все"] + sorted(df['Gamma'].unique().tolist()))

        df_filtered = df.copy()
        if h_filter != "Все":
            df_filtered = df_filtered[df_filtered['h'] == float(h_filter)]
        if level_filter != "Все":
            df_filtered = df_filtered[df_filtered['level'] == level_filter]
        if p_filter != "Все":
            df_filtered = df_filtered[df_filtered['degree'] == int(p_filter)]
        if gamma_filter != "Все":
            df_filtered = df_filtered[df_filtered['Gamma'] == float(gamma_filter)]

        st.markdown(f"**Показано: {len(df_filtered)} расчётов**")

        df_display = df_filtered.copy()
        df_display['omega'] = df_display['omega'].apply(lambda x: f"{x:.4f}")
        df_display['S'] = df_display['S'].apply(lambda x: f"{x:.4f}")
        df_display = df_display.rename(columns={
            'h': 'h',
            'Gamma': 'Γ',
            'level': 'Сетка',
            'degree': 'p',
            'nodes': 'Узлы',
            'cells': 'Ячейки',
            'omega': 'ω',
            'S': 'S',
            'n_iterations': 'Итер.',
            'converged': 'Сошёлся'
        })
        st.dataframe(
            df_display[['h', 'Γ', 'Сетка', 'p', 'Узлы', 'Ячейки', 'ω', 'S', 'Итер.', 'Сошёлся']],
            use_container_width=True, hide_index=True
        )
    else:
        st.warning("Результаты не найдены. Запустите `python run_calculations.py`")

elif menu == "Верификация по сетке":
    st.markdown("##### Верификация численных результатов")

    if df is not None:
        col1, col2 = st.columns(2)
        with col1:
            h_sel = st.selectbox("Высота уступа $h$",
                                 sorted(df['h'].unique()),
                                 index=1)  # h=1.0 по умолчанию
        with col2:
            gamma_sel = st.selectbox("Циркуляция $\Gamma$",
                                     sorted(df['Gamma'].unique()),
                                     index=1)  # Gamma=-2 по умолчанию

        df_base = df[(df['h'] == h_sel) &
                     (df['Gamma'] == gamma_sel) &
                     (df['degree'] == 2)]

        if len(df_base) > 0:
            st.markdown(rf"""
            **Сходимость по сетке ($h={h_sel}$, $\Gamma={gamma_sel}$, $p=2$)**

            Сравнение значений завихрённости $\omega$ на последовательности сгущающихся сеток.
            """)

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Таблица:**")
                df_conv = df_base[['level', 'nodes', 'cells', 'omega', 'S', 'n_iterations']].copy()
                df_conv['omega'] = df_conv['omega'].apply(lambda x: f"{x:.4f}")
                df_conv['S'] = df_conv['S'].apply(lambda x: f"{x:.4f}")
                df_conv = df_conv.rename(columns={
                    'level': 'Сетка',
                    'nodes': 'Узлы',
                    'cells': 'Ячейки',
                    'omega': 'ω',
                    'S': 'S',
                    'n_iterations': 'Итераций'
                })
                st.dataframe(df_conv, use_container_width=True, hide_index=True)

            with col2:
                if len(df_base) >= 2:
                    st.markdown("**График сходимости:**")
                    h_mesh = [1/(df_base.iloc[i]['cells'])**(1/2) for i in range(len(df_base))]
                    omega_vals = df_base['omega'].values

                    fig, ax = plt.subplots(figsize=(6, 4))
                    ax.plot(h_mesh, omega_vals, 'o-', markersize=8, linewidth=2)
                    ax.set_xlabel('Характерный размер ячейки $h$')
                    ax.set_ylabel(r'$\omega$')
                    ax.set_title('Зависимость $\omega$ от размера сетки')
                    ax.grid(True)
                    fig.tight_layout()
                    st.pyplot(fig)

                    if len(df_base) >= 3:
                        omega_ref = df_base[df_base['level'] == 'level3']['omega'].values[0]
                        st.markdown(f"**Эталонное значение (level3):** $\omega = {omega_ref:.4f}$")

                        if 'level2' in df_base['level'].values:
                            rel_diff_2 = abs(df_base[df_base['level'] == 'level2']['omega'].values[0] - omega_ref) / abs(omega_ref)
                            st.markdown(f"- level2: отличие {rel_diff_2*100:.1f}%")
                        if 'level1' in df_base['level'].values:
                            rel_diff_1 = abs(df_base[df_base['level'] == 'level1']['omega'].values[0] - omega_ref) / abs(omega_ref)
                            st.markdown(f"- level1: отличие {rel_diff_1*100:.1f}%")
        else:
            st.warning("Нет данных для выбранных параметров.")
    else:
        st.warning("Результаты не найдены.")

elif menu == "Влияние циркуляции":
    st.markdown("##### Влияние циркуляции на вихревую структуру")

    if df is not None:
        col1, col2 = st.columns(2)
        with col1:
            h_sel = st.selectbox("Высота уступа $h$",
                                 sorted(df['h'].unique()),
                                 index=1,
                                 key='gamma_h')
        with col2:
            level_sel = st.selectbox("Сетка",
                                     sorted(df['level'].unique()),
                                     index=1,  # level2
                                     key='gamma_level')

        df_gamma = df[(df['h'] == h_sel) &
                      (df['level'] == level_sel) &
                      (df['degree'] == 2)]
        df_gamma = df_gamma.sort_values('Gamma')

        if len(df_gamma) > 0:
            st.markdown(rf"""
            **Расчёты при различных значениях циркуляции $\Gamma$**
            ($h={h_sel}$, {level_sel}, $p=2$)
            """)

            st.markdown("**Таблица результатов:**")
            df_g_display = df_gamma[['Gamma', 'omega', 'S', 'n_iterations']].copy()
            df_g_display['omega'] = df_g_display['omega'].apply(lambda x: f"{x:.4f}")
            df_g_display['S'] = df_g_display['S'].apply(lambda x: f"{x:.4f}")
            df_g_display = df_g_display.rename(columns={
                'Gamma': 'Γ',
                'omega': 'ω',
                'S': 'S',
                'n_iterations': 'Итераций'
            })
            st.dataframe(df_g_display, use_container_width=True, hide_index=True)

            st.markdown("**График зависимости:**")
            fig, ax1 = plt.subplots(figsize=(8, 4))

            gamma_vals = df_gamma['Gamma'].values
            omega_vals = df_gamma['omega'].values
            S_vals = df_gamma['S'].values

            ax1.plot(gamma_vals, omega_vals, 'bo-', markersize=8, linewidth=2, label=r'$\omega$')
            ax1.set_xlabel(r'$\Gamma$')
            ax1.set_ylabel(r'$\omega$', color='blue')
            ax1.tick_params(axis='y', labelcolor='blue')
            ax1.grid(True, alpha=0.3)

            ax2 = ax1.twinx()
            ax2.plot(gamma_vals, S_vals, 'rs-', markersize=8, linewidth=2, label=r'$S$')
            ax2.set_ylabel(r'$S$', color='red')
            ax2.tick_params(axis='y', labelcolor='red')

            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
            ax1.set_title(r'Зависимость $\omega$ и $S$ от $\Gamma$')
            fig.tight_layout()
            st.pyplot(fig)

            st.markdown("**Графики линий тока:**")
            cols = st.columns(len(df_gamma))
            for i, (_, row) in enumerate(df_gamma.iterrows()):
                with cols[i]:
                    stream_file = row['stream_path']
                    if os.path.exists(stream_file):
                        st.image(stream_file,
                                 caption=f"$\Gamma={row['Gamma']}$",
                                 use_container_width=True)
        else:
            st.warning("Нет данных для выбранных параметров.")
    else:
        st.warning("Результаты не найдены.")

elif menu == "Влияние высоты уступа":
    st.markdown("##### Влияние высоты уступа на вихревую структуру")

    if df is not None:
        col1, col2 = st.columns(2)
        with col1:
            gamma_sel = st.selectbox("Циркуляция $\Gamma$",
                                     sorted(df['Gamma'].unique()),
                                     index=1,
                                     key='h_gamma')
        with col2:
            level_sel = st.selectbox("Сетка",
                                     sorted(df['level'].unique()),
                                     index=1,
                                     key='h_level')

        df_h = df[(df['Gamma'] == gamma_sel) &
                  (df['level'] == level_sel) &
                  (df['degree'] == 2)]
        df_h = df_h.sort_values('h')

        if len(df_h) > 0:
            st.markdown(rf"""
            **Расчёты при различных высотах уступа $h$**
            ($\Gamma={gamma_sel}$, {level_sel}, $p=2$)
            """)

            st.markdown("**Таблица результатов:**")
            df_h_display = df_h[['h', 'omega', 'S', 'n_iterations']].copy()
            df_h_display['omega'] = df_h_display['omega'].apply(lambda x: f"{x:.4f}")
            df_h_display['S'] = df_h_display['S'].apply(lambda x: f"{x:.4f}")
            df_h_display = df_h_display.rename(columns={
                'h': 'h',
                'omega': 'ω',
                'S': 'S',
                'n_iterations': 'Итераций'
            })
            st.dataframe(df_h_display, use_container_width=True, hide_index=True)

            st.markdown("**График зависимости:**")
            fig, ax1 = plt.subplots(figsize=(8, 4))

            h_vals = df_h['h'].values
            omega_vals = df_h['omega'].values
            S_vals = df_h['S'].values

            ax1.plot(h_vals, omega_vals, 'bo-', markersize=8, linewidth=2, label=r'$\omega$')
            ax1.set_xlabel(r'$h$')
            ax1.set_ylabel(r'$\omega$', color='blue')
            ax1.tick_params(axis='y', labelcolor='blue')
            ax1.grid(True, alpha=0.3)

            ax2 = ax1.twinx()
            ax2.plot(h_vals, S_vals, 'rs-', markersize=8, linewidth=2, label=r'$S$')
            ax2.set_ylabel(r'$S$', color='red')
            ax2.tick_params(axis='y', labelcolor='red')

            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
            ax1.set_title(r'Зависимость $\omega$ и $S$ от $h$')
            fig.tight_layout()
            st.pyplot(fig)

            st.markdown("**Графики линий тока:**")
            cols = st.columns(len(df_h))
            for i, (_, row) in enumerate(df_h.iterrows()):
                with cols[i]:
                    stream_file = row['stream_path']
                    if os.path.exists(stream_file):
                        st.image(stream_file,
                                 caption=f"$h={row['h']}$",
                                 use_container_width=True)
        else:
            st.warning("Нет данных для выбранных параметров.")
    else:
        st.warning("Результаты не найдены.")

elif menu == "Поля функции тока":
    st.markdown("##### Поля функции тока $\psi$")

    if df is not None:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            h_sel = st.selectbox("Высота уступа $h$",
                                 sorted(df['h'].unique()),
                                 key='field_h')
        with col2:
            gamma_sel = st.selectbox("Циркуляция $\Gamma$",
                                     sorted(df['Gamma'].unique()),
                                     key='field_gamma')
        with col3:
            level_sel = st.selectbox("Сетка",
                                     sorted(df['level'].unique()),
                                     key='field_level')
        with col4:
            p_sel = st.selectbox("Степень $p$",
                                 sorted(df['degree'].unique()),
                                 key='field_p')

        selected = df[(df['h'] == h_sel) &
                      (df['Gamma'] == gamma_sel) &
                      (df['level'] == level_sel) &
                      (df['degree'] == p_sel)]

        if len(selected) > 0:
            st.markdown("---")
            row = selected.iloc[0]
            cols = st.columns(2)
            with cols[0]:
                psi_file = row['psi_path']
                if os.path.exists(psi_file):
                    st.image(psi_file,
                             caption=f"Цветовая карта $\psi$",
                             use_container_width=True)
            with cols[1]:
                stream_file = row['stream_path']
                if os.path.exists(stream_file):
                    st.image(stream_file,
                             caption=f"Линии тока",
                             use_container_width=True)

            st.markdown("**Параметры расчёта:**")
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                st.metric("$h$", f"{row['h']}")
            with c2:
                st.metric("$\Gamma$", f"{row['Gamma']}")
            with c3:
                st.metric("$\omega$", f"{row['omega']:.4f}")
            with c4:
                st.metric("$S$", f"{row['S']:.4f}")
            with c5:
                st.metric("Итераций", int(row['n_iterations']))
        else:
            st.warning("Нет результатов для выбранных параметров.")
    else:
        st.warning("Результаты не найдены.")

elif menu == "Сходимость итераций":
    st.markdown("##### Сходимость итерационного процесса")

    if df is not None:
        col1, col2, col3 = st.columns(3)
        with col1:
            h_sel = st.selectbox("Высота уступа $h$",
                                 sorted(df['h'].unique()),
                                 key='conv_h')
        with col2:
            gamma_sel = st.selectbox("Циркуляция $\Gamma$",
                                     sorted(df['Gamma'].unique()),
                                     key='conv_gamma')
        with col3:
            level_sel = st.selectbox("Сетка",
                                     sorted(df['level'].unique()),
                                     key='conv_level')

        selected = df[(df['h'] == h_sel) &
                      (df['Gamma'] == gamma_sel) &
                      (df['level'] == level_sel)]

        if len(selected) > 0:
            st.markdown("**Графики сходимости по итерациям:**")
            cols = st.columns(min(3, len(selected)))
            for i, (_, row) in enumerate(selected.iterrows()):
                with cols[i % 3]:
                    conv_file = row['conv_path']
                    if os.path.exists(conv_file) and conv_file != "" and str(conv_file) != "nan":
                        st.image(conv_file,
                                 caption=f"$p={int(row['degree'])}$",
                                 use_container_width=True)
                    else:
                        st.info(f"Нет графика для p={int(row['degree'])}")
        else:
            st.warning("Нет результатов для выбранных параметров.")
    else:
        st.warning("Результаты не найдены.")

elif menu == "Код решателя":
    st.markdown("##### Код решателя (vortex_solver.py)")

    code = '''"""
Решатель задачи вихре-потенциального течения в канале с уступом.
Итерационный метод последовательных приближений для нелинейной правой части.
"""
import numpy as np
from dolfin import *


def solve_vortex_channel(mesh, boundaries, degree=1, Gamma=-2.0, H=1.0, h=1.0,
                         max_iter=100, tol=1e-6):
    """Итерационное решение задачи вихре-потенциального течения."""
    # Функциональное пространство
    V = FunctionSpace(mesh, 'P', degree)
    psi = TrialFunction(V)
    phi = TestFunction(V)

    # Краевые условия
    bc_G1 = DirichletBC(V, Constant(0.0), boundaries, 1)   # Gamma1: psi = 0
    bc_G2 = DirichletBC(V, Constant(H), boundaries, 2)     # Gamma2: psi = H
    inflow_expr = Expression('H * x[1]', H=H, degree=degree)
    bc_G3 = DirichletBC(V, inflow_expr, boundaries, 3)     # Gamma3: psi = H*x2
    bcs = [bc_G1, bc_G2, bc_G3]

    # Вариационная форма
    a = dot(grad(psi), grad(phi)) * dx
    dx_custom = Measure("dx", domain=mesh)
    DG0 = FunctionSpace(mesh, 'DG', 0)

    # Начальное приближение: уравнение Лапласа (f = 0)
    L0 = Constant(0.0) * phi * dx
    psi_k = Function(V)
    solve(a == L0, psi_k, bcs)

    # Проверка наличия вихря в начальном приближении
    psi_vals = psi_k.vector().get_local()
    dofmap = V.dofmap()
    has_vortex = any(np.min(psi_vals[dofmap.cell_dofs(c.index())]) < 0
                     for c in cells(mesh) if len(dofmap.cell_dofs(c.index())) > 0)

    if not has_vortex:
        # Принудительная вихревая зона за уступом
        marker_vals = np.zeros(DG0.dim())
        coords_DG = DG0.tabulate_dof_coordinates()
        for i, coord in enumerate(coords_DG):
            if 1.0 <= coord[0] <= 2.0 and -h <= coord[1] <= 0.0:
                marker_vals[i] = 1.0

        S_init = np.sum(marker_vals) * (1.0 * h / DG0.dim())
        omega_init = Gamma / S_init

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
        error_history = []
        start_k = 0

    # Итерационный процесс
    omega_k = None
    S_k = None
    converged = False
    n_iter = start_k

    for k in range(start_k, max_iter):
        n_iter = k + 1
        psi_vals = psi_k.vector().get_local()
        marker_vals = np.zeros(DG0.dim())

        # Шаг 1: Определение вихревой зоны (psi < 0)
        for cell in cells(mesh):
            dofs = dofmap.cell_dofs(cell.index())
            if len(dofs) > 0 and np.min(psi_vals[dofs]) < 0:
                marker_vals[cell.index()] = 1.0

        vortex_marker = Function(DG0)
        vortex_marker.vector().set_local(marker_vals)
        vortex_marker.vector().apply("insert")

        # Шаг 2: Площадь вихревой зоны
        S_k = assemble(vortex_marker * dx_custom)
        if abs(S_k) < 1e-14:
            omega_k = 0.0
            break

        # Шаг 3: Завихрённость
        omega_k = Gamma / S_k

        # Шаг 4-5: Правая часть и решение уравнения Пуассона
        f_func = Function(DG0)
        f_func.vector().set_local(marker_vals * omega_k)
        f_func.vector().apply("insert")
        L_rhs = f_func * phi * dx
        psi_new = Function(V)
        solve(a == L_rhs, psi_new, bcs)

        # Шаг 6: Проверка сходимости
        diff = Function(V)
        diff.vector().set_local(
            psi_new.vector().get_local() - psi_k.vector().get_local())
        diff.vector().apply("insert")
        norm_diff = norm(diff, 'L2')
        norm_psi = norm(psi_new, 'L2')
        error = norm_diff / norm_psi if norm_psi > 1e-14 else norm_diff
        error_history.append(error)

        psi_k.assign(psi_new)

        if error < tol:
            converged = True
            break

    return {
        "psi": psi_k,
        "omega": omega_k,
        "S": S_k if S_k is not None else 0.0,
        "n_iterations": n_iter,
        "error_history": error_history,
        "converged": converged
    }'''

    st.code(code, language="python")

elif menu == "Код расчётов":
    st.markdown("##### Код запуска расчётов (run_calculations.py)")

    code = '''# Основной цикл перебора всех параметров
h_values = [0.5, 1.0, 1.5]
levels = ["level1", "level2", "level3"]
degrees = [1, 2, 3]
gamma_values = [-1.0, -2.0, -4.0]

for h_val in h_values:
    for level in levels:
        mesh, boundaries, _ = load_or_convert_mesh(h_val, level)
        if mesh is None:
            continue
        for p in degrees:
            for Gamma_val in gamma_values:
                results = solve_vortex_channel(
                    mesh, boundaries, degree=p,
                    Gamma=Gamma_val, H=1.0, h=h_val,
                    max_iter=100, tol=1e-6
                )
                # Сохранение графиков и результатов
                plot_and_save(results["psi"], mesh, file_prefix, h_val)
                all_results.append({...})'''

    st.code(code, language="python")

    st.markdown("**Конвертация сетки из Gmsh в XDMF:**")

    code2 = '''def convert_msh_to_xdmf(msh_path, xdmf_path):
    """Конвертация .msh в XDMF через dolfin.MeshEditor."""
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
        f.write(mesh)'''

    st.code(code2, language="python")

elif menu == "Выводы":
    st.markdown(r"""
    ##### Выводы

    **1. Верификация на последовательности сеток:**

    - Наблюдается устойчивая сходимость $\omega$ при измельчении сетки
    - level1 даёт погрешность ~30%, level2 — ~7% относительно level3
    - Для практических расчётов рекомендуется level2, для высокой точности — level3

    **2. Влияние циркуляции $\Gamma$:**

    - С ростом $|\Gamma|$ площадь вихревой зоны $S$ увеличивается близко к линейному закону
    - Завихрённость $|\omega|$ при этом слабо уменьшается (распределение по большей площади)
    - Структура вихря качественно сохраняется при всех $\Gamma$

    **3. Влияние высоты уступа $h$:**

    - С увеличением $h$ площадь вихря $S$ растёт, $|\omega|$ существенно падает
    - При $h=0.5$ вихрь компактный и интенсивный ($|\omega| \approx 5.5$)
    - При $h=1.5$ вихрь занимает почти всю область за уступом ($S \approx 1.25$)

    **4. Влияние степени полиномов $p$:**

    - Результаты для $p=1,2,3$ близки (разница $\omega$ в пределах 3-5%)
    - $p=2$ — оптимальный выбор по соотношению точность/затраты
    - Более высокие $p$ требуют больше итераций для сходимости

    **5. Итерационный процесс:**

    - Метод последовательных приближений сходится за 5-26 итераций
    - Характерна немонотонная сходимость с осцилляциями
    - При стабилизации вихревой зоны ошибка падает до машинного нуля

    """)