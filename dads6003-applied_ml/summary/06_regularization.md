# Regularization

## ข้อมูลต้นฉบับ

- รายวิชา: DADS6003 Applied Machine Learning
- Lecture: `dads6003_06_regularization.pdf` จำนวน 27 หน้า
- Lab: `regularization.ipynb` จำนวน 15 cells
- หัวข้อ: underfitting, overfitting, Ridge, Lasso, Elastic Net, coefficient paths และ stochastic gradient descent

> **จากเอกสาร:** บทเรียนเริ่มจากปัญหาโมเดลซับซ้อนจนจำ training data แล้วเสนอ regularization เพื่อควบคุมขนาด coefficients ก่อนเปรียบเทียบ L2, L1 และ Elastic Net
>
> **คำอธิบายเพิ่มเติม:** บทนี้เติมที่มาของ objective function เหตุผลที่ต้อง scale features วิธีเลือก penalty และการประเมิน train/test พร้อมตรวจข้อจำกัดของ lab เดิม

## ภาพรวมและ Learning Objectives

Regularization คือการเพิ่มข้อจำกัดให้โมเดลไม่เลือก coefficients ที่รุนแรงเกินจำเป็น โมเดลอาจ fit training data แย่ลงเล็กน้อย แต่มีโอกาสทำนายข้อมูลใหม่ได้ดีและเสถียรกว่า เป้าหมายจึงไม่ใช่ training error ต่ำที่สุด แต่คือ **generalization**

เมื่อจบบทนี้ ผู้อ่านควรสามารถ:

1. แยก underfitting, good fit และ overfitting จากผล train/test ได้
2. อธิบายว่า regularization เปลี่ยน objective function อย่างไร
3. คำนวณ L1 และ L2 penalty ได้
4. เปรียบเทียบ Ridge, Lasso และ Elastic Net ได้
5. อธิบาย `alpha` และ `l1_ratio` โดยไม่สับสนกับสัญลักษณ์ในสไลด์
6. สร้าง Pipeline สำหรับ polynomial features, scaling และ regularized regression ได้
7. ตีความ coefficient path และผลจาก lab โดยไม่สรุปเกินหลักฐาน

## 1. ปัญหาก่อนมี Regularization

### 1.1 Model fit และ generalization

โมเดล regression รับ features \(X\) แล้วสร้างค่าทำนาย \(\hat{y}\) จาก coefficients เช่น polynomial degree 4:

$$
\hat{y} = \beta_0+\beta_1x+\beta_2x^2+\beta_3x^3+\beta_4x^4
$$

การ fit คือการหาค่า \(\beta\) ที่ลด loss ใน training data สำหรับ Mean Squared Error:

$$
MSE = \frac{1}{N} \sum_{i=1}^{N} (y_i-\hat{y}_i)^2
$$

แต่โมเดลที่ fit training data ดีไม่ได้แปลว่าจะทำนายข้อมูลใหม่ดี ความสามารถกับข้อมูลใหม่เรียกว่า generalization

### 1.2 Underfitting, good fit และ overfitting

| สภาวะ | สิ่งที่เกิดขึ้น | Train error | Test error |
|---|---|---:|---:|
| Underfitting | โมเดลง่ายเกิน จับ signal หลักไม่ได้ | สูง | สูง |
| Good fit | จับ signal โดยไม่ตาม noise มากไป | ต่ำพอเหมาะ | ต่ำ |
| Overfitting | โมเดลตามรายละเอียดเฉพาะชุดฝึก | ต่ำมาก | สูงกว่าชุดฝึก |

จากภาพในสไลด์ เส้นตรงอาจ underfit ความสัมพันธ์โค้ง ขณะที่ polynomial degree สูงวกผ่านจุดฝึกแทบทุกจุด แต่แกว่งรุนแรงระหว่างจุด สัญญาณของ overfitting จึงไม่ใช่ training error ต่ำเพียงอย่างเดียว แต่คือช่องว่าง train-test ที่กว้าง หรือ training error ลดต่อขณะที่ validation error กลับเพิ่ม

สาเหตุที่พบบ่อย ได้แก่ features มากเมื่อเทียบกับจำนวนแถว, polynomial degree สูง, noise, correlated features, ประเมินบนข้อมูลฝึก และเลือก hyperparameters หลังดู test setซ้ำ ๆ

การลด features เป็นทางหนึ่ง แต่เสี่ยงทิ้งข้อมูลที่ยังมีประโยชน์ Regularization เสนอทางกลาง: เก็บ features ไว้ แต่คิดต้นทุนเพิ่มเมื่อใช้ coefficients ขนาดใหญ่

## 2. Regularization แบบเห็นภาพก่อน

สมมติ degree 4 ใช้ \(\beta_3\) และ \(\beta_4\) ขนาดใหญ่มากเพื่อบิดเส้นให้ผ่านจุดฝึกทุกจุด หากบอกโมเดลว่า “coefficient ที่ใหญ่มีค่าใช้จ่าย” โมเดลต้องสมดุลสองเรื่อง:

1. ลด prediction error บน training data
2. รักษา coefficients ไม่ให้รุนแรงเกินไป

เมื่อ penalty แรงขึ้น coefficients ถูกดึงเข้าหาศูนย์ เส้นจึงเรียบและไวต่อการเปลี่ยน sample น้อยลง กระบวนการนี้เรียกว่า **shrinkage**

Regularization ไม่ใช่การรับประกันว่า test performance จะดีขึ้น ไม่แทน train-test split และไม่แก้ data leakage หาก model family ผิด เช่นใช้เส้นตรงกับความสัมพันธ์แบบ threshold การหด coefficients ก็ไม่สร้างรูปแบบที่ขาดไป

## 3. Penalized Objective Function

Linear regression ปกติลด prediction loss:

$$
J(\beta) = \frac{1}{N} \sum_{i=1}^{N} (y_i-\hat{y}_i)^2
$$

Regularized regression เพิ่ม penalty:

$$
J_{reg}(\beta) = \frac{1}{N} \sum_{i=1}^{N} (y_i-\hat{y}_i)^2 + \lambda P(\beta)
$$

โดย \(P(\beta)\) คือรูปแบบ penalty และ \(\lambda \geq 0\) ควบคุมความแรง เมื่อ \(\lambda=0\) จะกลับเป็น regression ที่ไม่มี penalty เมื่อ \(\lambda\) สูงขึ้น โมเดลยอมเสีย training fit มากขึ้นเพื่อให้ coefficients เล็กลง โดยทั่วไป intercept \(\beta_0\) ไม่ถูก penalize

### 3.1 ทำไมต้อง scale features

ถ้า `Age` มี coefficient 0.5 แต่ `Annual Income` มี coefficient 0.00002 ความต่างอาจมาจากหน่วย ไม่ได้แปลว่า Age สำคัญกว่า เมื่อ penalty ลงที่ coefficient โดยตรง feature สเกลใหญ่ใช้ coefficient เล็กและถูกลงโทษน้อยกว่าอย่างไม่ยุติธรรม

จึงควร scale numerical features ก่อน Ridge, Lasso และ Elastic Net โดย fit scaler เฉพาะ training data Polynomial features ยิ่งจำเป็น: ใน lab \(x\) อยู่ 10-30 แต่ \(x^4\) อยู่ 10,000-810,000

## 4. Ridge Regression: L2

Ridge ใช้ผลรวมกำลังสองของ coefficients:

$$
\lVert\beta\rVert_2^2 = \sum_{j=1}^{d}\beta_j^2
$$

$$
J_{Ridge}(\beta) = \frac{1}{N} \sum_{i=1}^{N} (y_i-\hat{y}_i)^2 + \lambda\sum_{j=1}^{d}\beta_j^2
$$

coefficients \([2,1]\) มี L2 penalty \(2^2+1^2=5\) ส่วน \([1.5,1.5]\) มีค่า 4.5 เมื่อสอง features ให้ข้อมูลคล้ายกัน Ridge จึงมักกระจายน้ำหนักแทนเลือกตัวเดียว เพราะการแบ่ง coefficient ใหญ่เป็นสองค่าเล็กลดผลรวมกำลังสอง

เมื่อ \(\lambda\) เพิ่ม coefficients หดเข้าหาศูนย์อย่างต่อเนื่อง แต่โดยทั่วไปไม่เป็นศูนย์พอดี Ridge เหมาะเมื่อหลาย features มีสัญญาณเล็กน้อย, features สัมพันธ์กันสูง หรือต้องการ prediction ที่เสถียรกว่าการเลือกตัวแปรเด็ดขาด

### 4.1 อ่าน coefficient path

Coefficient path แสดง coefficient แต่ละตัวเมื่อเปลี่ยน regularization strength:

- penalty อ่อน: coefficients คล้ายโมเดลเดิม
- penalty สูง: ทุกเส้นหดเข้าศูนย์
- เส้นที่เปลี่ยนแรง: coefficient ไวต่อ regularization และอาจไม่เสถียร

กราฟใน notebook กลับแกน x ด้วย `ax.set_xlim(ax.get_xlim()[::-1])` จึงต้องอ่านค่าบนแกน ไม่ควรเดาทิศจากซ้าย-ขวา

## 5. Lasso Regression: L1

Lasso ย่อมาจาก **Least Absolute Shrinkage and Selection Operator** และใช้ผลรวมค่าสัมบูรณ์:

$$
\lVert\beta\rVert_1 = \sum_{j=1}^{d}|\beta_j|
$$

$$
J_{Lasso}(\beta) = \frac{1}{N} \sum_{i=1}^{N} (y_i-\hat{y}_i)^2 + \lambda\sum_{j=1}^{d}|\beta_j|
$$

L1 constraint มีมุมบนแกน coefficients จุดเหมาะที่สุดจึงมีโอกาสอยู่ที่มุมและทำให้บาง coefficient เป็นศูนย์พอดี โมเดลที่มี coefficients ศูนย์จำนวนมากเรียกว่า **sparse model** Lasso จึงทำ shrinkage และ embedded feature selection พร้อมกัน

Lasso เหมาะเมื่อคาดว่ามี useful features เพียงส่วนน้อยและต้องการโมเดลกระชับ แต่ถ้า features สัมพันธ์กันสูง Lasso อาจเลือกตัวหนึ่งแล้วตัดอีกตัวแบบไม่เสถียร เมื่อ sample เปลี่ยนเล็กน้อยตัวที่ถูกเลือกอาจสลับกัน การเป็นศูนย์จึงไม่พิสูจน์ว่า feature ไม่มีประโยชน์หรือไม่มีผลเชิงเหตุผล

`Lasso(alpha=0)` ไม่ควรใช้แทน ordinary least squares เพราะ solver ถูกออกแบบสำหรับ L1 penalty ให้ใช้ `LinearRegression` เมื่อไม่ต้องการ penalty ตาม [Lasso API](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html)

## 6. Elastic Net: รวม L1 และ L2

Elastic Net ใช้ทั้ง L1 และ L2:

$$
J_{EN}(\beta) = Loss(\beta) + \lambda [ r\lVert\beta\rVert_1 + (1-r)\lVert\beta\rVert_2^2 ]
$$

เมื่อ \(r=1\) เหลือ L1 แบบ Lasso เมื่อ \(r=0\) เหลือ L2 แบบ Ridge จึงได้ทั้ง sparsity และความเสถียรกับ correlated features

### 6.1 สไลด์กับ scikit-learn ใช้ทิศทางตรงข้าม

| แหล่ง | ตัวแปรผสม | ค่า 0 | ค่า 1 |
|---|---|---|---|
| Lecture slide | \(\alpha\) เป็นน้ำหนัก L2 | Lasso | Ridge |
| scikit-learn | `l1_ratio` เป็นน้ำหนัก L1 | L2 | Lasso |

ใน scikit-learn `alpha` ควบคุมความแรงรวม ส่วน `l1_ratio` ควบคุมสัดส่วน L1 ตาม [ElasticNet API](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.ElasticNet.html) ดังนั้นอย่านำ \(\alpha\) ในสไลด์ไปเทียบกับ `alpha` ใน API โดยตรง

Elastic Net เหมาะเมื่อ useful features อยู่เป็นกลุ่มที่สัมพันธ์กันและยังต้องการตัดบาง features เช่นยอดขายย้อนหลังหลายเดือน Ridge อาจเก็บทั้งกลุ่ม ส่วน Lasso อาจเลือกเดือนเดียวอย่างไม่เสถียร Elastic Net เป็นทางกลาง

## 7. เลือก Regularization แบบใด

| สถานการณ์ | วิธีเริ่มต้น | เหตุผล |
|---|---|---|
| Features ส่วนใหญ่มีสัญญาณ | Ridge | หดทุก coefficient แต่ไม่รีบตัด |
| เชื่อว่ามี useful features น้อย | Lasso | ทำบาง coefficients เป็นศูนย์ |
| Useful features เป็นกลุ่ม correlated | Elastic Net | ผสม stability กับ sparsity |
| ไม่ต้องการ penalty | LinearRegression | ตรงกว่าการใช้ Lasso alpha 0 |
| Features ต่างหน่วย | Scale ก่อน | ทำให้ penalty ยุติธรรม |
| ต้องเลือก penalty strength | Validation หรือ CV | Training error ไม่วัด generalization |

Ridge เป็นจุดเริ่มต้นที่ปลอดภัยเมื่อยังไม่รู้โครงสร้างจริง แล้วเปรียบเทียบ Lasso และ Elastic Net ด้วยข้อมูลแบ่งและ metrics เดียวกัน ไม่มีวิธีใดดีที่สุดสำหรับทุก dataset

## 8. Optimization และ SGD

สไลด์แสดง Stochastic Gradient Descent ซึ่งสุ่มหนึ่ง observation แล้วขยับ coefficient ทวนทิศ gradient สำหรับ Ridge:

$$
\beta_j^{(t+1)} = \beta_j^{(t)} - \eta [ \nabla_j Loss + 2\lambda\beta_j^{(t)} ]
$$

\(\eta\) คือ learning rate ถ้าสูงเกินอาจแกว่ง ถ้าต่ำเกิน convergence ช้า

L1 ไม่ differentiable ที่ศูนย์ จึงใช้ subgradient:

$$
sign(\beta_j) = \begin{cases} -1, & \beta_j<0 \\ s, & \beta_j=0,\quad s\in[-1,1] \\ 1, & \beta_j>0 \end{cases}
$$

ที่ศูนย์มี subgradient ได้หลายค่า ไม่ได้แปลว่า optimize ไม่ได้ แต่ต้องใช้ solver ที่รองรับ nonsmooth objective เช่น coordinate descent

## 9. Lab Walkthrough

### 9.1 Linear regression

> **จาก `regularization.ipynb`:** Lab ใช้ข้อมูล 5 จุด:

```python
X = np.array([[10, 15, 20, 25, 30]]).T
y = np.array([[10, 30, 50, 51, 52]]).T
```

`.T` เปลี่ยนหนึ่งแถวห้าค่าเป็นห้า observations หนึ่ง feature ผลโมเดลเส้นตรง:

| Metric | ค่า |
|---|---:|
| Coefficient | 2.1 |
| Intercept | -3.4 |
| Training \(R^2\) | 0.8135 |
| Training MSE | 50.54 |

เส้นตรงจับแนวโน้มเพิ่ม แต่ไม่จับการเพิ่มเร็วช่วงต้นและเริ่มราบช่วงท้าย

### 9.2 Polynomial degree 2 และ 4

`PolynomialFeatures(degree=2)` เปลี่ยน \(x\) เป็น \([1,x,x^2]\):

```text
x = 10  ->  [1, 10, 100]
x = 15  ->  [1, 15, 225]
```

| Model | Training \(R^2\) | Training MSE |
|---|---:|---:|
| Linear | 0.8135 | 50.5400 |
| Polynomial degree 2 | 0.9848 | 4.1257 |
| Polynomial degree 4 | 1.0000 | ใกล้ 0 |

Degree 4 มี parameters เพียงพอผ่านข้อมูลทั้ง 5 จุดพอดี นี่คือ interpolation ไม่ใช่หลักฐานว่า generalize ดี เพราะยังไม่มี test observations

กราฟ degree 4 เดิมทำนายเฉพาะ x ห้าจุดแล้วเชื่อมด้วยเส้นตรง จึงยังไม่เห็นความโค้งจริง แบบฝึกหัดใน notebook แก้ได้ดังนี้:

```python
x_curve = np.linspace(X.min(), X.max(), 200).reshape(-1, 1)
x_curve_poly = poly_reg.transform(x_curve)
y_curve = lin_reg4.predict(x_curve_poly)

plt.scatter(X, y, label='Observations')
plt.plot(x_curve, y_curve, color='green', label='Degree 4')
plt.legend()
plt.show()
```

### 9.3 Ridge

`Ridge(alpha=100)` กับ degree 4 ได้ Training \(R^2=0.9827\), MSE 4.6936 และ intercept -15.4716 Training MSE สูงกว่า degree 4 ที่ไม่ regularize เพราะโมเดลยอม fit จุดฝึกไม่สมบูรณ์เพื่อหด coefficients จะเรียกว่า “ดีขึ้น” ได้ต่อเมื่อ test error ลด

เมื่อเพิ่ม alpha 0-1,000 training MSE เพิ่มจากใกล้ 0 เป็น 12.6279 นี่เป็นพฤติกรรมปกติของ penalty ไม่ได้พิสูจน์ว่า alpha 0 ดีที่สุด เพราะประเมินบน training data

### 9.4 Lasso

Lab เพิ่ม alpha 0-2,000 ที่ alpha 200 coefficients ของ degree 1 และ 2 เป็นศูนย์ แต่ degree 3 และ 4 ยังเหลือ และ MSE เท่ากับ 16.7088 นี่แสดง sparsity แต่ powers ต่างสเกลกันมาก จึงไม่ควรเปรียบ coefficient sizes ก่อน scaling

ที่ alpha 0 Lasso ได้ \(R^2=0.9847\) แทน 1.0 เพราะใช้ Lasso solver ในกรณีไม่แนะนำและ notebook ปิด warnings ด้วย `warnings.filterwarnings('ignore')` ควรเปิด warnings เพื่อเห็นปัญหา convergence หรือ parameter

### 9.5 Elastic Net

Notebook ใช้ `ElasticNet(l1_ratio=a)` จึงเปลี่ยนเฉพาะสัดส่วน L1/L2 แต่ปล่อย alpha ที่ default 1.0 การทดลองนี้ไม่ใช่การเปลี่ยน penalty strength ที่ `l1_ratio=0` ควรใช้ Ridge และที่ `l1_ratio=1` เทียบกับ Lasso ภายใต้ convention ของ scikit-learn

Cell สุดท้ายตั้งชื่อกราฟเป็น “Lasso coefficients” ทั้งที่ model เป็น Elastic Net จึงควรแก้ label ก่อนสื่อสารผล

### 9.6 Execution state

ทุก code cell มี `execution_count=None` แต่มี saved outputs อยู่ จึงไม่มีลำดับ execution ยืนยันได้ ผลข้างต้นอ้างอิง output ที่ฝังใน notebook ควร Run All ใหม่เพื่อพิสูจน์ว่า code ปัจจุบันรันตั้งแต่ต้นจนจบ

## 10. Guided Lab ที่วัด Generalization

Lab เดิมเหมาะกับการเห็น penalty แต่มีเพียง 5 จุดและไม่มี test set เวอร์ชันนี้สร้างข้อมูลเพิ่ม แบ่ง train/test และใช้ Pipeline:

```python
import numpy as np
import pandas as pd

from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import PolynomialFeatures, StandardScaler

rng = np.random.default_rng(42)

X = np.linspace(0, 10, 80).reshape(-1, 1)
y = 3 + 2 * X.ravel() - 0.25 * X.ravel() ** 2
y = y + rng.normal(0, 3, size=len(X))

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42
)
```

Pipeline เรียง `PolynomialFeatures -> StandardScaler -> Model` เพื่อให้ scaler เรียนจาก polynomial terms ของ training data:

```python
pipelines = {
    'Linear': Pipeline([
        ('model', LinearRegression())
    ]),
    'Polynomial': Pipeline([
        ('poly', PolynomialFeatures(degree=8, include_bias=False)),
        ('scale', StandardScaler()),
        ('model', LinearRegression())
    ]),
    'Ridge': Pipeline([
        ('poly', PolynomialFeatures(degree=8, include_bias=False)),
        ('scale', StandardScaler()),
        ('model', Ridge(alpha=1.0))
    ]),
    'Lasso': Pipeline([
        ('poly', PolynomialFeatures(degree=8, include_bias=False)),
        ('scale', StandardScaler()),
        ('model', Lasso(alpha=0.05, max_iter=20_000))
    ])
}

results = []

for name, model in pipelines.items():
    model.fit(X_train, y_train)

    train_pred = model.predict(X_train)
    test_pred = model.predict(X_test)

    results.append({
        'Model': name,
        'Train RMSE': mean_squared_error(
            y_train,
            train_pred
        ) ** 0.5,
        'Test RMSE': mean_squared_error(
            y_test,
            test_pred
        ) ** 0.5
    })

results = pd.DataFrame(results)
results['Gap'] = results['Test RMSE'] - results['Train RMSE']
results.round(3)
```

การแปลผล:

- Train/test RMSE สูงทั้งคู่: อาจ underfit
- Train ต่ำมาก แต่ test สูง: มีสัญญาณ overfit
- Regularized model มี train สูงขึ้นเล็กน้อย แต่ test ลด: penalty ช่วย generalization
- Penalty แรงจนทั้งสองสูง: regularization มากเกิน

### 10.1 เลือก alpha

ห้ามเลือก alpha จาก test set เพราะ test ต้องเก็บไว้ประเมินสุดท้าย วิธีพื้นฐานคือ validation set ส่วน cross-validation เสถียรกว่าเมื่อข้อมูลน้อย ตัวอย่าง RidgeCV:

```python
from sklearn.linear_model import RidgeCV

ridge_cv = Pipeline([
    ('poly', PolynomialFeatures(degree=8, include_bias=False)),
    ('scale', StandardScaler()),
    ('model', RidgeCV(alphas=np.logspace(-4, 4, 50)))
])

ridge_cv.fit(X_train, y_train)
selected_alpha = ridge_cv.named_steps['model'].alpha_

print(f'Selected alpha: {selected_alpha:.4f}')
```

ใช้ log scale เพราะค่าที่เหมาะอาจต่างกันหลายหลัก เช่น 0.001, 0.1, 10 หรือ 1,000

## 11. Validation และ Troubleshooting

### 11.1 Checklist

- split ก่อน fit scaler และ feature transformer
- ใช้ split และ metric เดียวกันทุกโมเดล
- รายงานทั้ง train และ test
- scale ก่อนลง penalty
- เลือก alpha จาก validation/CV ไม่ใช่ test
- ตรวจ convergence warnings
- ตรวจ non-zero coefficients ของ Lasso/Elastic Net
- วาด prediction บน sorted grid
- Run All และตรวจ execution order

### 11.2 Troubleshooting

| อาการ | สาเหตุ | แนวทางแก้ |
|---|---|---|
| Lasso ไม่ converge | alpha ต่ำ, ไม่ scale, iterations น้อย | scale, เพิ่ม `max_iter`, อ่าน warning |
| Coefficients ต่างมหาศาล | features ต่างหน่วย | ใช้ StandardScaler ใน Pipeline |
| Training MSE เพิ่มตาม alpha | เป็นผลปกติของ penalty | ดู validation/test |
| ทุก coefficient เกือบศูนย์ | alpha สูงเกิน | ลด alpha |
| Lasso เลือก feature ไม่คงที่ | correlated features | ทดลอง Elastic Net |
| Test score ดีผิดปกติ | leakage หรือใช้ test เลือก alpha | ตรวจ dependency |
| เส้นกราฟหัก | ทำนายเฉพาะ training x | สร้าง dense sorted grid |
| Lasso alpha 0 แปลก | solver ไม่เหมาะ | ใช้ LinearRegression |

## 12. Critical Discussion

Regularization แลก bias กับ variance: penalty ลดความยืดหยุ่นจึงเพิ่ม bias ได้ แต่ลด variance เพราะ coefficients ไวต่อ sample น้อยลง เป้าหมายคือสมดุลที่ลด error บนข้อมูลใหม่

Lasso ที่ให้ coefficient ศูนย์ตอบเพียงว่า feature ไม่ถูกใช้ในโมเดล prediction ภายใต้ dataset, scaling, penalty และ features อื่น ไม่พิสูจน์ว่า feature ไม่มีผลเชิงเหตุผล

ถ้า model family ผิด, data leakage หรือ dataset shift เป็นปัญหา regularization ไม่แก้ต้นเหตุ ต้องปรับการออกแบบข้อมูลหรือโมเดล

## 13. Common Misconceptions

1. **Training MSE ต่ำสุดคือโมเดลดีที่สุด** - ต้องดูข้อมูลที่ไม่ใช้ฝึก
2. **Ridge ลบ features** - โดยทั่วไปหดแต่ไม่เป็นศูนย์
3. **Lasso เลือกสาเหตุ** - เป็น feature selection เพื่อ prediction
4. **alpha ทุกแหล่งมีความหมายเดียวกัน** - ต้องดู objective และ API
5. **Regularization ไม่ต้อง scale** - รันได้แต่ penalty อาจไม่ยุติธรรม
6. **Elastic Net l1_ratio 0 คือ Lasso** - ใน scikit-learn ค่า 0 คือ L2
7. **ปิด warnings ได้เพราะ code รัน** - warning อาจบอกว่ายังไม่ converge

## 14. Likely Exam Focus

> อนุมานจากหัวข้อ สมการ กราฟ และ code ที่เน้น ไม่ใช่ข้อมูลข้อสอบจริง

- แยก underfitting และ overfitting จาก train/test error
- เขียน objective ของ Ridge, Lasso และ Elastic Net
- คำนวณ L1/L2 penalty
- อธิบายว่าเหตุใด Ridge กระจายน้ำหนัก แต่ Lasso สร้าง sparsity
- อธิบาย alpha, scaling และ validation
- อ่าน coefficient path
- ตรวจ code ที่ประเมิน training data หรือปิด warnings
- เปรียบเทียบสัญลักษณ์ Elastic Net ในสไลด์กับ `l1_ratio`

## 15. Progressive Practice พร้อมเฉลย

### ข้อ 1: คำนวณ

coefficients \([3,-2,0]\) มี L1 และ squared L2 เท่าใด

**เฉลย:**

$$
L1=|3|+|-2|+|0|=5
$$

$$
L2^2=3^2+(-2)^2+0^2=13
$$

### ข้อ 2: วิเคราะห์

โมเดล A มี Train RMSE 1.0, Test RMSE 5.0 ส่วน B มี 2.2 และ 2.5 ควรเลือกอะไร

**เฉลย:** เลือก B หาก test แยกถูกต้อง เพราะ generalize ดีกว่า ช่องว่างของ A บ่งชี้ overfitting

### ข้อ 3: เลือกโมเดล

มี 200 features เป็นกลุ่ม correlated และคาดว่ามีเพียงบางกลุ่มมีประโยชน์

**เฉลย:** เริ่ม Elastic Net เพื่อได้ sparsity และ group stability แล้วเลือก alpha/l1_ratio ด้วย validation หรือ CV

### ข้อ 4: Debug

```python
for alpha in alphas:
    model.fit(X, y)
    mse = mean_squared_error(y, model.predict(X))
```

**เฉลย:** fit และ evaluate ชุดเดียวกัน จึงให้รางวัลโมเดลที่จำ training data ต้องใช้ validation/CV

### ข้อ 5: Parameter

`l1_ratio=0.8` ใน scikit-learn หมายถึงอะไร

**เฉลย:** ให้น้ำหนัก L1 มากกว่า L2 จึงใกล้ Lasso แต่ความแรงรวมยังขึ้นกับ alpha

### ข้อ 6: Leakage

ถ้า scale ก่อน split จะเกิดอะไร

**เฉลย:** statistics จาก test รั่วเข้า training ต้อง split ก่อนหรือใช้ Pipeline

## 16. Mini-project

สร้าง nonlinear dataset ที่มี noise แล้ว:

1. แบ่ง train/test
2. เปรียบเทียบ degree 1, 2, 5, 10 และ 15
3. เปรียบเทียบ unregularized, Ridge, Lasso และ Elastic Net
4. ใช้ Pipeline กับ StandardScaler
5. เลือก hyperparameters โดยไม่ใช้ test
6. รายงาน train/test RMSE, gap และ non-zero coefficients
7. วาด prediction curves และ coefficient paths
8. เลือกโมเดลพร้อมข้อจำกัด

| เกณฑ์ | หลักฐาน |
|---|---|
| Correctness | ไม่มี preprocessing leakage |
| Reproducibility | มี random state และ parameters |
| Interpretation | แยก training fit กับ generalization |
| Comparison | ใช้ข้อมูลและ metric เดียวกัน |
| Diagnostics | ตรวจ warning และ sparsity |
| Communication | อธิบาย trade-off ไม่สรุปจาก score เดียว |

## 17. Mastery Checklist

- [ ] แยก underfitting/overfitting จาก train-test behavior ได้
- [ ] เขียน penalized objective ได้
- [ ] คำนวณ L1/L2 ได้
- [ ] เปรียบเทียบ Ridge, Lasso, Elastic Net ได้
- [ ] แยก alpha ใน lecture จาก alpha/l1_ratio ใน scikit-learn ได้
- [ ] สร้าง Pipeline ที่ scale ถูกลำดับได้
- [ ] เลือก alpha โดยไม่ใช้ test ได้
- [ ] แปลผล lab โดยไม่สรุปเกิน training-only evidence ได้
- [ ] ตรวจ warning, leakage และกราฟผิดวิธีได้

## 18. Key Takeaways

Regularization เพิ่มต้นทุนให้ coefficients ใหญ่เพื่อแลก training fit บางส่วนกับ generalization Ridge ใช้ L2 จึงหดทุก coefficient และเหมาะกับ correlated features ส่วน Lasso ใช้ L1 จึงสร้าง sparse model Elastic Net ผสมสองแบบ

ผลน่าเชื่อถือเมื่อ scale features, fit preprocessing เฉพาะ training data, เลือก hyperparameters จาก validation/CV และเก็บ test ไว้ประเมินสุดท้าย Training error ที่เพิ่มไม่ใช่ความล้มเหลว หาก test error ลดลง

## 19. Glossary

| คำ | ความหมาย |
|---|---|
| Generalization | ความสามารถกับข้อมูลใหม่ |
| Underfitting | โมเดลง่ายเกิน |
| Overfitting | จำรายละเอียดชุดฝึกมากเกิน |
| Regularization | เพิ่มข้อจำกัดให้ parameters |
| Penalty | ต้นทุนจากขนาด coefficients |
| Shrinkage | หด coefficients เข้าศูนย์ |
| L1 norm | ผลรวมค่าสัมบูรณ์ |
| L2 norm | รากผลรวมกำลังสอง |
| Ridge | Regression ใช้ squared L2 |
| Lasso | Regression ใช้ L1 |
| Elastic Net | รวม L1 และ L2 |
| Sparsity | coefficients จำนวนมากเป็นศูนย์ |
| Hyperparameter | ค่ากำหนดก่อน fit เช่น alpha |
| Coefficient path | coefficients เมื่อเปลี่ยน penalty |
| Subgradient | ตัวแทน gradient ที่จุดไม่ differentiable |

## 20. Source Coverage Audit

| เนื้อหาในแหล่งเรียน | ส่วน | สถานะ |
|---|---|---|
| Underfit, good fit, overfit | 1 | ครบและเชื่อม train/test |
| Overfit characteristics และ solutions | 1-2 | ครบ |
| Regularization intuition | 2-3 | ครบและขยาย objective |
| Ridge และ L2 | 4 | ครบ |
| Lasso, L1 และ feature selection | 5 | ครบ |
| Ridge/Lasso use cases และ geometry | 4-7 | ครบ |
| Elastic Net | 6 | ครบ พร้อมชี้ convention ต่างจาก API |
| SGD และ subgradient | 8 | ครบ |
| Linear/polynomial lab | 9.1-9.2 | ครบพร้อม output |
| Ridge/Lasso/Elastic Net lab | 9.3-9.5 | ครบพร้อมแปลผล |
| Coefficient paths | 4.1 และ 9 | ครบ |
| Exercise nonlinear curve | 9.2 | มี solution |
| Execution state และ warnings | 9.6 และ 11 | ตรวจพบและอธิบาย |

## References

1. Ekarat Rattagan. *Week 6: Regularization*. DADS6003 Applied Machine Learning, 28 July 2025.
2. Course lab. [Regularization Notebook](https://github.com/mdanmek/nida-dads-notes/blob/main/dads6003-applied_ml/lab/regularization.ipynb).
3. Scikit-learn developers. [Linear Models User Guide](https://scikit-learn.org/stable/modules/linear_model.html).
4. Scikit-learn developers. [Ridge API](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Ridge.html).
5. Scikit-learn developers. [Lasso API](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.Lasso.html).
6. Scikit-learn developers. [ElasticNet API](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.ElasticNet.html).
7. Zou, H. and Hastie, T. [Regularization and Variable Selection via the Elastic Net](https://doi.org/10.1111/j.1467-9868.2005.00503.x). *Journal of the Royal Statistical Society: Series B*, 67(2), 301-320, 2005.
