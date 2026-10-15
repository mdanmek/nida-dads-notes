# DADS6001 Midterm Review: จากข้อมูลหนึ่งชุดสู่การตัดสินใจทางสถิติ

เอกสารนี้รวมเนื้อหาบท 01–04 ให้เป็นเรื่องเดียว เป้าหมายไม่ใช่ท่องว่าแต่ละบทมีสูตรอะไร แต่คือมองโจทย์ใหม่ให้ออกว่า **โจทย์ต้องการรู้ค่าใด ข้อมูลมีโครงสร้างแบบไหน ต้องใช้วิธีใด รัน R อย่างไร และต้องหยิบค่าใดจาก output ไปเขียนตอบ**

ให้ใช้สถานการณ์เดียวเป็นภาพตั้งต้น: โรงพยาบาลต้องการทราบเวลารอของผู้ป่วยทั้งหมด แต่ไม่สามารถจับเวลาผู้ป่วยทุกคนได้ จึงสุ่มผู้ป่วยมาบางส่วน ข้อมูลที่เก็บได้เป็นเพียง sample แต่คำถามต้องการคำตอบเกี่ยวกับ population ช่องว่างระหว่างสองสิ่งนี้คือเหตุผลที่เราต้องเรียน Probability, Sampling Distribution, Confidence Interval, Resampling และ Hypothesis Testing

~~~mermaid
flowchart TD
    A["Population และ parameter ที่อยากรู้"] --> B["สุ่ม Sample"]
    B --> C["คำนวณ Statistic"]
    C --> D["วัด Sampling Uncertainty ด้วย SE"]
    D --> E["CI, Jackknife, Bootstrap หรือ Hypothesis Test"]
~~~

อ่านภาพจากบนลงล่าง เราเริ่มจากคำถามเกี่ยวกับประชากร ใช้ sample สร้างค่าประมาณ แล้วต้องวัดว่าค่าประมาณนั้นเปลี่ยนได้มากเพียงใดเมื่อ sample เปลี่ยน เครื่องมือในบท 02–04 เป็นคำตอบคนละแบบที่สร้างอยู่บนฐานเดียวกันนี้

---

## 1. เรื่องเดียวที่เชื่อมทั้งสี่บท

สมมติสุ่มผู้ป่วย 15 คนแล้วได้เวลารอเฉลี่ย 4.29 นาที

- ค่า 4.29 คือ **sample mean** หรือ statistic ที่คำนวณได้จากข้อมูลชุดนี้
- ค่าที่เราอยากรู้จริงคือ **population mean** หรือ parameter เขียนเป็น $\mu$
- หากสุ่มผู้ป่วยอีก 15 คน sample mean ย่อมเปลี่ยน นี่คือ sampling variability
- การกระจายของ sample mean จาก sample ที่เป็นไปได้ทั้งหมดเรียกว่า sampling distribution
- Standard error หรือ SE สรุปความกว้างของ sampling distribution

เมื่อเข้าใจถึงจุดนี้ เครื่องมือบทต่อไปจะต่อกันเอง:

1. **Confidence Interval** ใช้ estimate และ SE สร้างช่วงค่าที่เป็นไปได้ของ parameter
2. **Jackknife และ Bootstrap** ใช้ข้อมูลเดิมสร้าง resamples เพื่อประมาณ bias, SE หรือ CI เมื่อสูตร classical ไม่สะดวก
3. **Hypothesis Test** ตรวจว่าผลจาก sample ขัดกับค่าที่กำหนดใน $H_0$ มากพอหรือไม่

ทั้งสามเรื่องไม่ได้แยกขาดจากกัน แต่กำลังมอง uncertainty ของ statistic คนละมุม

---

## 2. ก่อนเลือกสูตร ต้องแปลโจทย์เป็นภาษาสถิติ

อ่านโจทย์ครั้งแรกโดยยังไม่กด R แล้วตอบคำถามต่อไปนี้

### 2.1 โจทย์ต้องการกล่าวถึงใคร

กลุ่มทั้งหมดที่ต้องการสรุปคือ **population** ส่วนกลุ่มที่เก็บข้อมูลจริงคือ **sample**

ตัวอย่าง “สุ่มผู้ป่วย 30 คนเพื่อตรวจว่าเวลารอเฉลี่ยของผู้ป่วยทั้งหมดต่ำกว่า 20 นาทีหรือไม่”

- Population: ผู้ป่วยทั้งหมดในขอบเขตที่โจทย์กำหนด
- Sample: ผู้ป่วย 30 คนที่ถูกสุ่ม
- Parameter: population mean waiting time หรือ $\mu$
- Statistic: sample mean waiting time หรือ $\bar{x}$

### 2.2 Outcome เป็นข้อมูลชนิดใด

ถ้าค่าที่วัดเป็นจำนวน เช่น เวลา น้ำหนัก รายได้ หรือคะแนน มักสนใจ **mean** หากผลลัพธ์มีสองสถานะ เช่น ผ่าน/ไม่ผ่าน ป่วย/ไม่ป่วย หรือซื้อ/ไม่ซื้อ มักสนใจ **proportion**

### 2.3 มีหนึ่ง sample หรือสอง samples

- หนึ่ง sample เทียบค่ามาตรฐาน เช่น เวลารอเฉลี่ยเทียบกับ 20 นาที
- สองกลุ่มอิสระ เช่น โรงพยาบาล A เทียบโรงพยาบาล B
- ข้อมูลจับคู่ เช่น คนเดิมก่อนและหลังรักษา

คำว่า “สองชุดข้อมูล” ยังไม่พอให้เลือก independent test ต้องดูว่าค่าทั้งสองชุดมาจากหน่วยทดลองเดียวกันหรือไม่

### 2.4 โจทย์ต้องการประมาณหรือทดสอบ

- “ประมาณ”, “สร้างช่วง”, “95% confidence” → Confidence Interval
- “แตกต่างหรือไม่”, “สูงกว่าไหม”, “มีหลักฐานหรือไม่” → Hypothesis Test
- “ใช้ Jackknife”, “Bootstrap”, “ประมาณ SE ของ median” → Resampling

---

## 3. Random Variable, Distribution และ Probability มีไว้ทำอะไร

ก่อนผู้ป่วยรายถัดไปมาถึง เรายังไม่รู้ว่าเขาจะรอกี่นาที จึงใช้ random variable $X$ แทนเวลารอที่ยังไม่ทราบ ค่า $x=12$ คือค่าที่สังเกตได้จริงหนึ่งค่า

**Probability distribution** อธิบายว่าค่าต่าง ๆ ของ $X$ มีโอกาสเกิดอย่างไร ถ้า $X$ เป็น continuous variable เช่นเวลา Probability ของค่าจุดเดียวเท่ากับศูนย์ สิ่งที่มีความหมายคือพื้นที่ในช่วง เช่น $P(5<X<10)$

Distribution ที่ต้องรู้บทบาทมีดังนี้

- **Binomial**: นับจำนวน successes จากจำนวน trials คงที่ เมื่อแต่ละครั้งมีสองผลลัพธ์ เป็นอิสระ และมี probability of success เท่ากัน
- **Normal**: แบบจำลองต่อเนื่องสมมาตรรอบ mean
- **Student's t**: ใช้กับ mean เมื่อไม่ทราบ population SD และต้องใช้ sample SD แทน
- **Chi-square**: เกิดในการอนุมานเกี่ยวกับ variance และงาน categorical บางประเภท

ประเด็นสอบที่สำคัญไม่ใช่จำชื่ออย่างเดียว แต่ต้องรู้ว่า distribution อธิบาย **ข้อมูลรายหน่วย** หรือ **statistic จากการสุ่ม**

---

## 4. Sampling Distribution และ Standard Error คือหัวใจของวิชา

สมมติเราสุ่มผู้ป่วย 15 คน คำนวณ mean แล้วทำกระบวนการนี้ซ้ำหลายครั้ง แต่ละครั้งจะได้ mean ไม่เท่ากัน การกระจายของ means เหล่านั้นคือ sampling distribution ของ $\bar{X}$

ถ้า observations เป็นอิสระและมาจาก population เดียวกัน:

$$
E(\bar{X})=\mu
$$

$$
SE(\bar{X})=\frac{\sigma}{\sqrt{n}}
$$

ในงานจริงมักไม่ทราบ $\sigma$ จึงประมาณด้วย $s$

$$
SE(\bar{X})=\frac{s}{\sqrt{n}}
$$

ต้องแยกสองคำนี้ให้ได้:

- SD บอกว่าข้อมูลรายคนกระจายจากกันมากเพียงใด
- SE บอกว่า estimate เช่น sample mean จะเปลี่ยนมากเพียงใดเมื่อเปลี่ยน sample

เมื่อ $n$ เพิ่มขึ้น SE ลดลงด้วยอัตรา $1/\sqrt{n}$ ดังนั้นการลด SE ลงครึ่งหนึ่งต้องเพิ่ม sample size ประมาณสี่เท่า อย่างไรก็ตาม sample ใหญ่ลด random error แต่ไม่แก้ selection bias หรือการวัดผิด

### Central Limit Theorem

Central Limit Theorem กล่าวว่า เมื่อ observations เป็นอิสระและ sample ใหญ่พอ sampling distribution ของผลรวมหรือ mean จะเข้าใกล้ Normal แม้ข้อมูลรายคนอาจไม่ Normal

สิ่งที่เข้าใกล้ Normal คือ **distribution ของ sample mean** ไม่ใช่ข้อมูลดิบ และไม่มีเกณฑ์ว่า $n=30$ ใช้ได้กับข้อมูลทุกรูปแบบ หากข้อมูลเบ้รุนแรงหรือมี outliers อาจต้องการ sample ใหญ่กว่านั้น

---

## 5. ตรวจข้อมูลก่อนอนุมาน

การตรวจ Normality ไม่ใช่การกด Shapiro–Wilk test แล้วจบ ต้องดูร่วมกันทั้งการออกแบบข้อมูล กราฟ outliers และ sample size

~~~r
%%R
summary(x)
boxplot(x, horizontal = TRUE)
hist(x)
qqnorm(x)
qqline(x, col = 'red')
shapiro.test(x)
~~~

ให้ดูผลดังนี้

- Boxplot: มี observation ที่ควรตรวจสอบเพิ่มเติมหรือไม่
- Histogram: เบ้ หลายยอด หรือมีหางยาวหรือไม่
- Q–Q plot: จุดโดยรวมอยู่ใกล้เส้นตรงหรือไม่ โดยเฉพาะบริเวณ tails
- Shapiro p-value: ถ้ามากกว่า .05 เขียนว่า “ยังไม่มีหลักฐานต่อต้าน Normality” ไม่ใช่ “พิสูจน์ว่า Normal”

สิ่งที่ต้องตรวจขึ้นกับวิธี:

- One-sample t: ตรวจตัวแปรที่วัด
- Independent t: ตรวจแต่ละกลุ่ม
- Paired t: ตรวจ **differences ภายในคู่**

Random sampling และ independence ต้องพิจารณาจากวิธีเก็บข้อมูล ไม่สามารถพิสูจน์จากกราฟหรือ Shapiro test

---

## 6. Confidence Interval: ค่าประมาณอยู่ในช่วงใด

Confidence interval มีโครงสร้างเดียว:

$$
\text{Estimate} \pm \text{Critical value}\times SE
$$

Estimate บอกตำแหน่งกึ่งกลาง SE บอก sampling uncertainty และ critical value กำหนดว่าต้องขยายออกกี่ SE เพื่อให้วิธีมี confidence level ตามที่ต้องการ

ความหมายของ 95% confidence ไม่ใช่ “ข้อมูล 95% อยู่ในช่วง” แต่หมายถึง หากสุ่ม sample และสร้างช่วงด้วยวิธีเดิมซ้ำจำนวนมาก ประมาณ 95% ของช่วงจะครอบคลุม parameter จริง

### 6.1 ตัวเลขหนึ่ง sample: CI ของ population mean

**โจทย์สั้น:** สุ่มผู้ป่วย 12 คน ต้องการประมาณเวลารอเฉลี่ยของผู้ป่วยทั้งหมด ไม่ทราบ population SD

**มองโจทย์:** Outcome เป็นตัวเลข หนึ่ง sample ต้องการ mean จึงใช้ one-sample t interval

~~~r
%%R
x <- c(12, 15, 9, 20, 18, 11, 14, 16, 10, 13, 17, 12)
t.test(x, conf.level = 0.95)$conf.int
~~~

**ดูอะไร:** Lower และ upper limits พร้อมหน่วย

**เขียนตอบ:** “95% confidence interval ของ population mean waiting time เท่ากับ ... ถึง ... นาที”

### 6.2 Binary outcome หนึ่ง sample: CI ของ population proportion

**โจทย์สั้น:** ผู้ป่วย 24 จาก 3,900 คนเกิดไข้หวัด ต้องการประมาณ population proportion

**มองโจทย์:** Outcome เป็นไข้หวัด/ไม่เป็นไข้หวัด จึงสนใจ proportion ไม่ใช่ mean

~~~r
%%R
p_hat <- 24 / 3900
se <- sqrt(p_hat * (1 - p_hat) / 3900)
p_hat + c(-1, 1) * qnorm(0.975) * se
~~~

**ดูอะไร:** Point estimate และขอบล่าง–ขอบบน แปลงเป็นเปอร์เซ็นต์เมื่อช่วยให้สื่อความหมายง่ายขึ้น

### 6.3 ตัวเลขสองกลุ่มอิสระ: CI ของ difference in means

**โจทย์สั้น:** เปรียบเทียบเวลารอของโรงพยาบาล A กับ B โดยผู้ป่วยเป็นคนละคน

**มองโจทย์:** Numeric outcome, independent groups ต้องกำหนดทิศทาง เช่น A minus B

~~~r
%%R
# Welch interval เป็นค่าเริ่มต้นเมื่อไม่สมมติ equal variances
t.test(group_a, group_b)$conf.int
~~~

ถ้าโจทย์กำหนด equal population variances:

~~~r
%%R
t.test(group_a, group_b, var.equal = TRUE)$conf.int
~~~

**ดูอะไร:** Estimate ของแต่ละกลุ่มและ CI ของ $\mu_A-\mu_B$ ถ้าช่วงครอบคลุม 0 ยังไม่มีหลักฐานของความแตกต่างแบบ two-sided ที่ระดับ .05

### 6.4 คนเดิมก่อน–หลัง: CI ของ mean difference

**โจทย์สั้น:** วัดความดันผู้ป่วยคนเดิมก่อนและหลังรักษา

**มองโจทย์:** เป็น paired data กำหนดลำดับ difference ก่อน เช่น after minus before

~~~r
%%R
t.test(after, before, paired = TRUE)$conf.int
~~~

**ดูอะไร:** Mean difference และ CI ของ mean difference ไม่ใช่ CI ของ before และ after แยกกัน

### 6.5 Binary outcome สองกลุ่ม

**โจทย์สั้น:** กลุ่ม A สำเร็จ 80 จาก 100 คน กลุ่ม B สำเร็จ 65 จาก 100 คน ต้องการเปรียบเทียบ proportions

~~~r
%%R
prop.test(
  x = c(80, 65),
  n = c(100, 100),
  correct = FALSE
)
~~~

**ดูอะไร:** Sample proportions, CI ของ $p_A-p_B$ และลำดับกลุ่ม หากสลับ A กับ B เครื่องหมายของผลต่างและ CI จะสลับ

---

## 7. Jackknife และ Bootstrap: เมื่ออยากเรียนรู้ uncertainty จากข้อมูลเดิม

Classical method สะดวกเมื่อมีสูตรของ SE และ sampling distribution ที่เหมาะสม แต่ถ้าสนใจ median, percentile, correlation หรือ statistic ที่สูตรซับซ้อน เราอาจใช้ resampling

สิ่งที่ต้องแยก:

- Sampling distribution เกิดจากการสุ่ม sample จริงจาก population ซ้ำ
- Resampling distribution เกิดจาก sample จำลองที่สร้างจาก sample เดิม

Resampling พยายามใช้สิ่งหลังประมาณสิ่งแรก ดังนั้นถ้า sample เดิมไม่เป็นตัวแทนหรือมี dependence ที่ไม่ถูกจัดการ ผล resampling ก็รับข้อจำกัดนั้นมาด้วย

### 7.1 Jackknife: ตัดออกทีละหนึ่ง

**โจทย์สั้น:** ต้องการ Jackknife estimate ของ bias และ SE ของ mean fuel efficiency

~~~r
%%R
library(bootstrap)

fuel <- c(26, 23, 21, 23, 19, 29, 15, 26, 19, 26)
jack_mean <- jackknife(fuel, mean)
print(jack_mean)
~~~

**ดูอะไร**

- jack.values: estimate หลังตัด observation แต่ละตัว
- jack.bias: estimated bias
- jack.se: estimated standard error

**เขียนตอบ:** “ใช้ Jackknife ตัดข้อมูลออกทีละหนึ่งค่า ได้ sample mean เท่ากับ 22.7 mpg, estimated bias เท่ากับ 0 และ Jackknife SE เท่ากับ 1.3421 mpg”

Jackknife เหมาะกับ statistic ที่เปลี่ยนอย่างราบรื่น เช่น mean หรือ regression coefficient ถ้าเป็น median หรือ maximum ค่าอาจไม่เปลี่ยนหลายรอบแล้วกระโดดเมื่อบาง observation ถูกตัด Bootstrap มักยืดหยุ่นกว่า

### 7.2 Bootstrap: สุ่มแบบคืนที่หลายรอบ

**โจทย์สั้น:** ต้องการ 95% Bootstrap CI ของ population median

~~~r
%%R
library(boot)

median_stat <- function(data, index) {
  median(data[index])
}

set.seed(11)
boot_median <- boot(x, statistic = median_stat, R = 2000)
print(boot_median)
boot.ci(boot_median, type = c('perc', 'bca'))
~~~

**ดูอะไร**

- original: statistic จาก sample เดิม
- bias: ค่าเฉลี่ยของ Bootstrap estimates ต่างจาก original เท่าใด
- std. error: การกระจายของ Bootstrap estimates
- Percentile หรือ BCa interval: lower และ upper bounds

Bootstrap ต้องสุ่ม **แบบคืนที่** เพราะค่าเดิมต้องปรากฏซ้ำได้และบางค่าไม่ปรากฏในแต่ละรอบ จึงทำให้ statistic เปลี่ยน หากสุ่มครบขนาดเดิมแบบไม่คืนที่ จะได้ข้อมูลชุดเดิมเพียงสลับลำดับและ mean จะไม่เปลี่ยน

จำนวน $R=2000$ คือจำนวน resamples ไม่ใช่จำนวน observations ใหม่ ใช้ set.seed() เพื่อให้ผลทำซ้ำได้

### 7.3 เลือก Classical, Jackknife หรือ Bootstrap

- Mean หนึ่ง sample และ assumptions ใช้ได้ → เริ่มด้วย t interval
- โจทย์ถามผลของการตัด observation, bias หรือ Jackknife SE → Jackknife
- Median, percentile หรือ statistic ที่สูตร SE ซับซ้อน → Bootstrap
- โจทย์สั่งเปรียบเทียบ classical กับ Bootstrap → รันทั้งสอง แล้วเปรียบเทียบขอบเขตและข้อสรุป

อย่าเลือก Bootstrap เพียงเพราะข้อมูลไม่ Normal ต้องดู parameter และ sample size ด้วย ข้อมูลรายคนอาจเบ้ แต่ sampling distribution ของ mean อาจใกล้ Normal จาก CLT

---

## 8. Hypothesis Testing: ข้อมูลขัดกับข้ออ้างมากพอหรือไม่

Hypothesis test เริ่มด้วยการสมมติว่า null hypothesis หรือ $H_0$ จริง แล้วถามว่า ผลที่สังเกตสุดโต่งเพียงใดภายใต้สมมติฐานนั้น

Test statistic มีโครงสร้าง:

$$
\mathrm{Test\ statistic} = \frac{\mathrm{Estimate}-\mathrm{Null\ value}}{\mathrm{SE\ under\ }H_0}
$$

p-value คือ probability ที่จะได้ผลอย่างน้อยสุดโต่งเท่าที่สังเกต เมื่อ $H_0$ จริง

$$
p\mathrm{-value} = \mathrm{P}(\mathrm{result\ at\ least\ as\ extreme\ as\ observed}\mid H_0)
$$

p-value ไม่ใช่ probability ที่ $H_0$ จริง

### 8.1 ทิศทางมาจากคำถาม

| คำในโจทย์ | $H_1$ | alternative ใน R |
|---|---|---|
| แตกต่าง | $\mu \ne \mu_0$ | 'two.sided' |
| ต่ำกว่า | $\mu < \mu_0$ | 'less' |
| สูงกว่า | $\mu > \mu_0$ | 'greater' |

เลือกทิศทางก่อนเห็นข้อมูล ไม่ควรเห็น sample mean แล้วค่อยเลือกหาง

### 8.2 การตัดสินใจ

- p-value $\le \alpha$ → reject $H_0$
- p-value $> \alpha$ → fail to reject $H_0$

Fail to reject ไม่ได้พิสูจน์ว่า $H_0$ จริง ให้เขียนว่า “ยังไม่มีหลักฐานเพียงพอ” ไม่ใช่ “ยอมรับว่าเท่ากัน”

### 8.3 One-sample t test

**โจทย์สั้น:** เวลารอเฉลี่ยต่ำกว่า 5 นาทีหรือไม่

$$
H_0: \mu = 5
$$

$$
H_1: \mu < 5
$$

~~~r
%%R
t.test(waiting_time, mu = 5, alternative = 'less')
~~~

**ดูอะไร:** Mean, t, df, p-value, one-sided CI และ alternative ว่าตรงกับโจทย์

ถ้า p-value = 0.0569 ที่ $\alpha=0.05$ ให้เขียนว่า “fail to reject $H_0$ ยังไม่มีหลักฐานเพียงพอว่า population mean waiting time ต่ำกว่า 5 นาที”

### 8.4 Independent two-sample t test

**โจทย์สั้น:** Mean ของโรงพยาบาล A แตกต่างจาก B หรือไม่ ผู้ป่วยเป็นคนละคน

~~~r
%%R
# Welch test
t.test(group_a, group_b, alternative = 'two.sided')
~~~

ถ้าโจทย์กำหนด equal variances:

~~~r
%%R
# Pooled-variance test
t.test(
  group_a,
  group_b,
  alternative = 'two.sided',
  var.equal = TRUE
)
~~~

**ดูอะไร:** Mean ของแต่ละกลุ่ม ทิศทางของ group A minus group B, t, df, p-value และ CI

### 8.5 Paired t test

**โจทย์สั้น:** น้ำหนักหลังรักษาสูงกว่าก่อนรักษาหรือไม่ ในผู้ป่วยคนเดิม

~~~r
%%R
t.test(
  after,
  before,
  paired = TRUE,
  alternative = 'greater'
)
~~~

R กำลังทดสอบ after minus before ถ้าสลับ argument ทิศทางของ alternative ต้องสลับตาม

**ดูอะไร:** Mean difference, t, df, p-value และ one-sided CI ของ differences

### 8.6 Type I, Type II และ Power

- Type I error: reject $H_0$ ทั้งที่ $H_0$ จริง ควบคุมด้วย $\alpha$
- Type II error: fail to reject $H_0$ ทั้งที่ $H_1$ จริง มี probability เท่ากับ $\beta$
- Power: โอกาสตรวจพบผลที่มีอยู่จริง

$$
\mathrm{Power}=1-\beta
$$

Power มักสูงขึ้นเมื่อ sample size ใหญ่ขึ้น ผลจริงมีขนาดใหญ่ขึ้น หรือข้อมูลมี variability ต่ำลง

---

## 9. ความสัมพันธ์ระหว่าง CI กับ Hypothesis Test

สำหรับ two-sided test ที่ $\alpha=0.05$ และ 95% CI ที่สร้างด้วยวิธีสอดคล้องกัน:

- Null value อยู่นอก CI → reject $H_0$
- Null value อยู่ใน CI → fail to reject $H_0$

ตัวอย่าง CI ของ $\mu_A-\mu_B$ เท่ากับ [-2.1, 4.7] ช่วงครอบคลุม 0 จึงยังไม่มีหลักฐานว่า population means แตกต่างกันแบบ two-sided ที่ระดับ .05

CI ให้ข้อมูลมากกว่าคำว่า significant เพราะแสดงทั้งทิศทาง ขนาดผล และความไม่แน่นอน ส่วน p-value เน้นความเข้ากันได้ของข้อมูลกับ $H_0$

---

## 10. แผนที่เลือกวิธีเมื่อเจอโจทย์ใหม่

| โครงสร้างโจทย์ | เป้าหมาย | วิธีหรือ R หลัก |
|---|---|---|
| Numeric, หนึ่ง sample | ประมาณ mean | `t.test(x)[['conf.int']]` |
| Numeric, หนึ่ง sample | ทดสอบ mean เทียบค่า | t.test(x, mu = value, alternative = ...) |
| Binary, หนึ่ง sample | ประมาณ proportion | Wald formula หรือ prop.test() |
| Numeric, สองกลุ่มอิสระ | ประมาณ/ทดสอบ difference in means | t.test(a, b) |
| Numeric, สองกลุ่มอิสระ และกำหนด equal variances | ประมาณ/ทดสอบ difference in means | t.test(a, b, var.equal = TRUE) |
| Numeric, ก่อน–หลังคนเดิม | ประมาณ/ทดสอบ mean difference | t.test(after, before, paired = TRUE) |
| Binary, สองกลุ่ม | เปรียบเทียบ proportions | prop.test(c(x1,x2), c(n1,n2)) |
| Statistic มีสูตร classical ยาก | ประมาณ SE หรือ CI | Bootstrap |
| ต้องการดูผลของการตัดแต่ละ observation | Bias, SE หรือ influence | Jackknife |

ตารางนี้ใช้หลังจากเข้าใจโครงสร้างข้อมูลแล้ว ไม่ควรเลือกวิธีจากชื่อ function เพียงอย่างเดียว

---

## 11. ตัวอย่างโจทย์รวมแบบสั้น

### ตัวอย่าง A: ค่าเฉลี่ยหนึ่งกลุ่ม

**โจทย์:** น้ำหนักบรรจุเฉลี่ยมากกว่า 500 กรัมหรือไม่

**อ่านโจทย์:** Numeric, one sample, right-sided test

~~~r
%%R
t.test(weight, mu = 500, alternative = 'greater')
~~~

**อ่าน output:** mean, t, df, p-value และ lower confidence bound

**ตอบ:** p-value เทียบกับ $\alpha$ แล้วสรุปถึง population mean

### ตัวอย่าง B: สองกลุ่มอิสระ

**โจทย์:** เวลารอของโรงพยาบาล A กับ B แตกต่างกันหรือไม่

**อ่านโจทย์:** Numeric, independent groups, two-sided Welch test

~~~r
%%R
t.test(wait_a, wait_b)
~~~

**อ่าน output:** mean ของทั้งสองกลุ่ม, difference direction, CI และ p-value

### ตัวอย่าง C: ก่อน–หลัง

**โจทย์:** คะแนนหลังอบรมสูงกว่าก่อนอบรมหรือไม่

**อ่านโจทย์:** Same people, difference = after - before, right-sided paired test

~~~r
%%R
t.test(after, before, paired = TRUE, alternative = 'greater')
~~~

**อ่าน output:** Mean difference และ p-value ของ differences

### ตัวอย่าง D: ประมาณค่าที่สูตรไม่สะดวก

**โจทย์:** ต้องการ 95% CI ของ median รายได้

**อ่านโจทย์:** Parameter คือ median ไม่ใช่ mean จึงใช้ Bootstrap

~~~r
%%R
median_stat <- function(data, index) median(data[index])
boot_result <- boot(income, median_stat, R = 2000)
boot.ci(boot_result, type = 'perc')
~~~

**อ่าน output:** Original median และ percentile CI

### ตัวอย่าง E: ดูความไวต่อ observation

**โจทย์:** ต้องการประเมิน bias และ SE ของ mean เมื่อตัดข้อมูลทีละค่า

~~~r
%%R
jack_result <- jackknife(x, mean)
print(jack_result)
~~~

**อ่าน output:** jack.bias, jack.se และช่วงของ jack.values

---

## 12. Code ตั้งต้นสำหรับ Google Colab

รัน Python cell นี้หนึ่งครั้ง:

~~~python
%load_ext rpy2.ipython
~~~

รัน R setup cell นี้หนึ่งครั้ง:

~~~r
%%R
# ติดตั้งเฉพาะ package ที่ใช้กับ Resampling
if (!requireNamespace('bootstrap', quietly = TRUE)) {
  install.packages('bootstrap', repos = 'https://cloud.r-project.org')
}

if (!requireNamespace('boot', quietly = TRUE)) {
  install.packages('boot', repos = 'https://cloud.r-project.org')
}

library(bootstrap)
library(boot)

# ลด scientific notation
options(scipen = 999, digits = 4)
~~~

Colab อาจไม่แสดง intermediate results เอง ถ้าหนึ่ง cell มีหลายคำสั่ง ให้ใช้ print() กับค่าที่ต้องการเห็น

---

## 13. วิธีอ่าน output ก่อนเขียนคำตอบ

### เมื่อใช้ t.test()

อ่านตามลำดับ:

1. ชื่อ test: one-sample, Welch, pooled หรือ paired
2. Alternative ตรงกับโจทย์หรือไม่
3. Sample estimate หรือ mean difference
4. t และ df
5. p-value
6. Confidence interval

### เมื่อใช้ boot()

อ่าน original, bias และ std. error จากนั้นอ่าน lower และ upper bounds จาก boot.ci()

### เมื่อใช้ jackknife()

อ่าน jack.values, jack.bias และ jack.se

### ตรวจความสมเหตุสมผล

- SE ต้องไม่ติดลบ
- Lower bound ต้องต่ำกว่า upper bound
- Unit ของ mean difference ต้องเป็น unit เดียวกับข้อมูล
- Proportion ต้องอยู่ระหว่าง 0 กับ 1
- Original จาก Bootstrap ควรเท่ากับ statistic ของข้อมูลเดิม
- ถ้า Bootstrap SE เป็น 0 ให้ตรวจว่า statistic function ใช้ data[index]

---

## 14. โครงเขียนตอบข้อสอบ

### 14.1 Confidence Interval

> จาก sample จำนวน ... ได้ point estimate เท่ากับ ... เมื่อใช้ [ชื่อวิธี] ได้ 95% confidence interval เท่ากับ ... ถึง ... [หน่วย] จึงมีความเชื่อมั่น 95% ว่าช่วงนี้ครอบคลุม [population parameter] ภายใต้ sampling method และ assumptions ที่กำหนด

ถ้าเป็น difference ให้ระบุลำดับกลุ่มและดูว่าช่วงครอบคลุม 0 หรือไม่

### 14.2 Hypothesis Test

> กำหนด $H_0$: ... และ $H_1$: ... ใช้ [ชื่อ test] เนื่องจาก [โครงสร้างข้อมูล] ผลได้ [test statistic และ df], p-value = ... เนื่องจาก p-value [น้อยกว่า/มากกว่า] $\alpha$ จึง [reject/fail to reject] $H_0$ และสรุปว่า [ข้อสรุปเกี่ยวกับ population ในบริบทโจทย์]

### 14.3 Bootstrap

> จาก sample ได้ original estimate เท่ากับ ... เมื่อ Bootstrap แบบคืนที่จำนวน ... รอบ ได้ estimated bias เท่ากับ ..., Bootstrap SE เท่ากับ ... และ 95% [ชื่อ interval] เท่ากับ ... ถึง ... จึงประมาณว่า [population parameter] อยู่ในช่วงดังกล่าว ภายใต้ความเป็นตัวแทนและ independence ของ sample

### 14.4 Jackknife

> ใช้ Jackknife ตัด observation ออกทีละหนึ่งแล้วคำนวณ [statistic] ซ้ำ ได้ estimated bias เท่ากับ ... และ Jackknife SE เท่ากับ ... ค่า jack.values แสดงว่า estimate [เสถียร/ไว] ต่อการตัด observation บางค่า

---

## 15. จุดที่ควรจำให้ถูกก่อนเข้าห้องสอบ

- Parameter เป็นค่าของ population ส่วน statistic คำนวณจาก sample
- SD อธิบาย observations ส่วน SE อธิบาย estimate
- CLT กล่าวถึง sampling distribution ของ mean ไม่ได้เปลี่ยนข้อมูลดิบให้เป็น Normal
- 95% CI ประมาณ population parameter ไม่ใช่ช่วงของข้อมูลรายคน
- Paired data ต้องวิเคราะห์ differences ภายในคู่
- Welch เป็นค่าเริ่มต้นของ t.test() สำหรับ independent groups
- ใช้ pooled test เมื่อมี assumption ว่า population variances เท่ากัน
- Bootstrap ต้องสุ่มแบบคืนที่
- Resampling ไม่แก้ sample bias หรือ dependence ที่ออกแบบผิด
- p-value ไม่ใช่ probability ที่ $H_0$ จริง
- Fail to reject ไม่ได้แปลว่าสอง population เท่ากัน
- Statistical significance ไม่ได้บอก practical significance เพียงอย่างเดียว

---

## 16. ลำดับทำข้อสอบที่ใช้ได้กับเกือบทุกโจทย์

1. วงคำที่บอก population และสิ่งที่วัด
2. ระบุ parameter: mean, proportion, difference, median หรือ statistic อื่น
3. ระบุหนึ่ง sample, independent groups หรือ paired data
4. ดูว่าโจทย์ต้องการ estimate, CI, bias, SE หรือ hypothesis test
5. หากเป็น test ให้ตั้ง $H_0$, $H_1$ และเลือกทิศทางก่อนรัน
6. ตรวจ assumptions ที่เกี่ยวข้อง
7. เลือกคำสั่ง R ที่สั้นที่สุดซึ่งตอบคำถาม
8. อ่านเฉพาะค่าที่ต้องใช้ ไม่คัดลอก output ทั้งหมด
9. ตรวจทิศทาง หน่วย ขอบเขต และความสมเหตุสมผล
10. เขียนข้อสรุปกลับไปยัง population ด้วยภาษาของโจทย์

ประโยคเดียวที่เชื่อมทั้งสี่บทคือ:

> เราใช้ statistic จาก sample เรียนรู้ parameter ของ population โดยวัด sampling uncertainty ก่อนสร้างช่วงประมาณหรือประเมินข้ออ้าง

---

## Sources

- 01_introduction.md
- 02_interval_estimation.md
- 03_jackknife_bootstrap.md
- 04_hypothesis_testing.md
