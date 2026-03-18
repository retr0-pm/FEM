import streamlit as st

st.set_page_config(
    page_title="ParaView: Заключение",
    layout="wide"
)

st.title("ParaView: Заключение")

menu = st.sidebar.radio(
    "Выберите раздел:",
    ["Общий вывод",
     "Полезные ссылки"]
)

if menu == "Общий вывод":

    st.markdown("### Основные результаты")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **ParaView как инструмент визуализации**

        - Приложение с открытым исходным кодом для визуализации научных данных
        - Построено на базе VTK (Visualization Toolkit)
        - Поддерживает широкий спектр форматов данных
        - Работает на Windows, Linux, macOS
        - Масштабируется от персонального компьютера до кластеров с MPI
        """)

    with col2:
        st.markdown("""
        **Ключевые возможности**

        - 2D и 3D визуализация
        - Скалярные, векторные и тензорные поля
        - Работа с сетками различной структуры
        - Анимация расчетных данных
        - Python-скриптинг и автоматизация
        - Более 300 встроенных фильтров
        """)

    st.markdown("### Место среди аналогов")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **Преимущества**

        - Бесплатное ПО (лицензия BSD)
        - Активное сообщество разработчиков
        - Поддержка MPI для больших данных
        - Широкая поддержка форматов
        - Гибкость настройки
        """)

    with col2:
        st.markdown("""
        **Ограничения**

        - Требует изучения интерфейса
        - Качество графики уступает коммерческим аналогам
        - Документация фрагментарна
        - Нет официальной техподдержки
        """)

    with col3:
        st.markdown("""
        **Области применения**

        - Вычислительная гидродинамика
        - Механика деформируемого твердого тела
        - Астрофизика и космология
        - Науки о Земле
        - Медицина и биоинженерия
        - Материаловедение
        """)

    st.markdown("### Итоговая рекомендация")

    st.markdown("""
    ParaView рекомендуется к использованию в следующих случаях:

    - Исследовательские задачи с ограниченным бюджетом
    - Работа с данными от десятков мегабайт до терабайт
    - Требуется автоматизация через Python-скрипты
    - Необходима кроссплатформенность
    - Важна возможность масштабирования на кластер

    Для промышленного использования с конкретными решателями (ANSYS, STAR-CCM+) 
    и при наличии бюджета могут быть предпочтительнее коммерческие аналоги 
    (Tecplot, FieldView, EnSight), дающие более тесную интеграцию и готовые 
    шаблоны визуализации.
    """)

elif menu == "Полезные ссылки":

    st.markdown("### Официальные ресурсы")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Документация и загрузка**

        - [Официальный сайт ParaView](https://www.paraview.org/)
        - [Загрузка дистрибутивов](https://www.paraview.org/download/)
        - [Документация](https://docs.paraview.org/)
        - [Wiki](https://www.paraview.org/Wiki/ParaView)
        - [Руководство пользователя (PDF)](https://www.paraview.org/paraview-downloads/download.php?submit=Download&version=v5.11&type=data&os=all&downloadFile=ParaViewGuide-5.11.0.pdf)
        """)

    with col2:
        st.markdown("""
        **Исходный код и разработка**

        - [GitLab репозиторий](https://gitlab.kitware.com/paraview/paraview)
        - [Отслеживание ошибок](https://gitlab.kitware.com/paraview/paraview/-/issues)
        - [API Python](https://kitware.github.io/paraview-docs/latest/python/)
        - [Каталог плагинов](https://www.paraview.org/plugins/)
        """)

    st.markdown("### Обучающие материалы")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **Туториалы**

        - [ParaView Tutorial (5.11)](https://www.paraview.org/tutorials/)
        - [Getting Started Guide](https://www.paraview.org/Wiki/images/b/bc/ParaViewGettingStarted-5.0.0.pdf)
        - [YouTube канал Kitware](https://www.youtube.com/user/KitwareVideo)
        - [Введение в ParaView](https://www.paraview.org/Wiki/ParaView/Users_Guide/Introduction)
        """)

    with col2:
        st.markdown("""
        **Примеры данных**

        - [Наборы данных для туториалов](https://www.paraview.org/Wiki/ParaView/Data)
        - [Wavelet example](https://www.paraview.org/Wiki/ParaView/Example_Visualizations)
        - [Тестовые данные OpenFOAM](https://openfoam.com/download/example-data.php)
        - [Научные визуализации](https://www.paraview.org/gallery/)
        """)

    with col3:
        st.markdown("""
        **Книги и руководства**

        - "The ParaView Guide" (Kitware)
        - "VTK Textbook" (сопутствующее)
        - "Mastering CMake" (для сборки)
        """)

    st.markdown("### Сообщество и поддержка")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Форумы и чаты**

        - [Дискуссионная группа](https://discourse.paraview.org/)
        - [Stack Overflow (тег paraview)](https://stackoverflow.com/questions/tagged/paraview)
        - [Канал Discord](https://discord.gg/paraview)
        - [Mailing list](https://www.paraview.org/mailing-lists/)
        """)

    with col2:
        st.markdown("""
        **Смежные проекты**

        - [VTK](https://vtk.org/)
        - [Kitware](https://www.kitware.com/)
        - [Catalyst](https://www.paraview.org/catalyst/)
        - [ParaViewWeb](https://www.paraview.org/web/)
        """)

    st.markdown("---")

    st.markdown("### Данная работа")

    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown("**Репозиторий проекта:**")

    with col2:
        st.markdown("[https://github.com/retr0-pm/FEM](https://github.com/retr0-pm/FEM)")

    st.markdown("""
    В репозитории представлены:
    - Код презентации на Streamlit
    - Примеры визуализации
    - Материалы по численным методам
    """)

    st.markdown("---")

    st.markdown("*Материал подготовлен в рамках ознакомительного курса по инструментам научной визуализации*")