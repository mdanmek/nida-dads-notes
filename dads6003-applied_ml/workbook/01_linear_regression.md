# Workbook 01: Linear Regression — จากสมการสู่โค้ดที่รันได้จริง

บทเรียนนี้พัฒนาจาก [`linear_regression.ipynb`](../lab/linear_regression.ipynb) โดยคง notebook ต้นฉบับไว้เหมือนเดิม แล้วนำแนวคิดและโค้ดมาเรียบเรียงใหม่ให้เรียน Machine Learning และ Python ไปพร้อมกัน

> หากต้องการทบทวนทฤษฎีแบบละเอียด อ่าน [`02_linear_regression.md`](../summary/02_linear_regression.md) ควบคู่กันได้ ส่วน workbook นี้จะเน้นว่า “แต่ละบรรทัดทำอะไร ทำไมต้องทำ และตรวจความถูกต้องอย่างไร”

## เป้าหมายการเรียนรู้

เมื่อเรียนจบบทนี้ เราควรสามารถ:

1. อธิบายสมการ Linear Regression และความหมายของ intercept กับ coefficient ได้
2. สร้างโมเดลด้วย Normal Equation ทั้งแบบ NumPy และ scikit-learn
3. เข้าใจรูปร่างของข้อมูลหรือ `shape` ที่แต่ละคำสั่งต้องการ
4. อธิบาย Gradient Descent, learning rate และ stopping condition ได้
5. อ่านผลลัพธ์ ตรวจข้อผิดพลาด และปรับโค้ดใน notebook ให้รันใหม่ได้จริง

---

## 1. ภาพรวมของโจทย์

ข้อมูลตัวอย่างมีเพียง 3 จุด:

| ตัวอย่าง | $x$ | $y$ |
|---:|---:|---:|
| 1 | 0 | 1 |
| 2 | 2 | 1 |
| 3 | 3 | 4 |

เราต้องการหาเส้นตรงที่อธิบายความสัมพันธ์ระหว่าง $x$ และ $y$:

$$
\hat{y}=\theta_0+\theta_1x
$$

- $\hat{y}$ คือค่าที่โมเดลทำนาย
- $\theta_0$ คือ intercept หรือค่าทำนายเมื่อ $x=0$
- $\theta_1$ คือ coefficient หรือความชันของเส้น

Notebook ใช้ 3 วิธีหา parameter ชุดเดียวกัน:

1. คำนวณ Normal Equation ด้วย NumPy
2. ใช้ `LinearRegression` จาก scikit-learn
3. ค่อย ๆ ปรับ parameter ด้วย Gradient Descent

ทั้งสามวิธีควรได้คำตอบใกล้เคียงกัน คือ

$$
\theta_0\approx0.571,\qquad \theta_1\approx0.857
$$

ดังนั้นสมการที่ได้คือ

$$
\hat{y}=0.571+0.857x
$$

## 2. ตรวจ notebook ก่อนเริ่มเรียน

Notebook เป็นตัวอย่างที่ดีสำหรับดูแนวคิด แต่มีบางจุดที่ควรรู้ก่อนกด **Run all**:

| จุดที่พบ | ผลที่อาจเกิดขึ้น | วิธีที่ใช้ใน workbook นี้ |
|---|---|---|
| ฟังก์ชันชื่อ `J` แต่ Gradient Descent เรียก `cost_function` | `NameError` เมื่อรันใน session ใหม่ | ใช้ชื่อ `half_mse` ให้ตรงกันทุกจุด |
| ทุก cell มี `execution_count=None` แต่ยังมี output เก็บอยู่ | output อาจมาจาก runtime เก่า | ยืนยันผลด้วยโค้ดที่รันจากต้นจนจบได้ |
| loop ใช้ `for x, y in ...` | เขียนทับตัวแปรข้อมูลเดิม | ใช้ชื่อ `x_point`, `y_point` |
| ใช้ global dictionary เก็บประวัติ | ฟังก์ชันพึ่งพาสถานะภายนอกและรันซ้ำยาก | คืนค่า `history` ออกจากฟังก์ชัน |
| กราฟใส่ marker ซ้ำทั้งใน format string และ argument | เกิด warning | ระบุ marker เพียงที่เดียว |
| cell หนึ่งมีประวัติ 4,241 จุด แต่ output ก่อนหน้าระบุว่าหยุดราว iteration 2,454 | output ไม่สอดคล้องกัน | สร้างประวัติใหม่ในการรันแต่ละครั้ง |

หลักสำคัญคือ **output ที่มองเห็นไม่ได้รับประกันว่าโค้ดปัจจุบันยังรันได้** จึงควร Restart session แล้ว Run all ก่อนใช้ผลในรายงาน

---

## 3. Normal Equation ด้วย NumPy

### 3.1 สร้างข้อมูล

```python
import numpy as np

np.set_printoptions(precision=3, suppress=True)

x = np.array([0, 2, 3], dtype=float)
y = np.array([1, 1, 4], dtype=float)

print('x shape:', x.shape)
print('y shape:', y.shape)
```

ผลลัพธ์ของทั้งสองตัวแปรมี `shape` เป็น `(3,)` หมายถึง vector หนึ่งมิติที่มี 3 ค่า

#### คำสั่งสำคัญ

| คำสั่ง | หน้าที่ | argument ที่ใช้ |
|---|---|---|
| `np.array(...)` | สร้าง NumPy array | ข้อมูล และ `dtype=float` เพื่อให้คำนวณเลขทศนิยมได้ชัดเจน |
| `np.set_printoptions(...)` | ตั้งค่าการแสดงผล ไม่เปลี่ยนค่าจริง | `precision=3` แสดง 3 ตำแหน่ง, `suppress=True` ลด scientific notation |
| `.shape` | บอกจำนวนมิติและขนาด | เป็น attribute จึงไม่ใส่วงเล็บ |

### 3.2 ทำไมต้องเพิ่มคอลัมน์เลข 1

สมการ $\hat{y}=\theta_0+\theta_1x$ เขียนเป็น matrix ได้ว่า

$$
\hat{\mathbf{y}}=\mathbf{X}\boldsymbol{\theta}
$$

เพื่อให้ matrix multiplication คำนวณ $\theta_0$ ได้ เราต้องเพิ่มคอลัมน์เลข 1 หน้า $x$:

```python
x_design = np.c_[np.ones((len(x), 1)), x]

print(x_design)
print('Design matrix shape:', x_design.shape)
```

ผลลัพธ์คือ

```text
[[1. 0.]
 [1. 2.]
 [1. 3.]]
```

แต่ละแถวแทนข้อมูลหนึ่งตัวอย่าง ส่วนแต่ละคอลัมน์แทน feature:

- คอลัมน์แรกคูณกับ $\theta_0$
- คอลัมน์ที่สองคูณกับ $\theta_1$

`np.ones((len(x), 1))` สร้าง array ขนาด 3 แถว 1 คอลัมน์ ส่วน `np.c_` นำ array มาต่อกันตามแนวคอลัมน์

### 3.3 คำนวณ Normal Equation

Normal Equation คือ

$$
\boldsymbol{\theta}=(\mathbf{X}^{T}\mathbf{X})^{-1}\mathbf{X}^{T}\mathbf{y}
$$

เขียนเป็นโค้ดได้ว่า

```python
theta = (
    np.linalg.inv(x_design.T @ x_design)
    @ x_design.T
    @ y
)

print('theta:', theta)
```

ผลที่ควรได้:

```text
theta: [0.571 0.857]
```

#### อ่าน operator และ attribute ในสูตร

| ส่วนของโค้ด | ความหมาย |
|---|---|
| `x_design.T` | transpose สลับแถวกับคอลัมน์ |
| `@` | matrix multiplication |
| `np.linalg.inv(...)` | หา inverse ของ square matrix |
| `theta[0]` | intercept $\theta_0$ |
| `theta[1]` | coefficient $\theta_1$ |

ตรวจขนาด matrix ก่อนคูณ:

| Matrix | Shape |
|---|---:|
| $\mathbf{X}$ | $3\times2$ |
| $\mathbf{X}^{T}$ | $2\times3$ |
| $\mathbf{X}^{T}\mathbf{X}$ | $2\times2$ |
| $\mathbf{X}^{T}\mathbf{y}$ | $2\times1$ |
| $\boldsymbol{\theta}$ | $2\times1$ |

### 3.4 คำนวณด้วยมือเพื่อตรวจคำตอบ

สำหรับข้อมูลนี้:

$$
\mathbf{X}^{T}\mathbf{X}
=
\begin{bmatrix}
3 & 5\\
5 & 13
\end{bmatrix},
\qquad
\mathbf{X}^{T}\mathbf{y}
=
\begin{bmatrix}
6\\
14
\end{bmatrix}
$$

จึงได้

$$
\boldsymbol{\theta}
=
\begin{bmatrix}
4/7\\
6/7
\end{bmatrix}
\approx
\begin{bmatrix}
0.571\\
0.857
\end{bmatrix}
$$

การตรวจด้วยมือช่วยแยกว่า error มาจากความเข้าใจสูตรหรือจากการเขียนโค้ด

### 3.5 Best practice: ไม่จำเป็นต้องหา inverse โดยตรง

การใช้ `inv()` เหมาะกับการสาธิตสูตร แต่ในการทำงานจริง `np.linalg.lstsq()` มักมีเสถียรภาพเชิงตัวเลขดีกว่าและรับมือกรณี matrix หา inverse ไม่ได้:

```python
theta_lstsq, residuals, rank, singular_values = np.linalg.lstsq(
    x_design,
    y,
    rcond=None
)

print('theta from lstsq:', theta_lstsq)
print('matrix rank:', rank)
```

| ค่าที่คืนมา | ความหมาย |
|---|---|
| `theta_lstsq` | parameter ที่ทำให้ผลรวม squared errors ต่ำที่สุด |
| `residuals` | ผลรวม squared residuals ในกรณีที่คำนวณได้ |
| `rank` | จำนวนมิติอิสระของ design matrix |
| `singular_values` | ค่า singular values ใช้ช่วยตรวจสภาพของ matrix |
| `rcond=None` | ใช้ค่าเกณฑ์มาตรฐานของ NumPy ในการมอง singular value ขนาดเล็ก |

อีกทางเลือกคือ `np.linalg.pinv(x_design) @ y` ซึ่งใช้ Moore–Penrose pseudoinverse

---

## 4. ใช้โมเดลทำนาย

### 4.1 ทำนายด้วยสมการ

```python
x_new = np.arange(0, 11, dtype=float)
y_pred_numpy = theta[0] + theta[1] * x_new

print(y_pred_numpy)
```

`np.arange(0, 11)` สร้างค่าเริ่มที่ 0 และหยุดก่อน 11 จึงได้ 0–10

ตัวอย่าง เมื่อ $x=5$:

$$
\hat{y}=0.571+(0.857)(5)\approx4.857
$$

### 4.2 วาดข้อมูลจริงกับเส้นทำนาย

```python
import matplotlib.pyplot as plt

plt.figure(figsize=(7, 4.5))
plt.scatter(x, y, color='steelblue', s=60, label='Observed data')
plt.plot(x_new, y_pred_numpy, color='firebrick', linewidth=2, label='Prediction line')

for x_point, y_point in zip(x, y):
    plt.annotate(
        f'({x_point:.0f}, {y_point:.0f})',
        (x_point, y_point),
        xytext=(5, 6),
        textcoords='offset points'
    )

plt.title('Linear Regression Fit')
plt.xlabel('x')
plt.ylabel('y')
plt.legend(frameon=False)
plt.grid(alpha=0.2)
plt.tight_layout()
plt.show()
```

#### เหตุผลที่ไม่ใช้ `for x, y in zip(x, y)`

Python จะเก็บค่ารอบสุดท้ายกลับลงในชื่อ `x` และ `y` ทำให้ array เดิมถูกเขียนทับ การใช้ `x_point` และ `y_point` ทำให้ความหมายชัดและไม่เปลี่ยน state ที่ cell ถัดไปต้องใช้

---

## 5. Linear Regression ด้วย scikit-learn

scikit-learn ซ่อนขั้นตอน matrix calculation ไว้ ทำให้เราโฟกัส workflow มาตรฐาน: เตรียมข้อมูล → สร้างโมเดล → fit → predict

### 5.1 เตรียม `X` และ `y`

```python
from sklearn.linear_model import LinearRegression

X = x.reshape(-1, 1)

print('X shape:', X.shape)
print('y shape:', y.shape)
```

scikit-learn ต้องการ:

- `X` เป็น 2 มิติ: `(n_samples, n_features)` ซึ่งในตัวอย่างคือ `(3, 1)`
- `y` เป็น 1 มิติ: `(n_samples,)` ซึ่งคือ `(3,)`

`reshape(-1, 1)` หมายถึงให้ NumPy คำนวณจำนวนแถวเอง (`-1`) และกำหนดให้มี 1 คอลัมน์

### 5.2 สร้างและ train โมเดล

```python
linear_model = LinearRegression(fit_intercept=True)
linear_model.fit(X, y)

print(f'Intercept: {linear_model.intercept_:.3f}')
print(f'Coefficient: {linear_model.coef_[0]:.3f}')
```

ผลควรเป็น:

```text
Intercept: 0.571
Coefficient: 0.857
```

#### Function, parameter และ attribute

| รายการ | ประเภท | ความหมาย |
|---|---|---|
| `LinearRegression(...)` | constructor | สร้าง estimator แต่ยังไม่ได้เรียนรู้ข้อมูล |
| `fit_intercept=True` | model parameter | ให้โมเดลประมาณค่า intercept; ไม่ควรเพิ่มคอลัมน์เลข 1 เองพร้อมกัน |
| `.fit(X, y)` | method | เรียนรู้ parameter จากข้อมูล |
| `X`, `y` | arguments | ข้อมูลที่ส่งให้ method ตอนเรียกใช้ |
| `.intercept_` | learned attribute | intercept ที่ได้หลัง `fit()` |
| `.coef_` | learned attribute | coefficient ของแต่ละ feature หลัง `fit()` |

คำลงท้าย `_` ใน scikit-learn มักบอกว่า attribute นั้นเกิดจากการเรียนรู้หลังเรียก `fit()` หากอ่านก่อน fit จะเกิด `NotFittedError` หรือยังไม่มี attribute นั้น

### 5.3 ทำนายข้อมูลใหม่

```python
X_new = np.array([[1.0], [5.0]])
y_pred_sklearn = linear_model.predict(X_new)

print(y_pred_sklearn)
```

ผลควรใกล้เคียง:

```text
[1.429 4.857]
```

ข้อควรจำคือแม้มีเพียง feature เดียว ข้อมูลใหม่ก็ยังต้องเป็น 2 มิติ เช่น `[[1.0], [5.0]]` ไม่ใช่ `[1.0, 5.0]`

### 5.4 ตรวจว่าสองวิธีให้คำตอบตรงกัน

```python
theta_sklearn = np.array([
    linear_model.intercept_,
    linear_model.coef_[0]
])

print(np.allclose(theta, theta_sklearn))
```

`np.allclose()` เปรียบเทียบเลขทศนิยมโดยยอมให้ต่างกันเล็กน้อย เพราะ floating-point computation อาจไม่ตรงกันทุกหลัก

---

## 6. Gradient Descent

Normal Equation คำนวณคำตอบโดยตรง ส่วน Gradient Descent เริ่มจาก parameter ชุดหนึ่ง แล้วปรับทีละน้อยให้ cost ลดลง

### 6.1 Cost function

เพื่อให้ derivative เขียนได้กระชับ เราใช้ half mean squared error:

$$
J(\theta_0,\theta_1)
=\frac{1}{2N}\sum_{i=1}^{N}
(\hat{y}^{(i)}-y^{(i)})^2
$$

ตัวคูณ $1/2$ ไม่เปลี่ยนจุดต่ำสุด แต่ทำให้เลข 2 จากการหาอนุพันธ์ตัดกันพอดี

Gradient คือ

$$
\frac{\partial J}{\partial \theta_0}
=\frac{1}{N}\sum_{i=1}^{N}(\hat{y}^{(i)}-y^{(i)})
$$

$$
\frac{\partial J}{\partial \theta_1}
=\frac{1}{N}\sum_{i=1}^{N}(\hat{y}^{(i)}-y^{(i)})x^{(i)}
$$

แล้วอัปเดตพร้อมกัน:

$$
\theta_j\leftarrow\theta_j-\eta\frac{\partial J}{\partial\theta_j}
$$

$\eta$ อ่านว่า eta และหมายถึง learning rate

### 6.2 ดูการอัปเดตรอบแรกด้วยมือ

ให้ $\theta_0=0.1$, $\theta_1=0.1$:

- prediction คือ $[0.1,0.3,0.4]$
- error หรือ $\hat{y}-y$ คือ $[-0.9,-0.7,-3.6]$
- gradient ของ $\theta_0$ เท่ากับ $-1.7333$
- gradient ของ $\theta_1$ เท่ากับ $-4.0667$

ถ้า $\eta=0.01$ จะได้:

$$
\theta_0\leftarrow0.1-0.01(-1.7333)=0.1173
$$

$$
\theta_1\leftarrow0.1-0.01(-4.0667)=0.1407
$$

parameter ขยับไปในทิศทางที่ทำให้ cost ลดลง

### 6.3 เวอร์ชันที่รันได้จริงและไม่พึ่ง global variable

```python
def half_mse(theta0, theta1, x_values, y_values):
    predictions = theta0 + theta1 * x_values
    errors = predictions - y_values
    return 0.5 * np.mean(errors ** 2)


def gradient_descent(
    x_values,
    y_values,
    learning_rate=0.01,
    tolerance=1e-11,
    max_iter=5000,
    initial_theta0=0.1,
    initial_theta1=0.1
):
    x_values = np.asarray(x_values, dtype=float).reshape(-1)
    y_values = np.asarray(y_values, dtype=float).reshape(-1)

    if x_values.shape != y_values.shape:
        raise ValueError('x_values and y_values must have the same length')

    theta0 = float(initial_theta0)
    theta1 = float(initial_theta1)
    previous_cost = half_mse(theta0, theta1, x_values, y_values)
    history = []

    for iteration in range(1, max_iter + 1):
        predictions = theta0 + theta1 * x_values
        errors = predictions - y_values

        gradient0 = np.mean(errors)
        gradient1 = np.mean(errors * x_values)

        new_theta0 = theta0 - learning_rate * gradient0
        new_theta1 = theta1 - learning_rate * gradient1
        new_cost = half_mse(
            new_theta0,
            new_theta1,
            x_values,
            y_values
        )

        history.append({
            'iteration': iteration,
            'theta0': new_theta0,
            'theta1': new_theta1,
            'cost': new_cost
        })

        if abs(previous_cost - new_cost) <= tolerance:
            theta0 = new_theta0
            theta1 = new_theta1
            break

        theta0 = new_theta0
        theta1 = new_theta1
        previous_cost = new_cost

    return np.array([theta0, theta1]), history
```

รันฟังก์ชัน:

```python
theta_gd, gd_history = gradient_descent(
    x,
    y,
    learning_rate=0.01,
    tolerance=1e-11,
    max_iter=5000
)

print('Gradient Descent theta:', theta_gd)
print('Iterations:', len(gd_history))
print('Final cost:', gd_history[-1]['cost'])
print('Close to Normal Equation:', np.allclose(theta_gd, theta, atol=1e-4))
```

### 6.4 Parameter ของ Gradient Descent

| Parameter | หน้าที่ | ถ้าตั้งไม่เหมาะสม |
|---|---|---|
| `learning_rate` | ขนาดก้าวในการปรับ parameter | เล็กเกินไปช้า; ใหญ่เกินไปอาจแกว่งหรือ divergence |
| `tolerance` | เกณฑ์ว่าการเปลี่ยนแปลงของ cost เล็กพอที่จะหยุด | ใหญ่เกินไปหยุดเร็ว; เล็กเกินไปเสียเวลามาก |
| `max_iter` | จำนวนรอบสูงสุด เป็น safety limit | ต่ำเกินไปอาจหยุดก่อน convergence |
| `initial_theta0`, `initial_theta1` | จุดเริ่มต้น | มีผลต่อเส้นทางและเวลาที่ใช้ โดยเฉพาะปัญหาที่ซับซ้อน |

### 6.5 ทำไมต้องคำนวณ `new_theta0` และ `new_theta1` ก่อน

Gradient ทั้งสองตัวต้องอ้างอิง parameter ชุดเดียวกันใน iteration ปัจจุบัน หากแก้ `theta0` แล้วนำค่าใหม่ไปคำนวณ gradient ของ `theta1` จะไม่ใช่ batch gradient descent ตามสมการเดียวกัน การเก็บค่าไว้ในตัวแปร `new_...` ช่วยให้เห็นว่าอัปเดตพร้อมกัน

---

## 7. ดูว่าโมเดลกำลังเรียนรู้หรือไม่

กราฟที่ตรงไปตรงมาที่สุดคือ iteration เทียบกับ cost:

```python
iterations = [record['iteration'] for record in gd_history]
costs = [record['cost'] for record in gd_history]

plt.figure(figsize=(7, 4.5))
plt.plot(iterations, costs, color='steelblue', linewidth=2)
plt.title('Gradient Descent Convergence')
plt.xlabel('Iteration')
plt.ylabel('Half MSE')
plt.grid(alpha=0.2)
plt.tight_layout()
plt.show()
```

สิ่งที่ควรเห็นคือ cost ลดลงเร็วในช่วงแรก แล้วค่อย ๆ ราบเมื่อเข้าใกล้ค่าต่ำสุด

Notebook ต้นฉบับวาด $\theta_0$ เทียบกับ cost ซึ่งดูการเคลื่อนที่ได้ แต่ต้องระวังว่า $\theta_1$ เปลี่ยนไปพร้อมกัน กราฟนั้นจึงเป็น “เส้นทางฉายบนหนึ่งมิติ” ไม่ใช่กราฟ cost ที่ขึ้นกับ $\theta_0$ เพียงตัวเดียว

### ทดลอง learning rate หลายค่า

```python
learning_rates = [0.001, 0.01, 0.05, 0.1]

plt.figure(figsize=(7, 4.5))

for rate in learning_rates:
    _, history = gradient_descent(
        x,
        y,
        learning_rate=rate,
        tolerance=1e-9,
        max_iter=5000
    )

    rate_iterations = [record['iteration'] for record in history]
    rate_costs = [record['cost'] for record in history]
    plt.plot(rate_iterations, rate_costs, label=f'eta = {rate}')

plt.title('Effect of Learning Rate')
plt.xlabel('Iteration')
plt.ylabel('Half MSE')
plt.yscale('log')
plt.legend(frameon=False)
plt.grid(alpha=0.2)
plt.tight_layout()
plt.show()
```

`plt.yscale('log')` ช่วยให้เห็น cost หลายระดับขนาดได้ง่ายขึ้น แต่ควรบอกผู้อ่านเสมอว่าแกนใช้ logarithmic scale

---

## 8. เปรียบเทียบทั้งสามวิธี

```python
comparison = np.vstack([
    theta,
    theta_sklearn,
    theta_gd
])

print(comparison)
```

| วิธี | วิธีหาคำตอบ | จุดเด่น | ข้อควรระวัง |
|---|---|---|---|
| NumPy Normal Equation | คำนวณจาก matrix โดยตรง | เห็นคณิตศาสตร์ชัด | การหา inverse โดยตรงอาจไม่เสถียร |
| scikit-learn | ใช้ estimator API | สั้น มาตรฐาน และต่อยอดง่าย | ต้องเข้าใจ shape และ workflow `fit`/`predict` |
| Gradient Descent | ปรับ parameter ซ้ำ ๆ | เห็น optimization และขยายสู่โมเดลใหญ่ได้ | ต้องเลือก learning rate และ stopping condition |

คำตอบใกล้กันไม่ได้แปลว่า implementation ทุกแบบดีเท่ากัน แต่เป็น sanity check ว่าเรากำลังแก้โจทย์เดียวกัน

## 9. ทำไมบทนี้ยังไม่แบ่ง train/test

ข้อมูลมีเพียง 3 จุดและเป้าหมายของ lab คือสาธิตการหา parameter ไม่ใช่ประเมินความสามารถในการ generalize หากแบ่ง test set ตอนนี้ training set จะเล็กเกินไปและ metric ผันผวนมาก

เมื่อใช้ข้อมูลจริงที่มีจำนวนมากขึ้น workflow ควรเป็น:

1. แบ่ง train/test ก่อน
2. fit ด้วย training data เท่านั้น
3. predict test data
4. ประเมินด้วย MAE, MSE, RMSE หรือ $R^2$

ดังนั้นอย่าใช้ความพอดีบน 3 จุดนี้เป็นหลักฐานว่าโมเดลจะทำนายข้อมูลใหม่ได้ดี

---

## 10. Error ที่พบบ่อยและวิธีแก้

| อาการ | สาเหตุที่เป็นไปได้ | วิธีตรวจหรือแก้ |
|---|---|---|
| `NameError: cost_function is not defined` | ชื่อฟังก์ชันตอนประกาศกับตอนเรียกไม่ตรงกัน | เลือกชื่อเดียวและค้นหาทุกจุดที่เรียกใช้ |
| `Expected 2D array, got 1D array` | ส่ง vector 1 มิติให้ scikit-learn เป็น `X` | ใช้ `reshape(-1, 1)` |
| `Singular matrix` | $\mathbf{X}^{T}\mathbf{X}$ หา inverse ไม่ได้ | ใช้ `np.linalg.lstsq()` หรือ pseudoinverse |
| cost เพิ่มขึ้นหรือเป็น `nan` | learning rate สูงเกินไป หรือข้อมูลมีปัญหา | ลด learning rate และตรวจ missing/infinite values |
| รัน cell เดี่ยวได้ แต่ Run all ไม่ได้ | พึ่งตัวแปรจาก session เก่า | Restart แล้ว Run all; จัดลำดับ cell ใหม่ |
| parameter กลายเป็น array รูปร่างแปลก | ผสม `(n,)` กับ `(n, 1)` จน broadcasting | พิมพ์ `.shape` ทุกจุดสำคัญและกำหนดรูปแบบให้ชัด |
| warning เรื่อง marker ซ้ำ | กำหนด marker ทั้งใน `'b.'` และ `marker='+'` | ระบุเพียงวิธีเดียว |

---

## 11. แบบฝึกหัดลงมือทำ

### แบบฝึกหัด 1: ตรวจ prediction

ใช้สมการที่ได้คำนวณ $\hat{y}$ เมื่อ $x=7$ ด้วยมือ แล้วตรวจด้วย `linear_model.predict()`

<details>
<summary>เฉลย</summary>

$$
\hat{y}=0.571+(0.857)(7)\approx6.571
$$

```python
linear_model.predict(np.array([[7.0]]))
```

</details>

### แบบฝึกหัด 2: เปลี่ยน learning rate

ทดลอง `learning_rate` เป็น `0.001`, `0.01`, `0.1` และ `1.0` แล้วบันทึก:

- จำนวน iteration
- final cost
- parameter สุดท้าย
- convergence หรือ divergence

อย่าเลือก learning rate จากความเร็วเพียงอย่างเดียว ต้องตรวจว่าคำตอบเข้าใกล้ Normal Equation ด้วย

### แบบฝึกหัด 3: สร้างกรณี singular matrix

ลองให้ $x=[2,2,2]$ แล้วรันสูตรที่ใช้ `inv()` อธิบายว่าทำไมไม่มีข้อมูลเพียงพอให้แยกผลของ intercept ออกจาก slope จากนั้นเปรียบเทียบกับ `np.linalg.lstsq()`

### แบบฝึกหัด 4: อธิบายโค้ดด้วยภาษาของตัวเอง

ตอบสั้น ๆ:

1. ทำไม scikit-learn ต้องการ `X` เป็น 2 มิติ?
2. `fit()` ต่างจาก `predict()` อย่างไร?
3. learning rate กับ tolerance ทำหน้าที่ต่างกันอย่างไร?
4. เพราะเหตุใด output เก่าจึงไม่ใช่หลักฐานว่า notebook ปัจจุบันถูกต้อง?

---

## 12. Checklist ก่อนนำแนวคิดไปใช้กับข้อมูลจริง

- [ ] กำหนด target และ feature ชัดเจน
- [ ] ตรวจ missing values, data type และหน่วยของข้อมูล
- [ ] ตรวจ `X.shape` และ `y.shape`
- [ ] แบ่ง train/test ก่อนขั้นตอนที่เรียนรู้จากข้อมูล
- [ ] fit preprocessing และ model ด้วย training data เท่านั้น
- [ ] ใช้ metric ที่เหมาะกับโจทย์
- [ ] ตรวจ residuals และ outliers
- [ ] เปรียบเทียบกับวิธีง่ายหรือ baseline ที่สมเหตุสมผล
- [ ] Restart และ Run all จากบนลงล่าง
- [ ] บันทึก `random_state`, parameter และเวอร์ชันที่จำเป็นต่อการทำซ้ำ

## 13. คำศัพท์สำคัญ

| คำศัพท์ | ความหมายแบบสั้น |
|---|---|
| Feature | ตัวแปรที่ใช้ทำนาย |
| Target | ตัวแปรที่ต้องการทำนาย |
| Parameter | ค่าที่โมเดลเรียนรู้ เช่น coefficient |
| Hyperparameter | ค่าที่ผู้พัฒนากำหนดก่อนเรียนรู้ เช่น learning rate |
| Intercept | ค่าทำนายเมื่อ feature เป็นศูนย์ |
| Coefficient | การเปลี่ยนแปลงของค่าทำนายเมื่อ feature เพิ่มหนึ่งหน่วย |
| Residual | ค่าจริงลบค่าทำนาย |
| Cost function | ตัวเลขที่สรุปความผิดพลาดเพื่อใช้ในการ optimize |
| Gradient | ทิศทางและอัตราการเปลี่ยนของ cost |
| Convergence | ภาวะที่การปรับ parameter เปลี่ยนคำตอบน้อยมากแล้ว |
| Divergence | ภาวะที่การปรับ parameter ไม่เข้าใกล้คำตอบและอาจยิ่งแย่ลง |

## สรุป

Lab นี้ไม่ได้สอนเพียงการลากเส้นตรง แต่แสดงให้เห็นโจทย์เดียวกันผ่านสามมุมมอง:

- Normal Equation ทำให้เห็นโครงสร้างทางคณิตศาสตร์
- scikit-learn แสดง workflow ที่ใช้จริงในงาน Machine Learning
- Gradient Descent ทำให้เข้าใจว่าโมเดลจำนวนมากเรียนรู้ parameter อย่างไร

คำตอบประมาณ $[0.571,0.857]$ ที่ได้ตรงกันเป็นสะพานเชื่อมระหว่างคณิตศาสตร์ โค้ด และ optimization ส่วนบทเรียนที่สำคัญไม่แพ้กันคือ notebook ต้องรันได้จาก state ว่าง ผลลัพธ์ต้องตรวจสอบซ้ำได้ และชื่อ รูปร่าง และขอบเขตของตัวแปรควรชัดเจนเสมอ

---

## แหล่งเรียนต่อ

- Notebook ต้นฉบับ: [`../lab/linear_regression.ipynb`](../lab/linear_regression.ipynb)
- บทเรียนทฤษฎีฉบับเต็ม: [`../summary/02_linear_regression.md`](../summary/02_linear_regression.md)
