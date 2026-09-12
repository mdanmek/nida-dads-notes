# Naive Bayes Classification

## ข้อมูลต้นฉบับ

- รายวิชา: DADS6003 Applied Machine Learning
- เอกสาร: `dads6003_05_naive_bayes_classification.pdf`
- Lab notebooks: `naive_bayes.ipynb` และ `naive_bayes_spam_email_classifier.ipynb`
- หัวข้อในสไลด์: Classification, Bayes' Rule, Naive Bayes assumption, categorical and continuous features, Laplace correction
- ขอบเขตเอกสาร: 15 หน้า

> **จากเอกสาร:** บทนี้เริ่มจากการทบทวนโจทย์ classification อธิบาย Bayes' Rule แล้วลดความซับซ้อนของ joint likelihood ด้วยสมมติฐาน conditional independence ก่อนต่อยอดไปยัง Gaussian density และ Laplace correction
>
> **คำอธิบายเพิ่มเติม:** Master Note นี้เติมที่มาของสูตร วิธีเลือกชนิดของ Naive Bayes การคำนวณใน log space การประเมินโมเดล และตัวอย่าง Python ที่รันได้ รวมทั้งตรวจแก้ตัวเลขในตัวอย่างหลายตัวแปรของสไลด์ และอธิบาย lab เรื่อง Play Tennis กับ Spam Email ทีละขั้น

## ภาพรวมและ Learning Objectives

Naive Bayes เป็นโมเดล classification ที่ใช้ความน่าจะเป็นตอบคำถามว่า เมื่อเห็นคุณลักษณะของตัวอย่างแล้ว ตัวอย่างนั้นน่าจะอยู่ในคลาสใดมากที่สุด จุดเด่นคือฝึกเร็ว ใช้ข้อมูลไม่มาก และทำงานได้ดีในบางโจทย์ เช่น การจำแนกข้อความ แต่ต้องแลกกับสมมติฐานที่ค่อนข้างแรงว่า features เป็นอิสระต่อกันเมื่อทราบคลาสแล้ว

เมื่อจบบทนี้ ผู้อ่านควรสามารถ:

1. อธิบาย prior, likelihood, evidence และ posterior ได้
2. ใช้ Bayes' Rule คำนวณ posterior probability ทีละขั้นได้
3. อธิบายว่าเหตุใดสมมติฐานแบบ naive จึงลดความซับซ้อนของโมเดล
4. จำแนกความแตกต่างระหว่าง Gaussian, Multinomial, Bernoulli และ Categorical Naive Bayes ได้
5. อธิบาย zero-frequency problem และใช้ Laplace smoothing ได้
6. สร้างและประเมิน `GaussianNB` และ `BernoulliNB` ได้
7. แปลงข้อความเป็น word-count features และสร้าง `MultinomialNB` ได้โดยไม่เกิด data leakage
8. แปลผล confusion matrix, precision, recall และ F1-score ในโจทย์ spam ได้
9. ตรวจจับการตีความผลลัพธ์ที่ผิด รวมถึงกรณีที่ค่าความน่าจะเป็นไม่น่าเชื่อถือ

## 1. พื้นฐานที่ต้องรู้ก่อน

### 1.1 Classification คืออะไร

Classification คือ supervised learning ที่เรียนรู้จากข้อมูลซึ่งมีคำตอบกำกับอยู่แล้ว เพื่อทำนาย **class label** ของข้อมูลใหม่ ตัวอย่างเช่น ลูกค้าจะยกเลิกบริการหรือไม่ อีเมลเป็น spam หรือไม่ และดอก Iris อยู่ในสายพันธุ์ใด

ถ้ามีข้อมูล $N$ แถว แต่ละแถวมี $d$ features เขียนได้ว่า

$$
X \in \mathbb{R}^{N \times d}
$$

และคำตอบของแถวที่ $i$ เป็นหนึ่งใน $K$ classes:

$$
y_i \in \{C_1, C_2, \ldots, C_K\}
$$

ตัวอย่างเช่น ถ้ามีดอกไม้ 150 ดอกและวัด 4 features แล้ว $X$ มี shape เท่ากับ $150 \times 4$ ส่วน $y_i$ อาจเป็น Setosa, Versicolor หรือ Virginica

Classification ต่างจาก regression ตรงที่ regression ทำนายค่าต่อเนื่อง เช่น ราคา แต่อย่าจำเพียงชนิดของ output เพราะหัวใจของ classification คือการแบ่งตัวอย่างออกเป็นกลุ่มตามรูปแบบใน features

### 1.2 ความน่าจะเป็นร่วมและความน่าจะเป็นแบบมีเงื่อนไข

- $P(X)$ คือโอกาสเกิดเหตุการณ์ $X$
- $P(X \cap Y)$ คือโอกาสที่ $X$ และ $Y$ เกิดพร้อมกัน
- $P(Y \mid X)$ คือโอกาสเกิด $Y$ เมื่อทราบแล้วว่า $X$ เกิด

นิยามของ conditional probability คือ

$$
P(Y \mid X) = \frac{P(Y \cap X)}{P(X)}
$$

เมื่อ $P(X) > 0$ สูตรนี้บอกว่าเราไม่ได้พิจารณาประชากรทั้งหมด แต่จำกัดเฉพาะกรณีที่ $X$ เกิด แล้วดูว่าสัดส่วนใดมี $Y$ ร่วมด้วย

## 2. Naive Bayes แบบเห็นภาพก่อน

ลองนึกถึงระบบคัดกรองอีเมล มีสองคลาสคือ `Spam` และ `Not Spam` เมื่อได้รับอีเมลใหม่ที่มีคำว่า `free`, `winner` และ `click` ระบบทำงานโดย:

1. เริ่มจากดูว่าในอดีตอีเมล spam พบมากน้อยเพียงใด
2. ดูว่าคำแต่ละคำปรากฏใน spam บ่อยเพียงใด
3. ทำแบบเดียวกันกับคลาส not spam
4. รวมหลักฐานของแต่ละคำเข้ากับโอกาสเริ่มต้นของแต่ละคลาส
5. เลือกคลาสที่ได้คะแนนความน่าจะเป็นสูงกว่า

คำว่า **naive** มาจากการสมมติว่า เมื่อเราทราบคลาสแล้ว การพบคำหนึ่งไม่เปลี่ยนโอกาสพบอีกคำหนึ่ง ทั้งที่ในภาษาใช้งานจริงคำหลายคำสัมพันธ์กัน สมมติฐานนี้อาจไม่จริงทั้งหมด แต่ช่วยให้คำนวณได้ง่ายมากและยังจำแนกได้ดีในหลายสถานการณ์

สิ่งที่ต้องแยกให้ออกคือ Naive Bayes ไม่ใช่ Bayes' Rule เอง Bayes' Rule เป็นกฎทางความน่าจะเป็น ส่วน Naive Bayes เป็น classifier ที่นำกฎนั้นมาใช้ร่วมกับ conditional independence assumption

## 3. Bayes' Rule

### 3.1 องค์ประกอบสี่ส่วน

Bayes' Rule เขียนได้ว่า

$$
P(Y \mid X) = \frac{P(X \mid Y)P(Y)}{P(X)}
$$

| องค์ประกอบ | ชื่อ | ความหมายในงาน classification |
|---|---|---|
| $P(Y \mid X)$ | Posterior | ความน่าจะเป็นของคลาส $Y$ หลังจากเห็น features $X$ |
| $P(Y)$ | Prior | ความน่าจะเป็นของคลาสก่อนเห็นข้อมูลแถวใหม่ |
| $P(X \mid Y)$ | Likelihood | โอกาสพบ features แบบ $X$ ถ้าตัวอย่างอยู่ในคลาส $Y$ |
| $P(X)$ | Evidence หรือ marginal probability | โอกาสพบ $X$ ในประชากรทั้งหมด |

Prior คือความเชื่อเริ่มต้นที่มาจากข้อมูล ไม่จำเป็นต้องหมายถึงความเห็นส่วนบุคคล เช่น ถ้าข้อมูลฝึกมี spam 20% ค่า prior ของ spam คือ 0.20

Likelihood มองคำถามย้อนทางกับ prediction เราต้องการ $P(Y \mid X)$ แต่ข้อมูลฝึกทำให้ประมาณ $P(X \mid Y)$ ได้ง่ายกว่า Bayes' Rule จึงเป็นสะพานที่กลับทิศทางของเงื่อนไข

### 3.2 ที่มาของสูตร

จาก conditional probability:

$$
P(Y \mid X) = \frac{P(Y \cap X)}{P(X)}
$$

และ

$$
P(X \mid Y) = \frac{P(X \cap Y)}{P(Y)}
$$

จึงได้

$$
P(X \cap Y) = P(X \mid Y)P(Y)
$$

เนื่องจาก $P(X \cap Y)=P(Y \cap X)$ เมื่อนำไปแทนในสมการแรกจึงได้ Bayes' Rule

### 3.3 ตัวอย่าง feature เดียวจากสไลด์

ข้อมูลมี 8 คน: Male 3 คน Female 5 คน ชื่อ Drew พบใน Male 1 คนและ Female 2 คน ต้องการทำนายเพศของ Drew คนใหม่

$$
P(M)=\frac{3}{8}, \qquad P(F)=\frac{5}{8}, \qquad P(Drew)=\frac{3}{8}
$$

สำหรับ Male:

$$
P(M \mid Drew)
= \frac{P(Drew \mid M)P(M)}{P(Drew)}
= \frac{\frac{1}{3}\frac{3}{8}}{\frac{3}{8}}
= \frac{1}{3}
$$

สำหรับ Female:

$$
P(F \mid Drew)
= \frac{P(Drew \mid F)P(F)}{P(Drew)}
= \frac{\frac{2}{5}\frac{5}{8}}{\frac{3}{8}}
= \frac{2}{3}
$$

ดังนั้น ถ้าใช้เพียงชื่อ Drew โมเดลจะทำนาย Female เพราะ posterior สูงกว่า แต่ตัวอย่างนี้สอนเรื่องการปรับ prior ด้วยข้อมูลใหม่ ไม่ได้หมายความว่าชื่อกำหนดเพศหรือมีความสัมพันธ์เชิงเหตุผล

## 4. จากหนึ่ง feature ไปสู่หลาย features

### 4.1 ปัญหาของ joint probability

เมื่อมี features $x_1,x_2,\ldots,x_d$ เราต้องการ

$$
P(Y \mid x_1,x_2,\ldots,x_d)
= \frac{P(x_1,x_2,\ldots,x_d \mid Y)P(Y)}{P(x_1,x_2,\ldots,x_d)}
$$

ส่วนที่ยากคือ joint likelihood $P(x_1,x_2,\ldots,x_d \mid Y)$ เพราะถ้า features พึ่งพากัน ต้องเก็บและประมาณ combinations จำนวนมาก ตาม chain rule:

$$
P(x_1,x_2,\ldots,x_d \mid Y)
= P(x_1 \mid Y)
P(x_2 \mid x_1,Y)
\cdots
P(x_d \mid x_1,\ldots,x_{d-1},Y)
$$

เมื่อจำนวน features หรือจำนวนค่าที่เป็นไปได้เพิ่มขึ้น หลาย combinations อาจไม่เคยปรากฏใน training data ทำให้ประมาณความน่าจะเป็นได้ไม่เสถียรและต้องใช้ข้อมูลจำนวนมาก

### 4.2 Naive conditional independence assumption

Naive Bayes สมมติว่า features เป็นอิสระต่อกัน **เมื่อกำหนดคลาสแล้ว**:

$$
P(x_1,x_2,\ldots,x_d \mid Y=c)
= \prod_{j=1}^{d} P(x_j \mid Y=c)
$$

คำว่า conditional สำคัญมาก เราไม่ได้อ้างว่า features เป็นอิสระในประชากรทั้งหมด แต่บอกว่าภายในแต่ละคลาส การรู้ feature หนึ่งไม่ให้ข้อมูลเพิ่มเกี่ยวกับอีก feature หนึ่ง

ตัวอย่างเช่น `มีไข้` กับ `ไอ` อาจสัมพันธ์กันในประชากร เพราะทั้งคู่สัมพันธ์กับโรค แต่แม้กำหนดคลาสโรคแล้ว ทั้งสองอาการก็ยังอาจสัมพันธ์กันอยู่ ถ้าเป็นเช่นนั้นสมมติฐานของโมเดลไม่สมบูรณ์

### 4.3 กฎการตัดสินใจ

สำหรับทุกคลาส $c$ โมเดลคำนวณคะแนน

$$
P(Y=c)\prod_{j=1}^{d}P(x_j \mid Y=c)
$$

Evidence เหมือนกันทุกคลาสสำหรับตัวอย่างเดียวกัน จึงไม่ต้องคำนวณเมื่อเป้าหมายมีเพียงการเลือกคลาส:

$$
\hat{y}
= \underset{c}{\mathrm{argmax}}
P(Y=c)\prod_{j=1}^{d}P(x_j \mid Y=c)
$$

นี่เรียกว่า Maximum A Posteriori หรือ MAP decision rule ส่วน posterior ที่รวมกันเป็น 1 ต้องนำคะแนนของทุกคลาสมาหารด้วยผลรวมคะแนนทั้งหมด

## 5. Worked Example หลาย features และการแก้ตัวเลขในสไลด์

ต้องการทำนายเพศจากข้อมูล:

- Name = Drew
- Over 170 cm = No
- Eye Color = Brown
- Hair Length = Short

### 5.1 คะแนนของ Male

จากข้อมูลฝึกในสไลด์:

$$
P(Drew \mid M)=\frac{1}{3}
$$

$$
P(No \mid M)=\frac{1}{3}
$$

$$
P(Brown \mid M)=\frac{1}{3}
$$

$$
P(Short \mid M)=\frac{2}{3}
$$

ดังนั้น likelihood และ unnormalized posterior score คือ

$$
P(X \mid M)
= \frac{1}{3}\frac{1}{3}\frac{1}{3}\frac{2}{3}
= \frac{2}{81}
$$

$$
s_M
= P(X \mid M)P(M)
= \frac{2}{81}\frac{3}{8}
= \frac{1}{108}
\approx 0.009259
$$

### 5.2 คะแนนของ Female

$$
P(Drew \mid F)=\frac{2}{5}, \quad
P(No \mid F)=\frac{3}{5}
$$

$$
P(Brown \mid F)=\frac{2}{5}, \quad
P(Short \mid F)=\frac{1}{5}
$$

จึงได้

$$
P(X \mid F)
= \frac{2}{5}\frac{3}{5}\frac{2}{5}\frac{1}{5}
= \frac{12}{625}
$$

$$
s_F
= P(X \mid F)P(F)
= \frac{12}{625}\frac{5}{8}
= \frac{3}{250}
= 0.012
$$

### 5.3 Normalize ให้เป็น posterior

$$
P(M \mid X)
= \frac{s_M}{s_M+s_F}
= \frac{0.009259}{0.009259+0.012}
\approx 0.4355
$$

$$
P(F \mid X)
= \frac{s_F}{s_M+s_F}
= \frac{0.012}{0.009259+0.012}
\approx 0.5645
$$

ดังนั้นคำตอบที่คำนวณได้จากข้อมูลในสไลด์คือ **Female** ไม่ใช่ Male

> **Source correction:** หน้า 9 คำนวณคะแนน Male เป็นประมาณ `0.0092` ถูกต้อง แต่หน้า 11 เปลี่ยนเป็น `0.092` โดยจุดทศนิยมคลาดไปหนึ่งตำแหน่ง จึงทำให้ posterior และ final class ผิด นอกจากนี้หน้า 10 เขียน `P(Y = Male)` ในบรรทัดฝั่ง Female แต่ค่าที่แทนจริงคือ prior ของ Female เท่ากับ $5/8$

การตรวจนี้เป็นบทเรียนสำคัญว่า output ที่ดูเป็นความน่าจะเป็นไม่รับประกันว่าถูกต้อง ควรตรวจ sign, order of magnitude, ผลรวม posterior และคำนวณซ้ำจาก unnormalized scores เสมอ

## 6. Numerical Stability: ทำไมโปรแกรมใช้ log probability

ถ้ามี features จำนวนมาก การคูณตัวเลขที่เล็กกว่า 1 ซ้ำ ๆ อาจเล็กจนคอมพิวเตอร์แทนค่าเป็นศูนย์ เรียกว่า numerical underflow เช่น $0.01$ คูณกันหลายร้อยครั้ง

เพราะ logarithm เปลี่ยนการคูณเป็นการบวก โมเดลจึงเปรียบเทียบ log score แทน:

$$
\log s_c
= \log P(Y=c)
+ \sum_{j=1}^{d}\log P(x_j \mid Y=c)
$$

เนื่องจาก log เป็นฟังก์ชันเพิ่ม คลาสที่มี score สูงสุดยังคงเป็นคลาสเดียวกับที่มี log score สูงสุด การเปลี่ยนนี้จึงช่วยด้านตัวเลขโดยไม่เปลี่ยนกฎการตัดสินใจ

## 7. Features แบบต่อเนื่อง: Gaussian Naive Bayes

ตัวอย่างก่อนหน้าเป็น categorical features จึงประมาณ probability ด้วยการนับ แต่ถ้า feature ต่อเนื่อง เช่น ส่วนสูง อุณหภูมิ หรือความยาวกลีบดอก การถามความน่าจะเป็นของค่าจุดเดียวไม่เหมาะ เพราะ continuous variable มีค่าที่เป็นไปได้ไม่จำกัด

Gaussian Naive Bayes สมมติว่า ภายในแต่ละคลาส feature แต่ละตัวแจกแจงแบบ Gaussian โดยประมาณค่าเฉลี่ยและความแปรปรวนแยกตาม class-feature pair:

$$
p(x_j \mid Y=c)
= \frac{1}{\sqrt{2\pi\sigma_{cj}^{2}}}
e^{-\frac{(x_j-\mu_{cj})^2}{2\sigma_{cj}^{2}}}
$$

เพื่อความเข้ากันได้กับ GitHub ให้ตีความ `exp` ในสมการนี้ว่า $e$ ยกกำลังข้อความภายในวงเล็บ โดย:

- $x_j$ คือค่าของ feature ที่ $j$ ในตัวอย่างใหม่
- $\mu_{cj}$ คือค่าเฉลี่ยของ feature ที่ $j$ ในคลาส $c$
- $\sigma_{cj}^{2}$ คือความแปรปรวนของ feature ที่ $j$ ในคลาส $c$
- density สูงเมื่อ $x_j$ อยู่ใกล้ค่าเฉลี่ยของคลาส และต่ำลงเมื่ออยู่ไกล

ค่าจาก Gaussian formula เป็น **probability density** ไม่ใช่ probability ของจุดเดียว ค่า density อาจมากกว่า 1 ได้ในบางกรณี แต่พื้นที่ใต้โค้งรวมเท่ากับ 1

ควรตรวจ histogram หรือ distribution แยกตาม class หากเบ้มาก มีหลายยอด หรือมี outliers รุนแรง Gaussian assumption อาจไม่เหมาะ แม้ Naive Bayes ยังอาจจำแนกได้ แต่เหตุผลรองรับและ probability estimates จะอ่อนลง

## 8. Zero-Frequency Problem และ Laplace Smoothing

### 8.1 ปัญหา

ถ้าค่าหนึ่งไม่เคยพบในคลาสใดเลย ค่า likelihood ของค่านั้นจะเป็นศูนย์ เมื่อคูณกับ feature อื่น คะแนนของทั้งคลาสจะกลายเป็นศูนย์ทันที ไม่ว่าหลักฐานอื่นจะสนับสนุนคลาสนั้นเพียงใด

เช่น มีข้อมูล Income 1,000 แถว:

$$
P(low)=0, \quad P(medium)=\frac{990}{1000}, \quad P(high)=\frac{10}{1000}
$$

### 8.2 Additive smoothing

Laplace smoothing เพิ่ม pseudo-count เท่ากับ 1 ให้ทุก category ถ้ามี $K$ categories:

$$
\hat{P}(x=v)
= \frac{N_v+1}{N+K}
$$

สำหรับตัวอย่างที่มี 3 categories:

$$
P(low)=\frac{0+1}{1000+3}
$$

$$
P(medium)=\frac{990+1}{1000+3}
$$

$$
P(high)=\frac{10+1}{1000+3}
$$

ตัวส่วนเพิ่ม 3 เพราะเราเพิ่ม 1 ให้ทั้งสาม categories ทำให้ผลรวม probability ยังคงเป็น 1

ใน Naive Bayes จริง เราคำนวณแยกตาม feature และ class ถ้า feature $j$ มี $K_j$ categories สูตรทั่วไปคือ

$$
\hat{P}(x_j=v \mid Y=c)
= \frac{N_{cjv}+\alpha}{N_c+\alpha K_j}
$$

โดย $\alpha=1$ คือ Laplace smoothing และ $0<\alpha<1$ มักเรียกว่า Lidstone smoothing ค่า $\alpha$ สูงขึ้นทำให้ probabilities ถูกดึงให้ใกล้ uniform มากขึ้น ซึ่งลดความรุนแรงจากข้อมูลน้อย แต่ถ้าสูงเกินไปก็กลบสัญญาณจริง

## 9. เลือก Naive Bayes ให้ตรงชนิดข้อมูล

Naive Bayes ไม่ได้มีสูตร likelihood แบบเดียว สิ่งที่ต่างกันระหว่าง variants คือสมมติฐานเกี่ยวกับการกระจายของแต่ละ feature

| Variant | Feature ที่เหมาะ | ตัวอย่าง | ข้อควรระวัง |
|---|---|---|---|
| `GaussianNB` | ค่าต่อเนื่อง | ส่วนสูง อุณหภูมิ measurements | สมมติ Gaussian แยกตาม class และ feature |
| `MultinomialNB` | จำนวนครั้งที่ไม่ติดลบ | word counts, event counts | ไม่เหมาะกับค่าติดลบ |
| `BernoulliNB` | binary features | มีหรือไม่มีคำหนึ่ง | สนใจ occurrence ไม่ใช่จำนวนครั้ง |
| `CategoricalNB` | category code ของแต่ละ feature | สี ประเภท ช่องทาง | ต้อง encode category เป็นเลขจำนวนเต็มที่ไม่ติดลบ |
| `ComplementNB` | count data โดยเฉพาะ class imbalance | text classification ที่คลาสไม่สมดุล | ความหมายการคำนวณต่างจาก standard MNB |

เอกสารของ scikit-learn อธิบาย variants และ likelihood assumptions ของ Naive Bayes แต่ละชนิดไว้ใน [Naive Bayes User Guide](https://scikit-learn.org/stable/modules/naive_bayes.html) โดย `MultinomialNB` ใช้ discrete counts, `BernoulliNB` ใช้ binary features และ `CategoricalNB` ใช้ categorical distribution แยกแต่ละ feature

## 10. Hands-on Lab: GaussianNB กับ Iris

### 10.1 เป้าหมาย

ใช้ features ต่อเนื่อง 4 ตัวของ Iris เพื่อจำแนก 3 species แบ่งข้อมูล train 80% และ test 20% ฝึกเฉพาะ training data แล้วประเมินด้วย accuracy, confusion matrix และ classification report

### 10.2 Code

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# Load features and target
iris = load_iris()
X = iris.data
y = iris.target

# Preserve class proportions in the 80/20 split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# Fit the model using training data only
model = GaussianNB()
model.fit(X_train, y_train)

# Predict unseen test observations
y_pred = model.predict(X_test)

print(f'Train shape: {X_train.shape}')
print(f'Test shape: {X_test.shape}')
print(f'Accuracy: {accuracy_score(y_test, y_pred):.3f}')
print(confusion_matrix(y_test, y_pred))
print(
    classification_report(
        y_test,
        y_pred,
        target_names=iris.target_names,
        digits=3
    )
)
```

### 10.3 Verified output

เมื่อรันด้วย scikit-learn และค่าตาม code ข้างต้น ได้ผล:

```text
Train shape: (120, 4)
Test shape: (30, 4)
Accuracy: 0.967

[[10  0  0]
 [ 0  9  1]
 [ 0  0 10]]
```

Accuracy 0.967 หมายถึงทำนายถูก 29 จาก 30 ตัวอย่าง แต่ confusion matrix บอกข้อมูลเพิ่มว่า Versicolor 1 ตัวอย่างถูกทำนายเป็น Virginica ส่วน Setosa และ Virginica ใน test split นี้ทำนายถูกทั้งหมด

### 10.4 Code dependency และ data leakage

| ขั้น | Input | การทำงาน | Output | ถ้าทำผิด |
|---|---|---|---|---|
| Load | Iris dataset | แยก features และ target | `X (150, 4)`, `y (150,)` | เลือก target ปนใน `X` จะเกิด leakage |
| Split | `X`, `y` | แบ่ง 80/20 แบบ stratified | train 120, test 30 | ใช้ test ฝึกจะทำให้การประเมินสูงเกินจริง |
| Fit | `X_train`, `y_train` | ประมาณ priors, means, variances | fitted `GaussianNB` | fit ก่อน split ทำลายความเป็น unseen data |
| Predict | `X_test` | คำนวณ class posterior | `y_pred (30,)` | ใช้ feature order ผิดจะได้ prediction ผิดความหมาย |
| Evaluate | `y_test`, `y_pred` | เทียบค่าจริงกับค่าทำนาย | metrics | accuracy อย่างเดียวอาจซ่อนปัญหาเฉพาะคลาส |

`stratify=y` ช่วยรักษาสัดส่วนแต่ละ class ไว้ใน train และ test ส่วน `random_state=42` ทำให้แบ่งข้อมูลซ้ำแล้วได้ชุดเดิม จึงตรวจสอบผลร่วมกันได้

### 10.5 ตรวจค่าที่โมเดลเรียนรู้

```python
print('Class prior:')
print(model.class_prior_)

print('\nMean of each feature within each class:')
print(model.theta_)

print('\nVariance of each feature within each class:')
print(model.var_)

print('\nPredicted probabilities for the first three test rows:')
print(model.predict_proba(X_test[:3]))
```

`class_prior_` เก็บ prior ของแต่ละคลาส `theta_` เก็บค่าเฉลี่ย และ `var_` เก็บความแปรปรวนของทุก class-feature pair ซึ่งตรงกับ parameters ใน Gaussian likelihood ตามเอกสาร [GaussianNB](https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.GaussianNB.html)

## 11. Hands-on Lab: Play Tennis จากการนับเองสู่ BernoulliNB

### 11.1 เป้าหมายและข้อมูล

> **จาก lab `naive_bayes.ipynb`:** Lab นี้ใช้ข้อมูลสภาพอากาศ 14 วันเพื่อทำนายว่าจะเล่นเทนนิสหรือไม่ ตัวแปรต้นมี 4 ตัว ได้แก่ Outlook, Temperature, Humidity และ Wind ส่วน target คือ `Play_Tennis`

ตัวอย่างนี้เชื่อมสองมุมมองเข้าด้วยกัน มุมแรกคือการเขียน Naive Bayes ด้วยตัวเองเพื่อให้เห็นว่าโมเดลนับ prior และ likelihood อย่างไร มุมที่สองคือการใช้ `BernoulliNB` ของ scikit-learn หลังแปลง categorical features เป็นคอลัมน์ 0/1

ฟังก์ชัน `pre_processing()` ลบคอลัมน์แรกซึ่งเป็นเลขวัน แล้วแยกคอลัมน์สุดท้ายเป็น target:

```python
def pre_processing(df):
    df = df.drop(columns=df.columns[0])
    X = df.drop(columns=df.columns[-1])
    y = df[df.columns[-1]]
    return X, y
```

หนึ่งแถวของ $X$ จึงแทนสภาพอากาศหนึ่งวัน ส่วนค่าใน $y$ คือ `Yes` หรือ `No` การลบคอลัมน์ด้วยตำแหน่งใช้ได้กับไฟล์นี้ แต่ถ้าลำดับคอลัมน์เปลี่ยน code อาจลบผิดคอลัมน์ ในงานจริงควรระบุชื่อคอลัมน์ให้ชัดเจน

### 11.2 Custom NaiveBayes ทำอะไรตอน fit

Class ที่เขียนใน notebook เก็บข้อมูลสำคัญสามกลุ่ม:

- `class_priors` เก็บ $P(c)$ เช่น สัดส่วน `Yes` และ `No`
- `likelihoods` เก็บ $P(x_j \mid c)$ ของแต่ละค่าตัวแปรเมื่อกำหนดคลาส
- `pred_priors` เก็บ $P(x_j)$ หรือ evidence ราย feature

เมื่อเรียก `fit(X, y)` ลำดับการทำงานคือ:

| ขั้น | Input | สิ่งที่คำนวณ | ตัวอย่าง Output |
|---|---|---|---|
| กำหนดโครงสร้าง | ชื่อ features และค่าที่พบ | เตรียม dictionary | key เช่น `Rain_Yes` |
| `_calc_class_prior()` | `y_train` | จำนวนแต่ละคลาสหารจำนวนแถว | $P(Yes)=9/14$ |
| `_calc_likelihoods()` | `X_train`, `y_train` | สัดส่วนค่าของ feature ภายในคลาส | $P(Rain \mid Yes)$ |
| `_calc_predictor_prior()` | `X_train` | สัดส่วนค่าของ feature ในข้อมูลทั้งหมด | $P(Rain)$ |

เมื่อ `predict()` รับ query หนึ่งแถว code จะคูณ likelihood ของทั้ง 4 features กับ class prior ทำซ้ำสำหรับทุกคลาส แล้วเลือกคลาสที่มีคะแนนสูงสุด

สำหรับการเลือกคลาสเพียงอย่างเดียว evidence เป็นตัวหารเดียวกันทุกคลาส จึงตัดออกได้โดยไม่เปลี่ยนคำตอบ:

$$
\hat{y}
=\underset{c}{\mathrm{argmax}}
[
P(c)\prod_j P(x_j \mid c)
]
$$

การคูณ evidence แยกราย feature ใน custom code เป็นวิธีสาธิตตาม notebook แต่ไม่ใช่สิ่งจำเป็นสำหรับ MAP classification และไม่ใช่การคำนวณ joint evidence ที่ถูกต้องเสมอไป

### 11.3 Trace การทำนายและผลจาก notebook

Notebook ทดลองสาม query:

| Query | Outlook | Temperature | Humidity | Wind | ผลทำนาย |
|---|---|---|---|---|---|
| 1 | Rain | Mild | Normal | Strong | Yes |
| 2 | Overcast | Cool | Normal | Strong | Yes |
| 3 | Sunny | Hot | High | Strong | No |

ตัวอย่าง Query 1 ได้คะแนนที่ notebook พิมพ์ออกมาเป็น `No = 0.2091` และ `Yes = 0.6453` จึงเลือก `Yes` ตัวเลขนี้ใช้เปรียบเทียบระหว่างคลาสได้ แต่ไม่ควรอ่านเป็น posterior ที่ normalize แล้ว เพราะคะแนนสองฝั่งรวมกันไม่เท่ากับ 1

### 11.4 จาก categorical data สู่ BernoulliNB

`BernoulliNB` ต้องการ features ที่ตีความเป็นเหตุการณ์เกิดหรือไม่เกิด Lab จึงใช้ `pd.get_dummies()` เปลี่ยนแต่ละ category เป็นคอลัมน์ 0/1 เช่น `Outlook_Rain` และ `Wind_Strong`

```python
query_data = pd.DataFrame(
    [query1[0], query2[0], query3[0]],
    columns=['Outlook', 'Temperature', 'Humidity', 'Wind']
)

X_with_query = pd.concat([X, query_data], ignore_index=True)
X_encoded = pd.get_dummies(X_with_query, dtype='int')

model = BernoulliNB()
model.fit(X_encoded.iloc[:len(X)], y)

query_pred = model.predict(X_encoded.iloc[len(X):])
query_prob = model.predict_proba(X_encoded.iloc[len(X):])
```

ผลจาก notebook คือ `['Yes', 'Yes', 'No']` ซึ่งตรงกับ custom model และ probabilities ของคลาสที่ถูกเลือกเท่ากับประมาณ 0.7994, 0.9711 และ 0.9666 ตามลำดับ

อย่างไรก็ตาม การรวม query ก่อนสร้าง dummy columns ทำให้ข้อมูลใหม่มีส่วนกำหนดโครงสร้าง features วิธีนี้ช่วยให้ lab สั้นและคอลัมน์ตรงกัน แต่ workflow ที่ปลอดภัยกว่าคือ fit encoder ด้วย training data เท่านั้น แล้วกำหนด `handle_unknown='ignore'`:

```python
from sklearn.compose import ColumnTransformer
from sklearn.naive_bayes import BernoulliNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

model = Pipeline([
    (
        'encode',
        ColumnTransformer([
            (
                'categorical',
                OneHotEncoder(handle_unknown='ignore'),
                X.columns
            )
        ])
    ),
    ('classifier', BernoulliNB())
])

model.fit(X, y)
model.predict(query_data)
```

Pipeline ทำให้ขั้นแปลงข้อมูลที่เรียนจาก training data ถูกนำไปใช้กับข้อมูลใหม่แบบเดิมโดยอัตโนมัติ และลดความเสี่ยงที่ลำดับหรือจำนวนคอลัมน์จะไม่ตรงกัน

### 11.5 ข้อจำกัดและแบบทดลอง

Custom model ไม่มี Laplace smoothing ถ้า query มี category ที่ไม่เคยพบในคลาสหนึ่ง อาจได้ probability เป็นศูนย์ หรือเกิด `KeyError` ถ้าไม่เคยพบค่านั้นเลย นอกจากนี้การคูณ probability จำนวนมากโดยตรงเสี่ยง numerical underflow เมื่อ features เยอะ

ลองเปลี่ยน query ให้มี category ใหม่ เช่น `Outlook='Foggy'` แล้วทำนายผลลัพธ์ก่อนรัน:

- Custom model มีแนวโน้มเกิด `KeyError`
- Pipeline ที่ใช้ `OneHotEncoder(handle_unknown='ignore')` ยังทำนายได้
- การทำนายได้ไม่ได้แปลว่า category ใหม่นั้นมีข้อมูลเพียงพอ ควรบันทึกอัตรา unknown categories เพื่อเฝ้าระวัง dataset shift

## 12. Hands-on Lab: Spam Email Classifier

### 12.1 ปัญหา ข้อมูล และ class balance

> **จาก lab `naive_bayes_spam_email_classifier.ipynb`:** Dataset มีอีเมล 5,728 ฉบับและ 2 คอลัมน์ คือข้อความ `text` กับ label `spam` โดย `1` หมายถึง spam และ `0` หมายถึง ham หรืออีเมลปกติ ทั้งสองคอลัมน์ไม่มี missing value

Class distribution คือ ham 4,360 ฉบับและ spam 1,368 ฉบับ หรือประมาณ 76.1% ต่อ 23.9% ถ้าทายทุกฉบับเป็น ham จะได้ accuracy ประมาณ 76.1% อยู่แล้ว ดังนั้นต้องดู confusion matrix, precision และ recall ของ spam เพิ่ม ไม่ควรสรุปจาก accuracy เพียงค่าเดียว

### 12.2 CountVectorizer เปลี่ยนข้อความเป็นตัวเลขอย่างไร

โมเดลไม่สามารถรับประโยคดิบโดยตรง `CountVectorizer` จึงสร้าง vocabulary จากคำที่พบ แล้วเปลี่ยนอีเมลแต่ละฉบับเป็นเวกเตอร์จำนวนครั้งที่แต่ละคำปรากฏ

สมมติมีข้อความสั้นสองฉบับ:

```text
free prize
project meeting
```

ถ้า vocabulary คือ `free`, `meeting`, `prize`, `project` แถวแรกจะกลายเป็น `[1, 0, 1, 0]` และแถวที่สองเป็น `[0, 1, 0, 1]` นี่คือ input แบบ non-negative count ที่สอดคล้องกับ `MultinomialNB`

ใน notebook:

```python
vectorizer = CountVectorizer()
data_vec = vectorizer.fit_transform(spam_df['text'])
```

ได้ sparse matrix shape `(5728, 37303)` หมายถึงอีเมล 5,728 แถวและคำ 37,303 features มีค่าที่ไม่เป็นศูนย์ 708,380 จุด การใช้ sparse matrix สำคัญเพราะเมทริกซ์ข้อความส่วนใหญ่เป็นศูนย์ จึงไม่ควรแปลงเป็น dense array โดยไม่จำเป็น ค่าสูงสุดในเมทริกซ์คือคำว่า `the` ซึ่งปรากฏ 596 ครั้งในอีเมลหนึ่งฉบับ

### 12.3 จุดที่ควรแก้: split ก่อน fit vectorizer

Notebook ต้นฉบับเรียก `fit_transform()` กับข้อความทั้งหมดก่อน `train_test_split()` แม้ label ไม่ได้รั่วเข้าไป แต่ vocabulary ได้เห็นคำจาก test set แล้ว จึงเป็น **preprocessing leakage** และอาจทำให้การประเมินมองโลกดีเกินจริง

ลำดับที่ควรใช้คือ:

1. แบ่งข้อความดิบและ label เป็น train/test
2. fit `CountVectorizer` ด้วยข้อความ train เท่านั้น
3. transform ข้อความ test ด้วย vocabulary เดิม
4. fit `MultinomialNB` ด้วย train matrix
5. predict และ evaluate test matrix

Pipeline รวมลำดับทั้งหมดและช่วยป้องกันการ fit ผิดชุด:

```python
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

X_train, X_test, y_train, y_test = train_test_split(
    spam_df['text'],
    spam_df['spam'],
    test_size=0.20,
    stratify=spam_df['spam'],
    random_state=123
)

spam_model = Pipeline([
    ('vectorizer', CountVectorizer()),
    ('classifier', MultinomialNB())
])

spam_model.fit(X_train, y_train)
y_pred = spam_model.predict(X_test)

print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred, digits=3))
```

เพราะ workflow นี้แก้ leakage ผลตัวเลขอาจต่างจาก output เดิมเล็กน้อย ความต่างดังกล่าวเป็นสิ่งที่ควรยอมรับเพื่อให้การประเมินสะท้อนข้อมูลที่ไม่เคยเห็นจริง

### 12.4 ทำไมเลือก MultinomialNB

Notebook แสดงชื่อ Gaussian, Multinomial, Bernoulli และ Categorical Naive Bayes แต่ model ที่ fit จริงคือ `MultinomialNB()` ซึ่งเหมาะกับ word counts:

- `MultinomialNB` ใช้จำนวนครั้งของคำและต้องการค่าไม่ติดลบ
- `BernoulliNB` เหมาะเมื่อสนใจเพียงมีหรือไม่มีคำ ไม่สนจำนวนครั้ง
- `ComplementNB` เป็นอีกทางเลือกที่ควรทดลองเมื่อ class distribution ไม่สมดุล
- `GaussianNB` สมมติ continuous features แบบ Gaussian และไม่เหมาะกับ sparse word counts โดยตรง
- `CategoricalNB` ใช้กับ categorical feature แต่ละคอลัมน์ ไม่ใช่ vocabulary counts จำนวนมาก

การ import หลายโมเดลไม่ได้หมายความว่า notebook ได้ทดลองทุกโมเดล ต้องดูบรรทัดที่สร้าง object และ `fit()` จริงเสมอ

### 12.5 ผลจาก notebook และการคำนวณ metrics

> **ผลที่บันทึกใน notebook:** Test set มี 1,146 ฉบับ และ confusion matrix ให้ค่า TN = 861, FP = 11, FN = 1, TP = 273

| ค่าจริง / ค่าทำนาย | Ham | Spam |
|---|---:|---:|
| Ham | TN = 861 | FP = 11 |
| Spam | FN = 1 | TP = 273 |

Accuracy คำนวณจาก:

$$
Accuracy
=
\frac{TN+TP}{TN+FP+FN+TP}
=
\frac{861+273}{1146}
\approx 0.9895
$$

สำหรับ spam class:

$$
Precision_{spam}
=
\frac{TP}{TP+FP}
=
\frac{273}{273+11}
\approx 0.9613
$$

$$
Recall_{spam}
=
\frac{TP}{TP+FN}
=
\frac{273}{273+1}
\approx 0.9964
$$

Precision ประมาณ 0.96 หมายความว่า ในอีเมลที่โมเดลแจ้งว่าเป็น spam มีประมาณ 96% ที่เป็น spam จริง ส่วน recall ใกล้ 1.00 หมายความว่าโมเดลพลาด spam จริงเพียง 1 ฉบับจาก 274 ฉบับ

ผลนี้ดูดีมาก แต่ต้องอ่านตามผลกระทบของข้อผิดพลาดด้วย FP 11 ฉบับคืออีเมลปกติที่ถูกส่งไป spam folder ซึ่งอาจสร้างความเสียหายมากกว่า FN ในบางองค์กร การเลือกโมเดลหรือ threshold จึงขึ้นกับต้นทุนของสองความผิดพลาด ไม่ใช่ดู accuracy สูงสุดเพียงอย่างเดียว

### 12.6 Validation และ troubleshooting

| อาการ | สาเหตุที่เป็นไปได้ | วิธีตรวจและแก้ |
|---|---|---|
| `ValueError: Negative values in data` | ส่ง standardized features เข้า `MultinomialNB` | ใช้ non-negative counts หรือเลือกโมเดลที่ตรงชนิดข้อมูล |
| Train/test มีจำนวน features ไม่เท่ากัน | fit vectorizer แยกกันสองชุด | fit บน train แล้วใช้ `transform()` กับ test หรือใช้ Pipeline |
| Memory เต็ม | แปลง sparse matrix เป็น dense | คง sparse matrix และอย่าเรียก `.toarray()` กับข้อมูลใหญ่ |
| Accuracy สูงแต่จับ spam ไม่ได้ | class imbalance | ดู recall, F1 และ confusion matrix ของ spam |
| ผลเปลี่ยนทุกครั้ง | split ไม่คงที่ | กำหนด `random_state` และใช้ `stratify` |
| คำใหม่ทั้งหมดถูกมองข้าม | vocabulary ไม่มีคำเหล่านั้น | ตรวจ out-of-vocabulary rate และ retrain เมื่อข้อมูลเปลี่ยน |

ก่อนเชื่อผล ควรตรวจอย่างน้อยว่า train/test ไม่ทับกัน, vectorizer fit เฉพาะ train, class proportions ใกล้เคียงกัน, จำนวน prediction เท่ากับจำนวน test labels และ confusion matrix รวมกันได้เท่ากับ test size

### 12.7 แบบทดลองต่อยอด

ทดลองเปลี่ยน `CountVectorizer()` เป็นแต่ละตัวเลือกต่อไปนี้ โดยคง split เดิม แล้วคาดการณ์ก่อนรันว่าค่า precision และ recall จะเปลี่ยนอย่างไร:

1. `CountVectorizer(binary=True)` เพื่อเปรียบเทียบ count กับ word presence
2. `CountVectorizer(stop_words='english')` เพื่อตัดคำทั่วไป เช่น `the`
3. `CountVectorizer(ngram_range=(1, 2), min_df=2)` เพื่อเพิ่มวลีสองคำแต่ลดคำที่พบครั้งเดียว
4. `TfidfVectorizer()` เพื่อให้น้ำหนักคำที่พบเฉพาะบางเอกสารมากขึ้น
5. `ComplementNB()` เพื่อเปรียบเทียบกับ MultinomialNB ในข้อมูลไม่สมดุล

เปรียบเทียบด้วย precision, recall และ F1 ของ spam พร้อมบันทึกจำนวน features และเวลา fit การเพิ่ม features ไม่ได้รับประกันว่าจะดีขึ้น เพราะอาจเพิ่ม noise, memory และความเสี่ยง overfitting

## 13. การตีความและตรวจสอบผลลัพธ์

### 11.1 Accuracy ไม่เพียงพอเสมอไป

Accuracy เหมาะเมื่อความผิดพลาดทุกคลาสมีต้นทุนใกล้กันและ class distribution ไม่เบ้มาก ถ้า fraud มีเพียง 1% โมเดลที่ตอบว่าไม่ fraud ทุกแถวจะได้ accuracy 99% แต่จับ fraud ไม่ได้เลย กรณีนี้ต้องดู recall, precision, F1-score, confusion matrix และ metric ที่สะท้อนต้นทุนทางธุรกิจ

### 11.2 Predicted class กับ predicted probability คนละเรื่อง

โมเดลอาจจัดอันดับคลาสถูก แต่ probability ไม่ได้ calibrated ดี กล่าวคือ prediction 0.90 อาจไม่ได้ถูกประมาณ 90% จริงเมื่อเก็บตัวอย่างลักษณะเดียวกันจำนวนมาก Conditional independence ที่ผิดสามารถทำให้ evidence ที่สัมพันธ์กันถูกนับซ้ำและ probability มั่นใจเกินจริง เอกสาร scikit-learn แสดงว่า `GaussianNB` อาจผลัก probability ไปใกล้ 0 หรือ 1 เมื่อ features มีความสัมพันธ์กัน [Probability calibration](https://scikit-learn.org/stable/modules/calibration.html)

ดังนั้น:

- ถ้าต้องการเพียง class label ให้ประเมิน classification performance
- ถ้าจะใช้ probability ตั้ง threshold หรือคำนวณความเสี่ยง ต้องตรวจ calibration เพิ่ม
- ถ้าค่า probability มีผลต่อการตัดสินใจสูง ควรใช้ calibration curve และพิจารณา probability calibration บนข้อมูลที่แยกจากชุดฝึก

## 14. ข้อดี ข้อจำกัด และ failure modes

### ข้อดี

- ฝึกและทำนายเร็ว เพราะประมาณ statistics แยกตาม class-feature pair
- ใช้ memory น้อยและรองรับ features จำนวนมาก
- เหมาะกับ text classification และข้อมูลแบบ count ในหลายสถานการณ์
- รองรับ incremental learning ในบาง implementation เช่น `partial_fit`
- เป็น baseline ที่ตีความกลไกได้ค่อนข้างตรงไปตรงมา

### ข้อจำกัด

- Conditional independence มักไม่จริงในข้อมูลจริง
- Correlated features อาจนับหลักฐานเดิมซ้ำ ทำให้ probability มั่นใจเกินไป
- Likelihood distribution ต้องเลือกให้เหมาะกับชนิด feature
- Category ที่ไม่เคยพบทำให้ probability เป็นศูนย์หากไม่ smoothing
- GaussianNB ไวต่อ distribution ที่เบ้ หลายยอด และ outliers
- ความแม่นยำดีไม่ได้แปลว่า posterior probability เชื่อถือได้

### อาการ สาเหตุ และแนวทางตรวจ

| อาการ | สาเหตุที่เป็นไปได้ | วิธีตรวจ | แนวทางแก้ |
|---|---|---|---|
| Probability เป็น 0 หรือ 1 จำนวนมาก | features สัมพันธ์กันหรือ underflow | correlation, calibration curve, log probabilities | ลด features ซ้ำซ้อน ใช้ log space หรือ calibrate |
| คลาสหนึ่งไม่เคยถูกทำนาย | imbalance หรือ prior ครอบงำ | class counts และ confusion matrix | ทบทวน sampling, prior, metric และ variant |
| คะแนนเป็นศูนย์เมื่อพบ category ใหม่ | ไม่ใช้ smoothing | ตรวจ category counts ต่อ class | ใช้ additive smoothing |
| GaussianNB ทำงานไม่ดี | distribution ไม่ใกล้ Gaussian | histogram แยก class และ feature | transform feature หรือเลือกโมเดลอื่น |
| ผล test สูงผิดปกติ | data leakage | ตรวจลำดับ split, preprocessing, duplicate entities | split ก่อนเรียน parameters และใช้ pipeline |

## 15. Decision Framework

เลือก Naive Bayes เมื่อข้อมูลตรงกับ likelihood ที่โมเดลสมมติ ต้องการโมเดลเร็ว หรืออยากได้ baseline ที่แข็งแรง โดยเฉพาะข้อมูลข้อความที่มี dimensions สูง แต่ไม่ควรเลือกเพียงเพราะชื่อโมเดลง่าย

| สถานการณ์ | ทางเลือกที่เหมาะ | เหตุผล |
|---|---|---|
| Continuous measurements และ distribution ต่อ class พอใกล้ Gaussian | GaussianNB | ประมาณ mean และ variance ได้โดยตรง |
| Word counts หรือ frequency | MultinomialNB | likelihood ตรงกับ count data |
| สนใจว่าคำปรากฏหรือไม่ | BernoulliNB | ใช้ binary occurrence |
| Features เป็น categories หลายค่า | CategoricalNB | ประมาณ categorical distribution แยก feature |
| Text data มี class imbalance | ทดลอง ComplementNB เทียบ MultinomialNB | ออกแบบมาเพื่อลดปัญหาจาก imbalance |
| Features สัมพันธ์กันมากและต้องการ probability ที่น่าเชื่อถือ | เปรียบเทียบ Logistic Regression และ calibration | Naive independence อาจทำให้ confidence สูงเกินจริง |
| ต้องอธิบาย interaction ซับซ้อน | Tree-based model หรือโมเดลที่รองรับ interaction | Naive Bayes ไม่จำลอง dependency โดยตรง |

## 16. Critical Discussion ระดับปริญญาโท

### 16.1 สมมติฐานผิดแล้วเหตุใดยังทำนายได้ดี

Classifier ต้องเลือกคลาสที่มี score สูงสุด ไม่จำเป็นต้องประมาณ joint distribution ได้ถูกต้องทุกจุด แม้ likelihood ของแต่ละคลาสคลาดเคลื่อน แต่ถ้าลำดับคะแนนยังถูก decision boundary ก็ยังจำแนกได้ดี นี่อธิบายว่าทำไม Naive Bayes อาจมี accuracy ดีแม้ probability calibration ไม่ดี

### 16.2 Prediction ไม่ใช่ causation

Feature ที่ช่วยจำแนกไม่จำเป็นต้องเป็นสาเหตุของคลาส ตัวอย่างชื่อกับเพศในสไลด์เป็น association ในข้อมูลขนาดเล็ก และยังเสี่ยงสร้าง bias หากนำไปใช้กับคนจริง การเลือก features ต้องพิจารณาความชอบธรรม ความเป็นส่วนตัว ผลกระทบต่อกลุ่ม และการเปลี่ยนแปลงของ population

### 16.3 Dataset shift

Prior และ likelihood เรียนจากอดีต ถ้าสัดส่วนคลาสหรือรูปแบบ features เปลี่ยน posterior ที่คำนวณย่อมไม่แทนสถานการณ์ปัจจุบัน ระบบ production จึงต้องติดตาม class distribution, feature distribution, performance และ calibration ตามเวลา

### 16.4 Independence ต้องตรวจในเงื่อนไขของคลาส

การดู correlation ของข้อมูลทั้งหมดไม่เท่ากับตรวจ conditional independence ควรสำรวจความสัมพันธ์ของ features ภายในแต่ละ class อย่างไรก็ตาม correlation วัดเพียงความสัมพันธ์เชิงเส้นและไม่พิสูจน์ independence การตรวจนี้จึงเป็น diagnostic ไม่ใช่ข้อพิสูจน์สมมติฐาน

## 17. Common Misconceptions

1. **Naive Bayes ต้องการให้ features เป็นอิสระโดยไม่มีเงื่อนไข** - ไม่ถูก ต้องเป็นอิสระเมื่อกำหนด class แล้ว
2. **Evidence ต้องคำนวณเสมอ** - ไม่จำเป็นสำหรับการเลือก class เพราะเป็นตัวหารร่วม แต่จำเป็นเมื่อ normalize เป็น posterior
3. **Probability density คือ probability** - ไม่เหมือนกันสำหรับ continuous variable
4. **Accuracy สูงแปลว่า probability ถูกต้อง** - ไม่จริง ต้องประเมิน calibration แยก
5. **ค่า likelihood เป็นศูนย์แปลว่าคลาสเป็นไปไม่ได้จริง** - อาจเกิดเพราะ training data ไม่เคยเห็นค่านั้น จึงต้องพิจารณา smoothing
6. **Naive Bayes ใช้ได้เฉพาะสองคลาส** - ไม่จริง สามารถคำนวณคะแนนทุกคลาสและเลือกค่าสูงสุดได้
7. **ชื่อ Laplacian correction หมายถึง Laplacian distribution** - ในบริบทสไลด์หมายถึง Laplace additive smoothing ไม่เกี่ยวกับ Laplace distribution

## 18. Likely Exam Focus

> ส่วนนี้เป็นการอนุมานจากหัวข้อ สมการ และตัวอย่างที่เน้นในเอกสาร ไม่ใช่ข้อมูลข้อสอบจริง

- ระบุและอธิบาย posterior, prior, likelihood และ evidence
- derive Bayes' Rule จาก conditional probability
- คำนวณ posterior สำหรับหนึ่ง feature และหลาย features
- อธิบาย conditional independence และผลต่อจำนวน parameters
- ตรวจข้อผิดพลาดในการคูณ prior, likelihood และ normalization
- อธิบาย Gaussian likelihood สำหรับ continuous feature
- อธิบาย zero-frequency problem และคำนวณ Laplace smoothing
- เปรียบเทียบข้อดี ข้อจำกัด และสถานการณ์ที่ควรใช้ Naive Bayes

## 19. Progressive Practice พร้อมเฉลย

### ข้อ 1: Recall

ใน Bayes' Rule ส่วนใดแทนความเชื่อก่อนเห็นตัวอย่างใหม่ และส่วนใดแทนความเชื่อหลังเห็นตัวอย่างใหม่

**เฉลย:** $P(Y)$ คือ prior ก่อนเห็น $X$ และ $P(Y \mid X)$ คือ posterior หลังเห็น $X$

### ข้อ 2: Calculation

ในข้อมูล 100 รายการ มี Fraud 20 รายการ ระบบพบ feature `international` ใน Fraud 12 รายการและใน Non-fraud 8 รายการ จงหา $P(Fraud \mid international)$

**เฉลย:**

$$
P(Fraud)=\frac{20}{100}=0.20
$$

$$
P(international \mid Fraud)=\frac{12}{20}=0.60
$$

$$
P(international)=\frac{12+8}{100}=0.20
$$

$$
P(Fraud \mid international)
= \frac{0.60 \times 0.20}{0.20}
= 0.60
$$

แม้ prior ของ Fraud มีเพียง 20% แต่เมื่อทราบว่าเป็น international transaction posterior เพิ่มเป็น 60%

### ข้อ 3: Laplace smoothing

ในคลาสหนึ่งมีข้อมูล 20 แถว Feature `channel` มี 4 categories และ category `mobile` ไม่เคยพบ จงคำนวณ probability ของ `mobile` เมื่อใช้ $\alpha=1$

**เฉลย:**

$$
P(mobile \mid class)
= \frac{0+1}{20+1 \times 4}
= \frac{1}{24}
$$

### ข้อ 4: Analyze

โมเดลอีเมลใช้ features `free`, `free_offer` และ `special_free_offer` ซึ่งสัมพันธ์กันมาก โมเดลทำนาย Spam probability 0.9999 ควรสรุปอย่างไร

**เฉลย:** โมเดลอาจจัด class ได้ถูก แต่ probability มีแนวโน้มมั่นใจเกินจริง เพราะหลักฐานที่มีความหมายซ้ำกันถูกคูณราวกับเป็นอิสระ ควรตรวจ correlation หรือ dependency ภายใน class, calibration curve และเปรียบเทียบกับ feature set ที่ลดความซ้ำซ้อน

### ข้อ 5: Model selection

จับหมวดหมู่ข่าวจากจำนวนครั้งที่แต่ละคำปรากฏควรเริ่มจากโมเดลใด เพราะเหตุใด

**เฉลย:** เริ่มจาก `MultinomialNB` เพราะ features เป็น non-negative word counts ซึ่งสอดคล้องกับ multinomial event model ถ้าข้อมูล class imbalance มากควรทดลอง `ComplementNB` เพิ่มและเปรียบเทียบบน validation data

### ข้อ 6: Debugging

เหตุใดจึงห้าม fit preprocessing หรือโมเดลโดยใช้ข้อมูลทั้งหมดก่อน train-test split

**เฉลย:** เพราะข้อมูลจาก test set จะมีอิทธิพลต่อ parameters ที่ใช้สร้างโมเดล ทำให้ test set ไม่เป็น unseen data และ metric สูงเกินความสามารถจริง ต้อง split ก่อน แล้วเรียน preprocessing parameters และ model parameters จาก training data เท่านั้น

## 20. Mini-project: Spam Message Classifier

สร้างตัวจำแนกข้อความเป็น Spam หรือ Not Spam โดย:

1. กำหนดให้หนึ่งแถวแทนหนึ่งข้อความและตรวจ class distribution
2. แบ่ง train-test แบบ stratified
3. แปลงข้อความเป็น word counts ด้วย `CountVectorizer`
4. ฝึก `MultinomialNB`
5. รายงาน confusion matrix, precision, recall, F1-score และ accuracy
6. เปลี่ยนค่า `alpha` อย่างน้อย 3 ค่าแล้วอธิบายผล
7. ตรวจข้อความที่ทำนายผิดอย่างน้อย 10 รายการ
8. อภิปราย privacy, bias, dataset shift และต้นทุนของ false positive กับ false negative

### เกณฑ์ประเมิน

| ด้าน | หลักฐานที่ต้องมี |
|---|---|
| Correct workflow | split ก่อน fit vectorizer และ model |
| Reproducibility | กำหนด random state และระบุ package versions |
| Interpretation | ไม่รายงาน accuracy เพียงค่าเดียว |
| Validation | ตรวจ confusion matrix และ prediction errors |
| Experiment | เปรียบเทียบ `alpha` โดยใช้ข้อมูลแบ่งแบบเดียวกัน |
| Critical thinking | อธิบาย assumption, bias และ deployment risk |

## 21. Mastery Checklist

- [ ] อธิบาย classification input และ output ได้
- [ ] แยก prior, likelihood, evidence และ posterior ได้
- [ ] derive Bayes' Rule จาก conditional probability ได้
- [ ] คำนวณตัวอย่าง Drew และอธิบาย source correction ได้
- [ ] อธิบาย conditional independence โดยไม่สับสนกับ unconditional independence ได้
- [ ] อธิบายเหตุผลที่ใช้ log probabilities ได้
- [ ] เลือก Naive Bayes variant ตามชนิด feature ได้
- [ ] คำนวณ Laplace smoothing และอธิบายตัวส่วนได้
- [ ] สร้าง `GaussianNB` ด้วย train-test split โดยไม่มี leakage ได้
- [ ] อธิบาย custom Naive Bayes และเปรียบเทียบผลกับ `BernoulliNB` ได้
- [ ] แปลงข้อความด้วย `CountVectorizer` โดย fit เฉพาะ training data ได้
- [ ] สร้าง `MultinomialNB` และตีความ FP/FN ในบริบท spam ได้
- [ ] ตีความ confusion matrix และข้อจำกัดของ accuracy ได้
- [ ] แยก classification performance ออกจาก probability calibration ได้
- [ ] อธิบายข้อจำกัดด้าน bias, privacy และ dataset shift ได้

## 22. Key Takeaways

Naive Bayes นำ Bayes' Rule มาใช้จำแนกคลาส โดยประมาณ prior จากสัดส่วนคลาสและ likelihood จากการกระจายของ features ภายในคลาส สมมติฐาน conditional independence ทำให้ joint likelihood แตกเป็นผลคูณของ likelihood ราย feature จึงฝึกและทำนายได้เร็ว

ความเรียบง่ายนี้มีต้นทุน Features ที่สัมพันธ์กันอาจทำให้หลักฐานถูกนับซ้ำและ probability มั่นใจเกินจริง การใช้งานที่ดีจึงต้องเลือก likelihood ให้ตรงชนิดข้อมูล ใช้ smoothing เมื่อมี categorical counts แยก train กับ test อย่างถูกต้อง และประเมินทั้ง classification performance กับ probability calibration ตามวัตถุประสงค์

## 23. Glossary

| คำศัพท์ | ความหมาย |
|---|---|
| Classification | การทำนาย class label จาก features |
| Feature | ตัวแปรนำเข้าที่ใช้อธิบายหรือทำนาย |
| Class | กลุ่มคำตอบที่โมเดลต้องเลือก |
| Prior | ความน่าจะเป็นของคลาสก่อนเห็นตัวอย่างใหม่ |
| Likelihood | ความเป็นไปได้ของ features เมื่อกำหนดคลาส |
| Evidence | ความน่าจะเป็นรวมของ features |
| Posterior | ความน่าจะเป็นของคลาสหลังเห็น features |
| Conditional independence | ความเป็นอิสระของ features เมื่อกำหนด class แล้ว |
| MAP | การเลือกคลาสที่มี posterior สูงสุด |
| Probability density | ความหนาแน่นของความน่าจะเป็นสำหรับค่าต่อเนื่อง |
| Laplace smoothing | การเพิ่ม pseudo-count เพื่อป้องกัน probability เป็นศูนย์ |
| Calibration | ความสอดคล้องระหว่าง predicted probability กับความถี่จริง |

## 24. Source Coverage Audit

| เนื้อหาในเอกสาร | ส่วนใน Master Note | สถานะ |
|---|---|---|
| Classification overview และ use cases | ส่วน 1 | ครบ |
| Bayes' Rule และองค์ประกอบ | ส่วน 3 | ครบและขยาย derivation |
| ตัวอย่างชื่อ Drew หนึ่ง feature | ส่วน 3.3 | ครบ |
| Multiple features และ chain rule | ส่วน 4 | ครบและขยายปัญหาความซับซ้อน |
| Naive conditional independence | ส่วน 4.2 | ครบ |
| ตัวอย่างคำนวณ Male/Female | ส่วน 5 | ตรวจใหม่และแก้ข้อผิดพลาดจากสไลด์ |
| Advantages and disadvantages | ส่วน 14 | ครบและขยาย failure modes |
| Continuous values และ Gaussian density | ส่วน 7 | ครบและอธิบาย density |
| Laplacian correction | ส่วน 8 | ครบและปรับศัพท์เป็น Laplace smoothing |
| Custom Naive Bayes กับ Play Tennis | ส่วน 11 | ครบทั้ง preprocessing, fit, predict และผลสาม queries |
| One-hot encoding และ BernoulliNB | ส่วน 11.4 | ครบ พร้อมเพิ่ม Pipeline สำหรับ unknown categories |
| Spam dataset และ CountVectorizer | ส่วน 12.1-12.2 | ครบ พร้อมอธิบาย sparse matrix และ class balance |
| Train-test split และ MultinomialNB | ส่วน 12.3-12.4 | ครบ พร้อมชี้ preprocessing leakage ในลำดับเดิม |
| Confusion matrix และ classification report | ส่วน 12.5 | ครบ พร้อมคำนวณและแปลผล metrics |
| Reference ในสไลด์ | References | ครบ |

## References

1. Ekarat Rattagan. *Week 4: Naive Bayes Classification*. DADS6003 Applied Machine Learning, 20 February 2026.
2. Scikit-learn developers. [Naive Bayes User Guide](https://scikit-learn.org/stable/modules/naive_bayes.html).
3. Scikit-learn developers. [GaussianNB API Reference](https://scikit-learn.org/stable/modules/generated/sklearn.naive_bayes.GaussianNB.html).
4. Scikit-learn developers. [Probability Calibration](https://scikit-learn.org/stable/modules/calibration.html).
5. Olabenjo, B. [Applying Naive Bayes Classification to Google Play Apps Categorization](https://arxiv.org/abs/1608.08574). arXiv:1608.08574, 2016.
6. Course lab. [Naive Bayes with Play Tennis](https://github.com/mdanmek/nida-dads-notes/blob/main/dads6003-applied_ml/lab/naive_bayes.ipynb).
7. Course lab. [Naive Bayes Spam Email Classifier](https://github.com/mdanmek/nida-dads-notes/blob/main/dads6003-applied_ml/lab/naive_bayes_spam_email_classifier.ipynb).
