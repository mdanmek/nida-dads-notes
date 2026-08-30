# บทที่ 02.1: Hive Foundations and Storage Design

> **จากเอกสาร:** `dads6002_02_hive.pdf` หน้า 1–5  
> [← สารบัญ](000_readme.md) | [บทที่ 02.2 →](022_hql_schema_serde_and_loading.md)

## Learning Objectives

หลังจบบทนี้ควรสามารถอธิบาย Hive แบบ end-to-end, แยก metadata ออกจาก data, เปรียบเทียบ table/partition/bucket และออกแบบ physical layout จาก query pattern ได้

## Prerequisites และระดับความลึก

ควรรู้ว่า HDFS แบ่งไฟล์เป็น blocks และ MapReduce เป็นงานประมวลผลแบบ batch หัวข้อ Core คือ Hive mental model, Metastore และ partition design; ACID/bucketing เป็น Supporting และ legacy indexing เป็น Reference

บทนี้ต่อจากชุด Hadoop โดยตรง ในบท 01.3 เราต้องอธิบายให้ MapReduce รู้ว่าจะสร้าง key อะไรและรวมค่าอย่างไร แม้คำถามจะเป็นเพียง “ยอดจัดซื้อต่อโรงพยาบาลเท่าไร” ภาระดังกล่าวเหมาะกับวิศวกรที่ต้องควบคุมอัลกอริทึม แต่ไม่เหมาะกับนักวิเคราะห์ที่คิดเป็นตาราง คอลัมน์ การกรอง และการรวมยอด Hive จึงไม่ได้มาแทน HDFS หรือ MapReduce แต่เพิ่มชั้นภาษาและ metadata เพื่อแปลคำถามเชิงตารางให้กลายเป็นแผนประมวลผลบนระบบกระจาย

## 1. Hive คืออะไร

### ปัญหาก่อนมี Hive

HDFS เก็บข้อมูลกระจายได้ แต่ไม่ได้มี table schema หรือ SQL interface ในตัว หากนักวิเคราะห์ต้องเขียน mapper และ reducer สำหรับทุกคำถาม เช่นยอดขายต่อเดือน ต้นทุนในการพัฒนาและตรวจสอบจะสูง Hive จึงเป็น data warehouse framework บน Hadoop ที่ให้ผู้ใช้ประกาศโครงสร้างและเขียนภาษาคล้าย SQL ซึ่งเรียกว่า HiveQL หรือ HQL

Input ของ Hive คือคำสั่ง HQL และ metadata ของ table ส่วน output อาจเป็น result set หรือไฟล์ที่เขียนกลับ storage Hive ทำหน้าที่ parse, validate, optimize และสร้าง execution plan แล้วมอบงานจริงให้ execution engine จึงไม่ใช่ storage engine ที่แทน HDFS และไม่ใช่ OLTP database สำหรับการแก้ทีละแถวอย่างถี่ ๆ

### ตัวอย่างเล็กที่สุด

สมมติ HDFS มีไฟล์ log หนึ่งพันไฟล์ เรากำหนด table ที่บอกว่าแต่ละ record มี `hospital`, `event_date` และ `amount` จากนั้นเขียน:

```sql
SELECT hospital, SUM(amount) AS total_amount
FROM purchase_log
GROUP BY hospital;
```

Hive อ่าน schema จาก Metastore วางแผน scan และ aggregation แล้ว engine ประมวลผลไฟล์ ข้อดีคือผู้ใช้คิดในระดับ table/query แทนการเขียน distributed program เอง

### Mental model สองรอบ: จากไฟล์สู่ตารางที่ query ได้

รอบแรกให้นึกถึงโกดังที่มีแฟ้มรายการจัดซื้อหลายล้านบรรทัด HDFS รับผิดชอบว่ากระดาษแต่ละกองอยู่ที่ใดและยังมีสำเนาเมื่อชั้นวางหนึ่งเสีย แต่ HDFS ไม่รู้ว่าอักขระช่วงแรกคือ `hospital_id` หรือช่วงท้ายคือ `amount` Hive เพิ่ม “บัตรรายการ” ที่บอกชื่อชุดข้อมูล ตำแหน่งไฟล์ ชื่อคอลัมน์ ชนิดข้อมูล และกติกาอ่านแต่ละบรรทัด เมื่อผู้ใช้ถามด้วย HQL ระบบจึงเปิดบัตรรายการก่อน แล้วค่อยส่งคนไปอ่านเฉพาะแฟ้มที่เกี่ยวข้อง

รอบที่สองใช้ศัพท์ทางการ บัตรรายการคือ metadata ใน Hive Metastore แฟ้มจริงคือ files ใน HDFS หรือ storage อื่น นิยาม table เชื่อมสองส่วนเข้าด้วยกัน และ execution engine เป็นผู้รัน physical plan ที่ Hive สร้าง ดังนั้น input ของ query ไม่ได้มีเพียงไฟล์ แต่มีทั้ง HQL, metadata และ file layout ส่วน output อาจเป็น result set หรือ files ของ table ใหม่

ความเปรียบเทียบแบบโกดังมีข้อจำกัด เพราะ Hive ไม่ได้อ่านไฟล์ทีละแฟ้มด้วยคน และ optimizer อาจปรับลำดับ operators หรือเลือก engine ต่างกัน แต่ภาพนี้ช่วยกันความเข้าใจผิดสำคัญสามข้อ: Hive ไม่ได้เก็บข้อมูลทั้งหมดใน Metastore, HQL ไม่ได้ทำงานแทน execution engine และการสร้าง table ไม่จำเป็นต้องคัดลอกไฟล์เสมอไป

## 2. Data กับ Metadata อยู่คนละที่

Metastore เป็นบริการเก็บ metadata เช่น database, table name, columns, types, location, partition และ SerDe โดยทั่วไป metadata อยู่ใน relational database เพราะต้องแก้ไขและค้นอย่างมีประสิทธิภาพ ส่วน record จำนวนมากยังอยู่ใน distributed storage

เมื่อ query เริ่มขึ้น Hive ต้องถาม Metastore ก่อนว่า table อยู่ที่ใดและอ่านอย่างไร แต่ไฟล์ข้อมูลไม่ไหลผ่านฐานข้อมูล Metastore ความเข้าใจผิดว่า “Hive table เก็บทุก row ใน MySQL” จึงไม่ถูกต้อง

### End-to-end query flow

1. Client ส่ง HQL
2. Hive parse syntax และ resolve ชื่อ table/column
3. Hive อ่าน metadata จาก Metastore
4. Optimizer สร้าง logical/physical plan
5. Execution engine อ่านไฟล์จาก storage และทำ operators
6. Hive ส่งผลกลับหรือเขียนเป็น table ใหม่

ถ้า Metastore ใช้งานไม่ได้ query ใหม่จะ resolve metadata ไม่ได้ แม้ไฟล์จริงยังอยู่ หากไฟล์ถูกลบแต่ metadata ยังอยู่ query อาจพบ path ว่างหรือ file-not-found ทั้งสองกรณีแสดงว่าความพร้อมของ metadata และ data ต้องตรวจแยกกัน

ลองตาม query ยอดจัดซื้อของเดือนสิงหาคม ผู้ใช้ส่ง HQL ไปยังบริการ Hive ระบบตรวจว่ามี table และ columns จริง จากนั้นถาม Metastore ว่า table ชี้ไป directory ใด แบ่ง partition ด้วยอะไร และใช้ file format/SerDe แบบใด Optimizer จึงตัด partition เดือนอื่นออกและสร้างแผน aggregation Execution engine อ่าน bytes จาก storage แปลงเป็น rows รวมยอด และส่งคำตอบกลับ ถ้า `month='08'` ไม่ได้เป็น partition predicate ระบบอาจต้องเปิดไฟล์ทั้งปี แม้คำตอบสุดท้ายเหมือนกัน นี่คือจุดที่ logical query เชื่อมกับ physical layout

## 3. ACID และข้อจำกัดเชิงงาน

สไลด์อธิบายว่า Hive สืบทอดแนวคิด write-once/read-many ของ HDFS และการ `INSERT`, `UPDATE`, `DELETE` ไม่เหมาะกับการเปลี่ยนแปลงถี่ ๆ ใน Hive แบบ ACID การเปลี่ยนแปลงสร้าง delta files และ compactor ทำงานเบื้องหลัง ภาษาปัจจุบันควรแยกว่า minor compaction รวม delta files ส่วน major compaction รวม delta กับ base file เป็น base ใหม่ ตาม [Hive Transactions](https://hive.apache.org/docs/latest/user/hive-transactions/)

ดังนั้น “Hive รองรับ UPDATE” ไม่ได้แปลว่าเหมาะแทน transactional system หาก use case คือ payment status ที่ต้องแก้ทันทีและอ่านด้วย latency ต่ำ ควรเก็บระบบต้นทางใน OLTP database แล้วนำสำเนามาวิเคราะห์ใน Hive

## 4. Table, Partition และ Bucket

### Table

Table เป็น logical schema ที่ผูกกับ location หนึ่งใน storage ไฟล์ถูก serialize ตาม file format และ Hive ใช้ schema/SerDe แปล bytes เป็น columns

### Partition

Partition แยก table เป็น subdirectories ตามค่าคอลัมน์ เช่น:

```text
/sales/country=TH/year=2026/month=08/
/sales/country=TH/year=2026/month=09/
```

ถ้า query มี predicate ที่ตรงกับ partition column Hive สามารถทำ partition pruning และไม่อ่าน directory ที่ไม่เกี่ยวข้อง ประโยชน์เกิดจาก “ลดไฟล์ที่ scan” ไม่ใช่เพราะ partition ทำให้ทุก query เร็วโดยอัตโนมัติ

การ partition ด้วย `po_id` ซึ่งมีหลายล้านค่าอาจสร้าง directories และ metadata จำนวนมาก จึงมักเลือกคอลัมน์ที่ปรากฏบ่อยใน filter และมี cardinality พอเหมาะ เช่น date/month/region

สมมติ table มีข้อมูล 5 ปี เดือนละ 100 GB และผู้ใช้ถามเฉพาะเดือนสิงหาคม 2026 หากจัด partition เป็น `year/month` และ predicate ระบุสองคอลัมน์ Hive มีโอกาสอ่านเพียง 100 GB แทน 6 TB แต่ถ้าจัด partition ด้วย `po_id` หลายล้านค่า เราจะได้ directory เล็กจำนวนมหาศาล Metastore ต้องติดตาม partitions มากขึ้นและเกิด small-files overhead การออกแบบ partition จึงเป็นการแลก “ลดปริมาณ scan” กับ “เพิ่มจำนวนหน่วยที่ต้องจัดการ” ไม่ใช่ยิ่งละเอียดแล้วยิ่งดี

### Bucket

Bucket ใช้ hash ของคอลัมน์กำหนดว่า row ไปไฟล์ใดภายใน table หรือ partition เช่น 8 buckets:

```text
bucket_number = hash(vendor_id) mod 8
```

Bucket ไม่เหมือน partition เพราะค่าจริงไม่ได้กลายเป็นชื่อ directory ทุกค่า การ bucket อาจช่วย sampling หรือ join บางรูปแบบ แต่ต้องแลกกับการควบคุมจำนวนไฟล์และการเขียนข้อมูลให้สอดคล้องกับนิยาม

ความสัมพันธ์ที่ควรจำคือ partition ตัดข้อมูลด้วยค่าที่ผู้ใช้มักเขียนใน `WHERE` ส่วน bucket กระจาย rows ภายใน partition ด้วย hash เช่น partition เดือนสิงหาคมอาจมี 8 bucket files ตาม `vendor_id` ผู้ใช้ไม่เลือก directory ชื่อ vendor แต่ hash จะกำหนดไฟล์ปลายทาง การประกาศ `CLUSTERED BY` ใน metadata โดยที่ขั้นเขียนไม่สร้าง layout ตามนั้นทำให้ table “บอกว่ามี bucket” แต่ไฟล์จริงไม่รักษาสัญญา เอกสาร Apache จึงเตือนว่าคุณสมบัติ bucketing ต้องถูกทำให้เกิดจริงตอนเขียน ไม่ใช่เชื่อจาก DDL อย่างเดียว [Apache Hive Bucketed Tables](https://hive.apache.org/docs/latest/language/languagemanual-ddl-bucketedtables/)

## สะพานไปสู่ HQL และ Schema-on-read

เมื่อรู้แล้วว่า Hive เชื่อม metadata กับ files อย่างไร คำถามถัดไปคือเราจะสร้าง metadata นั้นอย่างไร และถ้าไฟล์ดิบไม่เป็นตารางเรียบร้อย Hive จะแยก bytes เป็น columns ได้อย่างไร บท 02.2 จึงเริ่มจาก HQL สำหรับสร้าง database/table แล้วตามด้วย managed/external ownership, schema-on-read และ SerDe ลำดับนี้สำคัญ เพราะ syntax `CREATE TABLE` จะมีความหมายก็ต่อเมื่อเราเข้าใจว่ากำลังประกาศสัญญาการอ่านและ lifecycle ของไฟล์ ไม่ใช่เพียงสร้างกล่องว่างแบบฐานข้อมูลธุรกรรม

| กลไก | หน่วยกายภาพ | เหมาะเมื่อ | ความเสี่ยง |
|---|---|---|---|
| Table | directory หลัก | แยก dataset/schema | table มากเกินไป |
| Partition | subdirectory ตามค่า | filter ซ้ำบนคอลัมน์ cardinality พอเหมาะ | small partitions/Metastore overhead |
| Bucket | files จาก hash | sampling/join และกระจาย records | จำนวนไฟล์และ hash mismatch |

## 5. Index: เนื้อหาเดิมกับสถานะปัจจุบัน

สไลด์กล่าวว่า table สามารถทำ index เพื่อช่วยการค้นหา นี่เป็นข้อมูลเชิงประวัติศาสตร์ แต่ native Hive indexing ถูกนำออกตั้งแต่ Hive 3.0 ทางเลือกปัจจุบันรวม ORC/Parquet statistics, partition pruning และ materialized views ตาม [Apache Hive Language Manual](https://hive.apache.org/docs/latest/language/)

## Guided Design Lab

### สถานการณ์

ข้อมูล PO 1 TB ต่อปี ผู้ใช้ query รายเดือนและโรงพยาบาล โดยบางครั้งค้น vendor ข้ามปี

1. เสนอ table เดียว partition ด้วย `year`, `month`
2. พิจารณา `hospital` เป็น partition ชั้นถัดไปเฉพาะเมื่อจำนวนโรงพยาบาลและขนาดแต่ละ partition เหมาะสม
3. ไม่ partition ด้วย `vendor_id` หาก cardinality สูงมาก
4. ทดลองทำนายจำนวน directories เมื่อมี 12 เดือน × 60 โรงพยาบาล = 720 partitions ต่อปี
5. ตรวจว่าค่า filter ใน query ใช้ partition columns เพื่อให้ pruning เกิดจริง

### Deliberate failure

สร้าง query ที่ใช้ `year(CAST(event_time AS DATE)) = 2026` แทน predicate ตรงบน partition column `year = 2026` แล้วตรวจ `EXPLAIN` ว่า pruning เกิดหรือไม่ วิธีแก้คือใช้ partition predicate โดยตรงเมื่อ engine ไม่สามารถ infer ได้

## Validation และ Troubleshooting

| อาการ | ตรวจอะไร | สาเหตุที่เป็นไปได้ |
|---|---|---|
| query scan มากกว่าคาด | `EXPLAIN`, partition predicate | ไม่เกิด pruning |
| table มีแต่ไม่มีข้อมูล | table location และไฟล์ | metadata/data ไม่ตรงกัน |
| planning ช้า | จำนวน partitions | partition cardinality สูงเกินไป |
| update แล้วอ่านช้า | delta files/compaction | compaction backlog |

## Progressive Practice พร้อมเฉลย

**1. ทำไม Metastore ไม่ควรเก็บข้อมูลจริงทั้งหมด?** เพราะ metadata ต้อง update/query เร็ว แต่ record ปริมาณมากเหมาะกับ distributed storage การแยกช่วย scale ต่างบทบาท

**2. Query ส่วนใหญ่กรอง `month` แต่ไม่กรอง `vendor_id` ควร partition ด้วยอะไร?** ใช้ month เป็น candidate หลัก ส่วน vendor_id cardinality สูงและไม่ใช่ filter หลักจึงไม่ควรเป็น partition โดยอัตโนมัติ

**3. Hive เหมาะกับการแก้ inventory ทุก 20 ms หรือไม่?** ไม่เหมาะ เพราะ batch/analytical architecture และ ACID file compaction ไม่ได้ออกแบบแทน low-latency OLTP

## Likely Exam Focus

- Hive ทำให้ SQL เชื่อมกับ Hadoop อย่างไร
- Metastore เก็บอะไรและไม่เก็บอะไร
- table/partition/bucket ต่างกันอย่างไร
- เหตุใด partition design ผิดจึงทำให้ระบบแย่ลง
- ACID delta files และ compaction แก้ปัญหาอะไร

## Mastery Checklist

- อธิบาย query flow โดยไม่เรียก Hive ว่า database ที่เก็บ row ใน Metastore
- ออกแบบ partition จาก query pattern และคำนวณจำนวน partitions ได้
- แยก partition กับ bucket ได้จาก layout และกลไก
- เลือก Hive หรือ OLTP พร้อมเหตุผลด้าน latency และ mutation pattern ได้

## Glossary และ Source Coverage

`Metastore` ฐาน metadata; `partition pruning` การตัด directory ที่ไม่ต้องอ่าน; `bucket` กลุ่มไฟล์จาก hash; `compaction` การรวม delta/base files

ครอบคลุม PDF หน้า 1–5: definition, HQL/plan, ACID/delta, Metastore, table, partition, bucket และ legacy index

## References

- `dads6002_02_hive.pdf`, หน้า 1–5
- [Apache Hive DDL](https://hive.apache.org/docs/latest/language/languagemanual-ddl/)
- [Hive Transactions](https://hive.apache.org/docs/latest/user/hive-transactions/)
- [Managed vs. External Tables](https://hive.apache.org/docs/latest/language/managed-vs--external-tables/)
