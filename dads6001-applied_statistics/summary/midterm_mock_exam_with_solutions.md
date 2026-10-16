# DADS6001 Mock Midterm Exam พร้อมเฉลยและแนวเขียนตอบ

เอกสารนี้จำลองรูปแบบข้อสอบจาก Lecture 01–04, Lab และเฉลย Lab รวมถึงแนวข้อสอบเก่า โดยเน้นกระบวนการเดียวกับที่ต้องใช้ในห้องสอบจริง:

> อ่านโจทย์ → ระบุ parameter และโครงสร้างข้อมูล → ตรวจ assumptions → เลือกวิธี → รัน R → อ่าน output → เขียนข้อสรุปในบริบท

ข้อสอบจำลองมี 5 ข้อ รวม 30 คะแนน ใช้เวลาฝึก 180 นาที ส่วนแรกเป็นข้อสอบที่ยังไม่มีคำใบ้หรือเฉลย ส่วนเฉลยอยู่ครึ่งหลังของเอกสาร

---

## คำชี้แจง

1. กำหนดระดับนัยสำคัญ $\alpha=0.05$ เว้นแต่โจทย์ระบุเป็นอย่างอื่น
2. แสดงเหตุผลในการเลือกวิธีทางสถิติ ไม่ให้ตอบเฉพาะตัวเลขจากโปรแกรม
3. การสรุป hypothesis test ต้องกล่าวถึง population และบริบทของโจทย์
4. อนุญาตให้ใช้ R ช่วยวิเคราะห์ แต่ต้องเขียนสมมติฐาน วิธีที่ใช้ ค่าจาก output และข้อสรุปลงในกระดาษคำตอบ
5. ถ้าใช้ Google Colab ให้รันสอง cell ต่อไปนี้ก่อน

Python cell:

```python
%load_ext rpy2.ipython
```

R cell:

```r
%%R
# แสดงตัวเลขเป็นทศนิยมแทนรูปแบบ e+ หรือ e-
options(scipen = 999, digits = 4)
```

---

# ส่วนที่ 1: ข้อสอบจำลอง

## ข้อ 1 เวลาจัดเตรียมคำสั่งซื้อ: One-sample confidence interval (6 คะแนน)

ศูนย์กระจายสินค้าแห่งหนึ่งต้องการประมาณเวลาเฉลี่ยที่พนักงานทั้งหมดใช้จัดเตรียมคำสั่งซื้อหนึ่งรายการ จึงสุ่มคำสั่งซื้อ 20 รายการและบันทึกเวลาเป็นนาทีดังนี้

```text
38 42 45 40 44 47 41 39 43 46
48 44 42 40 45 43 41 46 39 44
```

1.1 ระบุตัวแปรที่ศึกษา population, parameter และ statistic ที่ใช้ประมาณ parameter (1 คะแนน)

1.2 ตรวจสอบความเหมาะสมของ Normality assumption โดยใช้ Q–Q plot และ Shapiro–Wilk test พร้อมอธิบายว่าควรอ่านผลอย่างไร (2 คะแนน)

1.3 เลือกวิธีสร้าง confidence interval ที่เหมาะสม พร้อมเหตุผล (1 คะแนน)

1.4 สร้าง 90% confidence interval ของ population mean preparation time และตีความในบริบท (2 คะแนน)

---

## ข้อ 2 อาการไม่พึงประสงค์หลังฉีดวัคซีน: One-proportion confidence interval (4 คะแนน)

โรงพยาบาลติดตามผู้รับวัคซีนแบบใหม่ 240 คน พบว่า 18 คนมีอาการไม่พึงประสงค์ภายใน 7 วัน

2.1 หาค่าประมาณแบบจุดของ population proportion ที่มีอาการไม่พึงประสงค์ (1 คะแนน)

2.2 สร้าง 95% confidence interval ของ population proportion ด้วย `prop.test()` โดยไม่ใช้ continuity correction (2 คะแนน)

2.3 ตีความช่วงที่ได้เป็นข้อความสำหรับเขียนตอบในห้องสอบ (1 คะแนน)

---

## ข้อ 3 ต้นทุนของรถแทรกเตอร์สองระบบ: Independent two-sample hypothesis test (7 คะแนน)

นักพัฒนาการเกษตรต้องการตรวจสอบว่ารถแทรกเตอร์ระบบ FWAD มีต้นทุนการผลิตเฉลี่ยต่ำกว่าระบบ T4WD หรือไม่ จึงสุ่มรถจากแต่ละระบบอย่างอิสระและได้ต้นทุนต่อคันดังนี้

```text
FWAD: 210 198 205 215 202 207 199 204 211 206 203 208
T4WD: 220 214 218 225 217 222 216 219 224 221 215 223
```

ข้อมูลแต่ละกลุ่มวัดจากรถคนละคัน

3.1 ตรวจสอบ Normality ของแต่ละกลุ่ม และทดสอบสมมติฐานว่า population variances เท่ากันหรือไม่ (2 คะแนน)

3.2 เขียน $H_0$ และ $H_1$ โดยกำหนดให้ $\mu_F$ เป็น population mean cost ของ FWAD และ $\mu_T$ เป็น population mean cost ของ T4WD (1 คะแนน)

3.3 เลือก independent-samples t test ที่เหมาะสม รันการทดสอบ และรายงาน test statistic, degrees of freedom และ p-value (2 คะแนน)

3.4 สรุปผลที่ระดับนัยสำคัญ 0.05 ในภาษาของโจทย์ และอธิบายว่าทำไมจึงห้ามเขียนว่า “ยอมรับ $H_0$” (2 คะแนน)

---

## ข้อ 4 คะแนนก่อนและหลังอบรม: Paired hypothesis test (6 คะแนน)

บริษัทต้องการทราบว่าหลักสูตรอบรมทำให้คะแนนทักษะของพนักงานเพิ่มขึ้นหรือไม่ จึงวัดพนักงาน 10 คนเดิมก่อนและหลังอบรม

```text
คนที่:       1  2  3  4  5  6  7  8  9 10
ก่อนอบรม:   72 68 75 80 77 69 74 71 78 73
หลังอบรม:   74 71 79 85 83 76 76 75 83 79
```

4.1 อธิบายว่าเหตุใดข้อมูลนี้จึงเป็น paired samples ไม่ใช่ independent samples และระบุค่าที่ต้องตรวจ Normality (1 คะแนน)

4.2 กำหนด $d=$ หลังอบรม $-$ ก่อนอบรม แล้วเขียน $H_0$ และ $H_1$ (1 คะแนน)

4.3 รัน paired t test แบบ one-sided และรายงาน mean difference, test statistic, degrees of freedom และ p-value (2 คะแนน)

4.4 สรุปผลในบริบทที่ระดับนัยสำคัญ 0.05 (2 คะแนน)

---

## ข้อ 5 จำนวนวันแก้ไขข้อร้องเรียน: Jackknife และ Bootstrap (7 คะแนน)

ร้านค้าเก็บจำนวนวันที่ใช้แก้ไขข้อร้องเรียน 15 กรณี ได้ข้อมูลดังนี้

```text
2 3 4 4 5 5 6 7 8 9 10 12 15 22 35
```

5.1 ใช้กราฟและ Shapiro–Wilk test อธิบายรูปทรงของข้อมูล พร้อมบอกเหตุผลที่ classical t interval อาจต้องใช้ความระมัดระวัง (1 คะแนน)

5.2 หาค่าประมาณแบบจุดของ population mean resolution time (1 คะแนน)

5.3 ใช้ Jackknife ประมาณ bias และ standard error ของ sample mean พร้อมตีความ (2 คะแนน)

5.4 ใช้ 10,000 bootstrap resamples สร้าง 95% percentile bootstrap confidence interval ของ population mean (2 คะแนน)

5.5 เปรียบเทียบ classical t interval กับ bootstrap percentile interval และเสนอช่วงที่ควรรายงานสำหรับข้อมูลชุดนี้ พร้อมเหตุผล (1 คะแนน)

---

# ส่วนที่ 2: เฉลยละเอียดและแนวเขียนตอบ

## เฉลยข้อ 1 เวลาจัดเตรียมคำสั่งซื้อ

### 1.1 แปลโจทย์ก่อนใช้ R

- ตัวแปร: เวลาจัดเตรียมคำสั่งซื้อหนึ่งรายการ มีหน่วยเป็นนาที เป็น quantitative continuous variable
- Population: คำสั่งซื้อทั้งหมดในกระบวนการที่ศูนย์กระจายสินค้าต้องการศึกษา
- Parameter: population mean preparation time เขียนเป็น $\mu$
- Statistic: sample mean เขียนเป็น $\bar{x}$

ค่าจาก sample เป็นสิ่งที่คำนวณได้ ส่วน parameter เป็นค่าของ population ที่ไม่ทราบและต้องประมาณ

### 1.2–1.4 รัน R ก่อน แล้วจึงเขียนตอบ

```r
%%R
delivery_time_q1 <- c(
  38, 42, 45, 40, 44, 47, 41, 39, 43, 46,
  48, 44, 42, 40, 45, 43, 41, 46, 39, 44
)

# ตรวจรูปทรงและ outliers
boxplot(delivery_time_q1, horizontal = TRUE,
        main = "Preparation time")
qqnorm(delivery_time_q1)
qqline(delivery_time_q1, col = "red")
print(shapiro.test(delivery_time_q1))

# สร้าง one-sample t interval ระดับความเชื่อมั่น 90%
delivery_ci_q1 <- t.test(delivery_time_q1, conf.level = 0.90)
print(delivery_ci_q1)
```

### ต้องดูค่าใดจาก output

- Shapiro–Wilk p-value ประมาณ 0.7955
- Sample mean เท่ากับ 42.8500 นาที
- 90% confidence interval ประมาณ 41.7473 ถึง 43.9527 นาที

Shapiro p-value มากกว่า 0.05 หมายความว่า sample นี้ยังไม่มีหลักฐานชัดเจนว่าขัดกับ Normality ต้องดู Q–Q plot และ outliers ประกอบ ไม่ควรเขียนว่า test นี้ “พิสูจน์ว่าข้อมูลเป็น Normal”

Population SD ไม่ทราบ จึงใช้ one-sample t interval ไม่ใช้ z interval

โครงสร้างช่วงคือ

$$
\text{Estimate} \pm \text{Critical value}\times SE
$$

สำหรับข้อนี้

$$
\bar{x} \pm t_{0.95,19}\frac{s}{\sqrt{n}}
$$

โดย $\bar{x}=42.85$, $s=2.8521$, $n=20$ และ $SE=0.6377$

### ตัวอย่างคำตอบในห้องสอบ

> ตัวแปรที่ศึกษาคือเวลาจัดเตรียมคำสั่งซื้อหนึ่งรายการ และ parameter คือ population mean preparation time $\mu$ จาก Q–Q plot จุดอยู่ใกล้เส้นตรงและไม่พบความผิดปกติเด่นชัด ขณะที่ Shapiro–Wilk test ให้ p-value = 0.7955 ซึ่งมากกว่า 0.05 จึงยังไม่มีหลักฐานต่อต้าน Normality เนื่องจากไม่ทราบ population SD จึงใช้ one-sample t interval ได้ 90% confidence interval เท่ากับ 41.7473 ถึง 43.9527 นาที กล่าวคือ เรามั่นใจ 90% ว่าวิธีสร้างช่วงนี้ให้ช่วงที่ครอบคลุม population mean preparation time ซึ่งสำหรับข้อมูลนี้อยู่ระหว่างประมาณ 41.75 และ 43.95 นาที

---

## เฉลยข้อ 2 อาการไม่พึงประสงค์หลังฉีดวัคซีน

### 2.1 มองโครงสร้างข้อมูล

Outcome ของแต่ละคนมีสองสถานะ คือ มีอาการหรือไม่มีอาการ จึงสนใจ population proportion $p$ ไม่ใช่ population mean

ค่าประมาณแบบจุดคือ

$$
\hat{p}=\frac{x}{n}=\frac{18}{240}=0.0750
$$

หรือ 7.50%

### 2.2 รัน R

```r
%%R
adverse_cases_q2 <- 18
vaccinated_total_q2 <- 240

adverse_prop_q2 <- adverse_cases_q2 / vaccinated_total_q2
print(adverse_prop_q2)

adverse_ci_q2 <- prop.test(
  x = adverse_cases_q2,
  n = vaccinated_total_q2,
  conf.level = 0.95,
  correct = FALSE
)
print(adverse_ci_q2)
```

### ต้องดูค่าใดจาก output

- Sample proportion เท่ากับ 0.0750
- 95% confidence interval ประมาณ 0.0480 ถึง 0.1154

คำสั่ง `correct = FALSE` ทำให้ผลตรงกับ score interval ที่ไม่ใช้ continuity correction ผลจึงอาจต่างจาก Wald interval ที่คำนวณด้วย $\hat{p}\pm zSE$

### ตัวอย่างคำตอบในห้องสอบ

> จากผู้รับวัคซีน 240 คน พบอาการไม่พึงประสงค์ 18 คน จึงได้ sample proportion เท่ากับ 0.0750 หรือ 7.50% การใช้ `prop.test()` โดยไม่ใช้ continuity correction ให้ 95% confidence interval ของ population proportion ประมาณ 0.0480 ถึง 0.1154 ดังนั้น population proportion ของผู้รับวัคซีนที่มีอาการไม่พึงประสงค์คาดว่าอยู่ระหว่างประมาณ 4.80% และ 11.54%

ข้อควรระวัง: ช่วงนี้ประมาณ proportion ของคนที่มีอาการ ไม่ได้แปลว่าอาการ 95% จะอยู่ในช่วงดังกล่าว

---

## เฉลยข้อ 3 ต้นทุนของรถแทรกเตอร์สองระบบ

### 3.1 แปลโครงสร้างโจทย์

- Outcome: ต้นทุนต่อคัน เป็นข้อมูลตัวเลข
- Groups: FWAD และ T4WD เป็นรถคนละคัน จึงเป็น independent samples
- Parameter ที่เปรียบเทียบ: $\mu_F-\mu_T$
- ทิศทางที่โจทย์ถาม: FWAD ต่ำกว่า T4WD จึงเป็น lower-tailed test

### 3.2–3.3 รัน R

```r
%%R
cost_fwad_q3 <- c(
  210, 198, 205, 215, 202, 207,
  199, 204, 211, 206, 203, 208
)

cost_t4wd_q3 <- c(
  220, 214, 218, 225, 217, 222,
  216, 219, 224, 221, 215, 223
)

# ตรวจ Normality แยกแต่ละกลุ่ม
qqnorm(cost_fwad_q3); qqline(cost_fwad_q3, col = "red")
print(shapiro.test(cost_fwad_q3))

qqnorm(cost_t4wd_q3); qqline(cost_t4wd_q3, col = "red")
print(shapiro.test(cost_t4wd_q3))

# ตรวจ equal population variances
print(var.test(cost_fwad_q3, cost_t4wd_q3))

# เมื่อ assumptions รองรับ equal variances ใช้ pooled two-sample t test
cost_test_q3 <- t.test(
  cost_fwad_q3,
  cost_t4wd_q3,
  alternative = "less",
  var.equal = TRUE
)
print(cost_test_q3)
```

### สมมติฐาน

$$
H_0:\mu_F-\mu_T=0
$$

$$
H_1:\mu_F-\mu_T<0
$$

### ต้องดูค่าใดจาก output

- Shapiro p-value ของ FWAD ประมาณ 0.9976
- Shapiro p-value ของ T4WD ประมาณ 0.8757
- `var.test()` ให้ p-value ประมาณ 0.3105
- Sample means: FWAD = 205.6667 และ T4WD = 219.5000
- Mean difference FWAD minus T4WD = -13.8333
- Pooled t statistic = -7.8332
- Degrees of freedom = 22
- One-sided p-value ประมาณ 0.0000000418

Shapiro p-values และ variance-test p-value มากกว่า 0.05 จึงยังไม่มีหลักฐานต่อต้าน Normality หรือ equal population variances สำหรับข้อมูลนี้ เมื่อการออกแบบเป็น independent samples จึงใช้ pooled independent-samples t test ตามโจทย์ได้

ถ้าโจทย์ไม่ได้ให้สมมติ equal variances และหลักฐานไม่รองรับความเท่ากัน ให้ใช้ Welch test ซึ่งเป็นค่าเริ่มต้นของ `t.test(x, y)` แทน

### ตัวอย่างคำตอบในห้องสอบ

> กำหนด $H_0:\mu_F-\mu_T=0$ และ $H_1:\mu_F-\mu_T<0$ ข้อมูลมาจากรถคนละคันจึงเป็น independent samples ผลตรวจ Normality ของทั้งสองกลุ่มให้ p-value มากกว่า 0.05 และ F test ของ equal variances ให้ p-value = 0.3105 จึงยังไม่มีหลักฐานว่าความแปรปรวนประชากรต่างกัน และใช้ pooled two-sample t test ได้ ผลการทดสอบให้ $t=-7.8332$, $df=22$ และ p-value = 0.0000000418 ซึ่งน้อยกว่า 0.05 จึงปฏิเสธ $H_0$ มีหลักฐานทางสถิติว่าต้นทุนเฉลี่ยของรถระบบ FWAD ต่ำกว่าระบบ T4WD โดย sample means เท่ากับ 205.67 และ 219.50 ตามลำดับ

เราไม่เขียนว่า “ยอมรับ $H_0$” เมื่อ p-value มาก เพราะการไม่ปฏิเสธหมายถึงข้อมูลยังไม่แรงพอ ไม่ได้พิสูจน์ว่า $H_0$ จริง อย่างไรก็ตาม ข้อนี้ p-value เล็กมากจึงปฏิเสธ $H_0$

---

## เฉลยข้อ 4 คะแนนก่อนและหลังอบรม

### 4.1 เหตุใดจึงเป็น paired samples

คะแนนก่อนและหลังมาจากพนักงานคนเดิม ค่าทั้งสองจึงสัมพันธ์กัน หน่วยวิเคราะห์ที่ถูกต้องไม่ใช่คะแนนสองกลุ่มแยกกัน แต่เป็น difference ของพนักงานแต่ละคน

กำหนด

$$
d=\text{คะแนนหลังอบรม}-\text{คะแนนก่อนอบรม}
$$

สิ่งที่ต้องตรวจ Normality คือ differences $d$ ไม่ใช่คะแนนก่อนและหลังแยกกัน

### 4.2 สมมติฐาน

$$
H_0:\mu_d=0
$$

$$
H_1:\mu_d>0
$$

### 4.3 รัน R

```r
%%R
score_before_q4 <- c(72, 68, 75, 80, 77, 69, 74, 71, 78, 73)
score_after_q4  <- c(74, 71, 79, 85, 83, 76, 76, 75, 83, 79)

score_diff_q4 <- score_after_q4 - score_before_q4
print(score_diff_q4)

# ตรวจ Normality ของ differences
qqnorm(score_diff_q4)
qqline(score_diff_q4, col = "red")
print(shapiro.test(score_diff_q4))

# Paired t test: หลังอบรมมากกว่าก่อนอบรม
training_test_q4 <- t.test(
  score_after_q4,
  score_before_q4,
  paired = TRUE,
  alternative = "greater"
)
print(training_test_q4)

print(mean(score_diff_q4))
```

อีกวิธีที่ให้ผลเดียวกันคือทดสอบ differences โดยตรง

```r
%%R
print(t.test(score_diff_q4, mu = 0, alternative = "greater"))
```

### ต้องดูค่าใดจาก output

- Differences คือ 2, 3, 4, 5, 6, 7, 2, 4, 5, 6
- Shapiro p-value ของ differences ประมาณ 0.5906
- Mean difference เท่ากับ 4.4000 คะแนน
- t statistic = 8.1240
- Degrees of freedom = 9
- One-sided p-value ประมาณ 0.0000098
- One-sided 95% lower confidence bound ประมาณ 3.4072 คะแนน

### ตัวอย่างคำตอบในห้องสอบ

> คะแนนก่อนและหลังมาจากพนักงานคนเดิม จึงใช้ paired t test โดยวิเคราะห์ difference หลังลบก่อน กำหนด $H_0:\mu_d=0$ และ $H_1:\mu_d>0$ Q–Q plot ของ differences ไม่แสดงความผิดปกติเด่นชัด และ Shapiro–Wilk test ให้ p-value = 0.5906 จึงยังไม่มีหลักฐานต่อต้าน Normality ผลทดสอบให้ mean difference = 4.4000 คะแนน, $t=8.1240$, $df=9$ และ p-value = 0.0000098 ซึ่งน้อยกว่า 0.05 จึงปฏิเสธ $H_0$ มีหลักฐานทางสถิติว่าหลักสูตรอบรมทำให้ population mean skill score เพิ่มขึ้น

ข้อผิดพลาดที่พบบ่อยคือใช้ independent t test เพราะเห็นข้อมูลสองคอลัมน์ วิธีนั้นทิ้งข้อมูลการจับคู่และตอบโจทย์ผิดโครงสร้าง

---

## เฉลยข้อ 5 จำนวนวันแก้ไขข้อร้องเรียน

### 5.1 เหตุใดจึงพิจารณา resampling

ข้อมูลมีค่าจำนวนมากกระจุกอยู่ช่วงต่ำ แต่มีค่ามากอย่าง 22 และ 35 ทำให้เกิดหางขวายาว Sample size มีเพียง 15 จึงไม่ควรอาศัย Central Limit Theorem โดยอัตโนมัติ Classical t interval ยังรันได้ แต่ Normality assumption ของข้อมูลขนาดเล็กไม่เหมาะสม จึงควรเปรียบเทียบกับ bootstrap interval

### 5.2–5.4 รัน R

```r
%%R
resolution_days_q5 <- c(2, 3, 4, 4, 5, 5, 6, 7, 8, 9, 10, 12, 15, 22, 35)

# ตรวจข้อมูล
boxplot(resolution_days_q5, horizontal = TRUE,
        main = "Complaint resolution time")
hist(resolution_days_q5,
     main = "Complaint resolution time",
     xlab = "Days")
qqnorm(resolution_days_q5)
qqline(resolution_days_q5, col = "red")
print(shapiro.test(resolution_days_q5))

# Point estimate และ classical t interval
print(mean(resolution_days_q5))
print(t.test(resolution_days_q5)$conf.int)
```

Jackknife ของ sample mean:

```r
%%R
resolution_n_q5 <- length(resolution_days_q5)
resolution_mean_q5 <- mean(resolution_days_q5)

# Leave-one-out estimates: รอบที่ i ตัด observation ที่ i ออก
jack_means_q5 <- sapply(
  seq_along(resolution_days_q5),
  function(i) mean(resolution_days_q5[-i])
)

jack_average_q5 <- mean(jack_means_q5)
jack_bias_q5 <- (resolution_n_q5 - 1) *
  (jack_average_q5 - resolution_mean_q5)
jack_se_q5 <- sqrt(
  (resolution_n_q5 - 1) / resolution_n_q5 *
  sum((jack_means_q5 - jack_average_q5)^2)
)

print(c(
  estimate = resolution_mean_q5,
  jackknife_bias = jack_bias_q5,
  jackknife_se = jack_se_q5
))
```

Bootstrap percentile interval:

```r
%%R
set.seed(6001)

boot_means_q5 <- replicate(
  10000,
  mean(sample(
    resolution_days_q5,
    size = length(resolution_days_q5),
    replace = TRUE
  ))
)

print(c(
  bootstrap_mean = mean(boot_means_q5),
  bootstrap_bias = mean(boot_means_q5) - mean(resolution_days_q5),
  bootstrap_se = sd(boot_means_q5)
))

print(quantile(boot_means_q5, c(0.025, 0.975)))
```

### ต้องดูค่าใดจาก output

- Sample mean เท่ากับ 9.8000 วัน
- Sample median เท่ากับ 7 วัน ซึ่งต่ำกว่า mean และสอดคล้องกับ right skewness
- Shapiro p-value ประมาณ 0.0016 จึงมีหลักฐานว่ารูปทรงไม่สอดคล้องกับ Normality
- Classical 95% t interval ประมาณ 4.9759 ถึง 14.6241 วัน
- Jackknife bias ของ sample mean เท่ากับ 0 หรือใกล้ 0 จากความคลาดเคลื่อนของคอมพิวเตอร์
- Jackknife standard error ประมาณ 2.2492 วัน
- Bootstrap standard error จะอยู่ประมาณ 2.17 วัน
- 95% percentile bootstrap interval จะอยู่ประมาณ 6.1 ถึง 14.5 วัน

ค่าปลายช่วง bootstrap อาจต่างกันเล็กน้อยตามจำนวน resamples และ random seed แต่ข้อสรุปไม่ควรเปลี่ยน

### ความหมายของ Jackknife

Jackknife สร้าง sample ใหม่ $n$ ชุดโดยตัด observation ออกครั้งละหนึ่งค่า แล้วดูว่า estimate เปลี่ยนมากเพียงใด สำหรับ sample mean ค่า jackknife bias เป็นศูนย์ เพราะ mean เป็น estimator แบบ linear แต่ jackknife SE ยังมีความหมาย เพราะบอกความไม่แน่นอนของ mean จาก sample นี้

### ความหมายของ Bootstrap

Bootstrap สุ่ม observations จาก sample เดิมแบบใส่คืนให้มีขนาดเท่าเดิม แล้วคำนวณ mean ซ้ำ 10,000 ครั้ง การกระจายของ bootstrap means ใช้ประมาณ sampling distribution ของ sample mean ส่วน percentile interval ใช้ quantile ที่ 2.5% และ 97.5% เป็นขอบช่วง

### ตัวอย่างคำตอบในห้องสอบ

> ข้อมูลจำนวนวันมีลักษณะเบ้ขวาและมีค่าสูง 22 กับ 35 วัน โดย Shapiro–Wilk test ให้ p-value ประมาณ 0.0016 จึงมีหลักฐานต่อต้าน Normality เมื่อ sample size มีเพียง 15 การใช้ classical t interval ต้องระมัดระวัง Sample mean เท่ากับ 9.8000 วัน Jackknife ให้ estimated bias ใกล้ 0 และ standard error ประมาณ 2.2492 วัน ขณะที่ 10,000 bootstrap resamples ให้ percentile 95% confidence interval ประมาณ 6.1 ถึง 14.5 วัน สำหรับข้อมูลขนาดเล็กที่เบ้ขวานี้ ข้าพเจ้าจะรายงาน bootstrap percentile interval พร้อมอธิบายวิธี resampling เพราะช่วงไม่บังคับสมมาตรรอบ sample mean และสะท้อนรูปทรงของข้อมูลได้ดีกว่า classical t interval

ข้อควรระวัง: Bootstrap ไม่แก้ปัญหา sample ที่สุ่มอย่างมีอคติ หาก sample ไม่เป็นตัวแทน population การ resample ข้อมูลเดิมก็ยังคงอคตินั้นไว้

---

# ส่วนที่ 3: แผ่นสรุปการเลือกวิธีจากข้อสอบชุดนี้

| สัญญาณในโจทย์ | โครงสร้างข้อมูล | วิธีหลักใน R | ค่าที่ต้องอ่าน |
|---|---|---|---|
| ตัวเลขหนึ่ง sample ต้องการช่วงของ mean | One numerical sample | `t.test(x, conf.level = ...)` | mean และ confidence interval |
| ผลลัพธ์สองสถานะ ต้องการช่วงของ proportion | One binary sample | `prop.test(x, n, correct = FALSE)` | sample estimate และ confidence interval |
| ตัวเลขสองกลุ่ม คนละหน่วยทดลอง | Independent samples | `t.test(x, y)` หรือ `t.test(x, y, var.equal = TRUE)` | means, t, df, p-value, CI |
| คนเดิมก่อน–หลัง หรือคู่ที่จับกัน | Paired samples | `t.test(after, before, paired = TRUE)` | mean difference, t, df, p-value |
| ต้องการ SE, bias หรือ CI จาก resampling | One sample, statistic ใด ๆ | Jackknife หรือ Bootstrap | estimate, bias, SE, percentile limits |

จำหลักนี้ก่อนจำ syntax:

1. ถามว่า parameter คืออะไร: mean, proportion หรือ difference
2. ถามว่าต้องการ estimate หรือ test
3. ถ้ามีสองชุด ให้ถามว่า independent หรือ paired
4. กำหนดทิศทาง difference และ alternative ก่อนรัน R
5. ตรวจ assumptions ที่ตรงกับวิธี
6. อ่านเฉพาะค่าที่ตอบโจทย์ แล้วเขียน conclusion พร้อมหน่วยและ population

---

# ส่วนที่ 4: Checklist การเขียนคำตอบ Hypothesis Test

ใช้โครงนี้กับข้อ 3 และข้อ 4 ได้โดยเปลี่ยนบริบท

1. **Parameter:** ระบุสิ่งที่ $\mu$, $p$ หรือ difference หมายถึง
2. **Hypotheses:** เขียน $H_0$ และ $H_1$ ให้ทิศทางตรงกับคำถาม
3. **Method:** ระบุชื่อ test และเหตุผลว่า one-sample, independent หรือ paired
4. **Assumptions:** กล่าวถึง random sampling, independence และผลตรวจรูปทรงที่เกี่ยวข้อง
5. **Evidence:** รายงาน test statistic, df และ p-value
6. **Decision:** เปรียบเทียบ p-value กับ $\alpha$
7. **Context:** สรุปว่ามีหรือไม่มีหลักฐานเกี่ยวกับ population ตามที่โจทย์ถาม

ประโยคต้นแบบ:

> เนื่องจาก p-value = ... [น้อยกว่า/มากกว่า] $\alpha=0.05$ จึง [ปฏิเสธ/ไม่ปฏิเสธ] $H_0$ ข้อมูลชุดนี้ [มี/ยังไม่มี] หลักฐานทางสถิติเพียงพอว่า ...

คำว่า “ยังไม่มีหลักฐานเพียงพอ” ไม่เท่ากับ “พิสูจน์ว่าไม่แตกต่าง”

---

# ส่วนที่ 5: วิธีใช้ Mock Exam ให้คุ้มก่อนสอบ

1. รอบแรกทำเฉพาะส่วนข้อสอบโดยจับเวลา 150 นาที
2. เหลือ 30 นาทีตรวจว่าแต่ละข้อมี parameter, method, output และ conclusion ครบหรือไม่
3. เปิดเฉลยแล้วทำเครื่องหมายข้อผิดพลาดตามประเภท: แปลโจทย์ผิด, เลือก test ผิด, syntax ผิด, อ่าน output ผิด หรือเขียน conclusion ไม่ครบ
4. รัน code ทุก cell ใน notebook เดียว ชื่อตัวแปรในเอกสารนี้ไม่ซ้ำกันระหว่างข้อ
5. ทำซ้ำเฉพาะข้อที่พลาดโดยไม่เปิดเฉลย และเขียนคำตอบด้วยภาษาของตนเอง

เอกสารอ้างอิงภายในรายวิชา: Lecture 01 Introduction, Lecture 02 Interval Estimation, Lecture 03 Jackknife and Bootstrap, Lecture 04 Hypothesis Testing, Lab 01–04 พร้อมเฉลย และแนวข้อสอบเก่าที่ให้ตรวจ Normality เลือกวิธี ทดสอบ assumptions วิเคราะห์ด้วยโปรแกรม และสรุปผลในบริบท
