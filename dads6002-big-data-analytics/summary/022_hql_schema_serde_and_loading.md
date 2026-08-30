# บทที่ 022: HQL, Schema, SerDe and Loading

> **จากเอกสาร:** `dads6002_02_hive.pdf` หน้า 6–15  
> [← บทที่ 021](021_hive_foundations_and_storage.md) | [สารบัญ](README.md) | [บทถัดไป →](023_hive_analytics_and_joins.md)

## Learning Objectives

สร้าง database/table, เลือก managed หรือ external, อธิบาย SerDe และ schema-on-read, เลือก data types และออกแบบ load/validation workflow ได้

## 1. จาก CLI สู่ HQL

สไลด์ใช้ Hive CLI เช่น `hive`, `hive -e` และ `hive -f` เพื่อสอน interactive, inline และ script execution แนวคิดสำคัญยังใช้ได้ แต่ระบบใช้งานจริงมักเชื่อม HiveServer2 ผ่าน Beeline เพื่อแยก client จาก service และรองรับ authentication/authorization

```sql
CREATE DATABASE IF NOT EXISTS log_data;
USE log_data;
SHOW TABLES;
DESCRIBE apache_log;
```

DDL เปลี่ยน metadata ส่วน `SELECT` อ่านข้อมูล และ `INSERT`/`LOAD` เปลี่ยนสิ่งที่ table อ้างถึงหรือเก็บ การ run สำเร็จไม่ได้ยืนยันว่า row ถูก parse ถูกต้อง จึงต้องมี validation หลัง load

## 2. Managed Table กับ External Table

Managed table หมายถึง Hive เป็นเจ้าของ lifecycle ของ metadata และ data โดยปกติ `DROP TABLE` ลบทั้งคู่ External table หมายถึง Hiveจัดการ metadata แต่ไฟล์ถูกจัดการจากภายนอก เมื่อ drop จะลบ metadata แต่เก็บไฟล์ไว้ พฤติกรรมละเอียดขึ้นกับ version/configuration จึงควรทดสอบใน environment และไม่ใช้ `DROP` เป็นการทดลองกับ production data

| คำถาม | Managed | External |
|---|---|---|
| ใครควบคุม lifecycle ไฟล์ | Hive | pipeline/system ภายนอก |
| ใช้เมื่อ | intermediate/curated data ที่ Hive เป็นเจ้าของ | shared/raw data หรือหลาย engine ใช้ร่วมกัน |
| ความเสี่ยงหลัก | drop แล้วสูญเสีย data | metadata กับ files drift |

ตัวอย่าง DDL ที่แก้ quote และ syntax ให้รันได้:

```sql
CREATE TABLE memo (
    line_no STRING,
    line_text STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE;

CREATE EXTERNAL TABLE memo_external (
    line_no STRING,
    line_text STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '\t'
STORED AS TEXTFILE
LOCATION '/user/student/external_table';
```

## 3. Schema-on-read คืออะไร

Hive ผูก schema ตอนอ่าน ไม่ได้ตรวจทุก field แบบ transactional database ตอน `LOAD DATA` หาก type หรือจำนวน fields ไม่ตรง query อาจคืน `NULL` แทน การโหลดสำเร็จจึงหมายถึงไฟล์ถูกย้าย/อ้างถึงสำเร็จ ไม่ได้หมายถึงข้อมูลมีคุณภาพ

ตัวอย่าง input ที่คาดว่า `po_id INT, amount DOUBLE`:

```text
1001	250.50
ABC	300.00
1003	missing
```

แถวสองมี `po_id` ผิดชนิดและแถวสามมี `amount` ผิดชนิด ผลลัพธ์อาจมี `NULL` การตรวจขั้นต่ำคือ total rows, null-by-column, rejected-pattern count และยอดรวมเทียบ source

## 4. SerDe: สะพานระหว่าง bytes กับ columns

SerDe ย่อจาก Serializer/Deserializer ฝั่งอ่าน Deserializer แปล record ในไฟล์เป็น fields ที่ Hive เข้าใจ ฝั่งเขียน Serializer แปลง row กลับเป็นรูปแบบจัดเก็บ SerDe ไม่ใช่เพียง delimiter แต่สามารถ parse format ที่ซับซ้อน เช่น web log ด้วย regular expression

คำศัพท์ต้องอ่านตามลำดับ: raw line → record boundary → pattern/delimiter → fields → type conversion → Hive row หาก regex จับกลุ่มไม่ครบ column mapping จะเลื่อนหรือกลายเป็น `NULL`

สไลด์แสดง `RegSerde` แต่ class ที่ใช้จริงควรตรวจจาก Hive distribution และมักพบ `RegexSerDe` การคัดลอก class name จากสไลด์โดยไม่ตรวจ JAR/version เป็น failure mode สำคัญ

## 5. Regex ที่จำเป็นต่อการอ่าน log

| สัญลักษณ์ | ความหมาย | ตัวอย่าง |
|---|---|---|
| `^`, `$` | ต้นและท้าย string | `^abc$` ตรงทั้ง string |
| `*`, `+`, `?` | 0+, 1+, 0/1 ครั้ง | `ab+c` ต้องมี b อย่างน้อยหนึ่ง |
| `{m,n}` | จำนวนครั้งเป็นช่วง | `b{3,5}` |
| `()` | group | `(ab)+` |
| `|` | OR | `GET|POST` |
| `[]` | character class | `[0-9]` |
| `.` | อักขระใดหนึ่งตัว | `a.[0-9]` |
| `\` | escape | ใช้กับอักขระพิเศษ |

ควร anchor pattern และทดสอบกับ valid/invalid samples ก่อนใช้ เพราะ regex ที่ permissive เกินไปอาจ parse ผิดอย่างเงียบ ๆ

## 6. Data Types

Primitive types ในสไลด์มี integer, floating point, boolean, string และ timestamp คำว่า `bint` ในสไลด์ควรแก้เป็น `BIGINT` ใน HQL และ precision ของ timestamp ต้องตรวจตาม version

Complex types ช่วยรักษาโครงสร้างซ้อน:

```sql
ARRAY<STRING>
MAP<STRING, INT>
STRUCT<name:STRING, age:INT>
```

เลือก type ให้สอดคล้องกับ semantics ไม่ใช่เพียงให้ load ผ่าน เช่นรหัส vendor ที่มี leading zero ควรเป็น `STRING` ไม่ใช่ integer และเงินควรใช้ `DECIMAL(precision, scale)` เมื่อความแม่นยำสำคัญ มากกว่า FLOAT

## 7. Loading Data

```sql
LOAD DATA INPATH '/user/student/apache.log'
OVERWRITE INTO TABLE apache_log;
```

`OVERWRITE` แทนข้อมูลเดิมใน target scope จึงต้องตรวจ path และ partition อย่างเข้มงวด ส่วน `INSERT OVERWRITE ... SELECT` สร้างข้อมูลจาก query และเหมาะกับ transformation ที่ต้อง parse/clean

### Safe loading workflow

1. สำรวจ sample และนิยาม schema contract
2. สร้าง external staging table เพื่อเก็บ raw data
3. ตรวจ row count, parse failures และ null distribution
4. insert เข้า curated table ด้วย explicit casts/filters
5. reconcile count และ business totals
6. เก็บ query/version เพื่อ reproducibility

## Guided Lab

ใช้ไฟล์ตัวอย่าง:

```text
1001	V001	250.50
1002	V002	175.00
BAD	V003	300.00
```

สร้าง staging ทุก field เป็น STRING แล้วสร้าง curated table ที่ `po_id BIGINT`, `vendor_id STRING`, `amount DECIMAL(12,2)` ใช้ conditional cast หรือ regex filter แยก invalid row ก่อน insert คาดว่า curated มี 2 rows และ reject มี 1 row

Validation:

```sql
SELECT COUNT(*) AS source_rows FROM po_staging;
SELECT COUNT(*) AS valid_rows FROM po_curated;
SELECT COUNT(*) AS rejected_rows
FROM po_staging
WHERE po_id = '' OR po_id RLIKE '[^0-9]';
```

สมการ reconciliation เชิงแนวคิดคือ `source_rows = valid_rows + rejected_rows` หากไม่เท่าต้องหาข้อมูลซ้ำ สูญหาย หรือ classification overlap

## Troubleshooting

| อาการ | สาเหตุ | การตรวจ/แก้ |
|---|---|---|
| ทุก column เป็น NULL | delimiter/SerDe ผิด | ดู raw bytes และ table DDL |
| บาง field เลื่อน | regex groups ไม่ตรง columns | trace group ทีละตำแหน่ง |
| LOAD สำเร็จแต่ count เป็น 0 | path/location/partition ผิด | `DESCRIBE FORMATTED`, list files |
| DROP แล้วข้อมูลหาย | ใช้ managed table | restore/backup และแก้ ownership design |
| amount เพี้ยน | FLOAT/locale/type mismatch | ใช้ DECIMAL และ validation |

## Progressive Practice พร้อมเฉลย

**1. ทำไม load สำเร็จยังไม่พอ?** เพราะ schema-on-read อาจยังไม่ parse/type-check จน query ทำงาน

**2. Raw files ถูกใช้ร่วมกับ Spark ควรเลือก table ใด?** External table เหมาะกว่าเพราะ Hiveไม่ควรเป็นเจ้าของ lifecycle เพียงระบบเดียว

**3. รหัส `00125` ควรเป็น INT หรือ STRING?** STRING เพราะเลขศูนย์นำหน้าเป็นส่วนของ identifier ไม่ใช่ปริมาณ

## Likely Exam Focus

- managed vs external และผลของ DROP
- schema-on-read กับ NULL/type mismatch
- SerDe มี input/output และหน้าที่อะไร
- regex symbols จากตัวอย่าง
- LOAD vs INSERT และอันตรายของ OVERWRITE
- primitive/complex types และการเลือก type

## Mastery Checklist

- เขียน DDL ที่กำหนด ownership, format และ location ได้
- trace raw line ผ่าน SerDe สู่ typed row ได้
- ออกแบบ staging-to-curated workflow พร้อม reject table ได้
- พิสูจน์ reconciliation ด้วย count และ business totals ได้

## Source Coverage และ References

ครอบคลุม PDF หน้า 6–15: CLI/HQL DDL, managed/external, RegexSerDe, regex, types, schema-on-read และ loading

- [Apache Hive DDL](https://hive.apache.org/docs/latest/language/languagemanual-ddl/)
- [Managed vs. External Tables](https://hive.apache.org/docs/latest/language/managed-vs--external-tables/)
- [Apache Hive Tutorial](https://hive.apache.org/docs/latest/user/tutorial/)
