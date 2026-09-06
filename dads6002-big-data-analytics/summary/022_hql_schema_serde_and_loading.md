# บทที่ 02.2: HQL, Schema, SerDe and Loading

> **จากเอกสาร:** [dads6002_02_hive.pdf หน้า 6–15](../lecture/dads6002_02_hive.pdf) และ [lab_02_hive.pdf หน้า 1–5](../lab/lab_02_hive.pdf)  
> [← บทที่ 02.1](021_hive_foundations_and_storage.md) | [สารบัญ](000_readme.md) | [บทที่ 02.3 →](023_hive_analytics_and_joins.md)

## เป้าหมายของบทเรียน

บทก่อนอธิบายว่า Hive ใช้ metadata ทำให้ไฟล์ถูกมองเป็นตาราง บทนี้จะตอบคำถามถัดไปว่าเราสร้างคำอธิบายนั้นอย่างไร และจะเกิดอะไรขึ้นเมื่อโครงสร้างที่ประกาศไม่ตรงกับข้อมูลจริง หลังอ่านจบ เราควรสร้าง database และ table ได้ เลือก managed หรือ external table จากผู้ที่เป็นเจ้าของไฟล์ อธิบาย schema-on-read และ SerDe ด้วยตัวอย่างหนึ่งบรรทัด ตลอดจนโหลดและตรวจข้อมูลโดยไม่สรุปว่า “คำสั่งรันผ่านเท่ากับข้อมูลถูกต้อง”

## พื้นฐานเชิงตารางก่อนเขียน HQL

ก่อนอ่าน syntax ต้องรู้ก่อนว่าเรากำลังอธิบายข้อมูลแบบใด **ตาราง (table)** คือมุมมองข้อมูลเป็นแถวและคอลัมน์ **แถว (row หรือ record)** หนึ่งแถวต้องแทนหน่วยบางอย่างที่ชัดเจน เช่นหนึ่งบรรทัดของใบสั่งซื้อ ไม่ใช่หนึ่ง vendor ขณะที่ **คอลัมน์ (column)** เก็บคุณลักษณะของหน่วยนั้น เช่นรหัสใบสั่งซื้อ รหัส vendor และจำนวนเงิน

คำว่า **grain** หมายถึงระดับรายละเอียดของหนึ่งแถว หากไฟล์มีหนึ่งแถวต่อ PO line แต่เราคิดว่าเป็นหนึ่งแถวต่อ PO ยอดรวมและจำนวนรายการจะถูกตีความผิดตั้งแต่ต้น **Key** คือคอลัมน์หรือชุดคอลัมน์ที่ใช้ระบุหรือเชื่อม records ส่วน **cardinality** ในบริบทนี้ช่วยบอกว่าคอลัมน์มีค่าที่แตกต่างกันมากน้อยเพียงใด ความหมายเหล่านี้ไม่ใช่ศัพท์เสริม แต่เป็นพื้นฐานสำหรับเลือก data type, partition และวิธีตรวจข้อมูล

ใช้ตัวอย่างเดียวตลอดบท: ไฟล์ `po_202608.csv` มีหนึ่งแถวต่อหนึ่ง PO line โดย `po_line_id` ควรไม่ซ้ำ, `vendor_id` เป็นรหัส และ `amount` เป็นมูลค่า ข้อตกลงว่าแต่ละคอลัมน์หมายถึงอะไรและยอมรับค่าแบบใดเรียกว่า **สัญญาข้อมูล (data contract)** Hive อ่านไฟล์ตาม schema ที่ประกาศ แต่ไม่ได้บังคับความเป็นเอกลักษณ์ของ `po_line_id` แทนเราโดยอัตโนมัติ Pipeline จึงต้องตรวจ grain, key และคุณภาพข้อมูลเอง

## 1. จาก CLI สู่ HQL

**HQL** คือภาษาที่ใช้บอก Hive ว่าต้องการสร้างโครงสร้าง เปลี่ยนข้อมูล หรืออ่านคำตอบ ส่วน **Command Line Interface (CLI)** เป็นเพียงช่องทางหนึ่งสำหรับส่งภาษา HQL เข้าไป สองสิ่งนี้ไม่ใช่เรื่องเดียวกัน เช่นเดียวกับภาษา SQL ที่สามารถส่งผ่านหลายโปรแกรมได้

สไลด์หน้า 6 ใช้ Hive CLI สามรูปแบบ การพิมพ์ `hive` เปิดหน้าจอ interactive สำหรับส่งคำสั่งทีละชุด `hive -e` ส่งคำสั่งสั้นจาก shell โดยไม่เปิดหน้าจอ และ `hive -f` รันคำสั่งหลายบรรทัดจากไฟล์ `.hql` แนวคิดเรื่อง interactive, inline และ script ยังสำคัญ แม้ระบบใหม่มักเชื่อม HiveServer2 ผ่าน Beeline แทน Hive CLI แบบเก่า

```sql
CREATE DATABASE IF NOT EXISTS log_data;
USE log_data;
SHOW TABLES;
DESCRIBE apache_log;
```

คำสั่ง `CREATE DATABASE` และ `CREATE TABLE` อยู่ในกลุ่ม **Data Definition Language (DDL)** เพราะสร้างหรือเปลี่ยนคำอธิบายโครงสร้าง `SELECT` อ่านข้อมูล ส่วน `INSERT` และ `LOAD` ทำให้ตารางมีข้อมูลให้อ่าน จุดสำคัญคือการสร้าง table สำเร็จยืนยันเพียงว่า metadata ถูกสร้าง ไม่ได้ยืนยันว่าไฟล์มีโครงสร้างตรงกับ schema และการ load สำเร็จก็ยังไม่ได้พิสูจน์ว่าแต่ละ row ถูกแยกคอลัมน์ถูกต้อง

ให้แยก “ภาษา” ออกจาก “ช่องทางส่งภาษา” HQL คือภาษาที่บอกสิ่งที่ต้องการ ส่วน Hive CLI, Beeline หรือ application client เป็นช่องทางส่งคำสั่ง สไลด์ใช้ Hive CLI เพื่อสาธิตได้ง่าย แต่ความรู้ที่ควรนำไปใช้คือ DDL/DML และ query semantics ไม่ใช่การยึดติดว่าต้องพิมพ์ผ่านคำสั่ง `hive` เท่านั้น ระบบจริงมักส่งคำสั่งผ่าน HiveServer2 และ Beeline เพื่อจัดการ session, authentication และหลายผู้ใช้ [Apache Hive documentation](https://hive.apache.org/docs/latest/)

## 2. Managed Table กับ External Table

ก่อนเลือกชนิด table ให้ถามว่า **ใครเป็นเจ้าของวงจรชีวิตของไฟล์** คำว่า “เจ้าของ” ในที่นี้ไม่ได้หมายถึง Linux user แต่หมายถึงระบบใดมีสิทธิ์ตัดสินใจสร้าง ย้าย เก็บรักษา และลบไฟล์เหล่านั้น

ถ้าเป็น **managed table** Hive เป็นผู้จัดการทั้ง metadata และข้อมูลของ table เมื่อเราสร้าง table แล้ว load ข้อมูล Hive จะนำไฟล์ไปอยู่ในพื้นที่ที่ Hive ดูแล โดยทั่วไปการ `DROP TABLE` จึงอาจลบทั้งคำอธิบายและข้อมูล วิธีนี้เหมาะกับ intermediate หรือ curated data ที่ Hive เป็นผู้สร้างและรับผิดชอบตลอดวงจรชีวิต

ถ้าเป็น **external table** Hive ดูแลเฉพาะ metadata ที่ชี้ไปยังตำแหน่งไฟล์ แต่ไฟล์มีเจ้าของหรือผู้ใช้อื่นอยู่แล้ว เช่น raw data ที่ pipeline นำเข้าหรือไฟล์ที่ Spark ต้องใช้ร่วมกัน เมื่อ drop external table โดยหลัก Hive จะลบคำอธิบายของตารางแต่ปล่อยไฟล์ไว้ การเลือก external จึงไม่ใช่เรื่องความเร็ว แต่เป็นการป้องกันไม่ให้การจัดการ metadata ของ Hive ลบข้อมูลร่วมโดยไม่ตั้งใจ รายละเอียดบางอย่างขึ้นกับ version และ configuration จึงไม่ควรทดลอง `DROP` กับข้อมูล production

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

ตัวอย่างเช่นไฟล์ raw PO ถูกวางไว้ที่ `/data/raw/po/` โดยระบบ ingestion และทั้ง Hive กับ Spark ต้องอ่าน path นี้ การสร้าง external table ทำให้ Hive เพิ่มมุมมองแบบตารางโดยไม่รับสิทธิ์ลบไฟล์ร่วม แต่ถ้า Hive สร้างตารางสรุปชั่วคราวสำหรับงานหนึ่งและไม่มีระบบอื่นใช้ managed table จะช่วยให้การ cleanup อยู่ภายใต้ Hive อย่างเป็นระบบ ก่อนใช้ `DROP TABLE` จึงต้องตอบให้ได้ว่าไฟล์เป็นของใครและมีระบบใดอ้าง path เดียวกันอยู่บ้าง

## 3. Schema-on-read คืออะไร

คำว่า **schema** หมายถึงคำอธิบายโครงสร้าง เช่นมีคอลัมน์อะไร เรียงอย่างไร และแต่ละคอลัมน์เป็นชนิดใด ส่วน **schema-on-read** หมายถึงระบบนำ schema มาใช้ตีความข้อมูลตอนอ่าน ไม่ได้ตรวจและแปลงทุกค่าจนผ่านกฎทั้งหมดตั้งแต่ตอนนำไฟล์เข้ามา

ลองนึกถึงไฟล์ที่มีข้อความ `1001|250.50` เราอาจประกาศว่าค่าแรกคือ `po_id INT` และค่าที่สองคือ `amount DECIMAL` เมื่อ query อ่านบรรทัดนี้ Hive จึงแยก fields แล้วพยายามแปลงชนิดตาม schema หากไฟล์จริงมี `ABC|300.00` ค่า `ABC` ไม่สามารถเป็น integer ได้ จึงอาจกลายเป็น `NULL` ตอนอ่าน ทั้งที่คำสั่งนำไฟล์เข้า table ก่อนหน้านั้นไม่ได้รายงานข้อผิดพลาด

ตัวอย่าง input ที่คาดว่า `po_id INT, amount DOUBLE`:

```text
1001	250.50
ABC	300.00
1003	missing
```

แถวสองมี `po_id` ผิดชนิดและแถวสามมี `amount` ผิดชนิด ผลลัพธ์อาจมี `NULL` การตรวจขั้นต่ำคือ total rows, null-by-column, rejected-pattern count และยอดรวมเทียบ source

ดังนั้น schema-on-read ไม่ได้แปลว่า “ไม่มี schema” แต่หมายถึงจุดที่ schema ถูกบังคับใช้ต่างจากระบบที่ตรวจเข้มตอนเขียน ข้อดีคือรับไฟล์ดิบได้รวดเร็วและเปลี่ยนวิธีมองข้อมูลได้ยืดหยุ่น ข้อเสียคือความผิดพลาดอาจถูกค้นพบช้า หากเดือนถัดมาผู้ส่งไฟล์สลับลำดับคอลัมน์ Query อาจยังรันแต่ `amount` กลายเป็น `NULL` และ `SUM(amount)` ต่ำกว่าความจริงโดยไม่มีข้อความแจ้งข้อผิดพลาดที่ชัดเจน

วิธีที่ปลอดภัยคือสร้าง **staging table** ซึ่งเก็บ fields ดิบเป็น `STRING` ก่อน แล้วใช้ขั้น **curated** ตรวจรูปแบบ แปลงชนิด และแยก rejected rows วิธีนี้ทำให้เรายังเห็นค่าต้นฉบับเมื่อ cast ไม่ผ่านและอธิบายได้ว่าข้อมูลใดถูกตัดออก

## 4. SerDe: สะพานระหว่าง bytes กับ columns

แม้ Hive จะมี schema แล้ว ระบบยังต้องรู้ว่าจะเปลี่ยนข้อความหนึ่งบรรทัดให้เป็นหลายคอลัมน์อย่างไร หน้าที่นี้เป็นของ **Serializer/Deserializer หรือ SerDe**

ฝั่งอ่านใช้ **Deserializer** รับ record จากไฟล์แล้วแยกออกเป็น fields ที่ Hive เข้าใจ เช่นรับ `H001|V020|1250.50` แล้วแยกเป็น `H001`, `V020` และ `1250.50` จากนั้น Hive จึงนำแต่ละ field ไปตีความตามชนิดคอลัมน์ ฝั่งเขียนใช้ **Serializer** ทำทางกลับกัน คือแปลง row ภายใน Hive ให้อยู่ในรูปที่บันทึกเป็นไฟล์ได้ เอกสาร Apache อธิบายว่า SerDe เป็นส่วนติดต่อด้าน input/output และสามารถรองรับรูปแบบที่กำหนดเองได้ [Apache Hive SerDe](https://hive.apache.org/docs/latest/user/serde/)

SerDe จึงไม่ใช่เพียงเครื่องหมายคั่นคอลัมน์ สำหรับไฟล์ง่ายอาจใช้ delimiter แต่ log ที่มีช่องว่างและข้อความอยู่ในเครื่องหมาย quote ต้องใช้กติกาซับซ้อนกว่า เช่น regular expression อย่างไรก็ตาม SerDe ทำหน้าที่แปล representation ไม่ได้ตรวจ business rule เช่นจำนวนเงินต้องมากกว่าศูนย์หรือ vendor ต้องมีอยู่ใน master

คำศัพท์ต้องอ่านตามลำดับ: raw line → record boundary → pattern/delimiter → fields → type conversion → Hive row หาก regex จับกลุ่มไม่ครบ column mapping จะเลื่อนหรือกลายเป็น `NULL`

สไลด์แสดง `RegSerde` แต่ class ที่ใช้จริงควรตรวจจาก Hive distribution และมักพบ `RegexSerDe` การคัดลอก class name จากสไลด์โดยไม่ตรวจ JAR/version เป็น failure mode สำคัญ

ลองติดตาม raw line `PO1001|V020|1250.50` ทีละขั้น ระบบอ่านหนึ่งบรรทัดเป็นหนึ่ง record จากนั้น Deserializer ใช้ `|` แยกเป็นสาม fields แล้ว Hive แปลง field ที่สามเป็นชนิดตัวเลขตาม schema ผลคือ row `(PO1001, V020, 1250.50)` ที่คำสั่งถัดไปนำไปกรองหรือรวมยอดได้ หากกติกาจับได้เพียงสอง fields คอลัมน์ที่สามจะไม่มีค่า และหากลำดับกติกาผิด ค่าจะไปอยู่ผิดคอลัมน์แม้ query ยังรันได้ การทดสอบ SerDe จึงต้องเทียบ raw sample กับผลลัพธ์ทีละ field ไม่ใช่ดูเฉพาะ `COUNT(*)`

Serializer ทำเส้นทางกลับกันเมื่อต้องเขียน row ออกเป็นไฟล์ แต่ไม่ควรเหมารวมว่า SerDe เป็นตัวตรวจ business rules มันแปล representation เท่านั้น กฎอย่าง `amount >= 0`, vendor ต้องมีใน master หรือ `po_line_id` ต้อง unique อยู่ในชั้น validation/curation

## 5. Regex ที่จำเป็นต่อการอ่าน log

**Regular expression หรือ regex** คือภาษาขนาดเล็กสำหรับบรรยายรูปแบบของข้อความ ใน Lab web log หนึ่งบรรทัดมี host, object ที่อยู่ในเครื่องหมาย quote และตัวเลขเวลา ช่องว่างทั่วไปจึงไม่สามารถใช้เป็น delimiter อย่างตรงไปตรงมา เพราะ object เองอาจมีรูปแบบเฉพาะ Regex ช่วยระบุว่าแต่ละส่วนเริ่มและจบตรงไหน

อย่าเริ่มจากการท่องสัญลักษณ์ทั้งหมด ให้อ่าน pattern `([^ ]+) "([^"]+)" ([0-9]+)` เป็นสามกลุ่ม กลุ่มแรกเก็บอักขระที่ไม่ใช่ช่องว่างตั้งแต่หนึ่งตัวขึ้นไป กลุ่มที่สองเก็บอักขระภายใน quote และกลุ่มที่สามเก็บตัวเลขตั้งแต่หนึ่งหลักขึ้นไป วงเล็บแต่ละคู่สร้าง capture group ซึ่งจะถูกส่งให้คอลัมน์ตามลำดับ

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

Data type บอก Hive ว่าควรตีความ field และอนุญาตการคำนวณแบบใด `INT` และ `BIGINT` ใช้กับจำนวนเต็ม `FLOAT` และ `DOUBLE` ใช้กับเลขทศนิยมแบบประมาณค่า `BOOLEAN` ใช้กับจริง/เท็จ `STRING` ใช้กับข้อความ และ `TIMESTAMP` ใช้กับวันเวลา คำว่า `bint` ในสไลด์เป็นการเขียนคลาดเคลื่อน ชนิดที่ถูกต้องใน HQL คือ `BIGINT`

Complex types ช่วยรักษาโครงสร้างซ้อน:

```sql
ARRAY<STRING>
MAP<STRING, INT>
STRUCT<name:STRING, age:INT>
```

เลือกชนิดจากความหมาย ไม่ใช่จากหน้าตาว่ามีแต่ตัวเลข เช่น zipcode `00125` และ vendor `0007` เป็นรหัส ไม่ได้ใช้บวกหรือลบ และเลขศูนย์นำหน้ามีความหมาย จึงควรเป็น `STRING` ส่วนจำนวนเงินต้องรักษาความแม่นยำ จึงควรพิจารณา `DECIMAL(precision, scale)` มากกว่า floating point ที่เป็นค่าประมาณ

## 7. Loading Data

```sql
LOAD DATA INPATH '/user/student/apache.log'
OVERWRITE INTO TABLE apache_log;
```

`LOAD DATA` ไม่ใช่กระบวนการ ETL ที่อ่านแต่ละแถว ตรวจ schema แล้วเขียนใหม่ เอกสาร Apache ระบุว่าโดยหลักเป็นการ copy หรือ move ไฟล์ไปยังตำแหน่งของ table และไม่ได้ทำ transformation ระหว่าง load [Apache Hive DML](https://hive.apache.org/docs/latest/language/languagemanual-dml/) ด้วยเหตุนี้ไฟล์ที่ผิด delimiter หรือผิดชนิดอาจเข้ามาอยู่ใน table ได้ แล้วปัญหาจึงปรากฏตอน query ตามหลัก schema-on-read

คำว่า `INPATH` โดยไม่มี `LOCAL` อ้างถึง path ใน filesystem ที่ Hive ใช้ เช่น HDFS และการ load อาจย้ายไฟล์ต้นทาง ส่วน `LOCAL INPATH` อ่านจาก local filesystem ของเครื่องที่บริการ Hive มองเห็น คำว่า `OVERWRITE` ให้แทนข้อมูลเดิมในขอบเขตเป้าหมาย จึงต้องตรวจ table, partition และ path ให้ถูกก่อนรัน

ต่างจาก `LOAD DATA`, คำสั่ง `INSERT ... SELECT` นำผลจาก query ไปเขียนใน table ปลายทาง จึงเหมาะกับการแปลง staging data ให้เป็น curated data เช่นกรองค่าที่ผิด cast และเลือกคอลัมน์ใหม่ ความแตกต่างสั้น ๆ คือ LOAD จัดวางไฟล์ ส่วน INSERT สร้างข้อมูลผลลัพธ์จากการประมวลผล

### Safe loading workflow

1. สำรวจ sample และนิยาม schema contract
2. สร้าง external staging table เพื่อเก็บ raw data
3. ตรวจ row count, parse failures และ null distribution
4. insert เข้า curated table ด้วย explicit casts/filters
5. reconcile count และ business totals
6. เก็บ query/version เพื่อ reproducibility

## Guided Lab: Staging-to-curated

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

## Lab จากชั้นเรียน: Hive DDL, MovieLens และ Web Log

ส่วนนี้เรียบเรียงจาก [Lab 02 Hive หน้า 1–5](../lab/lab_02_hive.pdf) Lab ใช้ Hive CLI และ Cloudera QuickStart VM ซึ่งเหมาะกับการเห็นกลไกพื้นฐาน แต่คำสั่งเดียวกันอาจต้องส่งผ่าน Beeline ในระบบใหม่ ก่อนรันทุกช่วงให้ถามว่า “คำสั่งนี้เปลี่ยนเฉพาะ metadata, ย้ายไฟล์ หรืออ่านไฟล์” เพื่อเชื่อม syntax กับความหมาย

### ช่วง A — Database และ table แรก

```sql
CREATE DATABASE IF NOT EXISTS my_db;
USE my_db;

CREATE TABLE test (
    id INT,
    name STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ',';

SHOW TABLES;
DESCRIBE test;
ALTER TABLE test ADD COLUMNS (address STRING);
DESCRIBE test;
```

ก่อน `ALTER` ให้ทำนายว่าไฟล์เก่าจะไม่ได้ถูก rewrite เพราะคำสั่งเปลี่ยน metadata เมื่ออ่านแถวเก่าซึ่งมีเพียงสอง fields คอลัมน์ `address` จึงอาจเป็น `NULL` อย่ารัน `DROP TABLE test` เพียงเพื่อทดลองจนกว่าจะยืนยันว่า table นี้ไม่มีข้อมูลที่ต้องเก็บ เพราะ managed table อาจลบทั้ง metadata และข้อมูล

### ช่วง B — MovieLens `u.user`: delimiter ทำให้ bytes กลายเป็น columns

หลังแตกไฟล์ MovieLens ให้ตรวจ raw sample และจำนวนบรรทัดก่อนส่งเข้า HDFS:

```bash
head ml-100k/u.user
wc -l ml-100k/u.user
hadoop fs -mkdir -p /user/cloudera/movielens
hadoop fs -put ml-100k/u.user /user/cloudera/movielens/u.user
hadoop fs -cat /user/cloudera/movielens/u.user | head
```

หนึ่งบรรทัดใช้ `|` คั่นห้า fields จึงประกาศ schema ตามลำดับจริง:

```sql
CREATE TABLE users (
    userid INT,
    age INT,
    gender STRING,
    occupation STRING,
    zipcode STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY '|';

LOAD DATA INPATH '/user/cloudera/movielens/u.user'
OVERWRITE INTO TABLE users;

SELECT * FROM users LIMIT 10;
SELECT COUNT(*) AS user_rows FROM users;
SELECT COUNT(*) AS invalid_rows
FROM users
WHERE userid IS NULL OR age IS NULL;
```

อย่าจำจำนวนผลลัพธ์โดยไม่ตรวจไฟล์ที่ใช้ หลักฐานที่แข็งแรงกว่าคือ `user_rows` ต้องเท่ากับจำนวนบรรทัดของ source และ sample fields ต้องไม่เลื่อน `zipcode` ใช้ `STRING` เพราะเป็นรหัสที่อาจมีเลขศูนย์นำหน้า ไม่ใช่ปริมาณสำหรับคำนวณ

จุดที่มักทำให้ผู้เริ่มต้นสับสนคือ `LOAD DATA INPATH` อาจย้ายไฟล์ใน filesystem เข้า location ของ managed table ไม่ใช่ parse แล้ว copy แบบ database loader ทั่วไป หากต้องใช้ raw path เดิมสร้าง external table อีกครั้ง ให้เก็บสำเนาแยกหรือเลือก external staging ตั้งแต่ต้น และตรวจ path หลัง `LOAD` ด้วย `hadoop fs -ls`

### ช่วง C — RegexSerDe: จาก log หนึ่งบรรทัดสู่สามคอลัมน์

Lab กำหนดรูปแบบหนึ่งบรรทัดเป็น `host "object" time` เช่น:

```text
client01 "GET_/index.html" 1470000000
```

Regex `([^ ]+) "([^"]+)" ([0-9]+)` จับสาม groups ตามลำดับคือ `host`, `object`, `time` ดังนั้นจำนวนและลำดับ groups ต้องตรงกับ columns:

```sql
CREATE EXTERNAL TABLE weblog (
    host STRING,
    object STRING,
    time STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.contrib.serde2.RegexSerDe'
WITH SERDEPROPERTIES (
    'input.regex' = '([^ ]+) "([^"]+)" ([0-9]+)'
)
LOCATION '/user/cloudera/weblog';
```

class `contrib` นี้ขึ้นกับ JAR ของ environment หากหา class ไม่พบ ต้องตรวจ Hive distribution ไม่ควรเปลี่ยน regex แบบสุ่ม หาก query ได้ `NULL` ให้ย้อนตรวจ raw line → แต่ละ capture group → ชนิดคอลัมน์ ด้วย:

```sql
SELECT * FROM weblog LIMIT 10;
SELECT COUNT(*) AS parsed_rows FROM weblog;
SELECT COUNT(*) AS parse_failures
FROM weblog
WHERE host IS NULL OR object IS NULL OR time IS NULL;
```

Lab ต้นฉบับโหลด `wlog` จาก `/user/cloudera/weblog/wlog` เข้า managed table `weblogtest` แล้วจึงสร้าง external table ให้ชี้กลับไปที่ `/user/cloudera/weblog` ขั้นนี้อาจทำให้ external table ไม่พบไฟล์ เพราะ `LOAD DATA INPATH` อาจย้าย `wlog` ออกจาก raw path ไปยังพื้นที่ของ managed table วิธีที่ทำซ้ำได้คือเก็บ raw copy แยกสำหรับ external table หรือสร้าง external table ให้ชี้ raw path ก่อน แล้วใช้ `INSERT ... SELECT` สร้าง managed/curated table ภายหลัง

การทดลอง failure ที่ให้ความรู้ที่สุดคือเปลี่ยน delimiter ของ `users` จาก `|` เป็น `,` หรือเอาเครื่องหมาย quote ออกจาก regex แล้วเปรียบเทียบ sample rows กับ null counts จากนั้นคืน DDL ให้ถูกต้อง หลักฐานว่าซ่อมสำเร็จคือจำนวนแถวตรง source, fields ไม่เลื่อน และ parse failures เป็นศูนย์สำหรับข้อมูลที่ตรง contract

## แผนผังการประเมินความเข้าใจ

| เป้าหมาย | หลักฐานในบท | คำถาม/กิจกรรมตรวจความเข้าใจ |
|---|---|---|
| เลือก managed/external จาก ownership | ตัวอย่าง raw PO ที่ Hive/Spark ใช้ร่วมกัน | อธิบายผลของ `DROP TABLE` และผู้ที่ควรควบคุมไฟล์ |
| อธิบาย schema-on-read | ตัวอย่าง `ABC|300.00` | ทำนายค่าเมื่อ cast ไม่ผ่านและออกแบบ null check |
| trace SerDe | `PO1001|V020|1250.50` และ web log | จับคู่ raw text กับ capture groups และ typed columns |
| แยก LOAD กับ INSERT | Safe loading workflow และ Lab MovieLens | ตรวจ path ก่อน/หลัง load และ reconcile source/target/reject |

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

**2. Raw files ถูกใช้ร่วมกับ Spark ควรเลือก table ใด?** External table เหมาะกว่า เพราะไม่ควรให้ Hive เป็นเจ้าของวงจรชีวิตของไฟล์ที่หลายระบบใช้ร่วมกันเพียงระบบเดียว

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
- ทำ Lab MovieLens/RegexSerDe พร้อมอธิบายผลของ delimiter, `LOAD DATA` และ table ownership ได้

## Source Coverage และ References

ครอบคลุม PDF หน้า 6–15: CLI/HQL DDL, managed/external, RegexSerDe, regex, types, schema-on-read และ loading รวมทั้ง [Lab 02 Hive หน้า 1–5](../lab/lab_02_hive.pdf) ช่วง DDL, MovieLens loading และ web-log tables

- [Apache Hive DDL](https://hive.apache.org/docs/latest/language/languagemanual-ddl/)
- [Managed vs. External Tables](https://hive.apache.org/docs/latest/language/managed-vs--external-tables/)
- [Apache Hive Tutorial](https://hive.apache.org/docs/latest/user/tutorial/)
- [Apache Hive DML](https://hive.apache.org/docs/latest/language/languagemanual-dml/)
- [Apache Hive SerDe](https://hive.apache.org/docs/latest/user/serde/)
