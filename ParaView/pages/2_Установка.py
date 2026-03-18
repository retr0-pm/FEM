import streamlit as st

st.set_page_config(
    page_title="ParaView: Установка",
    layout="wide"
)

st.title("ParaView: Установка")

menu = st.sidebar.radio(
    "Выберите раздел:",
    ["Системные требования",
     "Способы установки",
     "Настройка окружения"]
)

if menu == "Системные требования":

    st.markdown("### Минимальные требования")
    st.markdown("*Для запуска приложения и работы с небольшими наборами данных (до 10⁶ ячеек)*")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Аппаратное обеспечение**")
        st.markdown("- Процессор: x86_64, 2+ ядра")
        st.markdown("- ОЗУ: 4 ГБ")
        st.markdown("- Видеокарта: OpenGL 3.2")
        st.markdown("- Дисковое пространство: 1 ГБ")

    with col2:
        st.markdown("**Операционные системы**")
        st.markdown("- Windows 10/11 (64-bit)")
        st.markdown("- Linux (Ubuntu 20.04+, Fedora, RHEL)")
        st.markdown("- macOS 11+ (Intel и Apple Silicon)")

    with col3:
        st.markdown("**Программное обеспечение**")
        st.markdown("- Python 3.7–3.10 (опционально)")
        st.markdown("- Актуальные драйверы видеокарты")

    st.markdown("### Рекомендуемые требования")
    st.markdown("*Для работы с наборами данных среднего размера (10⁶–10⁸ ячеек)*")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Для комфортной работы**")
        st.markdown("- Процессор: 6–8 ядер")
        st.markdown("- ОЗУ: 16–32 ГБ")
        st.markdown("- SSD: 10+ ГБ свободного места")
        st.markdown("- Видеокарта: 2–4 ГБ VRAM")

    with col2:
        st.markdown("**Для больших данных**")
        st.markdown("- Процессор: 16+ ядер")
        st.markdown("- ОЗУ: 64+ ГБ")
        st.markdown("- Видеокарта: 8+ ГБ VRAM")
        st.markdown("- NVMe SSD или RAID массив")

    with col3:
        st.markdown("**Для кластерной работы**")
        st.markdown("- InfiniBand или 10+ GbE сеть")
        st.markdown("- Менеджер ресурсов (SLURM, PBS)")
        st.markdown("- Параллельная файловая система")
        st.markdown("- MPI-библиотека")

    st.markdown("""
    **Примечание:** Указанные требования являются ориентировочными. 
    ParaView может работать и с меньшими ресурсами, но производительность 
    будет зависеть от размера данных и сложности визуализации.
    """)

elif menu == "Способы установки":

    st.markdown("### Установка из бинарных пакетов")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Windows**")
        st.markdown("**Официальный установщик:**")
        st.markdown("1. Перейти на [paraview.org/download](https://www.paraview.org/download/)")
        st.markdown("2. Выбрать версию для Windows")
        st.markdown("3. Запустить .exe файл")
        st.markdown("4. Следовать инструкциям установщика")
        st.markdown("")
        st.markdown("**Chocolatey:**")
        st.code("choco install paraview")
        st.markdown("**Conda:**")
        st.code("conda install -c conda-forge paraview")

    with col2:
        st.markdown("**Linux**")
        st.markdown("**Ubuntu/Debian:**")
        st.code("sudo apt update\nsudo apt install paraview")
        st.markdown("**Fedora/RHEL:**")
        st.code("sudo dnf install paraview")
        st.markdown("**Arch Linux:**")
        st.code("sudo pacman -S paraview")
        st.markdown("**Conda:**")
        st.code("conda install -c conda-forge paraview")
        st.markdown("**AppImage:**")
        st.markdown("Скачать .AppImage с сайта, сделать исполняемым:")

    with col3:
        st.markdown("**macOS**")
        st.markdown("**Официальный .dmg:**")
        st.markdown("1. Скачать .dmg с [paraview.org](https://www.paraview.org/download/)")
        st.markdown("2. Открыть образ")
        st.markdown("3. Перетащить ParaView в папку Applications")
        st.markdown("")
        st.markdown("**Homebrew:**")
        st.code("brew install paraview")
        st.markdown("**Conda:**")
        st.code("conda install -c conda-forge paraview")

    st.markdown("### Сборка из исходников")
    st.markdown("*Рекомендуется при необходимости специфических настроек*")

    st.code("""
    # Клонирование репозитория
    git clone https://gitlab.kitware.com/paraview/paraview.git
    cd paraview
    git checkout v5.11.2  # или последний стабильный релиз

    # Создание директории для сборки
    mkdir build && cd build

    # Конфигурация CMake
    cmake -DCMAKE_BUILD_TYPE=Release \\
          -DPARAVIEW_USE_MPI=ON \\
          -DPARAVIEW_USE_PYTHON=ON \\
          -DVTK_USE_X=OFF \\
          -DVTK_OPENGL_HAS_OSMESA=ON \\
          ../paraview

    # Сборка
    make -j$(nproc)

    # Установка (опционально)
    sudo make install
    """)

    st.markdown("""
    **Зависимости для сборки:**
    - CMake 3.12+
    - Компилятор C++11 (GCC, Clang, MSVC)
    - Qt5 (для графического интерфейса)
    - Python 3.7+
    - MPI (опционально, для параллельной работы)
    - OpenGL и связанные библиотеки
    """)

elif menu == "Настройка окружения":

    st.markdown("### Проверка установки")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Запуск графического интерфейса**")
        st.code("paraview")
        st.markdown("**Проверка версии**")
        st.code("paraview --version")

    with col2:
        st.markdown("**Проверка Python-биндингов**")
        st.code("pvpython --version")
        st.code("""
        # Проверка импорта
        pvpython -c "from paraview.simple import *; print('OK')"
        """)

    st.markdown("### Переменные окружения")
    st.markdown("Обычно не требуются, но могут пригодиться в следующих случаях:")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Linux/macOS (добавить в ~/.bashrc или ~/.zshrc)**")
        st.code("""
# Добавление в PATH
export PATH=/path/to/paraview/bin:$PATH

# Для Python-биндингов (если установлены не в системный Python)
export PYTHONPATH=/path/to/paraview/lib/python3.x/site-packages:$PYTHONPATH

# Для MPI (опционально)
export OMPI_MCA_btl=^openib
        """)

    with col2:
        st.markdown("**Windows (PowerShell)**")
        st.code("""
# Временное добавление в текущей сессии
$env:Path += ";C:\\Program Files\\ParaView 5.11.2\\bin"

# Постоянное добавление (требует прав администратора)
[Environment]::SetEnvironmentVariable(
    "Path", 
    [Environment]::GetEnvironmentVariable("Path", "Machine") + 
    ";C:\\Program Files\\ParaView\\bin",
    "Machine"
)
        """)

    st.markdown("### Часто возникающие проблемы")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Проблемы с графическим интерфейсом**")
        st.markdown("""
        - **Приложение не запускается:** обновить драйверы видеокарты
        - **Ошибки OpenGL:** проверить поддержку OpenGL 3.2+
        - **Артефакты отображения:** отключить аппаратное ускорение в настройках
        - **Черный экран при рендеринге:** проверить совместимость драйверов
        """)

    with col2:
        st.markdown("**Проблемы с Python-биндингами**")
        st.markdown("""
        - **ModuleNotFoundError:** использовать pvpython вместо обычного python
        - **Ошибки версий Python:** ParaView поставляется со своим интерпретатором
        - **Пути импорта:** проверить PYTHONPATH
        - **Библиотеки не загружаются:** проверить наличие зависимостей (libstdc++ и др.)
        """)

    st.markdown("**Параллельный запуск (MPI)**")
    st.code("""
    # Локальный запуск на 4 процессах
    mpirun -np 4 pvserver

    # В клиенте ParaView: File → Connect → Add Server
    # Тип соединения: Client/Server
    # Host: localhost, Port: 11111
    """)