# DADS6001 Midterm: ชีทวิธีรัน R และเขียนตอบ

ชีทนี้ใช้ท่องรูปแบบการตอบก่อนเข้าห้องสอบ ข้อความใน `[ ]` คือส่วนที่ต้องเปลี่ยนตามโจทย์ โดยในวงเล็บใส่ตัวเลขและคำตอบตัวอย่างจริงไว้แล้ว เพื่อให้เห็นว่าประโยคสมบูรณ์ควรเป็นอย่างไร

## 0. Code ตั้งต้นใน Google Colab

Python cell:

```python
%load_ext rpy2.ipython
```

R cell:

```r
%%R
options(scipen = 999, digits = 4)
```

ทุก R cell ถัดไปต้องขึ้นต้นด้วย `%%R`

---

# ส่วนที่ 1: ตรวจข้อมูลก่อนเลือกวิธี

## 1. ตรวจ Normality ของข้อมูลหนึ่งกลุ่ม

**ใช้เมื่อ:** จะวิเคราะห์ mean ของ sample ขนาดเล็กด้วย t method

```r
%%R
boxplot(x, horizontal = TRUE)
qqnorm(x)
qqline(x, col = 'red')
shapiro.test(x)
```

**ดูอะไร:**

- Boxplot: มี outlier รุนแรงหรือไม่
- Q–Q plot: จุดโดยรวมใกล้เส้นตรงหรือไม่
- Shapiro–Wilk: ดู p-value

**เขียนตอบเมื่อไม่พบปัญหาชัดเจน:**

> จาก boxplot `[ไม่พบ outlier รุนแรง]` และ Q–Q plot `[จุดโดยรวมอยู่ใกล้เส้นตรง]` ผล Shapiro–Wilk test ให้ `[p-value = 0.5085]` ซึ่งมากกว่า 0.05 จึงยังไม่มีหลักฐานว่าข้อมูลขัดกับ Normality assumption ดังนั้นสามารถใช้ `[one-sample t method]` ได้

**เขียนตอบเมื่อข้อมูลไม่ Normal:**

> จาก boxplot `[พบค่าสูงผิดปกติที่ 35 วัน]` และ Q–Q plot `[จุดบริเวณหางขวาเบี่ยงออกจากเส้น]` ผล Shapiro–Wilk test ให้ `[p-value = 0.0016]` ซึ่งน้อยกว่า 0.05 จึงมีหลักฐานว่าข้อมูลไม่สอดคล้องกับ Normality เมื่อ sample มีขนาดเพียง `[15]` การใช้ classical t method ต้องระมัดระวัง และควรพิจารณา `[Bootstrap]`

อย่าเขียนว่า “ข้อมูลเป็น Normal เพราะ p-value > 0.05” ให้เขียนว่า “ยังไม่มีหลักฐานต่อต้าน Normality”

## 2. ตรวจ Normality ของสองกลุ่มอิสระ

```r
%%R
qqnorm(group1); qqline(group1, col = 'red')
shapiro.test(group1)

qqnorm(group2); qqline(group2, col = 'red')
shapiro.test(group2)
```

**เขียนตอบ:**

> Q–Q plots ของทั้งสองกลุ่ม `[ไม่แสดงความผิดปกติเด่นชัด]` และ Shapiro–Wilk tests ให้ `[p-value ของกลุ่ม 1 = 0.8597]` และ `[p-value ของกลุ่ม 2 = 0.8082]` ซึ่งมากกว่า 0.05 ทั้งคู่ จึงยังไม่มีหลักฐานต่อต้าน Normality ของแต่ละ population

## 3. ตรวจ Normality ของข้อมูลจับคู่

ต้องตรวจ **differences** ไม่ใช่ตรวจก่อนและหลังแยกกัน

```r
%%R
d <- after - before
qqnorm(d)
qqline(d, col = 'red')
shapiro.test(d)
```

**เขียนตอบ:**

> เนื่องจากเป็นข้อมูลคนเดิมก่อนและหลัง จึงตรวจ Normality ของ difference `[หลังลบก่อน]` ผล Q–Q plot `[จุดโดยรวมอยู่ใกล้เส้นตรง]` และ Shapiro–Wilk test ให้ `[p-value = 0.3889]` ซึ่งมากกว่า 0.05 จึงยังไม่มีหลักฐานต่อต้าน Normality ของ differences และสามารถใช้ paired t method ได้

---

# ส่วนที่ 2: Confidence Interval

## 4. One-sample confidence interval ของ population mean

**โจทย์ต้องการ:** ประมาณค่าเฉลี่ยของ population จากข้อมูลตัวเลขหนึ่ง sample และไม่ทราบ population SD

```r
%%R
t.test(x, conf.level = 0.95)
```

**ดูอะไร:** `mean of x` และ `95 percent confidence interval`

**เขียนตอบ:**

> เนื่องจาก outcome คือ `[จำนวนเงินค่าอาหารกลางวัน]` ซึ่งเป็นข้อมูลตัวเลขหนึ่ง sample และไม่ทราบ population SD จึงใช้ one-sample t interval Sample mean เท่ากับ `[7.0933 ดอลลาร์]` และ 95% confidence interval เท่ากับ `[6.3147 ถึง 7.8720 ดอลลาร์]` กล่าวคือ เรามั่นใจ 95% ว่าวิธีสร้างช่วงนี้ให้ช่วงที่ครอบคลุม `[population mean ค่าอาหารกลางวัน]` ซึ่งจากข้อมูลนี้อยู่ระหว่าง `[6.3147 และ 7.8720 ดอลลาร์]`

ไม่เขียนว่า “ข้อมูล 95% อยู่ในช่วง” เพราะ CI กล่าวถึง population parameter ไม่ใช่ observations

## 5. One-sample z interval ของ population mean

**ใช้เมื่อ:** โจทย์ให้ population SD หรือ population variance มาโดยตรง

```r
%%R
xbar <- mean(x)
n <- length(x)
sigma <- 12
xbar + c(-1, 1) * qnorm(0.975) * sigma / sqrt(n)
```

**เขียนตอบ:**

> โจทย์กำหนด population SD เท่ากับ `[12 หน่วย]` จึงใช้ z interval แทน t interval Sample mean เท่ากับ `[102.0000 หน่วย]` และ 95% confidence interval เท่ากับ `[97.2961 ถึง 106.7039 หน่วย]` ดังนั้น population mean `[ค่าที่โจทย์ศึกษา]` คาดว่าอยู่ในช่วงดังกล่าว

## 6. One-proportion confidence interval

**โจทย์ต้องการ:** ประมาณสัดส่วนของ population จาก outcome สองสถานะ เช่น ป่วย/ไม่ป่วย หรือสำเร็จ/ไม่สำเร็จ

```r
%%R
prop.test(success, total, conf.level = 0.95, correct = FALSE)
```

**ดูอะไร:** `sample estimates` และ `confidence interval`

**เขียนตอบ:**

> จาก `[ผู้รับวัคซีน 240 คน]` พบ `[ผู้มีอาการไม่พึงประสงค์ 18 คน]` จึงได้ sample proportion เท่ากับ `[0.0750 หรือ 7.50%]` ผล `prop.test()` ให้ 95% confidence interval เท่ากับ `[0.0480 ถึง 0.1154]` ดังนั้น population proportion ของ `[ผู้รับวัคซีนที่มีอาการไม่พึงประสงค์]` คาดว่าอยู่ระหว่าง `[4.80% และ 11.54%]`

## 7. Independent means CI แบบ Welch

**ใช้เมื่อ:** ข้อมูลตัวเลขสองกลุ่มมาจากคนละหน่วยทดลอง และไม่สมมติว่า population variances เท่ากัน

```r
%%R
t.test(group1, group2, conf.level = 0.95)
```

`t.test()` ใช้ Welch เป็นค่าเริ่มต้น และช่วงที่รายงานคือ `mean(group1) - mean(group2)`

**เขียนตอบ:**

> ข้อมูล `[เวลารอของโรงพยาบาล A และ B]` มาจากผู้ป่วยคนละกลุ่ม จึงเป็น independent samples และไม่ได้สมมติว่า population variances เท่ากัน จึงใช้ Welch two-sample t interval ค่าเฉลี่ยตัวอย่างเท่ากับ `[18.4000 นาทีสำหรับ A]` และ `[25.0000 นาทีสำหรับ B]` โดยประมาณผลต่างเป็น `[A-B = -6.6000 นาที]` และ 95% confidence interval ของ $\mu_A-\mu_B$ เท่ากับ `[-8.9000 ถึง -4.3000 นาที]` เนื่องจากทั้งช่วงต่ำกว่า 0 จึงบ่งชี้ว่า population mean waiting time ของ A ต่ำกว่า B

## 8. Independent means CI แบบ pooled variance

**ใช้เมื่อ:** ข้อมูลสองกลุ่มเป็นอิสระ และโจทย์กำหนดหรือ assumptions รองรับว่า population variances เท่ากัน

```r
%%R
t.test(group1, group2, var.equal = TRUE, conf.level = 0.95)
```

**เขียนตอบ:**

> ข้อมูล `[เวลาอ่านหนังสือของนักศึกษาที่วางแผนและไม่วางแผนเรียนต่อ]` เป็น independent samples และใช้สมมติฐาน equal population variances จึงใช้ pooled two-sample t interval Sample means เท่ากับ `[11.6667 และ 9.1000 ชั่วโมง]` และ 95% confidence interval ของ $\mu_1-\mu_2$ เท่ากับ `[-3.1103 ถึง 8.2436 ชั่วโมง]` เนื่องจากช่วงครอบคลุม 0 ข้อมูลจึงยังไม่แสดงความแตกต่างของ population means อย่างชัดเจนที่ระดับ 0.05

## 9. Paired confidence interval ของ mean difference

**ใช้เมื่อ:** คนเดิมก่อน–หลัง หรือ observations จับคู่กัน

```r
%%R
t.test(after, before, paired = TRUE, conf.level = 0.95)
```

R คำนวณ difference เป็น `after - before` เพราะใส่ `after` ก่อน

**เขียนตอบ:**

> ข้อมูลก่อนและหลังมาจาก `[ผู้ป่วยคนเดิม]` จึงใช้ paired t interval โดยกำหนด difference เป็น `[หลังลบก่อน]` Mean difference เท่ากับ `[2.5586 กิโลกรัม]` และ 95% confidence interval ของ population mean difference เท่ากับ `[0.4355 ถึง 4.6817 กิโลกรัม]` เนื่องจากทั้งช่วงมากกว่า 0 จึงบ่งชี้ว่า population mean หลังการรักษาสูงกว่าก่อนการรักษา

ถ้าต้องการทิศทาง “ก่อน−หลัง” ให้สลับลำดับ argument หรือสร้าง `d <- before - after` ให้ชัดเจน

## 10. Two-proportion confidence interval

**ใช้เมื่อ:** เปรียบเทียบสัดส่วนของสอง population ที่เป็นอิสระ

```r
%%R
prop.test(
  x = c(success1, success2),
  n = c(total1, total2),
  conf.level = 0.95,
  correct = FALSE
)
```

R รายงานผลต่างตามลำดับ `p1 - p2`

**เขียนตอบ:**

> Sample proportions ของ `[นักศึกษา non-biological sciences]` และ `[นักศึกษา biological sciences]` เท่ากับ `[0.5426]` และ `[0.6138]` ตามลำดับ ผลต่างที่ประมาณคือ `[p_1-p_2=-0.0713]` และ 95% confidence interval เท่ากับ `[-0.1271 ถึง -0.0154]` เนื่องจากทั้งช่วงต่ำกว่า 0 จึงบ่งชี้ว่า population proportion ของกลุ่มแรกต่ำกว่ากลุ่มที่สอง

## 11. Confidence interval ของ population variance

**ใช้เมื่อ:** ต้องการประมาณ variance ของ population และข้อมูลมาจาก Normal population

```r
%%R
n <- length(x)
(n - 1) * var(x) / qchisq(c(0.975, 0.025), df = n - 1)
```

**เขียนตอบ:**

> ภายใต้สมมติฐานว่า `[แรงที่ใช้ทำลายฉนวน]` มาจาก Normal population ค่า sample variance เท่ากับ `[8019.3520 ปอนด์กำลังสอง]` และ 95% confidence interval ของ population variance เท่ากับ `[5086.3860 ถึง 14492.4390 ปอนด์กำลังสอง]`

---

# ส่วนที่ 3: Hypothesis Testing

## 12. ประโยคกลางที่ใช้กับ hypothesis test ทุกแบบ

เขียนตามลำดับนี้:

1. กำหนด parameter และ hypotheses
2. บอกชื่อ test และ assumptions
3. รายงาน estimate, test statistic, df ถ้ามี และ p-value
4. เปรียบเทียบ p-value กับ $\alpha$
5. สรุปเป็นภาษาของ population ในบริบทโจทย์

**เมื่อปฏิเสธ $H_0$:**

> เนื่องจาก `[p-value = 0.0147]` น้อยกว่า `[α = 0.05]` จึงปฏิเสธ $H_0$ ข้อมูลมีหลักฐานทางสถิติเพียงพอว่า `[population proportion ของสองกลุ่มแตกต่างกัน]`

**เมื่อไม่ปฏิเสธ $H_0$:**

> เนื่องจาก `[p-value = 0.0569]` มากกว่า `[α = 0.05]` จึงไม่ปฏิเสธ $H_0$ ข้อมูลยังไม่มีหลักฐานทางสถิติเพียงพอว่า `[population mean waiting time ต่ำกว่า 5 นาที]`

อย่าเขียนว่า “ยอมรับ $H_0$” หรือ “สองกลุ่มเท่ากัน” เพราะการไม่ปฏิเสธแปลเพียงว่าหลักฐานยังไม่เพียงพอ

## 13. เลือก `alternative` ให้ตรงคำถาม

| คำถาม | $H_1$ | R |
|---|---|---|
| แตกต่างหรือไม่ | parameter $\ne$ ค่าที่กำหนด | `alternative = 'two.sided'` |
| มากกว่าหรือไม่ | parameter $>$ ค่าที่กำหนด | `alternative = 'greater'` |
| น้อยกว่าหรือไม่ | parameter $<$ ค่าที่กำหนด | `alternative = 'less'` |

ทิศทางต้องมาจากคำถามก่อนเห็นข้อมูล ห้ามเปลี่ยนเป็น one-sided หลังเห็น sample mean

## 14. One-sample t test ของ population mean

**โจทย์ต้องการ:** ทดสอบ mean ของ population หนึ่งกลุ่มเทียบค่ามาตรฐาน $\mu_0$

```r
%%R
t.test(x, mu = 5, alternative = 'less')
```

**สมมติฐานตัวอย่าง:**

$$
H_0:\mu=5
$$

$$
H_1:\mu<5
$$

**เขียนตอบ:**

> กำหนดให้ $\mu$ เป็น population mean waiting time สมมติฐานคือ $H_0:\mu=5$ และ $H_1:\mu<5$ เนื่องจากเป็นข้อมูลตัวเลขหนึ่ง sample ไม่ทราบ population SD และ `[ยังไม่มีหลักฐานต่อต้าน Normality]` จึงใช้ one-sample t test ผลได้ sample mean `[4.2867 นาที]`, `[t=-1.6867]`, `[df=14]` และ `[p-value=0.0569]` เนื่องจาก p-value มากกว่า 0.05 จึงไม่ปฏิเสธ $H_0$ ข้อมูลยังไม่มีหลักฐานเพียงพอว่า population mean waiting time ต่ำกว่า 5 นาที

เปลี่ยนเฉพาะ `alternative`:

```r
%%R
t.test(x, mu = 5, alternative = 'two.sided')
t.test(x, mu = 5, alternative = 'greater')
t.test(x, mu = 5, alternative = 'less')
```

## 15. Independent two-sample t test แบบ Welch

**ใช้เมื่อ:** สองกลุ่มเป็นอิสระ และไม่สมมติ equal population variances

```r
%%R
t.test(group1, group2, alternative = 'two.sided')
```

สมมติฐานของ R อ้างอิงผลต่าง `group1 - group2`

**เขียนตอบ:**

> กำหนดให้ $\mu_1$ และ $\mu_2$ เป็น population means ของ `[กลุ่ม A และกลุ่ม B]` สมมติฐานคือ $H_0:\mu_1-\mu_2=0$ และ $H_1:\mu_1-\mu_2\ne0$ ข้อมูลมาจากคนละกลุ่มและไม่ได้สมมติ equal variances จึงใช้ Welch two-sample t test ผลได้ sample means `[18.4000 และ 25.0000]`, `[t=-5.3200]`, `[df=17.8400]` และ `[p-value=0.00005]` เนื่องจาก p-value น้อยกว่า 0.05 จึงปฏิเสธ $H_0$ มีหลักฐานว่า population means ของ `[กลุ่ม A และ B]` แตกต่างกัน

## 16. Independent two-sample t test แบบ pooled variance

ตรวจ equal variances ก่อนเมื่อโจทย์ต้องการ:

```r
%%R
var.test(group1, group2)
t.test(group1, group2, var.equal = TRUE, alternative = 'greater')
```

**เขียนตอบ:**

> ข้อมูล `[ต้นทุนระบบ FWAD และ T4WD]` มาจากรถคนละคันจึงเป็น independent samples ผล F test ให้ `[p-value=0.3105]` ซึ่งมากกว่า 0.05 จึงยังไม่มีหลักฐานว่า population variances ต่างกัน และใช้ pooled two-sample t test ได้ กำหนด $H_0:\mu_F-\mu_T=0$ และ $H_1:\mu_F-\mu_T<0$ ผลทดสอบให้ sample means `[205.6667 และ 219.5000]`, `[t=-7.8332]`, `[df=22]` และ `[p-value=0.0000000418]` จึงปฏิเสธ $H_0$ มีหลักฐานทางสถิติว่า population mean cost ของ FWAD ต่ำกว่า T4WD

ใน code ของตัวอย่างนี้ต้องใช้ `alternative = 'less'` เพราะใส่ FWAD เป็น argument แรกและถามว่า FWAD ต่ำกว่า T4WD

## 17. Paired t test

**ใช้เมื่อ:** คนเดิมก่อน–หลัง หรือข้อมูลจับคู่กัน

```r
%%R
t.test(after, before, paired = TRUE, alternative = 'greater')
```

R ทดสอบ population mean difference `after - before`

**สมมติฐาน:**

$$
H_0:\mu_d=0
$$

$$
H_1:\mu_d>0
$$

**เขียนตอบ:**

> คะแนนก่อนและหลังมาจาก `[พนักงานคนเดิม]` จึงเป็น paired samples โดยกำหนด $d=$ `[หลังลบก่อน]` สมมติฐานคือ $H_0:\mu_d=0$ และ $H_1:\mu_d>0$ ผลตรวจ differences `[ยังไม่มีหลักฐานต่อต้าน Normality]` จึงใช้ paired t test ผลได้ mean difference `[4.4000 คะแนน]`, `[t=8.1240]`, `[df=9]` และ `[p-value=0.0000098]` ซึ่งน้อยกว่า 0.05 จึงปฏิเสธ $H_0$ มีหลักฐานว่าหลักสูตรอบรมทำให้ population mean skill score เพิ่มขึ้น

## 18. One-proportion hypothesis test

**ใช้เมื่อ:** ทดสอบ population proportion หนึ่งกลุ่มกับค่าที่กำหนด $p_0$

```r
%%R
prop.test(
  success,
  total,
  p = 0.80,
  alternative = 'greater',
  correct = FALSE
)
```

**สมมติฐานตัวอย่าง:**

$$
H_0:p=0.80
$$

$$
H_1:p>0.80
$$

**เขียนตอบ:**

> กำหนดให้ $p$ เป็น population proportion ของ `[นักศึกษาที่เห็นด้วยกับการฉีดวัคซีนเข็มที่ 4]` สมมติฐานคือ $H_0:p=0.80$ และ $H_1:p>0.80$ จาก sample ได้ `[170 จาก 200 คน หรือ sample proportion = 0.8500]` ผล one-proportion test ให้ `[p-value=0.0385]` ซึ่งน้อยกว่า 0.05 จึงปฏิเสธ $H_0$ มีหลักฐานว่า population proportion ของนักศึกษาที่เห็นด้วยมากกว่า 0.80

## 19. Two-proportion hypothesis test

**ใช้เมื่อ:** ทดสอบสัดส่วนของสอง population อิสระ

```r
%%R
prop.test(
  x = c(success1, success2),
  n = c(total1, total2),
  alternative = 'two.sided',
  correct = FALSE
)
```

ทิศทางของ alternative อ้างอิง `p1 - p2`

**เขียนตอบ:**

> กำหนดให้ $p_1$ และ $p_2$ เป็น population proportions ของ `[นักศึกษา non-biological และ biological sciences]` สมมติฐานคือ $H_0:p_1-p_2=0$ และ $H_1:p_1-p_2\ne0$ Sample proportions เท่ากับ `[0.5426 และ 0.6138]` ผล two-proportion test ให้ `[X-squared=5.9483]`, `[df=1]` และ `[p-value=0.0147]` ซึ่งน้อยกว่า 0.05 จึงปฏิเสธ $H_0$ มีหลักฐานว่า population proportions ของสองสาขาแตกต่างกัน

## 20. F test สำหรับ equality of variances

**ใช้เมื่อ:** ต้องการทดสอบว่า population variances ของสองกลุ่มเท่ากันหรือไม่ และแต่ละ population ใกล้ Normal

```r
%%R
var.test(group1, group2)
```

**สมมติฐาน:**

$$
H_0:\sigma_1^2=\sigma_2^2
$$

$$
H_1:\sigma_1^2\ne\sigma_2^2
$$

**เขียนตอบเมื่อ p-value มากกว่า 0.05:**

> กำหนด $H_0:\sigma_1^2=\sigma_2^2$ และ $H_1:\sigma_1^2\ne\sigma_2^2$ ผล F test ให้ `[F=1.8788]` และ `[p-value=0.3105]` ซึ่งมากกว่า 0.05 จึงไม่ปฏิเสธ $H_0$ ข้อมูลยังไม่มีหลักฐานว่า population variances ของสองกลุ่มแตกต่างกัน จึงสามารถใช้ pooled-variance t method ได้ หาก assumptions อื่นเหมาะสม

**เขียนตอบเมื่อ p-value น้อยกว่า 0.05:**

> ผล F test ให้ `[p-value=0.0120]` ซึ่งน้อยกว่า 0.05 จึงปฏิเสธ $H_0$ มีหลักฐานว่า population variances ต่างกัน ดังนั้นไม่ควรใช้ pooled-variance t method และควรใช้ Welch t method

---

# ส่วนที่ 4: Jackknife และ Bootstrap

## 21. Jackknife เพื่อประมาณ bias และ standard error

**ใช้เมื่อ:** โจทย์ให้ประเมินความไวของ statistic เมื่อเอาข้อมูลออกทีละหนึ่ง observation

```r
%%R
n <- length(x)
theta_hat <- mean(x)

jack_values <- sapply(
  seq_along(x),
  function(i) mean(x[-i])
)

jack_mean <- mean(jack_values)
jack_bias <- (n - 1) * (jack_mean - theta_hat)
jack_se <- sqrt((n - 1) / n * sum((jack_values - jack_mean)^2))

print(c(estimate = theta_hat, bias = jack_bias, se = jack_se))
```

**เขียนตอบ:**

> Sample mean ของ `[fuel efficiency]` เท่ากับ `[22.7000 mpg]` Jackknife สร้าง leave-one-out samples จำนวน `[10 ชุด]` และให้ estimated bias เท่ากับ `[0.0000]` กับ standard error เท่ากับ `[1.3421 mpg]` ดังนั้น sample mean ไม่มี jackknife bias ที่ตรวจพบในข้อมูลนี้ และค่าประมาณ mean มี sampling uncertainty ประมาณ `[1.3421 mpg]`

Bias ใกล้ 0 ไม่ได้แปลว่า estimate ไม่มี uncertainty ต้องอ่าน SE ด้วย

## 22. Bootstrap standard error และ percentile confidence interval

```r
%%R
set.seed(6001)

boot_values <- replicate(
  10000,
  mean(sample(x, size = length(x), replace = TRUE))
)

print(c(
  estimate = mean(x),
  bootstrap_bias = mean(boot_values) - mean(x),
  bootstrap_se = sd(boot_values)
))

quantile(boot_values, c(0.025, 0.975))
```

**เขียนตอบ:**

> ใช้ Bootstrap โดยสุ่ม observations แบบใส่คืนให้มี sample size เท่าเดิมจำนวน `[10,000 รอบ]` Sample mean เท่ากับ `[90.2414 ร้อยดอลลาร์]`, bootstrap bias เท่ากับ `[-0.0808]` และ bootstrap standard error เท่ากับ `[3.9360]` ส่วน 95% percentile bootstrap confidence interval เท่ากับ `[82.5200 ถึง 97.9000 ร้อยดอลลาร์]` ดังนั้น population mean family income คาดว่าอยู่ในช่วงดังกล่าว

ค่าจาก Bootstrap อาจต่างกันเล็กน้อยเมื่อเปลี่ยน random seed หรือจำนวน resamples

## 23. เปรียบเทียบ Classical กับ Bootstrap

**เขียนตอบเมื่อผลใกล้กัน:**

> Classical 95% t interval เท่ากับ `[82.2562 ถึง 98.2265]` ขณะที่ 95% percentile bootstrap interval เท่ากับ `[82.5200 ถึง 97.9000]` ทั้งสองช่วงใกล้เคียงกัน จึงให้ข้อสรุปสอดคล้องกันว่า population mean อยู่ประมาณ `[82 ถึง 98 ร้อยดอลลาร์]`

**เขียนตอบเมื่อข้อมูลเบ้และ sample เล็ก:**

> ข้อมูล `[จำนวนวันแก้ไขข้อร้องเรียน]` เบ้ขวาและ sample มีเพียง `[15 observations]` Classical t interval จึงต้องพึ่ง Normality assumption มากกว่า ข้าพเจ้าจะรายงาน `[95% percentile bootstrap interval = 6.1 ถึง 14.5 วัน]` เพราะช่วงสามารถสะท้อน sampling distribution ที่ไม่สมมาตรได้ โดยยังต้องสมมติว่า sample เป็นตัวแทนของ population

---

# ส่วนที่ 5: แผนเลือกวิธีในห้องสอบ

| โจทย์ถามหา | โครงสร้างข้อมูล | วิธีที่เลือก | R สั้นที่สุด |
|---|---|---|---|
| ช่วงของ mean หนึ่งกลุ่ม ไม่รู้ population SD | Numeric, one sample | One-sample t interval | `t.test(x)` |
| ช่วงของ mean หนึ่งกลุ่ม รู้ population SD | Numeric, one sample | One-sample z interval | คำนวณด้วย `qnorm()` |
| ช่วงของ proportion หนึ่งกลุ่ม | Binary, one sample | One-proportion interval | `prop.test(success, total)` |
| ช่วง/ทดสอบ mean สองกลุ่มอิสระ ไม่สมมติ equal variances | Numeric, independent | Welch t | `t.test(x, y)` |
| ช่วง/ทดสอบ mean สองกลุ่มอิสระ สมมติ equal variances | Numeric, independent | Pooled t | `t.test(x, y, var.equal=TRUE)` |
| ช่วง/ทดสอบ mean ก่อน–หลัง | Numeric, paired | Paired t | `t.test(after, before, paired=TRUE)` |
| ช่วง/ทดสอบ proportions สองกลุ่ม | Binary, independent | Two-proportion method | `prop.test(c(x1,x2), c(n1,n2))` |
| ทดสอบ variances สองกลุ่ม | Numeric, two Normal populations | F test | `var.test(x, y)` |
| ประมาณ bias/SE โดยตัดออกทีละค่า | Statistic ใด ๆ | Jackknife | leave-one-out loop |
| ประมาณ bias/SE/CI โดยสุ่มใส่คืน | Statistic ใด ๆ | Bootstrap | `replicate()` และ `sample()` |

---

# ส่วนที่ 6: ประโยคที่ควรจำให้ขึ้นใจ

## Confidence interval

> `[95% confidence interval]` ของ `[population parameter]` เท่ากับ `[ขอบล่าง ถึง ขอบบน พร้อมหน่วย]` กล่าวคือ เรามั่นใจ `[95%]` ว่าวิธีสร้างช่วงนี้ให้ช่วงที่ครอบคลุม `[population parameter]`

## Hypothesis test เมื่อปฏิเสธ

> เนื่องจาก `[p-value]` น้อยกว่า `[α = 0.05]` จึงปฏิเสธ $H_0$ ข้อมูลมีหลักฐานทางสถิติเพียงพอว่า `[ข้อความตาม H_1 ในบริบท population]`

## Hypothesis test เมื่อไม่ปฏิเสธ

> เนื่องจาก `[p-value]` มากกว่า `[α = 0.05]` จึงไม่ปฏิเสธ $H_0$ ข้อมูลยังไม่มีหลักฐานทางสถิติเพียงพอว่า `[ข้อความตาม H_1 ในบริบท population]`

## Normality

> `[กราฟที่ตรวจ]` ไม่แสดงความผิดปกติเด่นชัด และ Shapiro–Wilk test ให้ `[p-value]` มากกว่า 0.05 จึงยังไม่มีหลักฐานต่อต้าน Normality

## ทิศทางผลต่าง

ก่อนกด R ให้เขียนบนกระดาษเสมอว่า

> `[ผลต่างที่ต้องการ = กลุ่มแรก - กลุ่มที่สอง]`

จากนั้นใส่กลุ่มแรกเป็น argument แรกใน R เพื่อให้เครื่องหมายของ estimate, confidence interval และ alternative ตรงกับคำตอบที่ต้องการ

