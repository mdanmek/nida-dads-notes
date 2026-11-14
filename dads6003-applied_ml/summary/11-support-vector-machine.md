# Support Vector Machine (SVM)

> บทเรียนนี้เรียบเรียงจากสไลด์ Week 12: Support Vector Machine (SVM) ของรายวิชา DADS6003 และเติมคำอธิบายที่จำเป็นสำหรับการอ่านด้วยตนเอง เนื้อหาหลักครอบคลุมเส้นแบ่งข้อมูล, margin, support vectors, hard/soft margin, hinge loss, kernel และการเลือกใช้ SVM ในงานจริง

## 1. ปัญหาหลัก: เส้นแบ่งแบบใดจึงจะทำนายข้อมูลใหม่ได้ดี

สมมติว่าเรามีข้อมูลสองกลุ่ม เช่น อีเมลปกติกับสแปม แต่ละตัวอย่างถูกแทนด้วย feature vector $\mathbf{x}$ และมี class label $y$ ซึ่งกำหนดเป็น $+1$ หรือ $-1$ หากวาดข้อมูลที่มีสอง features ลงบนกราฟ เราอาจหาเส้นได้หลายเส้นที่แบ่งข้อมูลฝึกออกจากกันโดยไม่ผิดเลย คำถามสำคัญจึงไม่ใช่เพียงว่า “เส้นใดแบ่ง training data ได้” แต่คือ “เส้นใดน่าจะยังแบ่งข้อมูลใหม่ได้ดี”

Support Vector Machine หรือ SVM ตอบคำถามนี้ด้วยหลัก **maximum margin**: เลือก decision boundary ที่เว้นช่องว่างจากตัวอย่างที่อยู่ใกล้เส้นที่สุดของทั้งสองคลาสให้กว้างที่สุด ช่องว่างนี้เรียกว่า **margin** ส่วนตัวอย่างที่เป็นผู้กำหนดขอบ margin เรียกว่า **support vectors**

แนวคิดนี้ทำให้ SVM ต่างจากการหาเส้นที่เพียงแค่จำแนก training data ถูกทั้งหมด เพราะ SVM สนใจ “ความมั่นคง” ของเส้นแบ่งด้วย หากเส้นอยู่ชิดตัวอย่างบางจุดมาก การขยับข้อมูลเพียงเล็กน้อยอาจทำให้ทำนายผิด แต่เส้นที่มี margin กว้างจะมีพื้นที่เผื่อมากกว่า

SVM เป็น supervised learning algorithm ที่ใช้ได้ทั้ง classification และ regression แต่บทนี้เน้น **binary classification** ตามสไลด์ โดยมีข้อมูลฝึก

$$
\{(\mathbf{x}_i,y_i)\}_{i=1}^{N},\quad \mathbf{x}_i\in\mathbb{R}^{d},\quad y_i\in\{-1,+1\}
$$

$N$ คือจำนวนตัวอย่าง และ $d$ คือจำนวน features ของแต่ละตัวอย่าง

## 2. จากเส้นตรงไปสู่ Hyperplane

### 2.1 Decision boundary คืออะไร

ในข้อมูลสองมิติ decision boundary เป็นเส้นตรง ในสามมิติเป็นระนาบ และเมื่อมีมากกว่าสามมิติจะเรียกรวมว่า **hyperplane** สมการของ hyperplane คือ

$$
\mathbf{w}^{T}\mathbf{x}+b=0
$$

ความหมายของสัญลักษณ์มีดังนี้

| สัญลักษณ์ | ความหมาย |
|---|---|
| $\mathbf{x}$ | feature vector ของตัวอย่างหนึ่งรายการ |
| $\mathbf{w}$ | weight vector ซึ่งกำหนดทิศตั้งฉากกับ hyperplane |
| $b$ | bias หรือ intercept ซึ่งเลื่อนตำแหน่ง hyperplane |
| $\mathbf{w}^{T}\mathbf{x}$ | dot product ระหว่าง weights กับ features |

ตัวอย่างจากสไลด์ใช้เส้น

$$
4x_1+3x_2-24=0
$$

ดังนั้น $\mathbf{w}=[4,3]^T$ และ $b=-24$ หากแทนจุด $\mathbf{x}=[3,2]^T$ จะได้

$$
f(\mathbf{x})=4(3)+3(2)-24=-6
$$

ค่าติดลบหมายความว่าจุดอยู่ด้านหนึ่งของเส้น หากแทนจุด $\mathbf{x}=[6,2]^T$ จะได้

$$
f(\mathbf{x})=4(6)+3(2)-24=6
$$

จุดนี้อยู่คนละด้านกับจุดแรก การทำนายแบบ binary จึงเขียนได้ว่า

$$
\hat{y}=\mathrm{sign}(\mathbf{w}^{T}\mathbf{x}+b)
$$

ถ้า decision score เป็นบวก โมเดลทำนาย $+1$ ถ้าเป็นลบ โมเดลทำนาย $-1$ และถ้าเท่ากับศูนย์ จุดอยู่บน decision boundary พอดี ขนาดของ score สื่อว่าจุดอยู่ห่างจากขอบเขตในทิศทางของ $\mathbf{w}$ มากเพียงใด แต่ยังไม่ใช่ probability

### 2.2 เหตุใดต้องสนใจขนาดของ $\mathbf{w}$

สมการ $\mathbf{w}^{T}\mathbf{x}+b=0$ สามารถคูณทั้งสมการด้วยค่าคงที่บวกใด ๆ โดยยังได้เส้นเดิม เช่น $4x_1+3x_2-24=0$ กับ $8x_1+6x_2-48=0$ เป็นเส้นเดียวกัน ดังนั้นค่าของ decision score อย่างเดียวไม่ใช่ระยะทางทางเรขาคณิต

ระยะตั้งฉากจากจุด $\mathbf{x}$ ถึง hyperplane คือ

$$
\mathrm{distance}(\mathbf{x})=\frac{|\mathbf{w}^{T}\mathbf{x}+b|}{\|\mathbf{w}\|}
$$

ตัวหาร $\|\mathbf{w}\|$ ทำให้ระยะทางไม่เปลี่ยนเมื่อเราคูณสมการทั้งชุดด้วยค่าคงที่ นี่เป็นเหตุผลที่ norm ของ weight vector ปรากฏอยู่ใน objective function ของ SVM

## 3. Margin และ Support Vectors

SVM กำหนดเส้นขนานสองเส้นรอบ decision boundary ดังนี้

$$
\mathbf{w}^{T}\mathbf{x}+b=+1
$$

$$
\mathbf{w}^{T}\mathbf{x}+b=-1
$$

เส้นแรกเป็นขอบ margin ฝั่งคลาส $+1$ และเส้นที่สองเป็นขอบ margin ฝั่งคลาส $-1$ เมื่อนำ label มารวมกับเงื่อนไขทั้งสอง เราเขียนได้ในบรรทัดเดียวว่า

$$
y_i(\mathbf{w}^{T}\mathbf{x}_i+b)\geq 1
$$

ถ้าตัวอย่างอยู่บนขอบ margin พอดี จะเกิด equality

$$
y_i(\mathbf{w}^{T}\mathbf{x}_i+b)=1
$$

ตัวอย่างเหล่านี้คือ support vectors ในกรณีที่ข้อมูลแยกได้สมบูรณ์ จุดที่อยู่ไกลจากขอบไม่เป็นผู้กำหนดตำแหน่งเส้นแบ่งโดยตรงเท่ากับจุดที่ชิด margin เพราะ objective สนใจข้อจำกัดที่ตึงที่สุด

ระยะจาก decision boundary ไปยังขอบด้านหนึ่งเท่ากับ $1/\|\mathbf{w}\|$ ดังนั้นความกว้างรวมระหว่างขอบทั้งสองคือ

$$
\mathrm{margin\ width}=\frac{2}{\|\mathbf{w}\|}
$$

สมการนี้ให้ข้อสรุปสำคัญว่า หากต้องการ margin กว้าง เราต้องทำให้ $\|\mathbf{w}\|$ เล็ก การ maximize margin จึงเขียนเป็นปัญหา minimize $\|\mathbf{w}\|^2/2$ ได้ เครื่องหมาย $1/2$ ไม่เปลี่ยนตำแหน่งคำตอบ แต่ทำให้อนุพันธ์เรียบง่ายขึ้น

## 4. Hard-margin SVM

### 4.1 ปัญหา Optimization

Hard-margin SVM ใช้ objective และ constraints ต่อไปนี้

$$
\min_{\mathbf{w},b}\frac{1}{2}\|\mathbf{w}\|^2
$$

ภายใต้เงื่อนไข

$$
y_i(\mathbf{w}^{T}\mathbf{x}_i+b)\geq 1,\quad i=1,\ldots,N
$$

objective บอกให้ margin กว้างที่สุด ส่วน constraint บังคับให้ทุกตัวอย่างอยู่ถูกด้านและอยู่นอกหรือบนขอบ margin การหาคำตอบจึงเป็นการประนีประนอมภายใต้กติกาที่เข้มงวด แต่ใน hard margin ยัง **ไม่ยอมให้มีข้อผิดพลาดหรือการละเมิด margin เลย**

### 4.2 สมมติฐานและข้อจำกัด

Hard margin ใช้ได้เมื่อข้อมูล **linearly separable** คือมี hyperplane อย่างน้อยหนึ่งเส้นที่แบ่งสองคลาสได้สมบูรณ์ หากมี outlier เพียงจุดเดียวหรือคลาสทับซ้อนกัน constraints อาจไม่มีคำตอบที่เป็นไปได้ หรือเส้นที่ได้อาจถูก outlier บังคับจน margin แคบและ generalize ไม่ดี

> **หมายเหตุเพื่อความแม่นยำ:** สไลด์ระบุว่า hard margin ไม่ยอมให้จุด “touch the margin” แต่จาก constraint จุดสามารถอยู่บนขอบ margin ได้เมื่อ $y_i(\mathbf{w}^{T}\mathbf{x}_i+b)=1$ และจุดเหล่านี้คือ support vectors สิ่งที่ hard margin ไม่ยอมคือการล้ำเข้า margin หรือการจำแนกผิด

จุดนี้นำไปสู่ soft margin: แทนที่จะยืนยันว่าทุกจุดต้องถูกต้อง เราอนุญาตให้บางจุดละเมิดกติกาได้ แต่ต้องจ่าย penalty ตามระดับการละเมิด

## 5. Soft-margin SVM

### 5.1 Slack variable บอกอะไร

เพิ่มตัวแปร $\xi_i$ ให้แต่ละตัวอย่างเพื่อวัดการละเมิด margin

$$
y_i(\mathbf{w}^{T}\mathbf{x}_i+b)\geq 1-\xi_i,\quad \xi_i\geq 0
$$

การอ่านค่า $\xi_i$ ช่วยให้เห็นสถานะของจุดได้ชัดเจน

| ค่า $\xi_i$ | ความหมาย |
|---|---|
| $\xi_i=0$ | อยู่ถูกด้านและไม่ล้ำเข้า margin |
| $0<\xi_i<1$ | อยู่ถูกด้าน แต่ล้ำเข้า margin |
| $\xi_i=1$ | อยู่บน decision boundary |
| $\xi_i>1$ | อยู่ผิดด้านของ decision boundary และถูกจำแนกผิด |

objective ของ soft-margin SVM คือ

$$
\min_{\mathbf{w},b,\boldsymbol{\xi}}\frac{1}{2}\|\mathbf{w}\|^2+C\sum_{i=1}^{N}\xi_i
$$

พจน์แรกสนับสนุน margin ที่กว้าง ส่วนพจน์ที่สองลงโทษการละเมิด margin ค่า $C$ จึงทำหน้าที่กำหนดน้ำหนักระหว่างสองเป้าหมาย

### 5.2 ทำความเข้าใจค่า $C$

| ค่า $C$ | สิ่งที่โมเดลให้ความสำคัญ | ผลที่มักเกิด |
|---|---|---|
| สูง | ลงโทษการละเมิดหนัก | พยายามจำแนก training data ให้ถูกมากขึ้น, margin อาจแคบ, ไวต่อ outlier มากขึ้น |
| ต่ำ | ยอมรับการละเมิดมากขึ้น | margin มักกว้างขึ้น, regularization แรงขึ้น, boundary เรียบและยืดหยุ่นต่อ noise มากขึ้น |

คำว่า “$C$ สูงเหมือน hard margin” เป็น intuition ไม่ใช่ความเท่ากันโดยสมบูรณ์ เพราะ soft-margin formulation ยังมี slack variables อยู่ และข้อมูลที่แยกไม่ได้ก็ยังไม่สามารถกลายเป็น hard-margin problem ที่ feasible ได้เพียงเพราะเพิ่ม $C$

ไม่ควรสรุปว่า $C$ สูงหรือ $C$ ต่ำดีกว่าเสมอ ค่าเหมาะสมขึ้นกับข้อมูล จึงต้องเลือกด้วย validation data หรือ cross-validation โดยห้ามใช้ test set มาปรับค่า เพราะจะทำให้ผลประเมินมองโลกในแง่ดีเกินจริง

## 6. Hinge Loss: เปลี่ยน Constraint ให้เป็น Cost

soft-margin SVM สามารถเขียนด้วย hinge loss ได้ดังนี้

$$
\min_{\mathbf{w},b}\frac{1}{2}\|\mathbf{w}\|^2+C\sum_{i=1}^{N}\max(0,1-y_i(\mathbf{w}^{T}\mathbf{x}_i+b))
$$

กำหนด margin score ของตัวอย่างที่ $i$ เป็น

$$
m_i=y_i(\mathbf{w}^{T}\mathbf{x}_i+b)
$$

hinge loss ของตัวอย่างนั้นคือ

$$
L_i=\max(0,1-m_i)
$$

ตัวอย่างต่อไปนี้แสดงวิธีอ่าน loss โดยไม่ต้องวาดกราฟ

| $m_i$ | สถานะ | $L_i$ |
|---:|---|---:|
| 1.6 | ถูกด้านและพ้น margin | 0 |
| 1.0 | อยู่บนขอบ margin | 0 |
| 0.4 | ถูกคลาส แต่ล้ำเข้า margin | 0.6 |
| 0.0 | อยู่บน decision boundary | 1.0 |
| -0.5 | ถูกจำแนกผิด | 1.5 |

จุดที่สำคัญคือ SVM ไม่ได้ให้ loss เป็นศูนย์ทันทีที่ทำนาย class ถูก หากจุดถูกด้านแต่ยังอยู่ใน margin โมเดลยังลงโทษจุดนั้นอยู่ เพราะต้องการคำตอบที่ไม่เพียงถูก แต่ควรอยู่ห่าง boundary พอสมควร

### 6.1 Subgradient และการอัปเดตแบบ Gradient-based

hinge loss มีมุมหักที่ $m_i=1$ จึงใช้ **subgradient** แทนอนุพันธ์ปกติที่จุดนั้น สำหรับตัวอย่างหนึ่งรายการ หาก $m_i<1$ ตัวอย่างมีส่วนผลักให้ weights เปลี่ยนเพื่อเพิ่ม margin แต่ถ้า $m_i>1$ ตัวอย่างนั้นไม่มี hinge-loss gradient เหลืออยู่ และมีเพียง regularization ที่ดึง weights ให้เล็กลง

ในมุมมองแบบรวมทุกตัวอย่าง subgradient เขียนได้เป็น

$$
\nabla_{\mathbf{w}}=\mathbf{w}-C\sum_{i:m_i<1}y_i\mathbf{x}_i
$$

$$
\nabla_b=-C\sum_{i:m_i<1}y_i
$$

จากนั้นอัปเดตด้วย learning rate $\alpha$

$$
\mathbf{w}\leftarrow\mathbf{w}-\alpha\nabla_{\mathbf{w}}
$$

$$
b\leftarrow b-\alpha\nabla_b
$$

คำอธิบายเพิ่มเติม: สมการนี้ช่วยให้เข้าใจทิศทางการเรียนรู้ แต่ `SVC` ใน scikit-learn ไม่ได้ฝึกด้วย gradient descent ทั่วไป ส่วน `SGDClassifier(loss='hinge')` เป็นตัวเลือกที่ใช้ stochastic gradient descent เพื่อเรียนรู้ linear SVM โดยตรง

## 7. เมื่อเส้นตรงไม่พอ: Feature Mapping และ Kernel Trick

### 7.1 เหตุใดข้อมูลวงกลมจึงแบ่งด้วยเส้นตรงไม่ได้

สมมติจุดสีน้ำเงินอยู่ตรงกลางและจุดสีแดงล้อมเป็นวงแหวน ไม่ว่าเราจะลากเส้นตรงอย่างไร ก็ไม่สามารถแยกวงในกับวงนอกได้สมบูรณ์ แต่ถ้าสร้าง feature ใหม่

$$
z=x_1^2+x_2^2
$$

จุดใกล้ศูนย์จะมี $z$ ต่ำ ส่วนจุดวงนอกจะมี $z$ สูง ทำให้แบ่งด้วย threshold บนแกน $z$ ได้ ปัญหาที่ nonlinear ในพื้นที่เดิมจึงอาจเป็น linear ใน feature space ใหม่

### 7.2 Kernel ไม่จำเป็นต้องสร้าง feature ใหม่ออกมาตรง ๆ

SVM ในรูป dual formulation ใช้ข้อมูลผ่าน dot product ระหว่างตัวอย่าง หากเราต้องการ mapping $\phi(\mathbf{x})$ ไปยัง feature space ใหม่ สิ่งที่จำเป็นคือ

$$
\phi(\mathbf{x})^{T}\phi(\mathbf{x}')
$$

kernel function $K(\mathbf{x},\mathbf{x}')$ คำนวณค่านี้ได้โดยตรงโดยไม่ต้องสร้างพิกัดทุกมิติของ $\phi(\mathbf{x})$ ออกมาจริง วิธีนี้เรียกว่า **kernel trick** ข้อดีจึงไม่ใช่แค่ “ฉายข้อมูลไปมิติสูง” แต่คือการคำนวณความคล้ายใน feature space นั้นอย่างมีประสิทธิภาพ แนวคิดการสร้าง linear decision surface ใน feature space มิติสูงเป็นแกนสำคัญของงานต้นฉบับ [Support-Vector Networks](https://doi.org/10.1007/BF00994018)

ฟังก์ชัน kernel ต้องมีคุณสมบัติทางคณิตศาสตร์ที่สอดคล้องกับ inner product; ไม่ใช่ similarity function ใด ๆ ก็ใช้เป็น kernel ได้เสมอ

### 7.3 Kernel ที่พบบ่อย

**Linear kernel**

$$
K(\mathbf{x},\mathbf{x}')=\mathbf{x}^{T}\mathbf{x}'
$$

เหมาะเมื่อความสัมพันธ์ใกล้เชิงเส้น, features มีจำนวนมาก หรืออยากได้โมเดลที่ตีความ weights ได้ง่ายกว่า nonlinear kernel

**Polynomial kernel**

$$
K(\mathbf{x},\mathbf{x}')=(\gamma\mathbf{x}^{T}\mathbf{x}'+c_0)^d
$$

$d$ คือ degree, $\gamma$ ควบคุมขนาดอิทธิพลของ dot product และ $c_0$ ควบคุมบทบาทของพจน์ degree ต่ำ Polynomial kernel เหมาะเมื่อคาดว่าปฏิสัมพันธ์ระหว่าง features มีโครงสร้างคล้าย polynomial แต่ degree สูงอาจทำให้ boundary ซับซ้อนและไวต่อ scaling

**Radial Basis Function หรือ RBF kernel**

$$
K(\mathbf{x},\mathbf{x}')=\exp(-\gamma\|\mathbf{x}-\mathbf{x}'\|^2)
$$

RBF วัดความคล้ายตามระยะห่าง จุดที่ใกล้กันให้ค่า kernel ใกล้ 1 และค่าจะลดลงเมื่อห่างกัน

- $\gamma$ สูง: อิทธิพลของแต่ละตัวอย่างแคบ boundary จึงคดเคี้ยวและเสี่ยง overfit มากขึ้น
- $\gamma$ ต่ำ: อิทธิพลแผ่กว้าง boundary เรียบขึ้นและอาจ underfit

**Sigmoid kernel**

$$
K(\mathbf{x},\mathbf{x}')=\tanh(\gamma\mathbf{x}^{T}\mathbf{x}'+c_0)
$$

มีรูปคล้าย activation ของ neural network แต่ต้องระวังว่าค่าพารามิเตอร์บางช่วงอาจไม่ทำให้ฟังก์ชันนี้เป็น valid kernel

### 7.4 ความสัมพันธ์ระหว่าง $C$ กับ $\gamma$

สำหรับ RBF SVM ค่า $C$ และ $\gamma$ ต้องพิจารณาร่วมกัน เพราะ $C$ ควบคุมความเข้มของ penalty ต่อข้อผิดพลาด ส่วน $\gamma$ ควบคุมความเฉพาะที่ของอิทธิพลจากแต่ละตัวอย่าง โมเดลที่ $C$ สูงและ $\gamma$ สูงอาจสร้าง boundary ที่ตาม training data ละเอียดมาก ในทางกลับกัน $C$ ต่ำและ $\gamma$ ต่ำอาจเรียบจนแยกโครงสร้างที่สำคัญไม่ได้ จึงควรค้นหาคู่ค่าด้วย cross-validation ไม่ควรปรับทีละตัวโดยสรุปผลแยกขาดจากกัน

## 8. เหตุใด Feature Scaling จึงสำคัญมาก

SVM ใช้ dot product และระยะห่าง ถ้า feature หนึ่งมีช่วง 0-100,000 แต่อีก feature อยู่ 0-1 feature แรกอาจครอบงำระยะทาง แม้ไม่ได้มีความสำคัญต่อเป้าหมายมากกว่า ตัวอย่างเช่น `annual_income` อาจกลบ `debt_ratio` เพียงเพราะหน่วยต่างกัน

วิธีที่ใช้บ่อยคือ standardization

$$
z=\frac{x-\mu}{\sigma}
$$

$\mu$ คือค่าเฉลี่ยของ feature ใน training set และ $\sigma$ คือส่วนเบี่ยงเบนมาตรฐาน ต้อง `fit` scaler ด้วย training data เท่านั้น แล้วใช้ scaler เดิม `transform` validation/test data เพื่อป้องกัน data leakage

การใช้ `Pipeline` ช่วยบังคับลำดับนี้ให้ถูกต้องใน cross-validation เพราะ scaler จะถูก fit ใหม่ภายในแต่ละ training fold แทนที่จะเห็นข้อมูลทุก fold ล่วงหน้า ดูรูปแบบการใช้งานและข้อควรระวังเพิ่มเติมได้จาก [scikit-learn SVM User Guide](https://scikit-learn.org/stable/modules/svm.html)

## 9. ขั้นตอนสร้าง SVM อย่างถูกต้อง

ลำดับที่เหมาะสมคือ

1. แยก test set ไว้สำหรับประเมินครั้งสุดท้าย
2. แบ่งข้อมูลฝึกด้วย cross-validation เพื่อเลือก preprocessing, kernel และ hyperparameters
3. ใช้ `Pipeline` รวม scaling กับโมเดล
4. เปรียบเทียบค่า validation metric ที่เหมาะกับโจทย์ เช่น accuracy, precision, recall หรือ F1
5. เลือกโมเดลแล้ว fit ด้วย training data ทั้งหมด
6. ประเมิน test set เพียงครั้งสุดท้าย พร้อม confusion matrix และการวิเคราะห์ข้อผิดพลาด

ตัวอย่างต่อไปนี้ใช้ Iris เพื่อสาธิต workflow ไม่ใช่เพื่อประกาศว่า RBF เป็น kernel ที่ดีที่สุดเสมอ

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report

X, y = load_iris(return_X_y=True)

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('svm', SVC())
])

param_grid = [
    {
        'svm__kernel': ['linear'],
        'svm__C': [0.1, 1, 10]
    },
    {
        'svm__kernel': ['rbf'],
        'svm__C': [0.1, 1, 10],
        'svm__gamma': ['scale', 0.1, 1]
    }
]

search = GridSearchCV(
    pipeline,
    param_grid=param_grid,
    cv=5,
    scoring='accuracy'
)

search.fit(X_train, y_train)
y_pred = search.predict(X_test)

print('Best parameters:', search.best_params_)
print('Test accuracy:', accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))
```

สิ่งที่ควรอ่านจากผลลัพธ์ไม่ใช่ accuracy เพียงค่าเดียว ต้องดูว่าแต่ละคลาสมี precision และ recall อย่างไร มี class ใดถูกสับสนเป็นประจำหรือไม่ และผล cross-validation ต่างจาก test performance มากเพียงใด หากข้อมูลไม่สมดุล ควรเลือก metric ให้ตรงต้นทุนของ false positive และ false negative และอาจพิจารณา `class_weight='balanced'`

## 10. เลือก SVC, LinearSVC หรือ SGDClassifier อย่างไร

ตารางในสไลด์เปรียบเทียบ classifier สามชนิด แต่ควรอ่านอย่างละเอียดว่า “SVC รองรับ nonlinear kernel” ไม่ได้แปลว่า SVC ใช้ได้เฉพาะ nonlinear เพราะสามารถกำหนด `kernel='linear'` ได้เช่นกัน

| โมเดล | Boundary/Kernel | จุดเด่น | ข้อจำกัดและสถานการณ์ |
|---|---|---|---|
| `SVC` | linear, polynomial, RBF, sigmoid หรือ custom kernel | รองรับ nonlinear boundary และเข้าถึง support vectors ได้ | เวลา fit เพิ่มเร็วเมื่อจำนวนตัวอย่างมาก เหมาะกับข้อมูลขนาดเล็กถึงกลางมากกว่า |
| `LinearSVC` | linear | ออกแบบมาสำหรับ linear classification และขยายกับจำนวนตัวอย่างได้ดีกว่า kernel SVC | ไม่มี kernel trick และ API/ค่า loss เริ่มต้นต่างจาก `SVC(kernel='linear')` |
| `SGDClassifier(loss='hinge')` | linear | ฝึกแบบ mini-batch/online ได้และเหมาะกับข้อมูลขนาดใหญ่มากหรือ sparse | ไวต่อ scaling, learning schedule และ hyperparameters; คำตอบอาจไม่เหมือน `LinearSVC` ทุกประการ |

ดังนั้น “SVM” คือแนวคิดของ objective และ margin ส่วน `SVC`, `LinearSVC` และ `SGDClassifier` คือ implementation ที่ใช้วิธี optimization และข้อจำกัดต่างกัน

## 11. ข้อดี ข้อจำกัด และการตัดสินใจเลือกใช้

### 11.1 ข้อดี

SVM มีประสิทธิภาพในข้อมูลมิติสูง เช่น text classification ที่มี features จำนวนมาก และ maximum-margin principle ให้กรอบคิดที่ชัดเจนเกี่ยวกับความสามารถในการ generalize เมื่อใช้ kernel สามารถสร้าง nonlinear boundary ได้โดยไม่ต้องระบุ features ใหม่ทั้งหมดด้วยตนเอง นอกจากนี้คำตอบพึ่งพาตัวอย่างฝึกบางส่วนที่เป็น support vectors ในการสร้าง decision function

### 11.2 ข้อจำกัด

kernel SVM อาจฝึกช้าและใช้หน่วยความจำมากเมื่อจำนวนตัวอย่างสูงมาก เอกสารของ `SVC` ระบุว่าเวลา fit เพิ่มอย่างน้อยในระดับกำลังสองตามจำนวนตัวอย่าง และแนะนำ `LinearSVC` หรือ `SGDClassifier` สำหรับข้อมูลขนาดใหญ่กว่า ([SVC API Reference](https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html)) การเลือก kernel, $C$ และ $\gamma$ ต้องอาศัยการปรับอย่างระมัดระวัง โมเดลยังไวต่อ feature scale, outlier และข้อมูลที่คลาสทับซ้อนกันมาก อีกทั้ง decision score ไม่ใช่ probability โดยธรรมชาติ หากต้องการ probability ต้องมีขั้น calibration เพิ่มเติม ซึ่งเพิ่มต้นทุนและควรตรวจสอบ calibration quality ด้วย

### 11.3 Decision framework

| สถานการณ์ | ตัวเลือกเริ่มต้นที่สมเหตุผล | เหตุผล |
|---|---|---|
| features มาก, sparse เช่น TF-IDF | LinearSVC หรือ SGDClassifier | linear boundary มักเพียงพอและขยายกับข้อมูลได้ดีกว่า kernel SVC |
| ข้อมูลขนาดเล็กถึงกลางและ boundary ซับซ้อน | SVC with RBF | สร้าง nonlinear boundary ได้ยืดหยุ่น |
| ต้องตีความทิศทางของ feature weights | LinearSVC หรือ linear model | nonlinear kernel ไม่มี weight ต่อ original feature ที่ตีความตรงไปตรงมา |
| ข้อมูลมีตัวอย่างจำนวนมหาศาล | SGDClassifier หรือวิธี scalable อื่น | kernel SVC มักมีต้นทุนการฝึกสูงเกินไป |
| ต้องการ probability ที่ตีความได้โดยตรง | Logistic Regression หรือ calibrated classifier | SVM ให้ margin score เป็นหลัก ไม่ใช่ probability โดยกำเนิด |

## 12. การเปรียบเทียบกับ Logistic Regression

SVM และ Logistic Regression ต่างสร้าง linear decision boundary ได้ แต่เรียนรู้ด้วย loss ต่างกัน Logistic Regression ใช้ log loss และสร้าง probability model โดยตรง ส่วน linear SVM ใช้ hinge loss และเน้น margin ตัวอย่างที่ถูกจำแนกถูกและพ้น margin แล้วจะไม่มี hinge loss เพิ่ม ในขณะที่ทุกตัวอย่างยังมีส่วนต่อ log loss แม้ขนาดอิทธิพลจะลดลงเมื่อโมเดลมั่นใจและถูกต้อง

จึงไม่ควรบอกว่า SVM “แม่นกว่า” Logistic Regression เสมอ การเลือกขึ้นกับข้อมูล, metric, calibration, ความต้องการตีความ, ขนาดข้อมูล และผล validation จริง

## 13. จุดที่มักเข้าใจผิด

1. **Support vectors ไม่จำเป็นต้องเป็นจุดที่ทำนายผิด** จุดบน margin หรือภายใน margin ก็เป็น support vectors ได้
2. **decision score ไม่ใช่ probability** เครื่องหมายใช้เลือกคลาส ส่วนขนาดเป็นความมั่นใจเชิงระยะจาก boundary ในสเกลของโมเดล
3. **ค่า $C$ สูงไม่ได้แปลว่าโมเดลดีกว่า** มันเพียงลงโทษข้อผิดพลาดมากขึ้นและอาจ overfit
4. **RBF ไม่ได้ดีที่สุดสำหรับทุกข้อมูล** nonlinear flexibility มีต้นทุนด้าน tuning, เวลา และ interpretability
5. **ต้อง scale ก่อน cross-validation อย่างถูกวิธี** ควรใส่ scaler ใน Pipeline ไม่ใช่ fit scaler ด้วยข้อมูลทั้งหมดก่อนแบ่ง folds
6. **SVC ไม่ได้ใช้ gradient descent เสมอ** gradient ของ hinge loss เป็นแนวคิดสำคัญ แต่ implementation แต่ละชนิดมี optimization method ต่างกัน
7. **ข้อมูลมิติสูงไม่รับประกันว่า SVM จะดี** ต้องพิจารณาจำนวนตัวอย่าง, noise, sparsity และความเหมาะสมของ kernel ด้วย

## 14. Worked Example: อ่าน margin score และ hinge loss

กำหนด

$$
\mathbf{w}=[2,-1]^T,\quad b=-1
$$

และมีตัวอย่าง $\mathbf{x}=[3,2]^T$ ที่มี label $y=+1$

**ขั้นที่ 1: คำนวณ decision score**

$$
f(\mathbf{x})=2(3)-1(2)-1=3
$$

score เป็นบวก จึงทำนาย $+1$ ซึ่งตรงกับ label จริง

**ขั้นที่ 2: คำนวณ margin score**

$$
m=yf(\mathbf{x})=(+1)(3)=3
$$

เพราะ $m>1$ จุดอยู่ถูกด้านและพ้น margin

**ขั้นที่ 3: คำนวณ hinge loss**

$$
L=\max(0,1-3)=0
$$

**ขั้นที่ 4: คำนวณระยะจาก decision boundary**

$$
\|\mathbf{w}\|=\sqrt{2^2+(-1)^2}=\sqrt{5}
$$

$$
\mathrm{distance}=\frac{|3|}{\sqrt{5}}\approx 1.342
$$

การตรวจคำตอบทำได้จากเครื่องหมาย: label เป็นบวกและ score เป็นบวกจึงจำแนกถูก อีกทั้ง margin score มากกว่า 1 จึงต้องได้ hinge loss เท่ากับศูนย์ หากคำนวณได้ loss ติดลบ แสดงว่าลืมใช้ `max(0, ...)`

## 15. คำถามทบทวนพร้อมแนวคำตอบ

### คำถาม 1: เหตุใด SVM จึง maximize margin แทนที่จะเลือกเส้นใดก็ได้ที่จำแนก training data ถูก

**แนวคำตอบ:** เส้นที่จำแนก training data ถูกอาจอยู่ชิดตัวอย่างบางจุดมาก ทำให้การเปลี่ยนแปลงเล็กน้อยของข้อมูลใหม่พลิกคำทำนายได้ SVM เลือกเส้นที่ห่างจากตัวอย่างใกล้ที่สุดของทั้งสองคลาสมากที่สุด จึงสร้างพื้นที่เผื่อรอบ decision boundary อย่างไรก็ตาม margin กว้างไม่รับประกันว่าดีเสมอ ต้องเลือก regularization และ kernel ด้วย validation

### คำถาม 2: เปรียบเทียบ hard margin กับ soft margin

**แนวคำตอบ:** Hard margin บังคับให้ทุกจุดอยู่ถูกด้านและนอก margin จึงต้องใช้ข้อมูลที่ linearly separable และไวต่อ outlier ส่วน soft margin เพิ่ม slack variables และ penalty $C$ เพื่อยอมรับการละเมิดบางส่วน ทำให้ใช้กับข้อมูล noisy หรือคลาสทับซ้อนได้ ค่า $C$ สูงเน้นลดการละเมิด ส่วน $C$ ต่ำเน้น margin ที่กว้างและ regularization มากขึ้น

### คำถาม 3: จุดหนึ่งถูกจำแนกถูกแล้ว เหตุใด hinge loss อาจยังมากกว่าศูนย์

**แนวคำตอบ:** การจำแนกถูกต้องต้องการเพียง $y_if(\mathbf{x}_i)>0$ แต่ hinge loss เป็นศูนย์เมื่อ $y_if(\mathbf{x}_i)\geq1$ เท่านั้น จุดที่อยู่ถูกด้านแต่ภายใน margin จึงยังถูกลงโทษ เพราะ SVM ต้องการทั้งทิศทางที่ถูกและระยะห่างที่เพียงพอ

### คำถาม 4: Kernel trick แก้ปัญหาอะไร

**แนวคำตอบ:** ข้อมูลบางชุดแบ่งด้วยเส้นตรงใน original feature space ไม่ได้ การ mapping ไป feature space ใหม่อาจทำให้แบ่งเชิงเส้นได้ แต่การสร้าง features มิติสูงโดยตรงมีต้นทุนมาก Kernel trick คำนวณ inner product ใน feature space ผ่าน $K(\mathbf{x},\mathbf{x}')$ โดยไม่ต้องสร้างทุกพิกัดออกมาจริง

### คำถาม 5: ถ้า RBF SVM overfit ควรตรวจอะไร

**แนวคำตอบ:** ตรวจว่ามี data leakage หรือไม่, scaling ทำใน Pipeline หรือไม่, train-validation gap, ค่า $C$ และ $\gamma$ สูงเกินไปหรือไม่ และมี outlier/noise มากเพียงใด การลด $C$ เพิ่มการยอมรับ margin violation ส่วนการลด $\gamma$ ทำให้อิทธิพลของแต่ละจุดกว้างขึ้นและ boundary เรียบขึ้น แต่ต้องเลือกด้วย cross-validation ไม่ใช่เดาจาก training accuracy

### คำถาม 6: เหตุใดการ scale ทั้ง dataset ก่อน cross-validation จึงผิด

**แนวคำตอบ:** ค่าเฉลี่ยและส่วนเบี่ยงเบนมาตรฐานจาก validation folds จะไหลเข้าไปอยู่ใน preprocessing ของ training folds ทำให้โมเดลได้รับข้อมูลเกี่ยวกับ validation distribution ล่วงหน้า การใส่ scaler ใน Pipeline ทำให้แต่ละ fold fit scaler เฉพาะส่วน training ของ fold นั้น แล้วจึง transform validation fold อย่างเป็นอิสระ

## 16. Likely Exam Focus

หัวข้อต่อไปนี้มีน้ำหนักสูงจากการปรากฏเป็นสมการและสไลด์เฉพาะเรื่อง จึงน่าฝึกอธิบายและคำนวณ แต่ไม่ใช่การยืนยันข้อสอบจริง

- อธิบาย hyperplane, margin และ support vectors ด้วยสมการ $\mathbf{w}^{T}\mathbf{x}+b$
- แสดงว่าความกว้าง margin เท่ากับ $2/\|\mathbf{w}\|$ และเชื่อมกับ objective $\|\mathbf{w}\|^2/2$
- เปรียบเทียบ hard-margin และ soft-margin SVM
- แปลความหมายของ slack variable และผลของค่า $C$
- คำนวณ margin score และ hinge loss จากข้อมูลที่กำหนด
- อธิบาย kernel trick และเลือก linear, polynomial หรือ RBF kernel ตามสถานการณ์
- อธิบายผลของ $\gamma$ ใน RBF kernel และเหตุผลที่ต้องทำ feature scaling
- เปรียบเทียบ `SVC`, `LinearSVC` และ `SGDClassifier(loss='hinge')`

## 17. สรุปความสัมพันธ์สำคัญ

SVM เริ่มจาก hyperplane $\mathbf{w}^{T}\mathbf{x}+b=0$ และทำนายด้วยเครื่องหมายของ decision score จากนั้นเพิ่มหลัก maximum margin โดยกำหนดขอบ $+1$ และ $-1$ ทำให้ margin มีความกว้าง $2/\|\mathbf{w}\|$ Hard margin เหมาะกับข้อมูลที่แบ่งได้สมบูรณ์ ส่วน soft margin เพิ่ม slack variables และค่า $C$ เพื่อแลกเปลี่ยนระหว่าง margin กว้างกับการลงโทษข้อผิดพลาด Hinge loss เป็นรูป loss-based ของแนวคิดเดียวกัน

เมื่อ original feature space แบ่งด้วยเส้นตรงไม่ได้ kernel trick ช่วยให้ SVM ทำงานเสมือนอยู่ใน feature space ใหม่ Linear kernel เหมาะกับ boundary เชิงเส้น ส่วน polynomial และ RBF รองรับความสัมพันธ์ที่ซับซ้อนกว่า แต่ต้อง scale features และเลือก hyperparameters ด้วย cross-validation ในงานจริงจึงไม่มี kernel หรือค่า $C$ ที่ดีที่สุดล่วงหน้า มีเพียงตัวเลือกที่เหมาะกับข้อมูล, metric และข้อจำกัดของโจทย์

## References

- Ekarat Rattagan. *Week 12: Support Vector Machine (SVM)*, DADS6003, May 1, 2026.
- Cortes, C. and Vapnik, V. (1995). [Support-Vector Networks](https://doi.org/10.1007/BF00994018). *Machine Learning*, 20, 273-297.
- scikit-learn. [Support Vector Machines User Guide](https://scikit-learn.org/stable/modules/svm.html).
- scikit-learn. [SVC API Reference](https://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html).
- scikit-learn. [LinearSVC API Reference](https://scikit-learn.org/stable/modules/generated/sklearn.svm.LinearSVC.html).
- scikit-learn. [SGDClassifier API Reference](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.SGDClassifier.html).
