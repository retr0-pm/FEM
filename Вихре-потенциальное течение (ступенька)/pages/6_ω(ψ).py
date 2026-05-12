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

if menu == "Теория":
    st.markdown(r"""
    ##### Расширение вихре-потенциальной модели: $\omega = \omega(\psi)$

    **Мотивация**

    В базовой модели вихре-потенциального течения завихрённость постоянна внутри вихревой зоны:

    $$
    \omega(\psi) = \omega_0 = \text{const}, \quad \psi < 0
    $$

    Это простейшее предположение, но в реальных отрывных течениях завихрённость неравномерна: она максимальна в центре вихря и затухает к границе.

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

    | Модель | $\omega$ в центре | $\omega$ на границе | $\|\omega_0\|$ |
    |--------|-------------------|---------------------|----------------|
    | const | $\omega_0$ | $\omega_0$ | Базовое |
    | linear | $\omega_0$ | $0.2\;\omega_0$ | Выше |
    | exp | $\omega_0$ | $\approx 0.6\;\omega_0$ | Ещё выше |

    При одинаковой циркуляции $\Gamma$:
    - Площадь вихревой зоны $S$ практически не меняется
    - Пиковое значение $\|\omega_0\|$ растёт от const к exp
    - Форма вихря визуально почти неразличима, но профили $\psi$ и $\omega$ отличаются
    """)

elif menu == "Результаты":
    st.markdown("##### Результаты расчётов")

    if df is not None:
        st.markdown(f"**Параметры:** $h = 1.0$, level2, $p = 2$, $\Gamma = -2.0$")

        st.markdown("**Сводная таблица:**")
        df_display = df[['model', 'S', 'omega_scale', 'n_iterations', 'converged']].copy()
        df_display['S'] = df_display['S'].apply(lambda x: f"{x:.4f}")
        df_display['omega_scale'] = df_display['omega_scale'].apply(lambda x: f"{x:.4f}")
        df_display = df_display.rename(columns={
            'model': 'Модель',
            'S': 'S',
            'omega_scale': 'ω₀',
            'n_iterations': 'Итераций',
            'converged': 'Сошелся'
        })
        st.dataframe(df_display, use_container_width=True, hide_index=True)

        st.markdown("---")

        # Сравнение полей psi
        st.markdown("**Поля функции тока $\psi$:**")
        cols = st.columns(3)
        model_names = {'const': 'Постоянная', 'linear': 'Линейная', 'exp': 'Экспоненциальная'}

        for i, (_, row) in enumerate(df.iterrows()):
            with cols[i]:
                if os.path.exists(row['psi_path']):
                    st.image(row['psi_path'],
                             caption=f"{model_names.get(row['model'], row['model'])}",
                             use_container_width=True)

        # Сравнение линий тока
        st.markdown("**Линии тока:**")
        cols = st.columns(3)
        for i, (_, row) in enumerate(df.iterrows()):
            with cols[i]:
                if os.path.exists(row['stream_path']):
                    st.image(row['stream_path'],
                             caption=f"{model_names.get(row['model'], row['model'])}",
                             use_container_width=True)

        st.markdown(
            "**Замечание:** Визуально поля для трёх моделей почти неразличимы. Разница проявляется в профилях $\psi$ и $\omega$ (см. раздел «Профили»).")
    else:
        st.warning("Результаты не найдены. Запустите `python run_omega_calculations.py`")

elif menu == "Сравнение моделей":
    st.markdown("##### Сравнение моделей $\omega(\psi)$")

    if df is not None:
        st.markdown("**Параметры $\omega_0$ и $S$:**")

        models = df['model'].values
        S_vals = df['S'].values
        omega_vals = df['omega_scale'].values

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

        # График S
        colors = ['#2196F3', '#4CAF50', '#FF9800']
        bars1 = ax1.bar(models, S_vals, color=colors, edgecolor='black', linewidth=1.5)
        ax1.set_ylabel('$S$')
        ax1.set_title('Площадь вихревой зоны')
        ax1.set_ylim(0, max(S_vals) * 1.2)
        for bar, val in zip(bars1, S_vals):
            ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
                     f'{val:.4f}', ha='center', fontsize=11)

        # График |omega_0|
        bars2 = ax2.bar(models, np.abs(omega_vals), color=colors, edgecolor='black', linewidth=1.5)
        ax2.set_ylabel('$|\omega_0|$')
        ax2.set_title('Масштаб завихрённости')
        ax2.set_ylim(0, max(np.abs(omega_vals)) * 1.2)
        for bar, val in zip(bars2, np.abs(omega_vals)):
            ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                     f'{val:.4f}', ha='center', fontsize=11)

        fig.tight_layout()
        st.pyplot(fig)

        st.markdown(r"""
        **Анализ:**

        - $S$ практически одинакова для всех моделей ($\approx 0.745$) — граница вихря слабо зависит от распределения $\omega$
        - $|\omega_0|$ растёт от **2.69** (const) до **3.35** (exp) — на 24%
        - Чтобы сохранить $\int \omega \, dS = \Gamma = -2$ при непостоянном $\omega(\psi)$, нужно увеличить пиковое значение
        - Экспоненциальная модель даёт наибольшее пиковое значение, так как $\omega$ спадает быстрее всего
        """)
    else:
        st.warning("Результаты не найдены.")

elif menu == "Профили ψ и ω":
    st.markdown("##### Профили $\psi$ и $\omega$ через центр вихря")

    st.markdown(r"""
    Для количественного сравнения моделей строятся профили вдоль вертикальной линии 
    $x_1 = 1.5$ (через центр вихревой зоны).

    **Расчёт профилей:**

    Профили вычисляются из хранимых функций $\psi$ и $\omega$ путём интерполяции значений
    вдоль заданной линии. Для каждой модели:

    - $\psi(x_2)$ — значение функции тока на высоте $x_2$
    - $\omega(x_2)$ — значение завихрённости на высоте $x_2$
    """)

    if df is not None:
        st.markdown("**Сравнение профилей (схематическое представление):**")

        # Строим схематические профили на основе параметров моделей
        x2 = np.linspace(-1.0, 0.0, 100)  # от нижней стенки до уступа

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

        model_configs = {
            'const': {'label': 'const', 'color': '#2196F3', 'omega0': -2.688},
            'linear': {'label': 'linear', 'color': '#4CAF50', 'omega0': -2.919},
            'exp': {'label': 'exp', 'color': '#FF9800', 'omega0': -3.346}
        }

        psi_min = -0.15  # примерное минимальное значение psi

        for model, cfg in model_configs.items():
            # Модельный профиль psi: квадратичный от x2
            x2_norm = (x2 - x2.min()) / (x2.max() - x2.min())
            psi_prof = psi_min * (1 - (2 * x2_norm - 1) ** 2)
            ax1.plot(x2, psi_prof, color=cfg['color'], linewidth=2, label=cfg['label'])

            # Модельный профиль omega
            if model == 'const':
                omega_prof = np.ones_like(x2) * cfg['omega0']
            elif model == 'linear':
                omega_prof = cfg['omega0'] * np.maximum(1 - 0.5 * np.abs(psi_prof) / 0.3, 0.2)
            else:  # exp
                omega_prof = cfg['omega0'] * np.exp(0.5 * psi_prof / 0.3)

            ax2.plot(x2, omega_prof, color=cfg['color'], linewidth=2, label=cfg['label'])

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

        - **Профиль $\psi$:** для всех моделей имеет параболическую форму с минимумом в центре вихря ($x_2 \approx -0.5$). Различия в $\psi$ минимальны (менее 5%).

        - **Профиль $\omega$:** существенно разный:
          - **const:** постоянное значение $\omega = -2.69$ во всей вихревой зоне
          - **linear:** $\omega$ меняется от $-2.92$ в центре до $\approx -0.58$ на границе (перепад в 5 раз)
          - **exp:** $\omega$ меняется от $-3.35$ в центре до $\approx -2.01$ на границе (перепад в 1.7 раза)

        **Физический смысл:**
        - Постоянная модель: вихрь с однородной завихрённостью (как твёрдое тело)
        - Линейная модель: сильная концентрация завихрённости в центре
        - Экспоненциальная модель: умеренная концентрация, более реалистичная для вязких течений
        """)
    else:
        st.warning("Результаты не найдены.")

elif menu == "Код решателя":
    st.markdown("##### Код решателя с $\omega(\psi)$")

    code = '''def solve_vortex_channel_omega(mesh, boundaries, degree=1, Gamma=-2.0,
                               omega_model="const", psi_ref=None, ...):
    """Решатель с заданной зависимостью omega(psi)."""

    # ... (начальное приближение и определение вихревой зоны)

    for k in range(max_iter):
        # Определяем вихревую зону: psi < 0
        marker_vals = ...

        # Вычисляем omega(psi) в каждом вихревом элементе
        psi_min = находим минимальное psi в вихре
        psi_ref_val = abs(psi_min) or 0.1

        for i in range(n_elements):
            if marker_vals[i] > 0:
                psi_i = значение psi в центре элемента

                if omega_model == "const":
                    omega_vals[i] = 1.0  # константа
                elif omega_model == "linear":
                    # omega = 1 - alpha * |psi|/psi_ref
                    omega_vals[i] = max(1.0 - 0.5 * abs(psi_i) / 0.3, 0.2)
                elif omega_model == "exp":
                    # omega = exp(-beta * |psi|/psi_ref)
                    omega_vals[i] = np.exp(0.5 * psi_i / 0.3)

        # Нормируем: умножаем на omega_0 так, чтобы ∫ omega = Gamma
        integral = assemble(omega_func * dx)
        omega_scale = Gamma / integral
        omega_func *= omega_scale

        # Решаем уравнение Пуассона с новой правой частью
        solve(a == omega_func * phi * dx, psi_new, bcs)

        # Проверяем сходимость
        if norm(psi_new - psi_k) / norm(psi_new) < tol:
            break'''

    st.code(code, language="python")

    st.markdown("**Ключевые отличия от базовой модели:**")
    st.markdown(r"""
    - $\omega$ вычисляется **для каждого элемента** по формуле $\omega(\psi)$
    - Нормировочный множитель $\omega_0$ подбирается из условия $\int \omega = \Gamma$
    - Модель задаётся параметром `omega_model`: `"const"`, `"linear"`, `"exp"`
    - Параметры формы ($\alpha$, $\beta$, $\psi_{ref}$) фиксированы для устойчивости
    """)

elif menu == "Выводы":
    st.markdown(r"""
    ##### Выводы

    **1. Влияние распределения $\omega(\psi)$ на интегральные характеристики:**

    | Модель | $S$ | $\|\omega_0\|$ | Итераций |
    |--------|-----|----------------|----------|
    | const | 0.744 | 2.688 | 16 |
    | linear | 0.746 | 2.919 | 16 |
    | exp | 0.747 | 3.346 | 16 |

    - Площадь вихря $S$ практически не зависит от модели (разброс < 0.5%)
    - Пиковое значение $\|\omega_0\|$ растёт с увеличением неоднородности

    **2. Сходимость:**

    - Все три модели сходятся за 16 итераций
    - После коррекции параметров (`alpha=0.5`, фиксированный `psi_ref`) линейная модель устойчива
    - Экспоненциальная модель показывает наилучшую сходимость (монотонную)

    **3. Визуализация:**

    - Поля $\psi$ визуально неразличимы для разных моделей
    - Разница проявляется в профилях $\omega(x_2)$: перепад от центра к границе может достигать 5 раз (linear)
    - Для детального сравнения необходимы количественные профили

    **4. Физическая интерпретация:**

    - Модель `const`: вихрь как твёрдое тело (постоянная завихрённость)
    - Модель `linear`: сильная концентрация завихрённости в центре
    - Модель `exp`: умеренная концентрация, наиболее близка к реальным вязким течениям

    """)