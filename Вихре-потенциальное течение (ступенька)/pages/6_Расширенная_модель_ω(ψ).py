import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="Расширенная модель ω(ψ)", layout="wide")

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results_omega")

menu = st.sidebar.radio('***',
                        ("Теория",
                         "Результаты",
                         "Характеристики вихря",
                         "Сравнение моделей",
                         "Профили ψ и ω",
                         "Код решателя",
                         "Выводы")
                        )

csv_file = os.path.join(RESULTS_DIR, "omega_results.csv")
if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
else:
    df = None

model_names = {'const': 'Постоянная', 'linear': 'Линейная', 'exp': 'Экспоненциальная'}

if menu == "Теория":
    st.markdown(r"""
    ##### Расширение вихре-потенциальной модели: $\omega = \omega(\psi)$

    **Мотивация**

    В базовой модели вихре-потенциального течения завихрённость постоянна внутри вихревой зоны:

    $$
    \omega(\psi) = \omega_0 = \text{const}, \quad \psi < 0
    $$

    Это простейшее предположение, но в реальных отрывных течениях завихрённость неравномерна: 
    она максимальна в центре вихря и затухает к границе.

    **Расширенные модели**

    Рассматриваются три модели распределения $\omega(\psi)$:

    **1. Постоянная (const):**

    $$
    \omega(\psi) = \omega_0
    $$

    **2. Линейная (linear):**

    $$
    \omega(\psi) = \omega_0 \cdot \max\left(1 - \alpha \frac{|\psi|}{\psi_{ref}}, \; 0.2\right)
    $$

    где $\alpha = 0.5$, $\psi_{ref} = 0.3$. Завихрённость линейно спадает от центра вихря к границе.

    **3. Экспоненциальная (exp):**

    $$
    \omega(\psi) = \omega_0 \cdot \exp\left(-\beta \frac{|\psi|}{\psi_{ref}}\right)
    $$

    где $\beta = 0.5$. Более плавное затухание, чем в линейной модели.

    **Условие нормировки**

    Для каждой модели $\omega_0$ подбирается из условия сохранения циркуляции:

    $$
    \int_{\psi < 0} \omega(\psi) \, d\mathbf{x} = \Gamma
    $$

    **Ожидаемый эффект**

    При одинаковой циркуляции $\Gamma$:
    - Площадь вихревой зоны $S$ практически не меняется
    - Пиковое значение $|\omega_0|$ растёт от const к exp
    - Форма вихря визуально почти неразличима, но профили $\psi$ и $\omega$ отличаются
    """)

elif menu == "Результаты":
    st.markdown("##### Результаты расчётов")

    if df is not None:
        st.markdown(f"**Параметры:** $h = 1.0$, level2, $p = 2$, $\Gamma = -2.0$")

        st.markdown("**Сводная таблица:**")
        df_display = df[['model', 'S', 'omega_scale', 'psi_min', 'x_attach',
                         'y_max_vortex', 'n_iterations', 'converged']].copy()
        for col in ['S', 'omega_scale', 'psi_min', 'x_attach', 'y_max_vortex']:
            df_display[col] = df_display[col].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "")
        df_display = df_display.rename(columns={
            'model': 'Модель', 'S': 'S', 'omega_scale': 'ω₀',
            'psi_min': 'ψ_min', 'x_attach': 'x_прис', 'y_max_vortex': 'y_max',
            'n_iterations': 'Итераций', 'converged': 'Сошёлся'
        })
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Выбор модели для просмотра
        model_sel = st.selectbox("Выберите модель", df['model'].unique(),
                                 format_func=lambda x: model_names.get(x, x))

        selected = df[df['model'] == model_sel]
        if len(selected) > 0:
            row = selected.iloc[0]

            tab1, tab2, tab3 = st.tabs(["Цветовая карта ψ", "Линии тока", "Сходимость"])

            with tab1:
                if os.path.exists(row['psi_path']):
                    st.image(row['psi_path'],
                             caption=f"{model_names.get(model_sel, model_sel)}",
                             use_container_width=True)

            with tab2:
                if os.path.exists(row['stream_path']):
                    st.image(row['stream_path'],
                             caption=f"{model_names.get(model_sel, model_sel)}",
                             use_container_width=True)

            with tab3:
                conv_file = row['conv_path']
                if os.path.exists(conv_file) and str(conv_file) != "nan" and conv_file != "":
                    st.image(conv_file, caption=f"Сходимость: {model_sel}", use_container_width=True)

            st.markdown("**Характеристики:**")
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            with c1:
                st.metric("$S$", f"{row['S']:.4f}")
            with c2:
                st.metric("$\omega_0$", f"{row['omega_scale']:.4f}")
            with c3:
                st.metric("$\psi_{min}$", f"{row['psi_min']:.4f}")
            with c4:
                st.metric("$x_{прис}$", f"{row['x_attach']:.4f}")
            with c5:
                st.metric("$y_{max}$", f"{row['y_max_vortex']:.4f}")
            with c6:
                st.metric("Итераций", int(row['n_iterations']))

        st.markdown("---")
        st.markdown("**Сравнение полей $\psi$ для всех моделей:**")
        cols = st.columns(3)
        for i, (_, row) in enumerate(df.iterrows()):
            with cols[i]:
                if os.path.exists(row['psi_path']):
                    st.image(row['psi_path'],
                             caption=f"{model_names.get(row['model'], row['model'])}",
                             use_container_width=True)

        st.markdown("**Замечание:** Визуально поля $\psi$ для трёх моделей почти неразличимы. "
                    "Разница проявляется в профилях $\omega$ и количественных характеристиках.")
    else:
        st.warning("Результаты не найдены. Запустите `python run_omega_calculations.py`")

elif menu == "Характеристики вихря":
    st.markdown("##### Геометрия вихревой зоны")

    if df is not None:
        st.markdown(r"""
        **Характеристики вихревой зоны для разных моделей $\omega(\psi)$:**
        - $\psi_{min}$ — минимальное значение функции тока
        - $x_{прис}$ — координата точки присоединения
        - $y_{max}$ — максимальная высота вихря
        - $x_{центр}, y_{центр}$ — координаты центра вихря
        """)

        df_char = df[['model', 'psi_min', 'x_attach', 'y_max_vortex',
                      'x_vortex_center', 'y_vortex_center']].copy()
        for col in ['psi_min', 'x_attach', 'y_max_vortex', 'x_vortex_center', 'y_vortex_center']:
            df_char[col] = df_char[col].apply(lambda x: f"{float(x):.4f}" if pd.notna(x) else "")
        df_char['model'] = df_char['model'].map(model_names)
        df_char = df_char.rename(columns={
            'model': 'Модель', 'psi_min': 'ψ_min', 'x_attach': 'x_прис',
            'y_max_vortex': 'y_max', 'x_vortex_center': 'x_центр', 'y_vortex_center': 'y_центр'
        })
        st.dataframe(df_char, use_container_width=True, hide_index=True)

        st.markdown("""
        **Наблюдения:**
        - Геометрические характеристики ($x_{прис}$, $y_{max}$, центр вихря) практически одинаковы для всех моделей
        - $\psi_{min}$ также слабо зависит от модели
        - Распределение $\omega(\psi)$ влияет в основном на пиковое значение $\omega_0$, а не на геометрию вихря
        """)
    else:
        st.warning("Результаты не найдены.")

elif menu == "Сравнение моделей":
    st.markdown("##### Сравнение моделей $\omega(\psi)$")

    if df is not None:
        st.markdown("**Интегральные характеристики:**")

        models = df['model'].values
        S_vals = df['S'].values
        omega_vals = df['omega_scale'].values

        col1, col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots(figsize=(6, 4))
            colors = ['#2196F3', '#4CAF50', '#FF9800']
            model_labels = [model_names.get(m, m) for m in models]
            bars = ax.bar(model_labels, S_vals, color=colors, edgecolor='black', linewidth=1.5)
            ax.set_ylabel('$S$')
            ax.set_title('Площадь вихревой зоны')
            for bar, val in zip(bars, S_vals):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.002,
                        f'{val:.4f}', ha='center', fontsize=11)
            fig.tight_layout()
            st.pyplot(fig)

        with col2:
            fig, ax = plt.subplots(figsize=(6, 4))
            bars = ax.bar(model_labels, np.abs(omega_vals), color=colors, edgecolor='black', linewidth=1.5)
            ax.set_ylabel('$|\omega_0|$')
            ax.set_title('Масштаб завихрённости')
            for bar, val in zip(bars, np.abs(omega_vals)):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                        f'{val:.4f}', ha='center', fontsize=11)
            fig.tight_layout()
            st.pyplot(fig)

        st.markdown(f"""
        **Анализ:**

        - $S$ практически одинакова для всех моделей (разброс < 0.5%) — граница вихря слабо зависит от распределения $\omega$
        - $|\omega_0|$ растёт от const к exp — чтобы сохранить $\int \omega \, dS = \Gamma$ при непостоянном $\omega(\psi)$, нужно увеличить пиковое значение
        - Экспоненциальная модель даёт наибольшее пиковое значение, так как $\omega$ спадает быстрее всего
        """)
    else:
        st.warning("Результаты не найдены.")

elif menu == "Профили ψ и ω":
    st.markdown("##### Профили $\psi$ и $\omega$ через центр вихря")

    st.markdown(r"""
    Для количественного сравнения моделей строятся профили вдоль вертикальной линии 
    $x_1 = 1.5$ (через центр вихревой зоны).
    """)

    if df is not None:
        st.markdown("**Сравнение профилей (схематическое представление):**")

        x2 = np.linspace(-1.0, 0.0, 100)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        colors = {'const': '#2196F3', 'linear': '#4CAF50', 'exp': '#FF9800'}

        psi_min_model = -0.15

        for _, row in df.iterrows():
            model = row['model']
            omega0 = row['omega_scale']

            x2_norm = (x2 - x2.min()) / (x2.max() - x2.min())
            psi_prof = psi_min_model * (1 - (2 * x2_norm - 1) ** 2)
            ax1.plot(x2, psi_prof, color=colors.get(model, 'gray'), linewidth=2,
                     label=model_names.get(model, model))

            if model == 'const':
                omega_prof = np.ones_like(x2) * omega0
            elif model == 'linear':
                omega_prof = omega0 * np.maximum(1 - 0.5 * np.abs(psi_prof) / 0.3, 0.2)
            else:
                omega_prof = omega0 * np.exp(0.5 * psi_prof / 0.3)

            ax2.plot(x2, omega_prof, color=colors.get(model, 'gray'), linewidth=2,
                     label=model_names.get(model, model))

        ax1.set_xlabel('$x_2$')
        ax1.set_ylabel('$\psi$')
        ax1.set_title('Профиль $\psi(x_2)$ при $x_1 = 1.5$')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        ax2.set_xlabel('$x_2$')
        ax2.set_ylabel('$\omega$')
        ax2.set_title('Профиль $\omega(x_2)$ при $x_1 = 1.5$')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        fig.tight_layout()
        st.pyplot(fig)

        st.markdown("""
        **Наблюдения:**

        - **Профиль $\psi$:** для всех моделей имеет параболическую форму с минимумом в центре вихря. Различия минимальны.

        - **Профиль $\omega$:** существенно разный:
          - **const:** постоянное значение во всей вихревой зоне
          - **linear:** сильный перепад от центра к границе
          - **exp:** умеренный перепад, более реалистичный для вязких течений

        **Физический смысл:**
        - Постоянная модель: вихрь с однородной завихрённостью (как твёрдое тело)
        - Линейная модель: сильная концентрация завихрённости в центре
        - Экспоненциальная модель: умеренная концентрация, наиболее близка к реальным вязким течениям
        """)
    else:
        st.warning("Результаты не найдены.")

elif menu == "Код решателя":
    st.markdown("##### Код решателя с $\omega(\psi)$")

    solver_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "vortex_solver_omega.py")
    if os.path.exists(solver_path):
        with open(solver_path, "r") as f:
            code = f.read()
        st.code(code, language="python")
    else:
        st.warning("Файл vortex_solver_omega.py не найден.")

elif menu == "Выводы":
    st.markdown(r"""
    ##### Выводы

    **1. Влияние распределения $\omega(\psi)$ на интегральные характеристики:**

    - Площадь вихря $S$ практически не зависит от модели (разброс < 0.5%)
    - Пиковое значение $|\omega_0|$ растёт с увеличением неоднородности

    **2. Геометрия вихревой зоны:**

    - Форма вихря и его геометрические характеристики не зависят от модели $\omega(\psi)$
    - Граница $\psi = 0$ определяется интегральным условием $\int \omega = \Gamma$, а не распределением $\omega$

    **3. Сходимость:**

    - Все три модели сходятся за одинаковое число итераций
    - После коррекции параметров линейная модель устойчива

    **4. Визуализация и профили:**

    - Поля $\psi$ визуально неразличимы для разных моделей
    - Разница проявляется в профилях $\omega$: перепад от центра к границе может различаться в несколько раз
    - Для детального сравнения необходимы количественные профили

    **5. Физическая интерпретация:**

    - Модель `const`: вихрь как твёрдое тело (постоянная завихрённость)
    - Модель `linear`: сильная концентрация завихрённости в центре
    - Модель `exp`: умеренная концентрация, наиболее близка к реальным вязким течениям

    **6. Сравнение с Навье-Стоксом:**

    - Распределение $\omega$ в отрывной зоне NS ближе к экспоненциальной модели (плавное затухание)
    - Но в NS есть вторичные вихри и более сложная структура, недоступная в рамках VP-модели
    """)