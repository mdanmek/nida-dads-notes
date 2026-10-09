# ชุดคำถาม–คำตอบเตรียมสอบกลางภาค Applied Machine Learning

> DADS6003 Lecture 01–07 — เรียงตามบท เน้นคำตอบแบบเขียนสอบ  
> คำถามชุดนี้คาดจากหัวข้อและจุดเน้นใน Lecture ไม่ใช่ข้อสอบจริง

วิธีใช้: อ่านเฉพาะคำถามก่อน ปิดคำตอบแล้วลองพูดหรือเขียนจากความจำ จากนั้นเปิดตรวจและเติมส่วนที่ขาด

---

# บทที่ 1: Machine Learning Introduction

## ข้อ 1: Traditional Programming และ Machine Learning ต่างกันอย่างไร

**คำตอบ**

Traditional Programming รับข้อมูลและกฎที่มนุษย์กำหนด แล้วประมวลผลเป็นคำตอบ ส่วน Machine Learning รับข้อมูลและตัวอย่างคำตอบเพื่อเรียนรู้กฎหรือโมเดลจากข้อมูล

ML ไม่ได้หมายความว่าไม่ต้องเขียนโปรแกรม แต่หมายถึงไม่ต้องเขียนกฎตัดสินทุกกรณีด้วยตนเอง เรายังต้องเตรียมข้อมูล ฝึกโมเดล ประเมินผล และดูแลโมเดลหลังนำไปใช้

---

## ข้อ 2: อธิบาย Task, Performance และ Experience ตามนิยามของ Tom Mitchell

**คำตอบ**

โปรแกรมเรียนรู้จากประสบการณ์ **E** สำหรับงาน **T** ซึ่งวัดด้วยตัวชี้วัด **P** หากผลงานดีขึ้นเมื่อได้รับประสบการณ์เพิ่มขึ้น

ตัวอย่างระบบจำแนกลายมือ:

- **Task:** จำแนกรูปภาพว่าเป็นตัวเลขใด
- **Experience:** ชุดรูปลายมือที่มี Label
- **Performance:** สัดส่วนรูปที่จำแนกถูก

---

## ข้อ 3: Supervised, Unsupervised และ Reinforcement Learning ต่างกันอย่างไร

**คำตอบ**

- **Supervised Learning:** มีคำตอบกำกับ ถ้าคำตอบเป็นตัวเลขเรียก Regression ถ้าเป็นกลุ่มเรียก Classification
- **Unsupervised Learning:** ไม่มีคำตอบกำกับ ใช้ค้นหารูปแบบ เช่น Clustering, Dimensionality Reduction และ Anomaly Detection
- **Reinforcement Learning:** เรียนจาก State, Action และ Reward เพื่อหา Policy

Regression หรือ Classification พิจารณาจากชนิดของคำตอบ $y$ ไม่ใช่ชนิดของ Feature

---

## ข้อ 4: องค์ประกอบสามส่วนของอัลกอริทึม ML คืออะไร

**คำตอบ**

1. **Representation:** รูปแบบของโมเดล เช่น Linear Regression
2. **Optimization:** วิธีหาพารามิเตอร์ เช่น Gradient Descent
3. **Evaluation:** เกณฑ์วัดคุณภาพ เช่น MSE หรือ Accuracy

ตัวอย่าง Linear Regression ใช้สมการเส้นตรงเป็น Representation ใช้ Gradient Descent เป็น Optimization และใช้ MSE วัดความผิดระหว่างฝึก

---

## ข้อ 5: เพราะเหตุใดกระบวนการสร้าง ML จึงไม่ใช่กระบวนการเส้นตรง

**คำตอบ**

ผลจากขั้นหลังอาจแสดงปัญหาของขั้นก่อนหน้า เช่น โมเดลทำงานไม่ดีเพราะข้อมูลไม่สะอาด Feature ไม่เพียงพอ หรือเลือก Metric ไม่เหมาะสม จึงต้องมี Feedback Loop เพื่อย้อนกลับไปแก้ข้อมูล Feature โมเดล หรือโจทย์ธุรกิจ

---

# บทที่ 2: Single Variable Linear Regression

## ข้อ 6: Linear Regression คืออะไร และพารามิเตอร์มีความหมายอย่างไร

**คำตอบ**

Linear Regression ใช้ทำนายค่าตัวเลขต่อเนื่อง:

$$
\hat{y}=\theta_0+\theta_1x
$$

$\theta_0$ คือ Intercept หรือค่าทำนายเมื่อ $x=0$ ส่วน $\theta_1$ คือ Slope เมื่อ $x$ เพิ่มหนึ่งหน่วย ค่าทำนายเปลี่ยนไป $\theta_1$ หน่วย

---

## ข้อ 7: MSE คืออะไร และเหตุใดจึงยกกำลังสอง Error

**คำตอบ**

$$
\mathrm{MSE}=\frac{1}{N}\sum_{i=1}^{N}(\hat{y}_i-y_i)^2
$$

การยกกำลังสองทำให้ Error บวกและลบไม่หักล้างกัน และลงโทษ Error ขนาดใหญ่มากกว่า Error ขนาดเล็ก ข้อจำกัดคือไวต่อ Outlier

---

## ข้อ 8: `arg min` ต่างจาก `min` อย่างไร

**คำตอบ**

`min` คือค่าต่ำสุดของ Cost Function ส่วน `arg min` คือค่าพารามิเตอร์ที่ทำให้ Cost ต่ำที่สุด สิ่งที่นำไปใช้ทำนายคือพารามิเตอร์ จึงเขียนว่า

$$
\hat{\theta}=\underset{\theta}{\mathrm{arg\,min}}\ J(\theta)
$$

---

## ข้อ 9: Normal Equation และ Gradient Descent ต่างกันอย่างไร

**คำตอบ**

Normal Equation หาคำตอบโดยตรง:

$$
\theta=(X^TX)^{-1}X^Ty
$$

ไม่ต้องกำหนด Learning Rate และไม่ต้องวนซ้ำ แต่คำนวณแพงเมื่อ Feature มากและอาจมีปัญหา Inverse

Gradient Descent ปรับพารามิเตอร์ซ้ำไปในทิศตรงข้ามกับ Gradient รองรับ Feature จำนวนมากและไม่มีปัญหา Inverse แต่ต้องเลือก Learning Rate จำนวนรอบ และควรทำ Feature Scaling

---

## ข้อ 10: Learning Rate ใหญ่หรือเล็กเกินไปส่งผลอย่างไร

**คำตอบ**

- ใหญ่เกินไป: อาจก้าวข้ามจุดต่ำสุด แกว่ง หรือไม่ลู่เข้า
- เล็กเกินไป: ลู่เข้าช้าและต้องใช้หลายรอบ
- เหมาะสม: Cost ลดลงต่อเนื่องจนลู่เข้า

---

## ข้อ 11: จงหา MSE เมื่อค่าจริงคือ 1, 1, 4 และค่าทำนายคือ 3, 3, 3

**คำตอบ**

$$
\mathrm{MSE}=\frac{(3-1)^2+(3-1)^2+(3-4)^2}{3}
=\frac{4+4+1}{3}=3
$$

---

# บทที่ 3: Multiple Linear Regression

## ข้อ 12: Multiple Linear Regression ต่างจาก Simple Linear Regression อย่างไร

**คำตอบ**

Simple Linear Regression ใช้ Feature เดียว ส่วน Multiple Linear Regression ใช้หลาย Feature:

$$
\hat{y}=\theta_0+\theta_1x_1+\cdots+\theta_dx_d
$$

Coefficient ของ Feature หนึ่งแสดงการเปลี่ยนแปลงของค่าทำนายเมื่อ Feature นั้นเพิ่มหนึ่งหน่วย โดยควบคุม Feature อื่นให้คงที่

---

## ข้อ 13: เพราะเหตุใด Gradient Descent จึงต้องทำ Feature Scaling

**คำตอบ**

Feature ที่มีสเกลต่างกันมากทำให้ Gradient ของพารามิเตอร์มีขนาดไม่สมดุล แต่ทุกพารามิเตอร์ใช้ Learning Rate เดียวกัน ส่งผลให้การลู่เข้าช้าหรือไม่เสถียร Feature Scaling ทำให้แต่ละ Feature อยู่ในสเกลใกล้กัน จึงช่วยให้ Optimization สมดุลขึ้น

---

## ข้อ 14: Min-Max Scaling และ Z-score ต่างกันอย่างไร

**คำตอบ**

Min-Max Scaling:

$$
x'=\frac{x-x_{min}}{x_{max}-x_{min}}
$$

Training Data มักอยู่ช่วง 0–1

Z-score Standardization:

$$
z=\frac{x-\mu}{\sigma}
$$

ทำให้ Training Data มีค่าเฉลี่ยประมาณ 0 และส่วนเบี่ยงเบนมาตรฐานประมาณ 1 ค่าที่ใช้แปลงต้องคำนวณจาก Training Set แล้วใช้ค่าเดิมกับ Validation และ Test Set

---

## ข้อ 15: BGD, SGD และ Mini-batch ต่างกันอย่างไร

**คำตอบ**

- **BGD:** ใช้ข้อมูลทั้งหมดต่อหนึ่ง Update เสถียรแต่หนึ่งก้าวช้า
- **SGD:** ใช้หนึ่งแถวต่อหนึ่ง Update เร็วแต่แกว่งมาก
- **Mini-batch:** ใช้ข้อมูลกลุ่มเล็ก เป็นทางสายกลางระหว่างความเร็วและความเสถียร

Learning Rate Scheduling ช่วยลดความแกว่งโดยค่อย ๆ ลดขนาดก้าว

---

## ข้อ 16: Polynomial Regression คืออะไร และยังเป็น Linear Regression หรือไม่

**คำตอบ**

Polynomial Regression สร้าง Feature ใหม่ เช่น $x^2$ และ $x_1x_2$ เพื่อจับความสัมพันธ์โค้ง แม้กราฟจะโค้ง แต่ยังเป็น Linear Model เพราะเป็น Linear ในพารามิเตอร์ $\theta$

ข้อดีคือแก้ Underfitting จากโมเดลที่ง่ายเกินไป ข้อจำกัดคือดีกรีสูงทำให้โมเดลซับซ้อนและเสี่ยง Overfitting

---

# บทที่ 4: Logistic Regression

## ข้อ 17: เพราะเหตุใด Linear Regression จึงไม่เหมาะกับ Classification

**คำตอบ**

Linear Regression ให้ผลได้ตั้งแต่ลบอนันต์ถึงบวกอนันต์ จึงตีความเป็น Probability ไม่ได้ Logistic Regression นำคะแนน $z=\theta^Tx$ ผ่าน Sigmoid:

$$
\sigma(z)=\frac{1}{1+e^{-z}}
$$

ผลลัพธ์จึงอยู่ระหว่าง 0 กับ 1 และตีความเป็น Probability ของ Class 1 ได้

---

## ข้อ 18: Sigmoid, Threshold และ Decision Boundary ต่างกันอย่างไร

**คำตอบ**

- **Sigmoid:** เปลี่ยนคะแนนเป็น Probability
- **Threshold:** เปลี่ยน Probability เป็น Class
- **Decision Boundary:** ตำแหน่งในพื้นที่ Feature ที่โมเดลเปลี่ยนคำตอบระหว่าง Class

เมื่อ Threshold เท่ากับ 0.5 Decision Boundary เกิดที่ $\theta^Tx=0$

---

## ข้อ 19: Polynomial Features ส่งผลต่อ Decision Boundary อย่างไร

**คำตอบ**

หากใช้ Feature เชิงเส้นสองตัว Decision Boundary จะเป็นเส้นตรง แต่ถ้าเพิ่ม $x_1^2$, $x_2^2$ หรือ Interaction Boundary สามารถเป็นเส้นโค้งหรือวงกลมได้ ความโค้งเกิดจาก Feature ไม่ได้เกิดจาก Sigmoid โดยตรง

---

## ข้อ 20: ทำไม Logistic Regression จึงใช้ Cross-Entropy แทน MSE

**คำตอบ**

MSE ที่ครอบ Sigmoid มีคุณสมบัติด้าน Cost และ Gradient ที่ไม่เหมาะเท่า Cross-Entropy ส่วน Cross-Entropy เหมาะกับ Probability และลงโทษสูงเมื่อโมเดลมั่นใจแต่ตอบผิด

$$
J(\theta)=-\frac{1}{N}\sum_{i=1}^{N}
[y_i\ln(\hat{p}_i)+(1-y_i)\ln(1-\hat{p}_i)]
$$

---

## ข้อ 21: Logistic Regression มีคำว่า Regression แต่เหตุใดใช้ทำ Classification

**คำตอบ**

โมเดลสร้างสมการเชิงเส้นสำหรับคะแนนหรือ Log-odds แล้วใช้ Sigmoid เปลี่ยนเป็น Probability จากนั้นใช้ Threshold ตัดเป็น Class ผลลัพธ์สุดท้ายจึงเป็น Classification

---

# บทที่ 5: Naive Bayes Classification

## ข้อ 22: อธิบาย Prior, Likelihood, Evidence และ Posterior

**คำตอบ**

$$
P(Y\mid X)=\frac{P(X\mid Y)P(Y)}{P(X)}
$$

- **Prior:** Probability ของ Class ก่อนเห็นข้อมูลใหม่
- **Likelihood:** Probability ของ Feature เมื่อทราบ Class
- **Evidence:** Probability ของข้อมูลในประชากรทั้งหมด
- **Posterior:** Probability ของ Class หลังเห็นข้อมูล

โมเดลเลือก Class ที่มี Posterior สูงที่สุด

---

## ข้อ 23: เพราะเหตุใด Naive Bayes จึงใช้สมมติฐาน Conditional Independence

**คำตอบ**

การคำนวณ Joint Probability ของหลาย Feature ต้องใช้ข้อมูลจำนวนมาก Naive Bayes จึงสมมติว่า Feature เป็นอิสระต่อกันเมื่อทราบ Class:

$$
P(X\mid Y)=\prod_jP(x_j\mid Y)
$$

ทำให้โมเดลเร็วและใช้ข้อมูลน้อย แต่ Feature ที่สัมพันธ์กันมากอาจทำให้โมเดลนับหลักฐานซ้ำ

---

## ข้อ 24: Naive Bayes มีข้อดีและข้อจำกัดอะไร

**คำตอบ**

ข้อดีคือฝึกและทำนายเร็ว ใช้ข้อมูลไม่มาก และเหมาะกับข้อมูลมิติสูง เช่น Text Classification ข้อจำกัดคือพึ่งสมมติฐาน Independence และมีปัญหา Zero Probability เมื่อ Category ไม่เคยปรากฏใน Training Data

---

## ข้อ 25: Naive Bayes จัดการ Continuous Feature อย่างไร

**คำตอบ**

Categorical Feature คำนวณ Probability จากการนับ ส่วน Continuous Feature มักสมมติการแจกแจง Gaussian แล้วประมาณค่าเฉลี่ยและความแปรปรวนของแต่ละ Feature แยกตาม Class

---

## ข้อ 26: Zero Probability คืออะไร และ Laplace Smoothing แก้อย่างไร

**คำตอบ**

ถ้าค่า Feature ไม่เคยปรากฏใน Class ใด Likelihood จะเป็นศูนย์ และทำให้คะแนนทั้ง Class เป็นศูนย์ Laplace Smoothing บวก 1 ให้จำนวนของทุก Category

$$
P(\mathrm{low})=\frac{0+1}{1000+3}=\frac{1}{1003}
$$

---

## ข้อ 27: Logistic Regression และ Naive Bayes ต่างกันอย่างไร

**คำตอบ**

Logistic Regression เรียน Probability และ Decision Boundary โดยตรงผ่าน Sigmoid ส่วน Naive Bayes สร้าง Posterior จาก Prior และ Likelihood ภายใต้สมมติฐาน Conditional Independence

---

# บทที่ 6: Regularization

## ข้อ 28: Underfitting และ Overfitting ต่างกันอย่างไร

**คำตอบ**

Underfitting เกิดจากโมเดลง่ายเกินไป ทำให้ Training และ Validation Error สูง เรียกว่า High Bias

Overfitting เกิดจากโมเดลซับซ้อนและจำ Noise ของ Training Data ทำให้ Training Error ต่ำ แต่ Validation/Test Error สูง เรียกว่า High Variance

---

## ข้อ 29: Regularization คืออะไร และช่วยลด Overfitting อย่างไร

**คำตอบ**

Regularization เพิ่มค่าปรับตามขนาด Coefficient เข้าไปใน Loss เมื่อ Coefficient ขนาดใหญ่ถูกลงโทษ โมเดลจะเรียบง่ายลงและลดการไล่ตาม Noise ของ Training Data

$$
\mathrm{Regularized\ Cost}=\mathrm{Original\ Loss}+\mathrm{Penalty}
$$

---

## ข้อ 30: ค่า $\lambda$ ส่งผลต่อ Bias และ Variance อย่างไร

**คำตอบ**

- $\lambda$ ต่ำ: ค่าปรับน้อย โมเดลยืดหยุ่น Bias ต่ำ แต่ Variance สูงขึ้น
- $\lambda$ สูง: โมเดลเรียบง่าย Variance ลด แต่ Bias เพิ่ม
- สูงเกินไป: โมเดล Underfit

จึงต้องเลือก $\lambda$ จาก Validation Data ไม่ใช่เลือกค่าสูงที่สุด

---

## ข้อ 31: Ridge และ Lasso ต่างกันอย่างไร

**คำตอบ**

Ridge ใช้ L2 Penalty:

$$
\lambda\sum_{j=1}^{d}\theta_j^2
$$

ทำให้ Coefficient ทุกตัวเล็กลง แต่มักไม่เป็นศูนย์

Lasso ใช้ L1 Penalty:

$$
\lambda\sum_{j=1}^{d}|\theta_j|
$$

ทำให้บาง Coefficient เป็นศูนย์ จึงใช้เลือก Feature ได้

---

## ข้อ 32: เพราะเหตุใด Lasso ทำให้ Coefficient เป็นศูนย์ แต่ Ridge มักไม่ทำ

**คำตอบ**

บริเวณข้อจำกัดของ Ridge เป็นวงกลมที่ขอบเรียบ จุดสัมผัสจึงมักไม่อยู่บนแกน ส่วน Lasso เป็นรูปข้าวหลามตัดที่มีมุมอยู่บนแกน จุดสัมผัสจึงมีโอกาสอยู่ที่มุม ซึ่งทำให้ Coefficient บางตัวเป็นศูนย์

---

## ข้อ 33: Elastic Net คืออะไร และใช้เมื่อใด

**คำตอบ**

Elastic Net ผสม L1 และ L2 จึงทำให้บาง Coefficient เป็นศูนย์พร้อมกับจัดการกลุ่ม Feature ที่สัมพันธ์กันได้ดีกว่า Lasso เพียงอย่างเดียว เหมาะเมื่อมี Feature จำนวนมาก ทั้ง Feature ที่ไม่สำคัญและ Feature ที่สัมพันธ์กันสูง

ต้องตรวจนิยาม Mixing Parameter ของสูตรหรือ Software เพราะ $\alpha$ และ `l1_ratio` อาจกำหนดทิศต่างกัน

---

# บทที่ 7: Model Training and Evaluation

## ข้อ 34: Training, Validation และ Test Set มีหน้าที่ต่างกันอย่างไร

**คำตอบ**

- **Training:** ใช้หาพารามิเตอร์
- **Validation:** ใช้เลือกโมเดล Feature หรือ Hyperparameter
- **Test:** ใช้ประเมินครั้งสุดท้ายหลังตัดสินใจทุกอย่างแล้ว

ไม่ควรใช้ Test Set เลือกโมเดล เพราะจะ Overfit กับ Test และทำให้ผลประเมินไม่เป็นกลาง

---

## ข้อ 35: Hold-out และ Cross-Validation ต่างกันอย่างไร

**คำตอบ**

Hold-out แบ่งข้อมูลเพียงครั้งเดียว เช่น Train 80% และ Test 20% ง่ายและเร็ว แต่ผลขึ้นกับการสุ่มแบ่ง

k-fold Cross-Validation หมุนเวียน Fold ที่ใช้ Validation หลายรอบ ทำให้ประเมินเสถียรกว่าแต่ใช้เวลามากกว่า

สไลด์เรียกการแบ่ง 60/20/20 ว่า Cross Validation แต่ตามศัพท์มาตรฐานเป็น Train–Validation–Test Split แบบ Hold-out

---

## ข้อ 36: วินิจฉัย High Bias และ High Variance จาก Error อย่างไร

**คำตอบ**

- Training และ Validation Error สูง: High Bias หรือ Underfitting
- Training Error ต่ำ แต่ Validation Error สูง: High Variance หรือ Overfitting
- ทั้งคู่ต่ำและใกล้กัน: Generalize ได้ดี

---

## ข้อ 37: วิธีใดใช้แก้ High Bias และ High Variance

**คำตอบ**

แก้ High Bias ด้วยการเพิ่ม Useful Features เพิ่ม Polynomial Features ลด $\lambda$ หรือเพิ่มความซับซ้อน

แก้ High Variance ด้วยการเพิ่ม Training Data ลด Feature ลดความซับซ้อน หรือเพิ่ม $\lambda$

หลักจำคือเพิ่มความยืดหยุ่นช่วยลด Bias ส่วนลดความยืดหยุ่นช่วยลด Variance

---

## ข้อ 38: Confusion Matrix คืออะไร

**คำตอบ**

- **TP:** ทำนาย Positive และจริงเป็น Positive
- **FP:** ทำนาย Positive แต่จริงเป็น Negative
- **FN:** ทำนาย Negative แต่จริงเป็น Positive
- **TN:** ทำนาย Negative และจริงเป็น Negative

Positive หมายถึง Class ที่สนใจตรวจจับ ไม่ได้หมายถึงสิ่งดีเสมอไป

---

## ข้อ 39: Accuracy, Precision และ Recall ต่างกันอย่างไร

**คำตอบ**

$$
\mathrm{Accuracy}=\frac{TP+TN}{TP+TN+FP+FN}
$$

$$
\mathrm{Precision}=\frac{TP}{TP+FP}
$$

$$
\mathrm{Recall}=\frac{TP}{TP+FN}
$$

Accuracy วัดความถูกต้องทั้งหมด Precision วัดความน่าเชื่อถือของการเตือน และ Recall วัดความสามารถในการจับ Positive จริง

---

## ข้อ 40: ทำไม Accuracy อย่างเดียวจึงไม่เพียงพอ

**คำตอบ**

เมื่อ Class ไม่สมดุล โมเดลอาจทาย Class ใหญ่ทั้งหมดแล้วได้ Accuracy สูง เช่น ผู้ป่วยมี 1% โมเดลที่ทายว่าไม่ป่วยทุกคนได้ Accuracy 99% แต่ Recall ของผู้ป่วยเป็น 0 จึงต้องดู Precision, Recall หรือ F1 ร่วมด้วย

---

## ข้อ 41: ควรเน้น Precision หรือ Recall ในสถานการณ์ใด

**คำตอบ**

เน้น Precision เมื่อ FP มีต้นทุนสูง เช่น การระงับบัญชีลูกค้าปกติ เน้น Recall เมื่อ FN มีต้นทุนสูง เช่น การพลาดผู้ป่วยโรคร้าย การเลือก Metric ต้องอิงผลกระทบของความผิดพลาด

---

## ข้อ 42: ทำไม F1 ใช้ Harmonic Mean

**คำตอบ**

$$
F_1=\frac{2PR}{P+R}
$$

Harmonic Mean ถูกดึงลงโดยค่าที่ต่ำกว่า ทำให้ F1 สูงเมื่อทั้ง Precision และ Recall สูง ไม่ยอมให้ค่าหนึ่งที่สูงมากชดเชยอีกค่าที่ต่ำมาก

---

## ข้อ 43: ROC Curve และ Precision–Recall Curve ต่างกันอย่างไร

**คำตอบ**

ROC แสดง TPR เทียบกับ FPR ในหลาย Threshold และ AUC สรุปความสามารถในการจัดอันดับ ส่วน PR Curve แสดง Precision เทียบกับ Recall และเหมาะกว่าเมื่อ Positive Class พบได้น้อย เส้นฐานของ PR เท่ากับสัดส่วน Positive ไม่จำเป็นต้องเท่ากับ 0.5

---

## ข้อ 44: คำนวณ Accuracy, Precision และ Recall เมื่อ TP=3, FP=2, FN=1, TN=1

**คำตอบ**

$$
\mathrm{Accuracy}=\frac{3+1}{3+2+1+1}=\frac{4}{7}\approx0.571
$$

$$
\mathrm{Precision}=\frac{3}{3+2}=0.60
$$

$$
\mathrm{Recall}=\frac{3}{3+1}=0.75
$$

โมเดลจับ Positive จริงได้ 75% และในสิ่งที่แจ้งว่า Positive มีถูกจริง 60%

---

# หัวข้อที่ควรตอบให้ได้ก่อน

หากเวลาไม่พอ ให้ทบทวนตามลำดับนี้:

1. T–P–E และประเภทของ ML
2. MSE และ Normal Equation เทียบกับ Gradient Descent
3. Feature Scaling และ BGD–SGD–Mini-batch
4. Sigmoid, Threshold, Decision Boundary และ Cross-Entropy
5. Prior, Likelihood, Posterior และ Naive Assumption
6. Underfit–Overfit และ Ridge–Lasso–Elastic Net
7. Train–Validation–Test และ Bias–Variance
8. Confusion Matrix, Precision, Recall, F1 และ ROC/PR

# โครงเขียนตอบทฤษฎี

1. นิยามว่าแนวคิดคืออะไร
2. บอกปัญหาที่ต้องการแก้
3. อธิบายกลไกหรือส่วนประกอบ
4. เปรียบเทียบข้อดี ข้อจำกัด หรือผลของ Parameter
5. ยกตัวอย่างสั้น ๆ
