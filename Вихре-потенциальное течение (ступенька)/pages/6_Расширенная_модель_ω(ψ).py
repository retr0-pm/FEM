import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import json

st.set_page_config(page_title="Расширенная модель ω(ψ)", layout="wide")

RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "results_omega")

menu = st.sidebar.radio('***',
                        ("Постановка",
                         "Результаты",
                         "Характеристики вихря",
                         "Сравнение моделей",
                         "Профили ψ и ω",
                         "Код решателя",
                         "Выводы")
                        )

csv_file = os.path.join(RESULTS_DIR, "omega_results.csv")
profiles_json = os.path.join(RESULTS_DIR, "profiles.json")
profiles_png = os.path.join(RESULTS_DIR, "profiles_comparison.png")

if os.path.exists(csv_file):
    df = pd.read_csv(csv_file)
else:
    df = None

if os.path.exists(profiles_json):
    with open(profiles_json, 'r') as f:
        profiles_data = json.load(f)
else:
    profiles_data = None

model_names = {'const': 'Постоянная', 'linear': 'Линейная', 'exp': 'Экспоненциальная'}

if menu == "Постановка":
    st.markdown(r"""
    ##### Расширение вихре-потенциальной модели: $\omega = \omega(\psi)$

    В базовой модели вихре-потенциального течения завихрённость постоянна внутри вихревой зоны:

    $$
    \omega(\psi) = \omega_0 = \text{const}, \quad \psi < 0
    $$

    **Расширенные модели**

    Рассматриваются три модели распределения $\omega(\psi)$:

    1. Постоянная (const):

    $$
    \omega(\psi) = \omega_0
    $$

    2. Линейная (linear):

    $$
    \omega(\psi) = \omega_0 \cdot \max\left(1 - \alpha \frac{|\psi|}{\psi_{ref}}, \; 0.2\right)
    $$

    где $\alpha = 0.5$, $\psi_{ref} = 0.3$. Завихрённость линейно спадает от центра вихря к границе.

    3. Экспоненциальная (exp):

    $$
    \omega(\psi) = \omega_0 \cdot \exp\left(-\beta \frac{|\psi|}{\psi_{ref}}\right)
    $$

    где $\beta = 0.5$. Более плавное затухание, чем в линейной модели.

    **Условие нормировки**

    Для каждой модели $\omega_0$ подбирается из условия сохранения циркуляции:

    $$
    \int_{\psi < 0} \omega(\psi) \, d\mathbf{x} = \Gamma
    $$

    """)

elif menu == "Результаты":
    st.markdown("##### Результаты расчётов")

    if df is not None:
        st.markdown("**Параметры:** h = 1.0, level3, p = 2, Γ = −2.0")

        st.markdown("**Сводная таблица:**")
        df_display = df[['model', 'S', 'omega_scale', 'psi_min', 'x_attach',
                         'y_max_vortex', 'n_iterations']].copy()
        for col in ['S', 'omega_scale', 'psi_min', 'x_attach', 'y_max_vortex']:
            df_display[col] = df_display[col].apply(lambda x: f"{x:.4f}" if pd.notna(x) else "")
        df_display['model'] = df_display['model'].map(model_names)
        df_display = df_display.rename(columns={
            'model': 'Модель', 'S': 'S', 'omega_scale': 'ω₀',
            'psi_min': 'Минимум ψ', 'x_attach': 'Точка присоед.',
            'y_max_vortex': 'Высота вихря', 'n_iterations': 'Итерации'
        })
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        st.markdown("---")

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
                    st.image(conv_file, caption=f"Сходимость: {model_names.get(model_sel, model_sel)}",
                             use_container_width=True)

            st.markdown("**Характеристики:**")
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            with c1:
                st.metric("S", f"{row['S']:.4f}")
            with c2:
                st.metric("ω₀", f"{row['omega_scale']:.4f}")
            with c3:
                st.metric("Минимум ψ", f"{row['psi_min']:.4f}")
            with c4:
                st.metric("Точка присоед.", f"{row['x_attach']:.4f}")
            with c5:
                st.metric("Высота вихря", f"{row['y_max_vortex']:.4f}")
            with c6:
                st.metric("Итерации", int(row['n_iterations']))

        st.markdown("---")
        st.markdown("**Сравнение полей ψ для всех моделей:**")
        cols = st.columns(3)
        for i, (_, row) in enumerate(df.iterrows()):
            with cols[i]:
                if os.path.exists(row['psi_path']):
                    st.image(row['psi_path'],
                             caption=f"{model_names.get(row['model'], row['model'])}",
                             use_container_width=True)

        st.markdown("**Замечание:** Визуально поля ψ для трёх моделей близки, но количественные "
                    "различия видны в профилях ψ и ω (см. соответствующий раздел).")
    else:
        st.warning("Результаты не найдены. Запустите `python run_omega_calculations.py`")

elif menu == "Характеристики вихря":
    st.markdown("##### Геометрия вихревой зоны")

    if df is not None:
        st.markdown("""
        **Характеристики вихревой зоны для разных моделей ω(ψ):**

        - **Минимум ψ** — минимальное значение функции тока (достигается в центре вихря)
        - **Точка присоединения** — координата x₁, где ψ = 0 на нижней стенке после уступа
        - **Высота вихря** — максимальная координата x₂ среди точек с ψ < 0
        - **Центр вихря** — координаты точки с минимальным значением ψ
        """)

        df_char = df[['model', 'psi_min', 'x_attach', 'y_max_vortex',
                      'x_vortex_center', 'y_vortex_center']].copy()
        for col in ['psi_min', 'x_attach', 'y_max_vortex', 'x_vortex_center', 'y_vortex_center']:
            df_char[col] = df_char[col].apply(lambda x: f"{float(x):.4f}" if pd.notna(x) else "")
        df_char['model'] = df_char['model'].map(model_names)
        df_char = df_char.rename(columns={
            'model': 'Модель', 'psi_min': 'Минимум ψ', 'x_attach': 'Точка присоед.',
            'y_max_vortex': 'Высота вихря', 'x_vortex_center': 'X центра', 'y_vortex_center': 'Y центра'
        })
        st.dataframe(df_char, use_container_width=True, hide_index=True)

        st.markdown("""
        **Наблюдения:**
        - Точка присоединения и высота вихря практически одинаковы для всех моделей — граница ψ = 0 не меняется
        - Минимум ψ немного различается: наибольший по модулю у постоянной модели, наименьший — у экспоненциальной
        - Распределение ω(ψ) влияет на интенсивность вихря (значение ψ в центре), но не на его геометрические размеры
        """)
    else:
        st.warning("Результаты не найдены.")

elif menu == "Сравнение моделей":
    st.markdown("##### Сравнение моделей ω(ψ)")

    if df is not None:
        st.markdown("**Интегральные характеристики:**")

        models = df['model'].values
        S_vals = df['S'].values
        omega_vals = df['omega_scale'].values
        psi_min_vals = df['psi_min'].values

        col1, col2, col3 = st.columns(3)
        with col1:
            fig, ax = plt.subplots(figsize=(5, 4))
            colors = ['#2196F3', '#4CAF50', '#FF9800']
            model_labels = [model_names.get(m, m) for m in models]
            bars = ax.bar(model_labels, S_vals, color=colors, edgecolor='black', linewidth=1.5)
            ax.set_ylabel('S')
            ax.set_title('Площадь вихревой зоны')
            for bar, val in zip(bars, S_vals):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.002,
                        f'{val:.4f}', ha='center', fontsize=10)
            fig.tight_layout()
            st.pyplot(fig)

        with col2:
            fig, ax = plt.subplots(figsize=(5, 4))
            bars = ax.bar(model_labels, np.abs(omega_vals), color=colors, edgecolor='black', linewidth=1.5)
            ax.set_ylabel('|ω₀|')
            ax.set_title('Масштаб завихрённости')
            for bar, val in zip(bars, np.abs(omega_vals)):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                        f'{val:.4f}', ha='center', fontsize=10)
            fig.tight_layout()
            st.pyplot(fig)

        with col3:
            fig, ax = plt.subplots(figsize=(5, 4))
            bars = ax.bar(model_labels, np.abs(psi_min_vals), color=colors, edgecolor='black', linewidth=1.5)
            ax.set_ylabel('|ψ_min|')
            ax.set_title('Интенсивность вихря')
            for bar, val in zip(bars, np.abs(psi_min_vals)):
                ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.0005,
                        f'{val:.4f}', ha='center', fontsize=10)
            fig.tight_layout()
            st.pyplot(fig)

        st.markdown("""
        **Анализ:**

        - **Площадь S** практически одинакова для всех моделей — граница вихря определяется интегральным условием ∫ ω = Γ
        - **Масштаб |ω₀|** растёт от постоянной модели к экспоненциальной — при непостоянном ω(ψ) нужно увеличить пиковое значение, чтобы сохранить циркуляцию
        - **Интенсивность |ψ_min|** падает от постоянной модели к экспоненциальной — более concentrated ω в центре даёт более «мелкий» профиль ψ
        """)
    else:
        st.warning("Результаты не найдены.")

elif menu == "Профили ψ и ω":
    st.markdown("##### Профили ψ и ω через центр вихря")

    st.markdown("""
    Для количественного сравнения моделей строятся профили вдоль вертикальной линии 
    x₁ = 1.5 (через центр вихревой зоны). Значения получены интерполяцией МКЭ-решения.
    """)

    if os.path.exists(profiles_png):
        st.image(profiles_png, caption="Сравнение профилей ψ и ω", use_container_width=True)

        if profiles_data is not None:
            st.markdown("**Численные значения в центре вихря и на границе:**")
            table_data = []
            for model in ['const', 'linear', 'exp']:
                if model in profiles_data:
                    p = profiles_data[model]
                    x2_arr = np.array(p['x2'])
                    psi_arr = np.array(p['psi'])
                    omega_arr = np.array(p['omega'])

                    # Индекс центра вихря (минимум psi)
                    idx_center = np.argmin(psi_arr)
                    # Индекс границы вихря (последняя точка с psi < 0)
                    idx_boundary = np.where(psi_arr < 0)[0]
                    idx_boundary = idx_boundary[-1] if len(idx_boundary) > 0 else idx_center

                    table_data.append({
                        'Модель': model_names.get(model, model),
                        'ω в центре': f"{omega_arr[idx_center]:.4f}",
                        'ω на границе': f"{omega_arr[idx_boundary]:.4f}",
                        'Отношение': f"{omega_arr[idx_center] / omega_arr[idx_boundary]:.2f}",
                        'Минимум ψ': f"{psi_arr[idx_center]:.4f}"
                    })

            df_prof = pd.DataFrame(table_data)
            st.dataframe(df_prof, use_container_width=True, hide_index=True)

        st.markdown("""
        - **Физический смысл:** распределение ω(ψ) влияет на интенсивность вихря (минимум ψ), 
          но слабо влияет на его геометрические размеры.
        """)
    else:
        st.warning("Профили не найдены. Запустите `python run_omega_calculations.py`.")

elif menu == "Код решателя":
    st.markdown("##### Код решателя")

    st.markdown("**Инициализация и краевые условия:**")
    st.code('''V = FunctionSpace(mesh, 'P', degree)
psi, phi = TrialFunction(V), TestFunction(V)

bc_G1 = DirichletBC(V, Constant(0.0), boundaries, 1)   # Gamma1: psi = 0
bc_G2 = DirichletBC(V, Constant(H), boundaries, 2)     # Gamma2: psi = H
inflow_expr = Expression('H * x[1]', H=H, degree=degree)
bc_G3 = DirichletBC(V, inflow_expr, boundaries, 3)     # Gamma3: psi = H*x2
bcs = [bc_G1, bc_G2, bc_G3]

a = dot(grad(psi), grad(phi)) * dx
DG0 = FunctionSpace(mesh, 'DG', 0)''', language="python")

    st.markdown("**Вычисление ω(ψ) в каждом вихревом элементе:**")
    st.code('''for i in range(DG0.dim()):
    if marker_vals[i] > 0:  # элемент в вихревой зоне
        psi_i = psi_interp(coords_DG[i])  # значение psi в центре элемента
        if omega_model == "const":
            omega_vals[i] = 1.0
        elif omega_model == "linear":
            omega_vals[i] = max(1.0 - 0.5 * abs(psi_i) / 0.3, 0.2)
        elif omega_model == "exp":
            omega_vals[i] = np.exp(0.5 * psi_i / psi_ref_val)

# Нормировка: ∫ ω dS = Γ
integral_omega = assemble(omega_func * dx)
omega_scale = Gamma / integral_omega
omega_func *= omega_scale''', language="python")

    st.markdown("**Итерационный процесс (аналогично базовой модели):**")
    st.code('''for k in range(max_iter):
    # Определение вихревой зоны, сборка правой части с ω(ψ)
    # Решение уравнения Пуассона, проверка сходимости
    ...''', language="python")

    st.markdown("**Вычисление профилей вдоль линии x₁ = 1.5:**")
    st.code('''def compute_profiles(psi, omega_func, mesh, degree):
    x1_profile = 1.5
    x2_vals = np.linspace(x2_min, 0.0, 50)
    psi_vals = np.array([psi(x1_profile, x2) for x2 in x2_vals])
    omega_vals = np.array([omega_func(x1_profile, x2) for x2 in x2_vals])
    return {"x2": x2_vals, "psi": psi_vals, "omega": omega_vals}''', language="python")

elif menu == "Выводы":
    st.markdown(r"""
    ##### Выводы

    **1. Влияние распределения ω(ψ) на интегральные характеристики:**

    - Площадь вихря S практически не зависит от модели — граница определяется интегральным условием ∫ ω = Γ
    - Пиковое значение |ω₀| растёт с увеличением неоднородности: от постоянной модели к экспоненциальной
    - Интенсивность вихря |ψ_min| падает при более концентрированном распределении ω

    **2. Геометрия вихревой зоны:**

    - Точка присоединения и высота вихря не зависят от модели ω(ψ)
    - Это фундаментальное свойство: оператор Лапласа сглаживает неоднородности правой части

    **3. Профили ψ и ω:**

    - Профили ψ(x₂) качественно одинаковы, но количественно различаются по глубине минимума (~18%)
    - Профили ω(x₂) существенно различаются по форме: от постоянного до спадающего
    - Разница в распределении ω слабо влияет на геометрию вихря, но заметно влияет на интенсивность

    **4. Сходимость итераций:**

    - Все три модели сходятся за 14–23 итерации
    - Экспоненциальная модель требует несколько больше итераций из-за нелинейной связи ω(ψ)

    **5. Физическая интерпретация:**

    - **Постоянная модель:** простейшее предположение, даёт наиболее интенсивный вихрь
    - **Линейная модель:** промежуточный случай с умеренной концентрацией ω
    - **Экспоненциальная модель:** наиболее плавное распределение, качественно ближе к модели Навье-Стокса

    **6. Сравнение с моделью Навье-Стокса:**

    - В модели Навье-Стокса завихрённость в отрывной зоне затухает от центра к границе — качественно ближе к экспоненциальной модели
    - Однако в модели Навье-Стокса есть вторичные вихри и более сложная структура течения
    - Вихре-потенциальная модель не воспроизводит вторичные вихри, но даёт правильную форму основной вихревой зоны
    """)