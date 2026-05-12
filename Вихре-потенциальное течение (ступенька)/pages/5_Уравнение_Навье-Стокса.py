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

    **Граничные условия:**

    | Граница | Условие |
    |---------|---------|
    | $\Gamma_1, \Gamma_2$ (стенки) | $\mathbf{v} = \mathbf{0}$ (условие прилипания) |
    | $\Gamma_3$ (вход) | $v_1 = 6x_2/H \cdot (1 - x_2/H)$, $v_2 = 0$ (профиль Пуазейля) |
    | $\Gamma_4$ (выход) | $\partial\mathbf{v}/\partial n = 0$, $p = 0$ |

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

    Используются смешанные конечные элементы Тейлора-Худа (P2 для скорости, P1 для давления).

    **Функция тока** вычисляется интегрированием скорости:

    $$
    \psi(x_1, x_2) = \int_{x_2^{\text{bottom}}}^{x_2} v_1(x_1, \xi) \, d\xi
    $$

    Вихревая зона (отрывная область): $\psi < 0$.
    """)

elif menu == "Результаты NS":
    st.markdown("##### Результаты расчётов Навье-Стокса")

    if df_ns is not None:
        st.markdown("**Параметры расчётов:** $h = 1.0$, сетка level3")

        st.markdown("**Сводная таблица:**")
        df_display = df_ns[['Re', 'nodes', 'cells', 'S_vortex', 'psi_min', 'x_attach',
                            'y_max_vortex', 'n_iterations', 'converged']].copy()
        for col in ['S_vortex', 'psi_min', 'x_attach', 'y_max_vortex']:
            df_display[col] = df_display[col].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "")
        df_display = df_display.rename(columns={
            'Re': 'Re', 'nodes': 'Узлы', 'cells': 'Ячейки',
            'S_vortex': 'S', 'psi_min': 'ψ_min', 'x_attach': 'x_прис',
            'y_max_vortex': 'y_max', 'n_iterations': 'Итер.', 'converged': 'Сошёлся'
        })
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        st.markdown("---")

        # График S(Re)
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

        st.markdown("---")

        # Графики
        st.markdown("**Поля функции тока и скорости:**")
        Re_select = st.selectbox("Выберите число Рейнольдса", sorted(df_ns['Re'].unique()))

        selected = df_ns[df_ns['Re'] == Re_select]
        if len(selected) > 0:
            row = selected.iloc[0]

            tab1, tab2, tab3 = st.tabs(["Функция тока", "Линии тока", "Поле скорости"])
            with tab1:
                if os.path.exists(row['psi_path']):
                    st.image(row['psi_path'], caption=f"$\psi$, $Re={Re_select}$", use_container_width=True)
            with tab2:
                if os.path.exists(row['stream_path']):
                    st.image(row['stream_path'], caption=f"Линии тока, $Re={Re_select}$", use_container_width=True)
            with tab3:
                if os.path.exists(row['vel_path']):
                    st.image(row['vel_path'], caption=f"Поле скорости, $Re={Re_select}$", use_container_width=True)

            conv_file = row['conv_path']
            if os.path.exists(conv_file) and str(conv_file) != "nan" and conv_file != "":
                st.markdown("**Сходимость итераций Пикара:**")
                st.image(conv_file, use_container_width=True)

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
        - Навье-Стокс при $Re = 25, 50, 100$
        - Вихре-потенциальная модель при $\Gamma = -1, -2, -4$
        """)

        df_vp_base = df_vp[(df_vp['h'] == 1.0) &
                           (df_vp['level'] == 'level3') &
                           (df_vp['degree'] == 2)]

        st.markdown("**Площадь вихревой зоны $S$:**")
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
                         caption=f"Навье-Стокс: $Re={Re_sel}$", use_container_width=True)
        with col2:
            if os.path.exists(vp_row['stream_path']):
                st.image(vp_row['stream_path'],
                         caption=f"Вихре-потенциальная: $\\Gamma={Gamma_sel}$", use_container_width=True)

        st.markdown("---")
        st.markdown("""
        **Качественные различия:**

        | Особенность | Навье-Стокс | Вихре-потенциальная |
        |-------------|-------------|---------------------|
        | Форма вихря | Вытянутая, с плавной границей | Компактная, с чёткой границей $\psi=0$ |
        | Точка присоединения | На нижней стенке | Внутри области |
        | Вторичные вихри | Есть (угловой вихрь) | Отсутствуют |
        | Зависимость от параметра | $S$ растёт с $Re$ | $S$ растёт с $\|\Gamma\|$ |
        """)
    else:
        st.warning("Не все данные загружены.")

elif menu == "Код решателя":
    st.markdown("##### Код решателя Навье-Стокса")

    solver_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ns_solver.py")
    if os.path.exists(solver_path):
        with open(solver_path, "r") as f:
            code = f.read()
        st.code(code, language="python")
    else:
        st.warning("Файл ns_solver.py не найден.")

elif menu == "Выводы":
    st.markdown(r"""
    ##### Выводы

    **1. Сходимость метода Пикара:**

    - С ростом $Re$ сходимость замедляется
    - При $Re=25$ сходимость быстрая монотонная
    - При $Re=100$ появляются осцилляции, но метод сходится

    **2. Характеристики вихревой зоны:**

    - Площадь вихря $S$ растёт с увеличением $Re$
    - Точка присоединения $x_{прис}$ смещается вправо
    - Максимальная высота вихря $y_{max}$ увеличивается

    **3. Сравнение с вихре-потенциальной моделью:**

    - В модели Навье-Стокса вихрь более вытянутый и занимает большую площадь
    - Точка присоединения в NS находится на нижней стенке, в VP — внутри области
    - В NS обнаружен вторичный угловой вихрь (эффект Моффатта)
    - Форма вихря в NS плавная, в VP — с изломом на границе $\psi=0$

    **4. Физические особенности:**

    - Профиль скорости Пуазейля на входе перестраивается в сдвиговый профиль за уступом
    - При увеличении $Re$ отрывная зона удлиняется
    - Для более высоких $Re$ может потребоваться более длинный канал
    """)