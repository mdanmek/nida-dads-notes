# 09 K-Nearest Neighbors และ Decision Trees

บทนี้อธิบายอัลกอริทึม Supervised Learning สองกลุ่มที่มองการทำนายต่างกันอย่างชัดเจน ได้แก่ **K-Nearest Neighbors (k-NN)** ซึ่งตัดสินจากตัวอย่างที่อยู่ใกล้ข้อมูลใหม่ และ **Decision Tree** ซึ่งเรียนรู้กฎคำถามแบบ `if-then` เพื่อแบ่งข้อมูลออกเป็นกลุ่ม ทั้งสองวิธีใช้ได้กับ Classification และ Regression แต่มีสมมติฐาน จุดแข็ง และปัญหาในการใช้งานต่างกัน

เนื้อหาหลักยึดตามเอกสาร Week 9 เรื่อง k-NN และ Decision Trees พร้อมเติมคำอธิบาย ขั้นคำนวณ และแนวทางใช้ scikit-learn เพื่อให้สามารถอ่านและนำไปทดลองได้โดยไม่ต้องอาศัยคำบรรยายในชั้นเรียน

---

## 1. จาก Supervised Learning มาสู่ k-NN และ Decision Tree

ใน Supervised Learning เรามีข้อมูลตัวอย่างที่ประกอบด้วย feature $X$ และคำตอบ $y$ โมเดลใช้คู่ข้อมูลเหล่านี้เรียนรู้ความสัมพันธ์ แล้วนำความสัมพันธ์ไปทำนายคำตอบของข้อมูลใหม่

- **Regression** ใช้เมื่อ target เป็นค่าต่อเนื่อง เช่น ราคา ระยะเวลา หรืออุณหภูมิ
- **Classification** ใช้เมื่อ target เป็นกลุ่ม เช่น ผ่าน/ไม่ผ่าน หรือโรคชนิด A/B/C

Linear Regression และ Logistic Regression สร้างสมการที่มี parameter ซึ่งเรียนรู้ระหว่าง `fit()` แต่ k-NN ไม่ได้สร้างสมการลักษณะนั้น ส่วน Decision Tree สร้างชุดกฎที่แตกแขนงเป็นโครงสร้างต้นไม้ ความแตกต่างนี้ทำให้เกิดคำถามสำคัญว่า ถ้าไม่มีสมการเส้นตรงหรือ sigmoid แล้วโมเดลทั้งสองทำนายอย่างไร

บทนี้จะใช้คำว่า:

- **Model parameter** หมายถึงค่าที่เรียนรู้จากข้อมูล เช่น feature และ threshold ใน Decision Tree
- **Hyperparameter** หมายถึงค่าที่ผู้พัฒนากำหนดก่อนฝึก เช่น `n_neighbors` หรือ `max_depth`

---

# Part I: K-Nearest Neighbors

## 2. k-NN คืออะไร

### 2.1 แนวคิดแบบไม่ใช้ศัพท์เทคนิคก่อน

สมมติว่าต้องทำนายว่าร้านอาหารใหม่จะได้รับทิปหรือไม่ เราอาจค้นหาร้านในอดีตที่มีลักษณะใกล้เคียงที่สุดหลายร้าน แล้วดูว่าร้านส่วนใหญ่ในกลุ่มนั้นได้รับทิปหรือไม่ วิธีคิดนี้คือแก่นของ k-NN:

> ข้อมูลที่มีลักษณะคล้ายกันน่าจะมีผลลัพธ์คล้ายกัน

ตัวอักษร $k$ หมายถึงจำนวนเพื่อนบ้านที่นำมาใช้ตัดสิน ถ้า $k=3$ โมเดลจะหาข้อมูลฝึกที่ใกล้ข้อมูลใหม่ที่สุด 3 จุด

- Classification ใช้เสียงข้างมากของเพื่อนบ้าน
- Regression ใช้ค่าเฉลี่ยของ target จากเพื่อนบ้าน

### 2.2 นิยามอย่างเป็นทางการ

k-NN เป็นอัลกอริทึม Supervised Learning แบบ **instance-based** หรือ **lazy learning** เพราะขั้น `fit()` ส่วนใหญ่เป็นการเก็บข้อมูลฝึกไว้ ยังไม่สร้างสมการสรุปความสัมพันธ์ การคำนวณหนักจึงเกิดตอน `predict()` ซึ่งต้องเปรียบเทียบข้อมูลใหม่กับข้อมูลฝึก

k-NN ยังเป็น **non-parametric model** หมายถึงไม่ได้สมมติรูปแบบสมการตายตัว เช่น เส้นตรงหรือพหุนาม คำว่า non-parametric ไม่ได้แปลว่าไม่มี hyperparameter เพราะยังต้องเลือก $k$, distance metric และวิธีให้น้ำหนักเพื่อนบ้าน

## 3. k-NN ทำงานอย่างไร

สำหรับข้อมูลใหม่หนึ่งจุด ขั้นตอนคือ:

1. คำนวณระยะห่างจากข้อมูลใหม่ไปยังข้อมูลฝึกทุกจุด
2. เรียงระยะจากน้อยไปมาก
3. เลือกเพื่อนบ้านที่ใกล้ที่สุด $k$ จุด
4. รวมคำตอบของเพื่อนบ้านเพื่อสร้าง prediction

กระบวนการนี้ไม่มี cost function ที่ใช้ optimize parameter แบบ Linear หรือ Logistic Regression แต่ยังต้องมี **evaluation metric** เพื่อวัดคุณภาพ prediction เช่น accuracy, confusion matrix หรือ F1-score สำหรับ Classification และ MSE หรือ MAE สำหรับ Regression

## 4. Distance คือหัวใจของ k-NN

### 4.1 Euclidean distance

เมื่อ feature เป็นตัวเลข ระยะทางที่พบบ่อยคือ Euclidean distance:

$$
d(\mathbf{x},\mathbf{z})
=\sqrt{\sum_{j=1}^{d}(x_j-z_j)^2}
$$

โดย:

- $\mathbf{x}$ และ $\mathbf{z}$ คือข้อมูลสองจุด
- $j$ คือ feature ลำดับที่ $j$
- $d$ คือจำนวน feature
- ผลลัพธ์มีค่าตั้งแต่ 0 ขึ้นไป และ 0 หมายถึงสองจุดเหมือนกันทุก feature

ระยะนี้คือเส้นตรงระหว่างสองจุดใน feature space แต่จะมีความหมายก็ต่อเมื่อแต่ละ feature เปรียบเทียบกันได้อย่างเหมาะสม

### 4.2 Worked example: Regression และ Classification พร้อมกัน

ข้อมูลจากสไลด์มีดังนี้:

| Sample | $x_1$ | $x_2$ | $y_1$ | $y_2$ |
|---|---:|---:|---:|---|
| S1 | 1 | 5 | 1,000 | yes |
| S2 | 2 | 6 | 1,200 | yes |
| S3 | 3 | 1 | 1,100 | no |
| S4 | 2 | 4 | 2,000 | yes |
| S5 | 2 | 5 | ? | ? |

ต้องการทำนาย S5 ด้วย $k=3$

ระยะจาก S5 ไป S1:

$$
d(S5,S1)=\sqrt{(2-1)^2+(5-5)^2}=1
$$

คำนวณครบทุกจุดได้:

| เพื่อนบ้าน | การคำนวณ | Distance |
|---|---|---:|
| S1 | $\sqrt{(2-1)^2+(5-5)^2}$ | 1.000 |
| S2 | $\sqrt{(2-2)^2+(5-6)^2}$ | 1.000 |
| S3 | $\sqrt{(2-3)^2+(5-1)^2}$ | 4.123 |
| S4 | $\sqrt{(2-2)^2+(5-4)^2}$ | 1.000 |

เพื่อนบ้าน 3 จุดแรกคือ S1, S2 และ S4

สำหรับ Regression:

$$
\hat{y}_1=\frac{1000+1200+2000}{3}=1400
$$

สำหรับ Classification ทั้งสามจุดเป็น `yes` จึงได้:

$$
\hat{y}_2=\text{yes}
$$

ตัวอย่างนี้ทำให้เห็นว่า neighbor ชุดเดียวกันสามารถนำไปเฉลี่ยค่าตัวเลขหรือโหวต class ได้ ขึ้นอยู่กับชนิดของ target

### 4.3 Hamming distance สำหรับข้อมูลเชิงหมวดหมู่

ถ้า feature เป็น category เช่น `great`, `normal`, `yes`, `no` การลบและยกกำลังสองไม่มีความหมาย สไลด์จึงเสนอ **Hamming distance** ซึ่งนับจำนวนตำแหน่งที่ไม่ตรงกัน:

$$
H(\mathbf{x},\mathbf{z})
=\sum_{j=1}^{d}I(x_j\ne z_j)
$$

$I(\cdot)$ มีค่า 1 เมื่อเงื่อนไขเป็นจริง และ 0 เมื่อเป็นเท็จ

| Sample | Food | Chat | Fast | Price | Bar | Tip |
|---|---|---|---|---|---|---|
| S1 | great | yes | yes | normal | no | yes |
| S2 | great | no | yes | normal | no | yes |
| S3 | mediocre | yes | no | high | no | no |
| S4 | great | yes | yes | normal | yes | yes |
| S5 | great | no | no | high | no | ? |

เทียบเฉพาะ 5 feature แรก:

- $H(S5,S1)=3$ เพราะ `Chat`, `Fast` และ `Price` ต่างกัน
- $H(S5,S2)=2$ เพราะ `Fast` และ `Price` ต่างกัน
- $H(S5,S3)=2$ เพราะ `Food` และ `Chat` ต่างกัน
- $H(S5,S4)=4$ เพราะ `Chat`, `Fast`, `Price` และ `Bar` ต่างกัน

เมื่อ $k=2$ เพื่อนบ้านที่ใกล้ที่สุดคือ S2 ซึ่งมีคำตอบ `yes` และ S3 ซึ่งมีคำตอบ `no` จึงเกิด **vote tie** และยังตัดสิน class ไม่ได้จากเสียงข้างมากเพียงอย่างเดียว ระบบจริงต้องกำหนด tie-breaking rule เช่น ให้น้ำหนักตามระยะ เลือก class ตามลำดับที่กำหนด หรือปรับค่า $k$ โดยประเมินผ่าน cross-validation

โจทย์ฉบับปรับปรุงตั้งใจให้เห็นว่า $k$ เป็นเลขคู่สามารถทำให้ Binary Classification เสมอกันได้ แต่ **การเลือก $k$ เป็นเลขคี่ก็ไม่ได้รับประกันว่าจะไม่มี tie ทุกกรณี** เพราะยังอาจเสมอกันที่ระยะของเพื่อนบ้านหรือเกิดการแบ่งคะแนนใน Multiclass Classification

## 5. เลือกค่า $k$ อย่างไร

$k$ ควบคุมความเรียบของ decision boundary:

- $k$ เล็กมาก เช่น 1: โมเดลตอบสนองต่อรายละเอียดทุกจุด ขอบเขตคดเคี้ยวและไวต่อ noise จึงมีความเสี่ยง overfitting
- $k$ ใหญ่ขึ้น: การโหวตเฉลี่ยหลายจุดช่วยลดผลของ noise แต่ถ้าใหญ่เกินไป local pattern จะถูกกลบและเกิด underfitting

ไม่มีสูตร $\sqrt{N}$ หรือเลขคี่ใดที่รับประกันคำตอบดีที่สุด วิธีมาตรฐานคือกำหนด candidate หลายค่าแล้วเลือกด้วย cross-validation บน training data โดยไม่ใช้ test set ระหว่างการเลือก

```python
from sklearn.model_selection import GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

knn_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('model', KNeighborsClassifier())
])

parameter_grid = {
    'model__n_neighbors': [1, 3, 5, 7, 9, 11],
    'model__weights': ['uniform', 'distance'],
    'model__p': [1, 2]
}

grid_search = GridSearchCV(
    estimator=knn_pipeline,
    param_grid=parameter_grid,
    scoring='accuracy',
    cv=5,
    n_jobs=-1
)

grid_search.fit(X_train, y_train)

print(grid_search.best_params_)
print(grid_search.best_score_)
```

### พารามิเตอร์สำคัญ

| Parameter | ความหมาย | ผลเมื่อเปลี่ยน |
|---|---|---|
| `n_neighbors` | จำนวนเพื่อนบ้าน $k$ | เล็กทำให้ boundary ซับซ้อน; ใหญ่ทำให้เรียบขึ้น |
| `weights='uniform'` | ทุก neighbor มีน้ำหนักเท่ากัน | เป็นค่าเริ่มต้น |
| `weights='distance'` | จุดใกล้มีอิทธิพลมากกว่าจุดไกล | ช่วยเมื่อ neighbor อยู่ห่างไม่เท่ากัน |
| `p=1` | Manhattan distance | รวมระยะต่างแบบค่าสัมบูรณ์ |
| `p=2` | Euclidean distance | ระยะเส้นตรงใน feature space |
| `cv=5` | แบ่ง training data เป็น 5 folds | ใช้ประเมิน candidate โดยหมุน validation fold |

การใส่ scaler และโมเดลไว้ใน `Pipeline` ทำให้ scaler เรียนรู้ mean และ standard deviation เฉพาะจาก training folds จึงลดความเสี่ยง data leakage

## 6. ทำไม Feature Scaling จึงสำคัญมาก

สมมติ feature หนึ่งคือประชากรระดับหลายล้าน แต่อีก feature คืออายุระดับหลักสิบ ใน Euclidean distance ผลต่างของประชากรจะครอบงำผลต่างของอายุ แม้อายุอาจสำคัญต่อโจทย์กว่า ปัญหานี้ไม่ได้เกิดจากโมเดลรู้ว่าประชากรสำคัญ แต่เกิดจากหน่วยและสเกลของตัวเลข

### 6.1 Standardization หรือ z-score

$$
z=\frac{x-\mu}{\sigma}
$$

ค่าหลังแปลงมีค่าเฉลี่ยใกล้ 0 และส่วนเบี่ยงเบนมาตรฐานใกล้ 1 สำหรับ training data

> ข้อแก้ความเข้าใจจากสไลด์: z-score ไม่ได้บังคับทุกค่าให้อยู่ในช่วง $[-3,3]$ ช่วงดังกล่าวเป็นเพียงช่วงที่พบข้อมูลส่วนมากเมื่อ distribution ใกล้ Normal แต่ outlier สามารถมี z-score ต่ำกว่า −3 หรือสูงกว่า 3 ได้

### 6.2 Min-Max Scaling

$$
x'=\frac{x-x_{min}}{x_{max}-x_{min}}
$$

training data จะถูกแปลงให้อยู่ช่วง $[0,1]$ ตามค่า min และ max ที่เรียนรู้ แต่ข้อมูลใหม่สามารถออกนอกช่วงนี้ได้ถ้ามีค่าต่ำกว่า min หรือสูงกว่า max ของ training data

### 6.3 ลำดับที่ถูกต้อง

```python
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

knn_model = make_pipeline(
    StandardScaler(),
    KNeighborsClassifier(n_neighbors=5)
)

knn_model.fit(X_train, y_train)
test_accuracy = knn_model.score(X_test, y_test)

print(f'Test accuracy: {test_accuracy:.3f}')
```

ต้อง split ก่อน แล้วให้ scaler `fit()` จาก training data เท่านั้น หาก scale ทั้ง dataset ก่อน split ค่าเฉลี่ยและส่วนเบี่ยงเบนมาตรฐานจะมีข้อมูลจาก test set ปะปน ซึ่งเป็น data leakage

### 6.4 Worked example: Scaling เปลี่ยนเพื่อนบ้านที่ใกล้ที่สุดได้อย่างไร

เอกสารฉบับปรับปรุงเพิ่มตัวอย่างต่อไปนี้ โดย S4 เป็นข้อมูลใหม่ที่ต้องทำนายด้วย $k=1$:

| Sample | $X_1$ | $X_2$ | Class |
|---|---:|---:|---|
| S1 | 4.5 | 10,000 | yes |
| S2 | 0.1 | 3,000 | no |
| S3 | 0.2 | 3,200 | yes |
| S4 | 4.5 | 3,000 | ? |

ก่อน scaling ระยะของ $X_2$ ระดับหลักพันครอบงำ $X_1$:

| Training sample | Distance จาก S4 ก่อน scaling |
|---|---:|
| S1 | $\sqrt{(4.5-4.5)^2+(3000-10000)^2}=7000$ |
| S2 | $\sqrt{(4.5-0.1)^2+(3000-3000)^2}=4.4$ |
| S3 | $\sqrt{(4.5-0.2)^2+(3000-3200)^2}\approx200.046$ |

เพื่อนบ้านใกล้ที่สุดคือ S2 จึงทำนาย S4 เป็น `no`

เมื่อใช้ Min-Max Scaling โดยอาศัยค่า min และ max ของ training data:

$$
X_1'=\frac{X_1-0.1}{4.5-0.1},
\qquad
X_2'=\frac{X_2-3000}{10000-3000}
$$

ข้อมูลที่แปลงแล้วเป็น:

| Sample | $X_1'$ | $X_2'$ |
|---|---:|---:|
| S1 | 1.0000 | 1.0000 |
| S2 | 0.0000 | 0.0000 |
| S3 | 0.0227 | 0.0286 |
| S4 | 1.0000 | 0.0000 |

ระยะจาก S4 ไป S1 และ S2 เท่ากับ 1 ส่วนระยะไป S3 ประมาณ 0.978 ดังนั้น S3 กลายเป็นเพื่อนบ้านที่ใกล้ที่สุด และ prediction เปลี่ยนเป็น `yes`

ผลนี้ไม่ได้พิสูจน์ว่า scaling ทำให้คำตอบถูกเสมอ แต่พิสูจน์ว่า **scale เป็นส่วนหนึ่งของนิยามความใกล้** หากไม่ควบคุม scale โมเดลอาจให้ความสำคัญกับหน่วยวัดมากกว่าความสัมพันธ์กับ target

## 7. ปัญหาสำคัญของ k-NN

### 7.1 Noise และ outlier

จุดผิดปกติอาจกลายเป็น neighbor ใกล้ที่สุดและชักนำ prediction ผิด โดยเฉพาะเมื่อ $k$ เล็ก ควรตรวจสาเหตุของ outlier ก่อนลบเสมอ เพราะอาจเป็นเหตุการณ์จริงที่สำคัญ ไม่ใช่ข้อผิดพลาด

เอกสารฉบับใหม่เสนอ [**Robust Scaling**](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.RobustScaler.html) ซึ่งใช้ median และ interquartile range (IQR):

$$
x'=\frac{x-\mathrm{median}(x)}{IQR(x)}
$$

เพราะ median และ IQR ไวต่อค่ารุนแรงน้อยกว่า mean และ standard deviation จึงช่วยลดอิทธิพลของ outlier ต่อ scale แต่ไม่ได้ลบ outlier หรือรับประกันว่า outlier จะไม่กลายเป็น neighbor แนวทางอื่นได้แก่ปรับ $k$, ใช้ distance weighting, ตรวจ data quality หรือเลือก metric ที่เหมาะกับข้อมูล การลบ outlier ไม่ใช่คำตอบอัตโนมัติ

### 7.2 Prediction ช้าและใช้หน่วยความจำมาก

เพราะ k-NN เก็บ training instances และค้นหา neighbor ตอน predict การค้นหาแบบ brute force ต้องเปรียบเทียบกับข้อมูลจำนวนมาก โครงสร้างอย่าง KD-Tree และ Ball-Tree ช่วยลดเวลาค้นหาในบางสถานการณ์ แต่ประโยชน์ลดลงเมื่อมิติสูง

เอกสารฉบับใหม่เสนอ [**Product Quantization (PQ)**](https://docs.nvidia.com/cuvs/user-guide/api-guides/preprocessing-guide/product-quantization.html) สำหรับลด storage และเร่ง approximate nearest-neighbor search แนวคิดคือแบ่ง vector ออกเป็น subvectors แล้วแทนแต่ละส่วนด้วยรหัสของ centroid ใน codebook แทนการเก็บตัวเลขทุกมิติเต็มความละเอียด วิธีนี้ลดหน่วยความจำและทำให้ประมาณระยะได้เร็วขึ้น แต่แลกกับ quantization error ซึ่งอาจทำให้ลำดับ neighbor เปลี่ยน จึงต้องประเมินทั้ง recall ของการค้นหา latency และขนาด index

การบีบอัดไฟล์ทั่วไปอย่าง ZIP อาจลดพื้นที่จัดเก็บถาวร แต่ไม่ช่วยคำนวณระยะโดยตรง เพราะต้องคลายข้อมูลก่อน ส่วน PQ ออกแบบ representation ให้คำนวณระยะโดยประมาณจากรหัสได้ จึงตอบโจทย์ retrieval มากกว่า

### 7.3 Curse of Dimensionality

เมื่อจำนวน feature เพิ่ม พื้นที่มีปริมาตรเพิ่มเร็วมาก ข้อมูลจึงดูเบาบาง และระยะของจุดใกล้กับจุดไกลเริ่มแตกต่างกันน้อยลง คำว่า “ใกล้” จึงให้ข้อมูลน้อยลง

แนวทางรับมือ:

- เลือก feature ที่เกี่ยวข้องและตัด feature รบกวน
- ใช้ **PCA** ลดมิติแบบ unsupervised โดยรักษาทิศทางที่มีความแปรปรวนสูง แต่ความแปรปรวนสูงไม่จำเป็นต้องเป็นมิติที่แยก class ดีที่สุด
- ใช้ **LDA** ลดมิติแบบ supervised โดยใช้ class labels เพื่อเพิ่มการแยกระหว่างกลุ่ม จึงต้อง fit จาก training data เท่านั้น
- ใช้ **Autoencoder** เรียนรู้ latent representation แบบ nonlinear เมื่อมีข้อมูลและทรัพยากรเพียงพอ แต่มีความซับซ้อนและต้องตรวจ generalization
- ใช้ [**t-SNE**](https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html) เพื่อสำรวจหรือแสดงข้อมูลมิติสูงเป็น 2–3 มิติได้ แต่โดยทั่วไปไม่ควรใช้เป็น preprocessing หลักสำหรับ production k-NN เพราะเน้นรักษา local structure เพื่อ visualization และการฝังข้อมูลใหม่ไม่ตรงไปตรงมา
- เพิ่มข้อมูลให้เพียงพอกับมิติ
- ใช้ distance metric ที่สอดคล้องกับข้อมูล
- เปรียบเทียบกับโมเดลอื่นที่รับมือมิติสูงได้ดีกว่า

### 7.4 Decision boundary

เมื่อ $k=1$ แต่ละ training point มีอิทธิพลสูง พื้นที่เล็ก ๆ รอบจุดผิดปกติอาจกลายเป็นอีก class หนึ่ง เมื่อ $k$ ใหญ่ขึ้น ขอบเขตมักเรียบขึ้นเพราะต้องอาศัยฉันทามติจากพื้นที่กว้างกว่า ความเรียบนี้คือภาพเชิงเรขาคณิตของ bias–variance trade-off

---

# Part II: Decision Trees

## 8. Decision Tree คืออะไร

Decision Tree เป็น Supervised Learning model ที่เรียนรู้คำถามตาม feature แล้วแบ่งข้อมูลเป็นกิ่งไปเรื่อย ๆ จนถึงใบไม้ที่ให้ prediction ตัวอย่างกฎจากสไลด์ฉบับใหม่คือ:

```text
if X1 == F:
    Y = 1
elif X1 == M and X2 == N:
    Y = 0
else:
    Y = 1
```

การเพิ่ม `else` ทำให้กฎครอบคลุมทุก combination ที่ไม่ตรงสองเงื่อนไขแรก หากไม่มี default branch โมเดลจะไม่ระบุว่าจะตอบอะไรเมื่อพบกรณีใหม่ เช่น `X1=M` และ `X2=Y`

องค์ประกอบของต้นไม้มีดังนี้:

- **Root node** คือคำถามแรกที่ข้อมูลทุกแถวต้องผ่าน
- **Internal node** คือคำถามถัดไปภายในกิ่ง
- **Branch** คือผลของคำถามที่นำไปยัง node ถัดไป
- **Leaf node** คือจุดสิ้นสุดที่คืน class, probability หรือค่าทำนาย

โมเดลไม่ได้ให้เหตุผลเชิงสาเหตุ กฎที่ได้หมายความเพียงว่า split เหล่านั้นช่วยแบ่งข้อมูลฝึกตาม target ได้ดี

## 9. ต้นไม้เลือกคำถามแรกอย่างไร

คำถามที่ดีควรทำให้กลุ่มลูกบริสุทธิ์ขึ้น กล่าวคือหลัง split แล้วแต่ละกลุ่มควรมีตัวอย่าง class เดียวกันมากกว่าเดิม เราจึงต้องมีตัวเลขวัด **impurity**

## 10. Entropy

Entropy วัดความไม่แน่นอนของ class ภายใน node:

$$
H(S)=-\sum_{i=1}^{K}p_i\log_2p_i
$$

โดย:

- $S$ คือชุดข้อมูลใน node
- $K$ คือจำนวน class
- $p_i$ คือสัดส่วนของ class ที่ $i$

สำหรับ Binary Classification:

- ถ้าทุกตัวอย่างเป็น class เดียวกัน entropy = 0 เพราะไม่มีความไม่แน่นอน
- ถ้าสอง class มีสัดส่วน 50:50 entropy = 1 ซึ่งเป็นความไม่แน่นอนสูงสุด
- นิยาม $0\log_2 0=0$ จากค่าลิมิต เพื่อให้ class ที่ไม่ปรากฏไม่สร้างปัญหาในการคำนวณ

### 10.1 ตัวอย่าง Play Tennis

ข้อมูลมี `Yes` 9 ตัวอย่างและ `No` 5 ตัวอย่าง รวม 14:

$$
H(S)
=-\frac{9}{14}\log_2\frac{9}{14}
-\frac{5}{14}\log_2\frac{5}{14}
\approx0.940
$$

ค่า 0.940 บอกว่า root node ยังมี class ปะปนกันมาก แต่ entropy ไม่ใช่ accuracy และไม่ได้บอกโดยลำพังว่าจะเลือก feature ใด ต้องเปรียบเทียบ entropy ก่อนและหลัง split

## 11. Information Gain

Information Gain วัดว่า split ลดความไม่แน่นอนได้เท่าไร:

$$
IG(S,A)
=H(S)-\sum_{v\in Values(A)}\frac{|S_v|}{|S|}H(S_v)
$$

ส่วนหลังเครื่องหมายลบคือ weighted entropy ของ child nodes ต้องถ่วงน้ำหนักเพราะกิ่งที่มีข้อมูล 100 แถวควรมีอิทธิพลมากกว่ากิ่งที่มีข้อมูล 2 แถว

### 11.1 คำนวณ $IG(S,Outlook)$ ที่สไลด์ตั้งคำถามไว้

`Outlook` แบ่งเป็น 3 ค่า:

| Outlook | Yes | No | Total | Entropy |
|---|---:|---:|---:|---:|
| Sunny | 2 | 3 | 5 | 0.971 |
| Overcast | 4 | 0 | 4 | 0.000 |
| Rain | 3 | 2 | 5 | 0.971 |

Weighted entropy หลัง split:

$$
H(S\mid Outlook)
=\frac{5}{14}(0.971)
+\frac{4}{14}(0)
+\frac{5}{14}(0.971)
\approx0.694
$$

ดังนั้น:

$$
IG(S,Outlook)=0.940-0.694\approx0.247
$$

ค่าที่ต่างจาก 0.248 เล็กน้อยเกิดจากการปัดเศษระหว่างทาง

จากสไลด์ ค่า Information Gain ของ root คือ:

| Feature | Information Gain |
|---|---:|
| Outlook | 0.248 |
| Humidity | 0.151 |
| Wind | 0.048 |
| Temperature | 0.029 |

ID3 จึงเลือก `Outlook` เป็น root เพราะให้ Information Gain สูงสุดในการตัดสินใจรอบนั้น คำว่า “ดีที่สุด” หมายถึงดีที่สุดแบบ greedy ณ node ปัจจุบัน ไม่รับประกันว่าต้นไม้ทั้งต้นจะดีที่สุดทั่วโลก

### 11.2 เดินต่อในกิ่ง Sunny

เมื่อเลือก `Outlook` แล้ว กิ่ง `Overcast` มีแต่ `Yes` จึงจบเป็น leaf ส่วนกิ่ง `Sunny` ยังมี `No` 3 และ `Yes` 2:

$$
H(S_{sunny})\approx0.971
$$

สไลด์คำนวณ gain ภายใน subset นี้ได้:

| Candidate feature | Gain ในกิ่ง Sunny |
|---|---:|
| Humidity | 0.971 |
| Temperature | 0.571 |
| Wind | 0.020 โดยประมาณ |

`Humidity` แบ่ง Sunny subset ได้บริสุทธิ์พอดี จึงกลายเป็น node ถัดไป หลักการนี้ทำซ้ำแบบ recursive ในทุกกิ่งที่ยังไม่บริสุทธิ์

## 12. ID3 Algorithm

ID3 สร้างต้นไม้แบบ top-down:

1. ถ้าตัวอย่างทั้งหมดใน node เป็น class เดียว ให้สร้าง leaf เป็น class นั้น
2. ถ้าไม่มี feature เหลือ ให้สร้าง leaf เป็น class ที่พบมากที่สุด
3. เลือก feature ที่ให้ Information Gain สูงที่สุด
4. สร้าง branch สำหรับแต่ละค่าของ feature
5. ส่ง subset ของแต่ละ branch กลับเข้าอัลกอริทึมเดิม
6. ถ้า branch ไม่มีตัวอย่าง ให้ใช้ majority class ของ parent node

ตัวอย่าง pseudocode ที่อ่านง่าย:

```python
def id3(rows, target, available_features):
    if all_targets_are_the_same(target):
        return Leaf(target[0])

    if not available_features:
        return Leaf(most_common_class(target))

    best_feature = feature_with_highest_information_gain(
        rows,
        target,
        available_features
    )

    node = DecisionNode(best_feature)
    remaining_features = available_features - {best_feature}

    for value in unique_values(rows[best_feature]):
        child_rows, child_target = select_subset(
            rows,
            target,
            best_feature,
            value
        )

        node.add_branch(
            value,
            id3(child_rows, child_target, remaining_features)
        )

    return node
```

นี่เป็น pseudocode สำหรับเข้าใจกลไก ไม่ใช่ implementation พร้อมรัน เพราะ helper functions และ classes ยังไม่ได้ประกาศ

## 13. Gini Impurity

Gini Impurity เป็นอีกเกณฑ์วัดความปะปน:

$$
Gini(S)=1-\sum_{i=1}^{K}p_i^2
$$

สำหรับ Binary Classification:

- node บริสุทธิ์: $1-1^2-0^2=0$
- สัดส่วน 50:50: $1-0.5^2-0.5^2=0.5$

เมื่อประเมิน split ต้องคำนวณ weighted Gini ของ child nodes แล้วเลือกค่าต่ำที่สุด เพราะค่าต่ำแปลว่าหลัง split มีความปะปนน้อย

จากสไลด์:

| Feature | Weighted Gini หลัง split |
|---|---:|
| Outlook | 0.342 |
| Humidity | 0.367 |
| Wind | 0.428 |
| Temperature | 0.439 |

จึงเลือก `Outlook` เป็น root เช่นเดียวกับ Entropy/Information Gain ในตัวอย่างนี้ แต่สองเกณฑ์ไม่จำเป็นต้องเลือก split เดียวกันทุก dataset

## 14. Entropy กับ Gini ต่างกันอย่างไร

| ประเด็น | Entropy | Gini Impurity |
|---|---|---|
| สูตร | $-\sum p_i\log_2p_i$ | $1-\sum p_i^2$ |
| ช่วงใน binary case | 0 ถึง 1 | 0 ถึง 0.5 |
| ทิศทางที่ดี | ต่ำ | ต่ำ |
| การเลือก split | maximize impurity reduction | minimize weighted child impurity หรือ maximize reduction |
| การคำนวณ | มี logarithm | ไม่มี logarithm |

ไม่ควรเปรียบเทียบขนาดตัวเลขข้ามสูตรโดยตรง เช่น Gini 0.3 ไม่ได้แปลว่าดีกว่า Entropy 0.7 ต้องเปรียบเทียบ candidate ภายใต้ criterion เดียวกัน

## 15. ID3, C4.5 และ CART

| Algorithm | ลักษณะสำคัญ |
|---|---|
| ID3 | เลือก categorical feature ด้วย Information Gain และสร้าง multiway split |
| C4.5 | ต่อยอด ID3 ให้จัดการ continuous feature และ pruning ได้ดีขึ้น |
| CART | ใช้ binary split และรองรับทั้ง Classification กับ Regression |

scikit-learn ใช้ CART เวอร์ชันที่ปรับประสิทธิภาพ ไม่ได้มี ID3 โดยตรง และ `DecisionTreeClassifier` ใน scikit-learn ต้องรับ feature เชิงตัวเลข ดังนั้น category ต้อง encode ก่อน ไม่ควรแปลว่า Decision Tree ทุก implementation จัดการ category ดิบไม่ได้

## 16. Decision Tree ด้วย scikit-learn

```python
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

tree_model = DecisionTreeClassifier(
    criterion='entropy',
    max_depth=3,
    min_samples_leaf=5,
    random_state=42
)

tree_model.fit(X_train, y_train)
test_accuracy = tree_model.score(X_test, y_test)

print(f'Test accuracy: {test_accuracy:.3f}')
```

### Hyperparameters ที่มีผลต่อโครงสร้าง

| Hyperparameter | หน้าที่ | ผลเมื่อจำกัดมากขึ้น |
|---|---|---|
| `criterion` | วัดคุณภาพ split เช่น `'gini'`, `'entropy'` | เปลี่ยนวิธีจัดอันดับ candidate split |
| `max_depth` | ความลึกสูงสุด | ต้นไม้เล็กลง ลด variance แต่อาจ underfit |
| `min_samples_split` | จำนวน sample ขั้นต่ำก่อน node จะแตกต่อได้ | ป้องกันการแตก node ที่เล็กเกินไป |
| `min_samples_leaf` | จำนวน sample ขั้นต่ำในแต่ละ leaf | ทำให้ prediction แต่ละ leaf อาศัยข้อมูลมากขึ้น |
| `max_features` | จำนวน feature ที่พิจารณาต่อ split | เพิ่ม randomness และลด correlation ใน ensemble |
| `ccp_alpha` | ความแรงของ cost-complexity pruning | สูงขึ้นทำให้ prune มากขึ้น |
| `class_weight` | น้ำหนักแต่ละ class | ช่วยให้การฝึกคำนึงถึง class imbalance |
| `random_state` | ควบคุมส่วนที่มี randomness | ทำให้ผลทำซ้ำได้ |

Decision Tree ไม่อาศัยระยะทาง จึงไม่ต้อง scale feature เพื่อป้องกันหน่วยใหญ่ครอบงำแบบ k-NN อย่างไรก็ตาม preprocessing อื่น เช่น missing-value handling และ categorical encoding ยังต้องพิจารณาตาม implementation และข้อมูล

### ดูต้นไม้ที่เรียนรู้

```python
import matplotlib.pyplot as plt
from sklearn.tree import plot_tree

plt.figure(figsize=(14, 7))
plot_tree(
    tree_model,
    feature_names=feature_names,
    class_names=class_names,
    filled=True,
    rounded=True
)
plt.tight_layout()
plt.show()
```

เวลาอ่าน node ให้ดู:

- เงื่อนไข split
- impurity
- จำนวน samples ที่มาถึง node
- จำนวนหรือสัดส่วนของแต่ละ class
- predicted class

การมอง `feature_importances_` อย่างเดียวไม่พอ เพราะ impurity-based importance อาจมี bias และไม่บอกทิศทางผล ควรอ่านเส้นทางกฎ ตรวจ permutation importance หรือใช้วิธีอธิบายอื่นตามโจทย์

## 17. Overfitting และ Pruning

ถ้าปล่อยให้ต้นไม้เติบโตจนแต่ละ leaf มีข้อมูลน้อยมาก โมเดลสามารถจำรายละเอียดและ noise ใน training data ได้ Training Accuracy จึงสูง แต่ Test Accuracy ลดลง

### 17.1 Pre-pruning

หยุดการเติบโตก่อนต้นไม้ซับซ้อนเกินไป เช่น:

- จำกัด `max_depth`
- เพิ่ม `min_samples_split`
- เพิ่ม `min_samples_leaf`
- กำหนด `min_impurity_decrease`

### 17.2 Post-pruning และ Minimal Cost-Complexity Pruning

สร้างต้นไม้ก่อน แล้วตัดกิ่งที่เพิ่มความซับซ้อนมากกว่าประโยชน์ในการ generalize แนวคิด cost-complexity pruning ลงโทษต้นไม้ที่มี leaf มาก:

$$
R_\alpha(T)=R(T)+\alpha|T|
$$

- $R(T)$ คือความผิดพลาดหรือ impurity ของต้นไม้
- $|T|$ คือจำนวน terminal nodes
- $\alpha$ ควบคุมค่าปรับความซับซ้อน

เมื่อ $\alpha$ สูง ต้นไม้ขนาดใหญ่ถูกลงโทษมากขึ้น วิธีนี้เรียกว่า [**Minimal Cost-Complexity Pruning**](https://scikit-learn.org/stable/modules/tree.html#minimal-cost-complexity-pruning) หรือ Weakest Link Pruning โดยพิจารณาลำดับ subtree ที่ถูกตัดมากขึ้นเรื่อย ๆ แล้วเลือกค่าความซับซ้อนที่เหมาะสม ใน scikit-learn ใช้ `ccp_alpha` และควรเลือกค่าด้วย cross-validation ไม่ควรเลือกจาก test score

## 18. จากต้นไม้ต้นเดียวสู่ Ensemble

Decision Tree ต้นเดียวมี variance สูง การเปลี่ยนข้อมูลเล็กน้อยอาจสร้างต้นไม้ต่างกันมาก Ensemble จึงรวมต้นไม้หลายต้นเพื่อลดข้อจำกัดนี้

### 18.1 Bagging

Bagging หรือ Bootstrap Aggregation ทำงานดังนี้:

1. สุ่ม training set ขนาด $n$ จากข้อมูลเดิมแบบใส่คืน ทำให้บางแถวซ้ำและบางแถวไม่ถูกเลือก
2. ฝึก Decision Tree หนึ่งต้นบน bootstrap sample
3. ทำซ้ำทั้งหมด $M$ ต้น
4. Classification ใช้ majority vote; Regression ใช้ค่าเฉลี่ย

ต้นไม้แต่ละต้นเห็นข้อมูลต่างกัน ความผิดพลาดที่ไม่สัมพันธ์กันบางส่วนจึงหักล้างกัน Random Forest เพิ่มการสุ่ม feature ในแต่ละ split เพื่อทำให้ต้นไม้หลากหลายขึ้นอีก

### 18.2 Boosting

Boosting สร้าง weak learners ตามลำดับ โมเดลรอบใหม่มุ่งแก้ตัวอย่างที่ ensemble ก่อนหน้านี้ทำผิด ใน AdaBoost ตัวอย่างที่ทำนายผิดได้รับน้ำหนักเพิ่ม แล้วรวมต้นไม้ด้วยน้ำหนักตามความสามารถของแต่ละต้น

จุดต่างสำคัญ:

| ประเด็น | Bagging | Boosting |
|---|---|---|
| การฝึก | หลายโมเดลค่อนข้างอิสระ | ต่อเนื่องเป็นลำดับ |
| เป้าหมายหลัก | ลด variance | ลด bias และสร้างโมเดลที่เข้มแข็งจาก weak learners |
| การเน้นข้อมูลผิด | ไม่ได้เน้นโดยตรง | รอบถัดไปให้ความสำคัญมากขึ้น |
| ความไวต่อ noise | มักทนกว่า | อาจไวต่อ outlier/noise ถ้าไล่แก้ผิดมากเกินไป |

Bagging และ Boosting ไม่ใช่ pruning แต่เป็นอีกครอบครัววิธีจัดการข้อจำกัดของต้นไม้

---

# Part III: เลือกและประเมินโมเดล

## 19. k-NN กับ Decision Tree ต่างกันอย่างไร

| เกณฑ์ | k-NN | Decision Tree |
|---|---|---|
| วิธีทำนาย | ดูตัวอย่างใกล้เคียง | เดินตามกฎจาก root ถึง leaf |
| สิ่งที่เกิดตอน fit | เก็บข้อมูลและเตรียมโครงสร้างค้นหา | เรียนรู้ feature และ threshold ของแต่ละ split |
| Feature scaling | สำคัญมาก | โดยทั่วไปไม่จำเป็น |
| Prediction speed | อาจช้าเมื่อข้อมูลฝึกใหญ่ | มักเร็วตามความลึกของต้นไม้ |
| Memory | ต้องเก็บ training instances | เก็บโครงสร้างต้นไม้ |
| Decision boundary | local และยืดหยุ่น | แบ่งพื้นที่เป็นช่วงตามแกน feature |
| Interpretability | อธิบายผ่าน neighbors ที่ใกล้ | อธิบายเป็นเส้นทางกฎได้ง่ายเมื่อต้นไม้ไม่ใหญ่ |
| ปัญหาหลัก | scale, noise, มิติสูง, prediction cost | overfitting, instability, greedy split |
| Hyperparameter สำคัญ | $k$, weights, metric | depth, leaf size, criterion, pruning |

เลือก k-NN เมื่อแนวคิดความคล้ายมีความหมาย ข้อมูลไม่ใหญ่หรือมีโครงสร้างค้นหาที่เหมาะสม และ feature space ไม่สูงเกินไป เลือก Decision Tree เมื่อต้องการกฎที่สื่อสารได้ มี nonlinear interaction หรือไม่ต้องการ scaling แต่ต้องควบคุมความซับซ้อน

อย่าตัดสินจากข้อดีเชิงทฤษฎีเพียงอย่างเดียว ควรสร้าง pipeline ที่ถูกต้องและเปรียบเทียบด้วย cross-validation ภายใต้ metric เดียวกัน

## 20. การประเมินที่ถูกต้อง

สำหรับ Classification ควรเริ่มจาก confusion matrix แล้วเลือก metric ตามผลกระทบของความผิดพลาด:

- Accuracy เหมาะเมื่อ class ค่อนข้างสมดุลและความผิดพลาดแต่ละแบบมีต้นทุนใกล้กัน
- Precision สำคัญเมื่อ false positive มีต้นทุนสูง
- Recall สำคัญเมื่อ false negative มีต้นทุนสูง
- F1-score สมดุล precision และ recall
- ROC-AUC หรือ PR-AUC ใช้ประเมิน ranking หลาย threshold โดย PR-AUC มักให้ข้อมูลมากกว่าเมื่อ positive class พบได้น้อย

สำหรับ Regression ใช้ MAE, MSE, RMSE หรือ $R^2$ ตามคำถามและความไวต่อ error ขนาดใหญ่

ขั้นตอน model selection ที่ปลอดภัยคือ:

1. แยก test set ไว้ตั้งแต่ต้น
2. ใช้ cross-validation บน training set เพื่อเลือก preprocessing และ hyperparameters
3. fit configuration ที่เลือกบน training data ทั้งหมด
4. ประเมิน test set เพียงในขั้นสุดท้าย
5. วิเคราะห์ error ไม่ใช่รายงาน metric เดียว

## 21. Guided Lab: เปรียบเทียบ k-NN และ Decision Tree ด้วย Iris

### 21.1 เตรียมข้อมูล

```python
from sklearn.datasets import load_iris
from sklearn.metrics import classification_report, ConfusionMatrixDisplay
from sklearn.model_selection import train_test_split

iris = load_iris(as_frame=True)
X = iris.data
y = iris.target

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print('Training shape:', X_train.shape)
print('Test shape:', X_test.shape)
print(y_train.value_counts(normalize=True).sort_index())
```

`stratify=y` ช่วยรักษาสัดส่วน class ใกล้เคียงกันใน train และ test ส่วน `random_state=42` ทำให้แบ่งข้อมูลซ้ำได้ผลเดิม

### 21.2 ฝึกสองโมเดล

```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

models = {
    'k-NN': make_pipeline(
        StandardScaler(),
        KNeighborsClassifier(n_neighbors=5)
    ),
    'Decision Tree': DecisionTreeClassifier(
        max_depth=3,
        min_samples_leaf=3,
        random_state=42
    )
}

predictions = {}

for model_name, model in models.items():
    model.fit(X_train, y_train)
    predictions[model_name] = model.predict(X_test)

    print(f'\n{model_name}')
    print(classification_report(
        y_test,
        predictions[model_name],
        target_names=iris.target_names
    ))
```

จงทำนายก่อนรันว่าเหตุใด k-NN จึงมี `StandardScaler()` แต่ Decision Tree ไม่มี จากนั้นตรวจว่าแต่ละ class ผิดเป็น class ใดด้วย confusion matrix:

```python
for model_name, y_pred in predictions.items():
    ConfusionMatrixDisplay.from_predictions(
        y_test,
        y_pred,
        display_labels=iris.target_names,
        cmap='Blues'
    )
    plt.title(model_name)
    plt.tight_layout()
    plt.show()
```

### 21.3 Validation checks

```python
assert X_train.shape[1] == 4
assert len(X_train) + len(X_test) == len(X)
assert set(y_test.unique()).issubset(set(y_train.unique()))

for model_name, y_pred in predictions.items():
    assert len(y_pred) == len(y_test), model_name
```

โค้ดรันไม่ error ยังไม่พอ Assertions ช่วยตรวจรูปร่าง จำนวนแถว class และ alignment ของ prediction กับ test labels

### 21.4 การทดลองที่ควรทำ

1. เปลี่ยน `n_neighbors` เป็น 1, 3, 9 และ 25 แล้วเปรียบเทียบ Train/Test Accuracy
2. ตัด `StandardScaler()` ออกจาก k-NN แล้วอธิบายผลจากช่วงค่าของ Iris features
3. เปลี่ยน `max_depth` ของต้นไม้เป็น 1, 2, 3 และ `None`
4. เปรียบเทียบ `criterion='gini'` กับ `'entropy'`
5. รันหลาย `random_state` แล้วสังเกตว่า test score จาก dataset ขนาดเล็กผันผวนได้

---

## 22. Common Misconceptions

### “k-NN ไม่มีการ train เลย”

คำกล่าวนี้กว้างเกินไป ขั้น `fit()` ยังต้องตรวจและเก็บข้อมูล รวมทั้งอาจสร้าง index สำหรับค้นหา neighbor เพียงแต่ไม่ได้เรียนสมการ parameter แบบโมเดลเชิงเส้น

### “เลือก $k$ เป็นเลขคี่แล้วจะไม่มี tie”

จริงเฉพาะบางกรณีของ binary vote และยังมี tie ของระยะหรือ multiclass vote ได้ ต้องกำหนดพฤติกรรมเมื่อ tie และเลือก $k$ ด้วย validation

### “z-score ทำให้ข้อมูลอยู่ระหว่าง −3 ถึง 3”

ไม่จริง Standardization ทำให้ training feature มี mean ใกล้ 0 และ standard deviation ใกล้ 1 แต่ไม่ได้ clip ค่า

### “Decision Tree ไม่ต้องเตรียมข้อมูลเลย”

ไม่จริง แม้ไม่ต้อง scaling แต่ยังต้องจัดการ data type, missing values, category encoding, class imbalance, leakage และ train/test separation

### “ต้นไม้ลึกขึ้นย่อมแม่นขึ้น”

ต้นไม้ลึกมักลด training error แต่ test error อาจสูงขึ้นจาก overfitting ความลึกจึงต้องเลือกจาก validation ไม่ใช่ training score

### “Feature importance พิสูจน์ว่า feature เป็นสาเหตุ”

ไม่จริง Importance บอกว่าโมเดลใช้ feature ในการลด impurity หรือช่วย prediction ภายใต้ข้อมูลและโมเดลนี้ ไม่ใช่ causal effect

---

## 23. โจทย์ทบทวนและแนวคำตอบ

### ข้อ 1: อธิบายเหตุผลที่ scaling มีผลต่อ k-NN แต่ไม่ค่อยมีผลต่อ Decision Tree

**แนวคำตอบ:** k-NN ใช้ระยะทางโดยตรง ดังนั้น feature ที่มีหน่วยหรือช่วงค่ากว้างจะครอบงำ distance แม้ไม่ได้สำคัญกว่า ส่วน Decision Tree เปรียบเทียบค่าภายใน feature เดียวกับ threshold การแปลงเชิงอันดับแบบ scaling จึงไม่เปลี่ยนลำดับของตัวอย่างและมักได้ split เทียบเท่า อย่างไรก็ตาม preprocessing ด้าน missing values และ category ยังจำเป็น

### ข้อ 2: คำนวณ prediction เชิงหมวดหมู่ของ S5 ด้วย $k=2$

**แนวคำตอบ:** ใช้ Hamming distance กับ S5=`great, no, no, high, no` ได้ S1=3, S2=2, S3=2 และ S4=4 เพื่อนบ้านสองจุดคือ S2 ซึ่งมี class `yes` และ S3 ซึ่งมี class `no` จึงเกิด vote tie คำตอบที่สมบูรณ์ต้องบอก tie-breaking policy หรือเลือก $k$ ใหม่จาก cross-validation ไม่ควรตัดสิน class โดยพลการ

### ข้อ 3: เพราะเหตุใด Information Gain ต้องถ่วงน้ำหนัก child entropy

**แนวคำตอบ:** เพราะ child nodes มีจำนวนตัวอย่างไม่เท่ากัน หากเฉลี่ย entropy ทุกกิ่งเท่ากัน กิ่งเล็กมากจะมีอิทธิพลเท่ากิ่งใหญ่และทำให้ประเมิน split ผิด Weighted average จึงสะท้อนความไม่แน่นอนคาดหมายของตัวอย่างหนึ่งแถวหลังผ่าน split

### ข้อ 4: ต้นไม้มี Training Accuracy 100% แต่ Test Accuracy 72% ควรทำอย่างไร

**แนวคำตอบ:** ความต่างสูงเป็นหลักฐานของ overfitting ควรประเมินด้วย cross-validation และปรับ `max_depth`, `min_samples_leaf`, `min_samples_split` หรือ `ccp_alpha` ตรวจ leakage และ class balance แล้วเปรียบเทียบกับ ensemble การลดความลึกควรตัดสินจาก validation ไม่ใช่ test set ซ้ำ ๆ

### ข้อ 5: เปรียบเทียบ Bagging กับ Boosting

**แนวคำตอบ:** Bagging ฝึกโมเดลหลายตัวบน bootstrap samples และรวมผลเพื่อเฉลี่ยความผันผวน จึงเน้นลด variance ส่วน Boosting ฝึกตามลำดับและให้รอบหลังแก้ข้อผิดพลาดของรอบก่อน จึงสามารถลด bias ได้มาก แต่ไวต่อ noise มากกว่า ทั้งสองวิธีเป็น ensemble และต่างจาก pruning ซึ่งลดโครงสร้างของต้นไม้หนึ่งต้น

### ข้อ 6: ถ้าข้อมูลมี 50,000 แถว 500 feature และต้องทำนายแบบ real-time จะเลือก k-NN หรือ Decision Tree

**แนวคำตอบ:** ต้องทดลองจริง แต่เริ่มพิจารณา Decision Tree หรือ ensemble มากกว่า เพราะ k-NN ต้องเก็บและค้น training instances ตอน inference อีกทั้ง 500 feature เสี่ยง curse of dimensionality หากต้องใช้ k-NN ควรทำ feature selection/dimensionality reduction ประเมิน approximate search และวัด latency ควบคู่กับ accuracy

---

## 24. Likely Exam Focus

หัวข้อต่อไปนี้มีแนวโน้มสำคัญจากการเน้นและแบบคำนวณในสไลด์:

1. ขั้นตอน k-NN และการคำนวณ Euclidean/Hamming distance
2. การทำนาย Regression ด้วยค่าเฉลี่ย และ Classification ด้วย majority vote
3. ผลของ $k$ ต่อ overfitting และ underfitting
4. เหตุผลที่ k-NN ต้องทำ feature scaling
5. Entropy, Information Gain และการเลือก root node
6. Gini Impurity และทิศทางการเลือกค่าต่ำสุด
7. ลำดับการทำงานและ stopping conditions ของ ID3
8. ความแตกต่าง ID3, C4.5 และ CART
9. Overfitting, pre-pruning, post-pruning
10. Bagging กับ Boosting

### ตัวอย่างคำตอบแบบเขียนสอบ: k-NN ทำงานอย่างไร

k-NN เป็น non-parametric, instance-based supervised learning method ที่ทำนายข้อมูลใหม่จาก training instances ที่อยู่ใกล้ที่สุด ขั้นแรกคำนวณระยะจากข้อมูลใหม่ไปยัง training points แล้วเรียงลำดับ เลือก $k$ จุดที่ใกล้ที่สุด จากนั้น Classification ใช้ majority vote ส่วน Regression ใช้ค่าเฉลี่ยของ target ค่า $k$ เล็กมี variance สูงและเสี่ยง overfitting ขณะที่ $k$ ใหญ่เกินไปอาจ underfit เนื่องจาก k-NN พึ่งระยะทางจึงต้อง scale feature และควรเลือก $k$ ด้วย cross-validation

### ตัวอย่างคำตอบแบบเขียนสอบ: Decision Tree เลือก split อย่างไร

Decision Tree เลือก split ที่ทำให้ child nodes บริสุทธิ์กว่า parent node สำหรับ entropy criterion จะคำนวณ entropy ของ parent ลบ weighted entropy ของ children ซึ่งเรียกว่า Information Gain แล้วเลือก feature/split ที่ gain สูงสุด สำหรับ Gini criterion จะเลือก split ที่มี weighted child Gini ต่ำสุด กระบวนการทำซ้ำแบบ recursive จนถึง stopping condition แต่ถ้าต้นไม้ลึกเกินไปอาจ overfit จึงควรควบคุม depth, leaf size หรือ pruning โดยเลือก hyperparameters จาก validation data

---

## 25. สรุปความสัมพันธ์สำคัญ

k-NN และ Decision Tree เป็น non-parametric supervised learning methods เหมือนกัน แต่ k-NN นิยามคำตอบผ่านความใกล้ของตัวอย่าง ส่วน Decision Tree นิยามคำตอบผ่านการแบ่ง feature space ด้วยกฎ k-NN ย้ายภาระไปที่ prediction และไวต่อ scale กับมิติสูง ขณะที่ Decision Tree ย้ายภาระไปที่ training และไวต่อความซับซ้อนกับการเปลี่ยนแปลงข้อมูล

หัวใจของการใช้ทั้งสองวิธีไม่ใช่เพียงเรียก `.fit()` แต่ต้องเข้าใจว่าความคล้ายหรือความบริสุทธิ์ถูกวัดอย่างไร เลือก hyperparameter โดยไม่แตะ test set ป้องกัน leakage ตรวจทั้ง training และ validation performance และวิเคราะห์ความผิดพลาดในบริบทของโจทย์

---

## References

### เอกสารประกอบการเรียน

- Ekarat Rattagan. *Week 9: K-Nearest Neighbors (k-NN)*, revised October 2, 2026.
- Ekarat Rattagan. *Week 9-2: Decision Trees*, revised October 2, 2026.
- Bhatia, N. (2010). [Survey of Nearest Neighbor Techniques](https://arxiv.org/abs/1007.0085).
- Song, Y. Y., & Ying, L. U. (2015). [Decision tree methods: applications for classification and prediction](https://pmc.ncbi.nlm.nih.gov/articles/PMC4466856/).

### คำอธิบายเพิ่มเติมและการใช้งาน

- scikit-learn. [Nearest Neighbors User Guide](https://scikit-learn.org/stable/modules/neighbors.html).
- scikit-learn. [Decision Trees User Guide](https://scikit-learn.org/stable/modules/tree.html).
- scikit-learn. [StandardScaler](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.StandardScaler.html).
- scikit-learn. [RobustScaler](https://scikit-learn.org/stable/modules/generated/sklearn.preprocessing.RobustScaler.html).
- scikit-learn. [t-SNE](https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html).
- scikit-learn. [Cross-validation: evaluating estimator performance](https://scikit-learn.org/stable/modules/cross_validation.html).
- NVIDIA cuVS. [Product Quantization](https://docs.nvidia.com/cuvs/user-guide/api-guides/preprocessing-guide/product-quantization.html).
