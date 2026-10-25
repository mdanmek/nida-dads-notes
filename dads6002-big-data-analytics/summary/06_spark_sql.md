# Spark SQL และ DataFrame: จากข้อมูลแบบกระจายสู่ตารางที่ Spark เข้าใจ

> บทนี้เรียบเรียงจาก lecture_06_spark_sql.pdf ทั้ง 7 หน้า โดยขยายตัวอย่างสั้นในสไลด์ให้เป็นบทเรียนต่อเนื่อง และเทียบ API เก่ากับวิธีที่ใช้ในปัจจุบัน

## 1. เหตุใด Spark จึงต้องมี DataFrame

จากบท Spark ก่อนหน้า เรารู้จัก RDD ซึ่งเป็นชุด records ที่แบ่งเป็น partitions และกระจายไปประมวลผลบน Executors สมมติ record หนึ่งมีค่า (Anna, 25, CA) มนุษย์อาจทราบจากบริบทว่าค่าแรกคือชื่อ ค่าที่สองคืออายุ และค่าสุดท้ายคือรัฐ แต่ตัวค่าเพียงอย่างเดียวยังไม่ได้บอก Spark ว่าแต่ละตำแหน่งมีความหมายหรือชนิดข้อมูลอะไร

ถ้าระบบรู้ว่า **age** เป็นจำนวนเต็ม ก็สามารถตรวจเงื่อนไข age > 25 ได้ ถ้ารู้ว่า query ใช้เพียง name และ state ก็อาจอ่านเฉพาะสองคอลัมน์นั้นจากแหล่งข้อมูลที่รองรับ ความรู้เกี่ยวกับโครงสร้างจึงเปิดโอกาสให้ Spark ตรวจและปรับแผนได้มากกว่าการมองข้อมูลเป็น Python objects ทั่วไป

**DataFrame** คือชุดข้อมูลแบบกระจายที่จัดเป็น rows ภายใต้ columns ซึ่งมีชื่อกำกับ ในมุมของผู้ใช้จึงคล้าย table ในฐานข้อมูลหรือ worksheet ที่มีหัวคอลัมน์ แต่ในมุมของระบบ ข้อมูลยังคงแบ่งเป็น partitions และถูกประมวลผลด้วย tasks บน Executors หลายตัว

| มุมที่ผู้ใช้เห็น | สิ่งที่เกิดขึ้นใน Spark |
|---|---|
| ตารางที่มีชื่อคอลัมน์ | DataFrame ที่กระจายเป็น partitions |
| select, filter, groupBy | Logical plan ที่ยังไม่จำเป็นต้องรันทันที |
| show() หรือ count() | Action ที่เริ่มการประมวลผล |
| ผลไม่กี่แถวบนหน้าจอ | ผลจาก tasks ซึ่งถูกนำมาแสดงที่ Driver |

DataFrame ยังคง immutable, distributed และ lazy เช่นเดียวกับ RDD กล่าวคือ operation ไม่ได้แก้ DataFrame เดิม แต่สร้าง DataFrame ใหม่ และ Spark ยังไม่คำนวณจนกว่าจะมี action ต้องการผลจริง

## 2. Schema ทำให้ Spark เข้าใจโครงสร้าง

Schema คือคำอธิบายโครงสร้างของ DataFrame ประกอบด้วยชื่อคอลัมน์ ชนิดข้อมูล และเงื่อนไขว่าคอลัมน์ยอมให้มีค่า NULL หรือไม่

| name | age | state |
|---|---:|---|
| Anna | 25 | CA |
| Jack | 22 | TX |
| Tom | 20 | FL |

จากตารางนี้ Schema บอกว่า name และ state เป็น string ส่วน age เป็น integer เมื่อเขียน age > 25 Spark จึงรู้ว่าเป็นการเปรียบเทียบตัวเลข และหากอ้าง unknown_column ระบบสามารถตรวจพบว่าคอลัมน์นั้นไม่มีอยู่ก่อนเริ่มอ่านข้อมูลทั้งหมด

~~~mermaid
flowchart TD
    D["ข้อมูลจากไฟล์หรือ records"] --> S["Schema: ชื่อ ชนิดข้อมูล nullable"]
    S --> F["DataFrame ที่มีโครงสร้าง"]
    F --> Q["DataFrame API หรือ SQL"]
    Q --> P["Spark วิเคราะห์และปรับแผน"]
    P --> E["Executors ประมวลผล partitions"]
~~~

Schema ไม่ได้มีไว้เพียงแสดงหัวตาราง แต่ช่วยให้ Spark ตรวจชื่อและชนิดข้อมูล เลือกอ่านเฉพาะคอลัมน์เมื่อแหล่งข้อมูลรองรับ และสร้างแผนการทำงานได้ดีขึ้น ตามเอกสาร Apache Spark ปัจจุบัน DataFrame คือ Dataset ที่จัดข้อมูลอยู่ภายใต้ named columns และสร้างได้จาก structured files, Hive tables, external databases หรือ RDD ([Spark SQL Guide](https://spark.apache.org/docs/latest/sql-programming-guide.html)).

## 3. DataFrame ไม่ใช่การคัดลอกข้อมูลเป็นตารางใหม่เสมอไป

เมื่อเขียน

~~~python
adults = people_df.filter(people_df.age >= 20)
~~~

people_df ไม่ถูกแก้ไข และ adults ยังไม่จำเป็นต้องมีข้อมูลทุกแถวอยู่ใน memory ทันที Spark สร้างคำอธิบายว่าจะอ่าน people_df แล้วเก็บ rows ที่ผ่านเงื่อนไข เมื่อมี adults.show() หรือ action อื่นจึงเริ่มประมวลผล

จึงควรแยกภาพสามระดับออกจากกัน

1. **Data source** คือข้อมูลต้นทาง เช่น CSV, Parquet, Hive table หรือ RDD
2. **DataFrame** คือมุมมองเชิงตรรกะที่มี Schema และ transformations
3. **Physical execution** คือ tasks ที่อ่าน กรอง รวม หรือเรียง partitions จริง

## 4. Spark SQL เปลี่ยนคำสั่งเป็นงานบน Cluster อย่างไร

ผู้ใช้สั่งงานได้ทั้ง DataFrame API และ SQL

~~~python
result_api = (
    people_df
    .filter(people_df.age > 25)
    .select("name", "state")
)
~~~

~~~sql
SELECT name, state
FROM people
WHERE age > 25
~~~

ทั้งสองรูปแบบเข้าสู่ Spark SQL engine และถูกแปลงเป็นแผนก่อนรัน

~~~mermaid
flowchart TD
    A["SQL หรือ DataFrame API"] --> B["Logical Plan"]
    B --> C["Analyzer ใช้ Catalog และ Schema"]
    C --> D["Optimized Logical Plan"]
    D --> E["Physical Plan"]
    E --> F["Tasks บน Executors"]
~~~

Spark สร้าง logical plan จากสิ่งที่ผู้ใช้ต้องการ Analyzer ตรวจว่าตาราง คอลัมน์ และชนิดข้อมูลมีอยู่จริง จากนั้น optimizer ปรับแผนโดยยังรักษาความหมายเดิม เช่น ผลัก filter ไปใกล้แหล่งข้อมูลหรืออ่านเฉพาะคอลัมน์ที่จำเป็น สุดท้ายระบบเลือก physical operators และแบ่งงานให้ cluster

คำกล่าวว่า DataFrame เร็วกว่า RDD จึงควรเข้าใจอย่างมีเงื่อนไข ความได้เปรียบคือ Spark มองเห็นโครงสร้างและความหมายของ operations ได้มากกว่า จึงมีโอกาส optimize แผน ส่วนความเร็วจริงยังขึ้นกับ data source, partitions, shuffle, data skew และทรัพยากร

## 5. จุดเริ่มต้นของโปรแกรม: จาก SQLContext สู่ SparkSession

สไลด์ใช้ SparkContext และ SQLContext ซึ่งเป็นรูปแบบของ Spark รุ่นก่อน

~~~python
from pyspark import SparkContext
from pyspark.sql import SQLContext

sc = SparkContext()
sqlContext = SQLContext(sc)
~~~

ปัจจุบันใช้ **SparkSession** เป็นจุดเริ่มต้นหลักสำหรับ DataFrame และ Spark SQL

~~~python
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("SparkSQLExample")
    .getOrCreate()
)
~~~

SparkSession รวมการอ่านข้อมูล การสร้าง DataFrame การเรียก SQL และ Catalog ไว้ใน object เดียว หากต้องใช้ RDD API ยังเข้าถึง SparkContext ได้ด้วย spark.sparkContext

## 6. สร้าง DataFrame จากข้อมูลในโปรแกรม

~~~python
person = [
    ("Anna", 25, "CA"),
    ("Jack", 22, "TX"),
    ("Tom", 20, "FL"),
    ("Bob", 26, "NY"),
    ("Frank", 29, "CA"),
]

df = spark.createDataFrame(person, ["name", "age", "state"])
df.show()
~~~

แต่ละ tuple กลายเป็นหนึ่ง row ส่วน list ของชื่อคอลัมน์กำหนดความหมายของแต่ละตำแหน่ง Spark สามารถอนุมานชนิดข้อมูลจากค่าได้ แต่การอนุมานอาจไม่ตรงกับกฎของระบบงาน โดยเฉพาะข้อมูลที่มี NULL ตัวเลขหลายชนิด หรือไฟล์ที่ไม่สม่ำเสมอ งานจริงจึงมักกำหนด Schema เอง

เอกสารปัจจุบันระบุว่า spark.createDataFrame() รับข้อมูลได้จาก RDD, list, pandas DataFrame, NumPy array หรือ PyArrow table ([createDataFrame](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.SparkSession.createDataFrame.html)).

## 7. กำหนด Schema ด้วย StructType และ StructField

StructType แทนโครงสร้างทั้ง row ส่วน StructField แทนหนึ่ง column

~~~python
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType
)

person_schema = StructType([
    StructField("name", StringType(), nullable=False),
    StructField("age", IntegerType(), nullable=True),
    StructField("state", StringType(), nullable=True),
])

df = spark.createDataFrame(person, schema=person_schema)
df.printSchema()
~~~

~~~text
root
 |-- name: string (nullable = false)
 |-- age: integer (nullable = true)
 |-- state: string (nullable = true)
~~~

แต่ละ StructField ระบุชื่อ field, data type และ nullable ส่วน nullable=False บอกว่า field ไม่ควรเป็น NULL แต่ไม่ได้ทดแทน data validation ทั้งหมด เช่นอายุ -10 ยังเป็น integer ที่ไม่ใช่ NULL แม้ไม่มีความหมายทางธุรกิจ

## 8. สร้าง DataFrame จากไฟล์ข้อความ

สไลด์แสดงเส้นทางจาก text file ไปเป็น RDD แยกข้อความ แปลงชนิดข้อมูล แล้วสร้าง DataFrame

~~~python
rdd = (
    sc.textFile("/user/cloudera/test.data")
    .map(lambda line: line.split(","))
    .map(lambda fields: [
        int(fields[0]),
        int(fields[1]),
        float(fields[2]),
    ])
)

schema = StructType([
    StructField("x", IntegerType(), True),
    StructField("y", IntegerType(), True),
    StructField("z", FloatType(), True),
])

df = spark.createDataFrame(rdd, schema)
~~~

ตัวอย่างนี้ทำให้เห็นขั้นตอน ข้อความดิบ → fields → typed records → DataFrame แต่ถ้าเป็น CSV จริง ควรใช้ DataFrame reader ซึ่งจัดการ header, delimiter และ quoted values ได้ตรงหน้าที่กว่า

~~~python
df = (
    spark.read
    .option("header", True)
    .schema(schema)
    .csv("/user/cloudera/test.csv")
)
~~~

การใช้ line.split(",") อาจผิดเมื่อข้อความมี comma อยู่ภายใน quotation marks และ int() อาจทำให้ task ล้มเมื่อพบค่าผิดรูปแบบ จึงควรใช้ reader ตามชนิดไฟล์ เว้นแต่รูปแบบเฉพาะจน reader ปกติรองรับไม่ได้

## 9. Operations พื้นฐาน

### แสดงและนับข้อมูล

~~~python
df.show(5)
row_count = df.count()
~~~

show() เป็น action ที่นำ rows จำนวนน้อยมาแสดง ส่วน count() เป็น action ที่หาจำนวน rows จริง การเรียกสองคำสั่งนี้อาจสร้างคนละ job และคำนวณบางส่วนซ้ำหากไม่ได้ cache

### เลือกคอลัมน์และกรองแถว

~~~python
df.select("name", "age").show()
df.filter(df.age > 25).show()
df.filter("age > 25").show()
~~~

select() เลือก columns ส่วน filter() เลือก rows ทั้งสองเป็น transformations และคืน DataFrame ใหม่โดยยังคง lazy จนพบ action

### เรียงข้อมูล

~~~python
df.orderBy("age", ascending=False).show()
~~~

การเรียงข้อมูลแบบ distributed อาจต้อง shuffle เพื่อจัดช่วงค่าระหว่าง partitions จึงแพงกว่าการเรียงข้อมูลเล็กบนเครื่องเดียว ควรเรียงเมื่อผลลัพธ์ต้องใช้ลำดับจริง

### จัดกลุ่มและ Aggregation

~~~python
df.groupBy("state").avg("age").show()
~~~

groupBy("state") หมายถึงนำ rows ที่มี state เดียวกันมารวมเพื่อคำนวณบางอย่าง จึงต้องตามด้วย aggregation เช่น count, sum หรือ avg

~~~mermaid
flowchart LR
    A["Rows หลาย partitions"] --> B["เลือก key: state"]
    B --> C["Shuffle key เดียวกันมาพบกัน"]
    C --> D["คำนวณ avg age"]
    D --> E["DataFrame ผลลัพธ์"]
~~~

Shuffle ทำให้ groupBy บนข้อมูลใหญ่อาจใช้ network และเวลา หาก key หนึ่งมี rows มากผิดปกติจะเกิด data skew และ task ที่รับ key นั้นอาจช้ากว่าตัวอื่น

## 10. ใช้ SQL กับ DataFrame ผ่าน Temporary View

สไลด์ใช้ registerAsTable() ซึ่งเป็น API เก่า ปัจจุบันใช้ createOrReplaceTempView()

~~~python
df.createOrReplaceTempView("person")

result = spark.sql("""
    SELECT name, state
    FROM person
    WHERE age > 25
""")

result.show()
~~~

Temporary view ไม่ได้คัดลอกข้อมูลทั้งหมดไปเป็น table ใหม่ แต่เพิ่มชื่อให้ logical plan ของ DataFrame เพื่ออ้างผ่าน SQL อายุของ local temporary view ผูกกับ SparkSession ที่สร้าง view นั้น ([createOrReplaceTempView](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.createOrReplaceTempView.html)).

DataFrame API กับ SQL ไม่ใช่คนละ engine ทั้งสองเข้าสู่ Spark SQL engine เดียวกัน ผู้ใช้จึงเลือกวิธีเขียนที่เหมาะกับงานและทีมได้

## 11. ตัวอย่างต่อเนื่อง: อายุเฉลี่ยตามรัฐ

~~~python
from pyspark.sql import functions as F

state_summary = (
    df
    .groupBy("state")
    .agg(
        F.avg("age").alias("avg_age"),
        F.count("*").alias("person_count"),
    )
    .filter(F.col("avg_age") > 24)
    .orderBy(F.col("avg_age").desc())
)

state_summary.show()
~~~

คำสั่งเดียวกันเขียนเป็น SQL ได้ดังนี้

~~~sql
SELECT
    state,
    AVG(age) AS avg_age,
    COUNT(*) AS person_count
FROM person
GROUP BY state
HAVING AVG(age) > 24
ORDER BY avg_age DESC
~~~

ลำดับความหมายคืออ่าน DataFrame → จัดกลุ่มตาม state → คำนวณค่าเฉลี่ยและจำนวน → เก็บกลุ่มที่ผ่านเงื่อนไข → เรียงผลลัพธ์ ไม่ว่าจะเขียนด้วย API หรือ SQL ระบบยังสร้างแผนผ่าน Spark SQL

## 12. ตรวจแผนด้วย explain()

~~~python
state_summary.explain(mode="formatted")
~~~

explain() เชื่อมโค้ดระดับสูงกับสิ่งที่ cluster จะทำจริง เวลาอ่านแผนให้ดูว่า Spark อ่านข้อมูลจากที่ใด อ่านคอลัมน์ใด filter อยู่ตรงไหน และมี Exchange ซึ่งสื่อถึง shuffle หรือไม่ ผู้เริ่มต้นยังไม่ต้องจำ operator ทุกชื่อ แต่ควรใช้แผนตอบให้ได้ว่างานส่วนใดอาจแพง

## 13. เลือก DataFrame หรือ RDD

DataFrame เหมาะเมื่อข้อมูลมีโครงสร้างหรือกึ่งมีโครงสร้าง และงานอธิบายด้วย columns, expressions, joins และ aggregations ได้ เพราะ Schema ช่วยให้ Spark ตรวจและ optimize query โค้ดมักสั้นและสื่อความหมายชัดเจน

RDD ยังมีประโยชน์เมื่อจำเป็นต้องควบคุม records ระดับต่ำ หรือใช้ logic เฉพาะที่ relational operations อธิบายได้ยาก แต่การแปลง DataFrame ไปเป็น RDD โดยไม่จำเป็นทำให้ Spark มองเห็นความหมายของ operation น้อยลง

| สถานการณ์ | จุดเริ่มต้นที่เหมาะสม |
|---|---|
| เลือก กรอง รวม และ join ตามคอลัมน์ | DataFrame / Spark SQL |
| อ่าน Parquet, Hive table หรือ JDBC | DataFrame |
| ต้องการให้ optimizer มองเห็น query | DataFrame / Spark SQL |
| Logic เฉพาะที่ expressions รองรับยาก | พิจารณา RDD |
| นักวิเคราะห์ต้องการใช้ SQL | Temporary view หรือ table |

## 14. ข้อผิดพลาดที่พบบ่อย

- Smart quotes อย่าง ‘ ’ “ ” จากสไลด์ใช้กับ Python ไม่ได้ ควรใช้ quotation marks มาตรฐาน
- Schema เป็น integer แต่ข้อมูลจริงมีข้อความ อาจเกิดปัญหาระหว่าง parsing
- show() แสดงเพียงตัวอย่าง ไม่ได้พิสูจน์ว่าทุก row ถูกต้อง
- collect() นำทุก row กลับ Driver และเสี่ยง memory เต็ม
- Temporary view เป็นชื่อชั่วคราวภายใน session ไม่ใช่ persisted table
- groupBy, aggregation และ orderBy อาจเกิด shuffle จึงต้องระวัง data skew
- Schema ถูกชนิดไม่ได้รับประกันว่าค่าถูกต้องตามธุรกิจ จึงยังต้องมี validation

## 15. เชื่อม Spark Core กับ Spark SQL

RDD ทำให้เราเห็น partitions, transformations, actions, lineage และ lazy evaluation ส่วน DataFrame เพิ่ม Schema และ relational operations เพื่อให้ Spark เข้าใจโครงสร้าง เมื่อผู้ใช้เขียน DataFrame API หรือ SQL ระบบสร้าง logical plan วิเคราะห์ชื่อกับชนิดข้อมูล ปรับแผน แล้วสร้าง physical plan เพื่อรัน tasks บน Executors

เส้นทางทั้งหมดคือ

**Data source → DataFrame + Schema → SQL/DataFrame operations → Logical plan → Optimized plan → Physical plan → Tasks → Result**

เมื่อเห็นเส้นทางนี้ คำสั่งสั้นอย่าง df.groupBy("state").avg("age").show() จะไม่ใช่เพียง syntax แต่เป็นงานที่ซ่อนการตรวจ Schema การสร้างแผน การ shuffle และการคำนวณแบบกระจายไว้ข้างหลัง

## 16. คำถามฝึกอธิบายพร้อมแนวคำตอบ

### 1. DataFrame คืออะไร และต่างจาก RDD อย่างไร

DataFrame คือชุดข้อมูลแบบกระจายที่จัด rows ภายใต้ named columns และมี Schema จึงยัง immutable, distributed และ lazy เหมือน RDD แต่ Spark เข้าใจโครงสร้างได้มากกว่า ทำให้ตรวจคำสั่งและ optimize query ได้ ส่วน RDD ให้การควบคุม records ระดับต่ำกว่า

### 2. Schema มีประโยชน์อย่างไร

Schema ระบุชื่อคอลัมน์ ชนิดข้อมูล และ nullable ทำให้ Spark ตรวจชื่อและชนิดข้อมูลก่อนรัน และใช้ข้อมูลนี้สร้าง logical plan เมื่อ data source รองรับ Spark ยังอาจอ่านเฉพาะคอลัมน์ที่ query ต้องใช้ได้

### 3. อธิบายลำดับการทำงานของ Spark SQL

Spark รับ SQL หรือ DataFrame operations แล้วสร้าง logical plan จากนั้น Analyzer ใช้ Schema และ Catalog ตรวจความหมาย Optimizer ปรับแผนโดยไม่เปลี่ยนผลลัพธ์ แล้วระบบเลือก physical plan และแบ่งเป็น tasks ให้ Executors ประมวลผล partitions

### 4. select, filter, groupBy และ show ต่างกันอย่างไร

select() เลือก columns, filter() เลือก rows และ groupBy() กำหนด key สำหรับ aggregation ทั้งสามสร้าง DataFrame ใหม่แบบ lazy ส่วน show() เป็น action ที่ทำให้ Spark ประมวลผลแผนและนำตัวอย่างมาแสดง

### 5. Temporary view ทำให้ใช้ SQL กับ DataFrame ได้อย่างไร

createOrReplaceTempView() ลงทะเบียนชื่อให้ DataFrame ภายใน SparkSession เมื่อ SQL อ้างชื่อนี้ Spark เชื่อมชื่อกับ logical plan แล้วประมวลผลผ่าน Spark SQL engine การสร้าง view ไม่ได้บันทึกข้อมูลเป็น table ถาวร

### 6. เหตุใดงาน production ควรกำหนด Schema ชัดเจน

Schema ที่กำหนดเองทำให้ชนิดข้อมูลคงที่ ไม่ขึ้นกับข้อมูลตัวอย่างที่ใช้อนุมาน ช่วยตรวจข้อมูลผิดรูปแบบและทำให้ผลการอ่านสม่ำเสมอ แต่ยังต้องมี business validation เพราะชนิดข้อมูลถูกต้องไม่ได้แปลว่าค่าสมเหตุสมผล

## สรุป

DataFrame ทำให้ข้อมูลแบบกระจายมีชื่อคอลัมน์และ Schema ที่ระบบเข้าใจ ผู้ใช้จึงสั่งด้วย DataFrame API หรือ SQL ได้โดยไม่ต้องจัดการ records ทีละตัว Spark SQL นำคำสั่งมาสร้าง วิเคราะห์ และ optimize แผนก่อนส่ง tasks ไปทำงานบน Executors

หัวใจของบทนี้คือ DataFrame เป็นทั้งมุมมองแบบตารางสำหรับผู้ใช้และแผนการคำนวณแบบกระจายสำหรับ Spark ส่วน Schema เป็นสะพานระหว่างสองมุมมองและทำให้ Spark รู้ว่าคอลัมน์แต่ละตัวหมายถึงอะไร

## แหล่งอ้างอิง

- เอกสารประกอบการสอน lecture_06_spark_sql.pdf หน้า 1–7
- [Apache Spark: Spark SQL, DataFrames and Datasets Guide](https://spark.apache.org/docs/latest/sql-programming-guide.html)
- [Apache Spark: SparkSession.createDataFrame](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.SparkSession.createDataFrame.html)
- [Apache Spark: DataFrame.createOrReplaceTempView](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.createOrReplaceTempView.html)
- [Apache Spark: Performance Tuning](https://spark.apache.org/docs/latest/sql-performance-tuning.html)
