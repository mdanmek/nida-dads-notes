# Spark Lab: ฝึกมองการเดินทางของข้อมูลผ่าน RDD และ Word Count

> เอกสารปฏิบัติฉบับนี้เรียบเรียงจาก lab05_spark.pdf ทั้ง 11 หน้าและโปรแกรม lab05_spark_wordcount.py โดยรักษาโจทย์และคำสั่งหลักจากเอกสาร แต่แก้ quotation marks, path และจุดที่อาจทำให้รันซ้ำไม่ได้ พร้อมอธิบายผลลัพธ์และกลไกของ Spark ในแต่ละขั้น

## 1. ภาพรวมของ Lab

Lab นี้มีสองเป้าหมายที่เชื่อมกัน เป้าหมายแรกคือทดลอง RDD operations ขนาดเล็กใน PySpark shell เพื่อให้เห็นว่า transformation เปลี่ยนรูปร่างข้อมูลอย่างไร และ action ใดทำให้ Spark เริ่มคำนวณ เป้าหมายที่สองคือนำความเข้าใจนั้นมาประกอบเป็นโปรแกรม Word Count แล้วส่งโปรแกรมด้วย spark-submit

เส้นทางของข้อมูลตลอด Lab คือ

~~~mermaid
flowchart LR
    L["ไฟล์ข้อความในเครื่อง"] --> H["คัดลอกเข้า HDFS"]
    H --> R["textFile สร้าง RDD ของบรรทัด"]
    R --> T["flatMap แยกเป็นคำ"]
    T --> K["map สร้างคู่ word, 1"]
    K --> C["reduceByKey รวมจำนวน"]
    C --> O["บันทึกผลลง HDFS"]
~~~

Spark ไม่ได้ดึงไฟล์ทั้งหมดมารวมที่ Driver ก่อน แต่แบ่งไฟล์เป็น partitions แล้วให้ tasks ประมวลผลบน Executors ใน local mode Executors อาจอยู่ในเครื่องเดียวกัน แต่แนวคิดการแบ่งงานยังเหมือนกับ cluster

## 2. เตรียมไฟล์และพื้นที่ใน HDFS

สร้างไฟล์ข้อความบน local file system

~~~bash
nano test.txt
~~~

ใช้ข้อมูลที่ตรวจผลด้วยมือได้ง่าย เช่น

~~~text
spark makes data fast
spark makes analysis possible
hadoop stores data
~~~

สร้าง directory ใน HDFS และนำไฟล์เข้าไป

~~~bash
hadoop fs -mkdir -p /user/cloudera/sw
hadoop fs -put -f test.txt /user/cloudera/sw/test.txt
~~~

คำสั่งแรกสร้าง directory ส่วน -p ทำให้รันซ้ำได้แม้ parent directory ยังไม่มี คำสั่ง put คัดลอก local file เข้า HDFS และ -f อนุญาตให้เขียนทับไฟล์เดิม

ตรวจสอบก่อนเริ่ม Spark

~~~bash
hadoop fs -ls /user/cloudera/sw
hadoop fs -cat /user/cloudera/sw/test.txt
~~~

เอกสารต้นฉบับใช้ path ทั้ง /user/cloudera/sw และ /user/root/sw ปะปนกัน ใน Lab นี้ใช้ /user/cloudera/sw ให้เหมือนกันตลอด หากระบบของผู้เรียนใช้ user อื่น สามารถตรวจ home directory ด้วยคำสั่งต่อไปนี้

~~~bash
hadoop fs -ls /user
~~~

## 3. เปิด PySpark และอ่านไฟล์เป็น RDD

~~~bash
pyspark
~~~

ภายใน shell ตัวแปร sc คือ SparkContext ที่สร้างไว้แล้ว อ่านไฟล์ด้วย

~~~python
text = sc.textFile("/user/cloudera/sw/test.txt")
~~~

text เป็น RDD ที่สมาชิกหนึ่งตัวแทนหนึ่งบรรทัดของไฟล์ การเรียก textFile เป็น transformation แบบ lazy จึงยังไม่จำเป็นต้องอ่านข้อมูลทั้งหมดจนกว่าจะมี action

ใช้ take เพื่อตรวจตัวอย่าง

~~~python
text.take(3)
~~~

ในเอกสารใช้ collect ซึ่งใช้ได้เพราะไฟล์ทดลองเล็ก

~~~python
text.collect()
~~~

collect ส่งทุกสมาชิกกลับมาที่ Driver จึงไม่ควรใช้กับข้อมูลใหญ่ หากเพียงต้องการตรวจหน้าตาข้อมูลให้ใช้ take(n)

ออกจาก shell ด้วย

~~~python
exit()
~~~

## 4. Word Count แบบ Interactive

เปิด PySpark อีกครั้งแล้วอ่านไฟล์

~~~python
text = sc.textFile("/user/cloudera/sw/test.txt")
~~~

### ขั้นที่ 1: แยกหนึ่งบรรทัดเป็นหลายคำ

~~~python
def tokenize(line):
    return line.split()

words = text.flatMap(tokenize)
words.take(20)
~~~

หนึ่งบรรทัดให้หลายคำ จึงใช้ flatMap หากใช้ map ผลลัพธ์จะเป็น list ซ้อนอยู่หนึ่ง list ต่อบรรทัด

| Input record | Output records จาก flatMap |
|---|---|
| spark makes data fast | spark, makes, data, fast |
| hadoop stores data | hadoop, stores, data |

### ขั้นที่ 2: สร้างคู่ Key–Value

~~~python
word_pairs = words.map(lambda word: (word, 1))
word_pairs.take(10)
~~~

แต่ละคำถูกเปลี่ยนเป็นคู่ (word, 1) เช่น (spark, 1) ตัวเลข 1 หมายถึงการพบคำนั้นหนึ่งครั้ง

### ขั้นที่ 3: รวมค่าตาม Key

~~~python
from operator import add

counts = word_pairs.reduceByKey(add)
counts.collect()
~~~

reduceByKey นำค่าของ key เดียวกันมารวมกัน เช่น

~~~text
(spark, 1), (spark, 1)  →  (spark, 2)
(data, 1), (data, 1)    →  (data, 2)
~~~

ขั้นนี้มักเกิด shuffle เพราะคำเดียวกันอาจอยู่คนละ partition อย่างไรก็ตาม reduceByKey สามารถรวมบางส่วนภายใน partition ก่อนส่งข้อมูลข้าม network จึงเหมาะกว่าการใช้ groupByKey แล้วนับเอง

### ขั้นที่ 4: บันทึกผลลง HDFS

กำหนด output เป็น directory ใหม่ ไม่ใช้ directory ที่มี input อยู่

~~~python
output_path = "/user/cloudera/sw/output"
counts.saveAsTextFile(output_path)
~~~

saveAsTextFile ต้องการ path ที่ยังไม่มีอยู่ ถ้ารันซ้ำจะเกิด error ว่า output directory already exists ลบผลเก่าก่อนรันใหม่

~~~bash
hadoop fs -rm -r /user/cloudera/sw/output
~~~

หลังออกจาก PySpark ตรวจผล

~~~bash
hadoop fs -ls /user/cloudera/sw/output
hadoop fs -cat /user/cloudera/sw/output/part-*
~~~

ผลลัพธ์เป็น directory เพราะ Spark เขียนแบบกระจาย แต่ละ output partition เป็นไฟล์ part หนึ่งไฟล์ และอาจมีไฟล์ _SUCCESS ระบุว่า job สำเร็จ ลำดับของคำไม่รับประกันเพราะ reduceByKey ไม่ได้มีหน้าที่เรียงข้อมูล

## 5. Transformation Operations

Transformation รับ RDD แล้วสร้าง RDD ใหม่แบบ lazy ตัวอย่างส่วนนี้ใช้ข้อมูลเล็กและ collect เพื่อให้เห็นผลได้ทันที

### map: หนึ่ง Input ต่อหนึ่ง Output

~~~python
rdd = sc.parallelize([1, 2, 3, 4])
out = rdd.map(lambda x: x * 2)
out.collect()
~~~

ผลลัพธ์คือ [2, 4, 6, 8] จำนวนสมาชิกยังเท่าเดิม เพราะสมาชิกหนึ่งตัวผ่านฟังก์ชันแล้วให้ผลหนึ่งตัว

### filter: เก็บสมาชิกที่ผ่านเงื่อนไข

~~~python
rdd = sc.parallelize([1, 2, 3, 4])
out = rdd.filter(lambda x: x % 2 == 0)
out.collect()
~~~

ผลคือ [2, 4] ฟังก์ชันคืน True สำหรับเลขคู่ จึงเหลือเฉพาะสมาชิกเหล่านั้น

### distinct: ลบค่าซ้ำ

~~~python
rdd = sc.parallelize([1, 2, 3, 2, 4, 3])
out = rdd.distinct()
out.collect()
~~~

ผลประกอบด้วย 1, 2, 3 และ 4 แต่อย่าพึ่งพาลำดับ distinct อาจต้อง shuffle เพื่อหาค่าซ้ำที่อยู่คนละ partition จึงแพงกว่า filter หรือ map

### map กับ flatMap

~~~python
rdd = sc.parallelize([1, 2, 3, 4])

mapped = rdd.map(lambda x: [x, x + 5])
mapped.collect()
~~~

ผลของ map เป็น list ซ้อน

~~~text
[[1, 6], [2, 7], [3, 8], [4, 9]]
~~~

~~~python
flattened = rdd.flatMap(lambda x: [x, x + 5])
flattened.collect()
~~~

ผลของ flatMap ถูกคลี่เป็นสมาชิกระดับเดียว

~~~text
[1, 6, 2, 7, 3, 8, 4, 9]
~~~

ความแตกต่างนี้อธิบายว่าเหตุใด Word Count ต้องใช้ flatMap เพื่อทำให้คำจากทุกบรรทัดอยู่ใน RDD เดียวกัน

## 6. Action Operations

Action ขอผลลัพธ์จริง จึงทำให้ Spark ประมวลผล lineage ที่สร้างไว้

### reduce: รวมทั้ง RDD ให้เหลือค่าเดียว

~~~python
rdd = sc.parallelize([1, 2, 3, 4])
product = rdd.reduce(lambda a, b: a * b)
~~~

ผลคือ 24 ฟังก์ชันสำหรับ reduce แบบกระจายควร associative และ commutative เพราะ Spark อาจรวมค่าเป็นลำดับต่างจากรายการเดิม การบวกและคูณเหมาะ แต่การลบไม่เหมาะเมื่อผลขึ้นกับลำดับ

### take: ดึงเพียงบางสมาชิก

~~~python
rdd.take(2)
rdd.take(5)
~~~

ถ้าขอมากกว่าจำนวนที่มี Spark คืนเท่าที่มี take เหมาะกับการตรวจข้อมูลมากกว่า collect

### collect: ดึงทุกสมาชิกกลับ Driver

~~~python
rdd.collect()
~~~

ใช้ได้กับผลลัพธ์เล็กเท่านั้น หาก RDD ใหญ่เกิน memory ของ Driver application อาจล้ม

### takeOrdered: เอา n ค่าตามลำดับ

~~~python
rdd.takeOrdered(3, key=lambda x: -x)
~~~

ผลคือ [4, 3, 2] เพราะ key เป็นค่าติดลบ จึงเท่ากับเลือกค่ามากสุดก่อน

### count: นับจำนวนสมาชิก

~~~python
rdd.count()
~~~

count คืนค่าเดียวให้ Driver แต่ Spark ยังต้องประมวลผล partitions เพื่อหาจำนวนรวม

## 7. Pair RDD Operations

Pair RDD มีสมาชิกเป็นคู่ (key, value) จึงรองรับ operations ตาม key

### reduceByKey

~~~python
rdd = sc.parallelize([
    (1, 2), (3, 4), (3, 6), (1, 3), (3, 8)
])

out = rdd.reduceByKey(lambda a, b: a + b)
out.collect()
~~~

ผลเชิงเนื้อหาคือ (1, 5) และ (3, 18) แต่ลำดับอาจต่างกัน reduceByKey เป็น transformation ไม่ใช่ action

### sortByKey

~~~python
rdd = sc.parallelize([
    (1, "c"), (3, "d"), (3, "a"), (1, "b"), (3, "e")
])

out = rdd.sortByKey()
out.collect()
~~~

Key ถูกเรียงจากน้อยไปมาก แต่ values ภายใน key เดียวกันไม่ควรถูกตีความว่าได้รับลำดับเชิงธุรกิจ การ sort แบบ distributed มักมี shuffle และต้นทุนสูง

### groupByKey

~~~python
grouped = rdd.groupByKey()
grouped.map(
    lambda item: (item[0], list(item[1]))
).collect()
~~~

ผลทำให้ค่าของ key เดียวกันรวมเป็น iterable ใช้เมื่อจำเป็นต้องเห็น values ทุกตัว หากต้องการเพียงผลรวมให้ใช้ reduceByKey เพราะลดข้อมูลก่อนส่งข้าม network ได้

## 8. foreach, Broadcast และ Accumulator

### foreach

~~~python
def show_value(x):
    print(x)

rdd = sc.parallelize([1, 2, 3, 4])
rdd.foreach(show_value)
~~~

ใน local mode อาจเห็นข้อความบน terminal แต่บน cluster ฟังก์ชันทำงานใน Executors ข้อความจึงอาจอยู่ใน Executor logs และลำดับไม่รับประกัน อย่าใช้ foreach(print) เป็นวิธีรวบรวมผลลัพธ์

### Broadcast Variable

~~~python
b = sc.broadcast([1, 2, 3, 4])

def lookup(index):
    return b.value[index]

rdd = sc.parallelize([0, 3])
rdd.map(lookup).collect()
~~~

ผลคือ [1, 4] Broadcast ส่งข้อมูลแบบอ่านอย่างเดียวไปยัง Executors อย่างมีประสิทธิภาพ เหมาะกับ lookup data ขนาดไม่ใหญ่มากที่หลาย tasks ต้องใช้ซ้ำ ไม่ควรแก้ b.value ภายใน task

### Accumulator

~~~python
rdd = sc.parallelize([1, 2, 3, 4])
c = sc.accumulator(0)

def add_to_total(x):
    global c
    c += x

rdd.foreach(add_to_total)
c.value
~~~

ผลที่คาดหวังคือ 10 Executors เพิ่มค่า ส่วน Driver อ่านค่า Accumulator เหมาะกับ counters และ diagnostics ไม่ควรใช้ควบคุม business logic เพราะ task retry และ lazy evaluation อาจทำให้การอัปเดตไม่เป็นไปตามที่ผู้เริ่มต้นคาด

## 9. โปรแกรม Word Count ฉบับพร้อมรัน

ไฟล์ Python ต้นฉบับมี logic ถูกต้องและใช้ quotation marks มาตรฐานแล้ว ฉบับด้านล่างเพิ่ม argument เพื่อไม่ต้องแก้ path ใน source code ทุกครั้ง และป้องกันการลืมหยุด SparkContext

~~~python
#!/usr/bin/env python3

import sys
from operator import add
from pyspark import SparkContext


def main(input_path, output_path):
    sc = SparkContext(appName="WordCount")

    try:
        counts = (
            sc.textFile(input_path)
            .flatMap(lambda line: line.split())
            .map(lambda word: (word, 1))
            .reduceByKey(add)
        )

        counts.saveAsTextFile(output_path)
    finally:
        sc.stop()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(
            "Usage: spark-submit wordcount.py INPUT OUTPUT"
        )

    main(sys.argv[1], sys.argv[2])
~~~

ก่อนรันให้ลบ output เดิมหากมี

~~~bash
hadoop fs -rm -r -f /user/cloudera/sw/output
~~~

ส่งโปรแกรมด้วย local mode

~~~bash
spark-submit \
  --master "local[*]" \
  wordcount.py \
  /user/cloudera/sw/test.txt \
  /user/cloudera/sw/output
~~~

local[*] หมายถึงใช้ logical CPU cores ที่มีบนเครื่องสำหรับ local execution วิธีนี้เหมาะกับ Lab และการตรวจ logic แต่ยังไม่จำลอง network, resource contention และ failure ของหลายเครื่องครบทั้งหมด

ตรวจผล

~~~bash
hadoop fs -ls /user/cloudera/sw/output
hadoop fs -cat /user/cloudera/sw/output/part-*
~~~

## 10. วิธีตรวจว่าผลถูกต้อง

จากข้อมูลตัวอย่าง

~~~text
spark makes data fast
spark makes analysis possible
hadoop stores data
~~~

ผลที่ควรได้โดยไม่สนใจลำดับคือ

| คำ | จำนวน |
|---|---:|
| spark | 2 |
| makes | 2 |
| data | 2 |
| fast | 1 |
| analysis | 1 |
| possible | 1 |
| hadoop | 1 |
| stores | 1 |

ตรวจยอดรวมของ counts จะได้ 11 ซึ่งต้องเท่ากับจำนวน tokens ทั้งหมด หากผลต่างให้ตรวจ whitespace, punctuation และตัวพิมพ์เล็ก–ใหญ่ เพราะ split อย่างเดียวถือว่า spark กับ Spark และ data กับ data, เป็นคนละคำ

หากต้องการ normalize เบื้องต้น

~~~python
import re

def tokenize(line):
    return re.findall(r"[A-Za-z0-9]+", line.lower())
~~~

การเปลี่ยน tokenizer เปลี่ยนนิยามของคำ จึงต้องระบุให้ชัดในงานจริง

## 11. Troubleshooting

### Output directory already exists

saveAsTextFile ไม่เขียนทับ directory เดิม ลบ path เดิมหรือเปลี่ยนชื่อ output

~~~bash
hadoop fs -rm -r -f /user/cloudera/sw/output
~~~

### Input path does not exist

ตรวจว่าใช้ HDFS path ไม่ใช่ local path และชื่อ user ตรงกับที่สร้างไว้

~~~bash
hadoop fs -ls /user/cloudera/sw
~~~

### Permission denied

ตรวจสิทธิ์และ HDFS home directory ของ user ไม่ควรแก้ด้วยการเปิดสิทธิ์กว้างโดยไม่เข้าใจระบบ หากเป็นเครื่อง Lab ให้ใช้ directory ที่อาจารย์กำหนด

### ไม่เห็นผลจาก foreach(print)

บน cluster ข้อความถูกพิมพ์ที่ Executor logs ใช้ take หรือ collect เฉพาะผลเล็กเพื่อดูที่ Driver

### ผลมีหลาย part files

เป็นพฤติกรรมปกติของ distributed output แต่ละ partition เขียนหนึ่ง part file ใช้ part-* เพื่ออ่านรวม ไม่ควรสมมติว่าจะมี part-00000 เพียงไฟล์เดียว

### ลำดับผล Word Count เปลี่ยน

reduceByKey ไม่รับประกัน global order หากต้องการเรียง ให้สร้างคู่ที่เหมาะสมแล้วใช้ sortByKey แต่ควรทำเฉพาะเมื่อจำเป็นเพราะเกิด shuffle เพิ่ม

### Python SyntaxError จาก quotation marks

สไลด์บางหน้าใช้ smart quotes เช่น ‘ ’ ให้เปลี่ยนเป็น single quote หรือ double quote มาตรฐานของ Python

## 12. แบบฝึกหัดต่อยอดพร้อมแนวคำตอบ

### 1. ปรับ Word Count ให้ไม่นับตัวพิมพ์ใหญ่และเล็กแยกกัน

เปลี่ยน tokenizer ให้เรียก lower ก่อน split

~~~python
tokens = input_file.flatMap(
    lambda line: line.lower().split()
)
~~~

คำว่า Spark และ spark จะกลายเป็น key เดียวกันก่อน reduceByKey

### 2. นับเฉพาะคำที่มีความยาวตั้งแต่ 5 ตัวอักษร

เพิ่ม filter หลัง flatMap และก่อน map เพื่อลดข้อมูลก่อน shuffle

~~~python
counts = (
    input_file
    .flatMap(lambda line: line.lower().split())
    .filter(lambda word: len(word) >= 5)
    .map(lambda word: (word, 1))
    .reduceByKey(add)
)
~~~

ตำแหน่งของ filter สำคัญ เพราะถ้ากรองก่อน reduceByKey คำที่ไม่ต้องการจะไม่ถูกส่งผ่าน shuffle

### 3. หา 10 คำที่พบบ่อยที่สุดโดยไม่ collect ทุกคำ

~~~python
top_10 = counts.takeOrdered(
    10,
    key=lambda item: -item[1],
)
~~~

takeOrdered นำกลับเพียง 10 รายการ เหมาะกว่า collect แล้ว sort ที่ Driver เมื่อจำนวนคำแตกต่างกันมีมาก

### 4. อธิบายว่าเหตุใด map ใช้แทน flatMap ในขั้น tokenize ไม่ได้โดยตรง

map คืนหนึ่ง output ต่อหนึ่งบรรทัด จึงได้ RDD ของ lists แต่ flatMap คลี่คำจากทุกบรรทัดออกเป็นสมาชิกระดับเดียว ทำให้ map เป็น (word, 1) และ reduceByKey ตามคำได้ตรงรูปแบบ

### 5. เหตุใดไม่ควรใช้ groupByKey สำหรับ Word Count

groupByKey ส่งค่า 1 ทุกตัวของแต่ละคำข้าม network แล้วจึงรวมภายหลัง ส่วน reduceByKey รวมบางส่วนในแต่ละ partition ได้ก่อน จึงลดปริมาณข้อมูลผ่าน shuffle

## สรุป

Lab นี้เริ่มจากไฟล์ local นำเข้า HDFS แล้วให้ Spark อ่านเป็น RDD ของบรรทัด Word Count ใช้ flatMap เปลี่ยนบรรทัดเป็นคำ map เปลี่ยนคำเป็นคู่ Key–Value และ reduceByKey รวมจำนวนตามคำ เมื่อ action หรือ saveAsTextFile ถูกเรียก Spark จึงประมวลผล lineage และเขียนผลเป็นหลาย part files ตาม partitions

การทำ Lab ให้ได้ผลไม่ใช่เพียงพิมพ์คำสั่งตามเอกสาร แต่ต้องรู้ว่าข้อมูลมีรูปร่างอย่างไรในแต่ละขั้น operation ใดทำให้เกิด shuffle ผลลัพธ์อยู่ที่ Driver หรือ Executors และ path ใดอยู่ใน local file system หรือ HDFS เมื่อเข้าใจสี่เรื่องนี้จะสามารถแก้ error และต่อยอดโปรแกรมได้เอง

## แหล่งอ้างอิง

- เอกสารปฏิบัติ lab05_spark.pdf หน้า 1–11
- โปรแกรมประกอบ lab05_spark_wordcount.py
- [Apache Spark: RDD Programming Guide](https://spark.apache.org/docs/latest/rdd-programming-guide.html)
- [Apache Hadoop: File System Shell Guide](https://hadoop.apache.org/docs/current/hadoop-project-dist/hadoop-common/FileSystemShell.html)
