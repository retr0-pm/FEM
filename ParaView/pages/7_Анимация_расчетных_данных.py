import streamlit as st
import os

st.set_page_config(
    page_title="ParaView: Анимация расчетных данных",
    layout="wide"
)

st.title("ParaView: Анимация расчетных данных")

menu = st.sidebar.radio(
    "Выберите раздел:",
    ["Работа с временными рядами",
     "Создание и настройка анимации",
     "Экспорт анимации и примеры"]
)

if menu == "Работа с временными рядами":

    st.markdown("### Загрузка данных с временными шагами")

    st.markdown("""
    ParaView поддерживает форматы, содержащие временные ряды:
    - Серии файлов (`solution_0000.vtk`, `solution_0001.vtk`, ...)
    - Файлы с временными метками (`.pvd`, `.vtm`, `.xdmf`)

    При загрузке ParaView автоматически определяет доступные временные шаги. На панели инструментов появляется ползунок времени (VCR-панель) для перемещения по кадрам.
    """)

    st.markdown("### Генерация данных в формате .vts")

    st.markdown("""
    Формат **.vts (StructuredGrid)** используется для структурированных сеток. В сочетании с файлом коллекции **.pvd** создается временной ряд из нескольких .vts файлов.

    Пример скрипта генерации волн:
    """)

    code_generate = '''import numpy as np
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

        # Точки
        f.write('      <Points>\\n')
        f.write('        <DataArray NumberOfComponents="3" type="Float32" format="ascii">\\n')

        points = []
        for j in range(ny):
            y = j * spacing
            for i in range(nx):
                x = i * spacing
                z = z_values[j, i]
                points.append(f"{x:.5f} {y:.5f} {z:.5f}")

        f.write("          " + "\\n          ".join(points) + "\\n")
        f.write('        </DataArray>\\n')
        f.write('      </Points>\\n')

        # Данные: амплитуда волны
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

    Z = np.zeros_like(X)

    sources = [
        (center[0] + 0.5*np.sin(time_val*0.3), center[1] + 0.5*np.cos(time_val*0.4), 1.0),
        (center[0] - 0.8 + 0.3*np.sin(time_val*0.5), center[1] - 0.8, 0.7),
        (center[0] + 0.8, center[1] + 0.8 - 0.4*np.sin(time_val*0.6), 0.5),
    ]

    for sx, sy, amp in sources:
        R = np.sqrt((X-sx)**2 + (Y-sy)**2)
        wave = amp * np.sin(R*4 - time_val*3) * np.exp(-R/1.5) * np.exp(-time_val*0.02)
        Z += wave

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
    **Параметры скрипта:**
    - Сетка 50×50 точек
    - 45 временных шагов
    - Три источника волн с движущимися координатами

    **Загрузка в ParaView:**
    1. File → Open → выбрать `wave3d.pvd`
    2. Apply
    3. На панели инструментов появится ползунок времени
    """)

elif menu == "Создание и настройка анимации":

    st.markdown("### Programmable Source")

    st.markdown("""
    **Programmable Source** — источник данных, создающий геометрию через Python-скрипты в процессе визуализации. Данные генерируются на лету для каждого временного шага.

    Чтобы создать анимированный источник:
    1. Sources → Programmable Source
    2. Заполнить два скрипта: Script и RequestInformation Script
    """)

    st.markdown("#### Script")

    code_script = '''import vtk
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

# Генерация точек с волной
idx = 0
for j in range(ny):
    y = ymin + j * dy
    for i in range(nx):
        x = xmin + i * dx
        r = math.sqrt(x*x + y*y)
        z = math.sin(r * 1.5 - time * 2 * math.pi)
        points.SetPoint(idx, x, y, z)
        idx += 1

# Создание ячеек (квадраты)
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

# Скаляр для раскраски
scalars = vtk.vtkDoubleArray()
scalars.SetName('Height')
scalars.SetNumberOfValues(nx * ny)
for i in range(nx * ny):
    scalars.SetValue(i, points.GetPoint(i)[2])
output.GetPointData().AddArray(scalars)
output.GetPointData().SetActiveScalars('Height')
'''

    st.code(code_script, language='python')

    st.markdown("""
    **Что делает Script:**
    - Получает текущее время из ParaView
    - Создает сетку 40×40 точек
    - Вычисляет z-координату как функцию от расстояния и времени (бегущая волна)
    - Создает четырехугольные ячейки
    - Добавляет скалярное поле Height для раскраски
    """)

    st.markdown("#### RequestInformation Script")

    code_reqinfo = '''from paraview import vtk
import numpy as np

outInfo = self.GetOutputInformation(0)

# Временные шаги
timesteps = np.linspace(0, 5.0, 100).tolist()

# Диапазон и список шагов
outInfo.Set(vtk.vtkStreamingDemandDrivenPipeline.TIME_RANGE(), [0.0, 5.0], 2)
outInfo.Set(vtk.vtkStreamingDemandDrivenPipeline.TIME_STEPS(), timesteps, len(timesteps))
'''

    st.code(code_reqinfo, language='python')

    st.markdown("""
    **Что делает RequestInformation:**
    - Выполняется один раз при инициализации
    - Сообщает ParaView о доступных временных шагах (от 0 до 5 с шагом 0.05)
    - После этого появляется ползунок времени
    - При изменении положения ползунка вызывается Script с соответствующим значением time
    """)

    st.markdown("### Использование")
    st.markdown("""
    1. Настроить Programmable Source с этими скриптами
    2. Применить фильтры (например, Warp By Scalar для поднятия геометрии по Z)
    3. Настроить цвет
    4. Запустить анимацию — данные генерируются для каждого кадра
    """)

elif menu == "Экспорт анимации и примеры":

    st.markdown("### Сохранение анимации")

    st.markdown("""
    **File → Save Animation**

    **Форматы:**
    - AVI, OGG, MP4 — видеофайлы
    - PNG, JPEG, TIFF, BMP — последовательности изображений

    **Параметры:**
    - FrameRate — частота кадров (15, 24, 30 кадров/с)
    - Разрешение
    - Кодек (для видео)
    """)

    st.markdown("### Примеры готовых анимаций")

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