# บทที่ 03.1: HBase Foundations และ Data Model

> **จากเอกสาร:** [dads6002_03_hbase.pdf](../lecture/dads6002_03_hbase.pdf) หน้า 1–3 และ 7–8  
> **ขอบเขต:** เหตุผลที่ต้องมี HBase, NoSQL, RowKey, Column Family, Column Qualifier, Cell และ Version

> [← บทที่ 02.3: Hive Analytics](023_hive_analytics_and_joins.md) | [สารบัญ](000_readme.md) | [บทที่ 03.2: HBase Architecture →](032_hbase_architecture_and_storage.md)

## ภาพรวมและ Learning Objectives

บท Hive ทำให้ไฟล์จำนวนมากถูกมองเป็นตารางและวิเคราะห์ด้วย HQL ได้ดี แต่คำถามใหม่เกิดขึ้นเมื่อ application ต้องอ่านหรือแก้ข้อมูลหนึ่งรายการอย่างรวดเร็ว เช่น เปิดโปรไฟล์ผู้ป่วยจากรหัสเดียว หรือเพิ่มตัวนับจำนวนการแชร์ทันที การสแกนไฟล์จำนวนมากเป็น batch ไม่เหมาะกับรูปแบบนี้ HBase จึงเพิ่มฐานข้อมูลแบบกระจายที่เข้าถึงข้อมูลด้วย RowKey และรองรับการอ่านเขียนระดับแถวด้วย latency ต่ำกว่างาน Hive แบบ batch

เมื่อเรียนจบบทนี้ ผู้อ่านควรสามารถ:

1. อธิบายว่า HBase แก้ข้อจำกัดใดของ HDFS/Hive และไม่ใช่สิ่งใด
2. แยก NoSQL ออกจากความหมายผิดว่า “ไม่มีโครงสร้าง”
3. อ่านพิกัดข้อมูล `RowKey + Column Family:Qualifier + Timestamp`
4. ออกแบบตาราง sparse ซึ่งแต่ละแถวมี qualifier ไม่เท่ากัน
5. อธิบายขอบเขตของ version และ strong consistency ได้

หัวข้อ Core คือ HBase data model และการเลือกรูปแบบข้อมูล ส่วนชนิด NoSQL อื่นเป็น Supporting และชื่อคำสั่งเป็น Reference

## จาก Hive มาสู่ HBase: ปัญหาที่ระบบเดิมยังตอบไม่ดี

สมมติเครือโรงพยาบาลเก็บเหตุการณ์อุปกรณ์การแพทย์หลายปีไว้ใน HDFS และใช้ Hive สรุปจำนวนแจ้งเตือนรายวัน วิธีนี้เหมาะกับการอ่านข้อมูลจำนวนมากเพื่อหาผลรวม แต่หน้าจอปฏิบัติการต้องเปิดสถานะล่าสุดของอุปกรณ์ `DEV-0098` ทันทีและบันทึกค่าชีพจรใหม่ทุกไม่กี่วินาที หากทุกคำขอต้องเริ่ม batch job เพื่อสแกนไฟล์ คำตอบจะช้าและมี overhead สูง

HBase แก้โจทย์อีกแบบหนึ่ง: application รู้ key ของแถวที่ต้องการและต้องการอ่านหรือเขียนแถวนั้นอย่างรวดเร็วในชุดข้อมูลขนาดใหญ่ HBase ยังเก็บข้อมูลกระจายบนหลายเครื่องและใช้ HDFS เป็น storage ชั้นล่าง แต่เพิ่ม data model, index ตาม RowKey, write path และ read path สำหรับการเข้าถึงแบบสุ่ม ดังนั้น HBase ไม่ได้มาแทน Hive ทุกกรณี Hive เด่นที่การวิเคราะห์หลายแถวด้วยภาษาคล้าย SQL ส่วน HBase เด่นที่ lookup, range scan และ update ตาม RowKey

| คำถาม | Hive เหมาะกว่า | HBase เหมาะกว่า |
|---|---|---|
| ยอดขายรวมรายจังหวัดตลอด 3 ปี | ใช่ เพราะเป็น analytical scan/aggregation | ไม่ใช่จุดเด่น |
| เปิดข้อมูลลูกค้าจาก customer ID | อาจทำได้แต่ไม่ใช่ low-latency serving หลัก | ใช่ หาก RowKey ออกแบบจาก ID |
| Join หลายตารางแบบ ad hoc | HQL รองรับ | ไม่มี native join แบบ RDBMS |
| เพิ่มค่าตัวนับของแถวเดียว | ไม่ใช่ workload หลัก | รองรับ atomic operation ระดับแถว |

## ทำความเข้าใจ HBase สองรอบ

### รอบแรก: ตู้แฟ้มที่เรียงตามรหัส

ให้เปรียบเทียบของจริงสามอย่างก่อน: ตาราง HBase, แถวข้อมูล และตำแหน่งเก็บค่าภายในแถว ลองนึกถึงตู้แฟ้มขนาดใหญ่มากซึ่งเรียงแฟ้มตามรหัสอุปกรณ์ ทุกแฟ้มมีหมวดเอกสารที่กำหนดไว้ เช่น `identity` และ `reading` แต่แฟ้มแต่ละเล่มไม่จำเป็นต้องมีเอกสารทุกชนิด อุปกรณ์วัดอุณหภูมิอาจมี `reading:temperature` ขณะที่เครื่องวัดความดันมี `reading:systolic` และ `reading:diastolic`

เมื่อค่าหนึ่งถูกแก้ ระบบอาจเก็บค่ารุ่นใหม่พร้อมเวลาแทนการลบประวัติทันที ผู้ใช้จึงระบุได้ทั้งรหัสแฟ้ม ชื่อหมวด ชื่อรายการ และรุ่นเวลา ภาพเปรียบเทียบนี้ช่วยให้เห็นข้อมูล sparse และ versioned แต่มีข้อจำกัด: ระบบจริงไม่ได้มีตู้หรือค้นด้วยคน ข้อมูลถูกแบ่งเป็น Regions และกระจายให้ RegionServers ดูแล

### รอบที่สอง: แมปกับศัพท์ทางการ

ตู้ทั้งหมดคือ **Table** แฟ้มหนึ่งเล่มคือ **Row** และรหัสบนแฟ้มคือ **RowKey** หมวดที่กำหนดไว้ก่อนคือ **Column Family** ส่วนชื่อรายการซึ่งเพิ่มต่างกันได้ในแต่ละแถวคือ **Column Qualifier** พิกัดหนึ่งจุดที่มีค่าคือ **Cell** และค่าเดิมหลายรุ่นแยกกันด้วย **Timestamp**

ตัวอย่างข้อมูลจริงหนึ่ง Cell:

```text
RowKey:        DEV-0098
Column:        reading:temperature
Timestamp:     1726209000000
Value:         37.2
```

คำว่า column ใน HBase จึงเขียนเป็น `family:qualifier` เช่น `reading:temperature` โดย `reading` คือกลุ่มกายภาพที่ตั้งค่า storage ร่วมกัน ส่วน `temperature` คือชื่อรายการภายในกลุ่ม

## NoSQL ไม่ได้แปลว่าไม่มี Schema

**จากเอกสาร หน้า 1–2:** NoSQL เป็นคำกว้างซึ่งรวม document, key-value, graph และ column-family databases โดย HBase อยู่ในกลุ่ม column-family และมีต้นแบบจาก Google Bigtable

NoSQL ไม่ได้หมายถึงฐานข้อมูลทุกชนิดทำงานเหมือนกัน และไม่ได้หมายถึงห้ามใช้ SQL โดยนิยาม คำที่ปลอดภัยกว่าคือ “ฐานข้อมูลที่ไม่ยึด relational model แบบดั้งเดิมเป็นแกนหลัก” แต่ละประเภทออกแบบตาม access pattern ต่างกัน HBase จัดแถวตาม RowKey และจัด columns เป็น families จึงไม่ควรถูกมองเป็นตาราง RDBMS ที่เพียงมี column มากขึ้น

คำว่า **schema-less** ในสไลด์ควรอ่านเป็น **schema-flexible** เพราะ HBase ยังมีโครงสร้างที่ต้องออกแบบ Table และ Column Families ต้องประกาศก่อนใช้งาน เพียงแต่ Column Qualifiers ภายใน family สามารถเกิดต่างกันในแต่ละแถวได้ [Apache HBase Data Model](https://hbase.apache.org/docs/datamodel/) อธิบายว่า families คงที่ใน schema แต่ qualifiers เปลี่ยนและต่างกันระหว่าง rows ได้

## Data Model จากใหญ่ไปเล็ก

### Table และ RowKey

Table เป็น namespace ของ rows ทั้งหมด ทุก row ต้องมี RowKey ที่ไม่ซ้ำภายใน table และ HBase จัด rows ตามลำดับ byte ของ RowKey RowKey ไม่มีชนิดข้อมูลระดับฐานข้อมูลให้เราเลือกแบบ `INT` หรือ `VARCHAR`; application แปลงค่าของตนเป็น byte array ดังนั้นวิธี encode จึงมีผลต่อทั้งลำดับและตำแหน่งที่ข้อมูลถูกเก็บ

RowKey ทำหน้าที่พร้อมกันหลายอย่าง: ระบุแถว, เป็น index หลัก, กำหนดลำดับ scan และมีอิทธิพลต่อ Region ที่รับ read/write ถ้าเลือกผิด เราไม่สามารถแก้ด้วย secondary index หรือ join แบบ relational ได้ง่าย การออกแบบจึงเริ่มจากคำถามที่จะอ่าน ไม่ใช่เริ่มจากรายชื่อ attributes

### Column Family และ Column Qualifier

Column Family เป็นหน่วยจัดเก็บกายภาพและ configuration เช่น compression, versions หรือ TTL Columns ใน family เดียวกันถูกเก็บใกล้กัน จึงควรวางข้อมูลที่มักอ่านพร้อมกันและมีลักษณะ lifecycle ใกล้กันไว้ด้วยกัน การมี families จำนวนมากเพิ่ม MemStore และไฟล์ต่อ Region จึงไม่ควรสร้าง family ต่อ field

Column Qualifier คือชื่อย่อยหลังเครื่องหมาย colon เช่น `profile:name` และ `profile:address` Qualifier เพิ่มได้โดยไม่ alter schema และบาง row อาจไม่มี qualifier นั้นเลย เมื่อไม่มีค่า HBase ไม่จำเป็นต้องเก็บ `NULL` placeholder แบบตารางกว้างทั่วไป นี่คือความหมายของ sparse table

ตัวอย่าง Person Table จากสไลด์สามารถเขียนเป็น:

| RowKey | `personal:name` | `personal:address` | `demographic:birthdate` | `demographic:gender` |
|---|---|---|---|---|
| P001 | Mali | Bangkok | 1990-04-11 | F |
| P002 | Anan | - | 1985-08-20 | - |

เครื่องหมาย `-` ในตารางอธิบายหมายถึง Cell ไม่มีอยู่จริง ไม่ใช่ string ที่ HBase ต้องเก็บ

### Cell และ Version

Cell ถูกระบุด้วยพิกัด `{RowKey, Column Family, Column Qualifier, Timestamp}` และเก็บ Value เป็น bytes ถ้า `put` ค่าใหม่ที่พิกัดเดียวกันแต่ timestamp ใหม่ ระบบมีหลาย versions ของ Cell ได้ โดยอ่านรุ่นล่าสุดก่อนตามลำดับ timestamp อย่างไรก็ตามจำนวน versions ที่เก็บขึ้นกับ configuration ของ Column Family; ค่าเริ่มต้นที่สไลด์ระบุคือหนึ่ง version จึงห้ามสรุปว่าทุก update มีประวัติย้อนหลังให้ใช้เสมอ

Version ไม่ใช่ audit log ที่สมบูรณ์โดยอัตโนมัติ เพราะ retention, TTL, compaction และ delete markers มีผลต่อสิ่งที่ยังอ่านได้ หากข้อมูลทางการแพทย์หรือการเงินต้องมีประวัติที่พิสูจน์ได้ ควรออกแบบ event/audit table และ retention policy ชัดเจน ไม่ควรพึ่งหลาย versions โดยไม่กำหนดข้อกำกับ

## Strong Consistency มีขอบเขตอย่างไร

**จากเอกสาร หน้า 2:** HBase ให้ random row-level read/write, strong consistency และ flexible data modeling

คำว่า strong consistency หมายความว่า หลังการเขียนแถวสำเร็จ การอ่านตาม guarantee ของระบบจะไม่ควรเห็นค่าก่อนหน้าราวกับการเขียนยังไม่เกิด แต่ต้องระวังขอบเขต: HBase ให้ atomicity และ consistency ที่ระดับ row เป็นหลัก ไม่ได้ทำให้การแก้หลาย rows กลายเป็น transaction เดียวแบบฐานข้อมูล relational โดยอัตโนมัติ [Apache HBase Data Model](https://hbase.apache.org/docs/datamodel/) อธิบาย ACID semantics และข้อจำกัดไว้ในส่วน Data Model

ตัวอย่างเช่น การเพิ่ม counter `share` ใน row เดียวสามารถทำแบบ atomic ได้ แต่การหัก stock จาก row A และเพิ่ม stock ให้ row B ต้องพิจารณาความล้มเหลวระหว่างสองคำสั่งเอง หากธุรกิจต้องการ all-or-nothing ข้ามหลาย rows อาจต้องเปลี่ยน data model หรือเลือกฐานข้อมูลที่รองรับ transaction นั้นโดยตรง

## Decision Framework: ควรใช้ HBase หรือไม่

HBase เหมาะเมื่อชุดข้อมูลใหญ่ กระจายอยู่บนคลัสเตอร์ access pattern รู้ RowKey หรือช่วง RowKey และต้องอ่าน/เขียนระดับแถวจำนวนมากอย่างสม่ำเสมอ มันไม่ใช่ตัวเลือกอัตโนมัติเมื่อได้ยินคำว่า Big Data

ไม่ควรเริ่มด้วย HBase หากต้องการ joins แบบ ad hoc, transaction ข้ามหลาย rows, secondary indexes หลายชุด หรือ dataset เล็กที่ RDBMS จัดการได้ง่ายกว่า ต้นทุนของ HBase รวมถึง cluster operations, schema ที่ผูกกับ access pattern และความเสี่ยงจาก RowKey hotspot

## Common Misconceptions

- **“HBase เป็น Hive ที่เร็วกว่า”** ไม่จริง เพราะ workload และ data model ต่างกัน
- **“Schema-less จึงไม่ต้องออกแบบ”** ไม่จริง การออกแบบ RowKey และ Column Family เป็นหัวใจ
- **“ทุก column ต้องมีในทุก row”** ไม่จริง Qualifiers เป็น sparse ได้
- **“หลาย versions เท่ากับ audit trail”** ไม่เสมอ เพราะ retention และ compaction มีผล
- **“Strong consistency เท่ากับ transaction ทั้งตาราง”** ไม่จริง Guarantee หลักอยู่ระดับ row

## Likely Exam Focus และ Progressive Practice

**Explain:** เพราะเหตุใด Hive เหมาะกับ aggregation แต่ HBase เหมาะกับ lookup ตาม key?  
**แนวคำตอบ:** Hive สร้าง execution plan สำหรับอ่านข้อมูลจำนวนมากแบบ batch ส่วน HBase มี index และการแบ่งข้อมูลตาม RowKey เพื่อค้นหา Region และแถวเป้าหมาย การเลือกจึงขึ้นกับ access pattern ไม่ใช่ขนาดข้อมูลอย่างเดียว

**Apply:** อุปกรณ์ P001 มี `profile:name` แต่ไม่มี `reading:oxygen` ต้องเก็บ `NULL` หรือไม่?  
**เฉลย:** ไม่จำเป็น Cell ที่ไม่มีค่าไม่ต้องมีอยู่จริง นี่คือ sparse model

**Analyze:** ระบบต้องแก้ยอดคงเหลือสองคลังให้สำเร็จพร้อมกัน HBase row-level consistency เพียงพอหรือไม่?  
**เฉลย:** ไม่เพียงพอโดยอัตโนมัติ เพราะเป็นคนละ RowKey ต้องออกแบบ transaction/compensation หรือใช้ระบบที่ให้ multi-row transaction ตาม requirement

**Evaluate:** ควรสร้าง Column Family แยกทุก qualifier เพื่อความยืดหยุ่นหรือไม่?  
**เฉลย:** ไม่ควร Families เป็นหน่วยกายภาพและเพิ่ม resource/ไฟล์ต่อ Region ควรรวม qualifiers ที่อ่านและมี lifecycle ใกล้กัน

## Objective-to-Assessment Map

| Objective | หลักฐาน |
|---|---|
| แยก HBase จาก Hive | คำถาม Explain และ Decision Framework |
| อธิบาย NoSQL/schema flexibility | Common Misconceptions |
| อ่านพิกัด Cell | ตัวอย่าง `DEV-0098` |
| ออกแบบ sparse row | Person Table และคำถาม Apply |
| อธิบาย version/consistency | คำถาม Analyze และข้อจำกัด audit |

## Mastery Checklist

- [ ] อธิบาย HBase โดยไม่ใช้คำว่า “ฐานข้อมูลเร็ว” อย่างกว้าง ๆ ได้
- [ ] อ่าน `family:qualifier` และพิกัด Cell ได้
- [ ] แยกสิ่งที่กำหนดล่วงหน้ากับสิ่งที่เพิ่มได้ runtime ได้
- [ ] อธิบายผลของ RowKey ต่อ lookup และ range scan ได้
- [ ] ระบุขอบเขตของ versions และ row-level consistency ได้

## Glossary และ Source Coverage

| คำ | ความหมาย |
|---|---|
| RowKey | byte sequence ที่ระบุ row และกำหนดลำดับจัดเก็บ |
| Column Family | กลุ่ม columns ที่กำหนดใน schema และจัดเก็บร่วมกัน |
| Column Qualifier | ชื่อย่อยแบบยืดหยุ่นภายใน family |
| Cell | จุดตัดของ row, family, qualifier และ version |
| Sparse | ไม่ต้องเก็บ Cell ที่ไม่มีค่า |

ครอบคลุมหน้า 1–3 เรื่องข้อจำกัด Hive/NoSQL/HBase/RowKey และหน้า 7–8 เรื่อง Person Table, Column Families, Cells, Versions และข้อจำกัด joins โดยย้าย architecture ไปบท 03.2 และ Shell ไปบท 03.3

## References

- เอกสารหลัก หน้า 1–3 และ 7–8
- [Apache HBase: Data Model](https://hbase.apache.org/docs/datamodel/)
- [Apache HBase: Schema Design](https://hbase.apache.org/docs/schema-design/)

