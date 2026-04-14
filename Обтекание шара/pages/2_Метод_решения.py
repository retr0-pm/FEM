import streamlit as st

st.set_page_config(page_title="Метод решения", layout="wide")

menu = st.sidebar.radio('***',
                        ("Вариационная постановка",
                         "Конечно-элементная аппроксимация",
                         "Вычислительный алгоритм",
                         "Фрагменты кода",
                         )
                        )

if menu == "Вариационная постановка":
    st.markdown(r"""
    ##### Вариационная (слабая) постановка задачи

    **Исходное уравнение для потенциала скорости**

    $\begin{aligned}
    \frac{1}{r} \frac{\partial}{\partial r} \left( r \frac{\partial \varphi}{\partial r} \right) + 
    \frac{\partial^2 \varphi}{\partial z^2} = 0,
    \quad (r, z) \in \Omega
    \end{aligned}$

    **Умножение на тестовую функцию и интегрирование**

    Умножим уравнение на тестовую функцию $v$ и проинтегрируем по области с весом $r$:

    $\begin{aligned}
    \int_{\Omega} \left[ \frac{\partial}{\partial r} \left( r \frac{\partial \varphi}{\partial r} \right) + 
    r \frac{\partial^2 \varphi}{\partial z^2} \right] v \, dr dz = 0
    \end{aligned}$

    **Интегрирование по частям**

    После интегрирования по частям получаем:

    $\begin{aligned}
    \int_{\Omega} \left( \frac{\partial \varphi}{\partial r} \frac{\partial v}{\partial r} + 
    \frac{\partial \varphi}{\partial z} \frac{\partial v}{\partial z} \right) r \, dr dz = 0
    \end{aligned}$

    **Граничные условия**

    - На внешней границе $\Gamma$: $\varphi = u_\infty z$ (условие Дирихле)
    - На поверхности шара: $\frac{\partial \varphi}{\partial n} = 0$ (естественное условие Неймана)
    - На оси симметрии: $\frac{\partial \varphi}{\partial r} = 0$ (естественное условие)

    **Итоговая вариационная задача**

    Найти $\varphi \in V$ такую, что:

    $\begin{aligned}
    \int_{\Omega} \nabla \varphi \cdot \nabla v \, r dr dz = 0,
    \quad \forall v \in V_0
    \end{aligned}$

    где $V_0$ - пространство тестовых функций, равных нулю на внешней границе.
    """)

if menu == "Конечно-элементная аппроксимация":
    st.markdown(r"""
    ##### Конечно-элементная аппроксимация

    **Дискретизация области**

    Расчетная область $\Omega$ разбивается на треугольные элементы $K_e$:

    $\begin{aligned}
    \Omega \approx \Omega_h = \bigcup_{e=1}^{N_e} K_e
    \end{aligned}$

    **Функциональные пространства**

    Используются лагранжевы конечные элементы степени $p$:

    $\begin{aligned}
    V_h = \{v_h \in C^0(\Omega_h) : v_h|_{K_e} \in P_p(K_e)\}
    \end{aligned}$

    где $P_p$ - полиномы степени $p$:
    - $p=1$: линейные функции (3 узла на треугольник)
    - $p=2$: квадратичные функции (6 узлов на треугольник)  
    - $p=3$: кубические функции (10 узлов на треугольник)

    **Аппроксимация решения**

    $\begin{aligned}
    \varphi_h(r, z) = \sum_{j=1}^{N} \varphi_j \phi_j(r, z)
    \end{aligned}$

    где $\phi_j$ - базисные функции, $\varphi_j$ - узловые значения.

    **Дискретная задача**

    Найти $\varphi_h \in V_h$:

    $\begin{aligned}
    \int_{\Omega_h} \nabla \varphi_h \cdot \nabla v_h \, r dr dz = 0,
    \quad \forall v_h \in V_{0h}
    \end{aligned}$

    **Система линейных уравнений**

    $\begin{aligned}
    \mathbf{A} \boldsymbol{\varphi} = \mathbf{0}
    \end{aligned}$

    где элементы матрицы:

    $\begin{aligned}
    A_{ij} = \int_{\Omega_h} \nabla \phi_i \cdot \nabla \phi_j \, r dr dz
    \end{aligned}$
    """)

if menu == "Вычислительный алгоритм":
    st.markdown(r"""
    ##### Вычислительный алгоритм

    **1. Предварительный этап**
    - Генерация сетки в Gmsh с маркировкой границ
    - Конвертация в формат XDMF через `meshio`

    **2. Инициализация в FEniCS**
    - Загрузка сетки: `Mesh()` + `XDMFFile.read()`
    - Создание маркеров границ: `MeshFunction`
    - Определение пространства: `FunctionSpace(mesh, 'P', degree)`

    **3. Задание вариационной формы**
    - Определение пробной и тестовой функций
    - Задание билинейной формы с весом $r$
    - Учет граничных условий Дирихле

    **4. Решение СЛАУ**
    - Автоматическая сборка матрицы в FEniCS
    - Решение прямым методом (LU-разложение)

    **5. Постобработка**
    - Вычисление скорости: `project(grad(phi), W)`
    - Расчет касательной скорости на поверхности шара
    - Визуализация результатов

    **6. Верификация**
    - Сравнение с точным решением $u_\theta = 1.5 u_\infty \sin\theta$
    - Вычисление L2-нормы ошибки
    - Анализ сходимости на последовательности сеток
    """)

if menu == "Фрагменты кода":
    st.markdown(r"""
    ##### Фрагменты кода (реализация в FEniCS)

    **Загрузка сетки и создание пространства**
    """)

    code = """
from dolfin import *

# Загрузка сетки
mesh = Mesh()
with XDMFFile("mesh_sphere_R5.0_level2.xdmf") as infile:
    infile.read(mesh)

# Создание функционального пространства
degree = 2  # степень полиномов
V = FunctionSpace(mesh, 'P', degree)
    """
    st.code(code, language="python")

    st.markdown(r"""
    **Маркировка границ**
    """)

    code = """
# Создание маркеров границ
boundaries = MeshFunction("size_t", mesh, mesh.topology().dim()-1)
boundaries.set_all(0)

class SphereBoundary(SubDomain):
    def inside(self, x, on_boundary):
        r, z = x[1], x[0]
        return on_boundary and near(r*r + z*z, 1.0, 1e-2) and r > 0

class OuterBoundary(SubDomain):
    def inside(self, x, on_boundary):
        r, z = x[1], x[0]
        return on_boundary and near(r*r + z*z, 25.0, 5e-1) and r > 0

sphere_bd = SphereBoundary()
outer_bd = OuterBoundary()
sphere_bd.mark(boundaries, 1)  # поверхность шара
outer_bd.mark(boundaries, 2)   # внешняя граница
    """
    st.code(code, language="python")

    st.markdown(r"""
    **Вариационная задача**
    """)

    code = """
# Пробная и тестовая функции
phi = TrialFunction(V)
v = TestFunction(V)

# Координаты
x = SpatialCoordinate(mesh)
r = x[1]

# Билинейная форма с весом r
a = (phi.dx(0) * v.dx(0) + phi.dx(1) * v.dx(1)) * r * dx
L = Constant(0.0) * v * dx
    """
    st.code(code, language="python")

    st.markdown(r"""
    **Граничные условия и решение**
    """)

    code = """
# Условие на внешней границе: φ = u_inf * z
u_inf = 1.0
bc_outer = DirichletBC(V, Expression('u_inf * x[0]', degree=degree, u_inf=u_inf), 
                       boundaries, 2)

# Решение
phi = Function(V)
solve(a == L, phi, bc_outer)
    """
    st.code(code, language="python")

    st.markdown(r"""
    **Вычисление поля скорости**
    """)

    code = """
# Пространство для векторного поля
W = VectorFunctionSpace(mesh, 'P', degree)

# Скорость как градиент потенциала
velocity = project(grad(phi), W)
    """
    st.code(code, language="python")

    st.markdown(r"""
    **Вычисление касательной скорости на поверхности шара**
    """)

    code = """
def compute_surface_velocity(phi, V, a=1.0, u_inf=1.0):
    velocity = project(grad(phi), VectorFunctionSpace(V.mesh(), 'P', V.ufl_element().degree()))

    coords = V.mesh().coordinates()
    theta_vals, v_vals = [], []

    for x in coords:
        r, z = x[1], x[0]
        if near(r*r + z*z, a*a, 1e-2) and r > 0.05:
            vel = velocity(x)
            # Касательный вектор: t = (r/a, -z/a)
            v_t = vel[0] * (r/a) + vel[1] * (-z/a)

            theta = np.arccos(np.clip(-z/a, -1.0, 1.0))
            theta_vals.append(theta)
            v_vals.append(v_t)

    return np.array(theta_vals), np.array(v_vals)

theta, v_num = compute_surface_velocity(phi, V)
v_exact = 1.5 * u_inf * np.sin(theta)
    """
    st.code(code, language="python")