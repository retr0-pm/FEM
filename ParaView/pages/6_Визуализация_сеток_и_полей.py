import streamlit as st
import os

st.set_page_config(
    page_title="ParaView: Визуализация сеток и полей",
    layout="wide"
)

st.title("ParaView: Визуализация сеток и полей")

menu = st.sidebar.radio(
    "Выберите раздел:",
    ["Типы сеток",
     "Скалярные поля",
     "Векторные поля",
     "Тензорные поля"]
)

# --- ТИПЫ СЕТОК ---
if menu == "Типы сеток":

    st.markdown("### Классификация сеток в ParaView")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Структурированные сетки**
        - Регулярное расположение точек
        - Неявная топология (экономия памяти)
        - Форматы: .vts, .vtr, .vti

        **Неструктурированные сетки**
        - Произвольное расположение точек
        - Явная топология (гибкость)
        - Форматы: .vtu, .vtk
        """)

    with col2:
        st.markdown("""
        **Полигональные данные**
        - Поверхности, треугольники, четырехугольники
        - Форматы: .vtp, .stl, .obj

        **Мультиблоковые данные**
        - Объединение нескольких сеток
        - Формат: .vtm
        """)

    st.markdown("### Отображение сетки")

    st.markdown("""
    **Representation (вид):**
    - Surface — поверхность
    - Wireframe — каркас (только линии)
    - Surface With Edges — поверхность + каркас
    - Points — точки
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.image("images/6_1.jpg", caption="Surface")
        st.image("images/6_2.jpg", caption="Wireframe")

    with col2:
        st.image("images/6_3.jpg", caption="Surface With Edges")
        st.image("images/6_4.jpg", caption="Points")

    st.markdown("### Рекомендации по работе с сетками")

    st.markdown("""
    **Для структурированных сеток:**
    - Используйте Extract Subset для выборки подобласти (без преобразования в неструктурированную)
    - Slice и Contour безопасны — уменьшают размерность
    - Избегайте Clip и Threshold на структурированных сетках (преобразуют в неструктурированную)

    **Для больших данных:**
    - Применяйте фильтры, уменьшающие размерность, как можно раньше
    - Contour и Slice предпочтительнее Clip и Threshold
    - Неструктурированные сетки потребляют больше памяти на ячейку
    """)

# --- СКАЛЯРНЫЕ ПОЛЯ ---
elif menu == "Скалярные поля":

    st.markdown("### Скалярные поля")

    st.markdown("""
    Скалярное поле — это распределение некоторой величины по пространству (температура, давление, высота).
    Визуализируется с помощью цветовых карт и изолиний.
    """)

    st.markdown("#### Цветовые карты (Color Maps)")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Настройка:**
        1. Выбрать объект в Pipeline Browser
        2. В Display → Coloring выбрать скалярный массив
        3. Нажать кнопку Edit (рядом с выбором цвета)
        4. В Color Map Editor настроить:
           - Цветовую схему
           - Диапазон (авто или вручную)
           - Прозрачность
           - Логарифмическую шкалу
        """)

        st.image("images/6_5.jpg", caption="Color Map Editor")

    with col2:
        st.markdown("""
        **Популярные цветовые карты:**
        - Jet — радуга (классика)
        - Cool to Warm — синий-белый-красный
        - Viridis/Magma — perceptually uniform
        - Gray Scale — оттенки серого
        """)

    st.markdown("#### Elevation")

    st.markdown("""
    **Фильтр Elevation** создает скалярное поле по высоте (координате Z) — для раскраски геометрии по высоте.

    **Последовательность действий:**
    1. Sources → Cylinder → Apply
    2. Выбрать Cylinder1 → Filters → Alphabetical → Elevation
    3. Настроить Low Point и High Point (диапазон высот)
    4. Apply
    5. Раскрасить по массиву Elevation
    """)

    st.image("images/6_6.jpg", caption="Cylinder с Elevation")

    st.markdown("#### Изоповерхности (Contour)")

    st.markdown("""
    **Фильтр Contour** создает поверхности постоянного значения скаляра.

    **Последовательность действий (на примере disk_out_ref.ex2):**
    1. File → Open → disk_out_ref.ex2 → отметить массив Temp → Apply
    2. Выбрать источник → Filters → Common → Contour
    3. В Properties выбрать массив Temp
    4. Задать значения изолиний: кнопка Range → Min=300, Max=400, Contours=5 → OK
    5. Apply
    """)

    st.image("images/6_7.jpg", caption="Изоповерхности температуры на disk_out_ref")

# --- ВЕКТОРНЫЕ ПОЛЯ ---
elif menu == "Векторные поля":

    st.markdown("### Векторные поля")

    st.markdown("""
    Векторное поле описывает направление и величину в каждой точке (скорость, сила).
    """)

    st.markdown("#### Glyph (глифы)")

    st.markdown("""
    Глифы — геометрические фигуры (стрелки, конусы), ориентированные по направлению вектора.

    **Последовательность действий (на примере disk_out_ref.ex2 с массивом V):**
    1. File → Open → disk_out_ref.ex2 → отметить массив V → Apply
    2. Выбрать источник → Filters → Common → Glyph
    3. В Properties:
       - Vectors → V
       - Scale Factor = 0.5
       - Glyph Type = Arrow
       - Apply
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.image("images/6_8.jpg", caption="Glyph (стрелки)")

    with col2:
        st.image("images/6_9.jpg", caption="Glyph (конусы)")

    st.markdown("**Параметры Glyph:**")
    st.markdown("""
    - **Scale Factor** — общий размер глифов
    - **Scale Array** — масштабировать по скаляру
    - **Glyph Mode** — размещение:
      - All Points — во всех точках
      - Uniform Random — случайная выборка
      - Every Nth Point — каждый N-й узел
    """)

    st.markdown("#### Stream Tracer (линии тока)")

    st.markdown("""
    Линии тока показывают траектории частиц в векторном поле.

    **Последовательность действий:**
    1. Выбрать disk_out_ref.ex2
    2. Filters → Common → Stream Tracer
    3. В Properties:
       - Vectors → V
       - Seed Type = Point Source
       - В Point Source указать центр (например, 0, 0, 0)
       - Integration Direction = BOTH
       - Apply
    """)

    st.image("images/6_10.jpg", caption="Stream Tracer (линии тока)")

# --- ТЕНЗОРНЫЕ ПОЛЯ ---
elif menu == "Тензорные поля":

    st.markdown("### Тензорные поля")

    st.markdown("""
    Тензорные поля (напряжения, деформации) визуализируются через собственные значения и собственные векторы с помощью фильтра **Tensor Glyph**.
    """)

    st.markdown("#### Tensor Glyph")

    st.markdown("""
    **Последовательность действий (на примере tensors.vtk):**
    1. File → Open → tensors.vtk → Apply
    2. Выбрать источник → Filters → Alphabetical → Tensor Glyph
    3. В Properties:
       - Tensors — выбрать тензорный массив
       - Glyph Type = Ellipsoid
       - Scale Factor = 0.2
       - Apply
    """)

    st.image("images/6_11.jpg", caption="Tensor Glyph (эллипсоиды)")

    st.markdown("""
    **Параметры Tensor Glyph:**

    - **Tensors** — имя тензорного массива (симметричный, компоненты: XX, YY, ZZ, XY, YZ, XZ)
    - **Glyph Type** — форма глифа: Ellipsoid, Cuboid, Cylinder, Superquadric
    - **Three Glyphs** — три глифа в каждой точке (по одному на каждый собственный вектор)
    - **Extract Eigenvalues** — извлечь собственные значения как отдельные массивы
    - **Color Glyphs** — раскраска глифов (по собственным значениям или входным скалярам)

    **Интерпретация:**
    - Главные оси эллипсоида соответствуют собственным векторам
    - Размер вдоль оси пропорционален собственному значению
    - Цвет отражает величину собственного значения
    """)