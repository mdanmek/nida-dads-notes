# บทที่ 02.2: HQL, Schema, SerDe and Loading

> **จากเอกสาร:** `dads6002_02_hive.pdf` หน้า 6–15  
> [← บทที่ 02.1](021_hive_foundations_and_storage.md) | [สารบัญ](000_readme.md) | [บทที่ 02.3 →](023_hive_analytics_and_joins.md)

## Learning Objectives

สร้าง database/table, เลือก managed หรือ external, อธิบาย SerDe และ schema-on-read, เลือก data types และออกแบบ load/validation workflow ได้

## พื้นฐานเชิงตารางก่อนเขียน HQL

ก่อนอ่าน syntax ให้กำหนดความหมายของข้อมูลก่อน **table** คือมุมมองเชิงแถวและคอลัมน์ของชุดข้อมูล หนึ่ง **row** แทนหนึ่งหน่วยตาม grain เช่นหนึ่งรายการ PO ไม่ใช่หนึ่ง vendor ส่วน **column** แทนคุณลักษณะของหน่วยนั้น เช่น `po_id`, `vendor_id` และ `amount` คอลัมน์ที่ใช้ระบุหน่วยโดยไม่ซ้ำเรียก key และจำนวนค่าที่แตกต่างกันเรียก cardinality หากเราไม่รู้ว่า “หนึ่งแถวแทนอะไร” เราจะเลือก type, partition และการตรวจจำนวนแถวไม่ได้

ใช้ตัวอย่างเดียวตลอดบท: ไฟล์ `po_202608.csv` มีหนึ่ง row ต่อหนึ่ง PO line โดย `po_line_id` ควรไม่ซ้ำ, `vendor_id` เป็นรหัส และ `amount` เป็นมูลค่า Hive ไม่ได้บังคับความเป็นเอกลักษณ์นี้แทนเราโดยอัตโนมัติ มันอ่านไฟล์ตาม schema ที่ประกาศ ดังนั้น key และ grain เป็น data contract ที่ pipeline ต้องตรวจเอง

## 1. จาก CLI สู่ HQL

สไลด์ใช้ Hive CLI เช่น `hive`, `hive -e` และ `hive -f` เพื่อสอน interactive, inline และ script execution แนวคิดสำคัญยังใช้ได้ แต่ระบบใช้งานจริงมักเชื่อม HiveServer2 ผ่าน Beeline เพื่อแยก client จาก service และรองรับ authentication/authorization

```sql
CREATE DATABASE IF NOT EXISTS log_data;
USE log_data;
SHOW TABLES;
DESCRIBE apache_log;
```

DDL เปลี่ยน metadata ส่วน `SELECT` อ่านข้อมูล และ `INSERT`/`LOAD` เปลี่ยนสิ่งที่ table อ้างถึงหรือเก็บ การ run สำเร็จไม่ได้ยืนยันว่า row ถูก parse ถูกต้อง จึงต้องมี validation หลัง load

ให้แยก “ภาษา” ออกจาก “ช่องทางส่งภาษา” HQL คือภาษาที่บอกสิ่งที่ต้องการ ส่วน Hive CLI, Beeline หรือ application client เป็นช่องทางส่งคำสั่ง สไลด์ใช้ Hive CLI เพื่อสาธิตได้ง่าย แต่ความรู้ที่ควรนำไปใช้คือ DDL/DML และ query semantics ไม่ใช่การยึดติดว่าต้องพิมพ์ผ่านคำสั่ง `hive` เท่านั้น ระบบจริงมักส่งคำสั่งผ่าน HiveServer2 และ Beeline เพื่อจัดการ session, authentication และหลายผู้ใช้ [Apache Hive documentation](https://hive.apache.org/docs/latest/)

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

การเลือกสองแบบนี้คือการตัดสิน “ownership” มากกว่าการตัดสิน “ความเร็ว” ถ้า pipeline อื่นเป็นผู้สร้าง raw files และ Spark/Hive ต้องใช้ร่วมกัน การให้ Hive ลบไฟล์เมื่อ drop metadata เป็นความเสี่ยง External table จึงเหมาะกว่า ในทางกลับกัน ถ้า Hive สร้าง intermediate result และรับผิดชอบวงจรชีวิตทั้งหมด managed table ทำให้ cleanup เป็นระบบกว่า ก่อนใช้ `DROP TABLE` ต้องตอบให้ได้ว่าใครเป็นเจ้าของ data และมีระบบใดอ้าง path เดียวกันอยู่บ้าง

## 3. Schema-on-read คืออะไร

Hive ผูก schema ตอนอ่าน ไม่ได้ตรวจทุก field แบบ transactional database ตอน `LOAD DATA` หาก type หรือจำนวน fields ไม่ตรง query อาจคืน `NULL` แทน การโหลดสำเร็จจึงหมายถึงไฟล์ถูกย้าย/อ้างถึงสำเร็จ ไม่ได้หมายถึงข้อมูลมีคุณภาพ

ตัวอย่าง input ที่คาดว่า `po_id INT, amount DOUBLE`:

```text
1001	250.50
ABC	300.00
1003	missing
```

แถวสองมี `po_id` ผิดชนิดและแถวสามมี `amount` ผิดชนิด ผลลัพธ์อาจมี `NULL` การตรวจขั้นต่ำคือ total rows, null-by-column, rejected-pattern count และยอดรวมเทียบ source

คำว่า schema-on-read ไม่ได้แปลว่า “ไม่มี schema” แต่แปลว่า schema ถูกนำมาใช้ตีความเมื่ออ่าน ข้อดีคือรับไฟล์ดิบได้เร็วและเปลี่ยนมุมมองได้ยืดหยุ่น ข้อเสียคือความผิดพลาดอาจถูกค้นพบช้า เช่น load เสร็จโดยไม่ error แต่เดือนถัดมาคอลัมน์สลับตำแหน่งจน `amount` กลายเป็น `NULL` ถ้า dashboard ใช้ `SUM(amount)` โดยไม่ตรวจ null ยอดอาจต่ำลงอย่างเงียบ ๆ ดังนั้น staging table ควรเก็บค่าดิบเป็น string แล้ว curated step ค่อยตรวจรูปแบบ cast และแยก rejected rows

## 4. SerDe: สะพานระหว่าง bytes กับ columns

SerDe ย่อจาก Serializer/Deserializer ฝั่งอ่าน Deserializer แปล record ในไฟล์เป็น fields ที่ Hive เข้าใจ ฝั่งเขียน Serializer แปลง row กลับเป็นรูปแบบจัดเก็บ SerDe ไม่ใช่เพียง delimiter แต่สามารถ parse format ที่ซับซ้อน เช่น web log ด้วย regular expression

คำศัพท์ต้องอ่านตามลำดับ: raw line → record boundary → pattern/delimiter → fields → type conversion → Hive row หาก regex จับกลุ่มไม่ครบ column mapping จะเลื่อนหรือกลายเป็น `NULL`

สไลด์แสดง `RegSerde` แต่ class ที่ใช้จริงควรตรวจจาก Hive distribution และมักพบ `RegexSerDe` การคัดลอก class name จากสไลด์โดยไม่ตรวจ JAR/version เป็น failure mode สำคัญ

ลองตาม raw line `PO1001|V020|1250.50` ทีละขั้น InputFormat/record reader กำหนดว่าหนึ่งบรรทัดคือหนึ่ง record จากนั้น Deserializer แยกสาม fields ด้วย delimiter หรือ regex แล้ว Hive แปลง field ที่สามเป็นชนิดตัวเลขตาม schema ผลคือ row `(PO1001, V020, 1250.50)` ที่ operators ใช้ต่อได้ หาก regex จับได้เพียงสอง groups คอลัมน์ที่สามไม่มีค่า หากจับ groups เกินหรือเรียงผิด ค่าจะไปอยู่ผิด column แม้ query ยังรันได้ การทดสอบ SerDe จึงต้องเทียบ raw sample กับผลลัพธ์ทีละ field ไม่ใช่ดูเฉพาะ `COUNT(*)`

Serializer ทำเส้นทางกลับกันเมื่อต้องเขียน row ออกเป็นไฟล์ แต่ไม่ควรเหมารวมว่า SerDe เป็นตัวตรวจ business rules มันแปล representation เท่านั้น กฎอย่าง `amount >= 0`, vendor ต้องมีใน master หรือ `po_line_id` ต้อง unique อยู่ในชั้น validation/curation

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

## สะพานจาก rows ที่อ่านได้ไปสู่ analytics

หลังบทนี้ Hive มองไฟล์เป็น typed rows ได้แล้ว แต่การมี rows ยังไม่ตอบคำถามธุรกิจ เราต้องกำหนด grain ของผลลัพธ์ด้วย `GROUP BY` และเชื่อมข้อมูลคนละ table ด้วย key การทำสองอย่างนี้อาจลดหรือเพิ่มจำนวนแถว: aggregation รวมหลาย rows เป็นหนึ่งกลุ่ม ส่วน join อาจสร้างหลาย combinations เมื่อ key ซ้ำ บท 02.3 จึงเริ่มจากการนับและรวมยอด แล้วค่อยสร้าง relational mental model สำหรับ match, unmatched row และ row multiplication ก่อนเลือกชนิด join

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
