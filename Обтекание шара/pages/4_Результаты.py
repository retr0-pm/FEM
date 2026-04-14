import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Результаты расчетов", layout="wide")

RESULTS_DIR = "results"

menu = st.sidebar.radio('***',
                        ("Сводная таблица",
                         "Сходимость по сетке",
                         "Сравнение уровней сетки",
                         "Сравнение степеней p",
                         "Поля скорости",
                         "Выводы")
                        )

# Загрузка данных
csv_file = f"{RESULTS_DIR}/all_results.csv"
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
else:
    df = None

if menu == "Сводная таблица":
    st.markdown("##### Сводная таблица результатов")

    if df is not None:
        st.markdown("**Максимальная ошибка (max_error) — основной показатель точности:**")

        pivot = df.pivot_table(values='max_error', index=['R', 'level'], columns='degree')
        pivot.columns = [f'p={int(col)}' for col in pivot.columns]

        # Форматирование
        for col in pivot.columns:
            pivot[col] = pivot[col].apply(lambda x: f"{x:.2e}")

        st.dataframe(pivot, use_container_width=True)

        st.markdown("---")
        st.markdown("**Лучшие результаты (по max_error):**")

        best_idx = df['max_error'].idxmin()
        best = df.iloc[best_idx]
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("R", f"{best['R']:.1f}")
        with col2:
            st.metric("Сетка", best['level'])
        with col3:
            st.metric("p", int(best['degree']))
        st.metric("Мин. ошибка", f"{best['max_error']:.2e}")

        st.markdown("---")
        st.markdown("**Полная таблица:**")
        df_display = df.copy()
        df_display['L2_error'] = df_display['L2_error'].apply(lambda x: f"{x:.2e}")
        df_display['max_error'] = df_display['max_error'].apply(lambda x: f"{x:.2e}")
        df_display = df_display.rename(columns={
            'R': 'R', 'level': 'Сетка', 'degree': 'p',
            'nodes': 'Узлы', 'cells': 'Ячейки',
            'L2_error': 'L2 ошибка', 'max_error': 'Max ошибка'
        })
        st.dataframe(df_display, use_container_width=True)
    else:
        st.warning("Результаты не найдены. Запустите `python run_calculations.py`")

elif menu == "Сходимость по сетке":
    st.markdown("##### Сходимость по сетке (R=5)")

    fig_file = f"{RESULTS_DIR}/convergence_R5.png"
    if os.path.exists(fig_file):
        st.image(fig_file)

        if df is not None:
            st.markdown("**Данные:**")
            df_conv = df[df['R'] == 5.0][['level', 'degree', 'h_max', 'max_error']]
            df_conv = df_conv.pivot(index='level', columns='degree', values=['h_max', 'max_error'])
            st.dataframe(df_conv)
    else:
        st.warning("График не найден.")

elif menu == "Сравнение уровней сетки":
    st.markdown("##### Сравнение уровней сетки (R=5, p=2)")

    fig_file = f"{RESULTS_DIR}/mesh_level_comparison.png"
    if os.path.exists(fig_file):
        st.image(fig_file)

        if df is not None:
            st.markdown("**Ошибки для разных уровней сетки:**")
            df_levels = df[(df['R'] == 5.0) & (df['degree'] == 2)][['level', 'nodes', 'cells', 'max_error', 'L2_error']]
            st.dataframe(df_levels)
    else:
        st.warning("График не найден.")

elif menu == "Сравнение степеней p":
    st.markdown("##### Сравнение аппроксимаций p=1,2,3 (R=5, level2)")

    fig_file = f"{RESULTS_DIR}/degree_comparison.png"
    if os.path.exists(fig_file):
        st.image(fig_file)

        if df is not None:
            st.markdown("**Ошибки для разных p:**")
            df_p = df[(df['R'] == 5.0) & (df['level'] == 'level2')][['degree', 'max_error', 'L2_error']]
            st.dataframe(df_p)
    else:
        st.warning("График не найден.")

elif menu == "Поля скорости":
    st.markdown("##### Поля скорости (p=2, level2)")

    tab1, tab2, tab3 = st.tabs(["R=3.0", "R=5.0", "R=7.0"])

    with tab1:
        fig_file = f"{RESULTS_DIR}/velocity_R3.0_level2_p2.png"
        if os.path.exists(fig_file):
            st.image(fig_file)
    with tab2:
        fig_file = f"{RESULTS_DIR}/velocity_R5.0_level2_p2.png"
        if os.path.exists(fig_file):
            st.image(fig_file)
    with tab3:
        fig_file = f"{RESULTS_DIR}/velocity_R7.0_level2_p2.png"
        if os.path.exists(fig_file):
            st.image(fig_file)

elif menu == "Выводы":
    st.markdown("""
    ##### Основные выводы

    **1. Сходимость по сетке:**
    - При измельчении сетки ошибка монотонно уменьшается
    - p=2 показывает наилучшее соотношение точность/время
    - p=3 на грубых сетках может давать большую ошибку из-за недостаточного разрешения

    **2. Влияние уровня сетки (R=5, p=2):**
    - level1 (362 ячейки): max_error ≈ 2.1e-02
    - level2 (3668 ячеек): max_error ≈ 5.6e-03
    - level3 (55884 ячейки): max_error ≈ 4.4e-03
    - Переход от level1 к level2 дает значительное улучшение, далее — замедление

    **3. Влияние степени полиномов (R=5, level2):**
    - p=1: max_error ≈ 8.4e-03
    - p=2: max_error ≈ 5.6e-03
    - p=3: max_error ≈ 2.6e-02 (ухудшение на данной сетке!)
    - p=2 оптимален для level2

    **4. Влияние радиуса R (p=2, level2):**
    - R=3: max_error ≈ 2.1e-02 (близость границы влияет)
    - R=5: max_error ≈ 5.6e-03 (достаточно для точности)
    - R=7: max_error ≈ 3.0e-03 (небольшое улучшение)

    **5. Лучший результат:**
    - R=7.0, level3, p=2: max_error = 1.66e-03
    - R=5.0, level3, p=2: max_error = 4.38e-03 (почти так же хорошо)

    **6. Рекомендации:**
    - Оптимальный выбор: **R=5.0, level2, p=2**
    - Для высокой точности: **R=5.0, level3, p=2**
    - p=3 не рекомендуется для использованных сеток
    """)