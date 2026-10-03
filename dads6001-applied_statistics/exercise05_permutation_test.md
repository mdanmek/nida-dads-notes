# Exercise 05: Permutation Test พร้อมเฉลยและ R Programming

> เอกสารนี้รวมโจทย์ Permutation Test จากแบบฝึกหัดสองชุด พร้อมเฉลยทีละข้อ การคำนวณอย่างละเอียด คำตอบฉบับเขียนในห้องสอบ และโค้ด R ที่ใช้ตรวจคำตอบได้จริง

## วิธีใช้เอกสารนี้

โจทย์แต่ละข้อแบ่งเป็นสามชั้น

1. **เฉลยละเอียด:** อธิบายเหตุผล ตั้งสมมติฐาน เลือก statistic และคำนวณด้วยมือ
2. **R Programming:** รันโค้ด ตรวจ output และตีความผลที่ต้องนำไปใช้ตอบ
3. **แบบเขียนตอบข้อสอบ:** สรุปคำตอบจากผลคำนวณและผล R ให้สั้นพอสำหรับเขียนจริง

ก่อนทำโจทย์ควรจำหลักเดียวให้แม่น: Permutation Test สร้าง null distribution โดยสลับเฉพาะสิ่งที่สามารถแลกเปลี่ยนกันได้ หรือ **exchangeable** ภายใต้ $H_0$ แล้วนับว่าสถิติจากข้อมูลที่สลับมีค่ารุนแรงอย่างน้อยเท่าข้อมูลจริงบ่อยเพียงใด

---

# ข้อ 1: เวลาถอยรถออกจากที่จอด

## 1.1 โจทย์

งานวิจัยต้องการตรวจว่า เมื่อมีรถคันอื่นรอช่องจอด ผู้ขับขี่ใช้เวลาออกจากช่องจอดนานขึ้นหรือไม่ ตัวแปรตามคือเวลา หน่วยเป็นวินาที แบ่งข้อมูลเป็นสองกลุ่มอิสระ กลุ่มละ 20 คน

```text
No one waiting:
36.30, 42.07, 39.97, 39.33, 33.76, 33.91, 39.65, 84.92,
40.70, 39.65, 39.48, 35.38, 75.07, 36.46, 38.73, 33.88,
34.39, 60.52, 53.63, 50.62

Someone waiting:
49.48, 43.30, 85.97, 46.92, 49.18, 79.30, 47.35, 46.52,
59.68, 42.89, 49.29, 68.69, 41.61, 46.81, 43.75, 46.55,
42.33, 71.48, 78.95, 42.06
```

โจทย์กำหนดให้ใช้ random permutations จำนวน 5,000 รอบ แล้วหาและตีความ permutation p-value

## 1.2 ขั้นที่ 1: ระบุคำถามและสมมติฐาน

จากบริบท คำถามคือผู้ขับขี่ใช้เวลาออกจากที่จอด **นานขึ้น** เมื่อมีคนรอหรือไม่ จึงเป็น one-sided right-tailed test

กำหนด

- $\mu_W$ = ค่าเฉลี่ยเวลาถอยรถ เมื่อมีคนรอ
- $\mu_N$ = ค่าเฉลี่ยเวลาถอยรถ เมื่อไม่มีคนรอ

สมมติฐานคือ

$$
H_0:\mu_W\le\mu_N
$$

$$
H_1:\mu_W>\mu_N
$$

ในทาง permutation เราใช้กรณีขอบเขตของ $H_0$ ที่ไม่มี group effect กล่าวคือ distribution ของเวลาในสองกลุ่มเหมือนกัน และ group labels สามารถสลับกันได้

## 1.3 ขั้นที่ 2: สำรวจข้อมูล

ค่าพรรณนาที่สำคัญคือ

| กลุ่ม | $n$ | Mean | Median | SD | Sample skewness |
|---|---:|---:|---:|---:|---:|
| No one waiting | 20 | 44.4210 | 39.5650 | 14.0980 | 1.9465 |
| Someone waiting | 20 | 54.1055 | 47.1350 | 14.3942 | 1.1926 |

ทั้งสองกลุ่มเบ้ขวา เพราะเวลามีขอบล่างตามธรรมชาติ แต่บางคนอาจใช้เวลานานมาก ค่า 75-86 วินาทีจึงดึง mean ขึ้น ลักษณะนี้เป็นเหตุผลที่โจทย์เสนอ Permutation Test แทนการพึ่งพา Normal assumption อย่างเต็มที่

อย่างไรก็ตาม Permutation Test ไม่ได้แก้ทุกอย่างโดยอัตโนมัติ เรายังต้องเชื่อว่าผู้ขับขี่แต่ละคนเป็นหน่วยอิสระ และ group labels สามารถแลกเปลี่ยนกันได้ภายใต้ $H_0$

## 1.4 ขั้นที่ 3: คำนวณ Observed Statistic

เลือก statistic เป็นผลต่างค่าเฉลี่ย

$$
S=\bar{x}_W-\bar{x}_N
$$

แทนค่าได้

$$
S_{obs}=54.1055-44.4210=9.6845\text{ วินาที}
$$

เครื่องหมายบวกสอดคล้องกับ $H_1$ เพราะกลุ่มที่มีคนรอใช้เวลามากกว่าโดยเฉลี่ยประมาณ 9.68 วินาที

## 1.5 ขั้นที่ 4: สร้าง Permutation Distribution

ภายใต้ $H_0$ เรารวมเวลา 40 ค่า แล้วสลับ group labels โดยจัดให้ 20 ค่าอยู่ในกลุ่ม Someone waiting และอีก 20 ค่าอยู่ในกลุ่ม No one waiting ทุกครั้งคำนวณ mean difference ใหม่

จำนวนการแบ่งกลุ่มที่เป็นไปได้ทั้งหมดคือ

$$
\binom{40}{20}=137{,}846{,}528{,}820
$$

จำนวนนี้มากเกินกว่าจะแจกแจงด้วยวิธีตรงไปตรงมาในแบบฝึกหัด จึงสุ่มเพียง 5,000 permutations

หากมี $K$ รอบจาก 5,000 รอบที่ได้

$$
S_b\ge9.6845
$$

Monte Carlo p-value ที่ใช้ plus-one correction คือ

$$
\hat{p}=\frac{K+1}{5{,}000+1}
$$

ค่า exact one-sided p-value ที่คำนวณจากการนับ combinations แบบ dynamic programming เท่ากับประมาณ

$$
p_{exact}=0.01895
$$

ดังนั้นการสุ่ม 5,000 รอบควรให้ p-value ใกล้ 0.019 แต่ไม่จำเป็นต้องเท่ากันทุกครั้ง ตัวอย่างค่าประมาณ 0.016, 0.019 หรือ 0.023 ล้วนเป็นไปได้จาก Monte Carlo variation

## 1.6 ขั้นที่ 5: ตัดสินใจและตีความ

ที่ระดับนัยสำคัญ $\alpha=0.05$ ค่า p-value ประมาณ 0.019 ต่ำกว่า 0.05 จึงปฏิเสธ $H_0$

ข้อสรุปที่ถูกต้องคือ

> ข้อมูลให้หลักฐานทางสถิติว่า ผู้ขับขี่ใช้เวลาออกจากช่องจอดโดยเฉลี่ยนานขึ้นเมื่อมีรถคันอื่นรอช่องจอด โดยกลุ่มที่มีคนรอใช้เวลามากกว่าประมาณ 9.68 วินาที และ permutation p-value อยู่ใกล้ 0.019

ไม่ควรเขียนว่า “ความน่าจะเป็นที่ $H_0$ เป็นจริงเท่ากับ 1.9%” เพราะ p-value ไม่ใช่ความน่าจะเป็นของสมมติฐาน แต่เป็นความน่าจะเป็นที่จะพบ statistic สุดโต่งอย่างน้อยเท่าที่เห็น ภายใต้ $H_0$ และ permutation scheme ที่กำหนด

## 1.7 วิธีทำด้วย R และอ่านผลลัพธ์

```r
no_waiting <- c(
  36.30, 42.07, 39.97, 39.33, 33.76,
  33.91, 39.65, 84.92, 40.70, 39.65,
  39.48, 35.38, 75.07, 36.46, 38.73,
  33.88, 34.39, 60.52, 53.63, 50.62
)

someone_waiting <- c(
  49.48, 43.30, 85.97, 46.92, 49.18,
  79.30, 47.35, 46.52, 59.68, 42.89,
  49.29, 68.69, 41.61, 46.81, 43.75,
  46.55, 42.33, 71.48, 78.95, 42.06
)

mean(no_waiting)
mean(someone_waiting)
median(no_waiting)
median(someone_waiting)
sd(no_waiting)
sd(someone_waiting)

observed_diff <- mean(someone_waiting) - mean(no_waiting)
observed_diff
```

ผลที่ต้องได้คือ `observed_diff = 9.6845`

จากนั้นทำ Permutation Test

```r
pooled_time <- c(someone_waiting, no_waiting)
n_waiting <- length(someone_waiting)
B <- 5000

set.seed(2026)

permuted_diff <- replicate(B, {
  shuffled <- sample(pooled_time, replace = FALSE)

  new_waiting <- shuffled[1:n_waiting]
  new_no_waiting <- shuffled[-(1:n_waiting)]

  mean(new_waiting) - mean(new_no_waiting)
})

K <- sum(permuted_diff >= observed_diff)
p_value <- (K + 1) / (B + 1)

c(
  observed_difference = observed_diff,
  extreme_permutations = K,
  permutation_p_value = p_value
)
```

### อธิบายโค้ด

| Code | หน้าที่ |
|---|---|
| `pooled_time <- c(...)` | รวมเวลาไว้ภายใต้ $H_0$ ว่า labels แลกกันได้ |
| `sample(..., replace = FALSE)` | สลับ observation เดิมโดยไม่สุ่มซ้ำ |
| `shuffled[1:n_waiting]` | กำหนด 20 ค่าแรกเป็นกลุ่ม waiting ใหม่ |
| `replicate(B, {...})` | ทำขั้นตอนสลับและคำนวณซ้ำ 5,000 รอบ |
| `permuted_diff >= observed_diff` | ระบุรอบที่ statistic สุดโต่งอย่างน้อยเท่าค่าจริง |
| `(K + 1) / (B + 1)` | คำนวณ Monte Carlo p-value แบบ plus-one correction |

ตรวจกราฟ null distribution ได้ด้วย

```r
hist(
  permuted_diff,
  breaks = 30,
  main = 'Permutation Distribution of Mean Difference',
  xlab = 'Mean difference: waiting - no waiting',
  col = 'lightblue',
  border = 'white'
)

abline(v = observed_diff, col = 'red', lwd = 2)
```

เส้นแดงควรอยู่บริเวณหางขวาของ distribution หากเปลี่ยน seed ค่า $K$ และ p-value อาจเปลี่ยนเล็กน้อย แต่ข้อสรุปควรคงเดิม หากต้องการความเสถียรมากขึ้นให้เพิ่ม `B` เช่น 100,000

## 1.8 คำตอบฉบับเขียนในห้องสอบ

หลังจากรัน R และตรวจว่า `observed_diff = 9.6845` และ permutation p-value อยู่ใกล้ 0.019 จึงเขียนตอบได้ดังนี้

> กำหนด $H_0:\mu_W\le\mu_N$ และ $H_1:\mu_W>\mu_N$ ใช้ statistic $S=\bar{x}_W-\bar{x}_N$ จากข้อมูลได้ $S_{obs}=54.1055-44.4210=9.6845$ วินาที จากนั้นรวมข้อมูล 40 ค่าและสุ่มสลับ group labels โดยคงขนาดกลุ่มละ 20 จำนวน 5,000 รอบ ได้ permutation p-value ใกล้ 0.019 เนื่องจาก p-value ต่ำกว่า 0.05 จึงปฏิเสธ $H_0$ และสรุปว่ามีหลักฐานว่าการมีคนรอสัมพันธ์กับ mean waiting time ที่ยาวขึ้น

---

# ข้อ 2: Comparing Dosages

## 2.1 โจทย์

ทดลองยากับผู้ป่วยภูมิแพ้ 5 คน โดยสุ่มให้ผู้ป่วย 2 คนรับ High dose และอีก 3 คนรับ Low dose ตัวแปรตอบสนองคือจำนวนวันที่ไม่มีอาการ

| Patient | Dose เดิม | Days without symptoms |
|---:|---|---:|
| 1 | High | 12 |
| 2 | High | 13 |
| 3 | Low | 6 |
| 4 | Low | 6 |
| 5 | Low | 7 |

โจทย์ถาม

1. จงแสดงทุกวิธีที่เลือกผู้ป่วย 2 จาก 5 คนเข้าสู่ High-dose group
2. สำหรับแต่ละ assignment จงหาค่าเฉลี่ยของสองกลุ่มและผลต่างค่าเฉลี่ย

## 2.2 จำนวน Assignments ทั้งหมด

High-dose group ต้องมี 2 คนจากผู้ป่วย 5 คน จำนวนวิธีเลือกคือ

$$
\binom{5}{2}=\frac{5!}{2!3!}=10
$$

เหตุผลที่ไม่ใช้ $5!$ เพราะลำดับภายใน High group และ Low group ไม่มีความหมาย เช่น High = Patients 1, 2 เหมือนกับ High = Patients 2, 1

## 2.3 คำนวณ Assignment แรกอย่างละเอียด

Assignment ที่สังเกตจริงให้ Patients 1 และ 2 อยู่ High group

$$
\bar{x}_H=\frac{12+13}{2}=12.50
$$

$$
\bar{x}_L=\frac{6+6+7}{3}=6.33
$$

ดังนั้น

$$
S_{obs}=\bar{x}_H-\bar{x}_L=12.50-6.33=6.17
$$

## 2.4 คำตอบครบทั้ง 10 Assignments

| Assignment | High-dose patients | Low-dose patients | $\bar{x}_H$ | $\bar{x}_L$ | $\bar{x}_H-\bar{x}_L$ |
|---:|---|---|---:|---:|---:|
| 1 | 1, 2 | 3, 4, 5 | 12.50 | 6.33 | 6.17 |
| 2 | 1, 3 | 2, 4, 5 | 9.00 | 8.67 | 0.33 |
| 3 | 1, 4 | 2, 3, 5 | 9.00 | 8.67 | 0.33 |
| 4 | 1, 5 | 2, 3, 4 | 9.50 | 8.33 | 1.17 |
| 5 | 2, 3 | 1, 4, 5 | 9.50 | 8.33 | 1.17 |
| 6 | 2, 4 | 1, 3, 5 | 9.50 | 8.33 | 1.17 |
| 7 | 2, 5 | 1, 3, 4 | 10.00 | 8.00 | 2.00 |
| 8 | 3, 4 | 1, 2, 5 | 6.00 | 10.67 | -4.67 |
| 9 | 3, 5 | 1, 2, 4 | 6.50 | 10.33 | -3.83 |
| 10 | 4, 5 | 1, 2, 3 | 6.50 | 10.33 | -3.83 |

ตารางนี้คือ exact permutation distribution เพราะแจกแจงครบทุก assignment ที่เป็นไปได้

## 2.5 สร้าง Sampling Distribution

ผลต่างบางค่าซ้ำกัน จึงรวมเป็นความน่าจะเป็นได้ดังนี้

| Mean difference | จำนวน permutations | Probability ภายใต้ $H_0$ |
|---:|---:|---:|
| -4.67 | 1 | 0.10 |
| -3.83 | 2 | 0.20 |
| 0.33 | 2 | 0.20 |
| 1.17 | 3 | 0.30 |
| 2.00 | 1 | 0.10 |
| 6.17 | 1 | 0.10 |

หาก alternative คือ High dose ให้ค่าเฉลี่ยสูงกว่า Low dose จะใช้ right-tailed p-value

$$
p=P(S_{perm}\ge6.17\mid H_0)=\frac{1}{10}=0.10
$$

ที่ระดับ 0.05 ยังไม่ปฏิเสธ $H_0$ แม้ observed difference จะมาก เพราะมี sample เพียง 5 คน ทำให้ permutation distribution หยาบมาก p-value ต่ำสุดที่เป็นไปได้สำหรับ right-tailed test นี้คือ 0.10

ประเด็นนี้สำคัญ: effect ที่สังเกตได้ใหญ่ไม่ได้รับประกันว่าจะ statistically significant เมื่อจำนวน assignments น้อยมาก

## 2.6 วิธีทำด้วย R และอ่านผลลัพธ์

```r
patient <- 1:5
response <- c(12, 13, 6, 6, 7)

high_assignments <- combn(patient, 2)

permutation_result <- apply(high_assignments, 2, function(high_id) {
  low_id <- setdiff(patient, high_id)

  mean_high <- mean(response[high_id])
  mean_low <- mean(response[low_id])

  c(
    high_1 = high_id[1],
    high_2 = high_id[2],
    mean_high = mean_high,
    mean_low = mean_low,
    mean_difference = mean_high - mean_low
  )
})

permutation_table <- as.data.frame(t(permutation_result))
permutation_table
```

`combn(patient, 2)` สร้างทุก combination ของผู้ป่วย 2 คน จึงได้ matrix 2 แถว 10 คอลัมน์ แต่ละคอลัมน์คือ High-dose assignment หนึ่งกรณี `setdiff()` หาอีก 3 คนที่ต้องอยู่ Low group จากนั้น `apply(..., 2, ...)` คำนวณทีละคอลัมน์

คำนวณ p-value ได้ดังนี้

```r
observed_diff <- permutation_table[['mean_difference']][1]

K <- sum(
  permutation_table[['mean_difference']] >= observed_diff
)

exact_p_value <- K / nrow(permutation_table)

c(
  observed_difference = observed_diff,
  extreme_assignments = K,
  exact_p_value = exact_p_value
)
```

ผลที่ต้องได้คือ

```text
observed_difference = 6.166667
extreme_assignments = 1
exact_p_value = 0.1
```

กรณี exact enumeration ไม่ต้องใช้ plus-one correction เพราะเราไม่ได้สุ่มเพียงบางส่วน แต่แจกแจงครบทุก assignment และ observed assignment รวมอยู่ใน 10 กรณีแล้ว

## 2.7 คำตอบฉบับเขียนในห้องสอบ

หลังจากรัน R และตรวจว่า `observed_difference = 6.166667`, `extreme_assignments = 1` และ `exact_p_value = 0.1` จึงเขียนตอบได้ดังนี้

> เลือกผู้ป่วย 2 จาก 5 คนเข้าสู่ High-dose group ได้ $\binom{5}{2}=10$ assignments สำหรับข้อมูลจริง $\bar{x}_H=(12+13)/2=12.50$ และ $\bar{x}_L=(6+6+7)/3=6.33$ จึงได้ $S_{obs}=6.17$ เมื่อแจกแจงครบ 10 assignments มีเพียง assignment เดียวที่ได้ mean difference มากกว่าหรือเท่ากับ 6.17 ดังนั้น one-sided exact permutation p-value เท่ากับ $1/10=0.10$ ที่ระดับ 0.05 จึงยังไม่มีหลักฐานเพียงพอว่า High dose ให้ mean symptom-free days สูงกว่า Low dose

---

# ข้อ 3: Do Dogs Prefer Petting to Vocal Praise?

## 3.1 โจทย์และ Experimental Design

สุนัข 14 ตัวถูกสุ่มแบ่งเป็นสองกลุ่ม กลุ่มละ 7 ตัว

- Group 1: เจ้าของลูบสุนัข ส่วนผู้ช่วยใช้คำชมด้วยเสียง
- Group 2: เจ้าของใช้คำชมด้วยเสียง ส่วนผู้ช่วยลูบสุนัข

ตัวแปรตอบสนองคือเวลาที่สุนัขใช้ปฏิสัมพันธ์กับเจ้าของ หน่วยเป็นวินาที

```text
Petting group:
114, 203, 217, 254, 256, 284, 296

Vocal-praise group:
4, 7, 24, 25, 48, 71, 294
```

โจทย์ถาม

1. เพราะเหตุใด two-sample t test อาจไม่เหมาะสม
2. จงสร้าง Permutation Test พร้อมระบุสมมติฐานและวิธีสร้าง sampling distribution
3. จงหา permutation p-value และตีความ

## 3.2 ข้อ 3(a): เหตุใด t Test อาจไม่เหมาะสม

แต่ละกลุ่มมีเพียง 7 observations ทำให้ยากที่จะอาศัย Central Limit Theorem ชดเชย non-normality ข้อมูล Vocal-praise group มีค่า 294 วินาทีซึ่งห่างจากอีกหกค่ามาก Distribution จึงเบ้ขวารุนแรงและมี potential outlier

ค่าพรรณนาคือ

| กลุ่ม | Mean | Median | SD |
|---|---:|---:|---:|
| Petting | 232.0000 | 254 | 61.7117 |
| Vocal praise | 67.5714 | 25 | 102.5392 |

ค่า mean ของ Vocal-praise group ถูกค่า 294 ดึงขึ้นมาก เห็นได้จาก mean 67.57 แต่ median เพียง 25 การใช้ t test กับ sample เล็กและ skewed distribution เช่นนี้อาจไม่น่าเชื่อถือ โดยเฉพาะสำหรับ one-sided inference

การเลือก Permutation Test ไม่ได้หมายความว่า outlier หายไป ค่า 294 ยังอยู่ในข้อมูลทุก permutation แต่เราไม่จำเป็นต้องสมมติว่าประชากรมี Normal distribution เพื่อสร้าง null distribution

## 3.3 ข้อ 3(b): ตั้งสมมติฐานและสร้าง Permutation Test

โจทย์ต้องการตรวจว่าสุนัขใช้เวลากับเจ้าของมากกว่าเมื่อเจ้าของลูบ จึงกำหนด

$$
H_0:F_{Petting}=F_{Vocal}
$$

$$
H_1:\mu_{Petting}>\mu_{Vocal}
$$

$H_0$ ใน permutation framework ระบุว่า response distributions เหมือนกัน จึงอนุมานได้ว่า means เท่ากันด้วย ส่วน $H_1$ ใช้ทิศทางของ mean ตามคำถามวิจัย

เลือก statistic เป็น

$$
S=\bar{x}_{Petting}-\bar{x}_{Vocal}
$$

ค่าที่สังเกตคือ

$$
S_{obs}=232.0000-67.5714=164.4286\text{ วินาที}
$$

ภายใต้ $H_0$ เรารวม response 14 ค่า แล้วเลือก 7 ค่าเป็น Petting group ใหม่ อีก 7 ค่าเป็น Vocal-praise group จำนวน assignment ทั้งหมดคือ

$$
\binom{14}{7}=3{,}432
$$

เพราะมีเพียง 3,432 assignments จึงแจกแจงครบทั้งหมดได้ ไม่จำเป็นต้องใช้ Monte Carlo approximation

## 3.4 ข้อ 3(c): คำนวณ p-value

จาก 3,432 assignments มี 13 assignments ที่ให้ mean difference มากกว่าหรือเท่ากับ 164.4286 วินาที รวม observed assignment ด้วย

ดังนั้น

$$
p=\frac{13}{3{,}432}=0.00379\approx0.004
$$

ที่ระดับ $\alpha=0.05$ ค่า p-value ต่ำกว่า 0.05 จึงปฏิเสธ $H_0$

ข้อสรุปคือ

> ภายใต้ randomized design ข้อมูลให้หลักฐานอย่างมากว่า สุนัขใช้เวลาปฏิสัมพันธ์กับเจ้าของโดยเฉลี่ยมากกว่าเมื่อเจ้าของลูบ เทียบกับเมื่อเจ้าของให้คำชมด้วยเสียง

การทดลองนี้สนับสนุน causal interpretation ได้มากกว่า observational study เพราะสุนัขถูกสุ่มแบ่งกลุ่ม แต่ข้อสรุปยังจำกัดอยู่กับประชากรและเงื่อนไขที่กลุ่มตัวอย่างเป็นตัวแทนได้

## 3.5 วิธีทำด้วย R และอ่านผลลัพธ์

```r
petting <- c(114, 203, 217, 254, 256, 284, 296)
vocal_praise <- c(4, 7, 24, 25, 48, 71, 294)

mean(petting)
mean(vocal_praise)
median(petting)
median(vocal_praise)
sd(petting)
sd(vocal_praise)

observed_diff <- mean(petting) - mean(vocal_praise)
observed_diff
```

ผลต้องได้ `observed_diff = 164.4286` โดยประมาณ

แจกแจงครบทุก assignment ด้วย `combn()`

```r
all_responses <- c(petting, vocal_praise)
n_petting <- length(petting)

petting_assignments <- combn(
  seq_along(all_responses),
  n_petting
)

permuted_diff <- apply(
  petting_assignments,
  2,
  function(petting_id) {
    vocal_id <- setdiff(
      seq_along(all_responses),
      petting_id
    )

    mean(all_responses[petting_id]) -
      mean(all_responses[vocal_id])
  }
)

K <- sum(permuted_diff >= observed_diff)
exact_p_value <- K / length(permuted_diff)

c(
  total_assignments = length(permuted_diff),
  observed_difference = observed_diff,
  extreme_assignments = K,
  exact_p_value = exact_p_value
)
```

ผลที่ต้องได้คือ

```text
total_assignments = 3432
observed_difference = 164.4286
extreme_assignments = 13
exact_p_value = 0.003788
```

สร้าง histogram ได้ด้วย

```r
hist(
  permuted_diff,
  breaks = 30,
  main = 'Exact Permutation Distribution',
  xlab = 'Mean difference: petting - vocal praise',
  col = 'wheat',
  border = 'white'
)

abline(v = observed_diff, col = 'red', lwd = 2)
```

เส้นแดงควรอยู่ไกลในหางขวา ซึ่งสอดคล้องกับ p-value ประมาณ 0.004

## 3.6 คำตอบฉบับเขียนในห้องสอบ

เมื่อรัน R แล้ว เรามีหลักฐานสำหรับเขียนตอบครบทั้งลักษณะข้อมูล, observed statistic, จำนวน assignments และ exact p-value

### ข้อ 3(a): เหตุใด t Test อาจไม่เหมาะสม

> Two-sample t test อาจไม่เหมาะเพราะแต่ละกลุ่มมีเพียง $n=7$ และผลจาก R แสดงว่า Vocal-praise group มี mean 67.57 แต่ median เพียง 25 เนื่องจากมีค่าที่สูงผิดกลุ่มคือ 294 วินาที ข้อมูลจึงเบ้ขวารุนแรง เมื่อ sample เล็ก CLT ยังช่วยได้จำกัด จึงไม่มั่นใจใน Normal approximation ของ t statistic โดยเฉพาะสำหรับ one-sided test Permutation Test จึงเหมาะกว่า หาก group labels exchangeable ตาม randomized design

### ข้อ 3(b): สมมติฐานและวิธีสร้าง Permutation Distribution

> กำหนด $H_0$ ว่า distributions ของ interaction time ในสองเงื่อนไขเหมือนกัน และ $H_1:\mu_{Petting}>\mu_{Vocal}$ ใช้ statistic $S=\bar{x}_{Petting}-\bar{x}_{Vocal}$ จาก R ได้ observed value 164.43 วินาที ภายใต้ $H_0$ ให้รวมข้อมูล 14 ค่าและจัดแบ่งใหม่เป็นสองกลุ่มขนาด 7 เท่ากันครบ $\binom{14}{7}=3{,}432$ assignments แล้วคำนวณ mean difference ของแต่ละ assignment เพื่อสร้าง exact permutation distribution

### ข้อ 3(c): p-value และข้อสรุป

> ผลจาก R พบว่า 13 จาก 3,432 assignments ให้ mean difference อย่างน้อย 164.43 วินาที จึงได้ $p=13/3432=0.00379$ เนื่องจาก $p<0.05$ จึงปฏิเสธ $H_0$ และสรุปว่ามีหลักฐานว่าสุนัขใช้เวลากับเจ้าของมากกว่าเมื่อได้รับการลูบแทนคำชมด้วยเสียง

## 3.7 เปรียบเทียบกับ t Test

เอกสารรายงาน one-sided t-test p-value ประมาณ 0.0023 ขณะที่ exact permutation p-value ประมาณ 0.0038 ทั้งสองวิธีให้ข้อสรุปเหมือนกัน แต่ p-values ไม่เท่ากัน เพราะสร้าง null distribution คนละวิธี

- t test ใช้ theoretical t distribution ภายใต้ model assumptions
- Permutation Test ใช้ทุก assignment ที่อนุญาตโดย randomized design

ในโจทย์นี้ Permutation Test น่าเชื่อถือกว่าในแง่ distributional assumption เพราะข้อมูลเบ้และ sample เล็ก แต่ต้องจำไว้ว่ามันยังพึ่งพาการสุ่มแบ่งกลุ่มและ exchangeability

---

# 4. R Template สำหรับ Two-group Permutation Test

โค้ดต่อไปนี้นำไปดัดแปลงกับโจทย์สองกลุ่มอื่นได้

```r
permutation_mean_test <- function(
  group_1,
  group_2,
  B = 10000,
  alternative = 'greater',
  seed = 2026
) {
  observed <- mean(group_1) - mean(group_2)
  pooled <- c(group_1, group_2)
  n_1 <- length(group_1)

  set.seed(seed)

  permuted <- replicate(B, {
    shuffled <- sample(pooled, replace = FALSE)

    mean(shuffled[1:n_1]) -
      mean(shuffled[-(1:n_1)])
  })

  if (alternative == 'greater') {
    K <- sum(permuted >= observed)
  } else if (alternative == 'less') {
    K <- sum(permuted <= observed)
  } else if (alternative == 'two.sided') {
    K <- sum(abs(permuted) >= abs(observed))
  } else {
    stop('alternative must be greater, less, or two.sided')
  }

  p_value <- (K + 1) / (B + 1)
  se_mc <- sqrt(p_value * (1 - p_value) / B)

  list(
    observed_difference = observed,
    extreme_permutations = K,
    permutations = B,
    p_value = p_value,
    monte_carlo_se = se_mc,
    permuted_statistics = permuted
  )
}
```

ตัวอย่างใช้งานกับโจทย์ที่จอดรถ

```r
parking_result <- permutation_mean_test(
  group_1 = someone_waiting,
  group_2 = no_waiting,
  B = 5000,
  alternative = 'greater',
  seed = 2026
)

parking_result[[
  'observed_difference'
]]

parking_result[['p_value']]
parking_result[['monte_carlo_se']]
```

ใช้ `[[...]]` เพื่อดึงค่าจาก list โดยหลีกเลี่ยงความสับสนระหว่างเครื่องหมาย dollar ของ R กับ math delimiter ใน Markdown

## 4.1 Trace การทำงานหนึ่งรอบ

| State | สิ่งที่เกิดขึ้น | ผลลัพธ์ |
|---|---|---|
| ก่อนสลับ | รวม observation ของสองกลุ่ม | vector ความยาว $n_1+n_2$ |
| สลับ | `sample(..., replace = FALSE)` | observation เดิมครบ แต่ลำดับใหม่ |
| แบ่งกลุ่ม | $n_1$ ค่าแรกเป็น Group 1 | รักษาขนาดกลุ่มเดิม |
| คำนวณ | mean กลุ่ม 1 ลบ mean กลุ่ม 2 | permutation statistic หนึ่งค่า |
| ทำซ้ำ | `replicate(B, ...)` | null distribution จำนวน $B$ ค่า |
| นับหาง | เปรียบเทียบกับ observed statistic | จำนวน extreme permutations $K$ |
| สรุป | $(K+1)/(B+1)$ | Monte Carlo p-value |

## 4.2 จุดที่มักเขียน R ผิด

### ใช้ `replace = TRUE`

นี่เป็นการสุ่มแบบ Bootstrap ไม่ใช่ permutation เพราะ observation บางค่าอาจซ้ำและบางค่าหายไป ใน Permutation Test ทุก observation ต้องปรากฏหนึ่งครั้งต่อรอบ

### สลับแต่ลำดับภายในกลุ่ม

Mean ของแต่ละกลุ่มจะไม่เปลี่ยน จึงได้ statistic เดิมทุกครั้ง ต้องสลับ group membership ผ่าน pooled data หรือ labels

### นับหางผิดด้าน

หาก $H_1:\mu_1>\mu_2$ ต้องนับ `permuted >= observed` หาก $H_1:\mu_1<\mu_2$ ต้องนับ `permuted <= observed`

### รายงาน p-value เป็นศูนย์

สำหรับ Monte Carlo test ให้ใช้ plus-one correction หากไม่มี permutation ใดสุดโต่งกว่าค่าจริง ควรรายงาน $1/(B+1)$ ไม่ใช่ศูนย์

---

# 5. ตารางสรุปคำตอบ

| โจทย์ | Statistic | Observed value | Permutations | p-value | ข้อสรุปที่ $\alpha=0.05$ |
|---|---|---:|---:|---:|---|
| Parking space | Mean waiting - no waiting | 9.6845 วินาที | 5,000 random | ใกล้ 0.019 | ปฏิเสธ $H_0$ |
| Comparing dosages | Mean high - low | 6.1667 วัน | 10 exact | 0.1000 | ไม่ปฏิเสธ $H_0$ |
| Dogs | Mean petting - vocal | 164.4286 วินาที | 3,432 exact | 0.00379 | ปฏิเสธ $H_0$ |

## 6. โครงเขียนตอบ Permutation Test ที่ใช้ได้กับทุกข้อ

> กำหนด $H_0$ และ $H_1$ ตามคำถาม เลือก statistic เป็น [ชื่อและสูตร] จากข้อมูลจริงได้ $S_{obs}=[ค่า]$ ภายใต้ $H_0$ [ระบุสิ่งที่ exchangeable] จึงสลับ [labels/pairings/signs] โดยรักษา [ขนาดกลุ่ม/block/pair structure] แล้วคำนวณ statistic ซ้ำ [จำนวน] ครั้ง p-value คือสัดส่วนของ permuted statistics ที่สุดโต่งอย่างน้อยเท่า $S_{obs}$ ได้ $p=[ค่า]$ เนื่องจาก $p$ [น้อยกว่า/มากกว่า] $\alpha$ จึง [ปฏิเสธ/ไม่ปฏิเสธ] $H_0$ และสรุปในบริบทว่า [ข้อสรุป]

สิ่งที่ผู้ตรวจควรเห็นในคำตอบคือ

- ทิศทางของ $H_1$ ตรงกับหางที่นับ
- statistic มีนิยามและลำดับการลบชัดเจน
- บอกว่าสลับอะไร ไม่ใช่เขียนเพียงว่า “ทำ permutation”
- รักษาขนาดกลุ่มและโครงสร้างการทดลอง
- ตีความ p-value และข้อสรุปในบริบท
- ไม่ใช้คำว่า “ยอมรับ $H_0$” และไม่ตีความ p-value เป็นโอกาสที่ $H_0$ เป็นจริง

## References

- `exercise05_permutation.pdf`: โจทย์ Waiting at parking space
- `exercise05_permutation_test2.pdf`: ตัวอย่าง Comparing Dosages และ Do Dogs Prefer Petting to Vocal Praise?
