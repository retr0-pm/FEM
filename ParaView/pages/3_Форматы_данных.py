import streamlit as st

st.set_page_config(
    page_title="ParaView: Форматы данных",
    layout="wide"
)

st.title("ParaView: Форматы данных")

menu = st.sidebar.radio(
    "Выберите раздел:",
    ["Собственные форматы VTK",
     "Поддерживаемые сторонние форматы"]
)

if menu == "Собственные форматы VTK":

    st.markdown("### VTK Legacy Format")
    st.markdown("*Устаревший, но простой формат. Подходит для отладки и небольших данных.*")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Характеристики**")
        st.markdown("- Расширение: **.vtk**")
        st.markdown("- Текстовый (ASCII) или бинарный формат")
        st.markdown("- Читается человеком в текстовом режиме")
        st.markdown("- Не поддерживает параллельный ввод/вывод")
        st.markdown("- Нет встроенного сжатия")

    with col2:
        st.markdown("**Структура файла**")
        st.markdown("1. **Заголовок** — версия, тип данных")
        st.markdown("2. **Геометрия** — координаты точек и описание ячеек")
        st.markdown("3. **Атрибуты** — скалярные, векторные поля в точках или ячейках")

    st.markdown("**Пример структуры:**")
    st.code('''
# vtk DataFile Version 3.0
Пример данных
ASCII
DATASET STRUCTURED_POINTS
DIMENSIONS 10 10 10
ORIGIN 0 0 0
SPACING 1 1 1
POINT_DATA 1000
SCALARS temperature float
LOOKUP_TABLE default
0.0 0.1 0.2 0.3 ...
    ''')

    st.markdown("### VTK XML Formats")
    st.markdown("*Современный стандарт. Рекомендуется для новых проектов.*")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Типы сеток**")
        st.markdown("""
        - **.vtu** — неструктурированная сетка
        - **.vts** — структурированная сетка
        - **.vtr** — прямоугольная (rectilinear) сетка
        - **.vti** — изображение (равномерная сетка)
        - **.vtp** — полигональные данные
        - **.vtm** — мультиблок (несколько сеток в одном файле)
        """)

    with col2:
        st.markdown("**Преимущества**")
        st.markdown("""
        - Параллельный ввод/вывод (MPI)
        - Поддержка сжатия (zlib, lz4)
        - Частичная загрузка данных
        - Поддержка больших данных
        - Расширяемость
        """)

    with col3:
        st.markdown("**Форматы файлов**")
        st.markdown("""
        - **ASCII** — читаемый XML
        - **Binary** — компактный бинарный
        - **Compressed** — сжатый бинарный
        - **Appended** — данные в конце файла (для эффективности)
        """)

    st.markdown("**Пример .vtu (неструктурированная сетка):**")
    st.code('''<?xml version="1.0"?>
<VTKFile type="UnstructuredGrid" version="1.0" byte_order="LittleEndian">
  <UnstructuredGrid>
    <Piece NumberOfPoints="100" NumberOfCells="200">
      <Points>
        <DataArray type="Float32" NumberOfComponents="3" format="ascii">
          0.0 0.0 0.0  1.0 0.0 0.0  0.0 1.0 0.0 ...
        </DataArray>
      </Points>
      <Cells>
        <DataArray type="Int32" Name="connectivity" format="ascii">
          0 1 2  1 3 2 ...
        </DataArray>
        <DataArray type="Int32" Name="offsets" format="ascii">
          3 6 9 ...
        </DataArray>
        <DataArray type="UInt8" Name="types" format="ascii">
          5 5 5 ...
        </DataArray>
      </Cells>
    </Piece>
  </UnstructuredGrid>
</VTKFile>''')

elif menu == "Поддерживаемые сторонние форматы":

    st.markdown("""
    ParaView поддерживает множество форматов «из коробки» благодаря встроенным 
    модулям чтения и сторонним библиотекам.
    """)

    st.markdown("### Инженерные и CAD форматы")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**STL (Stereolithography)**")
        st.markdown("- Расширения: .stl")
        st.markdown("- Назначение: 3D-печать, поверхностные сетки")
        st.markdown("- Особенности: только геометрия, без атрибутов")

    with col2:
        st.markdown("**OBJ (Wavefront)**")
        st.markdown("- Расширения: .obj")
        st.markdown("- Назначение: геометрия с текстурами")
        st.markdown("- Особенности: поддерживает материалы (.mtl)")

    with col3:
        st.markdown("**STEP/IGES**")
        st.markdown("- Расширения: .step, .iges")
        st.markdown("- Назначение: CAD-модели")
        st.markdown("- Особенности: через плагины (ограниченная поддержка)")

    st.markdown("### Научные форматы")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**NetCDF**")
        st.markdown("- Расширения: .nc, .cdf")
        st.markdown("- Область: климат, океанология, атмосфера")
        st.markdown("- Особенности: самоописываемый формат")

    with col2:
        st.markdown("**HDF5**")
        st.markdown("- Расширения: .h5, .hdf5")
        st.markdown("- Область: универсальный научный формат")
        st.markdown("- Особенности: иерархическая структура, требует плагинов")

    with col3:
        st.markdown("**Exodus II**")
        st.markdown("- Расширения: .exo, .ex2")
        st.markdown("- Область: механика, прочностные расчеты")
        st.markdown("- Особенности: временные ряды, мультиблоки")

    st.markdown("""
    **FITS (Flexible Image Transport System)**
    - Расширения: .fits, .fit
    - Область: астрономия
    - Особенности: изображения и таблицы
    """)

    st.markdown("### Форматы гидродинамики (CFD)")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**OpenFOAM**")
        st.markdown("- Формат: директория case")
        st.markdown("- Область: вычислительная гидродинамика")
        st.markdown("- Особенности: открывает папку с расчетом напрямую")

    with col2:
        st.markdown("**CGNS**")
        st.markdown("- Расширения: .cgns")
        st.markdown("- Область: аэро- и гидродинамика")
        st.markdown("- Особенности: стандарт в авиастроении")

    with col3:
        st.markdown("**EnSight**")
        st.markdown("- Расширения: .case, .geo, .scl")
        st.markdown("- Область: аэродинамика, механика")
        st.markdown("- Особенности: популярный коммерческий формат")

    st.markdown("""
    **FLUENT/STAR-CCM+**
    - Расширения: .cas, .dat
    - Область: коммерческие CFD-пакеты
    - Особенности: прямая поддержка многих версий
    """)

    st.markdown("### Медицинские форматы")

    st.markdown("""
    **DICOM (Digital Imaging and Communications in Medicine)**
    - Расширения: .dcm (без расширения)
    - Область: медицинские изображения (КТ, МРТ)
    - Особенности: через плагин DICOM Reader или конвертацию в VTK
    """)

    st.markdown("### Визуализация и графика")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**PNG/JPEG/TIFF**")
        st.markdown("- 2D-изображения")
        st.markdown("- Текстуры и фоны")

    with col2:
        st.markdown("**BMP/PNM**")
        st.markdown("- Простые растровые форматы")
        st.markdown("- Для импорта текстур")

    st.markdown("---")

    st.markdown("### Работа с данными в ParaView")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Встроенные источники (для практики)**")
        st.markdown("""
        - **Sources → Wavelet** — синтетические 3D-данные (шумоподобный кубик)
        - **Sources → Sphere** — сфера
        - **Sources → Cylinder** — цилиндр
        - **Sources → Cone** — конус
        - **Sources → Mandelbrot** — фрактал Мандельброта
        - **Sources → RTAnalytic** — аналитические данные для тестов
        """)

    with col2:
        st.markdown("**Открытие файла**")
        st.markdown("""
        1. **File → Open** (или Ctrl+O)
        2. Выбрать файл в диалоговом окне
        3. Нажать **OK**
        4. В панели Properties нажать **Apply**

        ParaView автоматически определит тип файла и загрузит данные.
        """)

    st.markdown(
        "**Подсказка:** Для загрузки серии файлов (например, `solution_0000.vtk`, `solution_0001.vtk`) выберите первый файл и отметьте опцию **'File Series'** в диалоге открытия.")