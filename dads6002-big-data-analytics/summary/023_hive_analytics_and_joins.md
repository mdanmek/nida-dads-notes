# บทที่ 02.3: Hive Analytics and Joins

> **จากเอกสาร:** `dads6002_02_hive.pdf` หน้า 16–21  
> [← บทที่ 02.2](022_hql_schema_serde_and_loading.md) | [สารบัญ](README.md)

## Learning Objectives

เขียนและ trace aggregation, CTAS และ joins; เลือก join type จาก business question; ตรวจ row multiplication, unmatched keys และ totals ได้

## Relational mental model: grain, key และ cardinality

บทนี้ใช้สอง tables จากสไลด์ `sales(cname,id)` และ `things(id,iname)` หนึ่ง row ใน `sales` แทนเหตุการณ์ที่ลูกค้าหนึ่งคนซื้อสินค้าหนึ่งรหัส ส่วนหนึ่ง row ใน `things` แทนสินค้าหนึ่งชนิด ความหมายของหนึ่ง row เรียกว่า **grain** และเป็นคำถามแรกก่อน aggregation หรือ join เสมอ เพราะ `COUNT(*)` ของ sales คือจำนวนเหตุการณ์ซื้อ ไม่ใช่จำนวนลูกค้าที่ไม่ซ้ำ

คอลัมน์ `id` เป็น join key ที่ใช้เทียบว่ารายการซื้ออ้างถึงสินค้าใด ฝั่ง `things` คาดว่า `id` ไม่ซ้ำเพราะหนึ่งรหัสควรมีหนึ่งชื่อ แต่ฝั่ง `sales` ซ้ำได้เพราะสินค้าชนิดเดียวถูกซื้อหลายครั้ง **cardinality** อธิบายรูปแบบจำนวนแถวที่สัมพันธ์กัน เช่น many-to-one ในกรณีนี้ ถ้า `id=2` มีสอง sales rows และหนึ่ง things row ผล join จะมีสอง rows ไม่ใช่หนึ่ง เพราะแต่ละเหตุการณ์ซื้อยังคงเป็นคนละหน่วย

เมื่อ key ฝั่งหนึ่งหาอีกฝั่งไม่พบ เราเรียก row นั้นว่า unmatched เช่น `sales.id=0` ไม่มีใน things และ `things.id=1` ไม่เคยปรากฏใน sales ส่วน join type เป็นการตัดสินว่าจะรักษา population ฝั่งใดไว้ การเข้าใจตรงนี้มาก่อน syntax ทำให้เราเลือก join จากคำถามธุรกิจ ไม่ใช่ท่องรูปวงกลม

## 1. Aggregation: จาก MapReduce program สู่ HQL

หากเขียน group-count ด้วย MapReduce เราต้องนิยาม mapper, key, shuffle และ reducer แต่ Hiveให้ประกาศผลที่ต้องการ:

```sql
SELECT month, COUNT(*) AS hit_count
FROM apache_log
GROUP BY month
ORDER BY hit_count DESC;
```

`GROUP BY` กำหนด grain ของ output ทุก expression ใน `SELECT` ต้องเป็น grouping key หรือ aggregate การตีความ `COUNT(*)` ต้องถามว่า “หนึ่ง row ใน input แทนอะไร” เพราะ count ที่ถูก syntax อาจผิด business grain

Hive รองรับ `SUM`, `AVG`, `MIN`, `MAX`, variance, standard deviation และ covariance การเปิด map-side aggregation อาจลดข้อมูลก่อน shuffle แต่ใช้ memory เพิ่มและต้องอาศัย aggregate ที่รวม partial results ได้อย่างถูกต้อง

Aggregation เปลี่ยน grain อย่างเป็นระบบ ก่อน `GROUP BY` หนึ่ง row อาจแทน log event หลัง `GROUP BY month` หนึ่ง row แทนหนึ่งเดือน คอลัมน์ที่ไม่ได้อยู่ใน grouping key ต้องถูกสรุป เช่น `COUNT(*)` หรือ `SUM(amount)` เพราะระบบไม่สามารถเลือกค่ารายเหตุการณ์หนึ่งค่าให้ row รายเดือนได้อย่างมีความหมาย หาก grouping key ละเอียดเกินไป เช่นใส่ `event_id` ที่ไม่ซ้ำ ทุกกลุ่มจะเหลือหนึ่ง row และไม่ได้สรุปจริง หากหยาบเกินไป เช่นไม่ใส่ hospital เมื่อโจทย์ต้องการรายโรงพยาบาล ผลจะรวมประชากรต่างกลุ่มเข้าด้วยกัน

### Worked trace

Input:

| month | host |
|---|---|
| Jan | remote |
| Jan | local |
| Feb | remote |
| Jan | remote |

หลัง group by ได้ `Jan → 3`, `Feb → 1` ถ้ากรอง `host = 'remote'` ก่อน grouping ผลเป็น `Jan → 2`, `Feb → 1` ลำดับ filter ก่อน aggregate จึงเปลี่ยนผลอย่างมีเหตุผล

## 2. Subquery, SPLIT และ CTAS

สไลด์ดึงเดือนจากข้อความเวลาโดย `split(time, '/')[1]` ก่อน group ความเสี่ยงคือ format ที่ผิดทำให้ index ไม่มีค่า ควรตรวจ null/array length และพิจารณา parse เป็น timestamp ตั้งแต่ curated layer

```sql
CREATE TABLE remote_hits_by_month AS
SELECT month, COUNT(*) AS hit_count
FROM (
    SELECT SPLIT(time_text, '/')[1] AS month
    FROM apache_log
    WHERE host = 'remote'
) s
GROUP BY month;
```

CTAS หรือ `CREATE TABLE AS SELECT` สร้าง table และบรรจุผล query ในครั้งเดียว เหมาะกับ derived dataset แต่ต้องกำหนด ownership, format และ rerun behavior หาก pipeline รันซ้ำโดยไม่ออกแบบ idempotency อาจเกิด duplicate หรือ table-exists error

## 3. Join คืออะไร

Join เชื่อม rows จากสอง relations ด้วยเงื่อนไข key ตัวอย่างสไลด์มี `sales(cname,id)` และ `things(id,iname)` ก่อนเลือก join ต้องถามว่าต้องรักษา population ฝั่งใด ไม่ใช่เลือกจากความคุ้นเคยกับ syntax

Input:

**sales**: `(Joe,2)`, `(Hank,4)`, `(Ali,0)`, `(Eve,3)`, `(Hank,2)`  
**things**: `(2,Tie)`, `(4,Coat)`, `(3,Hat)`, `(1,Scarf)`

กระบวนการเชิงความคิดมีสามขั้น ขั้นแรกเลือก population หลัก เช่นต้องการรักษารายการขายทุกบรรทัด ขั้นที่สองกำหนด match condition `sales.id = things.id` ขั้นที่สามตัดสินว่าจะทำอย่างไรกับ unmatched rows Inner join ทิ้ง unmatched ทั้งสองฝั่ง ส่วน outer join เติม `NULL` ให้ด้านที่หาไม่พบ `NULL` ในผลจึงไม่ได้แปลว่าข้อมูลต้นทางว่างเสมอไป แต่อาจหมายถึงไม่มีคู่ที่ตรงกัน

## 4. Trace Join Types

### Inner Join

```sql
SELECT s.cname, s.id, t.iname
FROM sales s
JOIN things t ON s.id = t.id;
```

รักษาเฉพาะ key ที่พบสองฝั่ง จึงตัด `Ali,0` และ `Scarf,1` ผลมี 4 rows เพราะ id 2 ปรากฏใน sales สองครั้ง

### Left Outer Join

รักษาทุก row จาก sales และเติม `NULL` เมื่อไม่มี things จึงเก็บ Ali ไว้ เหมาะเมื่อ population หลักคือ transaction และต้องการรู้ missing master

### Right Outer Join

รักษาทุก row จาก things จึงเก็บ Scarf แม้ไม่เคยขาย ชื่อ left/right ขึ้นกับตำแหน่ง table ใน query ไม่ได้แปลว่าชนิดหนึ่งดีกว่าอีกชนิด

### Full Outer Join

รักษาทุก row จากทั้งสองฝั่ง เหมาะกับ reconciliation เพื่อเห็น unmatched ทั้งสองด้าน แต่ downstream ต้องจัดการ NULL keys/attributes

### Left Semi Join

คืนเฉพาะ columns จากฝั่งซ้ายสำหรับ rows ที่มี match ฝั่งขวา คล้าย existence test ไม่ได้คืน columns ฝั่งขวา ในตัวอย่าง `things LEFT SEMI JOIN sales` คืน Tie, Coat และ Hat แต่ไม่คืน Scarf

| คำถาม | Join ที่เป็นจุดเริ่มต้น |
|---|---|
| เอาเฉพาะ matched transactions | INNER |
| รักษา transaction แม้ master หาย | LEFT OUTER |
| รักษา master ทุกตัวแม้ไม่เคยใช้ | RIGHT OUTER หรือสลับ table แล้ว LEFT |
| reconcile unmatched ทั้งสองฝั่ง | FULL OUTER |
| กรองว่ามีอยู่ โดยไม่เอาคอลัมน์อีกฝั่ง | LEFT SEMI |

## 5. Row Multiplication และ Grain

หาก key ซ้ำทั้งสองฝั่ง join จะเป็น many-to-many เช่น key K มี 3 rows ซ้ายและ 4 rows ขวา ผลเฉพาะ K มี 12 rows นี่ไม่ใช่ bug ของ Hive แต่เป็นผลตาม relational algebra ก่อน join จึงต้องตรวจ uniqueness ตาม grain ที่คาด

```sql
SELECT id, COUNT(*)
FROM things
GROUP BY id
HAVING COUNT(*) > 1;
```

ถ้า master ควร unique แต่พบซ้ำ ต้อง deduplicate ด้วย business rule ที่ชัดเจน ไม่ควรใช้ `DISTINCT` ปิดอาการโดยไม่หาสาเหตุ

ตัวอย่างเชิงตัวเลขช่วยให้ตรวจได้ก่อนรัน ถ้า key `V01` มี PO 3 rows และ vendor master ผิดพลาดมี `V01` 2 rows ผล join สำหรับ key นี้จะเป็น 3 × 2 = 6 rows ยอดเงินของแต่ละ PO ถูกทำซ้ำสองครั้ง ถ้ารวมยอดหลัง join จะได้สองเท่า แม้ SQL ไม่มี error วิธีพิสูจน์คือวัด uniqueness ของ master, เทียบ row count ก่อน/หลัง และ reconcile `SUM(amount)` การใช้ `DISTINCT` อาจทำให้แถวดูน้อยลง แต่หาก attributes ต่างกันเพียงบางคอลัมน์ก็ยังไม่แก้ และอาจลบเหตุการณ์จริงที่เหมือนกันโดยบังเอิญ

## 6. Join Execution และ Optimization

เชิงแนวคิด distributed join มีต้นทุน shuffle หากข้อมูลสองฝั่งต้อง regroup ตาม key Optimizer อาจเลือก map join เมื่อด้านหนึ่งเล็กพอใส่ memory และใช้ statistics เพื่อ reorder joins ตาม [Join Optimization](https://hive.apache.org/docs/latest/language/)

การเพิ่ม partition ช่วย join ก็ต่อเมื่อ query filter partition ได้ ส่วน bucket อาจช่วยบาง plan แต่ไม่ควรสรุปว่า bucket แล้ว join เร็วเสมอ ต้องดู engine, statistics, file layout และ `EXPLAIN`

ให้แยก correctness ออกจาก performance ก่อน Join type, key และ grain กำหนดว่าคำตอบถูกหรือไม่ ส่วน join order, map-side join, statistics, partition pruning และ bucketing มีผลต่อวิธีใช้ทรัพยากร Query ที่เร็วแต่คูณยอดผิดไม่ใช่ optimization ที่สำเร็จ ลำดับทำงานที่ปลอดภัยคือพิสูจน์ผลด้วยข้อมูลเล็ก ตรวจ cardinality และ totals แล้วจึงอ่าน `EXPLAIN` เพื่อปรับ plan เอกสาร Apache อธิบายว่า optimizer ใช้แนวทางอย่าง filter/projection/partition pruning และ cost-based optimization เพื่อลดต้นทุน โดยเฉพาะ shuffle [Apache Hive Cost-Based Optimization](https://hive.apache.org/docs/latest/user/cost-based-optimization-in-hive/)

## สะพานกลับสู่ระบบ Big Data ทั้งชุด

Hive ปิดช่องว่างระหว่างนักวิเคราะห์กับระบบกระจาย แต่กลไกจากบทก่อนยังอยู่ใต้คำสั่ง SQL เมื่อ query scan table, HDFS/storage ยังส่งไฟล์ เมื่อ query aggregate หรือ join, execution engine ยังต้องแบ่งงานและอาจ shuffle ตาม key เมื่อมีหลายขั้นตอน Airflow/Oozie ยังอาจเป็นผู้ควบคุม schedule และ retry ดังนั้น Hive ไม่ได้ลบความจำเป็นในการเข้าใจ Hadoop แต่ยกระดับ abstraction ให้เราเขียน “ผลที่ต้องการ” และใช้ความรู้ด้าน storage/grain/failure ตรวจว่าแผนและผลลัพธ์สมเหตุผล

## Guided Lab: Vendor Reconciliation

Tables:

- `po(po_id, vendor_id, amount)` มี 5 rows
- `vendor(vendor_id, vendor_name)` มี 4 rows โดยมี vendor หนึ่งรายไม่ถูกใช้และ PO หนึ่ง row หา master ไม่พบ

งาน:

1. ใช้ inner join สรุป matched amount
2. ใช้ left join หา missing vendor master
3. ใช้ full outer join แยก `missing_master`, `unused_master`, `matched`
4. ตรวจ input counts, output counts และ sum(amount)
5. ปลูก error โดยเพิ่ม duplicate vendor_id ใน master แล้วสังเกต row count/amount โต
6. แก้ด้วย data-quality rule ก่อน join และพิสูจน์ totals กลับมาตรง

Validation queries:

```sql
SELECT COUNT(*) AS po_rows, SUM(amount) AS po_amount FROM po;

SELECT COUNT(*) AS missing_master_rows
FROM po p
LEFT JOIN vendor v ON p.vendor_id = v.vendor_id
WHERE v.vendor_id IS NULL;
```

## Troubleshooting

| อาการ | สาเหตุที่น่าจะเป็น | การตรวจ |
|---|---|---|
| จำนวน row เพิ่มมาก | duplicate keys/many-to-many | count per key ทั้งสองฝั่ง |
| unmatched หาย | ใช้ inner join | เปลี่ยนเป็น outer ตาม population |
| left join กลายเป็น inner | filter right table ใน `WHERE` | ย้ายเงื่อนไขเข้า `ON` หรือรองรับ NULL |
| aggregation ผิด | grain ก่อน group ผิด | inspect sample และ distinct business key |
| job ช้า | shuffle, skew, statistics เก่า | `EXPLAIN`, key distribution, stats |

## Progressive Practice พร้อม Model Answers

**1. ต้องรักษา PO ทุกใบ ใช้ join ใด?** `po LEFT JOIN vendor` เพราะ PO เป็น population หลัก

**2. ทำไม id 2 ออกสองแถวในตัวอย่าง inner join?** sales มีสองคน/รายการที่ id 2 และแต่ละ row match things id 2 หนึ่ง row

**3. ฝั่งซ้ายมี K 3 rows ฝั่งขวามี K 4 rows ผลกี่ rows?** 12 rows เพราะทุก combination ที่ key ตรงกันถูกสร้าง

**4. Left join แล้วใส่ `WHERE v.region = 'BKK'` มีผลอะไร?** rows ที่ไม่ match มี `v.region = NULL` และถูก filter ออก จึงทำให้พฤติกรรมส่วนนี้คล้าย inner join หากต้องรักษา unmatched ควรวาง filter ที่ `ON` ตามความหมายที่ต้องการ

## Likely Exam Focus

- trace ผลของ join จากตารางเล็ก
- เลือก join type จาก population ที่ต้องรักษา
- อธิบาย group grain และ partial aggregation
- วิเคราะห์ many-to-many/row multiplication
- อ่าน CTAS/subquery และตรวจ failure จาก parsing

## Mastery Checklist

- เขียน aggregation และบอก grain ของผลลัพธ์ได้
- trace join ทั้งห้าชนิดโดยไม่เดาจากชื่ออย่างเดียว
- ตรวจ uniqueness, unmatched keys, row count และ totals ได้
- ใช้ `EXPLAIN` และ key distribution ตั้งสมมติฐานเรื่อง performance ได้

## Source Coverage และ References

ครอบคลุม PDF หน้า 16–21: grouping, aggregate functions, map-side aggregation, CTAS, inner/outer/semi joins และ join diagram

- [Apache Hive Language Manual](https://hive.apache.org/docs/latest/language/)
- [Apache Hive Cost-Based Optimization](https://hive.apache.org/docs/latest/user/cost-based-optimization-in-hive/)
