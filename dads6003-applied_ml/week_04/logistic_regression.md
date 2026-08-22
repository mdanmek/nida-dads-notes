# DADS6003 Applied Machine Learning — Logistic Regression

> **แหล่งเนื้อหาหลัก:** `dads6003_week4_logistic_regression.pdf` จำนวน 17 หน้า  
> **ผู้สอนในเอกสาร:** Ekarat Rattagan  
> **วันที่ในเอกสาร:** 29 มกราคม 2026  
> **หมายเหตุ:** ชื่อไฟล์และ destination ระบุ Week 04 แต่หน้าปก/ส่วนท้ายของสไลด์ระบุ “Week 5: Logistic Regression” โน้ตนี้ใช้ path Week 04 ตามที่ผู้ใช้กำหนดโดยไม่แก้ข้อมูลต้นฉบับ

## 1. ภาพรวมบทเรียน

Logistic Regression เป็นแบบจำลองสำหรับ **classification** แม้ชื่อจะมีคำว่า Regression หลักการคือเริ่มจาก linear score

$$
z=\boldsymbol{\theta}^{T}\mathbf{x}
$$

แล้วใช้ sigmoid function แปลงค่าที่อยู่ในช่วง \((-∞,+∞)\) ให้เป็น probability ในช่วง \((0,1)\):

$$
h_{\theta}(\mathbf{x})
=\sigma(z)
=\frac{1}{1+e^{-z}}
$$

จาก probability จึงใช้ threshold เช่น 0.5 เพื่อเปลี่ยนเป็น class prediction โมเดลถูก train ด้วย Negative Log-Likelihood หรือ Binary Cross-Entropy ไม่ใช้ MSE เป็นตัวเลือกมาตรฐาน

```mermaid
flowchart LR
    A["Features x"] --> B["Linear score z"]
    B --> C["Sigmoid"]
    C --> D["Probability p"]
    D --> E["Threshold"]
    E --> F["Class 0/1"]
```

## 2. Learning Objectives

หลังเรียนบทนี้ควรสามารถ:

- อธิบายว่า Logistic Regression เหมาะกับปัญหาใด
- คำนวณ sigmoid จาก linear score ได้
- แปลงระหว่าง probability, odds และ log-odds ได้
- ตีความ coefficient และ odds ratio ได้
- หา decision boundary จากสมการโมเดลและ threshold ได้
- อธิบาย linear และ nonlinear decision boundary ได้
- คำนวณ Negative Log-Likelihood/Binary Cross-Entropy ได้
- derive gradient ของ Logistic Regression ด้วย chain rule ได้
- อธิบายเหตุที่ gradient มีรูป \((\hat{y}-y)x_j\) คล้าย Linear Regression ได้
- เปรียบเทียบ Linear กับ Logistic Regression ด้าน representation, cost, metrics และ output ได้
- เลือก threshold และ evaluation metric ตามต้นทุนของ FP/FN ได้
- อธิบาย class imbalance, probability calibration และ regularization เบื้องต้นได้

## 3. Logistic Regression ใช้ทำอะไร

จากเอกสารหน้า 2 Logistic Regression ใช้กับ binary/multiclass classification และให้ผลลัพธ์เป็น probability ในช่วง \((0,1)\) ตัวอย่างได้แก่ cancer prediction, churn prediction และ employee attrition prediction

### 3.1 Binary classification

ในบทนี้เน้นกรณี

$$
y\in\{0,1\}
$$

โดยมักเรียก \(y=1\) ว่า positive class และ \(y=0\) ว่า negative class เช่น:

- \(1\): เป็น fraud, \(0\): ไม่เป็น fraud
- \(1\): churn, \(0\): ไม่ churn
- \(1\): เป็นโรค, \(0\): ไม่เป็นโรค

การกำหนด positive class มีผลต่อความหมายของ precision, recall และ odds ratio จึงต้องประกาศให้ชัด

### 3.2 Multiclass

สไลด์กล่าวว่าใช้กับ multiclass ได้ แต่สมการ NLL ในบทนี้เป็น Bernoulli/binary form สำหรับหลาย class สามารถขยายด้วย:

- One-vs-Rest: ฝึก binary classifier หนึ่งตัวต่อ class
- Multinomial Logistic Regression: ใช้ softmax สร้าง probability รวมกันเป็น 1

## 4. ทำไมไม่ใช้ Linear Regression ทำนาย Probability โดยตรง

จากเอกสารหน้า 3 Linear Regression มี output ไม่จำกัด:

$$
h_{\theta}(\mathbf{x})=\boldsymbol{\theta}^{T}\mathbf{x}
\in(-∞,+∞)
$$

แต่ probability ต้องอยู่ระหว่าง 0 และ 1 หากใช้เส้นตรงอาจทำนาย -0.3 หรือ 1.4 ซึ่งตีความเป็น probability ไม่ได้

Logistic Regression จึงใช้ sigmoid “บีบ” linear score:

$$
\sigma(z)=\frac{1}{1+e^{-z}}
$$

### 4.1 คุณสมบัติของ sigmoid

| \(z\) | \(\sigma(z)\) โดยประมาณ | ความหมาย |
|---:|---:|---|
| \(-∞\) | 0 | มั่นใจไปทาง class 0 |
| -2 | 0.1192 | probability ของ class 1 ต่ำ |
| 0 | 0.5 | จุดกึ่งกลาง |
| 2 | 0.8808 | probability ของ class 1 สูง |
| \(+∞\) | 1 | มั่นใจไปทาง class 1 |

คุณสมบัติสำคัญ:

$$
\sigma(-z)=1-\sigma(z)
$$

และอนุพันธ์:

$$
\frac{d\sigma(z)}{dz}
=\sigma(z)(1-\sigma(z))
$$

อนุพันธ์มีค่าสูงสุดที่ \(z=0\) และเข้าใกล้ศูนย์เมื่อ \(|z|\) ใหญ่

## 5. Model Representation

จากเอกสารหน้า 4:

| Model | Representation |
|---|---|
| Linear Regression | \(h_{\theta}(\mathbf{x})=\boldsymbol{\theta}^{T}\mathbf{x}\) |
| Logistic Regression | \(h_{\theta}(\mathbf{x})=\sigma(\boldsymbol{\theta}^{T}\mathbf{x})\) |

สำหรับ \(d\) features และ \(x_0=1\):

$$
z=\theta_0+\theta_1x_1+\cdots+\theta_dx_d
$$

$$
P(y=1\mid\mathbf{x};\boldsymbol{\theta})
=h_{\theta}(\mathbf{x})
=\frac{1}{1+e^{-z}}
$$

และ

$$
P(y=0\mid\mathbf{x};\boldsymbol{\theta})
=1-h_{\theta}(\mathbf{x})
$$

## 6. Probability, Odds และ Log-Odds

### 6.1 Odds

จากเอกสารหน้า 14 หาก probability ของเหตุการณ์สำเร็จคือ \(p\):

$$
Odds=\frac{p}{1-p}
$$

ตัวอย่างจากสไลด์:

| Probability \(p\) | Odds \(p/(1-p)\) | การอ่าน |
|---:|---:|---|
| 0.8 | 4 | สำเร็จต่อไม่สำเร็จ = 4:1 |
| 0.9 | 9 | 9:1 |
| 0.5 | 1 | โอกาสเท่ากัน |
| 0.2 | 0.25 | 1:4 |

Odds ไม่เท่ากับ probability เช่น odds = 4 ไม่ได้หมายถึง probability 400% แต่

$$
p=\frac{Odds}{1+Odds}=\frac{4}{5}=0.8
$$

### 6.2 Logit หรือ Log-Odds

จากเอกสารหน้า 15 เมื่อใช้ natural logarithm กับ odds จะได้ความสัมพันธ์เชิงเส้น:

$$
\log\left(\frac{p}{1-p}\right)
=\theta_0+\theta_1x_1+\cdots+\theta_dx_d
$$

ฟังก์ชัน

$$
logit(p)=\ln\left(\frac{p}{1-p}\right)
$$

แปลง \(p\in(0,1)\) ไปเป็น \((-∞,+∞)\) และ inverse logit คือ sigmoid

### 6.3 Derive sigmoid จาก logit

เริ่มจาก

$$
\ln\left(\frac{p}{1-p}\right)=z
$$

ยกกำลัง \(e\):

$$
\frac{p}{1-p}=e^z
$$

จัดรูป:

$$
p=e^z(1-p)
$$

$$
p(1+e^z)=e^z
$$

$$
p=\frac{e^z}{1+e^z}
=\frac{1}{1+e^{-z}}
=\sigma(z)
$$

## 7. การตีความ Coefficient และ Odds Ratio

จาก logit model:

$$
\log\left(\frac{p}{1-p}\right)
=\theta_0+\theta_1x_1+\cdots+\theta_dx_d
$$

เมื่อ \(x_j\) เพิ่ม 1 หน่วย โดยควบคุม features อื่นคงที่:

- log-odds เปลี่ยน \(\theta_j\)
- odds ถูกคูณด้วย \(e^{\theta_j}\)

ดังนั้น

$$
OR_j=e^{\theta_j}
$$

### Worked example

หาก \(\theta_1=0.693\):

$$
e^{0.693}\approx2
$$

เมื่อ \(x_1\) เพิ่ม 1 หน่วย odds ของ class 1 เพิ่มเป็น 2 เท่า โดยคุม features อื่นคงที่

หาก \(\theta_2=-0.223\):

$$
e^{-0.223}\approx0.8
$$

odds ถูกคูณด้วย 0.8 หรือ **ลดลง 20%** ไม่ใช่ probability ลดลง 20 percentage points

> **ข้อควรระวัง:** ผลต่อ probability ไม่คงที่ เพราะ sigmoid เป็นเส้นโค้ง ผลของ feature ต่อ probability ขึ้นกับค่าเริ่มต้นของ \(z\)

## 8. Decision Rule และ Threshold

จากเอกสารหน้า 5 หากใช้ threshold 0.5:

$$
\hat{y}=\begin{cases}
1,&h_{\theta}(\mathbf{x})\ge0.5\\
0,&h_{\theta}(\mathbf{x})<0.5
\end{cases}
$$

เพราะ sigmoid เป็น monotonic และ \(\sigma(0)=0.5\):

$$
h_{\theta}(\mathbf{x})\ge0.5
\iff
\boldsymbol{\theta}^{T}\mathbf{x}\ge0
$$

ดังนั้น decision boundary ที่ threshold 0.5 คือ

$$
\boldsymbol{\theta}^{T}\mathbf{x}=0
$$

### 8.1 หนึ่ง feature

$$
h_{\theta}(x)=\sigma(\theta_0+\theta_1x)
$$

boundary:

$$
\theta_0+\theta_1x=0
\quad\Rightarrow\quad
x=-\frac{\theta_0}{\theta_1}
$$

### 8.2 สอง features

$$
h_{\theta}(\mathbf{x})
=\sigma(\theta_0+\theta_1x_1+\theta_2x_2)
$$

boundary:

$$
\theta_0+\theta_1x_1+\theta_2x_2=0
$$

หรือเมื่อ \(\theta_2\ne0\):

$$
x_2=-\frac{\theta_0}{\theta_2}
-\frac{\theta_1}{\theta_2}x_1
$$

จึงเป็นเส้นตรงในระนาบสอง features

### 8.3 Nonlinear decision boundary

จากเอกสารหน้า 5–6:

$$
h_{\theta}(\mathbf{x})
=\sigma(-1+x_1^2+x_2^2)
$$

boundary ที่ probability 0.5:

$$
-1+x_1^2+x_2^2=0
$$

$$
x_1^2+x_2^2=1
$$

เป็นวงกลมรัศมี 1 แม้ Logistic Regression linear ใน parameters แต่ polynomial feature mapping ทำให้ boundary nonlinear ใน original inputs

### 8.4 Threshold ไม่จำเป็นต้องเป็น 0.5

ถ้าใช้ threshold \(\tau\):

$$
h_{\theta}(\mathbf{x})\ge\tau
$$

เทียบเท่ากับ

$$
\boldsymbol{\theta}^{T}\mathbf{x}
\ge
\log\left(\frac{\tau}{1-	au}\right)
$$

ลด threshold มักเพิ่ม recall แต่ลด precision; เพิ่ม threshold มักเพิ่ม precision แต่ลด recall ทั้งนี้ขึ้นกับ distribution ของคะแนน

## 9. ทำไมไม่ใช้ MSE เป็น Cost มาตรฐาน

เอกสารหน้า 7 ระบุว่า MSE ซึ่งใช้ใน Linear Regression ไม่เหมาะกับ Logistic Regression เพราะเมื่อ sigmoid ประกอบกับ squared loss อาจให้ objective ที่มี convergence properties ไม่ดีและไม่เป็น convex ตาม parameter ในรูปมาตรฐาน

เหตุผลเพิ่มเติม:

- MSE ไม่สอดคล้องโดยตรงกับ Bernoulli likelihood
- เมื่อ sigmoid อิ่มตัว gradient อาจเล็กมากแม้ทำนายผิดอย่างมั่นใจ
- Binary Cross-Entropy ลงโทษ confident wrong prediction รุนแรงและให้ gradient ที่เรียบง่าย

## 10. Negative Log-Likelihood / Binary Cross-Entropy

จากเอกสารหน้า 8 กำหนด loss ของหนึ่ง sample:

$$
Cost(h_{\theta}(\mathbf{x}),y)
=\begin{cases}
-\ln h_{\theta}(\mathbf{x}),&y=1\\
-\ln(1-h_{\theta}(\mathbf{x})),&y=0
\end{cases}
$$

รวมสองกรณี:

$$
J(\boldsymbol{\theta})
=-\frac{1}{N}\sum_{i=1}^{N}
\left[
y_i\ln h_{\theta}(\mathbf{x}_i)
+(1-y_i)\ln(1-h_{\theta}(\mathbf{x}_i))
\right]
$$

ชื่อที่พบได้:

- Negative Log-Likelihood Loss (NLL/NLLL)
- Binary Cross-Entropy (BCE)
- Log Loss

ในบริบท binary Logistic Regression สูตรเหล่านี้หมายถึง objective เดียวกันหรือแตกต่างเพียง convention การรวม/เฉลี่ย

### 10.1 Shape ของ loss

จากกราฟหน้า 9:

- ถ้า \(y=1\), loss = \(-\ln\hat{p}\): \(\hat{p}\to1\) loss เข้าใกล้ 0; \(\hat{p}\to0\) loss เข้าใกล้ ∞
- ถ้า \(y=0\), loss = \(-\ln(1-\hat{p})\): \(\hat{p}\to0\) loss เข้าใกล้ 0; \(\hat{p}\to1\) loss เข้าใกล้ ∞

โมเดลจึงถูกลงโทษมากเมื่อทำนายผิดอย่างมั่นใจ

### 10.2 Worked example

ถ้า \(y=1\):

| \(\hat{p}\) | Loss \(-\ln\hat{p}\) |
|---:|---:|
| 0.9 | 0.1053 |
| 0.6 | 0.5108 |
| 0.1 | 2.3026 |

ถ้า \(y=0\) และ \(\hat{p}=0.9\):

$$
Loss=-\ln(1-0.9)=-\ln(0.1)=2.3026
$$

## 11. เชื่อมกับ Bernoulli Likelihood

จากเอกสารหน้า 8 สำหรับ \(y_i\in\{0,1\}\):

$$
P(y_i\mid\mathbf{x}_i;\boldsymbol{\theta})
=h_i^{y_i}(1-h_i)^{1-y_i}
$$

โดย \(h_i=h_{\theta}(\mathbf{x}_i)\)

- ถ้า \(y_i=1\): ได้ \(h_i\)
- ถ้า \(y_i=0\): ได้ \(1-h_i\)

สมมติ samples เป็นอิสระแบบมีเงื่อนไข likelihood ทั้งชุดคือ

$$
L(\boldsymbol{\theta})
=\prod_{i=1}^{N}h_i^{y_i}(1-h_i)^{1-y_i}
$$

ใช้ log เปลี่ยนผลคูณเป็นผลรวม:

$$
\ell(\boldsymbol{\theta})
=\sum_{i=1}^{N}
\left[y_i\ln h_i+(1-y_i)\ln(1-h_i)\right]
$$

Maximum Likelihood ต้อง maximize \(\ell\) ซึ่งเท่ากับ minimize negative average log-likelihood \(J\)

## 12. Derivation ของ Gradient

เอกสารหน้า 10–12 derive อนุพันธ์ของ NLL ดังนี้

กำหนด

$$
h_i=\sigma(z_i),\qquad
z_i=\boldsymbol{\theta}^{T}\mathbf{x}_i
$$

สำหรับหนึ่ง sample:

$$
L_i=-\left[y_i\ln h_i+(1-y_i)\ln(1-h_i)\right]
$$

### 12.1 อนุพันธ์ที่ต้องใช้

$$
\frac{d}{dx}\ln f(x)=\frac{1}{f(x)}\frac{df(x)}{dx}
$$

$$
\frac{d\sigma(z)}{dz}=\sigma(z)(1-\sigma(z))
$$

$$
\frac{\partial z_i}{\partial\theta_j}=x_{i,j}
$$

จึงได้

$$
\frac{\partial h_i}{\partial\theta_j}
=h_i(1-h_i)x_{i,j}
$$

### 12.2 Chain rule

$$
\frac{\partial L_i}{\partial\theta_j}
=-left[
y_i\frac{1}{h_i}\frac{\partial h_i}{\partial\theta_j}
+(1-y_i)\frac{1}{1-h_i}
\frac{\partial(1-h_i)}{\partial\theta_j}
\right]
$$

เพราะ

$$
\frac{\partial(1-h_i)}{\partial\theta_j}
=-\frac{\partial h_i}{\partial\theta_j}
$$

แทนอนุพันธ์ sigmoid:

$$
\frac{\partial L_i}{\partial\theta_j}
=-left[
y_i(1-h_i)x_{i,j}
-(1-y_i)h_ix_{i,j}
\right]
$$

จัดรูป:

$$
\frac{\partial L_i}{\partial\theta_j}
=(h_i-y_i)x_{i,j}
$$

เฉลี่ยทุก samples:

$$
\boxed{
\frac{\partial J}{\partial\theta_j}
=\frac{1}{N}\sum_{i=1}^{N}
(h_{\theta}(\mathbf{x}_i)-y_i)x_{i,j}}
$$

ในรูปเมทริกซ์:

$$
\boxed{
\nabla J(\boldsymbol{\theta})
=\frac{1}{N}X^T(\mathbf{h}-\mathbf{y})}
$$

### 12.3 เหตุใด gradient คล้าย Linear Regression

หน้า 12 ระบุว่าเป็นรูปเดียวกับ BGD ของ MSE ที่ใช้ในสไลด์ก่อนหน้า:

$$
(prediction-target)\times feature
$$

แต่ **representation และ cost function ไม่เหมือนกัน**:

- Linear Regression: prediction = \(X\theta\), cost = MSE
- Logistic Regression: prediction = \(\sigma(X\theta)\), cost = BCE/NLL

ความเหมือนของ gradient update ไม่ได้แปลว่าโมเดลหรือ probabilistic assumptions เหมือนกัน

## 13. Gradient Descent Update

$$
\theta_j^{(t+1)}
=\theta_j^{(t)}-eta
\frac{1}{N}\sum_{i=1}^{N}
(h_i-y_i)x_{i,j}
$$

matrix form:

$$
\boldsymbol{\theta}^{(t+1)}
=\boldsymbol{\theta}^{(t)}
-\eta\frac{1}{N}X^T
(\sigma(X\boldsymbol{\theta}^{(t)})-\mathbf{y})
$$

### Worked example: หนึ่ง update

มีหนึ่ง sample \(x_0=1,x_1=2,y=1\), parameters เริ่มต้น \(\theta_0=0,\theta_1=0\), \(\eta=0.1\)

$$
z=0+0(2)=0,qquad h=\sigma(0)=0.5
$$

gradients:

$$
g_0=(0.5-1)(1)=-0.5
$$

$$
g_1=(0.5-1)(2)=-1
$$

update:

$$
\theta_0^{new}=0-0.1(-0.5)=0.05
$$

$$
\theta_1^{new}=0-0.1(-1)=0.10
$$

หลัง update:

$$
z^{new}=0.05+0.10(2)=0.25
$$

$$
h^{new}=\sigma(0.25)\approx0.5622
$$

probability ของ class ที่ถูกต้องเพิ่มจาก 0.5 เป็น 0.5622

## 14. Linear vs Logistic Regression

สรุปจากเอกสารหน้า 13 และขยายความ:

| ประเด็น | Linear Regression | Logistic Regression |
|---|---|---|
| งานหลัก | ทำนายค่าต่อเนื่อง | Classification |
| Output | \((-∞,+∞)\) | probability \((0,1)\) |
| Representation | \(\theta^Tx\) | \(\sigma(\theta^Tx)\) |
| Target | \(y\in\mathbb{R}\) | binary \(y\in\{0,1\}\) ในบทนี้ |
| Cost | MSE/SSE | NLL/Binary Cross-Entropy |
| Distribution view | มักเชื่อมกับ Gaussian errors | Bernoulli likelihood |
| Metrics | MAE, MSE, RMSE, \(R^2\) | Accuracy, Precision, Recall, F1, ROC-AUC |
| Gradient form ตามสไลด์ | \(X^T(h-y)/N\) | \(X^T(h-y)/N\) |
| Decision threshold | ไม่มี | ต้องกำหนดสำหรับ class label |

## 15. Evaluation Metrics

เอกสารหน้า 13 ระบุ Accuracy, Precision, Recall, F1 และ AUC

### 15.1 Confusion Matrix

| | Predicted 1 | Predicted 0 |
|---|---:|---:|
| Actual 1 | TP | FN |
| Actual 0 | FP | TN |

$$
Accuracy=\frac{TP+TN}{TP+TN+FP+FN}
$$

$$
Precision=\frac{TP}{TP+FP}
$$

$$
Recall=\frac{TP}{TP+FN}
$$

$$
F_1=2\frac{Precision\times Recall}{Precision+Recall}
$$

### 15.2 เลือก metric ตามต้นทุน

- **Precision:** สำคัญเมื่อ FP แพง เช่น บล็อกธุรกรรมปกติ
- **Recall:** สำคัญเมื่อ FN แพง เช่น พลาดผู้ป่วยเสี่ยงสูง
- **F1:** สมดุล precision/recall แต่ไม่ใช้ TN
- **Accuracy:** เหมาะเมื่อ classes ค่อนข้างสมดุลและต้นทุนผิดพลาดคล้ายกัน

### 15.3 ROC Curve และ ROC-AUC

ROC plot:

$$
TPR=Recall=\frac{TP}{TP+FN}
$$

กับ

$$
FPR=\frac{FP}{FP+TN}
$$

เมื่อเปลี่ยน threshold ROC-AUC สรุปความสามารถในการจัดอันดับ positive เหนือ negative โดยไม่ยึด threshold เดียว

### 15.4 Precision-Recall Curve

> **คำอธิบายเพิ่มเติม:** เมื่อ positive class มีน้อยมาก PR curve/Average Precision มักสื่อ trade-off ที่สนใจได้ตรงกว่า ROC เพราะเน้น precision กับ recall ของ positive class

## 16. Threshold Selection

ไม่ควรเลือก 0.5 โดยอัตโนมัติทุกโจทย์ ขั้นตอนที่ดีกว่า:

1. train model ด้วย training data
2. สร้าง predicted probabilities บน validation data
3. คำนวณ metric/cost ที่ thresholds หลายค่า
4. เลือก threshold จาก business constraint เช่น recall อย่างน้อย 90%
5. ประเมิน threshold ที่เลือกครั้งสุดท้ายบน test data

ตัวอย่าง fraud screening:

- ทีมตรวจได้วันละ 100 รายการ
- เลือก threshold ให้จำนวน alerts ไม่เกิน capacity
- ภายในข้อจำกัดนั้น maximize fraud value captured หรือ recall

threshold เป็น **business/operating decision** ไม่ใช่ parameter ที่ sigmoid เรียนรู้เอง

## 17. Probability Calibration

ถ้าโมเดลทำนาย 0.8 ให้ 100 เคส โมเดล calibrated ดีควรมี positive จริงประมาณ 80 เคสในกลุ่มลักษณะนั้น

ควรแยก:

- **Discrimination:** จัดอันดับ positive สูงกว่า negative ได้ดีหรือไม่ เช่น ROC-AUC
- **Calibration:** probability ตรงกับอัตราเกิดจริงหรือไม่

โมเดลอาจ AUC สูงแต่ probability overconfident การใช้งานที่ตัดสินใจตาม expected cost จึงควรดู calibration curve และ metric เช่น log loss/Brier score

## 18. Assumptions และข้อจำกัด

> **คำอธิบายเพิ่มเติม:** ขยายจากเนื้อหาเพื่อการใช้งานจริง

1. observations ควรเป็นอิสระตามโครงสร้างที่โมเดลสมมติ
2. log-odds ควรสัมพันธ์เชิงเส้นกับ continuous predictors หากไม่ใช่อาจเพิ่ม transformation/spline/polynomial
3. ไม่มี perfect multicollinearity
4. ต้องมีข้อมูลเพียงพอต่อจำนวน parameters และ positive events
5. labels ต้องมีความหมายและใกล้เคียงสิ่งที่จะรู้ใน production
6. ต้องระวัง complete/quasi-complete separation ซึ่งทำให้ coefficients โตไม่สิ้นสุดใน unregularized MLE
7. outliers และ high-leverage points อาจเปลี่ยน decision boundary มาก

### 18.1 Regularization

เมื่อ features มากหรือสัมพันธ์กัน ใช้ penalty:

L2/Ridge Logistic Regression:

$$
J_{reg}(\theta)=J(\theta)+\lambda\sum_{j=1}^{d}\theta_j^2
$$

L1/Lasso-style penalty:

$$
J_{reg}(\theta)=J(\theta)+\lambda\sum_{j=1}^{d}|\theta_j|
$$

โดยทั่วไปไม่ penalize intercept การ regularize ช่วยลด variance และ coefficients ใหญ่เกินไป แต่ต้อง tune \(\lambda\) บน validation data

## 19. Numerical Stability

การคำนวณ \(\ln(h)\) เมื่อ \(h\) ใกล้ 0 หรือ \(\ln(1-h)\) เมื่อ \(h\) ใกล้ 1 อาจเกิด \(\ln0\) ใน floating point

แนวทาง:

- ใช้ฟังก์ชัน log-loss ที่คำนวณจาก logits อย่างเสถียร
- ไม่เขียน sigmoid + log แบบ naive ใน production
- หากจำเป็นต้องคำนวณ probability ให้ clip ด้วย epsilon อย่างระมัดระวัง

ไลบรารีมาตรฐานมักใช้รูปที่เทียบเท่า เช่น `logaddexp`/softplus เพื่อหลีกเลี่ยง overflow และ underflow

## 20. Practical Workflow

1. นิยาม positive class และ prediction time
2. กำหนดต้นทุน FP/FN และ business capacity
3. split train/validation/test โดยป้องกัน temporal/group leakage
4. fit preprocessing บน train เท่านั้น
5. train Logistic Regression และ tune regularization
6. ประเมิน log loss, discrimination และ calibration
7. เลือก threshold บน validation ตาม business objective
8. ตรวจ performance แยก subgroup เพื่อดู bias
9. ประเมินครั้งสุดท้ายบน test set
10. deploy ทั้ง preprocessing, model และ threshold เป็น version เดียวกัน
11. monitor class prevalence, feature drift, calibration และ metric หลังใช้งาน

## 21. Worked Scenario: Vendor Risk Screening

ต้องการจัดลำดับ vendor ที่ควรตรวจสอบ:

$$
P(Risk=1\mid x)
=\sigma(\theta_0
+\theta_1LateDeliveryRate
+\theta_2PriceVariance
+\theta_3ComplaintCount)
$$

การออกแบบที่สำคัญ:

- label ต้องมาจากผล audit ที่ยืนยันแล้ว
- features ต้องเป็นข้อมูลที่รู้ก่อนตัดสินใจตรวจ
- ถ้า risk cases มีน้อย ไม่ใช้ accuracy อย่างเดียว
- หากตรวจได้จำกัด ให้พิจารณา precision@k/recall ภายใต้ capacity
- probability ต้อง calibrated หากใช้คำนวณ expected loss
- coefficient ไม่ยืนยันว่า feature เป็นสาเหตุของ risk

## 22. Common Misconceptions

1. **“Logistic Regression ใช้ทำนายค่าต่อเนื่องเพราะชื่อ Regression”**  
   ในบทนี้ใช้ classification และให้ probability ของ class

2. **“Sigmoid output คือความน่าจะเป็นที่เชื่อถือได้เสมอ”**  
   การตีความเป็น probability อาศัย model specification และ calibration ต้องตรวจบน unseen data

3. **“Probability 0.8 เท่ากับ odds 0.8”**  
   Probability 0.8 มี odds \(0.8/0.2=4\)

4. **“Coefficient 0.2 หมายถึง probability เพิ่ม 20%”**  
   coefficient เปลี่ยน log-odds; odds ratio คือ \(e^{0.2}\) ผลต่อ probability ขึ้นกับ baseline

5. **“Decision boundary ต้องเป็นเส้นตรงเสมอ”**  
   เป็นเส้นตรงใน feature space แต่ polynomial mapping ทำให้โค้งใน original space ได้

6. **“Threshold 0.5 ดีที่สุดเสมอ”**  
   threshold ที่เหมาะขึ้นกับ metric, prevalence, cost และ capacity

7. **“AUC สูงจึงใช้ probability คำนวณความเสี่ยงได้ทันที”**  
   AUC วัด ranking/discrimination ไม่รับรอง calibration

8. **“Gradient เหมือน Linear Regression จึงใช้ MSE ได้เหมือนกัน”**  
   gradient form คล้ายกันหลัง simplify แต่ hypothesis และ objective ต่างกัน

9. **“Accuracy สูงแปลว่าตรวจจับ rare event ดี”**  
   หาก positive มี 1% การทาย 0 ทั้งหมดได้ accuracy 99% แต่ recall = 0

10. **“เพิ่ม features ยิ่งมากยิ่งดี”**  
   เพิ่มความเสี่ยง leakage, multicollinearity และ overfitting จึงต้อง validate และ regularize

## 23. Likely Exam Focus

> หัวข้อต่อไปนี้อนุมานจากสูตร กราฟ และตารางในเอกสาร ไม่ใช่ข้อสอบจริง

### Definitions

- sigmoid, probability, odds, logit/log-odds
- decision boundary และ classification threshold
- NLL, BCE, log loss และ Bernoulli likelihood
- precision, recall, F1 และ AUC

### Equations to remember

$$
\sigma(z)=\frac{1}{1+e^{-z}}
$$

$$
h_{\theta}(x)=\sigma(\theta^Tx)
$$

$$
Odds=\frac{p}{1-p},qquad
logit(p)=\ln\frac{p}{1-p}
$$

$$
J(\theta)=-\frac{1}{N}\sum_i
[y_i\ln h_i+(1-y_i)\ln(1-h_i)]
$$

$$
\frac{\partial J}{\partial\theta_j}
=\frac{1}{N}\sum_i(h_i-y_i)x_{i,j}
$$

### Calculations

- คำนวณ sigmoid/probability จาก \(z\)
- แปลง probability ↔ odds ↔ log-odds
- หา odds ratio จาก coefficient
- หา decision boundary
- คำนวณ BCE ของหนึ่งหรือหลาย samples
- ทำ Gradient Descent หนึ่ง iteration
- คำนวณ classification metrics จาก confusion matrix

### Concepts to compare

- Linear vs Logistic Regression
- MSE vs NLL/BCE
- probability vs odds
- class probability vs class label
- discrimination vs calibration

## 24. Practice Questions

### Recall

**1.** Logistic Regression แบบ binary มี target อยู่ในเซตใด?

**2.** \(\sigma(0)\) เท่ากับเท่าใด?

**3.** เมื่อ threshold = 0.5 decision boundary ใน logit space คือสมการใด?

### Explain and Compare

**4.** เพราะเหตุใด Linear Regression จึงไม่เหมาะกับการทำนาย probability โดยตรง?

**5.** เปรียบเทียบ probability, odds และ log-odds

**6.** อธิบายเหตุผลที่ Binary Cross-Entropy ลงโทษ confident wrong prediction รุนแรง

**7.** เหตุใด gradient ของ Logistic Regression จึง simplify เป็น \((h-y)x_j\)?

### Apply

**8.** ให้ \(z=-1\) จงหา \(\sigma(z)\) และ class ที่ threshold 0.5

**9.** Probability เท่ากับ 0.75 จงหา odds และ log-odds

**10.** Coefficient ของ feature เท่ากับ 0.4 จงหา odds ratio และตีความ

**11.** ให้ \(h(x)=\sigma(-3+x_1+2x_2)\) จงหา decision boundary

**12.** ถ้า \(y=1,\hat{p}=0.2\) จงหา BCE loss

### Analyze

**13.** โมเดล fraud มี accuracy 99.5% แต่ recall 5% จงวิเคราะห์

**14.** ทีมลด threshold จาก 0.5 เป็น 0.2 คาดว่า precision และ recall จะเปลี่ยนอย่างไร?

**15.** โมเดลมี ROC-AUC 0.92 แต่กลุ่มที่ทำนาย 0.8 เกิด positive จริงเพียง 0.5 มีปัญหาอะไร?

## 25. Model Answers with Reasoning

**1.** \(y\in\{0,1\}\)

**2.** \(\sigma(0)=1/(1+1)=0.5\)

**3.** \(\theta^Tx=0\) เพราะ \(\sigma(0)=0.5\)

**4.** Output ของเส้นตรงไม่ถูกจำกัดและอาจต่ำกว่า 0 หรือสูงกว่า 1 ขณะที่ probability ต้องอยู่ใน [0,1]

**5.** Probability \(p\) อยู่ 0–1; odds = \(p/(1-p)\) อยู่ 0–∞; log-odds = \(\ln[p/(1-p)]\) อยู่ -∞–+∞ และ Logistic Regression ทำให้ log-odds เป็น linear predictor

**6.** ถ้า \(y=1\) แต่ \(\hat{p}\to0\), \(-\ln\hat{p}\to∞\); ถ้า \(y=0\) แต่ \(\hat{p}\to1\), \(-\ln(1-\hat{p})\to∞\)

**7.** Chain rule ให้ sigmoid derivative \(h(1-h)\) ซึ่งตัดกับ denominators \(h\) และ \(1-h\) ใน derivative ของ log terms เหลือ \(h-y\)

**8.**

$$
\sigma(-1)=\frac{1}{1+e^1}\approx0.2689
$$

จึงทำนาย class 0 ที่ threshold 0.5

**9.**

$$
Odds=\frac{0.75}{0.25}=3
$$

$$
logit=\ln3\approx1.0986
$$

**10.**

$$
OR=e^{0.4}\approx1.4918
$$

เมื่อ feature เพิ่มหนึ่งหน่วย odds ของ class 1 เพิ่มประมาณ 49.18% โดยคุม features อื่นคงที่

**11.**

$$
-3+x_1+2x_2=0
$$

หรือ

$$
x_2=1.5-0.5x_1
$$

**12.**

$$
Loss=-\ln(0.2)\approx1.6094
$$

**13.** Accuracy ถูกครอบงำโดย negative class โมเดลพลาด fraud จริง 95% จึงอาจใช้งานไม่ได้ ต้องดู confusion matrix, prevalence, precision/recall, PR curve และปรับ threshold/weighting ตามต้นทุน

**14.** โดยทั่วไปจำนวน predicted positives เพิ่ม ทำให้ recall สูงขึ้นและ precision มีแนวโน้มลดลง แต่ค่าจริงต้องตรวจจาก validation data

**15.** Discrimination ดีแต่ probability calibration แย่และ overconfident ควรตรวจ calibration curve, log loss/Brier score และพิจารณา recalibration บน holdout data

## 26. Key Takeaways

- Logistic Regression แปลง linear score เป็น probability ด้วย sigmoid
- โมเดล linear ใน log-odds ไม่ใช่ linear ใน probability
- coefficient หนึ่งหน่วยเปลี่ยน log-odds \(\theta_j\) และคูณ odds ด้วย \(e^{\theta_j}\)
- threshold แยกขั้น probability estimation ออกจาก class decision
- threshold 0.5 ให้ boundary \(\theta^Tx=0\) แต่ไม่จำเป็นต้องเหมาะกับทุกธุรกิจ
- Polynomial features สร้าง nonlinear boundary ใน original feature space ได้
- BCE/NLL มาจาก Bernoulli likelihood และลงโทษ confident errors อย่างรุนแรง
- gradient simplify เป็น average ของ \((prediction-target)\times feature\)
- Accuracy ไม่พอสำหรับ class imbalance; ต้องดู precision, recall, F1 และ ranking metrics
- AUC กับ calibration วัดคนละมิติ และต้องเลือก threshold ตาม cost/capacity

## 27. Glossary

| คำศัพท์ | ความหมาย |
|---|---|
| Binary Cross-Entropy | Loss สำหรับ binary probability prediction เทียบเท่า negative Bernoulli log-likelihood |
| Calibration | ความสอดคล้องระหว่าง predicted probability กับ observed frequency |
| Decision boundary | จุด/เส้น/พื้นผิวที่โมเดลเปลี่ยน class prediction |
| Logit | Natural log ของ odds |
| Log Loss | อีกชื่อของ cross-entropy/negative log-likelihood ในบริบทนี้ |
| NLL | Negative Log-Likelihood |
| Odds | อัตราส่วน probability ของเกิดเหตุการณ์ต่อไม่เกิด |
| Odds ratio | ตัวคูณของ odds เมื่อ predictor เพิ่มหนึ่งหน่วย |
| Positive class | class ที่นิยามเป็น \(y=1\) |
| Sigmoid | ฟังก์ชันแปลงค่าจริงเป็นช่วง \((0,1)\) |
| Threshold | จุดตัด probability เพื่อสร้าง class label |

## 28. References

### เอกสารประกอบการสอน

- Rattagan, E. (2026). `dads6003_week4_logistic_regression.pdf`: *Week 5: Logistic Regression*, หน้า 1–17.

### แหล่งที่อ้างในเอกสาร

- Sperandei, S. (2014). Understanding logistic regression analysis. *Biochemia Medica, 24*(1), 12–18.
- UCLA Statistical Consulting, [Logistic Regression](https://stats.oarc.ucla.edu/other/mult-pkg/faq/general/faq-how-do-i-interpret-odds-ratios-in-logistic-regression/)

### คำอธิบายเพิ่มเติม

- scikit-learn, [Metrics and scoring](https://scikit-learn.org/stable/modules/model_evaluation.html)
- scikit-learn, [Precision-Recall](https://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html)
- scikit-learn, [Probability calibration](https://scikit-learn.org/stable/modules/calibration.html)
