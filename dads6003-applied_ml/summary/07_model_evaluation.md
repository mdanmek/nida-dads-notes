# Model Training and Evaluation

## ข้อมูลต้นฉบับ

- รายวิชา: DADS6003 Applied Machine Learning
- Lecture: `dads6003_07_model_evaluation.pdf` จำนวน 18 หน้า
- หัวข้อหลัก: model selection, hold-out, validation, bias-variance, confusion matrix, classification metrics, ROC และ Precision-Recall curve

> **จากเอกสาร:** บทเรียนตั้งคำถามว่าโมเดลที่ซับซ้อนระดับใดเหมาะที่สุด แล้วเชื่อม model complexity กับ bias-variance ก่อนสอนการประเมิน binary classification
>
> **คำอธิบายเพิ่มเติม:** Master Note นี้แยก train, validation และ test ให้ชัด เพิ่ม k-fold cross-validation, คำนวณตัวอย่างทุกตารางในสไลด์ และอธิบายวิธีเลือก metric ตามต้นทุนของความผิดพลาด

## ภาพรวมและ Learning Objectives

การฝึกโมเดลตอบคำถามว่า “โมเดลเรียนรู้จากข้อมูลอย่างไร” ส่วนการประเมินโมเดลตอบคำถามที่ต่างออกไปว่า “หลักฐานที่มีเพียงพอหรือไม่ที่จะเชื่อว่าโมเดลจะทำงานได้ดีกับข้อมูลใหม่” โมเดลที่มี training score สูงที่สุดจึงไม่จำเป็นต้องเป็นตัวเลือกที่ดีที่สุด

เมื่อจบบทนี้ ผู้อ่านควรสามารถ:

1. แยก model training, model selection และ final evaluation ได้
2. อธิบายบทบาทของ train, validation และ test set ได้
3. เปรียบเทียบ hold-out, train-validation-test split และ k-fold cross-validation ได้
4. วินิจฉัย high bias และ high variance จาก learning behavior ได้
5. สร้างและอ่าน confusion matrix ได้
6. คำนวณ Accuracy, Recall, Precision, Specificity, FPR, F1 และ MCC ได้
7. อธิบายผลของ decision threshold ต่อ metrics ได้
8. เปรียบเทียบ ROC-AUC กับ Precision-Recall curve ได้
9. เลือก metric ให้สอดคล้องกับโจทย์และต้นทุนความผิดพลาดได้

## 1. ปัญหาหลัก: โมเดลใดดีที่สุด

สไลด์เริ่มจาก polynomial models หลายระดับ ตั้งแต่เส้นตรงจนถึง degree 10:

$$
h_\theta(x)=\theta_0+\theta_1x
$$

$$
h_\theta(x)=\theta_0+\theta_1x+\theta_2x^2+\cdots+\theta_{10}x^{10}
$$

โมเดล degree สูงมีความยืดหยุ่นมาก จึงมักลด training error ได้ แต่ความยืดหยุ่นนั้นอาจใช้เรียน noise แทน signal หากเลือกโมเดลจาก training score อย่างเดียว เรามักให้รางวัลกับโมเดลที่ซับซ้อนเกินไป

คำว่า “ดีที่สุด” จึงต้องมีบริบท:

- ดีที่สุดบนข้อมูลฝึก หรือข้อมูลใหม่
- ดีที่สุดตาม metric ใด
- ความผิดพลาดชนิดใดมีต้นทุนสูง
- ต้องการทำนาย class label หรือ probability
- ผลต้องเสถียรเพียงใดเมื่อเปลี่ยน sample

Model evaluation ไม่ใช่เพียงเรียก `accuracy_score()` แต่เป็นการออกแบบหลักฐานให้ตอบคำถามเหล่านี้ได้โดยไม่รั่วข้อมูลจากชุดประเมินกลับไปสู่การฝึก

## 2. Train, Validation และ Test Set

### 2.1 หน้าที่ของแต่ละชุด

ข้อมูลสามชุดมีหน้าที่ต่างกัน:

| Dataset | ใช้ทำอะไร | สิ่งที่ห้ามทำ |
|---|---|---|
| Training set | fit parameters เช่น coefficients | ใช้รายงาน final performance เพียงชุดเดียว |
| Validation set | เลือก model, features, threshold และ hyperparameters | รายงานเป็น unbiased final test หลังใช้เลือกซ้ำ |
| Test set | ประเมินครั้งสุดท้ายหลังทุก decision ถูกล็อก | ใช้เลือก model หรือแก้ feature engineering |

Parameter คือค่าที่โมเดลเรียนระหว่าง `fit()` เช่น logistic regression coefficients ส่วน hyperparameter คือค่าที่กำหนดกระบวนการเรียน เช่น polynomial degree, Ridge alpha หรือ tree depth

การแตะ test set เพื่อเลือก degree แล้วเรียกชุดเดิมว่า “unseen test” เป็นความเข้าใจผิด เพราะผลจาก test ได้เปลี่ยน decision ของเราแล้ว แม้ไม่ได้ส่ง test rows เข้า `fit()` โดยตรง

### 2.2 Hold-out method

Hold-out แบ่งข้อมูลครั้งเดียว เช่น 80% train และ 20% test ข้อดีคือเข้าใจง่าย เร็ว และเหมาะเมื่อข้อมูลมากพอ แต่ผลอาจไวต่อ random split โดยเฉพาะ dataset ขนาดเล็กหรือ class imbalance

> **คำอธิบายเพิ่มเติมจากสไลด์หน้า 3:** Hold-out ไม่ได้ทำให้ overfitting โดยตัวมันเอง ความเสี่ยงเกิดเมื่อทดลองหลายโมเดลแล้วเลือกจาก test set เดิมซ้ำ ๆ จน decision ของเราปรับเข้าหา test set นั้น

### 2.3 Train-validation-test split

สไลด์หน้า 4 แบ่ง 60% train, 20% validation และ 20% test วิธีนี้ทำให้เลือกโมเดลจาก validation แล้วประเมิน test เพียงครั้งสุดท้าย จึงแยก model selection ออกจาก final evaluation ได้

อย่างไรก็ตาม วิธีนี้ยังเป็น single split ผลยังขึ้นกับว่าตัวอย่างใดตกอยู่ใน validation set

> **คำชี้แจงคำศัพท์:** สไลด์เรียก 60/20/20 ว่า “Cross validation Method” แต่โครงสร้างนี้ตรงกับ train-validation-test hold-out มากกว่า ส่วน k-fold cross-validation จะหมุนหลาย folds ให้แต่ละส่วนรับบท validation สลับกัน

### 2.4 K-fold cross-validation

K-fold แบ่ง training data เป็น \(K\) ส่วน ในรอบที่ \(k\) ใช้ fold ที่ \(k\) เป็น validation และใช้ส่วนที่เหลือ fit โมเดล ทำครบทุก fold แล้วเฉลี่ย score:

$$
\mathrm{CV\ Score}=\frac{1}{K}\sum_{k=1}^{K}s_k
$$

ค่า \(s_k\) คือ validation score ของ fold ที่ \(k\) วิธีนี้ใช้ observations ได้คุ้มและลดการพึ่ง split เดียว แต่ช้ากว่าเพราะ fit \(K\) ครั้งต่อหนึ่ง model configuration

สำหรับ classification ควรใช้ stratified folds เพื่อรักษาสัดส่วน class โดยประมาณ หากมีคนไข้หลายแถว ต้อง split แบบ grouped เพื่อไม่ให้ข้อมูลคนเดียวกันอยู่ทั้ง train และ validation หากข้อมูลมีลำดับเวลา ต้องใช้ time-aware split ไม่ควรสุ่มอนาคตกลับไปฝึกอดีต

Scikit-learn อธิบาย cross-validation และข้อควรระวังเรื่อง preprocessing leakage ใน [Cross-validation guide](https://scikit-learn.org/stable/modules/cross_validation.html)

## 3. Bias-Variance Diagnosis

### 3.1 Bias และ variance คืออะไร

**Bias** คือความคลาดเคลื่อนจากข้อสมมติของโมเดลที่ง่ายหรือจำกัดเกินไป โมเดล high bias จับ pattern หลักไม่พอ จึง underfit ทั้ง train และ validation

**Variance** คือความไวของโมเดลต่อ sample ที่ใช้ฝึก โมเดล high variance เปลี่ยนมากเมื่อข้อมูลฝึกเปลี่ยนเล็กน้อย จึง fit train ดีแต่ทำงานกับ validation แย่

| สภาวะ | Train error | Validation error | ช่องว่าง |
|---|---:|---:|---:|
| High bias | สูง | สูง | มักไม่กว้าง |
| Good balance | ต่ำพอเหมาะ | ต่ำ | แคบ |
| High variance | ต่ำมาก | สูง | กว้าง |

Polynomial degree ต่ำมักเพิ่ม bias ส่วน degree สูงมักเพิ่ม variance แต่คำว่า “ต่ำ” หรือ “สูง” ขึ้นกับข้อมูล ไม่ใช่กฎว่าค่า degree ใดผิดเสมอ

### 3.2 Regularization parameter

Ridge objective ในสไลด์คือ:

$$
J(\theta)=\frac{1}{N}\sum_{i=1}^{N}(h_\theta(x_i)-y_i)^2+\lambda\sum_{j=1}^{d}\theta_j^2
$$

เมื่อ \(\lambda\) เพิ่ม coefficients ถูกหดมากขึ้น โมเดลยืดหยุ่นน้อยลง:

- \(\lambda\) สูงเกิน: variance ลด แต่ bias เพิ่ม อาจ underfit
- \(\lambda\) ต่ำเกิน: bias ลด แต่ variance เพิ่ม อาจ overfit

ดังนั้นการเพิ่มหรือลด \(\lambda\) ไม่ใช่คำตอบเดียว ต้องวินิจฉัยก่อนว่า error มาจาก bias หรือ variance

### 3.3 Training data size

การเพิ่ม training data มักช่วยลด variance เพราะโมเดลพึ่งรายละเอียดเฉพาะ sample น้อยลง แต่ไม่แก้ high bias มากนัก หากเส้นตรง underfit pattern โค้งอย่างชัดเจน ต่อให้มีข้อมูลเพิ่ม โมเดลก็ยังไม่มีรูปแบบที่จำเป็น

### 3.4 เลือกแนวทางแก้ตามอาการ

| แนวทาง | มักช่วย High bias | มักช่วย High variance |
|---|---:|---:|
| เพิ่ม training data | น้อย | มาก |
| ลด features | อาจแย่ลง | ช่วย |
| เพิ่ม useful features | ช่วย | อาจแย่ลง |
| เพิ่ม polynomial features | ช่วย | อาจแย่ลง |
| ลด regularization | ช่วย | อาจแย่ลง |
| เพิ่ม regularization | อาจแย่ลง | ช่วย |

ตารางนี้เป็นแนวทางวินิจฉัย ไม่ใช่สูตรตายตัว ต้องยืนยันด้วย validation results

## 4. จาก Probability สู่ Class Label

Binary classifier มักสร้าง score หรือ probability ก่อน แล้วใช้ threshold แปลงเป็น class:

$$
\hat{y}=\begin{cases}1,&\hat{p}\geq t\\0,&\hat{p}<t\end{cases}
$$

\(\hat{p}\) คือ predicted probability ของ positive class และ \(t\) คือ threshold ค่า default 0.5 เป็นเพียง convention ไม่ได้เหมาะกับทุกต้นทุน

จากตัวอย่างสไลด์หน้า 12:

| ID | Actual \(y\) | Probability | Prediction เมื่อ \(t=0.5\) |
|---:|---:|---:|---:|
| 1 | 0 | 0.5 | 1 |
| 2 | 1 | 0.9 | 1 |
| 3 | 0 | 0.7 | 1 |
| 4 | 1 | 0.7 | 1 |
| 5 | 1 | 0.3 | 0 |
| 6 | 0 | 0.4 | 0 |
| 7 | 1 | 0.5 | 1 |

ได้ TP = 3, FP = 2, FN = 1 และ TN = 1 การลด threshold จะจับ positive ได้มากขึ้น แต่ false alarms มักเพิ่ม การเพิ่ม thresholdมักทำตรงข้าม

Threshold ต้องเลือกจาก validation data ตามต้นทุนหรือข้อกำหนด เช่น “recall อย่างน้อย 95% แล้ว maximize precision” ไม่ควรเลือกจาก test set

## 5. Confusion Matrix

Confusion matrix นับผลตาม actual class และ predicted class:

|  | Actual Positive | Actual Negative |
|---|---:|---:|
| Predicted Positive | TP | FP |
| Predicted Negative | FN | TN |

- **TP:** ทำนาย positive และเป็น positive จริง
- **FP:** ทำนาย positive แต่จริงเป็น negative
- **FN:** ทำนาย negative แต่จริงเป็น positive
- **TN:** ทำนาย negative และเป็น negative จริง

Positive class ต้องนิยามจากโจทย์ เช่น “มีโรค”, “fraud” หรือ “spam” ไม่ได้หมายถึงผลที่ดีเสมอไป หากสลับ positive class ความหมายของ precision และ recall ก็เปลี่ยน

จากตัวอย่าง 7 รายการ:

$$
\mathrm{Accuracy}=\frac{TP+TN}{TP+FP+FN+TN}=\frac{3+1}{7}=0.5714
$$

$$
\mathrm{Recall}=\frac{TP}{TP+FN}=\frac{3}{4}=0.75
$$

$$
\mathrm{Precision}=\frac{TP}{TP+FP}=\frac{3}{5}=0.60
$$

## 6. Metrics จาก Confusion Matrix

### 6.1 Accuracy

Accuracy ตอบว่า prediction ทั้งหมดถูกกี่สัดส่วน:

$$
\mathrm{Accuracy}=\frac{TP+TN}{TP+FP+FN+TN}
$$

เหมาะเมื่อ classes ค่อนข้างสมดุลและ FP/FN มีต้นทุนใกล้กัน แต่ misleading เมื่อ positive rare ตัวอย่างสไลด์หน้า 13 มี negative 8 และ positive 2:

| Model | วิธีทำนาย | Accuracy | Recall | Precision |
|---|---|---:|---:|---:|
| 1 | ทายทุกแถวเป็น 0 | 0.80 | 0.00 | นิยามไม่ได้ |
| 2 | จับ positive ถูก 1 จาก 2 และไม่มี FP | 0.90 | 0.50 | 1.00 |
| 3 | ทายทุกแถวเป็น 1 | 0.20 | 1.00 | 0.20 |

Model 1 ได้ accuracy 80% แต่จับ positive ไม่ได้เลย นี่คือเหตุผลที่ต้องดู class-specific metrics และเปรียบเทียบกับ dummy baseline

### 6.2 Recall หรือ Sensitivity

Recall ตอบว่า “ใน positive จริงทั้งหมด โมเดลจับได้กี่ส่วน”:

$$
\mathrm{Recall}=\mathrm{TPR}=\frac{TP}{TP+FN}
$$

Recall สำคัญเมื่อ FN แพง เช่นคัดกรองโรคร้ายหรือ fraud screening แต่ recall สูงอย่างเดียวทำได้ง่ายด้วยการทายทุกคนเป็น positive จึงต้องดู precision หรือ false positive burden ร่วมด้วย

### 6.3 Precision

Precision ตอบว่า “ในสิ่งที่โมเดลแจ้งว่า positive มี positive จริงกี่ส่วน”:

$$
\mathrm{Precision}=\frac{TP}{TP+FP}
$$

Precision สำคัญเมื่อการลงมือหลัง alert มีต้นทุนสูง เช่นส่งเคสให้ผู้เชี่ยวชาญตรวจ หรือบล็อกธุรกรรมลูกค้า

### 6.4 Specificity และ False Positive Rate

Specificity ตอบว่า negative จริงถูกปฏิเสธถูกกี่ส่วน:

$$
\mathrm{Specificity}=\mathrm{TNR}=\frac{TN}{TN+FP}
$$

False Positive Rate เป็นส่วนเติมเต็ม:

$$
\mathrm{FPR}=\frac{FP}{FP+TN}=1-\mathrm{Specificity}
$$

Recall มอง positive population ส่วน specificity มอง negative population ทั้งคู่ไม่ขึ้นกับจำนวน prediction ที่โมเดลประกาศโดยตรง

### 6.5 F1-score

F1 เป็น harmonic mean ของ precision และ recall:

$$
F_1=\frac{2PR}{P+R}
$$

Harmonic mean ลงโทษกรณีที่ค่าหนึ่งต่ำมากแรงกว่า arithmetic mean จึงไม่ถูกหลอกด้วยค่าอีกฝั่งที่สูงเพียงด้านเดียว

จากสไลด์หน้า 15:

| Model | Precision | Recall | Arithmetic Mean | F1 |
|---|---:|---:|---:|---:|
| 1 | 0.50 | 0.40 | 0.450 | 0.444 |
| 2 | 0.70 | 0.10 | 0.400 | 0.175 |
| 3 | 0.02 | 1.00 | 0.510 | 0.039 |

Model 3 มี arithmetic mean 0.51 แต่ F1 เพียง 0.039 เพราะ precision ต่ำมาก F1 เหมาะเมื่ออยากสมดุล precision/recall แต่ไม่ใช้ TN จึงไม่ตอบทุกโจทย์

### 6.6 Matthews Correlation Coefficient

MCC ใช้ทั้งสี่ช่องของ confusion matrix:

$$
\mathrm{MCC}=\frac{TP\times TN-FP\times FN}{\sqrt{(TP+FP)(TP+FN)(TN+FP)(TN+FN)}}
$$

ค่าอยู่ระหว่าง -1 ถึง 1:

- 1 คือ prediction สมบูรณ์
- 0 คือไม่มีความสัมพันธ์ดีกว่าการสุ่มตามโครงสร้างนั้น
- -1 คือทำนายกลับด้านสมบูรณ์

MCC มีประโยชน์กับ class imbalance เพราะพิจารณาทั้ง positive และ negative แต่ถ้าตัวส่วนเป็นศูนย์ต้องดูการจัดการของ implementation ไม่ควรคำนวณมือแล้วหารศูนย์ Scikit-learn มี `matthews_corrcoef` ตาม [official API](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.matthews_corrcoef.html)

## 7. Tumor Detection: Metric ต้องตามต้นทุน

ภาพในสไลด์หน้า 14 เปรียบเทียบพื้นที่ tumor จริงสีเหลืองกับพื้นที่ที่โมเดลทำนายสีแดง:

- M1: prediction อยู่ใน tumor แต่ครอบคลุมน้อย - precision สูง, recall ต่ำ
- M2: ครอบคลุม tumor มากขึ้นแต่กินพื้นที่นอก tumor - recall เพิ่ม, precision ลด
- M3: ทำนายพื้นที่กว้างมาก - recall อาจสูงสุด แต่ precision ต่ำ

> **จุดกำกวมในสไลด์:** legend เขียน “Predicted area (Negative)” แต่ภาพและบริบทการคำนวณ precision/recall สื่อว่าพื้นที่สีแดงคือ predicted positive area จึงควรอ่านตามบริบทนี้และไม่แก้ข้อความต้นฉบับโดยเงียบ ๆ

ใน medical screening เราอาจยอม FP เพิ่มเพื่อไม่พลาดผู้ป่วย แต่ใน confirmatory diagnosis หรือ intervention ราคาแพง precision อาจสำคัญขึ้น Metric ที่เหมาะจึงมาจาก decision cost ไม่ใช่เลือกเพราะเป็น metric ยอดนิยม

## 8. ROC Curve และ AUC

ROC curve คำนวณหลาย thresholds แล้วพล็อต:

- แกน x: False Positive Rate
- แกน y: True Positive Rate หรือ Recall

แต่ละจุดคือ operating point หนึ่ง threshold เมื่อ threshold ลด ทั้ง TPR และ FPR มักเพิ่ม เส้นที่โค้งเข้าใกล้มุมซ้ายบนแยก classes ได้ดีกว่าเส้นทแยงแบบ no-skill

ROC-AUC สรุปพื้นที่ใต้เส้น ROC ค่า 1 หมายถึง ranking สมบูรณ์ และ 0.5 ใกล้การสุ่มสำหรับ binary ranking ทั่วไป อีกความหมายคือโอกาสที่ positive ที่สุ่มมาหนึ่งตัวได้รับ score สูงกว่า negative ที่สุ่มมาหนึ่งตัว

ข้อจำกัดคือ ROC-AUC วัด ranking ข้าม thresholds ไม่บอกว่า threshold ใช้งานจริงเหมาะหรือ probability calibrated ดี เมื่อ negative class ใหญ่มาก FPR ต่ำอาจยังหมายถึง FP จำนวนมาก

ดูรายละเอียดการคำนวณได้จาก [scikit-learn ROC-AUC API](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html)

## 9. Precision-Recall Curve

PR curve พล็อต Precision กับ Recall หลาย thresholds จึงโฟกัส positive class โดยตรง:

- threshold สูง: predictions positive น้อย precision มักสูง แต่ recall ต่ำ
- threshold ต่ำ: จับ positive มากขึ้น recall สูง แต่ precision มักลด

เมื่อ positive class rare PR curve มักให้ภาพใช้งานชัดกว่า ROC เพราะ false positives ปรากฏโดยตรงใน precision Baseline precision ของ random rankingสัมพันธ์กับ prevalence ของ positive class ไม่ใช่ 0.5 เสมอ

ไม่ควรเทียบ AUC จาก ROC และ PR เป็นตัวเลขชนิดเดียวกัน ทั้งสองสรุปคนละแกนและตอบคนละคำถาม

| คำถาม | กราฟ/Metric ที่เหมาะ |
|---|---|
| โมเดลจัดอันดับ positive เหนือ negative โดยรวมได้ไหม | ROC-AUC |
| เมื่อ positive rare แล้ว alerts เชื่อถือได้เพียงใด | PR curve / Average Precision |
| Threshold ใช้งานจริงมี FP/FN เท่าใด | Confusion matrix ที่ threshold นั้น |
| Probability 0.8 ถูกประมาณ 80% จริงหรือไม่ | Calibration curve / Brier score |

## 10. End-to-End Evaluation Workflow

Model evaluation ที่ดีทำตามลำดับ:

1. นิยาม prediction target และ positive class
2. กำหนดต้นทุน FP/FN และ metric ก่อนดูผล
3. แยก final test set
4. ใช้ training data กับ validation/CV เพื่อเลือก preprocessing, features, model และ hyperparameters
5. เลือก threshold จาก validation data
6. ล็อก pipeline และ threshold
7. ประเมิน test เพียงครั้งสุดท้าย
8. รายงาน uncertainty, class distribution และข้อจำกัด

ถ้ากลับไปปรับโมเดลหลังเห็น test result ชุดนั้นกลายเป็น development data แล้ว ควรมี test set ใหม่หรือประเมินด้วยกระบวนการที่สะท้อนการใช้งานจริง

Scikit-learn แนะนำให้เลือก scoring function ให้สอดคล้องกับเป้าหมายการทำนายและ decision ที่ตามมา ไม่ใช่ใช้ metric เดียวกับทุกงาน ดู [Metrics and scoring guide](https://scikit-learn.org/stable/modules/model_evaluation.html)

## 11. Guided Lab: Binary Classification

### 11.1 เตรียมข้อมูลและแยก test

ตัวอย่างนี้ใช้ Breast Cancer dataset ที่มากับ scikit-learn เพื่อสาธิต workflow ไม่ใช่เพื่อใช้ตัดสินใจทางการแพทย์จริง

```python
import pandas as pd

from sklearn.datasets import load_breast_cancer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    matthews_corrcoef,
    precision_score,
    recall_score,
    roc_auc_score
)
from sklearn.model_selection import (
    StratifiedKFold,
    cross_validate,
    train_test_split
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

X, y = load_breast_cancer(return_X_y=True)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)
```

`stratify=y` รักษาสัดส่วน classes โดยประมาณ `random_state` ทำให้ split ทำซ้ำได้

### 11.2 Cross-validation บน training set

```python
model = Pipeline([
    ('scale', StandardScaler()),
    (
        'classifier',
        LogisticRegression(max_iter=5_000)
    )
])

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

cv_results = cross_validate(
    model,
    X_train,
    y_train,
    cv=cv,
    scoring=[
        'accuracy',
        'precision',
        'recall',
        'f1',
        'roc_auc'
    ]
)

cv_summary = pd.DataFrame(cv_results).filter(like='test_')
cv_summary.agg(['mean', 'std']).round(4)
```

Scaler อยู่ใน Pipeline จึง fit ใหม่ภายในแต่ละ training fold หาก scale ทั้ง dataset ก่อน CV ค่าเฉลี่ยและส่วนเบี่ยงเบนจาก validation fold จะรั่วเข้า training fold

### 11.3 Final test evaluation

```python
model.fit(X_train, y_train)

y_prob = model.predict_proba(X_test)[:, 1]
y_pred = (y_prob >= 0.50).astype(int)

tn, fp, fn, tp = confusion_matrix(
    y_test,
    y_pred
).ravel()

test_metrics = pd.Series({
    'Accuracy': accuracy_score(y_test, y_pred),
    'Precision': precision_score(y_test, y_pred),
    'Recall': recall_score(y_test, y_pred),
    'F1': f1_score(y_test, y_pred),
    'MCC': matthews_corrcoef(y_test, y_pred),
    'ROC-AUC': roc_auc_score(y_test, y_prob),
    'TN': tn,
    'FP': fp,
    'FN': fn,
    'TP': tp
})

test_metrics.round(4)
```

ROC-AUC รับ continuous score `y_prob` ไม่ใช่ hard label `y_pred` ส่วน confusion matrix metrics ต้องระบุ threshold ก่อน

### 11.4 ทดลอง threshold

```python
threshold_results = []

for threshold in [0.30, 0.50, 0.70]:
    y_pred_threshold = (
        y_prob >= threshold
    ).astype(int)

    threshold_results.append({
        'Threshold': threshold,
        'Precision': precision_score(
            y_test,
            y_pred_threshold
        ),
        'Recall': recall_score(
            y_test,
            y_pred_threshold
        ),
        'F1': f1_score(
            y_test,
            y_pred_threshold
        )
    })

pd.DataFrame(threshold_results).round(4)
```

Code นี้ใช้ test เพื่อ **สาธิตผลของ threshold เท่านั้น** ในงานจริงห้ามเลือก threshold ที่ชนะจากตาราง test ต้องเลือกบน validation data แล้วใช้ test ตรวจครั้งสุดท้าย

### 11.5 Validation checks

```python
assert len(y_test) == len(y_pred)
assert tn + fp + fn + tp == len(y_test)
assert set(y_pred).issubset({0, 1})
assert ((y_prob >= 0) & (y_prob <= 1)).all()
```

การรันโดยไม่ error ไม่ได้พิสูจน์ว่า evaluation ถูกต้อง Assertions ช่วยตรวจรูปร่างและช่วงค่า แต่ยังต้องตรวจ leakage, split strategy และความหมายของ positive class

## 12. Metric Decision Framework

| สถานการณ์ | Metric หลัก | Metric ประกอบ |
|---|---|---|
| Classes สมดุล ต้นทุนใกล้กัน | Accuracy | Confusion matrix |
| พลาด positive ไม่ได้ | Recall | Precision, FN count |
| Alert ผิดมีต้นทุนสูง | Precision | Recall, FP count |
| ต้องสมดุล P/R | F1 | แสดง P และ R แยก |
| Class imbalance และต้องการสรุป label | MCC | Confusion matrix |
| เปรียบเทียบ ranking ทุก threshold | ROC-AUC | PR-AUC |
| Positive rare | PR curve / Average Precision | Recall ที่ precision เป้าหมาย |
| ใช้ probability ตัดสินความเสี่ยง | Log loss / Brier / Calibration | Discrimination metrics |

ควรรายงาน raw counts ด้วย เพราะ precision 90% อาจหมายถึง FP 10 หรือ 100,000 เคส ขึ้นกับ volume

## 13. Validation และ Troubleshooting

| อาการ | สาเหตุที่เป็นไปได้ | แนวทางตรวจ/แก้ |
|---|---|---|
| Accuracy สูงแต่จับ positive ไม่ได้ | class imbalance | confusion matrix, recall, dummy baseline |
| CV สูงแต่ test ต่ำ | overfit hyperparameters หรือ dataset shift | nested validation, ตรวจเวลา/กลุ่ม |
| Score แกว่งตาม random seed | ข้อมูลน้อยหรือ split ไม่เสถียร | repeated CV, รายงาน mean/std |
| Precision หรือ recall เป็นศูนย์ | ไม่มี predicted/actual positive | ตรวจ threshold และ class counts |
| ROC-AUC ดีแต่ precision ต่ำ | positive rare หรือ FP เยอะ | ดู PR curve และ operating threshold |
| Test ดีผิดปกติ | leakage, duplicates, entity overlap | Pipeline, group split, deduplicate |
| Production แย่กว่าทดสอบ | distribution shift | monitor prevalence, features, metrics |
| Threshold 0.5 ไม่เหมาะ | ต้นทุนไม่สมดุล | เลือก threshold บน validation |

## 14. Critical Discussion

### 14.1 Metric เป็นตัวแทนเป้าหมาย

Metric ไม่ใช่ความจริงทั้งหมด แต่เป็นตัวแทนสิ่งที่เราต้องการ optimize หาก metric ไม่ตรง decision model อาจได้คะแนนดีแต่สร้างผลลัพธ์ทางธุรกิจหรือคลินิกที่ไม่ดี

### 14.2 Test score มี uncertainty

Test score เป็น statistic จาก sample หนึ่งชุด ไม่ใช่ค่าคงที่ของโมเดล หาก test set เล็ก ค่าเปลี่ยนได้มากเมื่อเปลี่ยน observations ควรรายงานจำนวนตัวอย่าง, class counts และถ้าเหมาะสม confidence interval หรือ resampling uncertainty

### 14.3 Prediction ไม่ใช่ causation

Model evaluation บอกความสามารถทำนายภายใต้ distribution ที่ทดสอบ ไม่พิสูจน์ว่า features เป็นสาเหตุ และไม่รับประกัน performance หลัง deployment เมื่อประชากร กระบวนการวัด หรือ prevalence เปลี่ยน

### 14.4 Fairness และ subgroup performance

ค่าเฉลี่ยรวมอาจซ่อน failure ใน subgroup ควรตรวจ metrics แยกตามกลุ่มที่เกี่ยวข้องอย่างรับผิดชอบ พร้อม sample size และ uncertainty แต่การใช้ sensitive attributes ต้องคำนึงถึงกฎหมาย ความเป็นส่วนตัว และวัตถุประสงค์ที่ชอบธรรม

## 15. Common Misconceptions

1. **โมเดล accuracy สูงสุดดีที่สุดเสมอ** - ไม่จริง ถ้า classes หรือต้นทุนไม่สมดุล
2. **Hold-out ทำให้ overfit** - ตัว split ไม่ได้ทำ แต่การเลือกซ้ำบน test ทำได้
3. **60/20/20 คือ k-fold CV** - เป็น single train-validation-test split
4. **Recall สูงหมายถึงโมเดลดี** - อาจทายทุกแถว positive ต้องดู precision/FP
5. **ROC-AUC สูงแปลว่า threshold 0.5 ดี** - AUC วัด ranking ข้าม thresholds
6. **F1 รวมทุกช่อง confusion matrix** - F1 ไม่ใช้ TN
7. **Test set ใช้เลือก threshold ได้** - ควรเลือกจาก validation แล้ว test ครั้งสุดท้าย
8. **Probability 0.9 แปลว่าถูก 90%** - ต้องตรวจ calibration แยก

## 16. Likely Exam Focus

> ส่วนนี้อนุมานจากนิยาม สมการ ตาราง และภาพที่ lecture เน้น ไม่ใช่ข้อมูลข้อสอบจริง

- แยกหน้าที่ train, validation และ test
- เปรียบเทียบ hold-out กับ cross-validation
- วินิจฉัย high bias/high variance และเลือกแนวทางแก้
- เติม TP, FP, FN, TN จาก actual/predicted labels
- คำนวณ Accuracy, Recall, Precision, Specificity, FPR, F1 และ MCC
- อธิบายเหตุผลที่ harmonic mean เหมาะกับ F1
- อธิบาย threshold trade-off
- เปรียบเทียบ ROC กับ PR curve
- เลือก metric จากต้นทุน FP/FN และ class imbalance
- ตรวจ data leakage ใน evaluation code

## 17. Progressive Practice พร้อมเฉลย

### ข้อ 1: Confusion matrix

มี TP = 40, FP = 10, FN = 20, TN = 930 จงหา Accuracy, Recall และ Precision

**เฉลย:**

$$
\mathrm{Accuracy}=\frac{40+930}{1000}=0.97
$$

$$
\mathrm{Recall}=\frac{40}{40+20}=0.6667
$$

$$
\mathrm{Precision}=\frac{40}{40+10}=0.80
$$

Accuracy 97% ดูสูง แต่ยังพลาด positive หนึ่งในสาม จึงห้ามอ่าน accuracy เดี่ยว ๆ

### ข้อ 2: F1

ถ้า precision = 0.8 และ recall = 0.5:

$$
F_1=\frac{2(0.8)(0.5)}{0.8+0.5}=0.6154
$$

### ข้อ 3: Bias-variance

โมเดลมี train accuracy 0.99 แต่ validation accuracy 0.72 ควรวินิจฉัยอย่างไร

**เฉลย:** มีสัญญาณ high variance ควรพิจารณาเพิ่มข้อมูล ลด complexity ลด features หรือเพิ่ม regularization โดยยืนยันด้วย validation

### ข้อ 4: Model selection

เหตุใดจึงไม่ควรเลือก polynomial degree จาก test RMSE

**เฉลย:** เมื่อใช้ test เลือก degree ข้อมูล test มีอิทธิพลต่อ model selection แล้ว ค่า test หลังเลือกจึง optimistic ควรเลือกด้วย validation/CV

### ข้อ 5: Threshold

ระบบคัดกรองโรคร้ายมี FN แพงกว่า FP มาก ควรขยับ threshold ทิศใด

**เฉลย:** โดยทั่วไปลด threshold เพื่อเพิ่ม recall และลด FN แต่ต้องวัด FP burden และเลือกจุดจาก validation data

### ข้อ 6: ROC หรือ PR

Fraud rate 0.2% ต้องการรู้ว่า alerts ที่ส่งให้ทีมตรวจมี fraud จริงกี่ส่วน ควรเน้นกราฟใด

**เฉลย:** PR curve เพราะ precision สะท้อนความน่าเชื่อถือของ alerts และ sensitive ต่อ rare positive มากกว่า ROC

## 18. Mini-project: Evaluation Report

เลือก binary classification dataset แล้ว:

1. นิยาม positive class และต้นทุน FP/FN
2. เก็บ final test set ก่อนเริ่มทดลอง
3. สร้าง baseline อย่างน้อยหนึ่งแบบ
4. เปรียบเทียบอย่างน้อยสองโมเดลด้วย stratified CV
5. รายงาน mean และ standard deviation
6. เลือก threshold จาก validation
7. ประเมิน final test ด้วย confusion matrix และ metrics ที่เหมาะ
8. แสดง ROC และ PR curve
9. วิเคราะห์ errors และ subgroup ที่สมเหตุสมผล
10. สรุปข้อจำกัดและ deployment monitoring

| เกณฑ์ | หลักฐาน |
|---|---|
| Evaluation design | test ไม่ถูกใช้เลือก model |
| Reproducibility | ระบุ split, seed, pipeline |
| Metric alignment | อธิบายต้นทุน FP/FN |
| Interpretation | รายงาน counts และ rates |
| Reliability | ตรวจ leakage และ variability |
| Communication | ไม่อ้างเกิน distribution ที่ทดสอบ |

## 19. Mastery Checklist

- [ ] อธิบายความต่าง training, selection และ evaluation ได้
- [ ] แยก train, validation และ test ได้ถูกต้อง
- [ ] อธิบาย k-fold CV และกรณีที่ต้องใช้ grouped/time split ได้
- [ ] วินิจฉัย bias/variance จาก train-validation results ได้
- [ ] สร้าง confusion matrix จาก predictions ได้
- [ ] คำนวณ metrics ทุกตัวใน lecture ได้
- [ ] อธิบาย threshold trade-off ได้
- [ ] เลือก ROC หรือ PR ให้ตรงโจทย์ได้
- [ ] เลือก metric จากต้นทุนความผิดพลาดได้
- [ ] ตรวจ evaluation leakage ใน code ได้

## 20. Key Takeaways

Model evaluation ต้องแยกข้อมูลที่ใช้เรียนรู้ เลือก decision และทดสอบขั้นสุดท้ายออกจากกัน Training score วัดความสามารถจำข้อมูลฝึก ไม่ใช่หลักฐานของ generalization

ไม่มี metric เดียวดีที่สุด Accuracy, precision, recall, F1, MCC, ROC-AUC และ PR curveตอบคำถามต่างกัน การเลือกที่ถูกเริ่มจาก positive class, prevalence, ต้นทุน FP/FN และ decision ที่จะเกิดหลัง prediction

## 21. Glossary

| คำศัพท์ | ความหมาย |
|---|---|
| Generalization | ความสามารถกับข้อมูลใหม่ |
| Hold-out | การแบ่งข้อมูลครั้งเดียว |
| Validation set | ชุดเลือก model/hyperparameters |
| Test set | ชุดประเมินสุดท้าย |
| Cross-validation | หมุน validation หลาย folds |
| Bias | ความผิดจากข้อจำกัดของโมเดล |
| Variance | ความไวต่อ sample ฝึก |
| Threshold | จุดตัด score เป็น class |
| Confusion matrix | ตารางนับ actual เทียบ prediction |
| Precision | สัดส่วน predicted positive ที่ถูก |
| Recall | สัดส่วน actual positive ที่จับได้ |
| Specificity | สัดส่วน actual negative ที่ปฏิเสธถูก |
| F1 | Harmonic mean ของ precision/recall |
| MCC | correlation-based metric จากสี่ช่อง |
| ROC curve | TPR เทียบ FPR หลาย thresholds |
| PR curve | Precision เทียบ Recall หลาย thresholds |
| Calibration | ความสอดคล้อง probability กับความถี่จริง |

## 22. Source Coverage Audit

| เนื้อหาใน lecture | ส่วนใน Master Note | สถานะ |
|---|---|---|
| Model complexity และ model choice | ส่วน 1 | ครบ |
| Hold-out 80/20 | ส่วน 2.2 | ครบและแก้ความเข้าใจ overfit |
| Training/validation/test 60/20/20 | ส่วน 2.3 | ครบและชี้ศัพท์ |
| Cross-validation | ส่วน 2.4 | ขยายเป็น k-fold |
| Bias vs variance | ส่วน 3 | ครบ |
| Polynomial degree diagnosis | ส่วน 3.1 | ครบ |
| Ridge lambda diagnosis | ส่วน 3.2 | ครบ |
| Training data size | ส่วน 3.3 | ครบ |
| แนวทางแก้ bias/variance | ส่วน 3.4 | ครบ |
| Confusion matrix | ส่วน 5 | ครบ |
| Accuracy, Recall, Precision examples | ส่วน 5-6 | คำนวณครบ |
| Sensitivity, Specificity, FPR | ส่วน 6 | ครบ |
| MCC | ส่วน 6.6 | ครบและแปลผล |
| Tumor detection diagram | ส่วน 7 | ครบพร้อมระบุ legend กำกวม |
| F1 table | ส่วน 6.5 | คำนวณครบ |
| ROC/AUC | ส่วน 8 | ครบและขยายข้อจำกัด |
| Precision-Recall curve | ส่วน 9 | ครบและเชื่อม imbalance |
| Raschka reference | References | ครบ |

## References

1. Ekarat Rattagan. *Week 7: Model Training and Evaluation*. DADS6003 Applied Machine Learning, 12 September 2025.
2. Raschka, S. [Model Evaluation, Model Selection, and Algorithm Selection in Machine Learning](https://arxiv.org/abs/1811.12808). arXiv:1811.12808, 2018.
3. Scikit-learn developers. [Cross-validation: Evaluating Estimator Performance](https://scikit-learn.org/stable/modules/cross_validation.html).
4. Scikit-learn developers. [Metrics and Scoring](https://scikit-learn.org/stable/modules/model_evaluation.html).
5. Scikit-learn developers. [Matthews Correlation Coefficient](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.matthews_corrcoef.html).
6. Scikit-learn developers. [ROC-AUC Score](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html).
