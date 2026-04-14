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
                         "Цветные графики полей",
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

elif menu == "Цветные графики полей":
    st.markdown("##### Цветные графики полей")
    st.markdown("Выберите параметры для просмотра графиков потенциала, скорости и линий тока.")

    if df is not None:
        col1, col2, col3 = st.columns(3)
        with col1:
            R_select = st.selectbox("Радиус R", sorted(df['R'].unique()))
        with col2:
            level_select = st.selectbox("Уровень сетки", sorted(df['level'].unique()))
        with col3:
            p_select = st.selectbox("Степень p", sorted(df['degree'].unique()))

        st.markdown("---")

        # Четыре типа графиков
        graph_types = {
            "potential": "Потенциал скорости φ",
            "velocity_mag": "Модуль скорости |u|/u_∞",
            "velocity_field": "Векторное поле скорости",
            "streamlines": "Эквипотенциали / Линии тока"
        }

        cols = st.columns(2)
        for i, (key, name) in enumerate(graph_types.items()):
            with cols[i % 2]:
                fig_file = f"{RESULTS_DIR}/{key}_R{R_select}_{level_select}_p{p_select}.png"
                if os.path.exists(fig_file):
                    st.image(fig_file, caption=f"{name} (R={R_select}, {level_select}, p={p_select})",
                             use_container_width=True)
                else:
                    st.warning(f"График {name} не найден")

        st.markdown("---")
        st.markdown("**Статистика для выбранного случая:**")
        selected_data = df[(df['R'] == R_select) & (df['level'] == level_select) & (df['degree'] == p_select)]
        if len(selected_data) > 0:
            row = selected_data.iloc[0]
            cols = st.columns(4)
            with cols[0]:
                st.metric("Узлы", int(row['nodes']))
            with cols[1]:
                st.metric("Ячейки", int(row['cells']))
            with cols[2]:
                st.metric("Max ошибка", f"{row['max_error']:.2e}")
            with cols[3]:
                st.metric("L2 ошибка", f"{row['L2_error']:.2e}")
    else:
        st.warning("Результаты не найдены. Запустите `python run_calculations.py`")

elif menu == "Выводы":
    st.markdown("""
    ##### Основные выводы

    **1. Сходимость по сетке (R=5):**

    | Уровень | p=1 | p=2 | p=3 |
    |---------|-----|-----|-----|
    | level1 | 5.56e-02 | 2.89e-02 | 1.07e-01 |
    | level2 | 1.69e-02 | 7.71e-03 | 3.78e-02 |
    | level3 | 1.02e-02 | 6.09e-03 | 6.91e-03 |

    - При измельчении сетки ошибка монотонно уменьшается для всех p
    - **p=2 показывает наилучшие результаты** на всех уровнях
    - p=3 на грубых сетках дает большую ошибку из-за осцилляций

    **2. Влияние радиуса R (p=2, level2):**

    | R | max_error |
    |----|-----------|
    | 3.0 | 2.97e-02 |
    | 5.0 | 7.71e-03 |
    | 7.0 | 4.38e-03 |

    - R=3: заметное влияние близкой границы (ошибка ~3%)
    - R=5: достаточно для практических расчетов (ошибка < 1%)
    - R=7: дальнейшее улучшение в ~1.8 раза

    **3. Сравнение уровней сетки (R=5, p=2):**

    | Уровень | Ячейки | max_error | Улучшение |
    |---------|--------|-----------|-----------|
    | level1 | 362 | 2.89e-02 | — |
    | level2 | 3,668 | 7.71e-03 | в 3.7 раза |
    | level3 | 55,884 | 6.09e-03 | в 1.3 раза |

    - Переход level1 → level2 дает значительное улучшение
    - Переход level2 → level3 дает небольшое улучшение при большом росте вычислений

    **4. Лучшие результаты:**

    | R | Уровень | p | max_error |
    |----|---------|---|-----------|
    | 7.0 | level3 | 2 | **2.37e-03** |
    | 7.0 | level2 | 2 | 4.38e-03 |
    | 5.0 | level3 | 2 | 6.09e-03 |

    **5. Анализ цветных графиков полей:**

    - **Потенциал φ**: плавное изменение от -R до +R, эквипотенциали сгущаются у шара
    - **Модуль скорости**: максимум (1.5 u_∞) достигается на экваторе шара (θ = 90°)
    - **Векторное поле**: поток плавно огибает шар, ускоряясь вблизи поверхности
    - **Линии тока**: симметричны относительно оси z, повторяют форму шара

    **6. Практические рекомендации:**

    | Сценарий | R | Уровень | p | max_error |
    |----------|---|---------|---|-----------|
    | Быстрая оценка | 5.0 | level1 | 2 | 2.89e-02 (3%) |
    | **Оптимальный** | **5.0** | **level2** | **2** | **7.71e-03 (<1%)** |
    | Высокая точность | 5.0 | level3 | 2 | 6.09e-03 |
    | Макс. точность | 7.0 | level3 | 2 | 2.37e-03 |

    """)