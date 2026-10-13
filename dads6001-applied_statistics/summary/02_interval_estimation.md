# จากค่าประมาณหนึ่งค่าไปสู่ช่วงที่สะท้อนความไม่แน่นอน

> **Course:** DADS6001 Applied Modern Statistical Analysis  
> **Week:** 02  
> **Sources:** Lecture 02 จำนวน 24 สไลด์, Lab 02 และ Lab 02 Solution in R  
> **Course navigation:** [Course Overview](00_readme.md) · บทก่อนหน้า [01 Introduction](01_introduction.md) · บทถัดไป [03 Jackknife and Bootstrap](03_jackknife_bootstrap.md)

สมมติว่าสุ่มลูกค้า 15 คนแล้วพบว่าใช้เงินมื้อกลางวันที่ร้าน fast-food เฉลี่ย 7.09 ดอลลาร์ ตัวเลขนี้เป็นคำตอบจาก sample ปัจจุบัน แต่ถ้าสุ่มลูกค้าใหม่ ค่าเฉลี่ยอาจเปลี่ยนไป เราจึงไม่ควรรายงาน 7.09 แล้วทำเหมือนรู้ค่าเฉลี่ยของลูกค้าทั้งหมดอย่างแน่นอน

บทที่ 01 อธิบายว่าค่าเฉลี่ยตัวอย่างเปลี่ยนได้เมื่อสุ่ม sample ใหม่ และใช้ standard error วัดความผันผวนนั้น บทนี้นำแนวคิดดังกล่าวมาสร้าง **ช่วงความเชื่อมั่น (confidence interval หรือ CI)** เพื่อรายงานทั้งค่าประมาณและความไม่แน่นอน

## 1. จาก Point Estimate ไปสู่ Interval Estimate

ในตัวอย่าง fast-food สิ่งที่ต้องการรู้คือค่าเฉลี่ยยอดใช้จ่ายของ population เขียนเป็น $\mu$ ค่านี้คือ **estimand** หรือ parameter เป้าหมาย

เราใช้ค่าเฉลี่ยตัวอย่าง:

$$
\bar X=\frac{1}{n}\sum_{i=1}^{n}X_i
$$

เป็น **estimator** ก่อนเห็นข้อมูล $\bar X$ ยังเปลี่ยนไปตาม sample หลังเก็บข้อมูลและคำนวณได้ $\bar x=7.0933$ ตัวเลขนี้คือ **estimate**

ความสัมพันธ์คือ:

> ต้องการรู้ estimand → ใช้ estimator กับ random sample → ได้ estimate

Point estimate บอกตำแหน่งที่ข้อมูลชี้ไป แต่ไม่บอกว่าแม่นเพียงใด Interval estimate จึงขยายออกจาก estimate ตามความผันผวนของ estimator

## 2. Confidence Interval ถูกสร้างจากอะไร

Confidence interval ส่วนใหญ่มีโครงสร้าง:

$$
\text{Estimate}
\mathbin{\pm}
\text{Critical value}
\mathbin{\times}
\text{Standard error}
$$

ส่วนที่คูณกันคือ **margin of error**:

$$
E=\text{Critical value}\times\text{Standard error}
$$

Estimate บอกจุดกึ่งกลาง Standard error บอกว่า estimator เปลี่ยนเพียงใดเมื่อสุ่ม sample ใหม่ และ critical value บอกว่าต้องขยายออกกี่ standard errors เพื่อให้วิธีมีระดับความเชื่อมั่นที่กำหนด

สำหรับ 95% CI ภายใต้ Standard Normal distribution พื้นที่ตรงกลาง 95% อยู่ระหว่าง $-1.96$ กับ $1.96$ จึงใช้ critical value 1.96 เมื่อไม่ทราบ population SD และใช้ sample SD แทน จะใช้ Student's t distribution ซึ่งมีหางหนากว่า Normal

## 3. ความหมายของ 95% Confidence

ก่อนสุ่มข้อมูล ขอบล่าง $L$ และขอบบน $U$ เป็น random quantities:

$$
P(L<\theta<U)=1-\alpha
$$

หากสุ่ม sample และสร้าง 95% CI ด้วยวิธีเดิมซ้ำจำนวนมาก ประมาณ 95% ของช่วงทั้งหมดจะครอบคลุม parameter จริง หลังเก็บข้อมูลแล้ว parameter เป็นค่าคงที่และช่วงที่คำนวณได้จะครอบคลุมหรือไม่ครอบคลุมค่านั้น

จึงเขียนในบริบทว่า:

> เรามีความเชื่อมั่น 95% ว่าค่าเฉลี่ยยอดใช้จ่ายมื้อกลางวันของ population ลูกค้าอยู่ระหว่าง 6.315 ถึง 7.872 ดอลลาร์

ช่วงนี้ประมาณ population mean ไม่ใช่ช่วงที่บอกว่าลูกค้ารายบุคคล 95% ต้องจ่ายอยู่ระหว่างสองค่านี้

## 4. ค่าเฉลี่ยหนึ่งประชากร

คำถามประเภทนี้มี sample เชิงปริมาณหนึ่งชุด เช่น ยอดใช้จ่ายหรือเวลารอ และต้องการประมาณ $\mu$

หากทราบ population standard deviation $\sigma$:

$$
\bar x\mathbin{\pm}z_{\alpha/2}\frac{\sigma}{\sqrt n}
$$

ในงานจริงมักไม่ทราบ $\sigma$ จึงใช้ sample standard deviation $s$ และ t distribution:

$$
SE(\bar X)=\frac{s}{\sqrt n}
$$

$$
\bar x\mathbin{\pm}t_{\alpha/2,n-1}\frac{s}{\sqrt n}
$$

ข้อมูลควรมาจากกระบวนการสุ่มที่เป็นตัวแทน observations ต้องเป็นอิสระ และสำหรับ sample เล็ก population ควรใกล้ Normal โดยไม่มี outlier รุนแรง Sample ใหญ่ช่วยลด random uncertainty แต่ไม่แก้ selection bias หรือ measurement error

### กรณี Bank Robberies จาก Lecture

Lecture ยกข้อมูลเหตุปล้นธนาคารในสหราชอาณาจักร 364 ครั้ง เพื่อประมาณ population means ของจำนวนเงินที่ถูกขโมย จำนวนพนักงาน ลูกค้า ผู้ก่อเหตุ และเวลาเดินทางจากสถานีตำรวจที่ใกล้ที่สุด หลักคิดเหมือนกันทุกตัวแปร: sample mean เป็น point estimate และใช้ sample SD สร้าง t interval เพราะไม่ทราบ population SD

ตัวอย่างเวลาเดินทางมี sample mean 4.557 นาที และ sample SD 4.028 นาที:

$$
SE=\frac{4.028}{\sqrt{364}}=0.2111
$$

เมื่อใช้ $t_{0.025,363}$ ประมาณ 1.966 จะได้:

$$
4.557\mathbin{\pm}1.966(0.2111)
$$

จึงได้ 95% CI ประมาณ 4.142 ถึง 4.972 นาที ช่วงนี้ประมาณ population mean travel time ไม่ได้บอกว่าเหตุปล้นแต่ละครั้งต้องมีเวลาเดินทางอยู่ในช่วงดังกล่าว

จำนวนเงินที่ถูกขโมยมี sample mean 20,330.5 ปอนด์ แต่ sample SD สูงถึง 53,510.2 ปอนด์ ตัวเลขนี้เตือนให้ตรวจความเบ้และ extreme values เพราะ mean และ standard error อาจได้รับอิทธิพลจากเหตุการณ์ที่มีมูลค่าสูงมาก แม้ sample ขนาดใหญ่จะช่วยให้ใช้ CLT ได้ดีขึ้นก็ตาม

## 5. สัดส่วนหนึ่งประชากร

หาก outcome มีสองสถานะ และพบ success จำนวน $x$ จากทั้งหมด $n$ คน:

$$
\hat p=\frac{x}{n}
$$

$$
SE(\hat p)=\sqrt{\frac{\hat p(1-\hat p)}{n}}
$$

$$
\hat p\mathbin{\pm}z_{\alpha/2}
\sqrt{\frac{\hat p(1-\hat p)}{n}}
$$

นี่คือ Wald interval ตามสูตรใน Lecture จำนวน successes และ failures ต้องมากพอให้ Normal approximation สมเหตุสมผล

## 6. ผลต่างค่าเฉลี่ยของสองกลุ่ม

หากสมาชิกในสองกลุ่มเป็นคนละคน จะเป็น **independent samples** กำหนดทิศทางก่อนคำนวณ:

$$
\mu_1-\mu_2
$$

Point estimator คือ $\bar X_1-\bar X_2$

หากทราบ population variances $\sigma_1^2$ และ $\sigma_2^2$:

$$
(\bar x_1-\bar x_2)
\mathbin{\pm}
z_{\alpha/2}
\sqrt{\frac{\sigma_1^2}{n_1}+\frac{\sigma_2^2}{n_2}}
$$

เมื่อไม่ทราบ variances และไม่สมมติว่าเท่ากัน ใช้ Welch interval:

$$
SE=\sqrt{\frac{s_1^2}{n_1}+\frac{s_2^2}{n_2}}
$$

$$
(\bar x_1-\bar x_2)
\mathbin{\pm}
t_{\alpha/2,\nu}SE
$$

หากโจทย์กำหนด equal population variances ใช้ pooled variance:

$$
s_p^2=
\frac{(n_1-1)s_1^2+(n_2-1)s_2^2}
{n_1+n_2-2}
$$

$$
(\bar x_1-\bar x_2)
\mathbin{\pm}
t_{\alpha/2,n_1+n_2-2}
s_p\sqrt{\frac{1}{n_1}+\frac{1}{n_2}}
$$

Welch เป็นค่าเริ่มต้นของ t.test() ใน R ส่วน pooled method ต้องระบุ var.equal = TRUE

## 7. ค่าเฉลี่ยของข้อมูลที่จับคู่กัน

ข้อมูลก่อนและหลังของผู้ป่วยคนเดิมไม่ใช่ independent samples วิธีที่ตรงกับ design คือสร้างผลต่างภายในแต่ละคู่:

$$
d_i=X_{1i}-X_{2i}
$$

แล้ววิเคราะห์ differences เหมือน one-sample problem:

$$
\bar d\mathbin{\pm}
t_{\alpha/2,n-1}\frac{s_d}{\sqrt n}
$$

ทิศทางขึ้นกับนิยาม $d_i$ หากกำหนด before minus after ค่าบวกหมายถึงค่าก่อนสูงกว่าหลัง สิ่งที่ควรใกล้ Normal สำหรับ small-sample paired interval คือ distribution ของ differences

## 8. ผลต่างสัดส่วนของสองกลุ่ม

สำหรับสองกลุ่มอิสระที่ outcome เป็น binary:

$$
\hat p_1=\frac{x_1}{n_1},
\qquad
\hat p_2=\frac{x_2}{n_2}
$$

$$
SE=
\sqrt{
\frac{\hat p_1(1-\hat p_1)}{n_1}
+
\frac{\hat p_2(1-\hat p_2)}{n_2}
}
$$

$$
(\hat p_1-\hat p_2)
\mathbin{\pm}
z_{\alpha/2}SE
$$

ต้องกำหนดกลุ่ม 1 และกลุ่ม 2 ให้ตรงกับคำถาม การกลับลำดับจะเปลี่ยนเครื่องหมายของ estimate และ interval แต่ไม่เปลี่ยนว่าช่วงครอบคลุม 0 หรือไม่

## 9. เลือกวิธีจากโครงสร้างของโจทย์

ก่อนเลือกสูตร ให้พิจารณาตามลำดับดังนี้

1. ตัวแปรเป็นค่าต่อเนื่องหรือผลลัพธ์สองแบบ
2. มีหนึ่งกลุ่มหรือสองกลุ่ม
3. ถ้ามีสองกลุ่ม เป็นคนละกลุ่มหรือเป็นข้อมูลจับคู่
4. ต้องการประมาณ mean, proportion, difference in means หรือ difference in proportions

### 9.1 ค่าต่อเนื่องจากหนึ่งกลุ่ม

ตัวอย่างโจทย์:

> โรงพยาบาลสุ่มผู้ป่วย 40 คน พบว่ามีเวลารอรับยาเฉลี่ย 32.5 นาที และ sample standard deviation เท่ากับ 8.4 นาที จงสร้าง 95% confidence interval ของเวลาเฉลี่ยที่ผู้ป่วยทั้งหมดใช้รอรับยา

สิ่งที่สังเกตได้คือ:

- เวลารอรับยาเป็นค่าต่อเนื่อง
- มีผู้ป่วยตัวอย่างเพียงหนึ่งกลุ่ม
- ต้องการประมาณ population mean
- ไม่ทราบ population standard deviation จึงใช้ sample standard deviation แทน

ดังนั้นโจทย์นี้ใช้ **one-sample t interval** โดยคำนวณตาม **ข้อ 4 ค่าเฉลี่ยหนึ่งประชากร**

$$
\bar{x} \pm t_{\alpha/2,n-1}\frac{s}{\sqrt{n}}
$$

#### R ที่ใช้

```r
%%R
# Confidence interval ของค่าเฉลี่ยหนึ่งประชากร
t.test(x, conf.level = 0.95)
```

`x` คือ vector ที่เก็บข้อมูลค่าต่อเนื่องของตัวอย่างหนึ่งกลุ่ม

ตัวอย่างอื่นที่ใช้วิธีเดียวกัน ได้แก่ ค่าใช้จ่ายเฉลี่ยของลูกค้า น้ำหนักเฉลี่ยของผลิตภัณฑ์ ระยะเวลานอนโรงพยาบาลเฉลี่ย และคะแนนสอบเฉลี่ยของนักศึกษา

หลักจำคือ:

> ค่าต่อเนื่อง + หนึ่งกลุ่ม + ต้องการค่าเฉลี่ย → ใช้ข้อ 4 และ `t.test(x)`

---

### 9.2 ผลลัพธ์สองแบบจากหนึ่งกลุ่ม

ตัวอย่างโจทย์:

> จากประชาชนตัวอย่าง 500 คน พบว่า 320 คนได้รับวัคซีน จงสร้าง 95% confidence interval ของสัดส่วนประชาชนทั้งหมดที่ได้รับวัคซีน

แต่ละคนมีผลลัพธ์เพียงสองแบบคือ:

- ได้รับวัคซีน
- ไม่ได้รับวัคซีน

จึงไม่ได้สนใจค่าเฉลี่ยของตัวเลขที่วัดได้ แต่สนใจ **สัดส่วนของประชากร** ที่มีลักษณะตามที่กำหนด

Sample proportion คือ

$$
\hat{p}=\frac{320}{500}=0.64
$$

ดังนั้นโจทย์นี้ใช้ **one-proportion interval** โดยคำนวณตาม **ข้อ 5 สัดส่วนหนึ่งประชากร**

$$
\hat{p} \pm z_{\alpha/2}\sqrt{\frac{\hat{p}(1-\hat{p})}{n}}
$$

#### R ที่ใช้

```r
%%R
# Confidence interval ของสัดส่วนหนึ่งประชากร
success <- 320
n <- 500

p_hat <- success / n

p_hat + c(-1, 1) * qnorm(0.975) *
  sqrt(p_hat * (1 - p_hat) / n)
```

`success` คือจำนวนคนที่เกิดผลลัพธ์ที่สนใจ และ `n` คือจำนวนตัวอย่างทั้งหมด

ตัวอย่างอื่นที่ใช้วิธีเดียวกัน ได้แก่ สัดส่วนผู้ป่วยที่หาย สัดส่วนสินค้าที่ชำรุด สัดส่วนลูกค้าที่พึงพอใจ และสัดส่วนนักศึกษาที่สอบผ่าน

หลักจำคือ:

> ผลลัพธ์สองแบบ + หนึ่งกลุ่ม + ต้องการสัดส่วน → ใช้ข้อ 5 และคำนวณจาก `p_hat`

---

### 9.3 ค่าต่อเนื่องจากสองกลุ่มอิสระ

ตัวอย่างโจทย์:

> สุ่มนักศึกษาที่เรียนด้วยวิธี A จำนวน 30 คน และนักศึกษาคนละกลุ่มที่เรียนด้วยวิธี B จำนวน 35 คน ต้องการสร้าง 95% confidence interval ของผลต่างคะแนนเฉลี่ยระหว่างวิธี A กับวิธี B

คะแนนสอบเป็นค่าต่อเนื่อง และนักศึกษาในกลุ่ม A กับกลุ่ม B เป็นคนละคนกัน จึงเป็น **independent samples**

Parameter ที่ต้องการประมาณคือ

$$
\mu_A-\mu_B
$$

Point estimate คือ

$$
\bar{x}_A-\bar{x}_B
$$

ต้องกำหนดลำดับของกลุ่มให้ตรงกับคำถาม เพราะการสลับกลุ่มจะทำให้เครื่องหมายของ point estimate และ confidence interval เปลี่ยนไป

โจทย์นี้คำนวณตาม **ข้อ 6 ผลต่างค่าเฉลี่ยของสองกลุ่ม** แต่ต้องเลือกวิธีย่อยตามข้อมูลเกี่ยวกับ population variances

#### 9.3.1 ทราบ population variances

ถ้าทราบ population variances หรือ population standard deviations ของทั้งสองกลุ่ม ให้ใช้ **two-sample z interval**

$$
(\bar{x}_A-\bar{x}_B)
\pm
z_{\alpha/2}
\sqrt{\frac{\sigma_A^2}{n_A}+\frac{\sigma_B^2}{n_B}}
$$

ตัวอย่างโจทย์:

> กลุ่ม A มีนักศึกษา 30 คน คะแนนเฉลี่ย 78 คะแนน และทราบว่า population standard deviation เท่ากับ 10 คะแนน ส่วนกลุ่ม B มีนักศึกษา 35 คน คะแนนเฉลี่ย 72 คะแนน และทราบว่า population standard deviation เท่ากับ 8 คะแนน

เนื่องจากโจทย์ให้ population standard deviations คือ $\sigma_A=10$ และ $\sigma_B=8$ จึงใช้ two-sample z interval

#### R ที่ใช้

```r
%%R
# Two-sample z interval เมื่อทราบ population variances
sigma_a <- 10
sigma_b <- 8

mean_difference <- mean(group_a) - mean(group_b)

standard_error <- sqrt(
  sigma_a^2 / length(group_a) +
  sigma_b^2 / length(group_b)
)

mean_difference + c(-1, 1) *
  qnorm(0.975) * standard_error
```

กรณีนี้ต้องคำนวณจากสูตรโดยตรง เพราะ `t.test()` ใช้ sample variances ไม่ได้ใช้ population variances ที่ทราบค่าอยู่แล้ว

หลักจำคือ:

> ทราบ population variances → ใช้ two-sample z interval และคำนวณจาก `sigma_a` กับ `sigma_b`

---

#### 9.3.2 ไม่ทราบ variances และไม่ได้สมมติว่าเท่ากัน

ถ้าไม่ทราบ population variances และโจทย์ไม่ได้กำหนดให้ variances เท่ากัน ให้ใช้ **Welch interval**

$$
(\bar{x}_A-\bar{x}_B)
\pm
t_{\alpha/2,\nu}
\sqrt{\frac{s_A^2}{n_A}+\frac{s_B^2}{n_B}}
$$

Welch degrees of freedom คำนวณจาก

$$
\nu=
\frac{
(\frac{s_A^2}{n_A}+\frac{s_B^2}{n_B})^2
}{
\frac{(s_A^2/n_A)^2}{n_A-1}
+
\frac{(s_B^2/n_B)^2}{n_B-1}
}
$$

ค่า degrees of freedom จึงขึ้นกับทั้ง $n_A$, $n_B$, $s_A$ และ $s_B$ โดย R จะคำนวณให้โดยอัตโนมัติ

ตัวอย่างโจทย์:

> ต้องการเปรียบเทียบคะแนนของนักศึกษากลุ่ม A และกลุ่ม B ซึ่งเป็นคนละกลุ่มกัน โดยโจทย์ให้ sample standard deviations และไม่ได้ระบุว่า population variances เท่ากัน

กรณีนี้ใช้ Welch interval

#### R ที่ใช้

```r
%%R
# Welch confidence interval
t.test(
  group_a,
  group_b,
  var.equal = FALSE,
  conf.level = 0.95
)
```

เนื่องจาก `var.equal = FALSE` เป็นค่าเริ่มต้นของ `t.test()` ใน R จึงเขียนแบบสั้นได้ว่า

```r
%%R
# Welch confidence interval
t.test(group_a, group_b)
```

หลักจำคือ:

> ไม่ทราบ variances + ไม่ได้สมมติว่าเท่ากัน → ใช้ Welch interval และ `var.equal = FALSE`

---

#### 9.3.3 ไม่ทราบ variances แต่สมมติว่าเท่ากัน

ถ้าไม่ทราบ population variances แต่โจทย์กำหนดให้สมมติว่า variances เท่ากัน ให้ใช้ **pooled-variance interval**

Pooled variance คือ

$$
s_p^2=
\frac{
(n_A-1)s_A^2+(n_B-1)s_B^2
}{
n_A+n_B-2
}
$$

Confidence interval คือ

$$
(\bar{x}_A-\bar{x}_B)
\pm
t_{\alpha/2,n_A+n_B-2}
s_p
\sqrt{\frac{1}{n_A}+\frac{1}{n_B}}
$$

Degrees of freedom คือ

$$
df=n_A+n_B-2
$$

ตัวอย่างโจทย์:

> ต้องการเปรียบเทียบคะแนนของนักศึกษากลุ่ม A และกลุ่ม B ซึ่งเป็นคนละกลุ่มกัน ไม่ทราบ population variances แต่โจทย์กำหนดให้สมมติว่า variances ของสองประชากรเท่ากัน

กรณีนี้ใช้ pooled-variance interval

#### R ที่ใช้

```r
%%R
# Pooled-variance confidence interval
t.test(
  group_a,
  group_b,
  var.equal = TRUE,
  conf.level = 0.95
)
```

หลักจำคือ:

> ไม่ทราบ variances + สมมติว่าเท่ากัน → ใช้ pooled-variance interval และ `var.equal = TRUE`

สรุปความแตกต่างของ R ในข้อ 9.3:

```r
%%R
# ทราบ population variances
# ใช้ two-sample z interval และคำนวณจากสูตรโดยตรง

# ไม่ทราบ variances และไม่ได้สมมติว่าเท่ากัน
t.test(group_a, group_b, var.equal = FALSE)

# ไม่ทราบ variances แต่สมมติว่าเท่ากัน
t.test(group_a, group_b, var.equal = TRUE)
```

---

### 9.4 ค่าต่อเนื่องจากข้อมูลที่จับคู่กัน

ตัวอย่างโจทย์:

> วัดความดันโลหิตของผู้ป่วย 20 คนก่อนและหลังได้รับยา ต้องการสร้าง 95% confidence interval ของการเปลี่ยนแปลงความดันโลหิตเฉลี่ย

แม้จะมีข้อมูลก่อนและหลังสองชุด แต่ข้อมูลทั้งสองชุดมาจากผู้ป่วยคนเดิม จึงไม่ใช่ independent samples

ให้สร้าง difference ของผู้ป่วยแต่ละคนก่อน เช่น

$$
d_i=\text{Before}_i-\text{After}_i
$$

จากนั้นจึงประมาณค่าเฉลี่ยของ differences

$$
\mu_d
$$

ดังนั้นโจทย์นี้ใช้ **paired t interval** โดยคำนวณตาม **ข้อ 7 ค่าเฉลี่ยของข้อมูลที่จับคู่กัน**

$$
\bar{d}
\pm
t_{\alpha/2,n-1}
\frac{s_d}{\sqrt{n}}
$$

#### R ที่ใช้

```r
%%R
# Paired confidence interval
t.test(
  before,
  after,
  paired = TRUE,
  conf.level = 0.95
)
```

R จะคำนวณ difference ตามลำดับเป็น

$$
\text{Before}-\text{After}
$$

ถ้าสลับลำดับตัวแปร เครื่องหมายของค่าเฉลี่ยและ confidence interval จะเปลี่ยนไป

นอกจากการวัดบุคคลเดิมก่อนและหลังแล้ว ข้อมูลยังถือว่าเป็น paired data ได้เมื่อหน่วยตัวอย่างถูกจับคู่กันอย่างมีเหตุผล เช่น ฝาแฝด ผู้ป่วยที่จับคู่ตามอายุ หรือร้านค้าที่จับคู่ตามขนาด

ตัวอย่างอื่นที่ใช้วิธีเดียวกัน ได้แก่ น้ำหนักก่อนและหลังเข้าโปรแกรม คะแนนก่อนและหลังเรียน และยอดขายของร้านเดิมก่อนและหลังทำโปรโมชั่น

หลักจำคือ:

> ค่าต่อเนื่อง + คนเดิมสองครั้งหรือข้อมูลจับคู่ → ใช้ข้อ 7 และ `paired = TRUE`

---

### 9.5 ผลลัพธ์สองแบบจากสองกลุ่มอิสระ

ตัวอย่างโจทย์:

> กลุ่มที่ได้รับยาใหม่มีผู้ป่วยหาย 72 คนจากทั้งหมด 100 คน ส่วนกลุ่มที่ได้รับยามาตรฐานมีผู้ป่วยหาย 60 คนจากทั้งหมด 100 คน จงสร้าง 95% confidence interval ของผลต่างสัดส่วนการหายระหว่างยาใหม่กับยามาตรฐาน

ผลลัพธ์ของผู้ป่วยแต่ละคนมีสองแบบคือ:

- หาย
- ไม่หาย

ผู้ป่วยในกลุ่มยาใหม่กับกลุ่มยามาตรฐานเป็นคนละกลุ่มกัน จึงเป็นข้อมูลสองกลุ่มอิสระ

กำหนดให้กลุ่มยาใหม่เป็นกลุ่ม 1 และกลุ่มยามาตรฐานเป็นกลุ่ม 2

$$
\hat{p}_1=\frac{72}{100}=0.72
$$

$$
\hat{p}_2=\frac{60}{100}=0.60
$$

Point estimate คือ

$$
\hat{p}_1-\hat{p}_2=0.72-0.60=0.12
$$

ดังนั้นโจทย์นี้ใช้ **difference in proportions interval** โดยคำนวณตาม **ข้อ 8 ผลต่างสัดส่วนของสองกลุ่ม**

$$
(\hat{p}_1-\hat{p}_2)
\pm
z_{\alpha/2}
\sqrt{
\frac{\hat{p}_1(1-\hat{p}_1)}{n_1}
+
\frac{\hat{p}_2(1-\hat{p}_2)}{n_2}
}
$$

#### R ที่ใช้

```r
%%R
# Difference in proportions confidence interval
x_1 <- 72
n_1 <- 100
x_2 <- 60
n_2 <- 100

p_1 <- x_1 / n_1
p_2 <- x_2 / n_2

proportion_difference <- p_1 - p_2

standard_error <- sqrt(
  p_1 * (1 - p_1) / n_1 +
  p_2 * (1 - p_2) / n_2
)

proportion_difference + c(-1, 1) *
  qnorm(0.975) * standard_error
```

การกำหนดลำดับกลุ่มต้องตรงกับคำถาม เพราะ code นี้คำนวณ

$$
\hat{p}_1-\hat{p}_2
$$

ถ้าสลับกลุ่ม เครื่องหมายของ point estimate และ confidence interval จะเปลี่ยนไป

ผลต่าง 0.12 หมายความว่า ใน sample กลุ่มยาใหม่มีสัดส่วนผู้ป่วยที่หายสูงกว่ากลุ่มยามาตรฐาน 0.12 หรือ 12 percentage points

ตัวอย่างอื่นที่ใช้วิธีเดียวกัน ได้แก่ เปรียบเทียบสัดส่วนผู้สอบผ่านของสองห้อง สัดส่วนสินค้าชำรุดของสองโรงงาน และสัดส่วนลูกค้าที่ซื้อสินค้าของสองแคมเปญ

หลักจำคือ:

> ผลลัพธ์สองแบบ + สองกลุ่มอิสระ + เปรียบเทียบสัดส่วน → ใช้ข้อ 8 และคำนวณจาก `p_1 - p_2`

---

เมื่ออ่านโจทย์ ให้เขียนโครงสร้างออกมาเป็นประโยคสั้น ๆ ก่อนเลือกสูตร เช่น

> ตัวแปรเป็นค่าต่อเนื่อง มีสองกลุ่ม และเป็นคนละกลุ่มกัน จึงต้องประมาณผลต่างค่าเฉลี่ยของสองประชากร หากไม่ทราบ population variances และไม่ได้สมมติว่าเท่ากัน จะใช้ Welch interval ตามข้อ 6

สรุปคำสั่ง R ที่แตกต่างกันตามโครงสร้างของโจทย์:

```r
%%R
# 1. ค่าเฉลี่ยหนึ่งประชากร
t.test(x)

# 2. สัดส่วนหนึ่งประชากร
p_hat + c(-1, 1) * qnorm(0.975) *
  sqrt(p_hat * (1 - p_hat) / n)

# 3. ค่าเฉลี่ยสองกลุ่มอิสระแบบ Welch
t.test(group_a, group_b, var.equal = FALSE)

# 4. ค่าเฉลี่ยสองกลุ่มอิสระแบบ pooled variance
t.test(group_a, group_b, var.equal = TRUE)

# 5. ข้อมูลจับคู่
t.test(before, after, paired = TRUE)

# 6. ผลต่างสัดส่วนสองกลุ่ม
proportion_difference + c(-1, 1) *
  qnorm(0.975) * standard_error
```

## 10. สิ่งที่กำหนดความกว้างของช่วง

$$
\text{Width}=2\times\text{Critical value}\times SE
$$

Confidence level สูงขึ้นทำให้ critical value ใหญ่ขึ้นและช่วงกว้างขึ้น Sample size ใหญ่ขึ้นทำให้ SE ลดลงและช่วงแคบลง Variability สูงขึ้นทำให้ช่วงกว้างขึ้น

สำหรับ mean มี $SE=s/\sqrt n$ หากต้องการลด SE ลงครึ่งหนึ่ง ต้องเพิ่ม sample size เป็นสี่เท่า CI ที่แคบสะท้อน random uncertainty ต่ำลง แต่คุณภาพของข้อสรุปยังขึ้นกับ sampling design และคุณภาพข้อมูล

## 11. เตรียม Google Colab

รัน cell นี้หนึ่งครั้ง:

~~~python
%load_ext rpy2.ipython
~~~

Lab นี้ใช้ Base R ไม่ต้องติดตั้ง package เพิ่ม:

~~~r
%%R
# ไม่แสดง scientific notation
options(scipen = 999, digits = 4)
~~~

## 12. Exercise 1: Money Spent on Fast Food

โจทย์ให้ยอดใช้จ่ายของลูกค้า 15 คน ต้องการ population mean และไม่ทราบ population SD จึงใช้ one-sample t interval

### เตรียมข้อมูล

~~~r
%%R
food <- c(
  7.42, 6.29, 5.83, 6.50, 8.34,
  9.51, 7.10, 6.80, 5.90, 4.89,
  6.50, 5.52, 7.90, 8.30, 9.60
)
~~~

### รัน R ตามคำถาม

~~~r
%%R
# Point estimate
mean(food)
~~~

~~~r
%%R
# Standard error
sd(food) / sqrt(length(food))
~~~

~~~r
%%R
# Margin of error
qt(0.975, df = length(food) - 1) *
  sd(food) / sqrt(length(food))
~~~

~~~r
%%R
# 95% confidence interval
t.test(food, conf.level = 0.95)$conf.int
~~~

ผลสำคัญ:

~~~text
Mean = 7.0933
SE = 0.3630
Margin of error = 0.7786
95% CI = 6.3147 to 7.8720
~~~

### เขียนตอบข้อสอบ

> จากลูกค้าตัวอย่าง 15 คน ได้ point estimate เท่ากับ 7.0933 ดอลลาร์ มี standard error 0.3630 และ margin of error 0.7786 ดังนั้น 95% confidence interval ของค่าเฉลี่ยยอดใช้จ่ายมื้อกลางวันเท่ากับ 6.3147 ถึง 7.8720 ดอลลาร์ เรามีความเชื่อมั่น 95% ว่าช่วงนี้ครอบคลุม population mean ภายใต้ sampling method และ assumptions ที่กำหนด

## 13. Exercise 2: Complaint Resolution Time

โจทย์มีเวลาปิด complaint 50 รายการ ต้องการ population mean จึงใช้ one-sample t interval ข้อมูลมีค่ามากหลายค่าและเบ้ขวา จึงทำให้ variability และช่วงประมาณกว้าง

### เตรียมข้อมูล

~~~r
%%R
complaints <- c(
  54, 5, 35, 137, 31, 27, 152, 2, 123, 81,
  74, 27, 11, 19, 126, 110, 110, 29, 61, 35,
  94, 31, 26, 5, 12, 4, 165, 32, 29, 28,
  29, 26, 25, 1, 14, 13, 13, 10, 5, 27,
  4, 52, 30, 22, 36, 26, 20, 23, 33, 68
)
~~~

~~~r
%%R
# Point estimate
mean(complaints)
~~~

~~~r
%%R
# 95% confidence interval
t.test(complaints, conf.level = 0.95)$conf.int
~~~

~~~text
Mean = 43.0400 days
95% CI = 31.1247 to 54.9553 days
~~~

### เขียนตอบข้อสอบ

> ค่าเฉลี่ยเวลาปิด complaint จาก sample เท่ากับ 43.04 วัน และ 95% confidence interval ของ population mean เท่ากับ 31.12 ถึง 54.96 วัน เรามีความเชื่อมั่น 95% ว่าช่วงนี้ครอบคลุมค่าเฉลี่ยจำนวนวันตั้งแต่รับ complaint จนแก้ไขเสร็จของ population ที่ศึกษา ขอบบนของ CI เป็นขอบสำหรับ mean ไม่ใช่เวลาสูงสุดของ complaint รายหนึ่ง

## 14. Exercise 3: Flu Shot

พบผู้เป็นไข้หวัด 24 คนจากผู้ได้รับวัคซีน 3,900 คน Outcome เป็น binary จึงใช้ one-proportion interval

~~~r
%%R
# Point estimate
p_hat <- 24 / 3900
print(p_hat)
~~~

~~~r
%%R
# Standard error
se_hat <- sqrt(p_hat * (1 - p_hat) / 3900)
print(se_hat)
~~~

~~~r
%%R
# Margin of error
margin_error <- qnorm(0.975) * se_hat
print(margin_error)
~~~

~~~r
%%R
# Wald confidence interval
c(
  lower = p_hat - margin_error,
  upper = p_hat + margin_error
)
~~~

~~~text
p_hat = 0.0062
SE = 0.0013
Margin of error = 0.0025
95% CI = 0.0037 to 0.0086
~~~

### เขียนตอบข้อสอบ

> Point estimate ของสัดส่วนผู้ได้รับวัคซีนแล้วยังเป็นไข้หวัดเท่ากับ 0.0062 หรือประมาณ 0.62% และ 95% confidence interval เท่ากับ 0.0037 ถึง 0.0086 หรือประมาณ 0.37% ถึง 0.86% เนื่องจากขอบบนต่ำกว่า 1% ข้อมูลจึงสนับสนุนข้อสรุปว่า population proportion ต่ำกว่า 1% ภายใต้วิธีประมาณและ assumptions ที่ใช้

## 15. Exercise 4: Basic Life Support Knowledge

กลุ่ม biological sciences มีผู้รู้วิธีเรียก MEAS 391 จาก 637 คน ส่วนกลุ่ม non-biological มี 306 จาก 564 คน โจทย์ถาม biological minus non-biological:

$$
p_{bio}-p_{nonbio}
$$

~~~r
%%R
# Sample proportions และ point estimate
p_bio <- 391 / 637
p_nonbio <- 306 / 564
diff_p <- p_bio - p_nonbio

print(c(
  p_bio = p_bio,
  p_nonbio = p_nonbio,
  difference = diff_p
))
~~~

~~~r
%%R
# Standard error และ 95% CI
se_diff <- sqrt(
  p_bio * (1 - p_bio) / 637 +
  p_nonbio * (1 - p_nonbio) / 564
)

margin_error <- qnorm(0.975) * se_diff

c(
  lower = diff_p - margin_error,
  upper = diff_p + margin_error
)
~~~

~~~text
p_bio = 0.6138
p_nonbio = 0.5426
Difference = 0.0713
95% CI = 0.0154 to 0.1271
~~~

### อ่านเครื่องหมายให้ตรงลำดับ

กลุ่ม biological sciences มี estimated proportion สูงกว่ากลุ่ม non-biological ประมาณ 7.13 percentage points และช่วงทั้งหมดเป็นบวก

เอกสารเฉลยใส่ non-biological เป็นกลุ่มแรกใน prop.test() จึงรายงาน $p_{nonbio}-p_{bio}$ เป็นช่วงติดลบ นอกจากนี้ continuity correction ทำให้ขอบเขตต่างจากสูตรใน Lecture เล็กน้อย ผลทั้งสองไม่ขัดกันเมื่ออ่านลำดับกลุ่มและวิธีคำนวณให้ชัด

### เขียนตอบข้อสอบ

> Point estimate ของ $p_{bio}-p_{nonbio}$ เท่ากับ 0.0713 หมายความว่าสัดส่วนผู้รู้วิธีเรียก MEAS ในกลุ่ม biological sciences สูงกว่ากลุ่ม non-biological ประมาณ 7.13 percentage points โดย 95% confidence interval เท่ากับ 0.0154 ถึง 0.1271 ช่วงไม่ครอบคลุม 0 จึงมีหลักฐานว่าสัดส่วนของสอง population แตกต่างกัน และทิศทางชี้ว่ากลุ่ม biological sciences สูงกว่า

## 16. Exercise 5: Study Time

นักศึกษาที่วางแผนเรียนต่อกับผู้ที่ไม่วางแผนเป็นคนละกลุ่ม จึงใช้ independent two-sample interval เอกสารเฉลยกำหนด equal variances และใช้ pooled t interval

### เตรียมข้อมูล

~~~r
%%R
plan <- c(
  15, 7, 15, 10, 5, 5, 2, 3, 12, 16, 15,
  37, 8, 14, 10, 18, 3, 25, 15, 5, 5
)

no_plan <- c(6, 8, 15, 6, 5, 14, 10, 10, 12, 5)
~~~

~~~r
%%R
# Point estimate: plan minus no_plan
mean(plan) - mean(no_plan)
~~~

~~~r
%%R
# Pooled t interval ตามเอกสารเฉลย
t.test(
  plan,
  no_plan,
  conf.level = 0.95,
  var.equal = TRUE
)
~~~

~~~text
Mean of plan = 11.6667
Mean of no_plan = 9.1000
Difference = 2.5667 hours
95% CI = -3.1103 to 8.2436 hours
~~~

### เขียนตอบข้อสอบ

> นักศึกษาที่วางแผนเรียนต่อมี sample mean สูงกว่ากลุ่มที่ไม่วางแผน 2.5667 ชั่วโมงต่อสัปดาห์ เมื่อใช้ pooled t interval ได้ 95% confidence interval ของ $\mu_{plan}-\mu_{no\ plan}$ เท่ากับ -3.1103 ถึง 8.2436 ชั่วโมง ช่วงครอบคลุม 0 จึงยังไม่มีหลักฐานเพียงพอว่า population means แตกต่างกันที่ระดับ 0.05 ช่วงยังกว้างและรองรับได้ทั้งค่าลบและค่าบวก จึงไม่ควรสรุปว่าค่าเฉลี่ยเท่ากัน

การใช้ var.equal = TRUE เป็น assumption เพิ่มเติม หากโจทย์ไม่กำหนด equal variances การใช้ Welch method ซึ่งเป็นค่าเริ่มต้นของ t.test() จะเหมาะกว่า

## 17. Exercise 6: Multiple Myeloma

ผู้ป่วย 7 คนถูกวัดก่อนและหลัง stem cell transplant ข้อมูลจึงจับคู่กัน กำหนด:

$$
d_i=before_i-after_i
$$

### เตรียมข้อมูล

~~~r
%%R
before <- c(158, 189, 202, 353, 416, 426, 441)
after <- c(284, 214, 101, 227, 290, 176, 290)
~~~

~~~r
%%R
# Point estimate: before minus after
mean(before - after)
~~~

~~~r
%%R
# Paired t interval
t.test(
  before,
  after,
  paired = TRUE,
  conf.level = 0.95
)
~~~

~~~text
Mean difference = 86.1429
95% CI = -28.2610 to 200.5467
~~~

### เขียนตอบข้อสอบ

> เมื่อกำหนด difference เป็น before minus after ได้ point estimate ของ population mean difference เท่ากับ 86.1429 และ 95% confidence interval เท่ากับ -28.2610 ถึง 200.5467 ช่วงครอบคลุม 0 จึงยังไม่มีหลักฐานเพียงพอว่าค่าเฉลี่ย bone marrow microvessel density ก่อนและหลังแตกต่างกันที่ระดับ 0.05 ช่วงกว้างมากเพราะมีเพียง 7 คู่ จึงยังรองรับได้ทั้งการลดลงและการเพิ่มขึ้นขนาดมาก

paired = TRUE ทำให้ R วิเคราะห์ผลต่างภายในผู้ป่วยแต่ละคน การใช้ independent two-sample method จะละทิ้งโครงสร้างการจับคู่

## 18. รูปแบบการเขียนตอบในข้อสอบ

เมื่อเจอโจทย์ใหม่ ให้เรียงคำตอบดังนี้:

1. ระบุ population parameter และทิศทางของผลต่าง
2. ระบุ one sample, independent groups หรือ paired data
3. เลือก z, one-sample t, Welch, pooled หรือ paired t
4. รายงาน point estimate, SE หรือ margin of errorตามที่โจทย์ถาม
5. รายงาน lower และ upper limits พร้อมหน่วย
6. ตีความถึง population parameter ในบริบท
7. หากเป็นผลต่าง ให้ดูว่าช่วงครอบคลุม 0 หรือไม่
8. ระบุ assumption หรือข้อจำกัดสำคัญ

หาก CI ของผลต่างครอบคลุม 0 ข้อมูลยังไม่ให้หลักฐานเพียงพอของความแตกต่างแบบสองด้านที่ระดับ 0.05 แต่ไม่ได้พิสูจน์ว่าสอง population เท่ากัน หาก CI ไม่ครอบคลุม 0 จะมีหลักฐานของความแตกต่าง และทิศทางอ่านจากเครื่องหมายของช่วง

## 19. สูตรที่ควรหาให้เจอในห้องสอบ

One mean เมื่อไม่ทราบ $\sigma$:

$$
\bar x\mathbin{\pm}
t_{\alpha/2,n-1}\frac{s}{\sqrt n}
$$

One proportion:

$$
\hat p\mathbin{\pm}
z_{\alpha/2}\sqrt{\frac{\hat p(1-\hat p)}{n}}
$$

Independent means แบบ Welch:

$$
(\bar x_1-\bar x_2)
\mathbin{\pm}
t_{\alpha/2,\nu}
\sqrt{\frac{s_1^2}{n_1}+\frac{s_2^2}{n_2}}
$$

Paired means:

$$
\bar d\mathbin{\pm}
t_{\alpha/2,n-1}\frac{s_d}{\sqrt n}
$$

Independent proportions:

$$
(\hat p_1-\hat p_2)
\mathbin{\pm}
z_{\alpha/2}
\sqrt{
\frac{\hat p_1(1-\hat p_1)}{n_1}
+
\frac{\hat p_2(1-\hat p_2)}{n_2}
}
$$

## 20. สรุปความคิดของบท

Confidence interval เริ่มจาก estimate แล้วขยายออกตาม standard error และ critical value จึงรวมทั้งตำแหน่งของค่าประมาณและความไม่แน่นอนจากการสุ่มไว้ในคำตอบเดียว

การเลือกสูตรต้องเริ่มจาก parameter และ study design One mean, one proportion, independent means, paired means และ two proportions มี standard error คนละแบบ เพราะข้อมูลเกิดขึ้นและสัมพันธ์กันคนละโครงสร้าง

> ระบุ parameter → ดูชนิด outcome → ดูจำนวนและความสัมพันธ์ของ samples → เลือก sampling distribution → คำนวณ CI → ตีความในบริบท

## 21. References

1. เอกสารประกอบการสอน DADS6001 Lecture 02: Interval Estimation, Slides 1–24.
2. DADS6001 Lab 02: Exercise - Interval Estimation, 4 pages.
3. DADS6001 Lab 02: Solutions and R Programming Examples - Confidence Interval, 4 pages.
4. Berenson, M. L., Levine, D. M., & Krehbiel, T. C. *Basic Business Statistics: Concepts and Applications*, 12th ed. Pearson.
5. Agresti, A., Franklin, C., & Klingenberg, B. *Statistics: The Art and Science of Learning from Data*, 4th ed. Pearson.
