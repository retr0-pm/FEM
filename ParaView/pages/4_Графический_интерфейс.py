import streamlit as st
import os

st.set_page_config(
    page_title="ParaView: Графический интерфейс",
    layout="wide"
)

st.title("ParaView: Графический интерфейс")

menu = st.sidebar.radio(
    "Выберите раздел:",
    ["Основные элементы интерфейса",
     "Панели инструментов и настройка",
     "Управление через командную строку и скрипты"]
)

if menu == "Основные элементы интерфейса":

    st.markdown("""
    ### Структура главного окна

    1. **Меню (Menu Bar)** — верхняя строка (File, Edit, View, Sources, Filters, Tools)
    2. **Панель инструментов (Toolbars)** — иконки под меню
    3. **Pipeline Browser** — дерево построения визуализации
    4. **Properties Panel** — настройки выбранного объекта
    5. **3D View** — окно отображения геометрии
    6. **Color Legend** — легенда цветовой шкалы
    """)

    st.markdown("### Создание объекта")

    col1, col2 = st.columns(2)

    with col1:
        st.image("images/1.jpg", caption="Sources → Shapes")

    with col2:
        st.image("images/2.jpg", caption="Cylinder (после Apply)")

    st.markdown("### Pipeline Browser")
    st.markdown(
        "Отображает дерево построения: источник данных → фильтры. Позволяет включать/выключать видимость объектов.")

elif menu == "Панели инструментов и настройка":

    st.markdown("### Properties Panel")

    col1, col2 = st.columns(2)

    with col1:
        st.image("images/3.jpg", caption="Properties (вкладка)")
        st.image("images/4.jpg", caption="Display (вкладка)")

    with col2:
        st.image("images/5.jpg", caption="Information (вкладка)")

    st.markdown("### Настройка отображения")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.image("images/6.jpg", caption="Styling")

    with col2:
        st.image("images/7.jpg", caption="Styling (продолжение)")

    st.markdown("### Фильтры")

    col1, col2 = st.columns(2)

    with col1:
        st.image("images/8.jpg", caption="Filters → Common → Slice")

    with col2:
        st.image("images/9.jpg", caption="Slice (пример 1)")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.image("images/10.jpg", caption="Slice (пример 2)")

    with col2:
        st.image("images/11.jpg", caption="Slice (пример 3)")

    with col3:
        st.image("images/12.jpg", caption="Slice (пример 4)")

    st.markdown("### Пример пайплайна")

    col1, col2 = st.columns(2)

    with col1:
        st.image("images/13.jpg", caption="Cylinder + Slice")

    with col2:
        st.image("images/14.jpg", caption="+ Elevation")

    st.markdown("### Extract Edges")
    st.image("images/15.jpg", caption="ExtractEdges")

    st.markdown("### Сохранение")

    col1, col2 = st.columns(2)

    with col1:
        st.image("images/16.jpg", caption="Save Screenshot")
        st.image("images/17.jpg", caption="Save State")

    with col2:
        st.image("images/18.jpg", caption="Save Data")
        st.image("images/19.jpg", caption="Configure writer")

    st.markdown("""
    **Форматы сохранения:**
    - PNG — скриншот с прозрачным фоном
    - JPG — скриншот с белым фоном
    - PVSM — проект ParaView (Save State)
    - VTK/STL/OBJ — геометрия (Save Data)
    """)

elif menu == "Управление через командную строку и скрипты":

    st.markdown("### pvpython (Python-интерфейс)")

    st.code("""
    from paraview.simple import *
    Sphere()
    Show()
    Render()
    SaveScreenshot('sphere.png')
    """)

    st.markdown("Запуск:")
    st.code("pvpython script.py")

    st.markdown("### pvbatch (параллельные скрипты)")
    st.markdown("Вариант pvpython для запуска в распределённом режиме (MPI) на кластерах.")

    st.markdown("### Python Trace (Запись действий)")
    st.markdown("Tools → Start Trace — записывает действия в виде Python-кода.")

    st.markdown("### Плагины")
    st.markdown("Tools → Manage Plugins — загрузка расширений.")