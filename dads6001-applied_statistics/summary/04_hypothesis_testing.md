# Hypothesis Testing: จากข้อมูลตัวอย่างสู่การตัดสินใจเกี่ยวกับประชากร

บทก่อนหน้าใช้ **Confidence Interval** เพื่อถามว่า “ค่าพารามิเตอร์ของประชากรน่าจะอยู่ในช่วงใด” ส่วนบทนี้เปลี่ยนคำถามเป็น “ข้อมูลที่เก็บมาให้หลักฐานเพียงพอต่อข้ออ้างที่สนใจหรือไม่”

สมมติผู้จัดการร้านอ้างว่า ลูกค้ารอคิวเฉลี่ยน้อยกว่า 5 นาที เราเก็บข้อมูลลูกค้า 15 คนแล้วได้ค่าเฉลี่ย 4.29 นาที แม้ 4.29 จะน้อยกว่า 5 แต่ยังสรุปทันทีไม่ได้ว่าเวลารอเฉลี่ยของลูกค้าทั้งหมดน้อยกว่า 5 นาที เพราะถ้าสุ่มลูกค้าชุดใหม่ ค่าเฉลี่ยย่อมเปลี่ยนไป

Hypothesis testing จึงไม่ได้ดูเฉพาะว่า sample mean อยู่ด้านใดของค่าที่อ้าง แต่ดูด้วยว่า **ความแตกต่างนั้นใหญ่เพียงใดเมื่อเทียบกับ sampling variability** หรือความผันผวนที่เกิดจากการสุ่มตัวอย่าง

---

## 1. Hypothesis คือข้ออ้างเกี่ยวกับประชากร

Hypothesis ในวิชาสถิติคือข้อความเกี่ยวกับ **population parameter** ไม่ใช่ข้อความเกี่ยวกับ sample statistic

- “เวลารอเฉลี่ยของลูกค้าทั้งหมดน้อยกว่า 5 นาที” เป็นข้ออ้างเกี่ยวกับ population mean หรือ $\mu$
- “ลูกค้า 15 คนที่เก็บข้อมูลมีเวลารอเฉลี่ย 4.29 นาที” เป็นผลจาก sample mean หรือ $\bar{x}$

เราใช้ค่าที่สังเกตได้จาก sample เป็นหลักฐานเพื่อเรียนรู้ค่าที่มองไม่เห็นของ population

ตัวอย่างอื่นจาก lecture ได้แก่ คะแนนเฉลี่ยของนักเรียนชายสูงกว่านักเรียนหญิงหรือไม่ คะแนนหลังเรียนของนักเรียนกลุ่มเดิมสูงกว่าก่อนเรียนหรือไม่ และสัดส่วนประชาชนที่สนับสนุนนโยบายสูงกว่า 80% หรือไม่ คำถามเหล่านี้ต่างกันตรง parameter และโครงสร้างข้อมูล จึงอาจใช้วิธีทดสอบต่างกัน แต่ตรรกะพื้นฐานเหมือนกัน

---

## 2. Null และ Alternative Hypotheses

การทดสอบเริ่มจากตั้งข้อความสองข้อความที่แข่งขันกัน

**Null hypothesis** เขียนเป็น $H_0$ เป็นจุดตั้งต้นที่ใช้คำนวณว่า “ถ้าข้ออ้างนี้จริง ผลที่เห็นจาก sample แปลกเพียงใด” โดยทั่วไป $H_0$ มีเครื่องหมายเท่ากับอยู่ด้วย

**Alternative hypothesis** เขียนเป็น $H_1$ หรือ $H_a$ เป็นข้อสรุปที่ต้องมีหลักฐานจากข้อมูลมาสนับสนุน

ตัวอย่าง ผู้จัดการอ้างว่าเวลารอเฉลี่ยน้อยกว่า 5 นาที:

$$
H_0: \mu = 5
$$

$$
H_1: \mu < 5
$$

เครื่องหมายใน $H_1$ เป็นตัวกำหนดทิศทางของการทดสอบ

| คำถามในโจทย์ | Alternative hypothesis | ชนิดการทดสอบ |
|---|---|---|
| แตกต่างจาก | $\mu \ne \mu_0$ | Two-sided |
| มากกว่า | $\mu > \mu_0$ | Right-sided |
| น้อยกว่า | $\mu < \mu_0$ | Left-sided |

ควรกำหนดทิศทางจากคำถามวิจัย **ก่อนเห็นผลข้อมูล** ไม่ควรเห็น sample mean แล้วค่อยเลือกหางที่ทำให้ p-value เล็กลง

> ในการคำนวณ เราใช้ค่าขอบเขตที่มีเครื่องหมายเท่ากับ เช่น $\mu=5$ แม้โจทย์อาจเขียน null เชิงประกอบว่า $\mu \ge 5$ ก็ตาม

---

## 3. ตรรกะของ Hypothesis Testing

วิธีคิดมีเพียงแกนเดียว:

1. สมมติไว้ก่อนว่า $H_0$ จริง
2. พิจารณาว่าผลจาก sample อยู่ไกลจากค่าที่ $H_0$ คาดไว้เพียงใด
3. ถ้าผลที่พบเกิดขึ้นได้ยากมากภายใต้ $H_0$ ข้อมูลจึงเป็นหลักฐานต่อต้าน $H_0$

เปรียบเหมือนการโยนเหรียญที่อ้างว่ายุติธรรม ถ้าโยน 10 ครั้งแล้วออกหัว 6 ครั้ง ยังไม่น่าแปลกมาก แต่ถ้าออกหัว 10 ครั้ง ผลนั้นขัดกับสิ่งที่คาดภายใต้เหรียญยุติธรรมมากกว่า

ผลที่เข้ากันได้กับ $H_0$ ไม่ได้พิสูจน์ว่า $H_0$ จริง เพียงแปลว่า sample ปัจจุบันยังไม่มีหลักฐานเพียงพอให้ปฏิเสธ

---

## 4. Test Statistic: ความต่างเมื่อเทียบกับความไม่แน่นอน

Test statistic แปลงความต่างระหว่างค่าที่ประมาณได้กับค่าภายใต้ $H_0$ ให้อยู่ในหน่วยของ standard error

$$
\mathrm{Test\ statistic} = \frac{\mathrm{Estimate}-\mathrm{Null\ value}}{\mathrm{SE\ under\ }H_0}
$$

ตัวเศษบอกว่า estimate ต่างจาก null value เท่าใด ส่วนตัวส่วนบอกว่าความผันผวนจากการสุ่มตัวอย่างตามปกติมีขนาดเท่าใด

- Statistic ใกล้ 0: estimate อยู่ใกล้ค่าภายใต้ $H_0$
- Statistic เป็นบวกมาก: estimate อยู่สูงกว่าค่าภายใต้ $H_0$ หลาย standard errors
- Statistic เป็นลบมาก: estimate อยู่ต่ำกว่าค่าภายใต้ $H_0$ หลาย standard errors

สำหรับการทดสอบค่าเฉลี่ยเมื่อไม่ทราบ population standard deviation เราใช้ t statistic และเปรียบเทียบกับ t distribution

---

## 5. p-value ตอบคำถามอะไร

p-value คือความน่าจะเป็นที่จะได้ผลอย่างน้อยสุดโต่งเท่ากับที่สังเกต เมื่อสมมติว่า $H_0$ จริง

$$
p\mathrm{-value} = \mathrm{P}(\mathrm{result\ at\ least\ as\ extreme\ as\ observed}\mid H_0)
$$

คำว่า “สุดโต่ง” ต้องตีความตาม $H_1$

- $H_1: \mu < \mu_0$ สนใจหางซ้าย
- $H_1: \mu > \mu_0$ สนใจหางขวา
- $H_1: \mu \ne \mu_0$ สนใจทั้งสองหาง

p-value ขนาดเล็กหมายความว่า ผลที่สังเกตไม่ค่อยเข้ากับ $H_0$ จึงเป็นหลักฐานต่อต้าน $H_0$

p-value **ไม่ใช่** ความน่าจะเป็นที่ $H_0$ เป็นจริง และไม่ใช่ขนาดของผลกระทบ

---

## 6. การตัดสินใจด้วยระดับนัยสำคัญ

ระดับนัยสำคัญ หรือ $\alpha$ คือเกณฑ์ที่กำหนดไว้ล่วงหน้าเพื่อควบคุมความเสี่ยงของ Type I error โดยโจทย์มักกำหนด $\alpha=0.05$

- ถ้า p-value $\le \alpha$: reject $H_0$
- ถ้า p-value $> \alpha$: fail to reject $H_0$

เมื่อ fail to reject $H_0$ ควรเขียนว่า “ยังไม่มีหลักฐานเพียงพอ” ไม่ควรเขียนว่า “ยอมรับ $H_0$” หรือ “พิสูจน์แล้วว่าไม่แตกต่าง”

### 6.1 Type I error

Type I error เกิดเมื่อ reject $H_0$ ทั้งที่ $H_0$ จริง ความน่าจะเป็นสูงสุดของความผิดพลาดชนิดนี้ถูกควบคุมด้วย $\alpha$

### 6.2 Type II error และ Power

Type II error เกิดเมื่อ fail to reject $H_0$ ทั้งที่ $H_1$ เป็นจริง ให้ความน่าจะเป็นเป็น $\beta$

$$
\mathrm{Power} = 1-\beta
$$

Power คือโอกาสที่การทดสอบจะตรวจพบผลที่มีอยู่จริง โดยทั่วไป power สูงขึ้นเมื่อ sample size ใหญ่ขึ้น ผลต่างจริงมีขนาดใหญ่ขึ้น หรือข้อมูลมีความผันผวนน้อยลง

---

## 7. Hypothesis Test เชื่อมกับ Confidence Interval อย่างไร

ทั้งสองวิธีใช้ estimate และ standard error ชุดเดียวกัน เพียงตอบคนละคำถาม

- Confidence interval บอกช่วงค่าพารามิเตอร์ที่เข้ากันได้กับข้อมูล
- Hypothesis test ตรวจว่าค่าที่ระบุใน $H_0$ เข้ากันได้กับข้อมูลเพียงใด

สำหรับ two-sided test ที่ $\alpha=0.05$:

- ถ้า null value อยู่นอก 95% CI จะ reject $H_0$
- ถ้า null value อยู่ใน 95% CI จะ fail to reject $H_0$

---

## 8. เลือกการทดสอบจากโครงสร้างข้อมูล

ก่อนเปิด R ให้ตอบสี่คำถาม:

1. Parameter ที่ถามคือ mean, proportion หรือความสัมพันธ์ของตัวแปรเชิงหมวดหมู่
2. มีหนึ่งกลุ่ม สองกลุ่ม หรือหลายกลุ่ม
3. ถ้ามีสองชุดข้อมูล ชุดข้อมูล independent หรือ paired
4. Alternative เป็น two-sided, less หรือ greater

| โครงสร้างโจทย์ | สิ่งที่เปรียบเทียบ | วิธีหลัก |
|---|---|---|
| ตัวเลขหนึ่ง sample เทียบค่ามาตรฐาน | $\mu$ กับ $\mu_0$ | One-sample t test |
| ตัวเลขสองกลุ่ม คนละหน่วยทดลอง | $\mu_1$ กับ $\mu_2$ | Independent two-sample t test |
| ก่อน–หลัง หรือจับคู่เป็นคู่เดียวกัน | Mean ของค่าผลต่าง | Paired t test |
| ค่าเฉลี่ยมากกว่าสองกลุ่ม | หลาย population means | ANOVA |
| หนึ่งสัดส่วนเทียบค่ามาตรฐาน | $p$ กับ $p_0$ | One-proportion test |
| สัดส่วนของสองกลุ่ม | $p_1$ กับ $p_2$ | Two-proportion test |

คำว่า one mean, independent means และ paired means เป็นชื่อย่อที่บอก **parameter และโครงสร้าง sample** ชื่อเต็มที่พบบ่อยคือ one-sample t test, independent two-sample t test และ paired-sample t test

---

## 9. การทดสอบค่าเฉลี่ยที่ใช้ใน Lecture และ Lab

### 9.1 One-sample t test

ใช้เมื่อมีตัวแปรเชิงตัวเลขหนึ่ง sample และต้องการเปรียบเทียบ population mean กับค่ามาตรฐาน

~~~r
t.test(x, mu = null_value, alternative = "two.sided")
t.test(x, mu = null_value, alternative = "less")
t.test(x, mu = null_value, alternative = "greater")
~~~

### 9.2 Independent two-sample t test

ใช้เมื่อเปรียบเทียบค่าเฉลี่ยของสองกลุ่ม และหน่วยทดลองในกลุ่มหนึ่งไม่ได้จับคู่กับอีกกลุ่ม

**Welch t test** ไม่สมมติว่า population variances เท่ากัน และเป็นค่าเริ่มต้นของ t.test() จึงเป็นตัวเลือกทั่วไปเมื่อโจทย์ไม่ได้ระบุ equal variances

~~~r
# Welch two-sample t test
t.test(group_1, group_2, alternative = "two.sided")
~~~

**Pooled-variance t test** สมมติว่า population variances เท่ากัน ใช้เมื่อโจทย์กำหนดสมมติฐานนี้หรือมีเหตุผลรองรับชัดเจน

~~~r
# Pooled-variance two-sample t test
t.test(group_1, group_2, alternative = "two.sided", var.equal = TRUE)
~~~

ใน Lab มีการตรวจความแปรปรวนก่อนใช้ pooled test แต่ในการวิเคราะห์ทั่วไปไม่ควรเลือก pooled เพียงเพราะ variance test ไม่ significant เพราะ “ไม่พบความแตกต่าง” ไม่ได้พิสูจน์ว่า variances เท่ากัน หากโจทย์ไม่สั่งและไม่แน่ใจ ให้ใช้ Welch

### 9.3 Paired t test

ใช้เมื่อข้อมูลสองค่ามาจากหน่วยทดลองเดียวกัน เช่น น้ำหนักก่อนและหลังรักษาของผู้ป่วยคนเดิม หลักการคือสร้างค่าผลต่างในแต่ละคู่ แล้วทำ one-sample t test กับค่าผลต่างนั้น

~~~r
# ตรวจว่า after - before มากกว่า 0 หรือไม่
t.test(after, before, paired = TRUE, alternative = "greater")

# คำสั่งที่มีความหมายเท่ากัน
difference <- after - before
t.test(difference, mu = 0, alternative = "greater")
~~~

ห้ามใช้ independent test กับข้อมูลก่อน–หลัง เพราะจะทิ้งข้อมูลความสัมพันธ์ภายในคนเดียวกัน

### 9.4 มากกว่าสองค่าเฉลี่ยและการทดสอบสัดส่วน

ถ้ามีหลายกลุ่ม การทำ t tests ทีละคู่จำนวนมากเพิ่มโอกาส Type I error วิธีมาตรฐานคือ ANOVA ส่วนข้อมูลจำนวน success จากจำนวนทั้งหมดสนใจ population proportion จึงใช้ proportion test ไม่ใช่ t test Lecture กล่าวถึงสองหัวข้อนี้ในภาพรวม ส่วน Lab ชุดนี้เน้น t tests สำหรับ means

---

## 10. Assumptions: ต้องตรวจอะไรและตรวจจากข้อมูลใด

### 10.1 Randomness และ Independence

การสุ่มตัวอย่างและความเป็นอิสระต้องพิจารณาจาก **การออกแบบการเก็บข้อมูล** ไม่สามารถพิสูจน์จาก Shapiro–Wilk test หรือกราฟได้

### 10.2 Normality

เมื่อ sample เล็ก t test ต้องการให้ distribution ที่เกี่ยวข้องไม่เบี่ยงจาก normal มากและไม่มี outlier รุนแรง

- One-sample t test: ตรวจตัวแปรที่วัด
- Paired t test: ตรวจ **ค่าผลต่างในแต่ละคู่**
- Independent t test: ตรวจแต่ละกลุ่ม

~~~r
hist(x)
boxplot(x, horizontal = TRUE)
qqnorm(x)
qqline(x, col = "red")
shapiro.test(x)
~~~

Shapiro p-value มากกว่า .05 หมายถึงยังไม่มีหลักฐานต่อต้าน normality ไม่ได้พิสูจน์ว่าข้อมูลเป็น normal โดยเฉพาะเมื่อ sample เล็ก

### 10.3 Outliers

Boxplot ใช้เกณฑ์ IQR เพื่อช่วยชี้ค่าที่ควรตรวจสอบ ค่าที่ถูก flag ไม่จำเป็นต้องลบทิ้ง ต้องตรวจว่าเป็นข้อมูลผิด เหตุการณ์จริง หรือ observation ที่สำคัญต่อโจทย์

~~~r
boxplot.stats(x)$out
~~~

---

## 11. เตรียม Google Colab สำหรับรัน R

รัน cell นี้หนึ่งครั้งใน Python runtime:

~~~python
%load_ext rpy2.ipython
~~~

จากนั้นใช้ %%R ที่บรรทัดแรกของทุก cell ที่เป็น R:

~~~r
%%R
# ปิด scientific notation และแสดงประมาณ 4 significant digits
options(scipen = 999, digits = 4)
~~~

digits = 4 ควบคุมจำนวน significant digits ไม่ได้บังคับทศนิยมสี่ตำแหน่งเสมอ หากต้องการพิมพ์ค่าหนึ่งเป็นทศนิยมสี่ตำแหน่ง ใช้ sprintf("%.4f", value)

Lab บทนี้ใช้คำสั่งจาก base R เป็นหลัก จึงไม่ต้องติดตั้ง package เพิ่ม

---

## 12. Lab 1.1: เวลาใช้โปรแกรม StatCrunch

โจทย์ให้ข้อมูลเวลาใช้งาน 15 ค่า และถามว่า population mean **แตกต่างจาก 7** หรือไม่ ที่ระดับนัยสำคัญ .05

### วิเคราะห์โจทย์

ข้อมูลเป็นตัวเลขหนึ่ง sample คำว่า “different from” ทำให้เป็น two-sided one-sample t test

$$
H_0: \mu = 7
$$

$$
H_1: \mu \ne 7
$$

### รัน R

~~~r
%%R
statcrunch_time <- c(6.5, 4, 3.5, 0, 12, 5, 12, 15, 12, 0, 1, 8, 0.5, 2, 7)

# ตรวจ normality และทดสอบ mean เทียบกับ 7 แบบสองด้าน
print(shapiro.test(statcrunch_time))
print(t.test(statcrunch_time, mu = 7, alternative = "two.sided"))
~~~

### อ่านผล

- Shapiro–Wilk: $W=0.9146$, p-value = 0.1590
- Sample mean = 5.9000
- $t=-0.8538$, df = 14
- p-value = 0.4076
- 95% CI = [3.1366, 8.6634]

แม้ sample mean ต่ำกว่า 7 แต่ผลต่างยังเล็กเมื่อเทียบกับ standard error ค่า 7 ยังอยู่ใน 95% CI และ p-value มากกว่า .05

### เขียนตอบข้อสอบ

> กำหนด $H_0:\mu=7$ และ $H_1:\mu\ne7$ ใช้ two-sided one-sample t test เนื่องจากเป็นข้อมูลเชิงตัวเลขหนึ่ง sample การตรวจ Shapiro–Wilk ให้ p-value = 0.1590 จึงยังไม่มีหลักฐานต่อต้าน normality ผลการทดสอบได้ $t(14)=-0.8538$, p-value = 0.4076 และ 95% CI เท่ากับ [3.1366, 8.6634] เนื่องจาก p-value มากกว่า .05 จึง fail to reject $H_0$ ยังไม่มีหลักฐานเพียงพอว่าเวลาใช้ StatCrunch เฉลี่ยแตกต่างจาก 7

---

## 13. Lab 1.2: เวลารอของลูกค้า

คำถามทางสถิติคือ population mean ต่ำกว่า 5 นาทีหรือไม่

### วิเคราะห์โจทย์

ข้อมูลเป็นเวลาหนึ่ง sample และ “less than” ทำให้เป็น left-sided one-sample t test

$$
H_0: \mu = 5
$$

$$
H_1: \mu < 5
$$

### รัน R

~~~r
%%R
waiting_time <- c(4.21, 5.55, 3.02, 5.13, 4.77, 2.34, 3.54, 3.20,
                  4.50, 6.10, 0.38, 5.12, 6.46, 6.19, 3.79)

# ตรวจ normality และทดสอบว่า mean ต่ำกว่า 5 หรือไม่
print(shapiro.test(waiting_time))
print(t.test(waiting_time, mu = 5, alternative = "less"))
~~~

### อ่านผล

- Shapiro–Wilk p-value = 0.5085
- Sample mean = 4.2867 นาที
- $t=-1.6867$, df = 14
- One-sided p-value = 0.0569
- One-sided 95% CI มี upper bound เท่ากับ 5.0316 นาที

Sample mean ต่ำกว่า 5 จริง แต่ p-value ยังสูงกว่า .05 เล็กน้อย จึงยังไม่มีหลักฐานเพียงพอ

### เขียนตอบข้อสอบ

> กำหนด $H_0:\mu=5$ และ $H_1:\mu<5$ ใช้ left-sided one-sample t test การตรวจ Shapiro–Wilk ให้ p-value = 0.5085 ผลการทดสอบได้ $t(14)=-1.6867$, p-value = 0.0569 เนื่องจาก p-value มากกว่า .05 จึง fail to reject $H_0$ ยังไม่มีหลักฐานเพียงพอว่าเวลารอเฉลี่ยของลูกค้าน้อยกว่า 5 นาที

คำกล่าวว่า “ลูกค้าแทบจะแน่ใจว่าจะรอน้อยกว่า 5 นาที” ยังแรงกว่าสิ่งที่ mean test ตอบ เพราะ mean ต่ำกว่า 5 ก็ไม่ได้หมายความว่าลูกค้าแต่ละคนจะรอน้อยกว่า 5 นาที

---

## 14. Lab 1.3: ความแข็งแรงของฉนวน

โจทย์ถามว่าความแข็งแรงเฉลี่ยของฉนวนสูงกว่า 1,500 หน่วยหรือไม่ จากข้อมูล 30 ค่า

### วิเคราะห์โจทย์

เป็น right-sided one-sample t test

$$
H_0: \mu = 1500
$$

$$
H_1: \mu > 1500
$$

### รัน R

~~~r
%%R
strength <- c(1870, 1764, 1774, 1680, 1728, 1734, 1550, 1810, 1656, 1662,
              1756, 1652, 1610, 1734, 1762, 1736, 1634, 1866, 1784, 1820,
              1522, 1744, 1696, 1788, 1592, 1688, 1662, 1810, 1866, 1752)

# ตรวจข้อมูลจากหลายมุม
print(summary(strength))
boxplot(strength, horizontal = TRUE, main = "Strength of insulators")
qqnorm(strength)
qqline(strength, col = "red")
print(shapiro.test(strength))

# ทดสอบว่า population mean สูงกว่า 1500 หรือไม่
print(t.test(strength, mu = 1500, alternative = "greater"))
~~~

### อ่านผล

- Mean = 1723.4 และ standard deviation ประมาณ 89.55
- Q–Q plot มีจุดใกล้แนวเส้นตรงโดยรวม
- Shapiro–Wilk p-value = 0.6220
- เกณฑ์ IQR ไม่พบ outlier
- $t=13.6640$, df = 29, p-value < 0.0001
- One-sided 95% lower bound = 1695.62

เอกสารเฉลยเสริมแสดงเกณฑ์ mean $\pm$ 2 SD ด้วย แต่ไม่ควรใช้เกณฑ์นี้เป็นเหตุผลอัตโนมัติในการลบข้อมูล ควรตรวจข้อมูลดิบและบริบทประกอบ

### เขียนตอบข้อสอบ

> กำหนด $H_0:\mu=1500$ และ $H_1:\mu>1500$ ใช้ right-sided one-sample t test ข้อมูลไม่มี outlier ตามเกณฑ์ IQR, Q–Q plot ใกล้เส้นตรง และ Shapiro–Wilk ให้ p-value = 0.6220 ผลการทดสอบได้ $t(29)=13.6640$, p-value < 0.0001 และ one-sided 95% lower confidence bound เท่ากับ 1695.62 จึง reject $H_0$ มีหลักฐานเพียงพอว่าความแข็งแรงเฉลี่ยของฉนวนสูงกว่า 1,500 หน่วย

---

## 15. Lab 2.1: น้ำหนักก่อนและหลังการรักษา

ข้อมูลเป็นน้ำหนักก่อนและหลังของผู้ป่วย 29 คนเดียวกัน โจทย์ถามว่าน้ำหนักเฉลี่ยหลังรักษาสูงขึ้นหรือไม่

### วิเคราะห์โจทย์

มีสองค่าจากคนเดียวกัน จึงเป็น paired data กำหนด difference = after - before

$$
H_0: \mu_d = 0
$$

$$
H_1: \mu_d > 0
$$

### รัน R

~~~r
%%R
before <- c(80.5, 84.9, 81.5, 82.6, 79.9, 88.7, 94.9, 76.3, 81.0, 80.5,
            85.0, 89.2, 81.3, 76.5, 70.0, 80.4, 83.3, 83.0, 87.7, 84.2,
            86.4, 76.5, 80.2, 87.8, 83.3, 79.7, 84.5, 80.8, 87.4)

after <- c(82.2, 85.6, 81.4, 81.9, 76.4, 103.6, 98.4, 93.4, 73.4, 82.1,
           96.7, 95.3, 82.4, 72.5, 90.9, 71.3, 85.4, 81.6, 89.1, 83.9,
           82.7, 75.7, 82.6, 100.4, 85.2, 83.6, 84.6, 96.2, 86.7)

# Paired t test ตรวจ normality ของค่าผลต่าง
weight_change <- after - before
print(shapiro.test(weight_change))
print(t.test(after, before, paired = TRUE, alternative = "greater"))
~~~

### อ่านผล

- Mean difference = 2.5586 หน่วย
- Shapiro–Wilk ของ differences: p-value = 0.3889
- $t=2.4686$, df = 28
- One-sided p-value = 0.0100
- One-sided 95% lower bound = 0.7955

### เขียนตอบข้อสอบ

> เนื่องจากน้ำหนักก่อนและหลังมาจากผู้ป่วยคนเดียวกัน จึงใช้ paired t test โดยกำหนด difference = after - before, $H_0:\mu_d=0$ และ $H_1:\mu_d>0$ การตรวจ differences ด้วย Shapiro–Wilk ให้ p-value = 0.3889 ผลการทดสอบได้ mean difference = 2.5586, $t(28)=2.4686$, p-value = 0.0100 จึง reject $H_0$ มีหลักฐานเพียงพอว่าน้ำหนักเฉลี่ยหลังการรักษาสูงกว่าก่อนการรักษา

---

## 16. Lab 2.2: ระยะเวลาที่รสชาติหมากฝรั่งคงอยู่

โจทย์เปรียบเทียบผู้หญิง 8 คนกับผู้ชาย 7 คน และถามว่าค่าเฉลี่ยแตกต่างกันหรือไม่

### วิเคราะห์โจทย์

ผู้หญิงและผู้ชายเป็นคนละกลุ่ม จึง independent คำว่า “different” ทำให้เป็น two-sided test เฉลยต้นฉบับตรวจ equal variances แล้วใช้ pooled t test

$$
H_0: \mu_F-\mu_M = 0
$$

$$
H_1: \mu_F-\mu_M \ne 0
$$

### รัน R

~~~r
%%R
female <- c(15, 21, 29, 22, 19, 25, 35, 23)
male <- c(22, 24, 23, 30, 12, 17, 28)

print(shapiro.test(female))
print(shapiro.test(male))

# เฉลยกำหนด equal variances จึงใช้ pooled-variance t test
print(t.test(female, male, alternative = "two.sided", var.equal = TRUE))
~~~

หากโจทย์ไม่ได้ให้สมมติว่า variances เท่ากัน ใช้ Welch โดยเอา var.equal = TRUE ออก

### อ่านผล

- Female mean = 23.6250, male mean = 22.2857
- Shapiro p-values ของทั้งสองกลุ่มมากกว่า .05
- $t=0.4192$, df = 13, p-value = 0.6819
- 95% CI ของ $\mu_F-\mu_M$ = [-5.5622, 8.2408]

### เขียนตอบข้อสอบ

> กำหนด $H_0:\mu_F-\mu_M=0$ และ $H_1:\mu_F-\mu_M\ne0$ ใช้ two-sided pooled two-sample t test ตามสมมติฐาน equal variances ของโจทย์ ผลการทดสอบได้ $t(13)=0.4192$, p-value = 0.6819 และ 95% CI เท่ากับ [-5.5622, 8.2408] จึง fail to reject $H_0$ ยังไม่มีหลักฐานเพียงพอว่าระยะเวลาที่รสชาติหมากฝรั่งคงอยู่เฉลี่ยแตกต่างกันระหว่างผู้หญิงและผู้ชาย

---

## 17. Lab 2.3: เวลาส่งพิซซ่าของร้านท้องถิ่นและร้านเชน

โฆษณาอ้างว่าร้านท้องถิ่นส่งเร็วกว่า เมื่อหน่วยเป็น “เวลา” คำว่าเร็วกว่าแปลว่า mean time **น้อยกว่า** ร้านเชน

### วิเคราะห์โจทย์

เป็น independent groups กำหนดผลต่างเป็น local - chain และเฉลยต้นฉบับใช้ pooled t test

$$
H_0: \mu_L-\mu_C = 0
$$

$$
H_1: \mu_L-\mu_C < 0
$$

### รัน R

~~~r
%%R
local <- c(16.8, 11.7, 15.6, 16.7, 17.5, 18.1, 14.1, 21.8, 13.9, 20.8)
chain <- c(22.0, 15.2, 18.7, 15.6, 20.8, 19.5, 17.0, 19.5, 16.5, 24.0)

print(shapiro.test(local))
print(shapiro.test(chain))

# local เป็น argument แรก: less หมายถึง local - chain < 0
print(t.test(local, chain, alternative = "less", var.equal = TRUE))
~~~

### อ่านผล

- Local mean = 16.70 นาที, chain mean = 18.88 นาที
- Observed difference = -2.18 นาที
- $t=-1.6341$, df = 18
- One-sided p-value = 0.0598
- One-sided 95% CI ของ local - chain มี upper bound = 0.1334

แม้ sample ของร้านท้องถิ่นเร็วกว่าเฉลี่ย 2.18 นาที แต่ p-value สูงกว่า .05 เล็กน้อย และ interval ยังรวมค่าที่ local อาจช้ากว่าได้เล็กน้อย

### เขียนตอบข้อสอบ

> กำหนด $H_0:\mu_L-\mu_C=0$ และ $H_1:\mu_L-\mu_C<0$ ใช้ left-sided pooled two-sample t test ตามสมมติฐาน equal variances ของโจทย์ ผลการทดสอบได้ $t(18)=-1.6341$, p-value = 0.0598 จึง fail to reject $H_0$ ยังไม่มีหลักฐานเพียงพอที่ระดับ .05 ว่าร้านท้องถิ่นมีเวลาส่งเฉลี่ยน้อยกว่าร้านเชน

การไม่ significant ไม่ได้แปลว่าความต่าง 2.18 นาทีไม่มีความสำคัญทางธุรกิจ เพียงแต่ sample นี้ยังให้หลักฐานทางสถิติไม่เพียงพอ

---

## 18. วิธีอ่านผล t.test() โดยไม่หลงบรรทัด

เมื่อ R แสดงผล ให้หาองค์ประกอบตามลำดับนี้:

1. ชื่อ test: one-sample, Welch, pooled หรือ paired
2. ค่า t และ df
3. p-value
4. Alternative hypothesis ว่าทิศทางตรงกับโจทย์หรือไม่
5. Confidence interval
6. Sample estimate หรือ mean difference

ตรวจทิศทางทุกครั้ง เพราะ alternative = "less" หมายถึง parameter ของ **argument แรกน้อยกว่า argument ที่สอง**

~~~r
# สองคำสั่งนี้ตอบคำถามเดียวกัน
t.test(group_a, group_b, alternative = "less")
t.test(group_b, group_a, alternative = "greater")
~~~

---

## 19. โครงเขียนตอบข้อสอบ

คำตอบที่ครบถ้วนควรมี:

1. Population parameter และ $H_0$, $H_1$
2. ชื่อ test และเหตุผลจากโครงสร้างข้อมูล
3. Assumptions และวิธีตรวจที่เกี่ยวข้อง
4. Statistic, df, p-value และ confidence interval ถ้ามี
5. การเปรียบเทียบ p-value กับ $\alpha$
6. ข้อสรุปด้วยภาษาของโจทย์

แม่แบบสำหรับกรณี reject:

> ใช้ [ชื่อ test] เนื่องจาก [เหตุผล] กำหนด $H_0$: [ข้อความ] และ $H_1$: [ข้อความ] ผลการทดสอบได้ [statistic และ df], p-value = [ค่า] เนื่องจาก p-value น้อยกว่า $\alpha$ จึง reject $H_0$ มีหลักฐานเพียงพอว่า [สรุปในบริบท]

แม่แบบสำหรับกรณี fail to reject:

> ผลการทดสอบได้ [statistic และ df], p-value = [ค่า] เนื่องจาก p-value มากกว่า $\alpha$ จึง fail to reject $H_0$ ยังไม่มีหลักฐานเพียงพอว่า [ข้อความตาม $H_1$]

---

## 20. จุดที่มักทำให้ตอบผิด

### เลือก one-sided หลังเห็นข้อมูล

ต้องเลือกจากคำถามวิจัยก่อนวิเคราะห์ มิฉะนั้น Type I error จะสูงกว่าที่กำหนด

### ใช้ independent test กับ before–after

ข้อมูลก่อน–หลังของคนเดิมต้องใช้ paired test และตรวจ normality ของ differences

### เขียนว่า p-value คือโอกาสที่ null เป็นจริง

p-value คำนวณภายใต้เงื่อนไขว่า $H_0$ จริง จึงไม่ใช่ความน่าจะเป็นของ $H_0$

### เขียนว่า fail to reject แปลว่าเท่ากัน

ข้อมูลอาจยังไม่พอแยกความแตกต่างจาก sampling variability การสรุปที่ถูกคือ “ยังไม่มีหลักฐานเพียงพอ”

### ใช้ Shapiro p-value มากกว่า .05 เป็นหลักฐานว่า normal แน่นอน

ควรเขียนว่า “ยังไม่มีหลักฐานต่อต้าน normality” และดู Q–Q plot, outliers, sample size และการออกแบบร่วมด้วย

### สับสนระหว่าง statistical กับ practical significance

รายงานทั้ง p-value และขนาดความแตกต่างพร้อม confidence interval เพื่อให้ผู้อ่านตัดสินความสำคัญในโลกจริง

---

## 21. สรุปวิธีเลือกคำสั่ง R

~~~r
# One sample
t.test(x, mu = value, alternative = "two.sided")
t.test(x, mu = value, alternative = "less")
t.test(x, mu = value, alternative = "greater")

# Independent groups: Welch เป็นค่าเริ่มต้น
t.test(group_1, group_2, alternative = "two.sided")

# Independent groups: pooled เมื่อสมมติ equal variances
t.test(group_1, group_2, alternative = "two.sided", var.equal = TRUE)

# Paired data
t.test(group_1, group_2, paired = TRUE, alternative = "two.sided")
~~~

two.sided, less และ greater มาจาก $H_1$ ส่วน paired และ var.equal มาจากโครงสร้างข้อมูลและ assumptions

---

## 22. Likely Exam Focus

1. แยก population parameter ออกจาก sample statistic
2. ตั้ง $H_0$ และ $H_1$ จากคำว่าแตกต่าง มากกว่า หรือน้อยกว่า
3. เลือก one-sample, independent หรือ paired t test
4. อธิบายว่า paired test วิเคราะห์ differences
5. อ่าน t, df, p-value, CI และ sample estimates จาก R
6. ตัดสินใจจาก p-value เทียบกับ $\alpha$
7. เขียน “fail to reject” โดยไม่แปลว่า $H_0$ ได้รับการพิสูจน์
8. อธิบาย Type I error, Type II error และ power ในบริบทโจทย์
9. ตรวจ normality จากข้อมูลที่ถูกต้องและไม่พึ่ง Shapiro test เพียงอย่างเดียว
10. แยก statistical significance ออกจาก practical significance

---

## 23. แบบฝึกคิดก่อนสอบ

### ข้อ 1

โรงงานอ้างว่าน้ำหนักบรรจุเฉลี่ยมากกว่า 500 กรัม เก็บสินค้าสุ่ม 20 ชิ้น ควรใช้ test ใด

**คำตอบ:** Right-sided one-sample t test

$$
H_0: \mu = 500
$$

$$
H_1: \mu > 500
$$

### ข้อ 2

วัดความดันผู้ป่วยคนเดิมก่อนและหลังรับยา ต้องใช้ independent หรือ paired test

**คำตอบ:** Paired t test เพราะค่าทั้งสองมาจากคนเดียวกัน ให้สร้าง difference ตามทิศทางที่สนใจแล้วทดสอบ mean difference เทียบกับ 0

### ข้อ 3

ผลการทดสอบให้ p-value = 0.08 ที่ $\alpha=0.05$ เขียนว่า “ยอมรับว่าไม่มีความแตกต่าง” ได้หรือไม่

**คำตอบ:** ไม่ได้ ควรเขียนว่า fail to reject $H_0$ และยังไม่มีหลักฐานเพียงพอว่ามีความแตกต่าง

### ข้อ 4

ถ้า two-sided test ที่ $\alpha=0.05$ ให้ 95% CI ของ mean difference เป็น [1.2, 3.8] ควรตัดสินใจอย่างไร

**คำตอบ:** Reject $H_0$ ที่กำหนด mean difference = 0 เพราะ interval ไม่รวม 0

---

## 24. ภาพรวมทั้งบท

Hypothesis testing ไม่ใช่ขั้นตอนหา p-value อย่างเดียว แต่เป็นกระบวนการเชื่อมคำถามในโลกจริงเข้ากับ population parameter เลือกแบบจำลองตามโครงสร้างข้อมูล ประเมินความแตกต่างเทียบกับ sampling variability แล้วสื่อสารข้อสรุปภายใต้ความไม่แน่นอน

> อ่านคำถาม → ระบุ parameter → ดูโครงสร้าง sample → ตั้ง $H_0$ และ $H_1$ → เลือก test → ตรวจ assumptions → รัน R → อ่าน p-value และ CI → สรุปด้วยภาษาของโจทย์

ถ้าทิศทางของ $H_1$ หรือการแยก independent กับ paired ผิด ต่อให้ R คำนวณถูก คำตอบก็ยังตอบคนละคำถามกับโจทย์

---

## แหล่งที่ใช้จัดทำบทนี้

- lecture04_hypothesis_testing.pptx — 21 slides
- lab04_hypothsis_test1.pdf — Exercise set 1
- lab04_hypothsis_test1_solution.pdf — Solution set 1
- lab04_hypothsis_test1_solution2_normalilty_outliers.pdf — Normality and outlier supplement
- lab04_hypothsis_test2.pdf — Exercise set 2
- lab04_hypothsis_test2_solution.pdf — Solution set 2
