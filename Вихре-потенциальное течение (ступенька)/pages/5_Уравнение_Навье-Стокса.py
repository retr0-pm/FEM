import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Уравнения Навье-Стокса", layout="wide")

RESULTS_NS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results_ns")
RESULTS_VP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")

menu = st.sidebar.radio('***',
                        ("Постановка",
                         "Результаты",
                         "Характеристики вихря",
                         "Сравнение с вихре-потенциальной",
                         "Код решателя",
                         "Выводы")
                        )

csv_ns = os.path.join(RESULTS_NS_DIR, "ns_results.csv")
csv_vp = os.path.join(RESULTS_VP_DIR, "all_results.csv")

if os.path.exists(csv_ns):
    df_ns = pd.read_csv(csv_ns)
else:
    df_ns = None

if os.path.exists(csv_vp):
    df_vp = pd.read_csv(csv_vp)
else:
    df_vp = None

if menu == "Постановка":
    st.markdown(r"""
    ##### Стационарные уравнения Навье-Стокса

    **Постановка задачи**

    Течение вязкой несжимаемой жидкости в канале с уступом описывается стационарными уравнениями Навье-Стокса:

    $$
    \begin{aligned}
    (\mathbf{v} \cdot \nabla) \mathbf{v} &= -\frac{1}{\rho} \nabla p + \nu \nabla^2 \mathbf{v} \\
    \nabla \cdot \mathbf{v} &= 0
    \end{aligned}
    $$

    где $\mathbf{v} = (v_1, v_2)$ — вектор скорости, $p$ — давление, $\nu$ — кинематическая вязкость.

    **Характерное число Рейнольдса:**

    $$
    Re = \frac{U H}{\nu}
    $$

    **Граничные условия:**

    | Граница | Условие |
    |---------|---------|
    | $\Gamma_1, \Gamma_2$ (стенки) | $\mathbf{v} = \mathbf{0}$ (условие прилипания) |
    | $\Gamma_3$ (вход) | $v_1 = 6x_2/H \cdot (1 - x_2/H)$, $v_2 = 0$ (профиль Пуазейля) |
    | $\Gamma_4$ (выход) | $\partial\mathbf{v}/\partial n = 0$, $p = 0$ |

    **Отличие от вихре-потенциальной модели:**

    | Характеристика | Вихре-потенциальная | Навье-Стокса |
    |----------------|---------------------|-------------|
    | Вязкость | Отсутствует | $\nu > 0$ |
    | Вихрь | Задан $\omega = \text{const}$ | Возникает из-за отрыва |
    | Размер вихря | Из условия $\int \omega = \Gamma$ | Из баланса вязкости и инерции |
    | Условие на стенках | Непротекание | Прилипание |

    **Метод Пикара:**

    Конвективный член линеаризуется:

    $$
    (\mathbf{v}^k \cdot \nabla) \mathbf{v}^{k+1} = -\nabla p^{k+1} + \frac{1}{Re} \nabla^2 \mathbf{v}^{k+1}
    $$

    Используются смешанные конечные элементы Тейлора-Худа (P2 для скорости, P1 для давления).

    **Функция тока** вычисляется интегрированием скорости:

    $$
    \psi(x_1, x_2) = \int_{x_2^{\text{bottom}}}^{x_2} v_1(x_1, \xi) \, d\xi
    $$

    Вихревая зона (отрывная область): $\psi < 0$.
    """)

elif menu == "Результаты":
    st.markdown("##### Результаты расчётов")

    if df_ns is not None:
        st.markdown("**Параметры расчётов:** $h = 1.0$, сетка level3")

        st.markdown("**Сводная таблица:**")
        df_display = df_ns[['Re', 'nodes', 'cells', 'S_vortex', 'psi_min', 'x_attach',
                            'y_max_vortex', 'n_iterations']].copy()
        for col in ['S_vortex', 'psi_min', 'x_attach', 'y_max_vortex']:
            df_display[col] = df_display[col].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "")
        df_display = df_display.rename(columns={
            'Re': 'Re', 'nodes': 'Узлы', 'cells': 'Ячейки',
            'S_vortex': 'S', 'psi_min': 'ψ_min', 'x_attach': 'x_прис',
            'y_max_vortex': 'y_max', 'n_iterations': 'Итерации'
        })
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        st.markdown("---")

        if len(df_ns) >= 2:
            st.markdown("**Зависимость характеристик вихря от Re:**")
            col1, col2 = st.columns(2)
            with col1:
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.plot(df_ns['Re'].values, df_ns['S_vortex'].values, 'bo-', markersize=8, linewidth=2)
                ax.set_xlabel('$Re$')
                ax.set_ylabel('$S$')
                ax.set_title('Площадь вихревой зоны')
                ax.grid(True, alpha=0.3)
                fig.tight_layout()
                st.pyplot(fig)
            with col2:
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.plot(df_ns['Re'].values, df_ns['x_attach'].values, 'o-', markersize=8, label=r'$x_{прис}$')
                ax.plot(df_ns['Re'].values, df_ns['y_max_vortex'].values, 's-', markersize=8, label=r'$y_{max}$')
                ax.set_xlabel('$Re$')
                ax.legend()
                ax.grid(True, alpha=0.3)
                fig.tight_layout()
                st.pyplot(fig)

            st.markdown("**Зависимость $\psi_{min}$ и центра вихря от Re:**")
            col1, col2 = st.columns(2)
            with col1:
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.plot(df_ns['Re'].values, df_ns['psi_min'].values, 'o-', markersize=8, color='purple')
                ax.set_xlabel('$Re$')
                ax.set_ylabel('$\psi_{min}$')
                ax.set_title('Минимум функции тока')
                ax.grid(True, alpha=0.3)
                fig.tight_layout()
                st.pyplot(fig)
            with col2:
                fig, ax = plt.subplots(figsize=(6, 4))
                ax.plot(df_ns['Re'].values, df_ns['x_vortex_center'].values, 'o-', markersize=8, label=r'$x_{центр}$')
                ax.plot(df_ns['Re'].values, df_ns['y_vortex_center'].values, 's-', markersize=8, label=r'$y_{центр}$')
                ax.set_xlabel('$Re$')
                ax.legend()
                ax.grid(True, alpha=0.3)
                fig.tight_layout()
                st.pyplot(fig)

        st.markdown("---")
        st.markdown("**Поля функции тока и скорости:**")

        Re_select = st.selectbox("Выберите число Рейнольдса", sorted(df_ns['Re'].unique()))

        selected = df_ns[df_ns['Re'] == Re_select]
        if len(selected) > 0:
            row = selected.iloc[0]

            tab1, tab2, tab3, tab4 = st.tabs(["Функция тока", "Линии тока", "Поле скорости", "Сходимость"])

            with tab1:
                if os.path.exists(row['psi_path']):
                    st.image(row['psi_path'], caption=f"$\psi$, $Re={Re_select}$", use_container_width=True)
            with tab2:
                if os.path.exists(row['stream_path']):
                    st.image(row['stream_path'], caption=f"Линии тока, $Re={Re_select}$", use_container_width=True)
            with tab3:
                if os.path.exists(row['vel_path']):
                    st.image(row['vel_path'], caption=f"Поле скорости, $Re={Re_select}$", use_container_width=True)
            with tab4:
                conv_file = row['conv_path']
                if os.path.exists(conv_file) and str(conv_file) != "nan" and conv_file != "":
                    st.image(conv_file, caption=f"Сходимость Пикара, $Re={Re_select}$", use_container_width=True)

            st.markdown("**Параметры:**")
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                st.metric("$Re$", f"{row['Re']}")
            with c2:
                st.metric("$S$", f"{row['S_vortex']:.4f}")
            with c3:
                st.metric("$\psi_{min}$", f"{row['psi_min']:.4f}")
            with c4:
                st.metric("$x_{прис}$", f"{row['x_attach']:.4f}")
            with c5:
                st.metric("Итераций", int(row['n_iterations']))
    else:
        st.warning("Результаты не найдены. Запустите `python run_ns_calculations.py`")

elif menu == "Характеристики вихря":
    st.markdown("##### Геометрия вихревой зоны")

    if df_ns is not None:
        st.markdown(r"""
        **Характеристики вихревой зоны:**
        - $\psi_{min}$ — минимальное значение функции тока (центр вихря)
        - $x_{прис}$ — координата точки присоединения ($\psi=0$ на нижней стенке)
        - $y_{max}$ — максимальная высота вихревой зоны
        - $x_{центр}, y_{центр}$ — координаты центра вихря
        """)

        df_char = df_ns[['Re', 'psi_min', 'x_attach', 'y_max_vortex',
                         'x_vortex_center', 'y_vortex_center']].copy()
        for col in ['psi_min', 'x_attach', 'y_max_vortex', 'x_vortex_center', 'y_vortex_center']:
            df_char[col] = df_char[col].apply(lambda x: f"{float(x):.4f}" if pd.notna(x) else "")
        df_char = df_char.rename(columns={
            'Re': 'Re', 'psi_min': 'ψ_min', 'x_attach': 'x_прис',
            'y_max_vortex': 'y_max', 'x_vortex_center': 'x_центр', 'y_vortex_center': 'y_центр'
        })
        st.dataframe(df_char, use_container_width=True, hide_index=True)
    else:
        st.warning("Результаты не найдены.")

elif menu == "Сравнение с вихре-потенциальной":
    st.markdown("##### Сравнение моделей: Навье-Стокс vs Вихре-потенциальная")

    if df_ns is not None and df_vp is not None:
        st.markdown(r"""
        **Сравнение для базового варианта:** $h = 1.0$, сетка level3

        Сравниваются:
        - Модель с ур-ми Навье-Стокса при различных $Re$
        - Вихре-потенциальная модель при $\Gamma = -1, -2, -4$
        """)

        df_vp_base = df_vp[(df_vp['h'] == 1.0) &
                           (df_vp['level'] == 'level3') &
                           (df_vp['degree'] == 2)]

        # Выбор типа графика и параметров
        st.markdown("**Выберите тип сравнения:**")
        compare_type = st.radio("Тип графика:",
                                ["Линии тока", "Цветовая карта $\psi$", "Поле скорости"])

        if compare_type == "Поле скорости":
            st.markdown("**Поле скорости для уравнений Навье-Стокса:**")
            Re_sel = st.selectbox("Re (уравнения Навье-Стокса)", sorted(df_ns['Re'].unique()), key='comp_vel')
            ns_row = df_ns[df_ns['Re'] == Re_sel].iloc[0]
            if os.path.exists(ns_row['vel_path']):
                st.image(ns_row['vel_path'], caption=f"Уравнения Навье-Стокса: $Re={Re_sel}$", use_container_width=True)

        else:
            col1, col2 = st.columns(2)
            with col1:
                Re_sel = st.selectbox("Re (Навье-Стокса)", sorted(df_ns['Re'].unique()), key='comp_ns')
            with col2:
                Gamma_sel = st.selectbox("Γ (вихре-потенциальная)",
                                         sorted(df_vp_base['Gamma'].unique()), key='comp_vp')

            ns_row = df_ns[df_ns['Re'] == Re_sel].iloc[0]
            vp_row = df_vp_base[df_vp_base['Gamma'] == Gamma_sel].iloc[0]

            col1, col2 = st.columns(2)
            if compare_type == "Линии тока":
                with col1:
                    if os.path.exists(ns_row['stream_path']):
                        st.image(ns_row['stream_path'],
                                 caption=f"Уравнения Навье-Стокса: $Re={Re_sel}$", use_container_width=True)
                with col2:
                    if os.path.exists(vp_row['stream_path']):
                        st.image(vp_row['stream_path'],
                                 caption=f"Вихре-потенциальная: $\\Gamma={Gamma_sel}$", use_container_width=True)
            elif compare_type == "Цветовая карта $\psi$":
                with col1:
                    if os.path.exists(ns_row['psi_path']):
                        st.image(ns_row['psi_path'],
                                 caption=f"Уравнения Навье-Стокса: $Re={Re_sel}$", use_container_width=True)
                with col2:
                    if os.path.exists(vp_row['psi_path']):
                        st.image(vp_row['psi_path'],
                                 caption=f"Вихре-потенциальная: $\\Gamma={Gamma_sel}$", use_container_width=True)

        # Таблицы сравнения
        st.markdown("---")
        st.markdown("**Сравнение характеристик:**")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Навье-Стокса (все Re):**")
            ns_table = df_ns[['Re', 'S_vortex', 'psi_min', 'x_attach', 'y_max_vortex']].copy()
            for col in ['S_vortex', 'psi_min', 'x_attach', 'y_max_vortex']:
                ns_table[col] = ns_table[col].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "")
            ns_table = ns_table.rename(columns={
                'Re': 'Re', 'S_vortex': 'S', 'psi_min': 'ψ_min',
                'x_attach': 'x_прис', 'y_max_vortex': 'y_max'
            })
            st.dataframe(ns_table, use_container_width=True, hide_index=True)

        with col2:
            st.markdown("**Вихре-потенциальная:**")
            vp_table = df_vp_base[['Gamma', 'S', 'psi_min', 'x_attach', 'y_max_vortex']].copy()
            for col in ['S', 'psi_min', 'x_attach', 'y_max_vortex']:
                vp_table[col] = vp_table[col].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "")
            vp_table = vp_table.rename(columns={
                'Gamma': 'Γ', 'S': 'S', 'psi_min': 'ψ_min',
                'x_attach': 'x_прис', 'y_max_vortex': 'y_max'
            })
            st.dataframe(vp_table, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("""
        **Качественные различия:**

        | Особенность | Навье-Стокса | Вихре-потенциальная |
        |-------------|-------------|---------------------|
        | Форма вихря | Вытянутая, с плавной границей | Компактная, с изломом на $\psi=0$ |
        | Точка присоединения | На нижней стенке | Внутри области |
        | Вторичные вихри | Есть (угловой вихрь) | Отсутствуют |
        | Зависимость от параметра | $S$ растёт с $Re$ | $S$ растёт с $\|\Gamma\|$ |
        | $\psi_{min}$ | Растёт по модулю с $Re$ | Определяется $\Gamma$ |
        """)
    else:
        st.warning("Не все данные загружены.")

elif menu == "Код решателя":
    st.markdown("##### Код решателя уравнений Навье-Стокса")

    st.markdown("**Инициализация и смешанное пространство Тейлора-Худа (P2/P1):**")
    st.code('''nu = Constant(H / Re)

# Пространства для скорости и давления
V = VectorFunctionSpace(mesh, 'P', 2)
Q = FunctionSpace(mesh, 'P', 1)

# Смешанное пространство
W_elem = MixedElement([V.ufl_element(), Q.ufl_element()])
W = FunctionSpace(mesh, W_elem)

u, p = TrialFunctions(W)
v, q = TestFunctions(W)

w = Function(W)
u_k = Function(V)''', language="python")

    st.markdown("**Краевые условия (прилипание на стенках, профиль Пуазейля на входе):**")
    st.code('''zero_vec = Constant((0.0, 0.0))
bc_walls_1 = DirichletBC(W.sub(0), zero_vec, boundaries, 1)
bc_walls_2 = DirichletBC(W.sub(0), zero_vec, boundaries, 2)

# Вход: параболический профиль Пуазейля
inflow_ux = Expression('6.0 * x[1]/H * (1.0 - x[1]/H)', H=H, degree=3)
inflow_uy = Constant(0.0)
inflow_func = Function(V)
inflow_func.assign(project(as_vector((inflow_ux, inflow_uy)), V))
bc_inflow = DirichletBC(W.sub(0), inflow_func, boundaries, 3)

bcs = [bc_walls_1, bc_walls_2, bc_inflow]''', language="python")

    st.markdown("**Вариационная форма (линеаризация Пикара):**")
    st.code('''# nu * вязкий член + (u_k · grad) u — конвективный член
# - p * div(v) — градиент давления
# - q * div(u) — условие несжимаемости
F = (nu * inner(grad(u), grad(v)) * dx
     + inner(grad(u) * u_k, v) * dx
     - p * div(v) * dx
     - q * div(u) * dx)

a, L = lhs(F), rhs(F)
w.vector()[:] = 0.0  # начальное приближение''', language="python")

    st.markdown("**Итерации Пикара:**")
    st.code('''for k in range(max_iter):
    solve(a == L, w, bcs,
          solver_parameters={"linear_solver": "mumps"})

    u_new, p_new = w.split(deepcopy=True)

    # Проверка сходимости по изменению скорости
    if k > 0:
        diff_u = Function(V)
        diff_u.vector().set_local(
            u_new.vector().get_local() - u_old.vector().get_local())
        error = norm(diff_u, 'L2') / norm(u_new, 'L2')
        if error < tol:
            break

    u_old.assign(u_new)
    u_k.assign(u_new)  # обновляем конвективное поле''', language="python")

    st.markdown("**Вычисление функции тока интегрированием скорости:**")
    st.code('''def compute_stream_function(u, mesh):
    V_psi = FunctionSpace(mesh, 'P', 2)
    psi_func = Function(V_psi)
    coords = V_psi.tabulate_dof_coordinates()
    psi_vals = np.zeros(len(coords))
    x2_min = mesh.coordinates()[:, 1].min()
    l = 1.0  # длина уступа

    for i, (x1, x2) in enumerate(coords):
        x2_bottom = 0.0 if x1 <= l else x2_min
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
    return psi_func''', language="python")

    st.markdown("**Характеристики вихревой зоны:**")
    st.code('''def compute_vortex_characteristics_ns(psi, mesh):
    # Минимум psi и центр вихря
    psi_min = np.min(psi_verts)
    x_vortex_center, y_vortex_center = coords[np.argmin(psi_verts)]

    # Точка присоединения: psi=0 на нижней стенке после уступа
    # Линейная интерполяция между узлами с разными знаками psi

    # Максимальная высота вихря и площадь S
    y_max_vortex = max(x2 for (x1, x2) if psi < 0)
    S = sum(cell.volume() for cell if min(psi in cell) < 0)''', language="python")

elif menu == "Выводы":
    st.markdown(r"""
    ##### Выводы

    **1. Сходимость метода Пикара:**

    - С ростом $Re$ сходимость замедляется
    - При малых $Re$ сходимость быстрая монотонная
    - При $Re \ge 50$ появляются осцилляции, но метод сходится

    **2. Характеристики вихревой зоны:**

    - Площадь вихря $S$ растёт с увеличением $Re$
    - Точка присоединения $x_{прис}$ смещается вправо
    - Максимальная высота вихря $y_{max}$ увеличивается
    - $|\psi_{min}|$ растёт — вихрь становится интенсивнее

    **3. Вторичный угловой вихрь:**

    - При малых и умеренных $Re$ обнаружен вторичный вихрь под уступом
    - Имеет треугольную форму, прилегающую к стенкам
    - С ростом $Re$ может отрываться от угла

    **4. Сравнение с вихре-потенциальной моделью:**

    - В модели Навье-Стокса вихрь более вытянутый и занимает большую площадь
    - Точка присоединения в находится на нижней стенке в модели Навье-Стокса, а в вихре-потенциальной — внутри области
    - В модели Навье-Стокса есть вторичные вихри, в вихре-потенциальной отсутствуют
    - Форма вихря в модели Навье-Стокса плавная, в вихре-потенциальной — с изломом на $\psi=0$

    **5. Физические особенности:**

    - Профиль Пуазейля на входе перестраивается в сдвиговый профиль за уступом
    - При увеличении $Re$ отрывная зона удлиняется
    - При $Re \ge 100$ вихревая зона приближается к выходной границе — требуется более длинный канал
    """)