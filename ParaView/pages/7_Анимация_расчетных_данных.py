import streamlit as st
import os

# Настройка страницы
st.set_page_config(
    page_title="Анимация расчетных данных в ParaView",
    layout="wide"
)

st.title("ParaView: Анимация расчетных данных")

# --- Боковая панель ---
menu = st.sidebar.radio(
    "Выберите раздел:",
    ["Работа с временными рядами",
     "Создание и настройка анимации",
     "Экспорт анимации и примеры"]
)

# --- Раздел 1: Работа с временными рядами ---
if menu == "Работа с временными рядами":

    st.markdown("### Загрузка данных с временными шагами")
    st.markdown("""
    ParaView поддерживает форматы, содержащие временные ряды:
    - Серии файлов (например, `solution_0000.vtk`, `solution_0001.vtk`, ...)
    - Файлы с временными метками (`.pvd`, `.vtm`, `.xdmf`)

    При загрузке такой информации ParaView автоматически определяет доступные временные шаги и позволяет перемещаться по ним с помощью ползунка времени.
    """)

    # Генерация данных в формате .vts
    st.markdown("---")
    st.markdown("### Генерация собственных данных в формате .vts")
    st.markdown("""
    Формат **.vts (StructuredGrid)** используется для хранения структурированных (регулярных) сеток в ParaView.  
    В сочетании с файлом коллекции **.pvd** можно создать временной ряд из нескольких .vts файлов.

    Рассмотрим пример генерации волн. Данные сохраняются как набор `.vts` файлов и один `.pvd`, который ссылается на них с указанием временных меток.

    #### Пример содержимого .vts файла
    """)

    st.code('''<?xml version="1.0"?>
<VTKFile type="StructuredGrid" version="1.0" byte_order="LittleEndian">
  <StructuredGrid WholeExtent="0 49 0 49 0 0">
    <Piece Extent="0 49 0 49 0 0">
      <Points>
        <DataArray NumberOfComponents="3" type="Float32" format="ascii">
          0.00000 0.00000 0.93515
          0.15000 0.00000 0.95131
          0.30000 0.00000 0.97469
          0.45000 0.00000 1.00180
          ...
        </DataArray>
      </Points>
    </Piece>
  </StructuredGrid>
</VTKFile>''', language='xml')

    st.markdown("""
    **Пояснения:**
    - `WholeExtent` и `Extent` задают размер сетки: `0 49 0 49 0 0` означает сетку 50×50×1 (2D поверхность в 3D).
    - Внутри `<Points>` перечислены координаты всех точек (x, y, z). В данном случае z — высота волны.
    """)

    st.markdown("#### Скрипт генерации (generate_wave3d.py)")

    code_generate = '''# generate_wave3d.py
import numpy as np
import os

OUTPUT_DIR = "paraview_wave3d"
NX, NY = 50, 50
SPACING = 0.15
TIME_STEPS = 45
DT = 0.12

def write_vts_3d(filename, z_values, nx, ny, spacing):
    """Генерирует 3D сетку, где Z-координата = z_values"""
    whole_extent = f"0 {nx-1} 0 {ny-1} 0 0"

    with open(filename, 'w') as f:
        f.write('<?xml version="1.0"?>\\n')
        f.write(f'<VTKFile type="StructuredGrid" version="1.0" byte_order="LittleEndian">\\n')
        f.write(f'  <StructuredGrid WholeExtent="{whole_extent}">\\n')
        f.write(f'    <Piece Extent="{whole_extent}">\\n')

        # Координаты с уже "поднятой" поверхностью
        f.write('      <Points>\\n')
        f.write('        <DataArray NumberOfComponents="3" type="Float32" format="ascii">\\n')
        points = []
        for j in range(ny):
            y = j * spacing
            for i in range(nx):
                x = i * spacing
                z = z_values[j, i]  # Z = высота волны
                points.append(f"{x:.5f} {y:.5f} {z:.5f}")
        f.write("          " + "\\n          ".join(points) + "\\n")
        f.write('        </DataArray>\\n')
        f.write('      </Points>\\n')

        # Данные: амплитуда волны (для цвета)
        f.write('      <PointData Scalars="amplitude">\\n')
        f.write('        <DataArray type="Float32" Name="amplitude" format="ascii">\\n')
        f.write("          " + "\\n          ".join([f"{v:.5f}" for v in z_values.flatten(order='C')]) + "\\n")
        f.write('        </DataArray>\\n')
        f.write('      </PointData>\\n')

        f.write('    </Piece>\\n')
        f.write('  </StructuredGrid>\\n')
        f.write('</VTKFile>')

def write_pvd(filename, files, timesteps):
    with open(filename, 'w') as f:
        f.write('<VTKFile type="Collection" version="0.1" byte_order="LittleEndian">\\n')
        f.write('  <Collection>\\n')
        for file, t in zip(files, timesteps):
            f.write(f'    <DataSet timestep="{t:.6f}" group="" part="0" file="{file}"/>\\n')
        f.write('  </Collection>\\n')
        f.write('</VTKFile>')

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

vts_files = []
timesteps = []

x = np.linspace(0, (NX-1)*SPACING, NX)
y = np.linspace(0, (NY-1)*SPACING, NY)
X, Y = np.meshgrid(x, y)
center = np.array([(NX*SPACING)/2, (NY*SPACING)/2])

for t in range(TIME_STEPS):
    time_val = t * DT

    # 3 источника волн
    Z = np.zeros_like(X)

    sources = [
        (center[0] + 0.5*np.sin(time_val*0.3), center[1] + 0.5*np.cos(time_val*0.4), 1.0),
        (center[0] - 0.8 + 0.3*np.sin(time_val*0.5), center[1] - 0.8, 0.7),
        (center[0] + 0.8, center[1] + 0.8 - 0.4*np.sin(time_val*0.6), 0.5),
    ]

    for sx, sy, amp in sources:
        R = np.sqrt((X-sx)**2 + (Y-sy)**2)
        # Бегущая волна с затуханием
        wave = amp * np.sin(R*4 - time_val*3) * np.exp(-R/1.5) * np.exp(-time_val*0.02)
        Z += wave

    # Нормализация и смещение (чтобы поверхность не уходила глубоко вниз)
    Z = Z - np.min(Z) + 0.1

    filename = os.path.join(OUTPUT_DIR, f"wave3d_{t:04d}.vts")
    write_vts_3d(filename, Z, NX, NY, SPACING)
    vts_files.append(os.path.basename(filename))
    timesteps.append(time_val)

write_pvd(os.path.join(OUTPUT_DIR, "wave3d.pvd"), vts_files, timesteps)
print(f"Сгенерировано {TIME_STEPS} файлов в {OUTPUT_DIR}/")
'''

    st.code(code_generate, language='python')

    st.markdown("""
    **Комментарии к скрипту:**

    1. **Параметры** – задаются размеры сетки, шаг по пространству, число временных шагов и шаг по времени.
    2. **Функция `write_vts_3d`** – записывает один `.vts` файл:
        - Заголовок XML с указанием размера сетки.
        - Блок `<Points>` – перечисляет координаты всех узлов, где z берётся из переданного массива `z_values`.
        - Блок `<PointData>` – сохраняет амплитуду (высоту) как скалярное поле с именем `amplitude`.
    3. **Функция `write_pvd`** – создаёт файл коллекции, который связывает все `.vts` файлы с соответствующими временными метками (`timestep`). Это позволяет ParaView воспринимать набор как временной ряд.
    4. **Генерация волны** – для каждого временного шага вычисляется интерференция трёх источников. Координаты источников немного меняются во времени, создавая эффект движения. Используется затухание (`exp(-R/1.5)`) и общее затухание со временем (`exp(-time_val*0.02)`).
    5. **Сохранение** – каждый кадр записывается в отдельный `.vts` файл с именем `wave3d_0000.vts`, `wave3d_0001.vts` и т.д. В конце создаётся `wave3d.pvd`.

    #### Загрузка в ParaView
    - Откройте ParaView.
    - **File → Open...** выберите созданный файл `wave3d.pvd`.
    - ParaView автоматически распознает временные шаги. На панели инструментов появится ползунок времени.
    """)

# --- Раздел 2: Создание и настройка анимации ---
elif menu == "Создание и настройка анимации":

    st.markdown("### Генерация анимированных данных через Programmable Source")
    st.markdown("""
    **Programmable Source** — это источник данных в ParaView, который позволяет создавать геометрию непосредственно в процессе визуализации с помощью Python-скриптов. Данные генерируются на лету для каждого запрошенного временного шага.

    Чтобы создать анимированный источник:
    1. Добавьте **Programmable Source** (Sources → Programmable Source).
    2. В его свойствах заполните два скрипта:
       - **Script** (основной скрипт генерации данных для текущего времени)
       - **RequestInformation Script** (скрипт, сообщающий ParaView о доступных временных шагах)
    """)

    st.markdown("#### Пример Script (генерация поверхности с волной)")

    code_ps_script = '''import vtk
import math
from paraview import vtk

output = self.GetOutput()
executive = self.GetExecutive()
outInfo = executive.GetOutputInformation(0)
if outInfo.Has(vtk.vtkStreamingDemandDrivenPipeline.UPDATE_TIME_STEP()):
    time = outInfo.Get(vtk.vtkStreamingDemandDrivenPipeline.UPDATE_TIME_STEP())
else:
    time = 0.0

# Параметры сетки
nx, ny = 40, 40
xmin, xmax = -5, 5
ymin, ymax = -5, 5
dx = (xmax - xmin) / (nx - 1)
dy = (ymax - ymin) / (ny - 1)

points = vtk.vtkPoints()
points.SetNumberOfPoints(nx * ny)

# Генерируем точки с волной
idx = 0
for j in range(ny):
    y = ymin + j * dy
    for i in range(nx):
        x = xmin + i * dx
        # Бегущая волна: z = sin( sqrt(x^2+y^2) - time*2pi )
        r = math.sqrt(x*x + y*y)
        z = math.sin(r * 1.5 - time * 2 * math.pi)  # волна распространяется наружу
        points.SetPoint(idx, x, y, z)
        idx += 1

# Создаём ячейки (квадраты) для поверхности
quads = vtk.vtkCellArray()
for j in range(ny - 1):
    for i in range(nx - 1):
        p0 = j * nx + i
        p1 = j * nx + i + 1
        p2 = (j + 1) * nx + i + 1
        p3 = (j + 1) * nx + i
        quads.InsertNextCell(4)
        quads.InsertCellPoint(p0)
        quads.InsertCellPoint(p1)
        quads.InsertCellPoint(p2)
        quads.InsertCellPoint(p3)

output.SetPoints(points)
output.SetPolys(quads)

# Добавим скаляр (Z координату) для раскраски
scalars = vtk.vtkDoubleArray()
scalars.SetName('Height')
scalars.SetNumberOfValues(nx * ny)
for i in range(nx * ny):
    scalars.SetValue(i, points.GetPoint(i)[2])
output.GetPointData().AddArray(scalars)
output.GetPointData().SetActiveScalars('Height')
'''

    st.code(code_ps_script, language='python')

    st.markdown("""
    **Пояснения к Script:**
    - Извлекается текущее время `time`, запрошенное ParaView для анимации.
    - Создаётся структурированная сетка (явно задаются точки и четырёхугольные ячейки).
    - Для каждой точки вычисляется z-координата как функция времени, создающая эффект бегущей волны.
    - Ячейки строятся как упорядоченные квадраты.
    - Скалярное поле `Height` добавляется для раскраски.
    """)

    st.markdown("#### Пример RequestInformation Script (объявление временных шагов)")

    code_ps_reqinfo = '''from paraview import vtk
import numpy as np

outInfo = self.GetOutputInformation(0)

# Определяем временные шаги
timesteps = np.linspace(0, 5.0, 100).tolist()

# Устанавливаем диапазон и список шагов
outInfo.Set(vtk.vtkStreamingDemandDrivenPipeline.TIME_RANGE(), [0.0, 5.0], 2)
outInfo.Set(vtk.vtkStreamingDemandDrivenPipeline.TIME_STEPS(), timesteps, len(timesteps))
'''

    st.code(code_ps_reqinfo, language='python')

    st.markdown("""
    **Пояснения к RequestInformation:**
    - Скрипт выполняется один раз для сообщения ParaView о доступных временных шагах.
    - Указывается общий временной диапазон (`TIME_RANGE`).
    - Передаётся список конкретных временных меток (`TIME_STEPS`), которые будут запрашиваться при анимации.
    - После этого ParaView покажет ползунок времени с этими шагами, и при каждом изменении времени будет вызываться основной Script с соответствующим значением `time`.
    """)

    st.markdown("#### Использование")
    st.markdown("""
    После настройки Programmable Source с этими скриптами можно применить к нему фильтры (например, **Warp By Scalar** для поднятия геометрии по Z), настроить цвет и запустить анимацию. Данные генерируются на лету для каждого кадра, что позволяет экспериментировать без создания файлов на диске.
    """)

# --- Раздел 3: Экспорт анимации и примеры ---
elif menu == "Экспорт анимации и примеры":

    st.markdown("### Сохранение анимации")
    st.markdown("""
    **File → Save Animation**

    **Форматы:**
    - AVI, OGG, MP4 — видеофайлы (через соответствующий кодек)
    - PNG, JPEG, TIFF, BMP — последовательности изображений

    **Параметры:**
    - FrameRate — частота кадров (рекомендуемые значения: 15, 24, 30 кадров/с)
    - Разрешение
    - Кодек (для видео)

    При сохранении в видеоформат можно управлять битрейтом и кодеком через дополнительные параметры (зависят от платформы).
    """)

    st.markdown("### Примеры готовых анимаций")
    st.markdown(
        "Ниже представлены четыре примера анимаций, созданных в ParaView (формат MP4, зацикленное воспроизведение).")

    video_dir = "video"

    col1, col2 = st.columns(2)

    with col1:
        video_path1 = os.path.join(video_dir, "anim1.mp4")
        if os.path.exists(video_path1):
            st.video(video_path1, format="video/mp4", loop=True)
            st.caption("Анимация 1: распространение волны")
        else:
            st.info("Файл anim1.mp4 не найден")

    with col2:
        video_path2 = os.path.join(video_dir, "anim2.mp4")
        if os.path.exists(video_path2):
            st.video(video_path2, format="video/mp4", loop=True)
            st.caption("Анимация 2: вращение кубика")
        else:
            st.info("Файл anim2.mp4 не найден")

    col3, col4 = st.columns(2)

    with col3:
        video_path3 = os.path.join(video_dir, "anim3.mp4")
        if os.path.exists(video_path3):
            st.video(video_path3, format="video/mp4", loop=True)
            st.caption("Анимация 3: пульсирующая поверхность")
        else:
            st.info("Файл anim3.mp4 не найден")

    with col4:
        video_path4 = os.path.join(video_dir, "anim4.mp4")
        if os.path.exists(video_path4):
            st.video(video_path4, format="video/mp4", loop=True)
            st.caption("Анимация 4: интерференция волн")
        else:
            st.info("Файл anim4.mp4 не найден")