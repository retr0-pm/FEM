import streamlit as st
import os

st.set_page_config(
    page_title="ParaView: Графический интерфейс",
    layout="wide"
)

st.title("ParaView: Графический интерфейс")

# Проверка наличия папки с изображениями
if not os.path.exists("images"):
    st.warning("Папка 'images' не найдена. Скриншоты не будут отображаться.")

menu = st.sidebar.radio(
    "Выберите раздел:",
    ["Основные элементы интерфейса",
     "Панели инструментов и настройка",
     "Управление через командную строку и скрипты"]
)

if menu == "Основные элементы интерфейса":

    st.markdown("### Структура главного окна")
    st.markdown("""
    После запуска ParaView главное окно делится на несколько функциональных зон:

    1. **Menu Bar (строка меню)** — верхняя строка с пунктами File, Edit, View, Sources, Filters, Tools, Help. Содержит все команды программы.

    2. **Toolbars (панели инструментов)** — иконки под меню для быстрого доступа к часто используемым командам. Настраиваются через View → Toolbars.

    3. **Pipeline Browser (браузер конвейера)** — левая часть окна. Отображает дерево построения визуализации: источник данных и примененные к нему фильтры. Позволяет включать/выключать видимость объектов (иконка глаза), удалять и переименовывать их.

    4. **Properties Panel (панель свойств)** — левая нижняя часть. При выборе объекта в Pipeline Browser здесь отображаются его настройки. Содержит вкладки:
       - Properties — параметры источника или фильтра
       - Display — настройки отображения (цвет, прозрачность, тип поверхности)
       - Information — информация о данных (размеры, диапазоны значений)

    5. **3D View (окно трехмерного вида)** — центральная область. Здесь отображается геометрия.

    6. **Color Legend (легенда цвета)** — появляется справа от 3D View при активной цветовой раскраске. Показывает соответствие цвета и значения.
    """)

    st.markdown("### Создание объекта")

    col1, col2 = st.columns(2)

    with col1:
        if os.path.exists("images/1.jpg"):
            st.image("images/1.jpg", caption="Sources → Shapes (выбор цилиндра)")
        else:
            st.info("Скриншот 1.jpg не найден")

        st.markdown("""
        **Последовательность действий:**
        1. В главном меню выбрать **Sources → Cylinder**
        2. В панели Properties нажать **Apply**
        3. В 3D View появится серый цилиндр
        4. В Pipeline Browser добавится элемент **Cylinder1**
        """)

    with col2:
        if os.path.exists("images/2.jpg"):
            st.image("images/2.jpg", caption="Цилиндр после Apply")
        else:
            st.info("Скриншот 2.jpg не найден")

    st.markdown("### Pipeline Browser")
    st.markdown("""
    **Pipeline Browser** — ключевой элемент управления пайплайном визуализации:

    - **Корень дерева** — источник данных (файл или встроенный источник)
    - **Ветви** — примененные фильтры (Contour, Slice, Clip и др.)
    - **Иконка глаза** — включение/отключение видимости объекта
    - **Контекстное меню (правый клик)** — удаление, переименование, копирование
    - **Порядок применения фильтров** — сверху вниз (нижний фильтр применяется к верхнему)
    """)

elif menu == "Панели инструментов и настройка":

    st.markdown("### Properties Panel (панель свойств)")

    st.markdown("""
    Панель свойств отображает настройки выбранного в Pipeline Browser объекта. Состоит из трех вкладок:
    """)

    col1, col2 = st.columns(2)

    with col1:
        if os.path.exists("images/3.jpg"):
            st.image("images/3.jpg", caption="Отображение Points")
        else:
            st.info("Скриншот 3.jpg не найден")

        st.markdown("""
        **Properties** — параметры источника или фильтра:
        - Для Cylinder: радиус, высота, разрешение
        - Для фильтров: специфичные настройки (направление среза, значение изолинии и т.д.)
        - Кнопка **Apply** — применить изменения
        - Кнопка **Reset** — сбросить к значениям по умолчанию
        """)

    with col2:
        if os.path.exists("images/4.jpg"):
            st.image("images/4.jpg", caption="Отображение Suface with edges")
        else:
            st.info("Скриншот 4.jpg не найден")

        st.markdown("""
        **Display** — настройки отображения:
        - **Representation**: Surface, Wireframe, Points, Surface With Edges
        - **Coloring**: выбор скалярного поля для раскраски
        - **Opacity**: прозрачность
        - **Edge Color**: цвет ребер (для Surface With Edges)
        """)

    col1, col2 = st.columns(2)

    with col1:
        if os.path.exists("images/5.jpg"):
            st.image("images/5.jpg", caption="Отображение Feature edge")
        else:
            st.info("Скриншот 5.jpg не найден")

        st.markdown("""
        **Information** — информация о данных:
        - Тип данных (структурированная/неструктурированная сетка)
        - Количество точек и ячеек
        - Доступные скалярные и векторные массивы
        - Диапазоны значений
        """)

    st.markdown("### Настройка отображения (Styling)")

    col1, col2 = st.columns(2)

    with col1:
        if os.path.exists("images/6.jpg"):
            st.image("images/6.jpg", caption="Настройки отображения (часть 1)")
        else:
            st.info("Скриншот 6.jpg не найден")

    with col2:
        if os.path.exists("images/7.jpg"):
            st.image("images/7.jpg", caption="Настройки отображения (часть 2)")
        else:
            st.info("Скриншот 7.jpg не найден")

    st.markdown("### Фильтры")

    st.markdown("""
    Фильтры — инструменты обработки данных. Применяются к выбранному объекту.
    Основные способы вызова:
    - Меню **Filters**
    - Кнопка **Ctrl+Space** (поиск по названию)
    - Панель инструментов (иконки часто используемых фильтров)
    """)

    col1, col2 = st.columns(2)

    with col1:
        if os.path.exists("images/8.jpg"):
            st.image("images/8.jpg", caption="Filters → Common → Slice")
        else:
            st.info("Скриншот 8.jpg не найден")

    with col2:
        if os.path.exists("images/9.jpg"):
            st.image("images/9.jpg", caption="Slice (пример 1)")
        else:
            st.info("Скриншот 9.jpg не найден")

    col1, col2, col3 = st.columns(3)

    with col1:
        if os.path.exists("images/10.jpg"):
            st.image("images/10.jpg", caption="Slice (пример 2)")
        else:
            st.info("Скриншот 10.jpg не найден")

    with col2:
        if os.path.exists("images/11.jpg"):
            st.image("images/11.jpg", caption="Slice (пример 3)")
        else:
            st.info("Скриншот 11.jpg не найден")

    with col3:
        if os.path.exists("images/12.jpg"):
            st.image("images/12.jpg", caption="Slice (пример 4)")
        else:
            st.info("Скриншот 12.jpg не найден")

    st.markdown("### Пример построения пайплайна")

    col1, col2 = st.columns(2)

    with col1:
        if os.path.exists("images/13.jpg"):
            st.image("images/13.jpg", caption="Цилиндр с примененным Slice")
        else:
            st.info("Скриншот 13.jpg не найден")

        st.markdown("**Шаг 1:** Cylinder → Slice")

    with col2:
        if os.path.exists("images/14.jpg"):
            st.image("images/14.jpg", caption="+ Elevation (раскраска по высоте)")
        else:
            st.info("Скриншот 14.jpg не найден")

        st.markdown("**Шаг 2:** + Elevation (раскраска по высоте)")

    st.markdown("### Extract Edges (извлечение ребер)")

    if os.path.exists("images/15.jpg"):
        st.image("images/15.jpg", caption="ExtractEdges — создание каркаса")
    else:
        st.info("Скриншот 15.jpg не найден")

    st.markdown("""
    Фильтр **Extract Edges** создает отдельный объект — только ребра (каркас) исходной геометрии.
    Полезно для наложения каркаса на полупрозрачную поверхность.
    """)

    st.markdown("### Сохранение результатов")

    col1, col2 = st.columns(2)

    with col1:
        if os.path.exists("images/16.jpg"):
            st.image("images/16.jpg", caption="Save Screenshot")
        else:
            st.info("Скриншот 16.jpg не найден")

        st.markdown("""
        **Save Screenshot** — сохранение изображения текущего вида:
        - PNG (с прозрачным фоном)
        - JPG (с белым фоном)
        - TIFF, BMP
        """)

        if os.path.exists("images/17.jpg"):
            st.image("images/17.jpg", caption="Save State")
        else:
            st.info("Скриншот 17.jpg не найден")

        st.markdown("""
        **Save State** — сохранение проекта (.pvsm):
        - Все настройки, фильтры, положение камеры
        - Можно загрузить позже через File → Load State
        """)

    with col2:
        if os.path.exists("images/18.jpg"):
            st.image("images/18.jpg", caption="Save Data")
        else:
            st.info("Скриншот 18.jpg не найден")

        st.markdown("""
        **Save Data** — сохранение геометрии выбранного объекта:
        - VTK (.vtk, .vtu) — для дальнейшей работы в ParaView
        - STL (.stl) — для 3D-печати
        - OBJ (.obj) — для других 3D-программ
        - CSV (.csv) — табличные данные
        """)

        if os.path.exists("images/19.jpg"):
            st.image("images/19.jpg", caption="Configure writer (настройки сохранения)")
        else:
            st.info("Скриншот 19.jpg не найден")

        st.markdown("""
        **Configure writer** — настройки сохранения:
        - Выбор сохраняемых массивов данных
        - Формат (ASCII или бинарный)
        - Сжатие
        - Для временных рядов: выбор кадров
        """)

elif menu == "Управление через командную строку и скрипты":

    st.markdown("### pvpython (Python-интерфейс)")

    st.markdown("""
    `pvpython` — это версия интерпретатора Python, в которую встроен модуль `paraview.simple`.
    Позволяет автоматизировать визуализацию без графического интерфейса.
    """)

    st.code("""
from paraview.simple import *

# Создать сферу
sphere = Sphere()

# Отобразить
Show(sphere)

# Настроить рендер
Render()

# Сохранить скриншот
SaveScreenshot('sphere.png')
    """, language="python")

    st.markdown("**Запуск:**")
    st.code("pvpython script.py")

    st.markdown("### pvbatch (параллельные скрипты)")

    st.markdown("""
    `pvbatch` — вариант pvpython для запуска в распределенном режиме с использованием MPI.
    Используется на кластерах для обработки больших данных.
    """)

    st.code("mpirun -np 16 pvbatch parallel_script.py")

    st.markdown("### Python Trace (запись действий)")

    st.markdown("""
    **Tools → Start Trace** — записывает все действия в графическом интерфейсе в виде Python-кода.

    1. Включите запись (Start Trace)
    2. Выполните нужные действия в интерфейсе
    3. Остановите запись (Stop Trace)
    4. Сохраните полученный скрипт

    Это отличный способ изучить API и автоматизировать повторяющиеся операции.
    """)

    st.markdown("### Плагины")

    st.markdown("""
    ParaView можно расширять с помощью плагинов:

    - **Tools → Manage Plugins** — открыть менеджер плагинов
    - **Remote** — плагины, загружаемые с сервера
    - **Local** — плагины, установленные локально

    Популярные плагины:
    - DICOM Reader — для медицинских изображений
    - CAD Reader — для STEP/IGES форматов
    - Topology — для топологического анализа
    """)