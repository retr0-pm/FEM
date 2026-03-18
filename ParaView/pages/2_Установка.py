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

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Аппаратное обеспечение**")
        st.markdown("- Процессор: 2+ ядра")
        st.markdown("- ОЗУ: 4 ГБ")
        st.markdown("- OpenGL 3.2")
        st.markdown("- Диск: 1 ГБ")

    with col2:
        st.markdown("**Операционные системы**")
        st.markdown("- Windows 10/11")
        st.markdown("- Linux (Ubuntu, Fedora)")
        st.markdown("- macOS Intel/Apple Silicon")

    with col3:
        st.markdown("**Опционально**")
        st.markdown("- Python 3.7+")
        st.markdown("- Актуальные драйверы GPU")

    st.markdown("### Рекомендуемые требования")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Для комфортной работы**")
        st.markdown("- Процессор: 6+ ядер")
        st.markdown("- ОЗУ: 16+ ГБ")
        st.markdown("- SSD: 5+ ГБ")

    with col2:
        st.markdown("**Для больших данных**")
        st.markdown("- Процессор: 8+ ядер")
        st.markdown("- ОЗУ: 32+ ГБ")
        st.markdown("- GPU 4+ ГБ")

    with col3:
        st.markdown("**Для объемного рендеринга**")
        st.markdown("- GPU NVIDIA/AMD")
        st.markdown("- ОЗУ: 64+ ГБ")
        st.markdown("- NVMe SSD")

elif menu == "Способы установки":

    st.markdown("### Установка")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**Windows**")
        st.markdown("Официальный сайт:")
        st.code(".exe установщик")
        st.markdown("Chocolatey:")
        st.code("choco install paraview")
        st.markdown("Conda:")
        st.code("conda install -c conda-forge paraview")

    with col2:
        st.markdown("**Linux**")
        st.markdown("Ubuntu/Debian:")
        st.code("sudo apt install paraview")
        st.markdown("Fedora:")
        st.code("sudo dnf install paraview")
        st.markdown("Arch:")
        st.code("sudo pacman -S paraview")

    with col3:
        st.markdown("**macOS**")
        st.markdown("Официальный .dmg:")
        st.code("Скачать с сайта")
        st.markdown("Homebrew:")
        st.code("brew install paraview")
        st.markdown("Conda:")
        st.code("conda install -c conda-forge paraview")

    st.markdown("**Сборка из исходников**")
    st.code(
        "git clone https://gitlab.kitware.com/paraview/paraview.git\ncd paraview\nmkdir build && cd build\ncmake ..\nmake -j$(nproc)\nsudo make install")

elif menu == "Настройка окружения":

    st.markdown("### Проверка установки")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Запуск GUI**")
        st.code("paraview")
        st.markdown("**Версия**")
        st.code("paraview --version")

    with col2:
        st.markdown("**Python-биндинги**")
        st.code("pvpython --version\npython -c \"import paraview.simple\"")

    st.markdown("### Переменные окружения")
    st.markdown("Только если ParaView не найден после установки:")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Linux/macOS**")
        st.code(
            "export PATH=/путь/к/paraview/bin:$PATH\nexport PYTHONPATH=/путь/к/paraview/lib/python3.x/site-packages:$PYTHONPATH")

    with col2:
        st.markdown("**Windows**")
        st.code("$env:Path += \";C:\\Program Files\\ParaView\\bin\"")

    st.markdown("### Типичные проблемы")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Не запускается GUI**")
        st.markdown("- Обновить драйверы GPU")
        st.markdown("- Проверить OpenGL")

    with col2:
        st.markdown("**Не работают Python-биндинги**")
        st.markdown("- Использовать pvpython")
        st.markdown("- Проверить путь установки")