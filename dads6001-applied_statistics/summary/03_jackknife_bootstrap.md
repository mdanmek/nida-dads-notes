# จาก Sample เดียวไปสู่ความไม่แน่นอนด้วย Jackknife และ Bootstrap

> **Course:** DADS6001 Applied Modern Statistical Analysis  
> **Lecture:** 03 Jackknife and Bootstrap Method for Estimation  
> **Sources:** Lecture 03 และ Lab 03 Solution in R  
> **Course navigation:** [Course Overview](00_readme.md) · บทก่อนหน้า [02 Interval Estimation](02_interval_estimation.md) · บทถัดไป [04 Hypothesis Testing](04_hypothesis_testing.md)

ในบทที่ 02 เราสร้าง confidence interval จากโครงสร้าง

$$
\text{Estimate} \pm \text{Critical value}\times SE
$$

ตัวอย่างเช่น หากต้องการช่วงประมาณของ population mean และไม่ทราบ population standard deviation เราใช้ `t.test()` เพราะทฤษฎีบอก sampling distribution ของ sample mean และบอกวิธีหา standard error ไว้แล้ว

แต่สถานการณ์จริงไม่ได้สะดวกเช่นนั้นเสมอไป สมมติว่าเราต้องการ confidence interval ของ median รายได้ ค่า correlation หรือ coefficient จากแบบจำลองที่ซับซ้อน เราอาจไม่รู้สูตรของ standard error หรือ sampling distribution อาจไม่เข้ารูปแบบที่วิธี classical ต้องการ

Jackknife และ Bootstrap แก้ปัญหานี้ด้วยแนวคิดเดียวกันคือ **ใช้ข้อมูลที่มีอยู่สร้างภาพจำลองว่า estimate จะเปลี่ยนอย่างไรหากเราได้ sample อื่น** วิธีเหล่านี้เรียกว่า **resampling methods**

บทนี้จึงไม่ควรเริ่มด้วยการจำสูตรจำนวนมาก สิ่งสำคัญกว่าคือเข้าใจว่า resampling กำลังเลียนแบบอะไร อ่าน output ของ R ให้เป็น และรู้ว่าข้อสรุปใดกล่าวได้จากผลที่ได้

## 1. ปัญหาที่ Resampling เข้ามาแก้

สมมติว่าเราสุ่มครอบครัว 29 ครอบครัวจากผู้พักอาศัยใน public housing แล้วได้ sample mean ของรายได้เท่ากับ 90.24 หน่วย ตัวเลขนี้คำนวณจาก sample ชุดปัจจุบัน หากสุ่มอีก 29 ครอบครัว เราน่าจะได้ mean ที่ต่างออกไป

ถ้าเราสามารถกลับไปสุ่มจาก population จริงซ้ำ 2,000 ครั้ง เราจะได้ sample means 2,000 ค่า การกระจายของค่าเหล่านี้คือ **sampling distribution** และความกว้างของการกระจายนี้บอก standard error ของ sample mean

ปัญหาคือเราไม่มีสิทธิ์ย้อนกลับไปเก็บ sample ใหม่ 2,000 ชุด เรามีเพียง sample 29 ครอบครัวชุดเดียว Resampling จึงใช้ sample นี้แทน population ชั่วคราว แล้วสร้าง sample จำลองหลายชุดจากข้อมูลเดิม

```mermaid
flowchart LR
    A[Sample ที่สังเกตได้] --> B[สร้าง Resamples]
    B --> C[คำนวณ Estimate ทุกชุด]
    C --> D[Resampling Distribution]
    D --> E[ประมาณ Bias, SE และ CI]
```

เริ่มอ่านภาพจากซ้ายไปขวา ลูกศรหมายถึงขั้นตอนการคำนวณ เราไม่ได้เพิ่มข้อมูลใหม่เข้าไป แต่เปลี่ยนวิธีจัดชุดข้อมูลเดิม แล้วดูว่า estimate แปรผันมากเพียงใด

### การแจกแจงสามอย่างที่ต้องแยกให้ออก

**Population distribution** อธิบายค่าของหน่วยทั้งหมดในประชากร เช่น การกระจายรายได้ของทุกครอบครัวใน public housing

**Sampling distribution** อธิบายค่าของ statistic จากการสุ่ม sample จริงซ้ำ เช่น การกระจายของ sample mean หากสุ่มครอบครัว 29 ครอบครัวใหม่หลายครั้ง

**Resampling distribution** อธิบายค่าของ statistic จาก sample จำลองที่สร้างขึ้นจาก sample เดิม เราใช้สิ่งนี้ประมาณ sampling distribution ที่มองไม่เห็น

ความเชื่อมโยงนี้คือหัวใจของทั้งบท หาก sample เดิมเป็นตัวแทนของ population ได้ดี resampling distribution ก็มีโอกาสเลียนแบบ sampling distribution ได้ดี แต่หาก sample เดิมลำเอียง Resampling จะสุ่มซ้ำอยู่ภายในข้อมูลที่ลำเอียงนั้น จึงไม่สามารถสร้างข้อมูลส่วนที่ไม่เคยถูกเก็บขึ้นมาได้

## 2. Bias และ Standard Error หมายถึงอะไร

ก่อนเรียนวิธีทำ ต้องรู้ก่อนว่า output สองคำนี้กำลังตอบคนละคำถาม

**Bias** ถามว่า หากทำกระบวนการสุ่มและประมาณค่าซ้ำเป็นจำนวนมาก estimate มีแนวโน้มสูงหรือต่ำกว่า parameter จริงอย่างเป็นระบบหรือไม่ Bias ที่ใกล้ศูนย์หมายความว่า estimate ไม่มีแนวโน้มเบ้ไปด้านใดด้านหนึ่งมากนัก

**Standard error หรือ SE** ถามว่า estimate เปลี่ยนมากเพียงใดระหว่าง sample ต่าง ๆ SE สูงหมายความว่า estimate ไม่ค่อยเสถียรต่อการเปลี่ยน sample ส่วน SE ต่ำหมายความว่า sample อื่นที่มีลักษณะคล้ายกันน่าจะให้ estimate ใกล้เคียงกัน

ตัวอย่าง Jackknife ของ fuel efficiency ในบทนี้ให้ estimated bias เท่ากับ 0 แต่ SE เท่ากับ 1.3421 ผลนี้มีความหมายว่า sample mean ไม่แสดงแนวโน้มคลาดเคลื่อนอย่างเป็นระบบจากการประเมินแบบ Jackknife แต่ยังมีความไม่แน่นอนจากการสุ่มอยู่ประมาณ 1.3421 mpg Bias เท่ากับศูนย์จึงไม่ได้แปลว่า estimate แม่นยำสมบูรณ์

คำว่า standard deviation กับ standard error ต้องแยกกันเช่นกัน Standard deviation อธิบายว่ารถแต่ละคันหรือครอบครัวแต่ละครอบครัวมีค่าต่างกันเพียงใด ส่วน standard error อธิบายว่า estimate เช่น sample mean จะต่างกันเพียงใดหากเปลี่ยน sample

## 3. Jackknife มองข้อมูลอย่างไร

Jackknife ใช้คำถามง่าย ๆ ว่า

> หากตัด observation แต่ละตัวออกทีละหนึ่ง ค่า estimate จะเปลี่ยนมากเพียงใด

สมมติ sample มี 4 ค่า ได้แก่ 10, 20, 30 และ 40 Jackknife จะสร้างข้อมูล 4 ชุด:

1. ตัด 10 ออก เหลือ 20, 30, 40
2. ตัด 20 ออก เหลือ 10, 30, 40
3. ตัด 30 ออก เหลือ 10, 20, 40
4. ตัด 40 ออก เหลือ 10, 20, 30

จากนั้นคำนวณ statistic ที่สนใจในทุกชุด หาก mean หรือ coefficient เปลี่ยนเพียงเล็กน้อยทุกครั้ง แสดงว่า estimate ค่อนข้างเสถียร หากตัด observation ตัวหนึ่งแล้ว estimate เปลี่ยนมาก Observation ตัวนั้นมีอิทธิพลต่อผลลัพธ์สูง

Jackknife จึงทำสองหน้าที่พร้อมกัน หน้าที่แรกคือประมาณ bias และ standard error หน้าที่ที่สองคือช่วยให้เห็นว่า estimate ไวต่อ observation บางตัวหรือไม่

### Jackknife เหมาะกับกรณีใด

Jackknife ทำงานได้ดีกับ statistic ที่เปลี่ยนอย่างค่อยเป็นค่อยไปเมื่อข้อมูลเปลี่ยนเล็กน้อย เช่น mean หรือ regression coefficient เพราะการตัดข้อมูลทีละตัวทำให้เห็นการเปลี่ยนแปลงของ estimate อย่างต่อเนื่อง

สำหรับ median, percentile หรือ maximum ค่า statistic อาจไม่เปลี่ยนเลยเมื่อตัดหลาย observation แล้วกระโดดทันทีเมื่อตัดบางตัว การเปลี่ยนแบบเป็นขั้นทำให้ Jackknife ประมาณ uncertainty ได้ไม่ดีเท่าวิธีที่ยืดหยุ่นกว่าอย่าง Bootstrap

สิ่งที่ควรจำจึงไม่ใช่สูตร Jackknife variance แต่คือกระบวนการ **ตัดทีละหนึ่ง คำนวณซ้ำ แล้วดูความเปลี่ยนแปลงของ estimate** ในห้องสอบเราสามารถให้ R ทำการคำนวณ และใช้ความเข้าใจนี้อธิบายผล

## 4. Exercise 1: Fuel Efficiency ด้วย Jackknife

Lecture ให้ fuel efficiency ของรถ SUV 10 คัน หน่วยเป็น miles per gallon หรือ mpg:

`26, 23, 21, 23, 19, 29, 15, 26, 19, 26`

โจทย์ต้องการ Jackknife point estimate ของ population mean และ standard error เราจึงกำหนด statistic ที่สนใจเป็น mean แล้วให้ R ตัดข้อมูลออกทีละหนึ่งค่า

### เตรียม Google Colab

รัน cell นี้ใน Python หนึ่งครั้ง:

~~~python
%load_ext rpy2.ipython
~~~

ติดตั้ง package และกำหนดรูปแบบตัวเลขไว้ต้นไฟล์:

~~~r
%%R
# ติดตั้ง package ที่ใช้ในบท
if (!requireNamespace("bootstrap", quietly = TRUE)) {
  install.packages("bootstrap", repos = "https://cloud.r-project.org")
}

if (!requireNamespace("boot", quietly = TRUE)) {
  install.packages("boot", repos = "https://cloud.r-project.org")
}

# เรียกใช้ package และไม่แสดง scientific notation
library(bootstrap)
library(boot)
options(scipen = 999, digits = 4)
~~~

### รัน R เพื่อหาคำตอบ

~~~r
%%R
# ข้อมูล fuel efficiency หน่วย mpg
fuel <- c(26, 23, 21, 23, 19, 29, 15, 26, 19, 26)

# Sample mean จากข้อมูลเดิม
mean(fuel)
~~~

ผลลัพธ์คือ 22.7 mpg ค่านี้เป็น estimate จาก sample เดิม

~~~r
%%R
# ตัดข้อมูลออกทีละหนึ่งค่า แล้วคำนวณ mean ใหม่
jack_mean <- jackknife(fuel, mean)
print(jack_mean)
~~~

ส่วนสำคัญของ output คือ:

~~~text
$jack.se
[1] 1.3421

$jack.bias
[1] 0

$jack.values
[1] 22.3333 22.6667 22.8889 22.6667 23.1111
[6] 22.0000 23.5556 22.3333 23.1111 22.3333
~~~

อ่าน output ตามลำดับดังนี้

`jack.values` คือ means จากข้อมูล 10 ชุดที่ตัดรถออกทีละคัน ค่าเหล่านี้เปลี่ยนจากประมาณ 22.00 ถึง 23.56 จึงแสดงผลกระทบของการตัดรถแต่ละคัน

`jack.bias = 0` หมายความว่า Jackknife ไม่พบ estimated bias ของ sample mean ในตัวอย่างนี้

`jack.se = 1.3421` หมายความว่า estimated standard error ของ sample mean เท่ากับประมาณ 1.3421 mpg ค่านี้อธิบายความไม่แน่นอนของ mean ไม่ใช่ความแตกต่างระหว่างรถรายคัน

หา bias-corrected estimate ได้ด้วย:

~~~r
%%R
# ค่าประมาณหลังหัก estimated bias
mean(fuel) - jack_mean$jack.bias
~~~

ผลยังเป็น 22.7 mpg เพราะ estimated bias เท่ากับศูนย์

### เขียนตอบข้อสอบ

> ใช้ Jackknife โดยตัดข้อมูลรถออกทีละหนึ่งคันจาก sample ขนาด 10 แล้วคำนวณ mean ใหม่ทุกครั้ง ผลได้ sample mean เท่ากับ 22.7 mpg, estimated bias เท่ากับ 0 และ Jackknife standard error เท่ากับ 1.3421 mpg ดังนั้น bias-corrected estimate ยังคงเท่ากับ 22.7 mpg ส่วนค่า SE แสดงว่า estimate ยังมีความไม่แน่นอนจากการสุ่ม แม้ estimated bias จะเป็นศูนย์

### หากโจทย์เปลี่ยนไป

ถ้าโจทย์ถาม median แทน mean เราเปลี่ยนเพียง statistic ที่ส่งให้ `jackknife()`:

~~~r
%%R
# Jackknife median
jackknife(fuel, median)
~~~

อย่างไรก็ตาม median เปลี่ยนเป็นขั้นเมื่อ observation บางตัวถูกตัด จึงควรระวังว่าค่า Jackknife SE อาจไม่เสถียร และ Bootstrap มักเหมาะกว่าสำหรับ statistic ลักษณะนี้

## 5. Bootstrap มองข้อมูลอย่างไร

Bootstrap ใช้แนวคิดต่างจาก Jackknife เล็กน้อย แทนที่จะตัดข้อมูลออกทีละหนึ่งค่า Bootstrap จะสุ่ม observation จาก sample เดิม **แบบคืนที่** จนครบขนาด sample เดิม แล้วทำซ้ำหลายรอบ

สมมติ sample เดิมยังเป็น 10, 20, 30 และ 40 Bootstrap sample ขนาด 4 อาจเป็น:

- 10, 10, 30, 40
- 20, 20, 20, 40
- 10, 30, 40, 40

ค่าเดิมปรากฏซ้ำได้ และบางค่าอาจไม่ปรากฏในรอบหนึ่ง เพราะทุกครั้งที่หยิบค่าออกมา เราคืนค่านั้นกลับก่อนสุ่มครั้งถัดไป คุณสมบัตินี้ทำให้แต่ละ Bootstrap sample แตกต่างกันและทำให้ statistic เปลี่ยนไป

หากสุ่มครบ 4 ค่าแบบไม่คืนที่ ทุกชุดจะมี 10, 20, 30 และ 40 เหมือนเดิม เพียงสลับลำดับ Mean จึงไม่เปลี่ยนและเราไม่สามารถเรียนรู้ความไม่แน่นอนของ mean ได้

เมื่อทำซ้ำ 2,000 รอบ เราจะได้ Bootstrap estimates 2,000 ค่า การกระจายของค่าเหล่านี้ใช้ประมาณ bias, standard error และ confidence interval

จำนวน 2,000 รอบหมายถึงจำนวนครั้งที่คอมพิวเตอร์สุ่มจาก sample เดิม ไม่ได้หมายความว่าเรามี observations 2,000 ราย และไม่ได้ทำให้ sample เดิมเป็นตัวแทนของ population มากขึ้น

## 6. Confidence Interval จาก Bootstrap

R ใน Lecture รายงาน confidence interval สามแบบ เราไม่จำเป็นต้องจำสูตรของทุกแบบ แต่ควรรู้ว่าขอบเขตแต่ละแบบมาจากไหนและควรอธิบายอย่างไร

**Normal interval** ใช้ Bootstrap standard error แล้วสร้างช่วงแบบสมมาตรรอบ estimate หลักคิดใกล้กับ classical interval จึงเหมาะเมื่อ Bootstrap distribution ใกล้สมมาตร

**Percentile interval** เรียง Bootstrap estimates แล้วใช้ percentile ที่ 2.5 และ 97.5 เป็นขอบเขตของ 95% CI วิธีนี้อ่านตรงไปตรงมาว่า estimates ส่วนกลาง 95% อยู่ระหว่างค่าใด และช่วงไม่จำเป็นต้องสมมาตร

**BCa interval** ย่อมาจาก Bias-Corrected and Accelerated interval วิธีนี้ปรับทั้ง bias และความไม่สมมาตรของ resampling distribution จึงมักใช้เมื่อ distribution ไม่สมมาตร แต่การคำนวณภายในซับซ้อนและให้ R จัดการได้

เมื่อเขียนตอบข้อสอบต้องระบุชื่อวิธี เช่น “95% Bootstrap percentile confidence interval” เพราะ Normal, Percentile และ BCa สามารถให้ขอบเขตต่างกันเล็กน้อย

### R ต้องรู้อะไรจึงจะ Bootstrap ได้

ฟังก์ชัน `boot()` ต้องได้รับข้อมูล statistic function และจำนวนรอบ

~~~r
mean_stat <- function(data, index) {
  mean(data[index])
}
~~~

`data` คือข้อมูลเดิม ส่วน `index` คือตำแหน่งที่ R สุ่มขึ้นมาในแต่ละรอบ คำสั่ง `data[index]` จึงสร้าง Bootstrap sample ของรอบนั้น แล้ว `mean()` คำนวณ statistic ที่ต้องการ

หากเขียน `mean(data)` โดยไม่ใช้ `index` ทุก replicate จะคำนวณจากข้อมูลเดิม Mean จะเหมือนกันทุกครั้งและ Bootstrap SE จะเป็นศูนย์ นี่เป็นจุดที่ต้องตรวจทันทีเมื่อเห็น output ผิดปกติ

## 7. Exercise 2: Family Income

โจทย์สำรวจ annual family income ของ 29 ครอบครัวใน public housing ที่ Chicago หน่วยเป็นร้อยดอลลาร์ ต้องการเปรียบเทียบ classical t interval กับ Bootstrap interval ของ population mean

ขั้นแรกต้องมองให้ออกว่าโจทย์ถาม **mean ของข้อมูลเชิงปริมาณหนึ่ง sample** ดังนั้น classical method ใช้ one-sample t interval ส่วน Bootstrap จะจำลอง sampling distribution ของ sample mean จากข้อมูลเดิม

### เตรียมข้อมูลและดูรูปร่าง

~~~r
%%R
# รายได้ต่อปี หน่วยเป็นร้อยดอลลาร์
family_income <- c(
  90, 77, 100, 83, 64, 78, 92, 73, 122, 96,
  60, 85, 86, 108, 70, 139, 56, 94, 84, 111,
  93, 120, 70, 92, 100, 124, 59, 112, 79
)

boxplot(
  family_income,
  main = "Annual Family Income",
  ylab = "Hundreds of Dollars"
)
~~~

Boxplot ช่วยให้เห็นตำแหน่งกึ่งกลาง การกระจาย และค่าด้านบนที่ค่อนข้างสูง เราใช้กราฟประเมินว่าข้อมูลมีความเบ้หรือ outlier รุนแรงหรือไม่ แต่กราฟจาก sample ไม่ได้พิสูจน์รูปร่างของ population อย่างแน่นอน

### Classical t interval

~~~r
%%R
# Point estimates
print(mean(family_income))
print(sd(family_income))
~~~

~~~text
Mean = 90.2414
SD = 20.9926
~~~

Mean เท่ากับ 90.2414 ร้อยดอลลาร์ หรือประมาณ 9,024.14 ดอลลาร์ ส่วน SD อธิบายความแตกต่างของรายได้ระหว่างครอบครัวใน sample

~~~r
%%R
# Classical 95% confidence interval ของ population mean
t.test(family_income, conf.level = 0.95)
~~~

ส่วนที่ใช้ตอบคำถามคือ:

~~~text
mean of x = 90.2414
df = 28
95 percent confidence interval:
82.2562 98.2265
~~~

### Bootstrap interval

~~~r
%%R
# ฟังก์ชันสำหรับคำนวณ mean จาก Bootstrap sample
mean_stat <- function(data, index) {
  mean(data[index])
}

# สุ่มแบบคืนที่ 2,000 รอบ
set.seed(11)
boot_family <- boot(
  data = family_income,
  statistic = mean_stat,
  R = 2000
)

print(boot_family)
~~~

ผลสำคัญจาก `boot_family` คือ:

~~~text
original = 90.2414
bias = -0.0808
std. error = 3.9360
~~~

`original` คือ sample mean จากข้อมูลเดิม ไม่ใช่ค่าเฉลี่ยของ Bootstrap samples

`bias = -0.0808` มีขนาดเล็กเมื่อเทียบกับ mean 90.2414 จึงไม่พบ estimated bias ที่มีขนาดสำคัญในตัวอย่างนี้

`std. error = 3.9360` คือ standard deviation ของ Bootstrap means 2,000 ค่า จึงบอกความไม่แน่นอนของ sample mean

หา confidence intervals ด้วย:

~~~r
%%R
# แสดง Bootstrap confidence intervals สามวิธี
boot.ci(
  boot.out = boot_family,
  conf = 0.95,
  type = c("norm", "perc", "bca")
)
~~~

ผลจากเอกสารเฉลย:

~~~text
Normal      (82.61, 98.04)
Percentile  (82.52, 97.90)
BCa         (82.90, 98.33)
~~~

ผลอาจต่างเล็กน้อยหากใช้ seed จำนวน replicates หรือ R version ต่างกัน แต่ข้อสรุปควรใกล้เคียงกัน

### เปรียบเทียบผลอย่างมีเหตุผล

Classical t interval เท่ากับ 82.2562 ถึง 98.2265 ส่วน Bootstrap percentile interval เท่ากับ 82.52 ถึง 97.90 ช่วงทั้งสองใกล้เคียงกันมาก แสดงว่าสำหรับข้อมูลชุดนี้ วิธี classical และ Bootstrap ประเมินความไม่แน่นอนของ population mean สอดคล้องกัน

การที่ช่วงใกล้กันไม่ได้พิสูจน์ว่าประชากรเป็น Normal สิ่งที่กล่าวได้คือ ภายใต้ sample นี้และ parameter ที่สนใจคือ mean การเปลี่ยนวิธีประมาณไม่ได้ทำให้ข้อสรุปต่างกันอย่างมีสาระ

### เขียนตอบข้อสอบ

> จากครอบครัวตัวอย่าง 29 ครอบครัว ได้ sample mean ของ annual income เท่ากับ 90.2414 ร้อยดอลลาร์ Classical 95% t interval เท่ากับ 82.2562 ถึง 98.2265 ร้อยดอลลาร์ เมื่อใช้ Bootstrap แบบคืนที่จำนวน 2,000 รอบ ได้ Bootstrap SE เท่ากับ 3.9360 และ 95% percentile interval เท่ากับ 82.52 ถึง 97.90 ร้อยดอลลาร์ ช่วงจากสองวิธีใกล้เคียงกัน จึงให้ข้อสรุปสอดคล้องกันเกี่ยวกับ population mean ทั้งนี้ข้อสรุปยังขึ้นกับการเป็นตัวแทนของ sample และความเป็นอิสระของ observations

## 8. Exercise 3: ข้อมูลเบ้ขวา

Exercise 3 มีค่าขนาดใหญ่หลายค่า เช่น 110, 123, 126, 137, 152 และ 165 ขณะที่ค่าจำนวนมากอยู่ต่ำกว่าช่วงดังกล่าว Sample จึงมีลักษณะเบ้ขวาและมี upper tail ยาว

โจทย์นี้สำคัญเพราะทดสอบว่าเราเลือกวิธีจากความเข้าใจได้หรือไม่ ข้อมูลดิบไม่ Normal อย่างชัดเจน แต่ parameter ที่สนใจคือ **population mean** และ sample size เท่ากับ 50 เราจึงเปรียบเทียบ classical t interval กับ Bootstrap interval แล้วดูว่าข้อสรุปต่างกันหรือไม่ แทนที่จะตัดสินจากคำว่า “เบ้” เพียงคำเดียว

### ความไม่สอดคล้องในเอกสารต้นฉบับ

Lecture ระบุ sample size เท่ากับ 50 แต่รายการบนสไลด์มี 49 ค่าและเริ่มด้วย 5 ส่วนไฟล์เฉลย R เพิ่มค่า 54 ไว้หน้าสุด ทำให้ครบ 50 ค่าและได้ mean เท่ากับ 43.04 ตาม output

ตัวอย่างต่อไปนี้ใช้ข้อมูล 50 ค่าจากไฟล์เฉลย R เพื่อให้ผลคำนวณตรงกับเอกสารเฉลย

~~~r
%%R
# ข้อมูล 50 ค่าตามไฟล์เฉลย R
x <- c(
  54, 5, 35, 137, 31, 27, 152, 2, 123, 81,
  74, 27, 11, 19, 126, 110, 110, 29, 61, 35,
  94, 31, 26, 5, 12, 4, 165, 32, 29, 28,
  29, 26, 25, 1, 14, 13, 13, 10, 5, 27,
  4, 52, 30, 22, 36, 26, 20, 23, 33, 68
)

boxplot(x, main = "Exercise 3 Data", ylab = "Observed Value")
~~~

### Classical t interval

~~~r
%%R
# Sample mean และ Classical 95% CI
print(mean(x))
t.test(x, conf.level = 0.95)
~~~

ผลสำคัญ:

~~~text
Mean = 43.0400
df = 49
95% CI = 31.1248 to 54.9553
~~~

### Bootstrap interval

ใช้ `mean_stat` เดิมได้ เพราะ statistic ที่ต้องการยังเป็น mean

~~~r
%%R
# Bootstrap sample mean จำนวน 2,000 รอบ
set.seed(11)
boot_x <- boot(
  data = x,
  statistic = mean_stat,
  R = 2000
)

print(boot_x)
~~~

~~~text
original = 43.0400
bias = 0.0405
std. error = 5.6983
~~~

~~~r
%%R
# Bootstrap confidence intervals ของข้อมูล x
boot.ci(
  boot.out = boot_x,
  conf = 0.95,
  type = c("norm", "perc", "bca")
)
~~~

ผลจากเอกสารเฉลย:

~~~text
Normal      (31.83, 54.17)
Percentile  (32.32, 54.68)
BCa         (32.81, 55.12)
~~~

Classical interval เท่ากับ 31.1248 ถึง 54.9553 ส่วน Bootstrap percentile interval เท่ากับ 32.32 ถึง 54.68 แม้ข้อมูลดิบจะเบ้ขวา แต่ช่วงทั้งสองยังใกล้กัน เหตุผลหนึ่งคือเรากำลังประมาณ mean จาก sample ขนาด 50 ซึ่ง sampling distribution ของ mean มักสมมาตรกว่าการกระจายของข้อมูลรายตัว

ผลนี้ไม่ได้หมายความว่าความเบ้และ extreme values ไม่มีผล ค่าเหล่านี้ยังดึง mean และเพิ่ม SE จึงทำให้ interval กว้าง เราเพียงพบว่าในข้อมูลชุดนี้ Classical และ Bootstrap ไม่ได้ให้ข้อสรุปต่างกันมาก

### เขียนตอบข้อสอบ

> ข้อมูล 50 ค่ามีลักษณะเบ้ขวาและมีค่าด้านบนสูงหลายค่า Sample mean เท่ากับ 43.04 Classical 95% t interval เท่ากับ 31.1248 ถึง 54.9553 เมื่อใช้ Bootstrap แบบคืนที่ 2,000 รอบ ได้ Bootstrap SE เท่ากับ 5.6983 และ 95% percentile interval เท่ากับ 32.32 ถึง 54.68 ช่วงจากสองวิธีใกล้เคียงกัน จึงให้ข้อสรุปสอดคล้องกันเกี่ยวกับ population mean อย่างไรก็ตาม ค่าด้านบนสูงทำให้ variability และความกว้างของช่วงเพิ่มขึ้น

## 9. เลือก Jackknife, Bootstrap หรือ Classical Method

อย่าเริ่มจากถามว่า “จำสูตรไหนได้” ให้เริ่มจากถามว่า **โจทย์ต้องการประมาณอะไร และสูตร classical สำหรับสิ่งนั้นใช้ง่ายและสมเหตุสมผลหรือไม่**

ถ้าโจทย์ถาม population mean ของหนึ่ง sample และ assumptions ใช้ได้ `t.test()` เป็นคำตอบที่ตรงและง่ายที่สุด การใช้ Bootstrap เพิ่มอาจมีประโยชน์เมื่อโจทย์สั่งให้เปรียบเทียบ หรือเมื่ออยากตรวจว่าข้อสรุปไวต่อวิธีประมาณหรือไม่

ถ้าโจทย์ต้องการประเมินว่า observation ใดมีอิทธิพลต่อ estimate หรือถาม bias และ SE ด้วยวิธีตัดข้อมูลทีละหนึ่ง ให้คิดถึง Jackknife

ถ้าโจทย์ถาม median, percentile, correlation หรือ statistic ที่สูตร SE ซับซ้อน ให้คิดถึง Bootstrap เพราะเปลี่ยน statistic function ได้โดยไม่ต้องหา sampling formula ใหม่ทั้งหมด

ตัวอย่างเช่น หากต้องการ 95% CI ของ median รายได้ ให้เปลี่ยน statistic function เท่านั้น:

~~~r
%%R
# Bootstrap median
median_stat <- function(data, index) {
  median(data[index])
}

set.seed(11)
boot_median <- boot(
  data = family_income,
  statistic = median_stat,
  R = 2000
)

boot.ci(boot_median, conf = 0.95, type = c("perc", "bca"))
~~~

ในกรณีนี้ `t.test()` ไม่ใช่เครื่องมือสำหรับ confidence interval ของ median การมอง parameter ก่อนจึงช่วยเลือกวิธีได้ถูกแม้โจทย์เปลี่ยนบริบท

## 10. สิ่งที่ Resampling ทำไม่ได้

Resampling ประมาณความไม่แน่นอนจากข้อมูลที่มีอยู่ จึงรับข้อจำกัดของ sample เดิมมาด้วย

หากเก็บข้อมูลเฉพาะครอบครัวที่ตอบแบบสอบถามง่าย Bootstrap จะสุ่มซ้ำจากครอบครัวเหล่านั้นและไม่สามารถสร้างกลุ่มที่ขาดหายขึ้นมาได้

หาก observations ไม่เป็นอิสระ เช่น วัดผู้ป่วยคนเดิมหลายครั้ง การสุ่มแต่ละ row แยกกันจะทำลายความสัมพันธ์ภายในคน ต้อง resample เป็นหน่วยผู้ป่วยหรือใช้วิธีที่รักษาโครงสร้างการพึ่งพา

หาก sample เล็กมาก empirical distribution มีข้อมูลให้เลียนแบบน้อย Bootstrap distribution อาจไม่สะท้อน population tail หรือเหตุการณ์หายากได้ดี

หาก statistic ไวต่อ outlier มาก Bootstrap samples ที่สุ่ม outlier ซ้ำหลายครั้งอาจให้ estimates ที่กระจายกว้าง นี่ไม่ใช่ข้อผิดพลาดของโปรแกรม แต่เป็นสัญญาณว่า estimate ไวต่อข้อมูลบางค่า

ดังนั้นการได้ R output ไม่ได้ยืนยันว่าข้อสรุปถูกต้อง เราต้องตรวจ sampling design ความเป็นอิสระ รูปร่างข้อมูล outliers และความหมายของ statistic ร่วมด้วย

## 11. วิธีอ่านโจทย์ใหม่ในห้องสอบ

เมื่อเจอโจทย์ที่ไม่เหมือนตัวอย่าง ให้ทำตามลำดับนี้

1. ระบุ population และ parameter ที่โจทย์ถาม เช่น population mean, median หรือ correlation
2. ระบุ estimate จาก sample เช่น sample mean หรือ sample median
3. ตรวจว่า observations เป็นอิสระหรือมีโครงสร้างจับคู่ กลุ่ม หรือเวลา
4. เลือกวิธี Classical, Jackknife หรือ Bootstrap จาก parameter และ assumptions
5. รัน R เพื่อหา estimate, bias, SE หรือ CI ตามคำถาม
6. อ่านหน่วยและทิศทางของผลก่อนเขียนตอบ
7. เขียนข้อสรุปกลับไปยัง population พร้อมชื่อวิธีและข้อจำกัดที่สำคัญ

โครงสร้างคำตอบที่ใช้ได้บ่อยคือ:

> จาก sample จำนวน ... ได้ estimate เท่ากับ ... เมื่อใช้ [ชื่อวิธี] ได้ standard error เท่ากับ ... และ 95% confidence interval เท่ากับ ... ถึง ... ดังนั้นเรามีความเชื่อมั่น 95% ว่าช่วงดังกล่าวครอบคลุม [parameter ของ population] ภายใต้ assumptions เรื่อง sampling และความเป็นอิสระของ observations

หากโจทย์ให้เปรียบเทียบสองวิธี ให้เพิ่มว่าช่วงใกล้กันหรือแตกต่างกันตรงไหน แล้วอธิบายผลต่อข้อสรุป อย่าหยุดเพียงรายงานตัวเลขสองช่วง

## 12. อ่าน Output ของ R ให้เป็น

เมื่อใช้ `boot()` ให้หา 3 ค่าก่อน:

- `original` คือ estimate จาก sample เดิม
- `bias` คือ estimated difference ระหว่างค่าเฉลี่ยของ Bootstrap estimates กับ original estimate
- `std. error` คือการกระจายของ Bootstrap estimates

เมื่อใช้ `boot.ci()` ให้ดู:

- ระดับ confidence เช่น 95%
- ชื่อ interval เช่น Normal, Percentile หรือ BCa
- lower และ upper bounds

เมื่อใช้ `jackknife()` ให้ดู:

- `jack.values` เพื่อเห็น estimates หลังตัดข้อมูลทีละหนึ่ง
- `jack.bias` เพื่อประเมิน systematic bias
- `jack.se` เพื่อประเมินความไม่แน่นอนของ estimate

ตรวจความสมเหตุสมผลทุกครั้ง เช่น CI ของรายได้ไม่ควรสลับขอบล่างกับขอบบน SE ต้องไม่ติดลบ และ `original` ควรเท่ากับ statistic ที่คำนวณจากข้อมูลเดิม

## 13. จุดผิดพลาดที่พบได้บ่อยใน R

### Bootstrap SE เท่ากับศูนย์

ตรวจว่า statistic function ใช้ `data[index]` หากใช้ข้อมูลเดิมโดยไม่ใช้ index ทุก replicate จะเหมือนกัน

### ผลเปลี่ยนเมื่อรันใหม่

Bootstrap มีการสุ่ม ให้ใช้ `set.seed()` ก่อน `boot()` เพื่อทำซ้ำผลเดิม และรายงานจำนวน replicates

### ได้ CI ของข้อมูลผิดชุด

ส่ง object ให้ `boot.ci()` ให้ตรงกับ exercise เช่น `boot_family` สำหรับ Family Income และ `boot_x` สำหรับ Exercise 3 การใช้ object เก่าจะให้ output ที่ดูถูกต้องแต่ตอบข้อมูลผิดชุด

### R หา `boot()` หรือ `jackknife()` ไม่พบ

ตรวจว่าเรียก `library(boot)` และ `library(bootstrap)` แล้ว หรือใช้ `boot::boot()` และ `bootstrap::jackknife()`

### ตัวเลขออกมาเป็น e notation

ตั้งค่าต้นไฟล์ด้วย:

~~~r
options(scipen = 999, digits = 4)
~~~

`scipen` ลดการใช้ scientific notation ส่วน `digits` กำหนดจำนวน significant digits ที่ R ใช้แสดงผล ไม่ใช่จำนวนตำแหน่งทศนิยมตายตัว หากต้องการแสดงทศนิยม 4 ตำแหน่งเฉพาะผลหนึ่งชุด ใช้ `round(x, 4)`

## 14. Likely Exam Focus

จาก Lecture และ Exercises ประเด็นที่ควรตอบได้มีดังนี้

### อธิบายความต่างระหว่าง Jackknife กับ Bootstrap

> Jackknife สร้าง resamples โดยตัด observation ออกทีละหนึ่งค่า จึงได้จำนวน resamples เท่ากับ sample size และไม่มี randomness ส่วน Bootstrap สุ่ม observations จาก sample เดิมแบบคืนที่ให้ได้ขนาดเท่าเดิม แล้วทำซ้ำจำนวนมาก Jackknife เหมาะกับการประเมิน bias, SE และอิทธิพลของ observation สำหรับ statistic ที่เปลี่ยนอย่างราบรื่น ส่วน Bootstrap ยืดหยุ่นกว่าในการประมาณ sampling distribution, SE และ confidence interval ของ statistic ที่หลากหลาย

### อธิบายเหตุผลที่ Bootstrap ต้องสุ่มแบบคืนที่

> การสุ่มแบบคืนที่ทำให้ observation เดิมปรากฏซ้ำได้และบาง observation ไม่ปรากฏในแต่ละ Bootstrap sample จึงทำให้ statistic เปลี่ยนระหว่าง replicates หากสุ่มครบขนาดเดิมแบบไม่คืนที่ จะได้ข้อมูลชุดเดิมเพียงสลับลำดับและ statistic เช่น mean จะไม่เปลี่ยน จึงไม่สามารถประมาณ sampling variability ได้

### อ่านผล Bootstrap แล้วเขียนข้อสรุป

หาก output ให้ `original = 90.2414`, `bias = -0.0808`, `SE = 3.9360` และ percentile CI เท่ากับ 82.52 ถึง 97.90 คำตอบควรเชื่อมตัวเลขกับบริบท:

> Sample mean เท่ากับ 90.2414 ร้อยดอลลาร์ Estimated bias มีขนาดเล็กเท่ากับ -0.0808 และ Bootstrap SE เท่ากับ 3.9360 ร้อยดอลลาร์ โดย 95% Bootstrap percentile CI ของ population mean เท่ากับ 82.52 ถึง 97.90 ร้อยดอลลาร์

### เลือกวิธีเมื่อโจทย์เปลี่ยน

หากโจทย์ถาม mean ของหนึ่ง sample และ assumptions ใช้ได้ ให้เริ่มจาก one-sample t interval หากถาม SE หรืออิทธิพลจากการตัด observation ให้ใช้ Jackknife หากถาม median หรือ statistic ที่สูตร classical ซับซ้อน ให้ใช้ Bootstrap และกำหนด statistic function ให้ตรงกับ parameter

## 15. สรุปความคิดของบท

บทที่ 01 สอนว่า statistic เปลี่ยนไปตาม sample และบทที่ 02 ใช้ standard error สร้าง confidence interval บทนี้ตอบคำถามต่อว่า หากสูตรของ standard error หรือ sampling distribution ไม่สะดวกใช้ เราจะเรียนรู้ความไม่แน่นอนจาก sample ที่มีอยู่ได้อย่างไร

Jackknife ตัดข้อมูลออกทีละหนึ่งค่าแล้วดูว่า estimate เปลี่ยนเพียงใด Bootstrap สุ่มจาก sample เดิมแบบคืนที่หลายครั้งแล้วสร้าง distribution ของ estimates ทั้งสองวิธีพยายามเลียนแบบพฤติกรรมของ estimate เมื่อ sample เปลี่ยน

สิ่งที่ต้องนำไปใช้ในห้องสอบคือ มองให้ออกว่าโจทย์ถาม parameter ใด เลือก statistic ให้ตรง ใช้ R สร้าง resampling results อ่าน bias, SE และ CI ในบริบท แล้วตรวจ assumptions ก่อนสรุป การเข้าใจลำดับนี้สำคัญกว่าการจำสูตร resampling ทุกสูตร

## 16. References

- Lecture 03: *Jackknife and Bootstrap Method for Estimation*
- Lab 03: *Solutions and R Programming Examples: Jackknife and Bootstrap Methods*
- Efron, B. and Tibshirani, R. J. (1993). *An Introduction to the Bootstrap*.
