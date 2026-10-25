# Spark SQL Lab: จาก RDD และไฟล์ข้อความสู่ DataFrame ที่ Query ได้

> เอกสารปฏิบัติฉบับนี้เรียบเรียงจาก lab06_spark_sql.pdf ทั้ง 5 หน้าและไฟล์ lab06_spark_sql_test.data โดยแก้ smart quotes และ API รุ่นเก่า พร้อมเพิ่มผลลัพธ์ที่ควรได้ วิธีตรวจ Schema และคำอธิบายว่าข้อมูลเปลี่ยนแปลงอย่างไรในแต่ละขั้น

## 1. สิ่งที่ Lab นี้กำลังเชื่อมเข้าด้วยกัน

บท Spark Lab ก่อนหน้าใช้ RDD ซึ่งมองข้อมูลเป็น records แบบกระจาย ส่วน Lab นี้เพิ่ม **Schema** เพื่อบอกชื่อและชนิดข้อมูล จากนั้นจึงใช้ DataFrame API หรือ SQL เข้าถึงข้อมูลด้วยชื่อคอลัมน์

~~~mermaid
flowchart LR
    A["Python tuples หรือ text file"] --> B["RDD ของ records"]
    B --> C["เพิ่มชื่อคอลัมน์และชนิดข้อมูล"]
    C --> D["DataFrame"]
    D --> E["DataFrame Operations"]
    D --> F["Temporary View"]
    F --> G["SQL Query"]
~~~

DataFrame ไม่ได้ทำให้ข้อมูลเลิกเป็น distributed ข้อมูลยังแบ่งเป็น partitions และทำงานบน Executors สิ่งที่เพิ่มขึ้นคือ Spark รู้ว่าแต่ละ field มีชื่อและ data type อะไร จึงตรวจและวางแผน query ได้

## 2. เริ่ม PySpark

เปิด shell

~~~bash
pyspark
~~~

เอกสารต้นฉบับใช้ sqlContext ซึ่งมีอยู่ใน environment รุ่นเก่า ปัจจุบัน PySpark shell เตรียม SparkSession ชื่อ spark ให้ และควรใช้ spark เป็นจุดเริ่มต้นหลัก

ตรวจ object ที่มีอยู่

~~~python
spark
sc
~~~

- spark คือ SparkSession สำหรับ DataFrame และ Spark SQL
- sc คือ SparkContext สำหรับ RDD

## 3. สร้าง DataFrame จาก Python Data

เริ่มจากข้อมูลบุคคล 5 คน แต่ละ tuple มีชื่อ อายุ และรัฐ

~~~python
person = [
    ("Anna", 25, "CA"),
    ("Jack", 22, "TX"),
    ("Tom", 20, "FL"),
    ("Bob", 26, "NY"),
    ("Frank", 29, "CA"),
]
~~~

สร้าง RDD จาก list

~~~python
rdd = sc.parallelize(person)
rdd.collect()
~~~

ตอนนี้ Spark เห็นแต่ records ที่เป็น tuples ยังไม่มีชื่อคอลัมน์ในระดับ DataFrame เปลี่ยนเป็น DataFrame ด้วย

~~~python
df = spark.createDataFrame(
    rdd,
    ["name", "age", "state"],
)
~~~

ตรวจชนิด object

~~~python
type(df)
~~~

ผลเป็น pyspark.sql.dataframe.DataFrame หรือชื่อ class ใกล้เคียงตามเวอร์ชัน

แสดงข้อมูล

~~~python
df.show()
~~~

ผลที่ควรได้

~~~text
+-----+---+-----+
| name|age|state|
+-----+---+-----+
| Anna| 25|   CA|
| Jack| 22|   TX|
|  Tom| 20|   FL|
|  Bob| 26|   NY|
|Frank| 29|   CA|
+-----+---+-----+
~~~

ตรวจ Schema

~~~python
df.printSchema()
~~~

Spark อนุมานชนิดข้อมูลจาก Python values ผลทั่วไปคือ name และ state เป็น string ส่วน age เป็น long

~~~text
root
 |-- name: string (nullable = true)
 |-- age: long (nullable = true)
 |-- state: string (nullable = true)
~~~

คำว่า nullable = true หมายถึง Schema อนุญาตให้คอลัมน์มีค่า NULL ไม่ได้ยืนยันว่าข้อมูลชุดนี้มี NULL จริง

## 4. เหตุใด DataFrame จึงยังเป็น Lazy

เมื่อเขียน

~~~python
older_people = df.filter("age > 25")
~~~

Spark สร้าง DataFrame ใหม่พร้อม logical plan แต่ยังไม่จำเป็นต้องกรองข้อมูลจริง จนกระทั่งเรียก action เช่น

~~~python
older_people.show()
~~~

show ทำให้ Spark สร้าง job ประมวลผลแผนและนำผลบางส่วนกลับมาแสดงที่ Driver แนวคิด transformation และ action จึงยังเหมือน RDD เพียงแต่ operations ของ DataFrame อ้างคอลัมน์และมี Schema

## 5. DataFrame Operations พื้นฐาน

### show(n): ดูตัวอย่าง

~~~python
df.show(5)
~~~

show แสดง 5 rows แรกสำหรับตรวจหน้าตาข้อมูล ไม่ควรตีความว่าเป็นการตรวจความถูกต้องทั้ง dataset

### count(): นับ rows

~~~python
df.count()
~~~

ผลคือ 5 count เป็น action และคืนค่าตัวเลขที่ Driver

### select(): เลือกคอลัมน์

~~~python
df.select("name", "age").show()
~~~

ผลลัพธ์ยังมี 5 rows แต่ Schema เหลือเพียง name และ age

~~~python
selected = df.select("name", "age")
selected.printSchema()
~~~

select ไม่แก้ df เดิม แต่สร้าง DataFrame ใหม่ตามคุณสมบัติ immutable

### orderBy(): เรียงข้อมูล

~~~python
df.orderBy("age", ascending=False).show()
~~~

ลำดับที่ควรได้คือ Frank 29, Bob 26, Anna 25, Jack 22 และ Tom 20 การเรียงข้อมูลข้าม partitions อาจเกิด shuffle จึงมีต้นทุนมากกว่าการแสดงข้อมูลโดยไม่เรียง

### filter(): กรอง rows

เขียนเป็น SQL expression

~~~python
df.filter("age > 25").show()
~~~

หรือ Column expression

~~~python
df.filter(df.age > 25).show()
~~~

ทั้งสองแบบได้ Bob และ Frank เงื่อนไขใช้ > จึงไม่รวม Anna ซึ่งมีอายุ 25

### groupBy() และ Aggregation

~~~python
df.groupBy("state").avg("age").show()
~~~

ผลเชิงเนื้อหาคือ

| state | avg(age) |
|---|---:|
| CA | 27.0 |
| TX | 22.0 |
| FL | 20.0 |
| NY | 26.0 |

CA มี Anna อายุ 25 และ Frank อายุ 29 ค่าเฉลี่ยจึงเป็น 27 ส่วนรัฐอื่นมีคนเดียว ค่าเฉลี่ยจึงเท่ากับอายุของคนนั้น ลำดับ rows ไม่รับประกันหากไม่ได้ orderBy

การ groupBy ต้องรวบรวม rows ที่มี key เดียวกัน และมักทำให้เกิด shuffle

~~~mermaid
flowchart LR
    P["Rows ในหลาย partitions"] --> K["จัดกลุ่มด้วย state"]
    K --> S["Shuffle ให้ state เดียวกันมาพบกัน"]
    S --> A["คำนวณ AVG age"]
    A --> R["DataFrame ผลลัพธ์"]
~~~

เขียนชื่อผลลัพธ์ให้อ่านง่ายขึ้น

~~~python
from pyspark.sql import functions as F

state_age = (
    df
    .groupBy("state")
    .agg(F.avg("age").alias("avg_age"))
    .orderBy("state")
)

state_age.show()
~~~

## 6. ลงทะเบียน Temporary View แล้วใช้ SQL

เอกสารต้นฉบับใช้ registerAsTable ซึ่งเป็น API เก่า ปัจจุบันใช้ createOrReplaceTempView

~~~python
df.createOrReplaceTempView("person_table")
~~~

จากนั้น query ผ่าน SparkSession

~~~python
result = spark.sql("""
    SELECT name, state
    FROM person_table
    ORDER BY name
""")

result.show()
~~~

Temporary view ไม่ได้คัดลอกข้อมูลไปสร้าง table ถาวร แต่ลงทะเบียนชื่อ person_table ให้ชี้ไปยัง logical plan ของ df ภายใน SparkSession

~~~mermaid
flowchart TD
    D["DataFrame df"] --> V["Temporary View: person_table"]
    Q["SQL SELECT"] --> V
    V --> L["Spark SQL Logical Plan"]
    L --> E["Execution บน partitions"]
~~~

ทดลอง SQL ที่เทียบกับ DataFrame operations

~~~python
spark.sql("""
    SELECT state, AVG(age) AS avg_age
    FROM person_table
    GROUP BY state
    ORDER BY state
""").show()
~~~

DataFrame API และ SQL เข้าสู่ Spark SQL engine เดียวกัน จึงเลือกใช้ตามความถนัดและความชัดเจนของงานได้

## 7. เตรียมไฟล์ lab06_spark_sql_test.data

ไฟล์มี 16 rows และไม่มี header

~~~text
1,1,5.0
1,2,1.0
1,3,5.0
1,4,1.0
...
4,4,5.0
~~~

แต่ละ row มีสามค่า ซึ่ง Lab ตั้งชื่อว่า x, y และ z สองคอลัมน์แรกเป็น integer ส่วนคอลัมน์สุดท้ายเป็น float

คัดลอกไฟล์จาก local file system เข้า HDFS

~~~bash
hadoop fs -mkdir -p /user/cloudera
hadoop fs -put -f lab06_spark_sql_test.data /user/cloudera/test.data
hadoop fs -ls /user/cloudera
hadoop fs -cat /user/cloudera/test.data
~~~

สไลด์ใช้เครื่องหมาย dash ที่มาจากการจัดเอกสารในคำสั่ง fs –put ต้องพิมพ์ hyphen ปกติเป็น fs -put

## 8. อ่าน Text File ผ่าน RDD

เปิด PySpark แล้วอ่านข้อมูล

~~~python
raw = sc.textFile("/user/cloudera/test.data")
raw.take(5)
~~~

ตอนนี้หนึ่งสมาชิกเป็น string ทั้งบรรทัด เช่น "1,1,5.0" ขั้นต่อไปคือ split และแปลงชนิด

~~~python
parsed = (
    raw
    .map(lambda line: line.split(","))
    .map(lambda fields: [
        int(fields[0]),
        int(fields[1]),
        float(fields[2]),
    ])
)

parsed.take(5)
~~~

การเปลี่ยนรูปข้อมูลคือ

| ขั้น | ตัวอย่างหนึ่ง record |
|---|---|
| raw text | "1,1,5.0" |
| split | ["1", "1", "5.0"] |
| type conversion | [1, 1, 5.0] |

ถ้าไม่แปลงชนิด ค่า "10" กับ "2" จะเป็น string และอาจเรียงแบบตัวอักษรผิดจากตัวเลข

## 9. กำหนด Schema และสร้าง DataFrame

~~~python
from pyspark.sql.types import (
    StructType,
    StructField,
    IntegerType,
    FloatType,
)

schema = StructType([
    StructField("x", IntegerType(), nullable=True),
    StructField("y", IntegerType(), nullable=True),
    StructField("z", FloatType(), nullable=True),
])

data_df = spark.createDataFrame(parsed, schema)
~~~

ตรวจข้อมูลและ Schema

~~~python
data_df.show(16)
data_df.printSchema()
data_df.count()
~~~

count ต้องได้ 16 และ Schema ต้องเป็น

~~~text
root
 |-- x: integer (nullable = true)
 |-- y: integer (nullable = true)
 |-- z: float (nullable = true)
~~~

## 10. สำรวจ Pattern ในไฟล์ข้อมูล

ไฟล์มี x และ y ตั้งแต่ 1 ถึง 4 ทุกคู่ รวม 4 × 4 = 16 rows ส่วน z มีค่า 1.0 หรือ 5.0 ตาม pattern

ตรวจจำนวนค่าของ z

~~~python
data_df.groupBy("z").count().orderBy("z").show()
~~~

ผลควรเป็น

| z | count |
|---:|---:|
| 1.0 | 8 |
| 5.0 | 8 |

ตรวจค่าเฉลี่ย z ตาม x

~~~python
data_df.groupBy("x").avg("z").orderBy("x").show()
~~~

ทุกค่า x มี z เป็น 1.0 สองครั้งและ 5.0 สองครั้ง ค่าเฉลี่ยจึงเป็น 3.0 เท่ากัน

หากดู pattern ของแต่ละคู่ จะพบว่า x = 1 และ 2 ให้ค่า 5.0 เมื่อ y เป็นเลขคี่ ส่วน x = 3 และ 4 ให้ค่า 5.0 เมื่อ y เป็นเลขคู่ การดูเพียงค่าเฉลี่ยตาม x จะซ่อน interaction นี้ไว้

เพิ่มคอลัมน์เพื่ออธิบาย pattern

~~~python
from pyspark.sql import functions as F

with_parity = (
    data_df
    .withColumn("x_group", F.when(F.col("x") <= 2, "low").otherwise("high"))
    .withColumn("y_parity", F.when(F.col("y") % 2 == 0, "even").otherwise("odd"))
)

with_parity.groupBy(
    "x_group",
    "y_parity",
).avg("z").orderBy(
    "x_group",
    "y_parity",
).show()
~~~

ตัวอย่างนี้ชี้ให้เห็นว่าการ aggregate ผิดระดับอาจกลบ pattern ของข้อมูล การเลือก grouping columns ต้องสัมพันธ์กับคำถาม ไม่ใช่เลือกเพียงเพราะคำนวณได้

## 11. วิธีอ่านไฟล์แบบ DataFrame โดยตรง

เส้นทาง RDD ในสไลด์ช่วยให้เห็นการ parse ทีละขั้น แต่ไฟล์ CSV มาตรฐานสามารถอ่านด้วย DataFrame reader โดยตรง

~~~python
data_df_direct = (
    spark.read
    .option("header", False)
    .schema(schema)
    .csv("/user/cloudera/test.data")
)

data_df_direct.show(5)
data_df_direct.printSchema()
~~~

เมื่อกำหนด Schema แล้ว reader แปลงชนิดข้อมูลให้ตามที่ระบุ วิธีนี้ลดโค้ด parsing และจัดการรูปแบบ CSV ได้ดีกว่า line.split(",") โดยเฉพาะไฟล์ที่มี quoted fields

เส้นทางทั้งสองเปรียบเทียบได้ดังนี้

| วิธี | เหมาะเมื่อ |
|---|---|
| textFile → split → createDataFrame | ต้องเรียนรู้กลไกหรือ format เฉพาะมาก |
| spark.read.schema(...).csv(...) | ข้อมูลเป็น CSV มาตรฐานและต้องการงานที่ดูแลต่อได้ง่าย |

## 12. ตรวจ Logical และ Physical Plan

สร้าง query

~~~python
summary = (
    data_df
    .filter(F.col("z") >= 5.0)
    .groupBy("x")
    .count()
    .orderBy("x")
)
~~~

ก่อนเรียก show สามารถดูแผนด้วย

~~~python
summary.explain(mode="formatted")
summary.show()
~~~

ให้สังเกต Scan, Filter, Aggregate, Exchange และ Sort คำว่า Exchange มักสื่อถึงการเคลื่อนข้อมูลระหว่าง partitions การดู explain เชื่อม syntax ระดับ DataFrame กับสิ่งที่ Spark ต้องทำจริง

## 13. Validation ที่ควรทำก่อนเชื่อผล

ตรวจจำนวน rows

~~~python
assert data_df.count() == 16
~~~

ตรวจว่าทุก x และ y อยู่ในช่วง 1–4

~~~python
invalid_xy = data_df.filter(
    (F.col("x") < 1)
    | (F.col("x") > 4)
    | (F.col("y") < 1)
    | (F.col("y") > 4)
)

assert invalid_xy.count() == 0
~~~

ตรวจค่า z

~~~python
invalid_z = data_df.filter(
    ~F.col("z").isin(1.0, 5.0)
)

assert invalid_z.count() == 0
~~~

Schema ตรวจชนิดข้อมูล แต่ไม่ได้บอกว่า integer ทุกค่าต้องอยู่ระหว่าง 1–4 Validation rules จึงเป็นอีกชั้นหนึ่งที่ต้องกำหนดตามความหมายของข้อมูล

## 14. Troubleshooting

### NameError: sqlContext is not defined

ใช้ spark.createDataFrame() และ spark.sql() แทน sqlContext ใน Spark รุ่นปัจจุบัน

### AttributeError เกี่ยวกับ registerAsTable

ใช้ createOrReplaceTempView()

~~~python
df.createOrReplaceTempView("person_table")
~~~

### SyntaxError จาก quotation marks

เอกสารใช้ smart quotes บางตำแหน่ง ให้พิมพ์ " หรือ ' มาตรฐานของ Python ใหม่

### Input path does not exist

ตรวจ HDFS path

~~~bash
hadoop fs -ls /user/cloudera
~~~

Local path กับ HDFS path เป็นคนละพื้นที่ การมีไฟล์ใน working directory ไม่ได้แปลว่า sc.textFile("/user/cloudera/test.data") จะพบไฟล์ใน HDFS

### ValueError ระหว่าง int หรือ float

อาจมี header, ช่องว่าง, จำนวน fields ไม่ครบ หรือข้อความแทนตัวเลข ตรวจ raw rows ก่อน

~~~python
raw.take(20)
~~~

### ลำดับผล groupBy เปลี่ยน

Distributed DataFrame ไม่รับประกันลำดับจนกว่าจะใช้ orderBy ควรเปรียบเทียบค่าตาม key ไม่เปรียบเทียบตำแหน่งของ row

### ใช้ collect แล้ว Driver memory เต็ม

ใช้ show หรือ take สำหรับตรวจตัวอย่าง และเขียนผลลง storage เมื่อข้อมูลใหญ่

## 15. แบบฝึกหัดต่อยอดพร้อมแนวคำตอบ

### 1. เลือกเฉพาะ rows ที่ z เท่ากับ 5.0

~~~python
high = data_df.filter(F.col("z") == 5.0)
high.orderBy("x", "y").show()
~~~

ควรได้ 8 rows Validation ด้วย high.count() == 8

### 2. นับจำนวน z = 5.0 แยกตาม x

~~~python
high.groupBy("x").count().orderBy("x").show()
~~~

แต่ละ x มีจำนวน 2 เพราะแต่ละกลุ่มมี z = 5.0 สองตำแหน่ง

### 3. เขียนด้วย SQL

~~~python
data_df.createOrReplaceTempView("test_data")

spark.sql("""
    SELECT x, COUNT(*) AS high_count
    FROM test_data
    WHERE z = 5.0
    GROUP BY x
    ORDER BY x
""").show()
~~~

ผลควรเหมือน DataFrame API เพราะทั้งสองใช้ Spark SQL engine

### 4. หาผลรวม z แยกตาม y

~~~python
data_df.groupBy("y").sum("z").orderBy("y").show()
~~~

ทุก y มีค่า 1.0 สองครั้งและ 5.0 สองครั้ง ผลรวมจึงเป็น 12.0 ทุกกลุ่ม

### 5. เพราะเหตุใดค่าเฉลี่ย z ตาม x จึงมองไม่เห็น pattern ทั้งหมด

แต่ละ x มีค่า 1.0 และ 5.0 อย่างละสองครั้ง ค่าเฉลี่ยจึงเป็น 3.0 เหมือนกัน แต่ตำแหน่งของค่าขึ้นกับทั้งกลุ่มของ x และ parity ของ y การ aggregate ตาม x เพียงตัวเดียวจึงลบข้อมูล interaction ระหว่าง x กับ y

## สรุป

Lab นี้เริ่มจาก tuples และไฟล์ข้อความ เปลี่ยนเป็น RDD แล้วเพิ่ม Schema เพื่อสร้าง DataFrame เมื่อ Spark รู้ชื่อและชนิดของ columns ผู้ใช้จึงใช้ select, filter, orderBy, groupBy และ SQL ได้ Temporary view เป็นชื่อชั่วคราวที่ชี้ไปยัง DataFrame ไม่ใช่การสร้างสำเนาข้อมูลถาวร

ส่วนสำคัญไม่ใช่จำ method ให้ครบ แต่ต้องติดตามให้ได้ว่าแต่ละขั้นรับข้อมูลรูปใด คืน DataFrame ที่มี Schema อย่างไร operation ใดเป็น lazy และ aggregation ใดทำให้เกิด shuffle เมื่อรวมความเข้าใจนี้กับการตรวจ row count, value range และ expected result จะสามารถใช้ Spark SQL กับข้อมูลจริงได้อย่างน่าเชื่อถือขึ้น

## แหล่งอ้างอิง

- เอกสารปฏิบัติ lab06_spark_sql.pdf หน้า 1–5
- ชุดข้อมูล lab06_spark_sql_test.data จำนวน 16 rows
- [Apache Spark: Spark SQL, DataFrames and Datasets Guide](https://spark.apache.org/docs/latest/sql-programming-guide.html)
- [Apache Spark: CSV Data Source](https://spark.apache.org/docs/latest/sql-data-sources-csv.html)
- [Apache Spark: DataFrame API](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/dataframe.html)
