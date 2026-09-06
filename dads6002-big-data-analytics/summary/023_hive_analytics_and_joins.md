# บทที่ 02.3: Hive Analytics and Joins

> **จากเอกสาร:** [dads6002_02_hive.pdf หน้า 16–21](../lecture/dads6002_02_hive.pdf) และ [lab_02_hive.pdf หน้า 3–5](../lab/lab_02_hive.pdf)  
> [← บทที่ 02.2](022_hql_schema_serde_and_loading.md) | [สารบัญ](000_readme.md)

## เป้าหมายของบทเรียน

สองบทก่อนทำให้ Hive อ่านไฟล์เป็นแถวและคอลัมน์ได้ บทนี้จึงก้าวจาก “อ่านได้” ไปสู่ “ตอบคำถามจากข้อมูล” เราจะเริ่มจากการรวมหลายแถวเป็นผลสรุปด้วย `GROUP BY` แล้วจึงเชื่อมสองตารางด้วย `JOIN` หลังอ่านจบ เราควรบอกระดับรายละเอียดของผลลัพธ์ได้ เลือกชนิด join จากประชากรที่ต้องรักษา และตรวจให้พบว่าคีย์ซ้ำหรือข้อมูลที่จับคู่ไม่ได้ทำให้จำนวนแถวและยอดรวมเปลี่ยนอย่างไร

## Relational mental model: grain, key และ cardinality

ก่อนใช้ `GROUP BY` หรือ `JOIN` ต้องตอบคำถามพื้นฐานที่สุดว่า “หนึ่งแถวแทนอะไร” คำตอบนี้เรียกว่า **ระดับรายละเอียดของข้อมูล (grain)** หากตอบผิด คำสั่ง SQL อาจรันได้สมบูรณ์แต่คำตอบทางธุรกิจผิด

บทนี้ใช้สองตารางจากสไลด์ ตาราง `sales(cname,id)` มีหนึ่งแถวต่อเหตุการณ์ที่ลูกค้าหนึ่งคนซื้อสินค้าหนึ่งรหัส ดังนั้นลูกค้าคนเดิมหรือสินค้ารหัสเดิมปรากฏได้หลายครั้ง ตาราง `things(id,iname)` มีหนึ่งแถวต่อสินค้าหนึ่งรหัส เพราะทำหน้าที่คล้ายรายการอ้างอิงชื่อสินค้า ด้วย grain นี้ `COUNT(*)` ของ `sales` จึงหมายถึงจำนวนเหตุการณ์ซื้อ ไม่ใช่จำนวนลูกค้าที่ไม่ซ้ำ และ `COUNT(*)` ของ `things` หมายถึงจำนวนแถวสินค้าในรายการอ้างอิง

คอลัมน์ `id` เป็น **คีย์สำหรับเชื่อมตาราง (join key)** เพราะใช้ตอบว่าเหตุการณ์ซื้ออ้างถึงสินค้าชิ้นใด ฝั่ง `things` เราคาดว่า `id` ไม่ซ้ำ เนื่องจากหนึ่งรหัสควรมีชื่อสินค้าหนึ่งรายการ แต่ฝั่ง `sales` ซ้ำได้เพราะสินค้าชนิดเดียวขายหลายครั้ง ความสัมพันธ์นี้เรียกว่า many-to-one: หลายแถวจาก sales จับคู่กับหนึ่งแถวจาก things

คำว่า **cardinality** ใช้อธิบายจำนวนหรือรูปแบบความสัมพันธ์ระหว่างแถว ถ้า `id=2` ปรากฏสองครั้งใน sales และหนึ่งครั้งใน things ผล join จะมีสองแถว ไม่ใช่หนึ่ง เพราะเหตุการณ์ซื้อทั้งสองยังคงเป็นคนละเหตุการณ์ Join เติมชื่อสินค้าให้แต่ละเหตุการณ์ ไม่ได้รวมเหตุการณ์เหล่านั้นเข้าด้วยกัน

เมื่อคีย์ฝั่งหนึ่งหาอีกฝั่งไม่พบ เราเรียกแถวนั้นว่า **แถวที่จับคู่ไม่ได้ (unmatched row)** ในตัวอย่าง `sales.id=0` ไม่มีสินค้ารหัส 0 ใน things ขณะที่ `things.id=1` มีอยู่ในรายการสินค้าแต่ไม่เคยปรากฏใน sales การเลือกชนิด join คือการตัดสินว่าเราต้องการรักษาแถวกลุ่มใดไว้ ไม่ใช่การเลือกรูปวงกลมจากความจำ

## 1. Aggregation: จาก MapReduce program สู่ HQL

**Aggregation หรือการสรุปรวม** คือการนำหลายแถวมาเปลี่ยนเป็นค่ารวม เช่นจำนวน ผลรวม ค่าเฉลี่ย ค่าต่ำสุด หรือค่าสูงสุด ส่วน `GROUP BY` กำหนดว่าแถวใดควรถูกนำมาสรุปร่วมกัน

ลองเริ่มจากข้อมูล log สี่แถว โดยสามแถวอยู่เดือน Jan และหนึ่งแถวอยู่เดือน Feb หากถามจำนวนเหตุการณ์ต่อเดือน ระบบต้องจัดแถวที่มีเดือนเดียวกันเป็นกลุ่ม แล้วนับสมาชิกในแต่ละกลุ่ม ผลลัพธ์จึงเปลี่ยน grain จาก “หนึ่งแถวต่อเหตุการณ์” เป็น “หนึ่งแถวต่อเดือน”

หากเขียนงาน group-count ด้วย MapReduce เราต้องสร้าง mapper, key, shuffle และ reducer แต่ Hive ให้ผู้ใช้ประกาศผลที่ต้องการด้วย HQL:

```sql
SELECT month, COUNT(*) AS hit_count
FROM apache_log
GROUP BY month
ORDER BY hit_count DESC;
```

คอลัมน์ `month` หลัง `GROUP BY` เป็น **grouping key** ส่วน `COUNT(*)` เป็น aggregate function ที่นับแถวในแต่ละกลุ่ม ทุกคอลัมน์ใน `SELECT` จึงต้องเป็นสิ่งที่บอกชื่อกลุ่มหรือเป็นค่าที่สรุปจากสมาชิกของกลุ่ม มิฉะนั้นระบบไม่รู้ว่าจะเลือกค่าจากแถวใดมาแสดงในผลลัพธ์หนึ่งแถว

Hive รองรับ `SUM`, `AVG`, `MIN`, `MAX`, variance, standard deviation และ covariance การเลือกฟังก์ชันต้องตรงกับความหมายของข้อมูล เช่น `SUM(amount)` มีความหมายกับยอดเงิน แต่ `SUM(zipcode)` ไม่มีความหมายแม้ zipcode จะประกอบด้วยตัวเลข

สไลด์กล่าวถึง map-side aggregation ซึ่งให้ worker รวมผลย่อยบางส่วนก่อนส่งข้อมูลผ่านเครือข่าย วิธีนี้ลดข้อมูลที่ต้อง shuffle แต่ใช้หน่วยความจำในช่วง map มากขึ้น และ aggregate ต้องรวม partial results ได้อย่างถูกต้อง ตัวอย่าง `SUM` รวมผลย่อยต่อได้ตรงไปตรงมา แต่การรวมค่าเฉลี่ยต้องรักษาทั้งผลรวมและจำนวน ไม่ควรเฉลี่ยค่าเฉลี่ยของกลุ่มที่มีขนาดไม่เท่ากัน

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

บางครั้งคอลัมน์ที่ต้องใช้จัดกลุ่มยังซ่อนอยู่ในข้อความ เช่น `time` เก็บวันเวลาเต็มและเดือนอยู่ระหว่างเครื่องหมาย `/` ฟังก์ชัน `SPLIT(time_text, '/')` แบ่งข้อความเป็น array และ `[1]` เลือกสมาชิกตำแหน่งที่สอง เพราะ index เริ่มจากศูนย์ เราจึงใช้ subquery สร้างคอลัมน์ `month` ชั่วคราวก่อน แล้ว query ชั้นนอกค่อย group ตามเดือน

กลไกนี้พึ่งพารูปแบบข้อความ หากบางแถวไม่มี `/` สมาชิก `[1]` อาจไม่มีค่าและกลายเป็น `NULL` จึงควรตรวจจำนวนแถวที่ parse ไม่ได้ หรือแปลงวันเวลาเป็นชนิดที่ชัดเจนใน curated layer แทนการแตกข้อความซ้ำทุก query

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

**CTAS หรือ `CREATE TABLE AS SELECT`** ทำสองอย่างในคำสั่งเดียว: สร้าง metadata ของตารางใหม่และเขียนผลจาก query ลงเป็นข้อมูลของตารางนั้น จึงเหมาะเมื่ออยากเก็บผลสรุปไว้ใช้ต่อ แต่ต้องคิดเรื่องเจ้าของไฟล์ รูปแบบไฟล์ และการรันซ้ำ หาก table มีอยู่แล้วคำสั่งอาจ error และหากเปลี่ยนไปใช้ insert โดยไม่กำหนด overwrite หรือ partition อย่างเหมาะสมก็อาจเกิดข้อมูลซ้ำ

## 3. Join คืออะไร

**Join** คือการสร้างแถวผลลัพธ์จากแถวของสองตารางที่ตรงตามเงื่อนไขการจับคู่ ในตัวอย่าง เรามีชื่อผู้ซื้อและรหัสสินค้าอยู่ใน `sales` แต่ชื่อสินค้าอยู่ใน `things` หากต้องการรายงานว่าแต่ละคนซื้ออะไร เราต้องจับคู่ `sales.id` กับ `things.id`

Input:

**sales**: `(Joe,2)`, `(Hank,4)`, `(Ali,0)`, `(Eve,3)`, `(Hank,2)`  
**things**: `(2,Tie)`, `(4,Coat)`, `(3,Hat)`, `(1,Scarf)`

ลองตามแถว `(Joe,2)` ระบบค้น `things.id=2` แล้วพบ `(2,Tie)` จึงสร้างแถวผลลัพธ์ `(Joe,2,2,Tie)` ส่วน `(Ali,0)` หา `things.id=0` ไม่พบ สิ่งที่เกิดกับ Ali ต่อไปขึ้นกับชนิด join ที่เราเลือก

ก่อนเขียน syntax ให้ตัดสินใจสามเรื่อง ขั้นแรกคือประชากรที่ต้องรักษา เช่นต้องการเก็บรายการขายทุกแถวหรือเฉพาะรายการที่มี master data ขั้นที่สองคือเงื่อนไขการจับคู่ `sales.id = things.id` ขั้นที่สามคือวิธีจัดการ unmatched rows การตัดสินใจนี้ทำให้เราเลือก join จากคำถามธุรกิจ ไม่ใช่จากความคุ้นเคยกับชื่อ

## 4. Trace Join Types

### Inner Join

```sql
SELECT s.cname, s.id, t.iname
FROM sales s
JOIN things t ON s.id = t.id;
```

Inner join เก็บเฉพาะแถวที่หาคู่ได้ทั้งสองฝั่ง Joe, Hank และ Eve จึงได้ชื่อสินค้า ส่วน Ali ถูกตัดเพราะรหัส 0 ไม่มีใน things และ Scarf ไม่ปรากฏเพราะไม่มี sales อ้างรหัส 1 ผลมี 4 แถวเนื่องจาก id 2 ปรากฏใน sales สองเหตุการณ์และแต่ละเหตุการณ์จับคู่กับ Tie แยกกัน

### Left Outer Join

Left outer join รักษาทุกแถวจากตารางด้านซ้าย ในคำสั่งนี้ sales อยู่ซ้าย จึงยังเก็บ `(Ali,0)` ไว้ แต่เนื่องจากหา things ไม่พบ คอลัมน์จากฝั่ง things จะเป็น `NULL` ค่า `NULL` นี้ไม่ได้แปลว่าชื่อสินค้าในไฟล์ต้นทางว่างเสมอไป แต่อาจหมายถึงไม่มีแถวที่จับคู่ได้ วิธีนี้เหมาะเมื่อต้องรักษาธุรกรรมทุกแถวและต้องการค้นหา master data ที่หาย

### Right Outer Join

Right outer join ทำหลักเดียวกันแต่รักษาทุกแถวจากตารางด้านขวา เมื่อ things อยู่ขวา สินค้า Scarf จึงยังปรากฏแม้ไม่มีใครซื้อ และคอลัมน์จาก sales เป็น `NULL` คำว่า left กับ right อ้างตำแหน่งตารางในคำสั่ง ไม่ได้บอกว่าชนิดใดดีกว่า หากสลับลำดับตาราง ความหมายของ left/right ก็เปลี่ยนตาม

### Full Outer Join

Full outer join รักษาทั้งแถว sales ที่ไม่มี master และแถว things ที่ไม่มี transaction จึงเห็นทั้ง Ali และ Scarf ในผลเดียว เหมาะกับ **reconciliation** หรือการกระทบยอดเพื่อค้นความต่างระหว่างสองชุดข้อมูล แต่ผู้ใช้ต้องตีความ `NULL` ว่าเกิดจากการไม่พบคู่ด้านใด

### Left Semi Join

Left semi join ตอบคำถามว่า “แถวฝั่งซ้ายมีคู่ในฝั่งขวาหรือไม่” แล้วคืนเฉพาะคอลัมน์จากฝั่งซ้าย ไม่ได้นำคอลัมน์ฝั่งขวามาต่อ ในตัวอย่าง `things LEFT SEMI JOIN sales` จึงคืน Tie, Coat และ Hat เพราะมี sales อย่างน้อยหนึ่งแถวอ้างถึงสินค้าเหล่านี้ แต่ไม่คืน Scarf จุดสำคัญคือแม้ Tie มี sales สองแถว semi join ก็ใช้เพื่อทดสอบการมีอยู่ ไม่ได้ทำซ้ำแถว Tie ตามจำนวนคู่เหมือน inner join

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

ตัวอย่างเชิงตัวเลขช่วยให้ตรวจได้ก่อนรัน ถ้า key `V01` มี PO 3 rows และ vendor master ผิดพลาดมี `V01` 2 rows ผล join สำหรับ key นี้จะเป็น 3 × 2 = 6 rows ยอดเงินของแต่ละ PO ถูกทำซ้ำสองครั้ง ถ้ารวมยอดหลัง join จะได้สองเท่า แม้ SQL ไม่มีข้อความแจ้งข้อผิดพลาด วิธีพิสูจน์คือวัด uniqueness ของ master, เทียบ row count ก่อน/หลัง และ reconcile `SUM(amount)` การใช้ `DISTINCT` อาจทำให้แถวดูน้อยลง แต่หาก attributes ต่างกันเพียงบางคอลัมน์ก็ยังไม่แก้ และอาจลบเหตุการณ์จริงที่เหมือนกันโดยบังเอิญ

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

## Lab จากชั้นเรียน: Aggregation บน MovieLens และ Web Log

ส่วนนี้ต่อจากการสร้าง `users` และ `weblog` ใน [บท 02.2](022_hql_schema_serde_and_loading.md) และมาจาก [Lab 02 Hive หน้า 3–5](../lab/lab_02_hive.pdf) จุดประสงค์ไม่ใช่เพียงให้ query รัน แต่ให้เห็นว่า `GROUP BY` เปลี่ยน grain อย่างไร

ตัวอย่างแรกเปลี่ยนจากหนึ่ง row ต่อผู้ใช้เป็นหนึ่ง row ต่อรหัสไปรษณีย์:

```sql
SELECT
    zipcode,
    COUNT(*) AS user_count,
    AVG(age) AS avg_age
FROM users
GROUP BY zipcode
ORDER BY user_count DESC;
```

ก่อนรัน ให้ทำนายว่า output rows จะเท่ากับจำนวน `zipcode` ที่แตกต่างกัน ไม่ใช่จำนวน users แล้วตรวจด้วย:

```sql
SELECT COUNT(*) AS source_rows FROM users;
SELECT COUNT(DISTINCT zipcode) AS expected_group_rows FROM users;
SELECT SUM(user_count) AS reconciled_rows
FROM (
    SELECT zipcode, COUNT(*) AS user_count
    FROM users
    GROUP BY zipcode
) g;
```

`reconciled_rows` ต้องเท่ากับ `source_rows` หากไม่มี row ถูก filter ส่วน `AVG(age)` เป็นค่าเฉลี่ยต่อคนในแต่ละกลุ่ม ไม่ควรนำค่าเฉลี่ยของแต่ละ zipcode ไปเฉลี่ยต่ออีกครั้งโดยไม่ถ่วงด้วย `user_count`

ตัวอย่างที่สองเปลี่ยนจากหนึ่ง row ต่อ log event เป็นหนึ่ง row ต่อ object:

```sql
SELECT object, COUNT(*) AS hit_count
FROM weblog
GROUP BY object
ORDER BY hit_count DESC;
```

ตรวจยอดรวมของ `hit_count` เทียบกับ `COUNT(*)` จาก `weblog` และตรวจ `parse_failures` จากบทก่อนก่อนเชื่อผล หาก regex ทำให้ `object` เป็น `NULL` การ aggregate อาจสร้างกลุ่ม `NULL` ขนาดใหญ่ ซึ่งเป็นสัญญาณ data quality ไม่ใช่ object ที่ได้รับความนิยมจริง

ทดลองให้พังโดยแก้ DDL delimiter/regex ในบท 02.2 แล้วรัน query เดิม สังเกตว่า SQL ยังอาจทำงานจนจบโดยไม่รายงานข้อผิดพลาด แต่ grain และค่ากลุ่มผิด จากนั้นซ่อม SerDe และพิสูจน์ด้วย row reconciliation นี่เชื่อมบทเรียนสำคัญว่า query syntax ถูกไม่ได้รับประกันคำตอบธุรกิจถูก

## Troubleshooting

| อาการ | สาเหตุที่น่าจะเป็น | การตรวจ |
|---|---|---|
| จำนวน row เพิ่มมาก | duplicate keys/many-to-many | count per key ทั้งสองฝั่ง |
| unmatched หาย | ใช้ inner join | เปลี่ยนเป็น outer ตาม population |
| left join กลายเป็น inner | filter right table ใน `WHERE` | ย้ายเงื่อนไขเข้า `ON` หรือรองรับ NULL |
| aggregation ผิด | grain ก่อน group ผิด | inspect sample และ distinct business key |
| job ช้า | shuffle, skew, statistics เก่า | `EXPLAIN`, key distribution, stats |

## แผนผังการประเมินความเข้าใจ

| เป้าหมาย | หลักฐานในบท | คำถาม/กิจกรรมตรวจความเข้าใจ |
|---|---|---|
| อธิบายว่า grouping เปลี่ยน grain อย่างไร | Worked trace เดือน Jan/Feb | ทำนายจำนวน output rows และ reconcile counts |
| เลือก join จากประชากรที่ต้องรักษา | sales/things และ unmatched Ali/Scarf | เลือก inner/outer/semi พร้อมเหตุผล |
| ตรวจ row multiplication | ตัวอย่าง key K และ vendor `V01` | คำนวณจำนวนแถวและผลต่อ `SUM(amount)` |
| เชื่อผลลัพธ์หลังตรวจข้อมูล | MovieLens/Web Log Lab | ตรวจ parse failures, counts และ totals ก่อนตีความ |

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
- รันและ reconcile aggregation จาก MovieLens/web log โดยตรวจ grain และ parse failures ก่อนตีความได้

## Source Coverage และ References

ครอบคลุม PDF หน้า 16–21: grouping, aggregate functions, map-side aggregation, CTAS, inner/outer/semi joins และ join diagram รวมทั้ง aggregation exercises ใน [Lab 02 Hive หน้า 3–5](../lab/lab_02_hive.pdf)

- [Apache Hive Language Manual](https://hive.apache.org/docs/latest/language/)
- [Apache Hive Cost-Based Optimization](https://hive.apache.org/docs/latest/user/cost-based-optimization-in-hive/)
