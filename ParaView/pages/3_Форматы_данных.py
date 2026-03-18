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

    st.markdown("### VTK Legacy Format (устаревший)")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Характеристики**")
        st.markdown("- Расширение: .vtk")
        st.markdown("- Текстовый или бинарный формат")
        st.markdown("- Подходит для отладки")

    with col2:
        st.markdown("**Структура файла**")
        st.markdown("- Заголовок (тип данных)")
        st.markdown("- Геометрия (точки и ячейки)")
        st.markdown("- Атрибуты (скаляры, векторы)")

    st.markdown("### VTK XML Formats (рекомендованные)")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Расширения**")
        st.markdown("- .vtu — неструктурированная сетка")
        st.markdown("- .vts — структурированная")
        st.markdown("- .vtr — прямоугольная")
        st.markdown("- .vti — изображение/вокселы")
        st.markdown("- .vtp — полигональные данные")
        st.markdown("- .vtm — мультиблок")

    with col2:
        st.markdown("**Преимущества**")
        st.markdown("- Параллельный ввод/вывод")
        st.markdown("- Поддержка сжатия")
        st.markdown("- Частичная загрузка данных")
        st.markdown("- Современный стандарт")

    with col3:
        st.markdown("**Форматы файлов**")
        st.markdown("- XML (читаемый)")
        st.markdown("- Бинарный (компактный)")
        st.markdown("- Сжатый (экономия места)")

elif menu == "Поддерживаемые сторонние форматы":

    st.markdown("### Инженерные и CAD форматы")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**STL**")
        st.markdown("- Расширение: .stl")
        st.markdown("- 3D-печать")
        st.markdown("- Поверхностные сетки")

    with col2:
        st.markdown("**OBJ**")
        st.markdown("- Расширение: .obj")
        st.markdown("- Геометрия с текстурами")
        st.markdown("- Wavefront формат")

    st.markdown("### Научные форматы")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**NetCDF**")
        st.markdown("- Климат")
        st.markdown("- Океанология")
        st.markdown("- Сетки")

    with col2:
        st.markdown("**HDF5**")
        st.markdown("- Иерархический формат")
        st.markdown("- Требуется настройка")
        st.markdown("- Плагины")

    with col3:
        st.markdown("**Exodus II**")
        st.markdown("- Расширение: .exo")
        st.markdown("- Механика")
        st.markdown("- Прочностные расчеты")

    st.markdown("### Форматы гидродинамики (CFD)")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**OpenFOAM**")
        st.markdown("- Открывает папку case")
        st.markdown("- Прямая загрузка")

    with col2:
        st.markdown("**CGNS**")
        st.markdown("- CFD General Notation")
        st.markdown("- Аэро- и гидродинамика")

    with col3:
        st.markdown("**Ensight**")
        st.markdown("- Аэродинамика")
        st.markdown("- Популярный формат")

    st.markdown("### Медицина")

    st.markdown("**DICOM**")
    st.markdown("- Медицинские изображения")
    st.markdown("- Через плагин или конвертацию")

    st.markdown("---")

    st.markdown("### Как открыть данные")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Встроенные источники (для практики)**")
        st.markdown("Sources → Wavelet (синтетические 3D-данные)")
        st.markdown("Sources → Sphere (сфера)")
        st.markdown("Sources → Cylinder (цилиндр)")
        st.markdown("Sources → Cone (конус)")
        st.markdown("Sources → Mandelbrot (фрактал)")
        st.markdown("Sources → RTAnalytic (аналитические данные)")

    with col2:
        st.markdown("**Открытие файла**")
        st.markdown("1. File → Open (Ctrl+O)")
        st.markdown("2. Выбрать файл")
        st.markdown("3. Нажать OK")
        st.markdown("4. В Properties нажать Apply")