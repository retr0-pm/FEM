import streamlit as st
from PIL import Image
import os

st.set_page_config(
    page_title="ParaView: Режимы отображения",
    layout="wide"
)

st.title("2D и 3D визуализация в ParaView")
st.markdown("---")

# Список режимов отображения
modes = [
    "Surface (Поверхность)",
    "Wireframe (Каркас)",
    "Points (Точки)",
    "Surface With Edges (Поверхность с ребрами)",
    "Volume (Объем)",
    "Point Gaussian (Гауссовы точки)",
    "3D Glyphs (3D глифы)",
    "Feature Edges (Характерные ребра)",
    "Outline (Контуры)",
    "Surface LIC (LIC на поверхности)"
]

# Подразделы управления камерой и освещением
camera_lighting_options = [
    "Управление камерой",
    "Управление освещением"
]

# Подразделы работы с цветом и прозрачностью
color_opacity_options = [
    "Цветовые карты (Color Maps)",
    "Настройка прозрачности (Opacity)"
]

# Боковая панель с навигацией
st.sidebar.header("2D и 3D визуализация")
st.sidebar.markdown("---")

# Выбор раздела через radio buttons
selected_section = st.sidebar.radio(
    "Раздел:",
    ["Режимы отображения", "Управление камерой и освещением", "Работа с цветом и прозрачностью"]
)

# st.markdown("---")

# Если выбраны режимы отображения
if selected_section == "Режимы отображения":
    # Выпадающий список на основной странице
    selected_mode = st.selectbox("Выберите режим отображения:", modes)

    st.markdown("---")

    # Данные для каждого режима
    mode_data = {
        "Surface (Поверхность)": {
            "description": "Стандартное отображение поверхности объекта с закрашенными полигонами.",
            "characteristics": [
                "Показывает внешнюю геометрию",
                "Применяет освещение и материалы",
                "Скрывает внутреннюю структуру",
                "Быстрый рендеринг"
            ],
            "use_cases": [
                "Общая визуализация формы объекта",
                "Финальные рендеры для презентаций",
                "Когда важна только внешняя геометрия",
                "Анализ распределения скалярных полей на поверхности"
            ],
            "settings": """Properties → Representation → Surface

Дополнительные настройки:
- Properties → Coloring → выбор скалярного поля
- Properties → Lighting → управление освещением
- Properties → Opacity → прозрачность""",
            "screenshot": "Screens/Representation_Surface.png"
        },
        "Wireframe (Каркас)": {
            "description": "Отображение только ребер сетки без поверхности.",
            "characteristics": [
                "Показывает структуру сетки",
                "Все линии видны, включая внутренние",
                "Прозрачный вид",
                "Низкая нагрузка на GPU"
            ],
            "use_cases": [
                "Проверка качества сетки",
                "Демонстрация структуры модели",
                "Просмотр внутренней геометрии",
                "Отладка конечно-элементных моделей"
            ],
            "settings": """Properties → Representation → Wireframe

Дополнительные настройки:
- Properties → Line Width → толщина линий
- Properties → Coloring → цвет ребер""",
            "screenshot": "Screens/Representation_Wireframe.png"
        },
        "Points (Точки)": {
            "description": "Отображение только узлов сетки как точек.",
            "characteristics": [
                "Каждая вершина отображается как точка",
                "Размер точек настраивается",
                "Показывает плотность и распределение сетки",
                "Минимальная нагрузка на систему"
            ],
            "use_cases": [
                "Анализ распределения узлов сетки",
                "Визуализация точечных данных",
                "Демонстрация разрешения сетки",
                "Проверка граничных условий"
            ],
            "settings": """Properties → Representation → Points

Дополнительные настройки:
- Properties → Point Size → размер точек
- Properties → Coloring → цвет точек""",
            "screenshot": "Screens/Representation_Points.png"
        },
        "Surface With Edges (Поверхность с ребрами)": {
            "description": "Комбинация Surface и Wireframe — поверхность с наложенной сеткой.",
            "characteristics": [
                "Закрашенная поверхность",
                "Видимые границы полигонов",
                "Цвет и толщина ребер настраиваются",
                "Хороший баланс между формой и структурой"
            ],
            "use_cases": [
                "Одновременный показ формы и структуры",
                "Демонстрация качества сетки на поверхности",
                "Технические иллюстрации",
                "Инженерная визуализация"
            ],
            "settings": """Properties → Representation → Surface With Edges

Дополнительные настройки:
- Properties → Edge Color → цвет ребер
- Properties → Line Width → толщина линий
- Properties → Coloring → цвет поверхности""",
            "screenshot": "Screens/Representation_Surface_with_Edges.png"
        },
        "Volume (Объем)": {
            "description": "Объемная визуализация данных с использованием transfer functions.",
            "characteristics": [
                "Показывает внутренние значения скалярного поля",
                "Использует функции цвета и прозрачности",
                "Требует объемных данных",
                "Высокая вычислительная нагрузка"
            ],
            "use_cases": [
                "Медицинские данные (КТ, МРТ)",
                "Метеорологические данные",
                "Визуализация внутренних структур",
                "Научные объемные данные"
            ],
            "settings": """Properties → Representation → Volume

Дополнительные настройки:
- Color Map Editor → Edit Color Map → цветовая карта
- Color Map Editor → Edit Opacity → функция прозрачности
- Properties → Coloring → выбор скалярного поля""",
            "screenshot": "Screens/Representation_Volume.png"
        },
        "Point Gaussian (Гауссовы точки)": {
            "description": "Отображение точек в виде гауссовых распределений для сглаженной визуализации больших наборов данных.",
            "characteristics": [
                "Точки отображаются как размытые гауссовы пятна",
                "Эффективно для миллионов точек",
                "Сглаженный вид без резких краев",
                "Поддерживает прозрачность и цвет по скалярам",
                "Требует OpenGL 3.2+"
            ],
            "use_cases": [
                "Визуализация больших облаков точек",
                "Молекулярные структуры",
                "Астрономические данные",
                "Результаты частиц (SPH, DEM)",
                "Когда Points режим слишком детализирован"
            ],
            "settings": """Properties → Representation → Point Gaussian

Дополнительные настройки:
- Properties → Gaussian Radius → радиус размытия
- Properties → Scale Factor → масштаб точек
- Properties → Opacity → прозрачность
- Color Map Editor → цветовая карта по скалярам""",
            "screenshot": "Screens/Representation_Point_Gaussian.png"
        },
        "3D Glyphs (3D глифы)": {
            "description": "Отображение геометрических примитивов (стрелки, сферы, кубы) в каждой точке для визуализации векторных полей и тензоров.",
            "characteristics": [
                "Показывает направление и величину векторов",
                "Настраиваемые типы глифов (20+ форм)",
                "Масштабирование по величине или компоненте",
                "Требует применения фильтра Glyph",
                "Может быть ресурсоемким при большом количестве точек"
            ],
            "use_cases": [
                "Векторные поля (скорость, сила, перемещение)",
                "Градиенты скалярных полей",
                "Направление потоков жидкости",
                "Напряжения и деформации",
                "Ориентация в пространстве"
            ],
            "settings": """Filters → Alphabetical → Glyph

Настройки фильтра:
- Glyph Type → Arrow/Sphere/Cone/Cube (тип маркера)
- Vectors → выбор векторного поля
- Scale Mode → magnitude/vector component
- Scale Factor → коэффициент масштабирования
- Mask Points → шаг выборки точек (для уменьшения количества)
- Orient → направление ориентации""",
            "screenshot": "Screens/Representation_3D_Glyphs.png"
        },
        "Feature Edges (Характерные ребра)": {
            "description": "Выделение характерных ребер геометрии: грани, острые углы, границы и не-манхэттенские ребра.",
            "characteristics": [
                "Показывает только важные ребра геометрии",
                "Выделяет границы между поверхностями",
                "Отображает острые углы (feature angles)",
                "Полезен для анализа качества CAD-геометрии"
            ],
            "use_cases": [
                "Анализ CAD-геометрии",
                "Выделение границ деталей",
                "Проверка острых углов и кромок",
                "Визуализация границ областей",
                "Контроль качества сетки"
            ],
            "settings": """Filters → Alphabetical → Feature Edges

Настройки фильтра:
- Feature Angle → угол для выделения острых ребер
- Boundary Edges → показать границы
- Feature Edges → показать характерные ребра
- Non-Manifold Edges → показать не-манхэттенские ребра
- Manifold Edges → показать манхэттенские ребра""",
            "screenshot": "Screens/Representation_Feature_Edges.png"
        },
        "Outline (Контуры)": {
            "description": "Отображение только ограничивающего параллелепипеда (bounding box) вокруг данных.",
            "characteristics": [
                "Показывает только границы области данных",
                "Минимальная нагрузка на систему",
                "Полезен для определения положения объекта",
                "Часто используется как контекст"
            ],
            "use_cases": [
                "Быстрая проверка положения данных",
                "Контекст для других визуализаций",
                "Определение границ области",
                "Минималистичное представление",
                "Ориентация в сцене"
            ],
            "settings": """Filters → Alphabetical → Outline

Дополнительные настройки:
- Properties → Line Width → толщина линий
- Properties → Color → цвет контура
- Можно комбинировать с другими представлениями""",
            "screenshot": "Screens/Representation_Outline.png"
        },
        "Surface LIC (LIC на поверхности)": {
            "description": "Line Integral Convolution (LIC) — метод визуализации векторных полей на поверхностях с помощью текстурных линий потока.",
            "characteristics": [
                "Показывает направление потока на поверхности",
                "Использует текстурные линии для визуализации",
                "Эффективен для сложных векторных полей",
                "Требует векторное поле на поверхности",
                "Создает художественный эффект 'потока'"
            ],
            "use_cases": [
                "Визуализация потоков жидкости на поверхностях",
                "Направление напряжений на поверхности",
                "Векторные поля на сложных геометриях",
                "Аэродинамические исследования",
                "Гидродинамическое моделирование"
            ],
            "settings": """Properties → Representation → Surface LIC

Настройки:
- Properties → LIC Intensity → интенсивность LIC
- Properties → Enhanced LIC → улучшенное качество
- Properties → Contrast → контраст линий
- Требуется векторное поле в Properties → Vectors""",
            "screenshot": "Screens/Representation_Surface_LIC.png"
        }
    }

    data = mode_data[selected_mode]

    st.header(selected_mode)
    st.subheader("Описание")
    st.write(data["description"])
    st.subheader("Характеристики")
    for char in data["characteristics"]:
        st.markdown(f"- {char}")
    st.subheader("Примеры использования")
    for case in data["use_cases"]:
        st.markdown(f"- {case}")
    st.subheader("Как настроить")
    st.code(data["settings"], language="python")
    st.subheader("Пример визуализации")
    col1, col2 = st.columns(2)
    with col1:
        if os.path.exists(data["screenshot"]):
            st.image(data["screenshot"], caption=selected_mode, use_container_width=True)
        else:
            st.info(f"Загрузите скриншот: {data['screenshot']}")

# Если выбрано управление камерой и освещением
elif selected_section == "Управление камерой и освещением":
    # Выпадающий список на основной странице (аналогично режимам)
    selected_topic = st.selectbox("Выберите тему:", camera_lighting_options)

    st.markdown("---")

    # Данные для подразделов
    topic_data = {
        "Управление камерой": {
            "description": "Инструменты управления положением, углом обзора и проекцией камеры в 3D-сцене.",
            "characteristics": [
                "Интерактивное вращение, панорамирование и масштабирование",
                "Настройка стандартных видов (сверху, спереди, изометрия)",
                "Переключение между перспективной и параллельной проекцией",
                "Точная настройка позиции и фокуса камеры",
                "Сохранение и восстановление позиций камеры"
            ],
            "use_cases": [
                "Настройка оптимального ракурса для визуализации",
                "Создание стандартных инженерных видов",
                "Подготовка скриншотов и презентаций",
                "Детальный осмотр отдельных частей модели",
                "Анимация полёта камеры"
            ],
            "settings": """ПАНЕЛЬ ИНСТРУМЕНТОВ CAMERA:
- Reset Camera → сброс камеры к объекту
- Isometric View → изометрическая проекция
- Front/Back/Top/Bottom/Left/Right View → стандартные виды

НАСТРОЙКИ В PROPERTIES (выделить Render View):
- Camera Position → позиция камеры (X, Y, Z)
- Camera Focal Point → точка фокусировки
- Camera View Up → направление "верха" камеры
- View Angle → угол обзора (FOV), градусов
- Parallel Projection → переключатель проекции

ИНТЕРАКТИВНОЕ УПРАВЛЕНИЕ МЫШЬЮ:
- ЛКМ + Drag → вращение вокруг объекта
- ПКМ + Drag → масштабирование (zoom)
- Колесико + Drag → панорамирование (pan)
- Колесико прокрутки → быстрый зум""",
            "screenshot": "Screens/Camera_Control.png"
        },
        "Управление освещением": {
            "description": "Инструменты настройки источников света и параметров освещения для улучшения восприятия 3D-сцены.",
            "characteristics": [
                "Управление несколькими источниками света",
                "Настройка типа, позиции и интенсивности света",
                "Контроль параметров материалов (ambient, diffuse, specular)",
                "Визуализация эффектов освещения в реальном времени",
                "Поддержка головных и сценных источников света"
            ],
            "use_cases": [
                "Улучшение восприятия глубины и формы объектов",
                "Подчёркивание деталей поверхности через блики",
                "Создание драматического освещения для презентаций",
                "Имитация реальных условий освещения",
                "Устранение теневых артефактов"
            ],
            "settings": """LIGHT INSPECTOR (View → Light Inspector):

КНОПКИ УПРАВЛЕНИЯ:
- Add Light → добавить новый источник света
- Move to Camera → привязать свет к камере (движется вместе с ней)
- Reset Light → сбросить параметры к значениям по умолчанию
- Remove Light → удалить источник света
- Enable → включить/выключить источник

НАСТРОЙКИ:
- Coords: Scene/Camera → система координат (мировая/камеры)
- Intensity → интенсивность света (0.0–10.0+)
- Type → Directional/Positional/Headlight/Scene Light
- Light Position → координаты источника (X, Y, Z)
- Focal Point → точка, на которую направлен свет
- Diffuse Color → цвет рассеянного света

НАСТРОЙКИ МАТЕРИАЛОВ В PROPERTIES:
- Ambient → фоновое освещение (равномерная подсветка)
- Diffuse → рассеянное освещение (основной свет)
- Specular → зеркальное отражение (блики)
- Specular Power → сила/размер блика
- Interpolation → сглаживание освещения (Gouraud/Phong)""",
            "screenshot": "Screens/Lighting_Control.png"
        }
    }

    data = topic_data[selected_topic]

    st.header(selected_topic)
    st.subheader("Описание")
    st.write(data["description"])
    st.subheader("Характеристики")
    for char in data["characteristics"]:
        st.markdown(f"- {char}")
    st.subheader("Примеры использования")
    for case in data["use_cases"]:
        st.markdown(f"- {case}")
    st.subheader("Как настроить")
    st.code(data["settings"], language="python")
    st.subheader("Пример визуализации")
    col1, col2 = st.columns(2)
    with col1:
        if os.path.exists(data["screenshot"]):
            st.image(data["screenshot"], caption=selected_topic, use_container_width=True)
        else:
            st.info(f"Загрузите скриншот: {data['screenshot']}")

# Если выбрана работа с цветом и прозрачностью
elif selected_section == "Работа с цветом и прозрачностью":
    selected_topic = st.selectbox("Выберите тему:", color_opacity_options)

    st.markdown("---")

    topic_data = {
        "Цветовые карты (Color Maps)": {
            "description": "Инструменты для настройки цветового отображения скалярных данных с использованием предустановленных палитр.",
            "characteristics": [
                "Автоматическое сопоставление значений скаляров с цветами",
                "Более 100 предустановленных цветовых палитр",
                "Редактирование отдельных точек цвета",
                "Настройка диапазона значений"
            ],
            "use_cases": [
                "Визуализация температурных полей",
                "Отображение напряжений и деформаций",
                "Анализ распределения давления",
                "Выделение областей интереса цветом"
            ],
            "settings": """COLOR MAP EDITOR (кнопка палитры в Properties → Coloring):

ВЫБОР СКАЛЯРНОГО ПОЛЯ:
- Coloring → выбор поля (DISPL, VEL, Pressure)
- Solid Color → однотонное отображение

ВЫБОР ЦВЕТОВОЙ ПАЛИТРЫ:
- Choose preset → выбор из 100+ палитр
- Популярные: Viridis, Plasma, Cool to Warm, Rainbow

НАСТРОЙКА ДИАПАЗОНА:
- Rescale to Custom → ручной диапазон (Min, Max)
- Rescale to Data Range → по данным

ЦВЕТОВЫЕ ТОЧКИ:
- Двойной клик на шкалу → добавить точку цвета
- Перетаскивание → изменить позицию
- Double-click на точку → изменить цвет

НАСТРОЙКИ:
- Nan Color → цвет для пропущенных значений
- Above Range Color → цвет для значений выше максимума
- Below Range Color → цвет для значений ниже минимума""",
            "screenshot": "Screens/Color_Map_Editor.png"
        },
        "Настройка прозрачности (Opacity)": {
            "description": "Инструменты управления прозрачностью объектов для визуализации внутренних структур.",
            "characteristics": [
                "Глобальная прозрачность для всего объекта",
                "Прозрачность по значениям скаляров",
                "Редактирование кривой прозрачности",
                "Комбинирование с цветовыми картами"
            ],
            "use_cases": [
                "Просмотр внутренних структур без срезов",
                "Визуализация многослойных данных",
                "Объёмный рендеринг (Volume)",
                "Выделение диапазонов значений прозрачностью"
            ],
            "settings": """ГЛОБАЛЬНАЯ ПРОЗРАЧНОСТЬ:

Properties → Opacity:
- Ползунок 0.0–1.0 (0%–100%)
- 1.0 = полностью непрозрачный
- 0.0 = полностью прозрачный

ПРОЗРАЧНОСТЬ ПО СКАЛЯРАМ (Opacity Transfer Function):

Color Map Editor → кнопка Edit Opacity:
- Кривая прозрачности по значениям скаляра
- Ось X → значения скаляра (Min–Max)
- Ось Y → прозрачность (0–1)
- Добавить точку → клик на кривую
- Удалить точку → перетащить за пределы
- Изменить значение → перетаскивание точки

ПРИМЕРЫ НАСТРОЙКИ:
- Прозрачный центр, непрозрачные края → V-образная кривая
- Видны только высокие значения → подъём справа
- Видны только низкие значения → подъём слева""",
            "screenshot": "Screens/Opacity_Control.png"
        }
    }

    data = topic_data[selected_topic]

    st.header(selected_topic)
    st.subheader("Описание")
    st.write(data["description"])
    st.subheader("Характеристики")
    for char in data["characteristics"]:
        st.markdown(f"- {char}")
    st.subheader("Примеры использования")
    for case in data["use_cases"]:
        st.markdown(f"- {case}")
    st.subheader("Как настроить")
    st.code(data["settings"], language="python")
    st.subheader("Пример визуализации")
    col1, col2 = st.columns(2)
    with col1:
        if os.path.exists(data["screenshot"]):
            st.image(data["screenshot"], caption=selected_topic, use_container_width=True)
        else:
            st.info(f"Загрузите скриншот: {data['screenshot']}")

st.markdown("---")

