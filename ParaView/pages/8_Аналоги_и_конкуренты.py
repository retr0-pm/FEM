import streamlit as st

st.set_page_config(
    page_title="ParaView: Аналоги и конкуренты",
    layout="wide"
)

st.title("ParaView: Аналоги и конкуренты")

menu = st.sidebar.radio(
    "Выберите раздел:",
    ["Коммерческое ПО",
     "Открытые альтернативы",
     "Сравнение по критериям"]
)

if menu == "Коммерческое ПО":

    st.markdown("### Tecplot")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Характеристики**")
        st.markdown("- Специализация: инженерная визуализация, CFD")
        st.markdown("- Лицензия: проприетарная")
        st.markdown("- Интерфейс: графический, Python")
        st.markdown("- Платформы: Windows, Linux, macOS")

    with col2:
        st.markdown("**Особенности**")
        st.markdown("- Прямая поддержка форматов Fluent, STAR-CCM+")
        st.markdown("- Zones для многосрезового анализа")
        st.markdown("- Есть студенческая версия")
        st.markdown("- Ограничения по объему данных (до 10⁸ ячеек)")

    st.markdown("### EnSight")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Характеристики**")
        st.markdown("- Специализация: промышленная визуализация")
        st.markdown("- Лицензия: проприетарная")
        st.markdown("- Интерфейс: графический, Python, C API")
        st.markdown("- Платформы: Windows, Linux")

    with col2:
        st.markdown("**Особенности**")
        st.markdown("- Удаленная работа с аннотациями")
        st.markdown("- Поддержка VR-устройств")
        st.markdown("- Используется в автомобилестроении")
        st.markdown("- Поддержка MPI")

    st.markdown("### AVS/Express")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Характеристики**")
        st.markdown("- Специализация: научная визуализация")
        st.markdown("- Лицензия: проприетарная")
        st.markdown("- Интерфейс: визуальное программирование")
        st.markdown("- Платформы: Windows, Linux")

    with col2:
        st.markdown("**Особенности**")
        st.markdown("- Разработка ведется с 1990-х")
        st.markdown("- Модульная сборка пайплайнов")
        st.markdown("- Последние обновления нерегулярны")
        st.markdown("- Ограниченная поддержка современных форматов")

    st.markdown("### FieldView")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Характеристики**")
        st.markdown("- Специализация: вычислительная гидродинамика")
        st.markdown("- Лицензия: проприетарная")
        st.markdown("- Интерфейс: графический, FVX, Python")
        st.markdown("- Платформы: Windows, Linux")

    with col2:
        st.markdown("**Особенности**")
        st.markdown("- Интеграция с ANSYS Fluent, STAR-CCM+")
        st.markdown("- Используется в авиастроении")
        st.markdown("- Только CFD-задачи")
        st.markdown("- Привязка к форматам конкретных решателей")

elif menu == "Открытые альтернативы":

    st.markdown("### VisIt")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Характеристики**")
        st.markdown("- Разработка: Ливерморская национальная лаборатория")
        st.markdown("- Лицензия: BSD")
        st.markdown("- Интерфейс: графический, Python")
        st.markdown("- Платформы: Windows, Linux, macOS")

    with col2:
        st.markdown("**Особенности**")
        st.markdown("- Ориентация на суперкомпьютеры")
        st.markdown("- Параллельная обработка MPI")
        st.markdown("- Поддержка Silo, HDF5, NetCDF")
        st.markdown("- Меньше встроенных фильтров чем в ParaView")

    st.markdown("### Mayavi")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Характеристики**")
        st.markdown("- Ядро: VTK")
        st.markdown("- Лицензия: BSD")
        st.markdown("- Интерфейс: Python-библиотека")
        st.markdown("- Платформы: все через Python")

    with col2:
        st.markdown("**Особенности**")
        st.markdown("- Работа из IPython/Jupyter")
        st.markdown("- Прямая работа с NumPy")
        st.markdown("- Базовый графический интерфейс")
        st.markdown("- Не поддерживает MPI")

    st.markdown("### OpenDX")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Характеристики**")
        st.markdown("- Разработка: IBM (передан open source)")
        st.markdown("- Лицензия: IBM Public License")
        st.markdown("- Интерфейс: визуальное программирование")
        st.markdown("- Платформы: Windows, Linux, AIX")

    with col2:
        st.markdown("**Особенности**")
        st.markdown("- Разработка остановлена в 2000-х")
        st.markdown("- Проблемы с запуском на новых системах")
        st.markdown("- Представляет исторический интерес")
        st.markdown("- Не рекомендуется для новых проектов")

    st.markdown("### Другие открытые инструменты")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**PyVista**")
        st.markdown("- Обертка над VTK для Python")
        st.markdown("- Работа через скрипты")
        st.markdown("- Интеграция с NumPy")
        st.markdown("- Нет графического интерфейса")

    with col2:
        st.markdown("**yt**")
        st.markdown("- Специализация: астрофизика")
        st.markdown("- Работа с объемными данными")
        st.markdown("- Ограничен другими областями")
        st.markdown("- Собственные форматы данных")

    with col3:
        st.markdown("**VTK**")
        st.markdown("- Базовый toolkit")
        st.markdown("- Требует программирования")
        st.markdown("- Максимальная гибкость")
        st.markdown("- Нет готового интерфейса")

elif menu == "Сравнение по критериям":

    st.markdown("### Критерии сравнения")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Поддержка параллельных вычислений**")
        st.markdown("- ParaView: MPI")
        st.markdown("- VisIt: MPI")
        st.markdown("- EnSight: MPI")
        st.markdown("- Tecplot: SMP")
        st.markdown("- Mayavi: нет")
        st.markdown("- FieldView: SMP/MPI")

    with col2:
        st.markdown("**Поддержка форматов**")
        st.markdown("- ParaView: VTK, Exodus, CGNS, HDF5, NetCDF, более 100")
        st.markdown("- VisIt: Silo, HDF5, NetCDF, VTK")
        st.markdown("- Tecplot: собственный, Fluent, PLOT3D")
        st.markdown("- EnSight: собственный, ANSYS, Abaqus")
        st.markdown("- Mayavi: VTK, через NumPy")

    st.markdown("**Интеграция с Python**")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("- ParaView: pvpython")
        st.markdown("- Mayavi: import mayavi")
        st.markdown("- VisIt: visit -cli")

    with col2:
        st.markdown("- Tecplot: PyTec")
        st.markdown("- EnSight: EnSight Python")
        st.markdown("- FieldView: FVX, Python")

    st.markdown("**Области применения**")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**ParaView**")
        st.markdown("- Академические исследования")
        st.markdown("- Междисциплинарные задачи")
        st.markdown("- Национальные лаборатории")

    with col2:
        st.markdown("**Tecplot/FieldView**")
        st.markdown("- Аэрокосмическая промышленность")
        st.markdown("- Автомобилестроение")
        st.markdown("- Энергетическое машиностроение")

    with col3:
        st.markdown("**EnSight**")
        st.markdown("- Автомобилестроение")
        st.markdown("- Тяжелое машиностроение")
        st.markdown("- Оборонная промышленность")

    st.markdown("---")

    st.markdown("### Сводная таблица")

    st.markdown("""
| | ParaView | VisIt | Mayavi | Tecplot | EnSight | FieldView |
|---|---|---|---|---|---|---|
| Лицензия | BSD | BSD | BSD | Проприетарная | Проприетарная | Проприетарная |
| Стоимость | 0 | 0 | 0 | Высокая | Высокая | Высокая |
| Параллельные вычисления | MPI | MPI | нет | SMP | MPI | SMP/MPI |
| Python API | есть | есть | есть | есть | есть | есть |
| GUI | есть | есть | минимальный | есть | есть | есть |
| Специализация | универсальный | универсальный | скриптинг | CFD | мультифизика | CFD |
    """)

    st.markdown("### Выводы")

    st.markdown("""
**ParaView** — универсальный инструмент с поддержкой MPI и широким набором форматов. Бесплатный, развивается сообществом и Kitware.

**Tecplot/FieldView** — коммерческие продукты, интегрированные с конкретными CFD-решателями. Используются в промышленности.

**VisIt** — бесплатный аналог с аналогичными возможностями параллельной визуализации, разрабатываемый национальной лабораторией.

**Mayavi/PyVista** — библиотеки для встраивания визуализации в Python-приложения, не предназначенные для работы с большими данными.
    """)