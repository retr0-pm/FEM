import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Навье-Стокс", layout="wide")

RESULTS_NS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results_ns")
RESULTS_VP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")

menu = st.sidebar.radio('***',
                        ("Теория",
                         "Результаты NS",
                         "Сравнение с вихре-потенциальной",
                         "Код решателя NS",
                         "Выводы")
                        )

# Загрузка данных
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

if menu == "Теория":
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

    где $U$ — характерная скорость (средняя скорость на входе), $H$ — высота канала.

    **Граничные условия:**

    | Граница | Условие |
    |---------|---------|
    | $\Gamma_1, \Gamma_2$ (стенки) | $\mathbf{v} = \mathbf{0}$ (условие прилипания) |
    | $\Gamma_3$ (вход) | $v_1 = 6x_2/H \cdot (1 - x_2/H)$, $v_2 = 0$ (профиль Пуазейля) |
    | $\Gamma_4$ (выход) | $\partial\mathbf{v}/\partial n = 0$, $p = 0$ (стресс-фри) |

    **Отличие от вихре-потенциальной модели:**

    | Характеристика | Вихре-потенциальная | Навье-Стокс |
    |----------------|---------------------|-------------|
    | Вязкость | Отсутствует | $\nu > 0$ |
    | Вихрь | Задан $\omega = \text{const}$ | Возникает из-за отрыва |
    | Размер вихря | Из условия $\int \omega = \Gamma$ | Из баланса вязкости и инерции |
    | Условие на стенках | Непротекание | Прилипание |

    **Метод решения (Пикар):**

    Конвективный член линеаризуется:

    $$
    (\mathbf{v}^k \cdot \nabla) \mathbf{v}^{k+1} = -\nabla p^{k+1} + \frac{1}{Re} \nabla^2 \mathbf{v}^{k+1}
    $$

    На каждой итерации решается линейная система для $(\mathbf{v}^{k+1}, p^{k+1})$.
    Используются смешанные конечные элементы Тейлора-Худа (P2 для скорости, P1 для давления).

    **Функция тока:**

    Вычисляется интегрированием скорости:

    $$
    \psi(x_1, x_2) = \int_{x_2^{\text{bottom}}}^{x_2} v_1(x_1, \xi) \, d\xi
    $$

    Вихревая зона (отрывная область): $\psi < 0$.
    """)

elif menu == "Результаты NS":
    st.markdown("##### Результаты расчётов Навье-Стокса")

    if df_ns is not None:
        st.markdown("**Параметры расчётов:** $h = 1.0$, сетка level2")

        st.markdown("**Сводная таблица:**")
        df_display = df_ns.copy()
        df_display['S_vortex'] = df_display['S_vortex'].apply(lambda x: f"{x:.4f}")
        df_display = df_display.rename(columns={
            'Re': 'Re',
            'nodes': 'Узлы',
            'cells': 'Ячейки',
            'S_vortex': 'S вихря',
            'n_iterations': 'Итер. Пикара',
            'converged': 'Сошелся'
        })
        st.dataframe(df_display[['Re', 'Узлы', 'Ячейки', 'S вихря', 'Итер. Пикара', 'Сошелся']],
                     use_container_width=True, hide_index=True)

        st.markdown("---")

        # График зависимости S от Re
        st.markdown("**Зависимость площади вихревой зоны от Re:**")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(df_ns['Re'].values, df_ns['S_vortex'].values, 'bo-', markersize=8, linewidth=2)
        ax.set_xlabel('$Re$')
        ax.set_ylabel('$S$')
        ax.set_title('Площадь вихревой зоны')
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        st.pyplot(fig)

        st.markdown("---")

        # Графики
        st.markdown("**Поля функции тока и скорости:**")

        Re_select = st.selectbox("Выберите число Рейнольдса",
                                 sorted(df_ns['Re'].unique()))

        selected = df_ns[df_ns['Re'] == Re_select]
        if len(selected) > 0:
            row = selected.iloc[0]

            tab1, tab2, tab3 = st.tabs(["Функция тока", "Линии тока", "Поле скорости"])

            with tab1:
                if os.path.exists(row['psi_path']):
                    st.image(row['psi_path'],
                             caption=f"Цветовая карта $\psi$, $Re={Re_select}$",
                             use_container_width=True)

            with tab2:
                if os.path.exists(row['stream_path']):
                    st.image(row['stream_path'],
                             caption=f"Линии тока, $Re={Re_select}$",
                             use_container_width=True)

            with tab3:
                if os.path.exists(row['vel_path']):
                    st.image(row['vel_path'],
                             caption=f"Поле скорости, $Re={Re_select}$",
                             use_container_width=True)

            # График сходимости Пикара
            conv_file = row['conv_path']
            if os.path.exists(conv_file) and str(conv_file) != "nan":
                st.markdown("**Сходимость итераций Пикара:**")
                st.image(conv_file, use_container_width=True)

            st.markdown("**Параметры:**")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("$Re$", f"{row['Re']}")
            with c2:
                st.metric("$S$", f"{row['S_vortex']:.4f}")
            with c3:
                st.metric("Итераций", int(row['n_iterations']))
    else:
        st.warning("Результаты не найдены. Запустите `python run_ns_calculations.py`")

elif menu == "Сравнение с вихре-потенциальной":
    st.markdown("##### Сравнение моделей: Навье-Стокс vs Вихре-потенциальная")

    if df_ns is not None and df_vp is not None:
        st.markdown(r"""
        **Сравнение для базового варианта:** $h = 1.0$, сетка level2

        Сравниваются:
        - Навье-Стокс при $Re = 25, 50, 100$
        - Вихре-потенциальная модель при $\Gamma = -1, -2, -4$
        """)

        # Таблица сравнения
        st.markdown("**Площадь вихревой зоны $S$:**")

        df_vp_base = df_vp[(df_vp['h'] == 1.0) &
                           (df_vp['level'] == 'level2') &
                           (df_vp['degree'] == 2)]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Навье-Стокс:**")
            ns_table = df_ns[['Re', 'S_vortex']].copy()
            ns_table['S_vortex'] = ns_table['S_vortex'].apply(lambda x: f"{x:.4f}")
            ns_table = ns_table.rename(columns={'Re': 'Параметр', 'S_vortex': 'S'})
            st.dataframe(ns_table, use_container_width=True, hide_index=True)

        with col2:
            st.markdown("**Вихре-потенциальная:**")
            vp_table = df_vp_base[['Gamma', 'S']].copy()
            vp_table['S'] = vp_table['S'].apply(lambda x: f"{x:.4f}")
            vp_table = vp_table.rename(columns={'Gamma': 'Параметр', 'S': 'S'})
            st.dataframe(vp_table, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Сравнение графиков линий тока
        st.markdown("**Сравнение линий тока:**")

        Re_sel = st.selectbox("Re (Навье-Стокс)", sorted(df_ns['Re'].unique()), key='comp_re')
        Gamma_sel = st.selectbox("Γ (вихре-потенциальная)",
                                 sorted(df_vp_base['Gamma'].unique()), key='comp_gamma')

        ns_row = df_ns[df_ns['Re'] == Re_sel].iloc[0]
        vp_row = df_vp_base[df_vp_base['Gamma'] == Gamma_sel].iloc[0]

        col1, col2 = st.columns(2)
        with col1:
            if os.path.exists(ns_row['stream_path']):
                st.image(ns_row['stream_path'],
                         caption=f"Навье-Стокс: $Re={Re_sel}$",
                         use_container_width=True)
        with col2:
            if os.path.exists(vp_row['stream_path']):
                st.image(vp_row['stream_path'],
                         caption=f"Вихре-потенциальная: $\\Gamma={Gamma_sel}$",
                         use_container_width=True)

        st.markdown("---")
        st.markdown("""
        **Качественные различия:**

        | Особенность | Навье-Стокс | Вихре-потенциальная |
        |-------------|-------------|---------------------|
        | Форма вихря | Вытянутая, с плавной границей | Компактная, с чёткой границей $\psi=0$ |
        | Точка присоединения | На стенке ($\psi=0$) | Внутри области |
        | Вторичные вихри | Есть (угловой вихрь) | Отсутствуют |
        | Зависимость от параметра | $S$ растёт с $Re$ | $S$ растёт с $\|\Gamma\|$ |
        """)

    else:
        st.warning("Не все данные загружены.")

elif menu == "Код решателя NS":
    st.markdown("##### Код решателя Навье-Стокса")

    st.markdown("**Основной решатель (ns_solver.py):**")

    code = '''def solve_navier_stokes_channel(mesh, boundaries, Re=100.0, H=1.0,
                                max_iter=50, tol=1e-6):
    """Решение стационарных уравнений Навье-Стокса методом Пикара."""
    nu = Constant(H / Re)

    # Смешанное пространство Тейлора-Худа: P2/P1
    V = VectorFunctionSpace(mesh, 'P', 2)
    Q = FunctionSpace(mesh, 'P', 1)
    W_elem = MixedElement([V.ufl_element(), Q.ufl_element()])
    W = FunctionSpace(mesh, W_elem)

    u, p = TrialFunctions(W)
    v, q = TestFunctions(W)
    w = Function(W)
    u_k = Function(V)

    # Краевые условия
    zero_vec = Constant((0.0, 0.0))
    bc_walls_1 = DirichletBC(W.sub(0), zero_vec, boundaries, 1)
    bc_walls_2 = DirichletBC(W.sub(0), zero_vec, boundaries, 2)

    # Вход: профиль Пуазейля
    inflow_ux = Expression('6.0 * x[1]/H * (1.0 - x[1]/H)', H=H, degree=3)
    inflow_uy = Constant(0.0)
    inflow_func = Function(V)
    inflow_func.assign(project(as_vector((inflow_ux, inflow_uy)), V))
    bc_inflow = DirichletBC(W.sub(0), inflow_func, boundaries, 3)

    # Вариационная форма (Пикар)
    F = (nu * inner(grad(u), grad(v)) * dx
         + inner(grad(u) * u_k, v) * dx
         - p * div(v) * dx
         - q * div(u) * dx)
    a, L = lhs(F), rhs(F)
    w.vector()[:] = 0.0

    for k in range(max_iter):
        solve(a == L, w, bcs,
              solver_parameters={"linear_solver": "mumps"})
        u_new, p_new = w.split(deepcopy=True)

        if k > 0:
            # Проверка сходимости
            ...
            if error < tol:
                break

        u_k.assign(u_new)

    u_final, p_final = w.split(deepcopy=True)
    psi = compute_stream_function(u_final, mesh)
    return {"velocity": u_final, "pressure": p_final, "psi": psi, ...}'''

    st.code(code, language="python")

    st.markdown("**Вычисление функции тока:**")

    code2 = '''def compute_stream_function(u, mesh):
    """psi(x1,x2) = int_{x2_bottom}^{x2} u1(x1,xi) dxi"""
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
    return psi_func'''

    st.code(code2, language="python")

elif menu == "Выводы":
    st.markdown(r"""
    ##### Выводы по результатам

    **1. Сходимость метода Пикара:**

    | $Re$ | Итераций | Характер |
    |------|----------|----------|
    | 25 | 12 | Быстрая монотонная |
    | 50 | 28 | Монотонная |
    | 100 | 30 | С небольшими осцилляциями |

    - С ростом $Re$ сходимость замедляется
    - Осцилляции связаны с усилением конвективного члена

    **2. Площадь вихревой зоны:**

    | $Re$ | $S$ |
    |------|-----|
    | 25 | 1.15 |
    | 50 | 1.93 |
    | 100 | 2.80 |

    - Вихревая зона растёт с увеличением $Re$
    - При $Re=25$ отрывная зона только формируется
    - При $Re=100$ вихрь занимает почти половину области за уступом

    **3. Сравнение с вихре-потенциальной моделью:**

    | Характеристика | Навье-Стокс | Вихре-потенциальная |
    |----------------|-------------|---------------------|
    | Механизм отрыва | Вязкость + градиент давления | Заданная циркуляция |
    | Форма вихря | Вытянутая, плавная | Компактная, с изломом на $\psi=0$ |
    | Точка присоединения | На нижней стенке | Внутри области |
    | Вторичные вихри | Есть (угол) | Нет |
    | Площадь ($h=1$, $Re=50$/$\Gamma=-2$) | 1.93 | 0.74 |

    **4. Физические особенности:**

    - Обнаружен вторичный угловой вихрь под уступом (эффект Моффатта)
    - При $Re=100$ вихревая зона приближается к выходной границе
    - Профиль скорости Пуазейля на входе перестраивается в сдвиговый профиль за уступом

    """)