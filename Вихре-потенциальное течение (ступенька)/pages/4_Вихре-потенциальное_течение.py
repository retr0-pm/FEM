import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Вихре-потенциальное течение", layout="wide")

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results")

menu = st.sidebar.radio('***',
                        ("Сводная таблица",
                         "Верификация по сетке",
                         "Влияние циркуляции",
                         "Влияние высоты уступа",
                         "Поля функции тока",
                         "Характеристики вихря",
                         "Сходимость итераций",
                         "Код решателя",
                         "Выводы")
                        )

csv_file = os.path.join(RESULTS_DIR, "all_results.csv")
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
else:
    df = None


def filter_df(df, filters):
    """Применяет словарь фильтров {column: value} к датафрейму."""
    result = df.copy()
    for col, val in filters.items():
        if val is not None and val != "Все":
            result = result[result[col] == val]
    return result


def get_available_values(df, column, filters):
    """Возвращает отсортированные уникальные значения колонки с учётом фильтров."""
    filtered = filter_df(df, filters)
    return sorted(filtered[column].unique().tolist())


if menu == "Сводная таблица":
    st.markdown("##### Сводная таблица результатов")

    if df is not None:
        st.markdown(f"**Всего расчётов: {len(df)}**")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            h_vals = ["Все"] + sorted(df['h'].unique().tolist())
            h_filter = st.selectbox("Высота уступа $h$", h_vals)
        with col2:
            df_h = df if h_filter == "Все" else df[df['h'] == float(h_filter)]
            level_vals = ["Все"] + sorted(df_h['level'].unique().tolist())
            level_filter = st.selectbox("Сетка", level_vals)
        with col3:
            df_l = df_h if level_filter == "Все" else df_h[df_h['level'] == level_filter]
            p_vals = ["Все"] + sorted(df_l['degree'].unique().tolist())
            p_filter = st.selectbox("Степень $p$", p_vals)
        with col4:
            df_p = df_l if p_filter == "Все" else df_l[df_l['degree'] == int(p_filter)]
            gamma_vals = ["Все"] + sorted(df_p['Gamma'].unique().tolist())
            gamma_filter = st.selectbox("$\Gamma$", gamma_vals)

        # Применяем все фильтры
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

        if len(df_filtered) > 0:
            df_display = df_filtered[[
                'h', 'Gamma', 'level', 'degree', 'nodes', 'cells',
                'omega', 'S', 'psi_min', 'x_attach', 'y_max_vortex',
                'x_vortex_center', 'y_vortex_center', 'n_iterations', 'converged'
            ]].copy()

            for col in ['omega', 'S', 'psi_min', 'x_attach', 'y_max_vortex',
                         'x_vortex_center', 'y_vortex_center']:
                df_display[col] = df_display[col].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "")

            df_display = df_display.rename(columns={
                'h': 'h', 'Gamma': 'Γ', 'level': 'Сетка', 'degree': 'p',
                'nodes': 'Узлы', 'cells': 'Ячейки',
                'omega': 'ω', 'S': 'S',
                'psi_min': 'ψ_min', 'x_attach': 'x_прис',
                'y_max_vortex': 'y_max', 'x_vortex_center': 'x_центр',
                'y_vortex_center': 'y_центр',
                'n_iterations': 'Итер.', 'converged': 'Сошёлся'
            })
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.warning("Нет результатов с выбранными фильтрами.")
    else:
        st.warning("Результаты не найдены. Запустите `python run_calculations.py`")

elif menu == "Верификация по сетке":
    st.markdown("##### Верификация численных результатов")

    if df is not None:
        df_ver = df[df['variant'] == 'verification']

        if len(df_ver) > 0:
            st.markdown(r"""
            **Верификация на последовательности сеток**
            ($h=1.0$, $\Gamma=-2$, все $p$)
            """)

            available_p = sorted(df_ver['degree'].unique())

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Зависимость $\omega$ от сетки:**")
                fig, ax = plt.subplots(figsize=(6, 4))
                for p in available_p:
                    df_p = df_ver[df_ver['degree'] == p].sort_values('cells')
                    if len(df_p) >= 2:
                        h_mesh = [1/(c)**(1/2) for c in df_p['cells']]
                        ax.plot(h_mesh, df_p['omega'].values, 'o-', markersize=8, linewidth=2,
                                label=f'$p={int(p)}$')
                ax.set_xlabel('Характерный размер ячейки')
                ax.set_ylabel(r'$\omega$')
                ax.legend()
                ax.grid(True, alpha=0.3)
                fig.tight_layout()
                st.pyplot(fig)

            with col2:
                st.markdown("**Таблица (p=2):**")
                df_p2 = df_ver[df_ver['degree'] == 2].sort_values('cells')
                if len(df_p2) > 0:
                    df_t = df_p2[['level', 'nodes', 'cells', 'omega', 'S', 'psi_min', 'x_attach']].copy()
                    for col in ['omega', 'S', 'psi_min', 'x_attach']:
                        df_t[col] = df_t[col].apply(lambda x: f"{float(x):.4f}")
                    df_t = df_t.rename(columns={
                        'level': 'Сетка', 'nodes': 'Узлы', 'cells': 'Ячейки',
                        'omega': 'ω', 'S': 'S', 'psi_min': 'ψ_min', 'x_attach': 'x_прис'
                    })
                    st.dataframe(df_t, use_container_width=True, hide_index=True)
                else:
                    st.info("Нет данных для p=2.")

            st.markdown("**Поля $\psi$ для разных сеток (p=2):**")
            if len(df_p2) > 0:
                cols = st.columns(len(df_p2))
                for i, (_, row) in enumerate(df_p2.iterrows()):
                    with cols[i]:
                        if os.path.exists(row['psi_path']):
                            st.image(row['psi_path'], caption=f"{row['level']}", use_container_width=True)
            else:
                st.info("Нет данных для отображения.")
        else:
            st.warning("Нет данных верификации. Запустите расчёты.")
    else:
        st.warning("Результаты не найдены.")

elif menu == "Влияние циркуляции":
    st.markdown("##### Влияние циркуляции на вихревую структуру")

    if df is not None:
        # Ищем данные для level3, p=2, h=1.0
        df_gamma = df[(df['level'] == 'level3') & (df['degree'] == 2) & (df['h'] == 1.0)]
        df_gamma = df_gamma.sort_values('Gamma')

        if len(df_gamma) > 0:
            st.markdown(r"""
            **Расчёты при различных $\Gamma$** ($h=1.0$, level3, $p=2$)
            """)

            df_g_display = df_gamma[['Gamma', 'omega', 'S', 'psi_min', 'x_attach', 'y_max_vortex']].copy()
            for col in ['omega', 'S', 'psi_min', 'x_attach', 'y_max_vortex']:
                df_g_display[col] = df_g_display[col].apply(lambda x: f"{float(x):.4f}")
            df_g_display = df_g_display.rename(columns={
                'Gamma': 'Γ', 'omega': 'ω', 'S': 'S',
                'psi_min': 'ψ_min', 'x_attach': 'x_прис', 'y_max_vortex': 'y_max'
            })
            st.dataframe(df_g_display, use_container_width=True, hide_index=True)

            if len(df_gamma) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**График $\omega$ и $S$:**")
                    fig, ax1 = plt.subplots(figsize=(6, 4))
                    gamma_vals = df_gamma['Gamma'].values
                    ax1.plot(gamma_vals, df_gamma['omega'].values, 'bo-', markersize=8, label=r'$\omega$')
                    ax1.set_xlabel(r'$\Gamma$')
                    ax1.set_ylabel(r'$\omega$', color='blue')
                    ax2 = ax1.twinx()
                    ax2.plot(gamma_vals, df_gamma['S'].values, 'rs-', markersize=8, label=r'$S$')
                    ax2.set_ylabel(r'$S$', color='red')
                    lines1, labels1 = ax1.get_legend_handles_labels()
                    lines2, labels2 = ax2.get_legend_handles_labels()
                    ax1.legend(lines1 + lines2, labels1 + labels2)
                    ax1.grid(True, alpha=0.3)
                    fig.tight_layout()
                    st.pyplot(fig)

                with col2:
                    st.markdown("**График $x_{прис}$ и $y_{max}$:**")
                    fig, ax = plt.subplots(figsize=(6, 4))
                    ax.plot(gamma_vals, df_gamma['x_attach'].values, 'o-', markersize=8, label=r'$x_{прис}$')
                    ax.plot(gamma_vals, df_gamma['y_max_vortex'].values, 's-', markersize=8, label=r'$y_{max}$')
                    ax.set_xlabel(r'$\Gamma$')
                    ax.legend()
                    ax.grid(True, alpha=0.3)
                    fig.tight_layout()
                    st.pyplot(fig)

            st.markdown("**Линии тока:**")
            cols = st.columns(len(df_gamma))
            for i, (_, row) in enumerate(df_gamma.iterrows()):
                with cols[i]:
                    if os.path.exists(row['stream_path']):
                        st.image(row['stream_path'], caption=f"$\Gamma={row['Gamma']}$", use_container_width=True)
        else:
            st.warning("Нет данных для level3. Возможно, расчёты ещё не завершены.")
    else:
        st.warning("Результаты не найдены.")

elif menu == "Влияние высоты уступа":
    st.markdown("##### Влияние высоты уступа на вихревую структуру")

    if df is not None:
        df_h = df[(df['level'] == 'level3') & (df['degree'] == 2) & (df['Gamma'] == -2.0)]
        df_h = df_h.sort_values('h')

        if len(df_h) > 0:
            st.markdown(r"""
            **Расчёты при различных $h$** ($\Gamma=-2$, level3, $p=2$)
            """)

            df_h_display = df_h[['h', 'omega', 'S', 'psi_min', 'x_attach', 'y_max_vortex']].copy()
            for col in ['omega', 'S', 'psi_min', 'x_attach', 'y_max_vortex']:
                df_h_display[col] = df_h_display[col].apply(lambda x: f"{float(x):.4f}")
            df_h_display = df_h_display.rename(columns={
                'h': 'h', 'omega': 'ω', 'S': 'S',
                'psi_min': 'ψ_min', 'x_attach': 'x_прис', 'y_max_vortex': 'y_max'
            })
            st.dataframe(df_h_display, use_container_width=True, hide_index=True)

            if len(df_h) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**График $\omega$ и $S$:**")
                    fig, ax1 = plt.subplots(figsize=(6, 4))
                    h_vals = df_h['h'].values
                    ax1.plot(h_vals, df_h['omega'].values, 'bo-', markersize=8, label=r'$\omega$')
                    ax1.set_xlabel(r'$h$')
                    ax1.set_ylabel(r'$\omega$', color='blue')
                    ax2 = ax1.twinx()
                    ax2.plot(h_vals, df_h['S'].values, 'rs-', markersize=8, label=r'$S$')
                    ax2.set_ylabel(r'$S$', color='red')
                    lines1, labels1 = ax1.get_legend_handles_labels()
                    lines2, labels2 = ax2.get_legend_handles_labels()
                    ax1.legend(lines1 + lines2, labels1 + labels2)
                    ax1.grid(True, alpha=0.3)
                    fig.tight_layout()
                    st.pyplot(fig)

                with col2:
                    st.markdown("**График $x_{прис}$ и $y_{max}$:**")
                    fig, ax = plt.subplots(figsize=(6, 4))
                    ax.plot(h_vals, df_h['x_attach'].values, 'o-', markersize=8, label=r'$x_{прис}$')
                    ax.plot(h_vals, df_h['y_max_vortex'].values, 's-', markersize=8, label=r'$y_{max}$')
                    ax.set_xlabel(r'$h$')
                    ax.legend()
                    ax.grid(True, alpha=0.3)
                    fig.tight_layout()
                    st.pyplot(fig)

            st.markdown("**Линии тока:**")
            cols = st.columns(len(df_h))
            for i, (_, row) in enumerate(df_h.iterrows()):
                with cols[i]:
                    if os.path.exists(row['stream_path']):
                        st.image(row['stream_path'], caption=f"$h={row['h']}$", use_container_width=True)
        else:
            st.warning("Нет данных для level3. Возможно, расчёты ещё не завершены.")
    else:
        st.warning("Результаты не найдены.")

elif menu == "Поля функции тока":
    st.markdown("##### Поля функции тока $\psi$")

    if df is not None:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            h_vals = sorted(df['h'].unique())
            h_sel = st.selectbox("Высота уступа $h$", h_vals, key='field_h')
        with col2:
            gamma_vals = sorted(df[df['h'] == h_sel]['Gamma'].unique())
            gamma_sel = st.selectbox("$\Gamma$", gamma_vals, key='field_gamma')
        with col3:
            level_vals = sorted(df[(df['h'] == h_sel) & (df['Gamma'] == gamma_sel)]['level'].unique())
            level_sel = st.selectbox("Сетка", level_vals, key='field_level')
        with col4:
            p_vals = sorted(df[(df['h'] == h_sel) & (df['Gamma'] == gamma_sel) &
                               (df['level'] == level_sel)]['degree'].unique())
            p_sel = st.selectbox("Степень $p$", p_vals, key='field_p')

        selected = df[(df['h'] == h_sel) & (df['Gamma'] == gamma_sel) &
                      (df['level'] == level_sel) & (df['degree'] == p_sel)]

        if len(selected) > 0:
            row = selected.iloc[0]
            cols = st.columns(2)
            with cols[0]:
                if os.path.exists(row['psi_path']):
                    st.image(row['psi_path'], caption="Цветовая карта $\psi$", use_container_width=True)
            with cols[1]:
                if os.path.exists(row['stream_path']):
                    st.image(row['stream_path'], caption="Линии тока", use_container_width=True)

            st.markdown("**Параметры и характеристики:**")
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            with c1:
                st.metric("$\omega$", f"{row['omega']:.4f}")
            with c2:
                st.metric("$S$", f"{row['S']:.4f}")
            with c3:
                st.metric("$\psi_{min}$", f"{row['psi_min']:.4f}")
            with c4:
                st.metric("$x_{прис}$", f"{row['x_attach']:.4f}")
            with c5:
                st.metric("$y_{max}$", f"{row['y_max_vortex']:.4f}")
            with c6:
                st.metric("Итераций", int(row['n_iterations']))
        else:
            st.warning("Нет результатов для выбранной комбинации.")
    else:
        st.warning("Результаты не найдены.")

elif menu == "Характеристики вихря":
    st.markdown("##### Геометрия вихревой зоны и функция тока")

    if df is not None:
        st.markdown(r"""
        **Характеристики вихревой зоны:**
        - $\psi_{min}$ — минимальное значение функции тока (центр вихря)
        - $x_{прис}$ — координата точки присоединения ($\psi=0$ на нижней стенке)
        - $y_{max}$ — максимальная высота вихревой зоны
        - $x_{центр}, y_{центр}$ — координаты центра вихря
        """)

        col1, col2, col3 = st.columns(3)
        with col1:
            h_vals = sorted(df['h'].unique())
            h_sel = st.selectbox("Высота уступа $h$", h_vals, key='geom_h')
        with col2:
            gamma_vals = sorted(df[df['h'] == h_sel]['Gamma'].unique())
            gamma_sel = st.selectbox("$\Gamma$", gamma_vals, key='geom_gamma')
        with col3:
            level_vals = sorted(df[(df['h'] == h_sel) & (df['Gamma'] == gamma_sel)]['level'].unique())
            level_sel = st.selectbox("Сетка", level_vals, key='geom_level')

        # Показываем все степени для выбранной конфигурации
        df_geom = df[(df['h'] == h_sel) & (df['Gamma'] == gamma_sel) & (df['level'] == level_sel)]
        df_geom = df_geom.sort_values('degree')

        if len(df_geom) > 0:
            st.markdown("**Характеристики для всех $p$:**")
            df_char = df_geom[['degree', 'psi_min', 'x_attach', 'y_max_vortex',
                               'x_vortex_center', 'y_vortex_center']].copy()
            for col in ['psi_min', 'x_attach', 'y_max_vortex', 'x_vortex_center', 'y_vortex_center']:
                df_char[col] = df_char[col].apply(lambda x: f"{float(x):.4f}")
            df_char = df_char.rename(columns={
                'degree': 'p', 'psi_min': 'ψ_min', 'x_attach': 'x_прис',
                'y_max_vortex': 'y_max', 'x_vortex_center': 'x_центр', 'y_vortex_center': 'y_центр'
            })
            st.dataframe(df_char, use_container_width=True, hide_index=True)
        else:
            st.warning("Нет данных.")
    else:
        st.warning("Результаты не найдены.")

elif menu == "Сходимость итераций":
    st.markdown("##### Сходимость итерационного процесса")

    if df is not None:
        col1, col2, col3 = st.columns(3)
        with col1:
            h_vals = sorted(df['h'].unique())
            h_sel = st.selectbox("Высота уступа $h$", h_vals, key='conv_h')
        with col2:
            gamma_vals = sorted(df[df['h'] == h_sel]['Gamma'].unique())
            gamma_sel = st.selectbox("$\Gamma$", gamma_vals, key='conv_gamma')
        with col3:
            level_vals = sorted(df[(df['h'] == h_sel) & (df['Gamma'] == gamma_sel)]['level'].unique())
            level_sel = st.selectbox("Сетка", level_vals, key='conv_level')

        selected = df[(df['h'] == h_sel) & (df['Gamma'] == gamma_sel) & (df['level'] == level_sel)]
        selected = selected.sort_values('degree')

        if len(selected) > 0:
            st.markdown("**Графики сходимости:**")
            cols = st.columns(min(3, len(selected)))
            for i, (_, row) in enumerate(selected.iterrows()):
                with cols[i % 3]:
                    conv_file = row['conv_path']
                    if os.path.exists(conv_file) and str(conv_file) != "nan" and conv_file != "":
                        st.image(conv_file, caption=f"$p={int(row['degree'])}$", use_container_width=True)
        else:
            st.warning("Нет результатов.")
    else:
        st.warning("Результаты не найдены.")

elif menu == "Код решателя":
    st.markdown("##### Код решателя (vortex_solver.py)")

    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "vortex_solver.py"), "r") as f:
        code = f.read()
    st.code(code, language="python")

elif menu == "Выводы":
    st.markdown(r"""
    ##### Выводы

    **1. Верификация на последовательности сеток:**

    - Значения $\omega$, $S$ и характеристик вихря сходятся при измельчении сетки
    - Разница между level1 и level3 существенна, между level2 и level3 — меньше

    **2. Влияние циркуляции $\Gamma$:**

    - С ростом $|\Gamma|$ площадь вихревой зоны $S$ увеличивается
    - Точка присоединения $x_{прис}$ смещается вправо
    - $|\omega|$ меняется слабее, чем $S$

    **3. Влияние высоты уступа $h$:**

    - С увеличением $h$ площадь вихря $S$ растёт
    - $|\omega|$ при больших $h$ уменьшается — вихрь распределяется по большей площади
    - Максимальная высота вихря $y_{max}$ растёт с $h$

    **4. Влияние степени полиномов $p$:**

    - Результаты для $p=1,2,3$ близки по интегральным характеристикам
    - Более высокие $p$ могут требовать больше итераций для сходимости

    **5. Итерационный процесс:**

    - Характер сходимости — немонотонный из-за дискретного переключения вихревых зон
    - При стабилизации вихревой зоны ошибка падает до машинного нуля за одну итерацию
    """)