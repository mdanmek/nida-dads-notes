# K-Nearest Neighbors (k-NN)

สมมติว่ามีข้อมูลใหม่หนึ่งแถวและต้องทำนายคำตอบ แต่เราไม่ได้เริ่มจากการสร้างสมการ วิธีที่ตรงไปตรงมาที่สุดคือค้นหาตัวอย่างในอดีตที่มีลักษณะใกล้เคียง แล้วใช้คำตอบของตัวอย่างเหล่านั้นช่วยตัดสิน แนวคิดนี้คือหัวใจของ **K-Nearest Neighbors (k-NN)**

บทนี้จะใช้ข้อมูลตัวอย่างชุดเดียวตลอดทาง เพื่ออธิบายว่าคำว่า “ใกล้” ถูกคำนวณอย่างไร ค่า $k$ เปลี่ยนคำตอบอย่างไร เหตุใด Feature Scaling จึงสำคัญ และเมื่อใดที่โมเดลซึ่งดูเรียบง่ายนี้เริ่มมีปัญหา

> **ขอบเขตของบท:** เนื้อหาหลักยึดตามสไลด์ Week 9: K-Nearest Neighbors ฉบับวันที่ 20 ตุลาคม 2026 คำอธิบายทีละขั้นและข้อสังเกตด้านการใช้งานเป็นส่วนขยายเพื่อให้เรียนด้วยตนเองได้ บทถัดไปอธิบายอีกแนวคิดหนึ่งซึ่งเรียนรู้กฎแทนการค้นหาเพื่อนบ้าน: [Decision Tree](09_decision_tree.md)

หลังอ่านบทนี้ ผู้อ่านควรสามารถอธิบายขั้นตอน k-NN, คำนวณ Euclidean และ Hamming Distance, ทำนายทั้ง Classification และ Regression, อธิบายผลของ $k$ และ Scaling และเลือกใช้โมเดลโดยมองเห็นข้อจำกัดของข้อมูลมิติสูง

---

## 1. k-NN อยู่ตรงไหนใน Supervised Learning

Supervised Learning เริ่มจากข้อมูลที่มี Feature $X$ และคำตอบ $y$ เราใช้ข้อมูลส่วนหนึ่งฝึกโมเดล แล้วนำโมเดลไปทำนายข้อมูลใหม่

ถ้า $y$ เป็นตัวเลขต่อเนื่อง เช่น ราคา อุณหภูมิ หรือระยะเวลารอ เราเรียกงานนั้นว่า **Regression** แต่ถ้า $y$ เป็นกลุ่ม เช่น ผ่าน/ไม่ผ่าน หรือชนิดของดอกไม้ เราเรียกว่า **Classification**

Linear Regression และ Logistic Regression สร้างสมการที่มี Coefficients ให้เรียนรู้ แต่ k-NN ไม่ได้สรุป Training Data เป็นสมการรูปเดียว มันเก็บตัวอย่างไว้และย้อนกลับมาค้นหาตัวอย่างที่ใกล้ข้อมูลใหม่ในเวลาทำนาย

ด้วยเหตุนี้ k-NN จึงถูกเรียกว่า

- **Instance-based Learning** เพราะยังใช้ Training Instances แต่ละแถวตอนทำนาย
- **Lazy Learning** เพราะงานคำนวณสำคัญเกิดตอน `predict()` มากกว่าตอน `fit()`
- **Non-parametric Model** เพราะไม่ได้บังคับความสัมพันธ์ให้อยู่ในสมการที่มีจำนวน Parameters คงที่

คำว่า Non-parametric ไม่ได้แปลว่าไม่มีค่าต้องเลือก k-NN ยังมี **Hyperparameters** เช่น จำนวนเพื่อนบ้าน $k$, วิธีวัดระยะ และวิธีให้น้ำหนักเพื่อนบ้าน

### 1.1 Cost Function กับ Evaluation Metric ไม่ใช่สิ่งเดียวกัน

k-NN ไม่มี Cost Function สำหรับปรับ Coefficients แบบ Linear หรือ Logistic Regression แต่ต้องมี **Distance Function** เพื่อวัดความคล้าย และยังต้องมี **Evaluation Metric** เพื่อวัดว่าคำทำนายดีเพียงใด

- Classification อาจประเมินด้วย Confusion Matrix, Accuracy, Precision, Recall หรือ F1-score
- Regression อาจประเมินด้วย MAE, MSE, RMSE หรือ $R^2$

MSE เป็นตัวเลขวัดขนาด Error ส่วน Confusion Matrix เป็นตารางนับประเภทของผลทำนาย ทั้งสองจึงไม่ใช่สิ่งเดียวกัน และคำว่า “Error Matrix” ไม่ใช่ชื่อมาตรฐานของ MSE

---

## 2. k-NN ทำงานอย่างไร

ตัวอักษร $k$ หมายถึงจำนวนเพื่อนบ้านที่ใช้ตัดสิน ถ้า $k=3$ โมเดลจะเลือก Training Examples ที่ใกล้ข้อมูลใหม่ที่สุดสามแถว

กระบวนการมีสี่ขั้นตอน

1. คำนวณระยะจากข้อมูลใหม่ไปยัง Training Examples ทุกแถว
2. เรียงระยะจากน้อยไปมาก
3. เลือก $k$ แถวแรก
4. Classification ใช้การโหวต ส่วน Regression ใช้ค่าเฉลี่ยของ Target

```mermaid
flowchart LR
    A["ข้อมูลใหม่"] --> B["คำนวณระยะ"]
    B --> C["เลือก k เพื่อนบ้าน"]
    C --> D["โหวตหรือเฉลี่ย"]
    D --> E["Prediction"]
```

ให้อ่านภาพจากซ้ายไปขวา ข้อมูลใหม่ไม่ได้ถูกนำไปฝึกโมเดลซ้ำ แต่ถูกเปรียบเทียบกับ Training Data ที่เก็บไว้ การนิยามระยะจึงเป็นตัวกำหนดว่าใครจะถูกนับเป็นเพื่อนบ้าน

---

## 3. Euclidean Distance: เปลี่ยนคำว่า “คล้าย” ให้เป็นตัวเลข

เมื่อ Features เป็นตัวเลข ระยะพื้นฐานที่ใช้บ่อยคือ **Euclidean Distance** ซึ่งเป็นระยะเส้นตรงระหว่างสองจุด

$$d(x_i,x_j)=\sqrt{\sum_{r=1}^{m}(x_{i,r}-x_{j,r})^2}$$

โดย $x_i$ และ $x_j$ คือข้อมูลสองแถว, $r$ คือ Feature ลำดับที่ $r$ และ $m$ คือจำนวน Features

สูตรทำสามอย่างตามลำดับ: หาผลต่างของแต่ละ Feature, ยกกำลังสองเพื่อไม่ให้ผลต่างบวกกับลบหักล้างกัน แล้วรวมและถอดรากเพื่อกลับมาเป็นระยะทาง หากระยะเท่ากับศูนย์ แสดงว่าสองแถวมีค่า Features เหมือนกันทั้งหมด

Distance ไม่ได้รู้ว่า Feature ใดมีความหมายทางธุรกิจมากกว่า มันสะท้อนเพียงนิยามทางคณิตศาสตร์ที่เราเลือกไว้ หากหน่วยหรือ Scale ไม่เหมาะ เพื่อนบ้านที่ได้ก็อาจไม่ใช่ตัวอย่างที่คล้ายกันในความหมายของโจทย์จริง

---

## 4. Worked Example: ทำนายทั้ง Regression และ Classification

ใช้ข้อมูลจากสไลด์ดังนี้ โดย $s_5$ เป็นข้อมูลใหม่ที่ยังไม่ทราบคำตอบ

| Sample | $x_1$ | $x_2$ | Target ตัวเลข $y_1$ | Target กลุ่ม $y_2$ |
|---|---:|---:|---:|---|
| $s_1$ | 1 | 10 | 1,000 | yes |
| $s_2$ | 2 | 7 | 1,200 | yes |
| $s_3$ | 3 | 5 | 1,100 | no |
| $s_4$ | 3 | 2 | 2,000 | yes |
| $s_5$ | 2 | 9 | ? | ? |

เราต้องคำนวณระยะจาก $s_5=(2,9)$ ไปยังทุกแถวใน Training Data

$$d(s_5,s_1)=\sqrt{(2-1)^2+(9-10)^2}=\sqrt{2}\approx1.414$$

$$d(s_5,s_2)=\sqrt{(2-2)^2+(9-7)^2}=2$$

$$d(s_5,s_3)=\sqrt{(2-3)^2+(9-5)^2}=\sqrt{17}\approx4.123$$

$$d(s_5,s_4)=\sqrt{(2-3)^2+(9-2)^2}=\sqrt{50}\approx7.071$$

เมื่อนำมาเรียงจากใกล้ไปไกล:

| ลำดับ | Neighbor | Distance | $y_1$ | $y_2$ |
|---:|---|---:|---:|---|
| 1 | $s_1$ | 1.414 | 1,000 | yes |
| 2 | $s_2$ | 2.000 | 1,200 | yes |
| 3 | $s_3$ | 4.123 | 1,100 | no |
| 4 | $s_4$ | 7.071 | 2,000 | yes |

### 4.1 ผลเมื่อเปลี่ยน $k$

| $k$ | Neighbors ที่ใช้ | Regression: ค่าเฉลี่ย $y_1$ | Classification: เสียงข้างมาก $y_2$ |
|---:|---|---:|---|
| 1 | $s_1$ | 1,000 | yes |
| 2 | $s_1,s_2$ | 1,100 | yes |
| 3 | $s_1,s_2,s_3$ | 1,100 | yes |
| 4 | ทุกแถว | 1,325 | yes |

ตัวอย่างนี้บังเอิญได้ Class `yes` ทุกค่า $k$ แต่ค่าทำนายแบบ Regression เปลี่ยน เพราะเพื่อนบ้านที่ไกลและมี Target สูงถูกนำเข้ามาเฉลี่ยเมื่อ $k$ เพิ่มขึ้น จึงไม่ควรสรุปว่า $k$ ไม่มีผลเพียงเพราะ Class ในตัวอย่างหนึ่งไม่เปลี่ยน

ถ้า $k=3$ คำตอบแบบ Regression คือ

$$\hat{y}_1=\frac{1000+1200+1100}{3}=1100$$

ส่วน Classification มี `yes` สองเสียงและ `no` หนึ่งเสียง จึงทำนาย `yes`

---

## 5. Hamming Distance สำหรับ Categorical Data

Euclidean Distance ใช้การลบตัวเลข แต่ Category เช่น `great`, `normal`, `yes` และ `no` ไม่มีระยะทางตามธรรมชาติ วิธีพื้นฐานคือ **Hamming Distance** ซึ่งนับจำนวนตำแหน่งที่ค่าไม่ตรงกัน

$$H(x_i,x_j)=\sum_{r=1}^{m}I(x_{i,r}\ne x_{j,r})$$

$I$ เป็น Indicator Function มีค่า 1 เมื่อค่าต่างกัน และ 0 เมื่อตรงกัน ระยะที่ต่ำกว่าจึงหมายถึงมี Attributes ตรงกันมากกว่า

ใช้ตารางแบบฝึกหัดหน้าที่สองของสไลด์:

| Sample | Food | Chat | Fast | Price | Bar | Tip |
|---|---|---|---|---|---|---|
| $s_1$ | great | yes | yes | normal | no | yes |
| $s_2$ | great | no | yes | normal | no | yes |
| $s_3$ | mediocre | yes | no | high | no | no |
| $s_4$ | great | yes | yes | normal | yes | yes |
| $s_5$ | great | no | no | high | no | ? |

เทียบเฉพาะห้า Features แรก:

- $H(s_5,s_1)=3$ เพราะ `Chat`, `Fast` และ `Price` ต่างกัน
- $H(s_5,s_2)=2$ เพราะ `Fast` และ `Price` ต่างกัน
- $H(s_5,s_3)=2$ เพราะ `Food` และ `Chat` ต่างกัน
- $H(s_5,s_4)=4$ เพราะ `Chat`, `Fast`, `Price` และ `Bar` ต่างกัน

เมื่อ $k=2$ เพื่อนบ้านคือ $s_2$ ซึ่งเป็น `yes` กับ $s_3$ ซึ่งเป็น `no` จึงโหวตเสมอ โมเดลต้องมีกติกาเพิ่มเติม เช่น ให้น้ำหนักตามระยะ เปลี่ยน $k$ หรือกำหนด Tie-breaking Rule ที่แน่นอน

> **ข้อสังเกตจากเอกสาร:** ตาราง Categorical Data สองหน้ามีค่า `Tip` ของ $s_2$ และ `Price` ของ $s_5$ ไม่ตรงกัน บทเรียนนี้ใช้หน้าที่สองซึ่งเป็นหน้าที่กำหนดโจทย์ $k=2$ โดยตรง ความไม่สอดคล้องของข้อมูลสามารถเปลี่ยนคำตอบได้ จึงต้องตรวจ Version ก่อนคำนวณ

Hamming Distance ถือว่าความไม่ตรงกันทุก Feature มีต้นทุนเท่ากัน หาก `Price` สำคัญกว่า `Chat` วิธีนี้อาจไม่สะท้อนโจทย์จริง เราอาจออกแบบ Weighted Distance ได้ แต่ Weight ควรมาจากหลักฐานและ Validation ไม่ใช่กำหนดตามความรู้สึกเพียงอย่างเดียว

---

## 6. ค่า $k$ ควบคุมความละเอียดของ Decision Boundary

เมื่อ $k=1$ ข้อมูลใหม่รับคำตอบจากจุดใกล้ที่สุดเพียงจุดเดียว Decision Boundary จึงคดเคี้ยวตาม Training Data และไวต่อ Noise หากจุดหนึ่งติด Label ผิด พื้นที่รอบจุดนั้นอาจทำนายผิดตามไปด้วย

เมื่อ $k$ ใหญ่ขึ้น การตัดสินใช้หลายจุด Noise ของจุดเดียวมีอิทธิพลน้อยลง Boundary เรียบขึ้น แต่ถ้า $k$ ใหญ่เกินไป รูปแบบเฉพาะพื้นที่จะถูกเสียงส่วนใหญ่กลบและเกิด Underfitting

| ค่า $k$ | พฤติกรรม | ความเสี่ยงเด่น |
|---|---|---|
| เล็ก | เน้นรายละเอียดเฉพาะพื้นที่ | Variance สูง, Overfitting |
| ปานกลาง | สมดุลรายละเอียดกับความเรียบ | ต้องเลือกจาก Validation |
| ใหญ่ | เฉลี่ยข้อมูลกว้างและ Boundary เรียบ | Bias สูง, Underfitting |

สไลด์เสนอเลขคี่เพื่อลดโอกาสเสมอใน Binary Classification และใช้ $\sqrt{N}$ เป็นจุดเริ่มต้น แต่ทั้งสองอย่างเป็นเพียง Heuristic ค่า $k$ ที่เหมาะสมควรเลือกด้วย Cross-validation บน Training Data และเก็บ Test Data ไว้ประเมินครั้งสุดท้าย

เลขคี่ช่วยลด Tie จากจำนวนเสียงใน Binary Classification แต่ยังอาจมีจุดหลายจุดที่ระยะเท่ากัน และ Multiclass Classification ยังเกิดคะแนนเสมอได้

---

## 7. Feature Scaling เปลี่ยนเพื่อนบ้านได้อย่างไร

k-NN ไม่รู้หน่วยของ Feature มันเห็นเพียงตัวเลข หาก Feature หนึ่งคือ Population ระดับหลายล้าน แต่อีก Feature คือ Age ระดับหลักสิบ ผลต่างของ Population จะครอบงำ Euclidean Distance แม้ Age อาจสำคัญต่อผลลัพธ์มากกว่า

นี่ไม่ใช่หลักฐานว่า Feature ที่มีตัวเลขใหญ่สำคัญกว่า แต่เป็นผลจากหน่วยวัด Features ที่ใช้คำนวณระยะจึงควรถูกปรับให้อยู่ใน Scale ที่เปรียบเทียบกันได้

### 7.1 Standardization หรือ z-score

$$z=\frac{x-\mu}{\sigma}$$

เราลบค่าเฉลี่ย $\mu$ แล้วหารด้วยส่วนเบี่ยงเบนมาตรฐาน $\sigma$ ทำให้ Training Feature มีค่าเฉลี่ยใกล้ 0 และส่วนเบี่ยงเบนมาตรฐานใกล้ 1

ข้อความในสไลด์ที่ว่า z-score “Maps to range $(-3,3)$” ต้องตีความอย่างระมัดระวัง Standardization ไม่ได้บังคับให้ทุกค่าอยู่ในช่วงนี้ หากข้อมูลใกล้ Normal Distribution ค่าส่วนมากอาจอยู่ระหว่าง -3 และ 3 แต่ Outliers สามารถออกนอกช่วงได้

### 7.2 Min-Max Scaling

$$x'=\frac{x-x_{min}}{x_{max}-x_{min}}$$

สำหรับ Training Data ค่าต่ำสุดจะเป็น 0 และค่าสูงสุดเป็น 1 แต่ข้อมูลใหม่อาจออกนอกช่วง $[0,1]$ หากต่ำกว่าหรือสูงกว่าช่วงที่พบตอน Fit Scaler

### 7.3 Worked Example: คำตอบเปลี่ยนหลัง Scaling

| Sample | $X_1$ | $X_2$ | Class |
|---|---:|---:|---|
| $s_1$ | 4.5 | 10,000 | yes |
| $s_2$ | 0.1 | 3,000 | no |
| $s_3$ | 0.2 | 3,200 | yes |
| $s_4$ | 4.5 | 3,000 | ? |

ก่อน Scaling และใช้ $k=1$:

$$d(s_4,s_1)=7000$$

$$d(s_4,s_2)=4.4$$

$$d(s_4,s_3)=\sqrt{4.3^2+200^2}\approx200.046$$

เพื่อนบ้านใกล้ที่สุดคือ $s_2$ จึงทำนาย `no` เพราะผลต่างของ $X_2$ ครอบงำระยะทาง

ต่อไปทำ Min-Max Scaling โดยใช้ Min และ Max จาก Training Data $s_1,s_2,s_3$ เท่านั้น:

| Sample | $X_1'$ | $X_2'$ |
|---|---:|---:|
| $s_1$ | 1.0000 | 1.0000 |
| $s_2$ | 0.0000 | 0.0000 |
| $s_3$ | 0.0227 | 0.0286 |
| $s_4$ | 1.0000 | 0.0000 |

ระยะใหม่คือ

$$d(s_4,s_1)=1$$

$$d(s_4,s_2)=1$$

$$d(s_4,s_3)\approx0.978$$

หลัง Scaling เพื่อนบ้านใกล้ที่สุดเปลี่ยนเป็น $s_3$ และคำทำนายเปลี่ยนเป็น `yes` Scaling จึงไม่ได้เพียงทำให้ตัวเลขสวยขึ้น แต่เปลี่ยนเรขาคณิตของ Feature Space และ Prediction โดยตรง

Scaler ต้อง Fit ด้วย Training Data เท่านั้น หากใช้ทั้ง Dataset ก่อนแบ่ง Train/Test ค่า Min, Max, Mean หรือ Standard Deviation จาก Test Data จะรั่วเข้าสู่ขั้น Training เกิด Data Leakage

---

## 8. ข้อจำกัดของ k-NN

### 8.1 Noisy Data และ Outliers

จุดผิดปกติอาจกลายเป็นเพื่อนบ้านใกล้ที่สุดและเปลี่ยน Prediction ก่อนลบ Outlier ต้องตรวจว่าเป็นข้อมูลผิดจริงหรือเป็นกรณีหายากที่สำคัญ เพราะการลบทุกค่าที่แปลกอาจทำให้โมเดลมองไม่เห็นกลุ่มเสี่ยง

Robust Scaling ใช้ Median และ Interquartile Range จึงไวต่อ Outlier น้อยกว่า Mean และ Standard Deviation

$$x'=\frac{x-\mathrm{median}}{\mathrm{IQR}}$$

### 8.2 Prediction ช้าและใช้ Memory สูง

k-NN ต้องเก็บ Training Instances และค้นหาเพื่อนบ้านตอน Predict เวลาคำนวณจึงเพิ่มตามขนาด Training Data โครงสร้างอย่าง KD-tree หรือ Ball-tree ช่วยในข้อมูลบางลักษณะ แต่ประโยชน์ลดลงเมื่อมิติสูงมาก ตามเอกสาร [Nearest Neighbors ของ scikit-learn](https://scikit-learn.org/stable/modules/neighbors.html) ประสิทธิภาพขึ้นกับทั้งจำนวนแถว จำนวน Features และโครงสร้างภายในของข้อมูล

Product Quantization ช่วยบีบอัด Vectors และรองรับ Approximate Nearest Neighbor Search แต่แลกกับโอกาสที่ผลค้นหาไม่ใช่เพื่อนบ้านที่ใกล้ที่สุดจริงทุกครั้ง

### 8.3 Curse of Dimensionality

เมื่อจำนวน Features เพิ่ม ปริมาตรของ Feature Space เพิ่มเร็ว ข้อมูลจึงกระจายห่างกันและระยะ “ใกล้” กับ “ไกล” เริ่มต่างกันน้อยลง k-NN ต้องการข้อมูลมากขึ้นเพื่อรักษาความหนาแน่นของเพื่อนบ้าน

แนวทางรับมือคือเลือก Features ที่มีความหมายหรือลดมิติ เช่น PCA สำหรับย่อความแปรปรวนเชิงเส้น และ LDA สำหรับหาทิศที่ช่วยแยก Class เมื่อมี Labels ส่วน [t-SNE](https://scikit-learn.org/stable/modules/generated/sklearn.manifold.TSNE.html) เหมาะกับการแสดงภาพข้อมูลมิติสูงมากกว่าการเป็น Preprocessing เริ่มต้นสำหรับทำนายข้อมูลใหม่ทุกงาน

### 8.4 การประยุกต์ใช้

แนวคิด Nearest Neighbors ถูกใช้กับ Image Geolocation, Data Imputation และ Recommendation Systems แต่คำว่า “เพื่อนบ้าน” ต้องนิยามให้สอดคล้องกับงาน เช่น ระบบแนะนำอาจใช้ความคล้ายของพฤติกรรมแทนระยะของข้อมูลประชากร

---

## 9. เมื่อใดควรและไม่ควรเริ่มจาก k-NN

k-NN เหมาะเป็นจุดเริ่มต้นเมื่อความคล้ายเชิงระยะมีความหมาย จำนวน Features ไม่สูงเกินไป Dataset ยังมีขนาดที่ค้นหาได้ และต้องการ Baseline ที่อธิบายง่าย โมเดลยังเหมาะเมื่อ Local Patterns สำคัญและ Boundary ไม่เป็นเส้นตรง

ควรระวังเมื่อข้อมูลมีหน่วยต่างกันมาก มี Noise สูง จำนวน Features มาก Training Data ใหญ่มาก หรือต้อง Predict แบบ Real-time ด้วย Latency ต่ำ เพราะภาระการค้นหาจะเกิดในเวลาที่ผู้ใช้รอคำตอบ

ถ้าต้องการกฎที่อ่านได้และ Prediction เร็วกว่า แนวคิดถัดไปคือ [Decision Tree](09_decision_tree.md) ซึ่งเรียนรู้เงื่อนไขไว้ตั้งแต่ Training แทนการค้นหา Training Instances ทุกครั้ง

---

## 10. การประเมินและเลือก Hyperparameters โดยไม่แตะ Test Set

ลำดับที่ปลอดภัยคือ

1. แยก Test Set ไว้ตั้งแต่ต้น
2. ใช้ Cross-validation ภายใน Training Set เพื่อเลือก $k$, Scaling, Distance Metric และ Neighbor Weights
3. Fit Configuration ที่เลือกบน Training Data ทั้งหมด
4. ประเมิน Test Set หนึ่งครั้งในขั้นสุดท้าย
5. วิเคราะห์ชนิดของ Error เพิ่มจาก Metric สรุป

สำหรับ Classification ให้เลือก Metric ตามต้นทุนความผิดพลาด Accuracy เหมาะเมื่อ Classes ค่อนข้างสมดุล Precision สำคัญเมื่อ False Positive มีต้นทุนสูง Recall สำคัญเมื่อ False Negative มีต้นทุนสูง และ F1-score ใช้เมื่ออยากสมดุล Precision กับ Recall

สำหรับ Regression ใช้ MAE, MSE, RMSE หรือ $R^2$ ตามคำถาม MSE ลงโทษ Error ขนาดใหญ่แรงขึ้นเพราะยกกำลังสอง ส่วน MAE อ่านเป็นหน่วยเดียวกับ Target ได้ตรงไปตรงมา

---

## 11. จุดที่ควรจำให้แม่น

- k-NN มีขั้น `fit()` ที่เบา ไม่ได้แปลว่าไม่มีการ Train เลย
- Non-parametric ไม่ได้แปลว่าไม่มี Hyperparameters
- เลขคี่ช่วยลด Vote Tie บางกรณี แต่ไม่รับประกันว่าไม่มี Tie ทุกกรณี
- Standardization ไม่ได้ Clip ทุกค่าให้อยู่ระหว่าง -3 ถึง 3
- Scaling ต้องเรียนจาก Training Data เท่านั้น
- Distance ที่คำนวณได้ถูกต้องทางคณิตศาสตร์อาจยังไม่เหมาะทางความหมาย
- การลดมิติควรเลือกตามวัตถุประสงค์ ไม่ใช่ใช้ t-SNE เป็น Default Preprocessing

---

## 12. คำถามฝึกตอบพร้อมแนวคำตอบ

### ข้อ 1: k-NN ต่างจาก Logistic Regression อย่างไร

**แนวคำตอบ:** Logistic Regression เรียนรู้ Coefficients แล้วคำนวณ Probability จากสมการ ส่วน k-NN เก็บ Training Instances และทำนายจากตัวอย่างที่อยู่ใกล้ข้อมูลใหม่ k-NN จึงไม่มีสมการสรุปแบบเดียวกับ Logistic Regression แต่ไวต่อ Distance Metric, Feature Scaling และจำนวนข้อมูลที่ต้องค้นหาระหว่าง Prediction

### ข้อ 2: จากตัวอย่างในหัวข้อ 4 ถ้า $k=3$ ค่าทำนายเป็นเท่าใด

**แนวคำตอบ:** เพื่อนบ้านสามจุดคือ $s_1,s_2,s_3$ เพราะมีระยะ 1.414, 2.000 และ 4.123 Regression ได้ $(1000+1200+1100)/3=1100$ ส่วน Classification มี `yes` สองเสียงและ `no` หนึ่งเสียง จึงทำนาย `yes`

### ข้อ 3: เพราะเหตุใด Feature Scaling จึงมีผลต่อ k-NN

**แนวคำตอบ:** Euclidean Distance ใช้ขนาดผลต่างของ Features โดยตรง Feature ที่มีหน่วยหรือช่วงกว้างจึงครอบงำระยะ แม้ไม่ได้สำคัญกว่า Scaling ทำให้ Features มีขนาดที่เปรียบเทียบกันได้และอาจเปลี่ยน Neighbor Set รวมถึง Prediction

### ข้อ 4: เหตุใดไม่ควรเลือก $k$ จาก Test Accuracy

**แนวคำตอบ:** ถ้าใช้ Test Set เปรียบเทียบค่า $k$ หลายครั้ง ข้อมูล Test จะมีอิทธิพลต่อ Model Selection และไม่เป็นข้อมูลใหม่จริงอีกต่อไป ควรเลือก $k$ ด้วย Cross-validation บน Training Data แล้วใช้ Test Set ประเมิน Configuration สุดท้ายครั้งเดียว

### ข้อ 5: ข้อมูลมี 50,000 แถว 500 Features และต้อง Predict แบบ Real-time ควรกังวลอะไร

**แนวคำตอบ:** k-NN ต้องค้นหา Training Instances ตอน Prediction จึงมีความเสี่ยงด้าน Latency และ Memory อีกทั้ง 500 Features ทำให้เกิด Curse of Dimensionality ควรพิจารณา Feature Selection หรือ Dimensionality Reduction วัด Latency จริง และเปรียบเทียบกับโมเดลที่เรียนกฎล่วงหน้า เช่น Decision Tree หรือ Ensemble

---

## 13. Likely Exam Focus

หัวข้อต่อไปนี้คาดจากสิ่งที่สไลด์เน้น ไม่ใช่ข้อมูลข้อสอบจริง

1. ลำดับการทำงานของ k-NN
2. การคำนวณ Euclidean Distance
3. Classification ด้วย Majority Vote และ Regression ด้วย Average
4. Hamming Distance สำหรับ Categorical Data
5. ผลของ $k$ ต่อ Overfitting และ Underfitting
6. Standardization, Min-Max Scaling และตัวอย่างที่ Prediction เปลี่ยน
7. Noisy Data, Prediction Time, Storage และ Curse of Dimensionality

### ตัวอย่างคำตอบแบบเขียนสอบ

k-NN เป็น Instance-based, Non-parametric Supervised Learning Method ที่ทำนายข้อมูลใหม่จาก Training Examples ที่อยู่ใกล้ที่สุด ขั้นแรกคำนวณ Distance จากข้อมูลใหม่ไปยัง Training Data แล้วเรียงจากน้อยไปมาก เลือก $k$ จุดที่ใกล้ที่สุด จากนั้น Classification ใช้ Majority Vote ส่วน Regression ใช้ค่าเฉลี่ยของ Target ค่า $k$ เล็กให้ Boundary ยืดหยุ่นและเสี่ยง Overfitting ขณะที่ $k$ ใหญ่เกินไปอาจ Underfit เนื่องจากโมเดลพึ่ง Distance จึงควร Scale Features และเลือก $k$ ด้วย Cross-validation

---

## 14. สรุปท้ายบท

k-NN เปลี่ยนการทำนายให้เป็นปัญหาการค้นหาตัวอย่างที่คล้ายกัน กลไกจึงขึ้นกับสามสิ่ง: Distance นิยามความคล้าย, $k$ กำหนดขอบเขตของ Neighborhood และวิธีรวมคำตอบเปลี่ยนตาม Classification หรือ Regression

ความเรียบง่ายของ k-NN ทำให้มองเห็นผลของ Feature Engineering ได้ชัดมาก หาก Scale ไม่เหมาะ เพื่อนบ้านจะเปลี่ยน หาก $k$ เล็กเกินไป โมเดลจะไล่ตาม Noise หาก $k$ ใหญ่เกินไป รูปแบบเฉพาะพื้นที่จะหาย และเมื่อมิติสูงขึ้น ความหมายของระยะจะอ่อนลง

บทถัดไปเปลี่ยนคำถามจาก “ข้อมูลใหม่นี้คล้ายใคร” เป็น “ควรถามเงื่อนไขอะไรเพื่อแบ่งข้อมูลให้บริสุทธิ์ขึ้น” ซึ่งนำไปสู่ [Decision Tree](09_decision_tree.md)

---

## References

- Ekarat Rattagan. *Week 9: K-Nearest Neighbors (k-NN)*, revised October 20, 2026.
- Bhatia, N. (2010). [Survey of Nearest Neighbor Techniques](https://arxiv.org/abs/1007.0085).
- scikit-learn. [Nearest Neighbors](https://scikit-learn.org/stable/modules/neighbors.html).
- scikit-learn. [Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html).
