import streamlit as st
import json
import os

st.set_page_config(page_title="Расчетная сетка", layout="wide")

# Абсолютный путь к папке meshes
MESH_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "meshes")

menu = st.sidebar.radio('***',
                        ("Описание сетки",
                         "Визуализация сеток",
                         "Параметры сеток",
                         "Код генератора",
                         )
                        )

if menu == "Описание сетки":
    st.markdown(r"""
    ##### Построение расчетной сетки

    **Геометрия области**

    Расчетная область строится в цилиндрических координатах $(z, r)$:
    - Ось $z$ направлена горизонтально (слева направо)
    - Ось $r$ направлена вертикально (вверх)
    - Шар моделируется как полукруг радиуса $a=1$ с центром в $(0,0)$
    - Внешняя граница — полукруг радиуса $R$
    - Ось симметрии — прямая $r=0$

    **Генерация сетки в Gmsh**

    Сетка строится с использованием генератора Gmsh. Основные этапы:
    1. Определение геометрических точек и кривых
    2. Создание замкнутого контура области
    3. Определение физических групп для граничных условий
    4. Генерация треугольной сетки

    **Физические группы**
    - Группа 1: поверхность шара (условие непротекания)
    - Группа 2: внешняя граница (равномерный поток)
    - Группа 3: ось симметрии (условие симметрии)
    - Группа 4: расчетная область
    """)

elif menu == "Визуализация сеток":
    st.markdown("##### Визуализация расчетных сеток")

    stats_file = os.path.join(MESH_DIR, "stats.json")

    if os.path.exists(stats_file):
        with open(stats_file, 'r', encoding='utf-8') as f:
            stats = json.load(f)

        R_values = sorted(list(set([s['R'] for s in stats])))
        levels = sorted(list(set([s['level'] for s in stats])))

        col1, col2 = st.columns(2)
        with col1:
            R_select = st.selectbox("Радиус внешней границы $R$", R_values)
        with col2:
            level_select = st.selectbox("Уровень сгущения", levels)

        # Поиск нужной сетки
        for s in stats:
            if s['R'] == R_select and s['level'] == level_select:
                png_file = s['png']
                nodes = s['nodes']
                elements = s['elements']

                if os.path.exists(png_file):
                    st.image(png_file, caption=f"R={R_select}, {level_select} (узлов: {nodes}, элементов: {elements})")
                else:
                    st.warning(f"Изображение не найдено: {png_file}")
                break
    else:
        st.warning(f"Файл статистики не найден: {stats_file}")
        st.info("Запустите генератор сеток: `python generate_meshes.py`")

elif menu == "Параметры сеток":
    st.markdown("##### Параметры расчетных сеток")

    stats_file = os.path.join(MESH_DIR, "stats.json")

    if os.path.exists(stats_file):
        with open(stats_file, 'r', encoding='utf-8') as f:
            stats = json.load(f)

        import pandas as pd

        st.markdown("**Все сгенерированные сетки:**")

        data = []
        for s in stats:
            data.append({
                'Радиус R': s['R'],
                'Уровень': s['level'],
                'Фактор': s['factor'],
                'Узлы': s['nodes'],
                'Элементы': s['elements']
            })

        df = pd.DataFrame(data)
        st.table(df)
    else:
        st.warning(f"Файл статистики не найден: {stats_file}")
        st.info("Запустите генератор сеток: `python generate_meshes.py`")

elif menu == "Код генератора":
    st.markdown("##### Код генератора сетки")

    code = '''import gmsh
import meshio
import os
import json
import numpy as np
import matplotlib.pyplot as plt

def create_mesh_for_sphere(a=1.0, R=5.0, mesh_size_factor=1.0, output_file="mesh"):
    """Создание расчетной сетки для обтекания шара"""

    gmsh.initialize()
    gmsh.model.add("sphere_flow")

    base_size = 0.15 * mesh_size_factor

    # Точки
    center = gmsh.model.geo.addPoint(0, 0, 0, base_size)
    p1 = gmsh.model.geo.addPoint(-a, 0, 0, base_size)
    p2 = gmsh.model.geo.addPoint(0, a, 0, base_size)
    p3 = gmsh.model.geo.addPoint(a, 0, 0, base_size)
    p4 = gmsh.model.geo.addPoint(-R, 0, 0, base_size * 3)
    p5 = gmsh.model.geo.addPoint(0, R, 0, base_size * 3)
    p6 = gmsh.model.geo.addPoint(R, 0, 0, base_size * 3)

    # Кривые
    circle1 = gmsh.model.geo.addCircleArc(p1, center, p2)
    circle2 = gmsh.model.geo.addCircleArc(p2, center, p3)
    outer1 = gmsh.model.geo.addCircleArc(p6, center, p5)
    outer2 = gmsh.model.geo.addCircleArc(p5, center, p4)
    sym_left = gmsh.model.geo.addLine(p4, p1)
    sym_right = gmsh.model.geo.addLine(p3, p6)

    # Контур и поверхность
    cl1 = gmsh.model.geo.addCurveLoop([sym_left, circle1, circle2, 
                                       sym_right, outer1, outer2])
    surf1 = gmsh.model.geo.addPlaneSurface([cl1])

    gmsh.model.geo.synchronize()

    # Физические группы
    gmsh.model.addPhysicalGroup(1, [circle1, circle2], tag=1)
    gmsh.model.addPhysicalGroup(1, [outer1, outer2], tag=2)
    gmsh.model.addPhysicalGroup(1, [sym_left, sym_right], tag=3)
    gmsh.model.addPhysicalGroup(2, [surf1], tag=4)

    # Генерация сетки
    gmsh.option.setNumber("Mesh.CharacteristicLengthFactor", mesh_size_factor)
    gmsh.model.mesh.generate(2)

    # Сохранение и конвертация...
    gmsh.write(f"{output_file}.msh")
    gmsh.finalize()

    # Конвертация в XDMF через meshio...
    return output_file'''

    st.code(code, language="python")