# เตรียมสอบกลางภาค Applied Machine Learning (DADS6003)

> ฉบับอ่านให้จบภายใน 1 วัน — เน้นทฤษฎีและการคำนวณพื้นฐานจาก Lecture 01–07

ข้อสอบมีแนวโน้มเป็นทฤษฎีเป็นส่วนใหญ่ เอกสารนี้จึงเน้นให้เรา **อธิบายเหตุผล เปรียบเทียบวิธี และตีความผลลัพธ์ได้** มากกว่าท่อง derivation ยาว ๆ เนื้อหาเรียงตามชื่อไฟล์ Lecture 01–07 แม้เลข Week หรือ Course Outline บางหน้าจะเรียงต่างกัน

---

## วิธีใช้เอกสารนี้ในวันนี้

อ่านตามลำดับ เพราะแต่ละบทต่อยอดจากบทก่อนหน้า หลังจบแต่ละบทให้ปิดเอกสารแล้วลองพูดสรุป 1–2 นาที ถ้าอธิบายไม่ได้จึงย้อนกลับไปอ่าน ไม่ควรเสียเวลาจำตัวเลขในตัวอย่างทุกตัว

แผนอ่านที่แนะนำ:

| รอบ | เนื้อหา | เวลาประมาณ |
|---|---|---:|
| 1 | ภาพรวม + บท 1 | 45 นาที |
| 2 | บท 2–3: Linear Regression | 90 นาที |
| 3 | บท 4–5: Classification | 90 นาที |
| 4 | บท 6–7: Regularization และ Evaluation | 90 นาที |
| 5 | คำนวณพื้นฐาน + คำถามท้ายเอกสาร | 60–90 นาที |
| 6 | ทบทวนเฉพาะจุดที่ยังอธิบายไม่ได้ | 45 นาที |

ลำดับความสำคัญในเอกสาร:

- **ต้องเข้าใจ:** แนวคิดที่ควรอธิบายได้โดยไม่เปิดเอกสาร
- **ควรคำนวณได้:** โจทย์สั้นที่ทำด้วยมือได้
- **อ่านผ่านก่อน:** รายละเอียดที่รู้ไว้ช่วยให้เข้าใจ แต่ไม่ควรใช้เวลามากในรอบแรก

---

## ภาพรวมทั้ง 7 บท

วิชานี้เริ่มจากคำถามว่า Machine Learning คืออะไร จากนั้นสร้างโมเดลที่ง่ายที่สุดคือ Linear Regression แล้วขยายให้รองรับหลาย feature และความสัมพันธ์แบบโค้ง เมื่อคำตอบเปลี่ยนจากตัวเลขเป็น class จึงเปลี่ยนไปใช้ Logistic Regression หรือ Naive Bayes หากโมเดลซับซ้อนเกินไปจะเกิด overfitting จึงใช้ Regularization และสุดท้ายต้องแบ่งข้อมูลกับเลือก metric ให้เหมาะเพื่อประเมินว่าโมเดลใช้กับข้อมูลใหม่ได้จริงหรือไม่

| บท | คำถามหลัก |
|---|---|
| 1 | ML ต่างจากโปรแกรมทั่วไปอย่างไร และโจทย์ ML ที่ดีต้องระบุอะไร |
| 2 | จะหาเส้นตรงที่ทำนายตัวเลขได้ดีที่สุดอย่างไร |
| 3 | ถ้ามีหลาย feature ข้อมูลต่างสเกล หรือความสัมพันธ์โค้ง จะทำอย่างไร |
| 4 | จะเปลี่ยนคะแนนเชิงเส้นให้เป็นความน่าจะเป็นและ class ได้อย่างไร |
| 5 | จะจำแนก class ด้วยกฎความน่าจะเป็นได้อย่างไร |
| 6 | จะลดการจำ training data มากเกินไปได้อย่างไร |
| 7 | จะเลือกและประเมินโมเดลโดยไม่หลอกตัวเองได้อย่างไร |

กรอบที่เชื่อมทุกบทคือ:

1. **Representation:** โมเดลมีรูปแบบอย่างไร
2. **Optimization:** หาพารามิเตอร์ที่เหมาะสมอย่างไร
3. **Evaluation:** ใช้อะไรวัดว่าโมเดลดีหรือไม่

---

# 1. Machine Learning Introduction

## 1.1 Traditional Programming ต่างจาก Machine Learning อย่างไร

โปรแกรมแบบเดิมรับ **ข้อมูลและกฎที่มนุษย์เขียน** แล้วให้คำตอบ เช่น ถ้ายอดซื้อเกิน 1,000 บาทให้ส่วนลด 10% ส่วน Machine Learning รับ **ข้อมูลและตัวอย่างคำตอบ** แล้วเรียนรู้กฎหรือโมเดลขึ้นมา เช่น เรียนจากรูปตัวเลขที่มี label เพื่อจำแนกรูปใหม่

ML ไม่ได้หมายความว่าไม่ต้องเขียนโปรแกรม แต่หมายความว่าเราไม่ต้องเขียนกฎตัดสินทุกกรณีด้วยตนเอง เรายังต้องเตรียมข้อมูล เลือก feature ฝึกโมเดล วัดผล และดูแลโมเดลหลังนำไปใช้

## 1.2 นิยาม T–P–E

Tom Mitchell อธิบายว่าโปรแกรมเรียนรู้จาก **Experience (E)** สำหรับ **Task (T)** ซึ่งวัดด้วย **Performance (P)** หากผลงานดีขึ้นเมื่อได้รับประสบการณ์เพิ่ม

ตัวอย่างการจำแนกลายมือ:

- **T:** จำแนกรูปว่าเป็นตัวเลขใด
- **E:** รูปลายมือที่มี label กำกับ
- **P:** สัดส่วนรูปที่จำแนกถูก

จุดสำคัญคือ P ต้องเหมาะกับงาน ไม่จำเป็นต้องเป็น Accuracy เสมอ เช่น ระบบตรวจโรคอาจให้ความสำคัญกับ Recall เพราะการพลาดผู้ป่วยมีต้นทุนสูง

## 1.3 ประเภทของ Machine Learning

**Supervised Learning** มีทั้ง input และคำตอบกำกับ หากคำตอบเป็นค่าตัวเลขต่อเนื่องเรียก Regression เช่น ราคาบ้าน หากคำตอบเป็นกลุ่มเรียก Classification เช่น spam หรือ not spam

**Unsupervised Learning** ไม่มีคำตอบกำกับ เป้าหมายคือหารูปแบบในข้อมูล เช่น Clustering, Dimensionality Reduction และ Anomaly Detection

**Reinforcement Learning** เรียนจาก state, action และ reward เพื่อหา policy ว่าในแต่ละสถานะควรทำอะไร

> จุดที่มักตอบผิด: Regression หรือ Classification ดูจากชนิดของ **คำตอบ $y$** ไม่ได้ดูจากชนิดของ feature

## 1.4 กระบวนการทำโครงการ ML

ก่อนเลือก algorithm ต้องเริ่มจากโจทย์ธุรกิจ ลักษณะข้อมูล ประเภทงาน และวิธีวัดผล จากนั้นจึงเก็บข้อมูล ทำความสะอาด ติด label สร้าง feature ฝึกโมเดล ประเมิน นำไปใช้ และเฝ้าติดตาม

กระบวนการนี้ไม่ใช่เส้นตรง ผลการประเมินอาจทำให้ต้องย้อนกลับไปแก้ข้อมูล feature หรือแม้แต่โจทย์ตั้งต้น

### คำตอบแบบเขียนสอบ

> Machine Learning คือการให้คอมพิวเตอร์เรียนรู้รูปแบบจากข้อมูลแทนการเขียนกฎทุกข้อโดยตรง โจทย์ที่ชัดเจนควรระบุ Task, Performance และ Experience ได้ครบ และการเลือก algorithm ควรเกิดหลังจากเข้าใจเป้าหมาย ข้อมูล และวิธีวัดความสำเร็จแล้ว

---

# 2. Single Variable Linear Regression

## 2.1 โมเดลกำลังทำอะไร

Linear Regression ใช้ทำนายค่าตัวเลขต่อเนื่องจาก feature โมเดลหนึ่งตัวแปรคือ

$$
h_\theta(x)=\theta_0+\theta_1x
$$

$\theta_0$ คือ intercept หรือค่าทำนายเมื่อ $x=0$ ส่วน $\theta_1$ คือ slope เมื่อ $x$ เพิ่มหนึ่งหน่วย ค่าทำนายเปลี่ยนไป $\theta_1$ หน่วย

คำว่า linear หมายถึงโมเดลเป็นผลรวมของพารามิเตอร์คูณ feature ไม่ได้หมายความว่าข้อมูลทุกอย่างในโลกต้องเป็นเส้นตรง

## 2.2 MSE วัดความผิดอย่างไร

$$
J(\theta)=\frac{1}{N}\sum_{i=1}^{N}(h_\theta(x_i)-y_i)^2
$$

ขั้นตอนคือทำนายแต่ละแถว ลบค่าจริง ยกกำลังสอง แล้วเฉลี่ย การยกกำลังสองทำให้ error บวกและลบไม่หักล้างกัน และลงโทษ error ขนาดใหญ่มากกว่า error ขนาดเล็ก

**ควรคำนวณได้:** ถ้าค่าจริงคือ $1,1,4$ และโมเดลทำนาย $3,3,3$ จะได้ squared errors เท่ากับ $4,4,1$ ดังนั้น MSE เท่ากับ $9/3=3$

## 2.3 หาค่าพารามิเตอร์ได้สองแนวทาง

**Normal Equation** คำนวณคำตอบโดยตรง ไม่ต้องกำหนด learning rate และไม่ต้องวนซ้ำ แต่มีปัญหาเมื่อเมทริกซ์หา inverse ไม่ได้ และคำนวณแพงเมื่อ feature จำนวนมาก วิธีเชิงตัวเลขมักใช้ pseudo-inverse แทน inverse ตรง ๆ

**Gradient Descent** เริ่มจากพารามิเตอร์ชุดหนึ่ง แล้วค่อย ๆ ปรับไปในทิศตรงข้ามกับ gradient เพราะ gradient ชี้ไปทางที่ cost เพิ่มเร็วที่สุด

$$
\theta_j^{t+1}=\theta_j^t-\eta\frac{\partial J}{\partial\theta_j}
$$

$\eta$ คือ learning rate ถ้าใหญ่เกินไปอาจก้าวข้ามจุดต่ำสุดและแกว่ง ถ้าเล็กเกินไปจะลู่เข้าช้า ทุกพารามิเตอร์ควรถูกคำนวณจากค่ารอบเดิมแล้วอัปเดตพร้อมกัน

| ประเด็น | Normal Equation | Gradient Descent |
|---|---|---|
| วิธี | คำนวณคำตอบโดยตรง | ปรับทีละรอบ |
| Hyperparameter | ไม่ต้องมี learning rate | ต้องเลือก learning rate และจำนวนรอบ |
| Feature scaling | ไม่จำเป็นต่อการหาคำตอบ | ช่วยให้ลู่เข้าเร็วและสมดุล |
| Feature จำนวนมาก | คำนวณเมทริกซ์แพง | เหมาะกว่า |
| ปัญหา inverse | อาจพบ | ไม่มี |

> หมายเหตุ: ตาราง complexity ในสไลด์เป็นภาพรวมแบบย่อ ไม่ควรจำ $O(n^2)$ กับ $O(n^3)$ โดยไม่ระบุ algorithm และมิติของข้อมูล

### คำตอบแบบเขียนสอบ

> Linear Regression หาเส้นที่ทำให้ MSE ต่ำที่สุด Normal Equation หาคำตอบโดยตรงและไม่ต้องกำหนด learning rate แต่มีต้นทุนสูงเมื่อ feature มากและอาจมีปัญหา inverse ส่วน Gradient Descent ปรับพารามิเตอร์ซ้ำไปในทิศที่ลด cost จึงรองรับ feature มากกว่า แต่ต้องเลือก learning rate และอาจต้องทำ feature scaling

---

# 3. Multiple Linear Regression และ Polynomial Regression

## 3.1 หลาย feature เปลี่ยนอะไร

เมื่อค่าที่ต้องการทำนายขึ้นกับหลายปัจจัย โมเดลจะเป็น

$$
h_\theta(x)=\theta_0+\theta_1x_1+\cdots+\theta_dx_d=\theta^Tx
$$

แต่ละ coefficient แสดงผลของ feature นั้นต่อค่าทำนาย **เมื่อควบคุม feature อื่นให้คงที่** Cost function ยังเป็น MSE และหลักของ Gradient Descent ยังเหมือนบท 2

## 3.2 ทำไมต้อง Feature Scaling

หาก feature หนึ่งอยู่หลักพันแต่อีก feature อยู่หลักหน่วย gradient ของพารามิเตอร์จะมีขนาดต่างกันมาก การใช้ learning rate เดียวกันจึงทำให้ Gradient Descent เดินไม่สมดุล

**Min-Max Scaling** มักแปลงข้อมูลฝึกให้อยู่ช่วง 0–1:

$$
x'=\frac{x-x_{min}}{x_{max}-x_{min}}
$$

**Z-score Standardization** ทำให้ข้อมูลฝึกมีค่าเฉลี่ยประมาณ 0 และส่วนเบี่ยงเบนมาตรฐานประมาณ 1:

$$
x'=\frac{x-\mu}{\sigma}
$$

ค่าของ $x_{min}$, $x_{max}$, $\mu$ และ $\sigma$ ต้องคำนวณจาก training set แล้วนำค่าเดิมไปใช้กับ validation/test เพื่อป้องกัน data leakage

Feature Scaling ไม่ได้สร้างข้อมูลใหม่และไม่ได้รับประกันว่าโมเดลจะแม่นขึ้นทุกครั้ง หน้าที่หลักคือช่วยกระบวนการ optimization โดยเฉพาะวิธีที่ไวต่อสเกล

## 3.3 BGD, SGD และ Mini-batch

| วิธี | ข้อมูลที่ใช้ต่อหนึ่ง update | ข้อดี | ข้อจำกัด |
|---|---:|---|---|
| Batch GD | ทั้ง training set | ทิศทางเสถียร | หนึ่ง update ช้าเมื่อข้อมูลมาก |
| SGD | 1 แถว | update เร็วและบ่อย | เส้นทางแกว่งมาก |
| Mini-batch GD | กลุ่มเล็ก $b$ แถว | สมดุลและคำนวณแบบ vectorized ได้ | ต้องเลือก batch size |

Learning Rate Scheduling ช่วยลดความแกว่งโดยใช้ก้าวใหญ่ในช่วงต้นและค่อย ๆ ลดขนาดก้าวเมื่อเข้าใกล้คำตอบ

## 3.4 Polynomial Regression

ถ้าความสัมพันธ์โค้ง เส้นตรงธรรมดาอาจ underfit เราจึงสร้าง feature ใหม่ เช่น $x^2$ หรือ $x_1x_2$

$$
h_\theta(x)=\theta_0+\theta_1x_1+\theta_2x_2+\theta_3x_1x_2+\theta_4x_1^2+\theta_5x_2^2
$$

กราฟของโมเดลอาจโค้ง แต่ยังเรียกว่า linear model เพราะยังเป็น linear ในพารามิเตอร์ $\theta$ พจน์ $x_1x_2$ คือ interaction ซึ่งเปิดให้ผลของ feature หนึ่งสัมพันธ์กับอีก feature

ความยืดหยุ่นที่เพิ่มขึ้นช่วยลด underfitting แต่ดีกรีสูงเกินไปทำให้โมเดลไล่ตาม noise และเกิด overfitting ซึ่งนำไปสู่บท Regularization และ Model Evaluation

### คำตอบแบบเขียนสอบ

> Feature Scaling ทำให้ feature มีสเกลใกล้กัน จึงช่วยให้ Gradient Descent ปรับพารามิเตอร์อย่างสมดุล Polynomial Regression เพิ่มพจน์กำลังและ interaction เพื่อจับความสัมพันธ์โค้ง แต่ถ้าเพิ่มดีกรีมากเกินไป โมเดลอาจ overfit

---

# 4. Logistic Regression

## 4.1 ทำไม Linear Regression ไม่เหมาะกับ Classification

Linear Regression ให้ผลได้ตั้งแต่ลบอนันต์ถึงบวกอนันต์ จึงตีความเป็นความน่าจะเป็นไม่ได้ Logistic Regression เริ่มจากคะแนนเชิงเส้น

$$
z=\theta^Tx
$$

แล้วใช้ Sigmoid บีบคะแนนให้อยู่ระหว่าง 0 กับ 1

$$
\hat{p}=\sigma(z)=\frac{1}{1+e^{-z}}
$$

$\hat{p}$ คือความน่าจะเป็นที่ตัวอย่างอยู่ใน class 1 หากใช้ threshold 0.5 จะทำนาย class 1 เมื่อ $\hat{p}\geq0.5$ และ class 0 เมื่อ $\hat{p}<0.5$

> Sigmoid เปลี่ยนคะแนนเป็นความน่าจะเป็น ส่วน threshold เปลี่ยนความน่าจะเป็นเป็น class

## 4.2 Decision Boundary

Decision Boundary คือตำแหน่งที่โมเดลเปลี่ยนคำตอบระหว่างสอง class เมื่อ threshold เท่ากับ 0.5 จุด boundary จะเกิดที่ $\theta^Tx=0$

- มี feature เดียว: boundary เป็นจุดบนเส้นจำนวน
- มีสอง feature เชิงเส้น: boundary เป็นเส้นตรง
- มี polynomial features: boundary อาจเป็นเส้นโค้งหรือวงกลม

ความโค้งมาจาก polynomial features ไม่ได้เกิดจาก Sigmoid โดยตรง

## 4.3 ทำไมใช้ Cross-Entropy

MSE ไม่เหมาะกับ Logistic Regression เพราะเมื่อนำ Sigmoid ซ้อนอยู่ข้างใน รูปร่างของ cost และ gradient ไม่เอื้อต่อการ optimization เท่า Cross-Entropy

สำหรับหนึ่งตัวอย่าง:

- ถ้า $y=1$ ใช้ $-\ln(\hat{p})$
- ถ้า $y=0$ ใช้ $-\ln(1-\hat{p})$

รวมเป็น

$$
J(\theta)=-\frac{1}{N}\sum_{i=1}^{N}[y_i\ln(\hat{p}_i)+(1-y_i)\ln(1-\hat{p}_i)]
$$

Cross-Entropy ลงโทษสูงเมื่อโมเดลมั่นใจแต่ตอบผิด เช่น ค่าจริงเป็น 1 แต่ให้ความน่าจะเป็นใกล้ 0

**อ่านผ่านก่อน:** Derivation เต็มของ gradient ไม่จำเป็นต่อการอ่านรอบแรก สิ่งที่ควรรู้คือหลังย่อแล้ว gradient มีรูป $(\hat{p}-y)x$ คล้ายกับ Linear Regression แต่ใช้ prediction และ loss คนละแบบ

### Linear เทียบกับ Logistic Regression

| ประเด็น | Linear | Logistic |
|---|---|---|
| งาน | Regression | Classification |
| Output | จำนวนจริง | Probability 0–1 แล้วตัดเป็น class |
| Model | $\theta^Tx$ | $\sigma(\theta^Tx)$ |
| Loss | MSE | Cross-Entropy |
| Metric ตัวอย่าง | MSE, MAE, $R^2$ | Accuracy, Precision, Recall, F1, AUC |

---

# 5. Naive Bayes Classification

## 5.1 กฎของ Bayes กำลังย้อนคำถาม

เรามักทราบว่า “ถ้าเป็น class นี้ จะพบ feature แบบใดบ่อย” แต่สิ่งที่ต้องการทำนายคือ “เมื่อเห็น feature แบบนี้ น่าจะเป็น class ใด” Bayes' Rule ใช้กลับทิศของเงื่อนไข:

$$
P(Y\mid X)=\frac{P(X\mid Y)P(Y)}{P(X)}
$$

- **Prior $P(Y)$:** ความเชื่อหรือสัดส่วนของ class ก่อนเห็นข้อมูลใหม่
- **Likelihood $P(X\mid Y)$:** โอกาสพบ feature นี้เมื่อทราบ class
- **Evidence $P(X)$:** โอกาสพบข้อมูลนี้ในประชากรทั้งหมด
- **Posterior $P(Y\mid X)$:** ความน่าจะเป็นของ class หลังเห็น feature

หากต้องการเลือก class เพียงอย่างเดียว $P(X)$ เหมือนกันทุก class จึงเปรียบเทียบเฉพาะ $P(X\mid Y)P(Y)$ ได้

## 5.2 ทำไมต้องมีคำว่า Naive

เมื่อมีหลาย feature การคำนวณ joint probability ต้องใช้ข้อมูลจำนวนมาก Naive Bayes จึงสมมติว่า feature เป็น **conditionally independent เมื่อทราบ class แล้ว**

$$
P(X\mid Y)=P(x_1\mid Y)P(x_2\mid Y)\cdots P(x_d\mid Y)
$$

สมมติฐานนี้มักไม่จริงทั้งหมด แต่ทำให้โมเดลฝึกเร็ว ใช้ข้อมูลน้อย และเหมาะกับงานอย่าง text classification ข้อจำกัดคือ feature ที่สัมพันธ์กันมากอาจทำให้โมเดลนับหลักฐานซ้ำ

## 5.3 Continuous Feature และ Zero Probability

feature แบบ category คำนวณ likelihood จากการนับ ส่วน feature ต่อเนื่องสามารถสมมติการแจกแจง เช่น Gaussian แล้วใช้ค่าเฉลี่ยและความแปรปรวนแยกตาม class

ถ้าค่าหนึ่งไม่เคยปรากฏใน training data likelihood จะเป็นศูนย์ และเมื่อคูณกับพจน์อื่นจะทำให้คะแนนทั้ง class เป็นศูนย์ **Laplace Smoothing** แก้โดยบวกค่าจำนวนน้อยให้ทุก category ก่อนคำนวณ

ตัวอย่าง หากมี 1,000 ตัวอย่างและ Income มี 3 กลุ่ม แต่ `low` ไม่เคยปรากฏ:

$$
P(\text{low})=\frac{0+1}{1000+3}=\frac{1}{1003}
$$

## 5.4 ข้อผิดพลาดในตัวอย่างสไลด์

ตัวอย่างหลาย feature ในสไลด์คำนวณคะแนน Male เท่ากับ 0.0092 และ Female เท่ากับ 0.012 ดังนั้น posterior ของ Female สูงกว่า แต่สไลด์เขียน Final answer เป็น Male หากข้อสอบใช้ตัวเลขเดียวกัน ควรแสดงการคำนวณและเลือก Female ตามค่าที่สูงกว่า

### Logistic Regression เทียบกับ Naive Bayes

Logistic Regression เรียนเส้นแบ่ง class โดยตรงและให้ probability ผ่าน Sigmoid ส่วน Naive Bayes สร้างคะแนนจาก Prior และ Likelihood ภายใต้สมมติฐาน conditional independence ทั้งคู่ทำ classification แต่หลักคิดต่างกัน

---

# 6. Regularization

## 6.1 Underfit, Good Fit และ Overfit

**Underfitting** เกิดเมื่อโมเดลง่ายเกินไปจนจับรูปแบบหลักไม่ได้ จึงผิดทั้ง training และ validation เรียกว่า high bias

**Overfitting** เกิดเมื่อโมเดลซับซ้อนจนจับทั้งรูปแบบจริงและ noise ของ training data ทำให้ training error ต่ำแต่ validation/test error สูง เรียกว่า high variance

Good fit คือสมดุลระหว่างสองด้าน ไม่ได้หมายความว่าต้องทำให้ training error ต่ำที่สุด

วิธีลด overfitting ได้แก่ เพิ่มข้อมูล ลด feature ลดความซับซ้อน หรือใช้ Regularization

## 6.2 แนวคิดของ Regularization

Regularization เพิ่มค่าปรับเข้าไปใน loss เพื่อไม่ให้ coefficient มีขนาดใหญ่โดยไม่จำเป็น โมเดลจึงต้องแลกระหว่างการ fit ข้อมูลกับการรักษาความเรียบง่าย

$\lambda$ ควบคุมความแรงของค่าปรับ:

- $\lambda$ ต่ำ: โมเดลมีอิสระสูง เสี่ยง variance สูง
- $\lambda$ สูง: coefficient ถูกหดมากขึ้น variance ลดแต่ bias เพิ่ม
- สูงเกินไป: โมเดล underfit

## 6.3 Ridge, Lasso และ Elastic Net

**Ridge หรือ L2** เพิ่มผลรวม coefficient ยกกำลังสอง:

$$
J(\theta)=\text{MSE}+\lambda\sum_{j=1}^{d}\theta_j^2
$$

Ridge หด coefficient ทุกตัวเข้าหาศูนย์ แต่มักไม่ทำให้เป็นศูนย์พอดี เหมาะเมื่อหลาย feature มีส่วนช่วยทำนาย หรือ feature มีความสัมพันธ์กัน

**Lasso หรือ L1** เพิ่มผลรวมค่าสัมบูรณ์:

$$
J(\theta)=\text{MSE}+\lambda\sum_{j=1}^{d}|\theta_j|
$$

Lasso สามารถทำให้ coefficient บางตัวเป็นศูนย์ จึงใช้เป็น feature selection ได้ เหมาะเมื่อเชื่อว่ามี feature สำคัญเพียงบางส่วน

**Elastic Net** ผสม L1 และ L2 เพื่อให้ได้ทั้งการหด coefficient และการเลือก feature พร้อมลดข้อจำกัดของ Lasso เมื่อ feature สัมพันธ์กันมาก

| วิธี | ผลต่อ coefficient | ภาพจำ |
|---|---|---|
| Ridge | ทุกตัวเล็กลง แต่มักไม่เป็นศูนย์ | เก็บทุก feature แต่ลดอิทธิพล |
| Lasso | บางตัวเป็นศูนย์ | เลือก feature |
| Elastic Net | ผสมสองแบบ | เลือกบางตัวและจัดการกลุ่ม feature ที่สัมพันธ์กัน |

> ระวังนิยามพารามิเตอร์ผสม: สไลด์กำหนด $\alpha=1$ เป็น Ridge และ $\alpha=0$ เป็น Lasso แต่นิยาม `l1_ratio` ของ software หลายตัวใช้ทิศตรงกันข้าม จึงต้องดูสูตรของเครื่องมือก่อนเสมอ

**อ่านผ่านก่อน:** เราไม่จำเป็นต้องไล่ SGD update หรือ sub-gradient ของ Lasso ในรอบแรก ให้เข้าใจว่าค่าปรับเปลี่ยน gradient เพื่อดึง coefficient เข้าหาศูนย์

### คำตอบแบบเขียนสอบ

> Regularization ลด overfitting โดยเพิ่มค่าปรับตามขนาด coefficient เข้าไปใน loss Ridge ใช้ L2 และหด coefficient ทุกตัว ส่วน Lasso ใช้ L1 และทำให้บาง coefficient เป็นศูนย์ได้ Elastic Net ผสมทั้งสองแบบ ค่า $\lambda$ ที่สูงขึ้นลด variance แต่เพิ่ม bias จึงต้องเลือกให้สมดุล

---

# 7. Model Training and Evaluation

## 7.1 ทำไม Training Error อย่างเดียวไม่พอ

โมเดลที่ซับซ้อนมักทำ training error ต่ำ แต่เป้าหมายจริงคือทำงานกับข้อมูลใหม่ จึงต้องกันข้อมูลที่ไม่ได้ใช้ฝึกไว้ประเมิน generalization

**Hold-out 80/20** แบ่ง Train และ Test ง่ายและเร็ว แต่ผลขึ้นกับการสุ่มครั้งเดียว หากทดลองหลายโมเดลแล้วเลือกจาก Test ซ้ำ ๆ เราจะ overfit กับ Test set

**Train–Validation–Test 60/20/20** ใช้ Train หาพารามิเตอร์ ใช้ Validation เลือกโมเดลหรือ hyperparameter และใช้ Test ประเมินครั้งสุดท้าย

> สไลด์เรียกการแบ่ง 60/20/20 ว่า Cross Validation แต่ตามศัพท์มาตรฐานนี่คือ hold-out แบบสามชุด ส่วน k-fold cross-validation จะหมุนเวียน validation หลายรอบ ในข้อสอบให้เข้าใจทั้งคำที่สไลด์ใช้และความหมายมาตรฐาน

หลักสำคัญคือ Test set ต้องไม่ถูกใช้ตัดสินใจระหว่างพัฒนาโมเดล หากใช้เลือกดีกรี polynomial หรือ $\lambda$ แล้ว ผล Test จะไม่เป็นการประเมินที่เป็นกลางอีกต่อไป

## 7.2 Bias–Variance Diagnosis

| อาการ | Training Error | Validation Error | ปัญหา |
|---|---:|---:|---|
| ทั้งคู่สูง | สูง | สูง | High Bias / Underfit |
| Train ต่ำ แต่ Validation สูง | ต่ำ | สูง | High Variance / Overfit |
| ทั้งคู่ต่ำและใกล้กัน | ต่ำ | ต่ำ | Generalize ได้ดี |

แนวทางแก้:

| วิธี | ช่วยแก้โดยทั่วไป |
|---|---|
| เพิ่ม training data | High Variance |
| ลดจำนวน feature หรือความซับซ้อน | High Variance |
| เพิ่ม $\lambda$ | High Variance |
| เพิ่ม useful features | High Bias |
| เพิ่ม polynomial features | High Bias |
| ลด $\lambda$ | High Bias |

จำเป็นหลัก: ทำให้โมเดลยืดหยุ่นขึ้นช่วยลด bias; ทำให้โมเดลเรียบง่ายขึ้นช่วยลด variance

## 7.3 Confusion Matrix

|  | Actual Positive | Actual Negative |
|---|---:|---:|
| Predicted Positive | TP | FP |
| Predicted Negative | FN | TN |

- **TP:** ทำนาย positive และจริงเป็น positive
- **FP:** ทำนาย positive แต่จริงเป็น negative
- **FN:** ทำนาย negative แต่จริงเป็น positive
- **TN:** ทำนาย negative และจริงเป็น negative

คำว่า positive หมายถึง class ที่เราสนใจตรวจจับ ไม่ได้หมายความว่าเป็นสิ่งดีเสมอไป

## 7.4 Accuracy, Precision, Recall และ F1

$$
\text{Accuracy}=\frac{TP+TN}{TP+TN+FP+FN}
$$

Accuracy ตอบว่าทายถูกทั้งหมดกี่ส่วน แต่หลอกได้เมื่อ class ไม่สมดุล เช่น ข้อมูลป่วยเพียง 1% โมเดลที่ตอบไม่ป่วยทุกคนจะได้ Accuracy 99% ทั้งที่จับผู้ป่วยไม่ได้เลย

$$
\text{Precision}=\frac{TP}{TP+FP}
$$

Precision ตอบว่า “ในสิ่งที่โมเดลเตือนว่า positive ถูกจริงกี่ส่วน” เหมาะเมื่อ FP มีต้นทุนสูง เช่น ส่งเคสไปตรวจราคาแพง

$$
\text{Recall}=\frac{TP}{TP+FN}
$$

Recall ตอบว่า “ใน positive จริงทั้งหมด โมเดลจับได้กี่ส่วน” เหมาะเมื่อ FN มีต้นทุนสูง เช่น พลาดผู้ป่วยโรคร้าย

$$
F_1=\frac{2PR}{P+R}
$$

F1 เป็น harmonic mean จึงสูงได้เมื่อ Precision และ Recall ดีทั้งคู่ ไม่ยอมให้ค่าที่สูงมากชดเชยอีกค่าที่ต่ำมากเหมือน arithmetic mean

**ควรคำนวณได้:** ถ้า TP=3, FP=2, FN=1, TN=1 จะได้ Accuracy $=4/7$, Precision $=3/5$ และ Recall $=3/4$

## 7.5 Sensitivity, Specificity และ FPR

Sensitivity หรือ TPR คือ Recall ส่วน Specificity วัดว่าในกลุ่ม negative จริง โมเดลทายถูกกี่ส่วน

$$
\text{Specificity}=\frac{TN}{TN+FP}
$$

$$
\text{FPR}=\frac{FP}{FP+TN}=1-\text{Specificity}
$$

## 7.6 ROC และ Precision–Recall Curve

metric จาก Confusion Matrix ขึ้นกับ threshold หากเปลี่ยน threshold จำนวน TP, FP, FN และ TN จะเปลี่ยน

**ROC Curve** แสดง TPR เทียบกับ FPR ในหลาย threshold เส้นที่เข้าใกล้มุมซ้ายบนดีกว่า AUC สรุปความสามารถในการจัดอันดับ positive เหนือ negative โดย 0.5 ใกล้การสุ่ม และ 1 คือแยกได้สมบูรณ์

**Precision–Recall Curve** แสดง Precision เทียบกับ Recall เมื่อเปลี่ยน threshold เหมาะกับข้อมูลที่ positive พบได้น้อย เพราะเน้น performance ของ class ที่สนใจโดยตรง เส้นฐานของ PR เท่ากับสัดส่วน positive ในข้อมูล ไม่ได้เท่ากับ 0.5 เสมอไป

### คำตอบแบบเขียนสอบ

> Accuracy อย่างเดียวไม่พอเมื่อ class ไม่สมดุล เพราะโมเดลอาจทาย class ใหญ่ทั้งหมดแล้วได้ Accuracy สูง Precision วัดความน่าเชื่อถือของการเตือน ส่วน Recall วัดความสามารถในการจับ positive จริง F1 ใช้เมื่อต้องการสมดุลสองค่า และการเลือก metric ต้องขึ้นกับต้นทุนของ FP กับ FN

---

# ตารางเชื่อมโยงที่ต้องจำ

## โมเดลหลัก

| ประเด็น | Linear Regression | Logistic Regression | Naive Bayes |
|---|---|---|---|
| งาน | ทำนายตัวเลข | จำแนก class | จำแนก class |
| หลักการ | ผลรวมเชิงเส้น | ผลรวมเชิงเส้นผ่าน Sigmoid | Prior คูณ Likelihood |
| Loss/การเรียน | ลด MSE | ลด Cross-Entropy | ประมาณ probability จากข้อมูล |
| สมมติฐานเด่น | ความสัมพันธ์ตามรูปโมเดล | log-odds เป็นเชิงเส้นกับ feature | feature independent เมื่อทราบ class |
| จุดเด่น | เข้าใจง่าย | เส้นแบ่งและ probability ตีความได้ | เร็วและใช้ข้อมูลไม่มาก |

## คู่เปรียบเทียบที่มีโอกาสใช้เขียนตอบ

| คู่ | ประเด็นที่ต้องพูด |
|---|---|
| Supervised / Unsupervised / Reinforcement | มี label / ไม่มี label / เรียนจาก reward |
| Normal Equation / Gradient Descent | คำตอบตรง / ทำซ้ำ; inverse / learning rate |
| Min-Max / Z-score | ช่วง 0–1 / ค่าเฉลี่ย 0 และ SD 1 |
| BGD / SGD / Mini-batch | ทุกแถว / 1 แถว / กลุ่มเล็ก |
| Linear / Logistic | ตัวเลขไม่จำกัด / probability ผ่าน Sigmoid |
| Logistic / Naive Bayes | เรียน boundary / สร้าง posterior จาก probability |
| Ridge / Lasso / Elastic Net | หดทุกตัว / ทำบางตัวเป็นศูนย์ / ผสมสองแบบ |
| High Bias / High Variance | ง่ายเกินไป / จำข้อมูลฝึกมากเกินไป |
| Precision / Recall | ความน่าเชื่อถือของการเตือน / จับ positive จริงได้ครบแค่ไหน |
| ROC / PR | TPR–FPR / Precision–Recall; PR เหมาะเมื่อ positive หายาก |

---

# การคำนวณพื้นฐานที่ควรทำได้

## 1. MSE

ค่าจริง $1,1,4$ และค่าทำนาย $1,3,4$

$$
\text{MSE}=\frac{(1-1)^2+(3-1)^2+(4-4)^2}{3}=\frac{4}{3}
$$

## 2. Min-Max Scaling

ถ้า $x=30$, ค่าต่ำสุด 10 และค่าสูงสุด 50:

$$
x'=\frac{30-10}{50-10}=0.5
$$

## 3. Z-score

ถ้า $x=70$, ค่าเฉลี่ย 50 และ SD เท่ากับ 10:

$$
z=\frac{70-50}{10}=2
$$

แปลว่าค่านี้สูงกว่าค่าเฉลี่ย 2 ส่วนเบี่ยงเบนมาตรฐาน

## 4. Sigmoid และ Threshold

ถ้า $z=0$ จะได้

$$
\sigma(0)=\frac{1}{1+e^0}=0.5
$$

เมื่อ threshold เท่ากับ 0.5 จุด $z=0$ จึงอยู่บน Decision Boundary

## 5. Naive Bayes

สำหรับแต่ละ class ให้คำนวณ

$$
\text{score}=P(Y)\prod_jP(x_j\mid Y)
$$

แล้วเลือก class ที่ score สูงกว่า หากโจทย์ขอ posterior จึงนำ score ของแต่ละ class หารด้วยผลรวม score ทุก class

## 6. Confusion Matrix

เขียน TP, FP, FN, TN ให้ครบก่อนแทนสูตร และตรวจว่าผลรวมทั้งสี่ช่องเท่ากับจำนวนข้อมูลทั้งหมด

---

# คำถามทบทวนก่อนสอบ

ลองตอบออกเสียงโดยไม่เปิดเอกสาร หากตอบไม่ได้ให้ย้อนกลับไปอ่านเฉพาะหัวข้อนั้น

1. ML ต่างจาก Traditional Programming อย่างไร และ T–P–E คืออะไร
2. Regression ต่างจาก Classification โดยดูจากสิ่งใด
3. MSE ทำงานอย่างไร และเหตุใดต้องยกกำลังสอง
4. Normal Equation และ Gradient Descent ต่างกันอย่างไร
5. ทำไม Gradient Descent จึงต้องสนใจ Feature Scaling และ Learning Rate
6. BGD, SGD และ Mini-batch ต่างกันอย่างไร
7. Polynomial Regression ช่วยอะไร และสร้างความเสี่ยงอะไร
8. Sigmoid, Threshold และ Decision Boundary ทำหน้าที่ต่างกันอย่างไร
9. ทำไม Logistic Regression ใช้ Cross-Entropy แทน MSE
10. Prior, Likelihood, Evidence และ Posterior คืออะไร
11. สมมติฐาน Naive คืออะไร และ Laplace Smoothing แก้ปัญหาใด
12. Underfit และ Overfit สังเกตจาก Train/Validation Error อย่างไร
13. Ridge, Lasso และ Elastic Net ต่างกันอย่างไร
14. เพิ่มหรือลด $\lambda$ ส่งผลต่อ Bias และ Variance อย่างไร
15. Train, Validation และ Test มีหน้าที่ต่างกันอย่างไร
16. ทำไม Accuracy สูงจึงยังไม่ได้แปลว่าโมเดลดี
17. Precision กับ Recall ควรเลือกเน้นค่าใดในสถานการณ์ใด
18. ROC และ PR Curve ต่างกันอย่างไร

## โครงเขียนตอบทฤษฎี

เมื่อเจอคำถามอธิบายหรือเปรียบเทียบ ให้เขียนตามลำดับนี้:

1. นิยามว่าแนวคิดนั้นคืออะไร
2. บอกปัญหาที่ต้องการแก้
3. อธิบายกลไกหรือส่วนประกอบสำคัญ
4. เปรียบเทียบข้อดี ข้อจำกัด หรือผลจากการปรับ parameter
5. ยกตัวอย่างสั้น ๆ

ตัวอย่าง “ทำไมต้อง Feature Scaling”:

> Feature ที่มีสเกลต่างกันมากทำให้ gradient ของพารามิเตอร์แต่ละตัวมีขนาดไม่สมดุล เมื่อใช้ learning rate เดียวกัน Gradient Descent อาจแกว่งหรือใช้เวลาลู่เข้านาน Feature Scaling จึงปรับ feature ให้อยู่ในช่วงใกล้กัน เช่น Min-Max หรือ Z-score เพื่อช่วยให้ optimization ทำงานสมดุลขึ้น

---

# จุดคลาดเคลื่อนในสไลด์ที่ควรรู้

1. Course Outline วาง Naive Bayes ก่อน Logistic Regression แต่เอกสารนี้เรียงตามชื่อไฟล์ 04 Logistic และ 05 Naive Bayes
2. ตัวอย่าง Naive Bayes เขียนคำตอบ Male แต่ตัวเลขให้ Female สูงกว่า
3. Decision Boundary รูปวงกลมมี label ด้านในไม่ตรงกับสมการ
4. Inverse Time Decay ตัวอย่างควรได้ประมาณ 0.00999
5. สูตร Ridge SGD ในสไลด์ลงโทษ intercept แต่ Cost Function ไม่รวม intercept
6. ภาพ Tumor Detection เขียน Predicted Area เป็น Negative ทั้งที่บริบทน่าจะเป็น Positive
7. สไลด์เรียกการแบ่ง 60/20/20 ว่า Cross Validation แต่ตามมาตรฐานคือ Train–Validation–Test Split
8. นิยาม $\alpha$ ของ Elastic Net ในสไลด์ไม่ควรนำไปเท่ากับ `l1_ratio` ของ software โดยไม่ตรวจสูตร

---

# เช้าวันสอบควรทบทวนอะไร

ยังไม่ต้องสร้าง Cheat Sheet จากส่วนนี้จนกว่าจะอ่านเนื้อหาครบ วันนี้ให้ทำเครื่องหมายเฉพาะเรื่องที่ยังจำไม่ได้ พรุ่งนี้ก่อนสอบให้ทบทวน:

- ตารางเปรียบเทียบโมเดลและคู่แนวคิด
- สูตร MSE, Scaling, Sigmoid, Bayes, Accuracy, Precision, Recall และ F1
- วิธีวินิจฉัย High Bias กับ High Variance
- ความแตกต่าง Ridge, Lasso และ Elastic Net
- หน้าที่ของ Train, Validation และ Test
- ต้นทุนของ FP และ FN ในโจทย์สถานการณ์

หลังอ่านฉบับนี้ครบแล้ว จึงค่อยเลือกเฉพาะสิ่งที่จำยากและมีโอกาสใช้ตอบสอบมาจัดลง A4 หน้า–หลัง เพื่อให้กระดาษนั้นเป็นเครื่องมือเตือนความจำ ไม่ใช่การย่อเอกสารทั้งเล่มลงในพื้นที่เล็กเกินไป
