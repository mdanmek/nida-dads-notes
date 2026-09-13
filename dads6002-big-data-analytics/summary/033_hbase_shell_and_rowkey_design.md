# บทที่ 03.3: HBase Shell, RowKey Design และการใช้งานจริง

> **จากเอกสาร:** [dads6002_03_hbase.pdf](../lecture/dads6002_03_hbase.pdf) หน้า 9–16  
> **ขอบเขต:** Create/Alter, Put/Get/Increment, Versions, Scan, Filters, Delete, Flush และ Hotspot

> [← บทที่ 03.2: HBase Architecture](032_hbase_architecture_and_storage.md) | [สารบัญ](000_readme.md)

## Learning Objectives และจุดเริ่มต้น

สองบทก่อนสร้าง mental model ของข้อมูลและกลไกภายใน บทนี้จึงค่อยนำคำสั่ง Shell มาใช้พิสูจน์แนวคิด ไม่ควรจำ `put`, `get` และ `scan` เป็นรายการแยกกัน เพราะประสิทธิภาพของทุกคำสั่งย้อนกลับไปที่ RowKey, Column Family และ Region

เมื่อเรียนจบควรสามารถ:

1. สร้าง table และอธิบาย schema ที่ประกาศได้
2. เขียน อ่าน เพิ่ม counter และอ่านหลาย versions อย่างถูกพิกัด
3. อธิบายลำดับแบบ lexicographic และออกแบบ RowKey เพื่อลด hotspot
4. แยก point `get`, range `scan` และ filter ออกจากกัน
5. ใช้ destructive commands พร้อม validation และ cleanup ที่ปลอดภัย

## ก่อนพิมพ์คำสั่ง: ออกแบบจาก Query ย้อนกลับ

สมมติเราต้องสร้างระบบบันทึกลิงก์ตามตัวอย่างสไลด์ หนึ่ง row แทนหนึ่งเว็บไซต์ ใช้ domain กลับด้าน เช่น `org.hbase.www` เป็น RowKey ข้อมูลชื่อเรื่องอยู่ใน `link:title` และจำนวนแชร์อยู่ใน `statistics:share` Access patterns คือเปิดเว็บไซต์หนึ่งรายการจาก domain, เพิ่ม counter และ scan เว็บไซต์กลุ่มเดียวกัน

การกลับ domain ทำให้ส่วนกว้างอยู่ด้านหน้า เช่น `org.apache.www`, `org.apache.mail` และ `org.apache.jira` เรียงใกล้กัน จึง scan กลุ่ม Apache ได้ง่ายกว่าใช้ `www.apache.org`, `mail.apache.org` และ `jira.apache.org` ซึ่งจะกระจายตาม subdomain [Apache HBase Data Model](https://hbase.apache.org/docs/datamodel/) ใช้แนวคิด reversed domain เป็นตัวอย่าง RowKey เช่นกัน

## HBase Shell และ Schema Lifecycle

เริ่ม Shell ด้วย:

```bash
hbase shell
```

คำสั่งใน HBase Shell ใช้รูปแบบ Ruby/JRuby และชื่อ table, row, column ควรใส่ single quotes ตาม [Apache HBase Shell](https://hbase.apache.org/docs/shell/) ตัวอย่างในสไลด์มี smart quotes จาก PowerPoint ซึ่งต้องเปลี่ยนเป็น ASCII quotes ก่อนรัน

สร้าง table ใน default namespace โดยกำหนดสอง Column Families ตั้งแต่ต้น:

```ruby
create 'linkshare', 'link', 'statistics'
list
describe 'linkshare'
```

เหตุที่กำหนด `link` และ `statistics` แยกกันควรมาจาก storage/access policy ไม่ใช่เพียงชื่อสวยงาม เช่น metadata ลิงก์อาจเก็บหลาย versions ส่วน counter อาจมี retention ต่างกัน Qualifiers อย่าง `title`, `url` และ `share` ไม่ต้องประกาศใน `create`

สไลด์สอน workflow แบบเดิมให้ disable ก่อนเปลี่ยน schema:

```ruby
disable 'linkshare'
alter 'linkshare', {NAME => 'link', VERSIONS => 5}
enable 'linkshare'
describe 'linkshare'
```

ความสามารถ online schema change ต่างตาม operation และ HBase version สำหรับการเรียนให้ทำตาม environment ของอาจารย์และอ่าน `help 'alter'` ก่อน หาก disable table clients จะอ่าน/เขียนไม่ได้ชั่วคราว จึงต้องวาง maintenance และตรวจว่า table กลับเป็น enabled

## Put ไม่ใช่ Insert อย่างเดียว

```ruby
put 'linkshare', 'org.hbase.www', 'link:title', 'Apache HBase'
get 'linkshare', 'org.hbase.www'
```

`put` ระบุ table, RowKey, column และ value ถ้า Cell พิกัดเดียวกันยังไม่มี มันสร้างค่าใหม่ หากมีแล้ว `put` ค่าใหม่จะสร้าง version ตาม timestamp และค่าล่าสุดจะถูกอ่านก่อน จึงเป็นทั้ง insert/update ในภาษาทั่วไป แต่ไม่ใช่ SQL `UPDATE` ที่ค้นหลาย rows ด้วย predicate

สำหรับ counter ให้ใช้ atomic increment แทนการอ่านค่าเดิมมาบวกใน client:

```ruby
incr 'linkshare', 'org.hbase.www', 'statistics:share', 1
get_counter 'linkshare', 'org.hbase.www', 'statistics:share'
```

ถ้า client สองตัวอ่านค่า 10 พร้อมกัน แล้วต่างคนเขียน 11 อาจเกิด lost update แต่ `incr` ให้ server ทำการเพิ่มแบบ atomic ตาม row/column operation จึงเหมาะกับ counter มากกว่า read-modify-write ฝั่ง client

## Versions และ Time Range

เขียนสอง versions แบบกำหนด timestamp เพื่อให้ทดลองซ้ำได้:

```ruby
put 'linkshare', 'org.hbase.www', 'link:title', 'Apache HBase v1', 1700000000000
put 'linkshare', 'org.hbase.www', 'link:title', 'Apache HBase v2', 1700000001000

get 'linkshare', 'org.hbase.www', {
  COLUMN => 'link:title',
  VERSIONS => 2
}
```

คำสั่งจะคืนสอง versions ได้ก็ต่อเมื่อ Column Family ตั้ง `VERSIONS` ไว้เพียงพอ หากยังเป็นค่าเริ่มต้นหนึ่ง version ผลอาจเห็นเพียงล่าสุด การกำหนด `{TIMERANGE => [start, end]}` ใช้ช่วง timestamp หน่วย milliseconds และควรตรวจ semantics ของปลายช่วงตาม version; โดยทั่วไป start รวมและ end ไม่รวม

Timestamp เป็นส่วนของ Cell coordinate แต่ไม่ควรใช้แทน business event time โดยไม่คิด หากข้อมูลมาถึงช้า server timestamp อาจสะท้อนเวลา ingestion ไม่ใช่เวลาที่เหตุการณ์เกิด ควรเก็บ event time เป็น qualifier เมื่อธุรกิจต้องวิเคราะห์เวลาเหตุการณ์จริง

## RowKey เรียงตาม Bytes: เหตุใด 100 มาก่อน 2

HBase ไม่รู้ว่า string `'100'` เป็นเลขหนึ่งร้อย มันเปรียบเทียบ byte จากซ้ายไปขวา ดังนั้นลำดับของ strings คือ `'1'`, `'10'`, `'100'`, `'11'`, ... `'2'` เพราะทุกค่าที่ขึ้นต้นด้วย byte ของ `1` อยู่ก่อน byte ของ `2`

ถ้าต้องการให้เลขเรียงตามค่าจริง มีสองวิธีหลัก:

- encode integer เป็น fixed-width binary ด้วยกติกาที่รักษาลำดับ
- zero-pad string ให้กว้างเท่ากัน เช่น `000001`, `000002`, `000100`

ต้องเลือกตาม client libraries และช่วงค่า การใช้ `str(number)` โดยไม่ pad แล้วหวังว่า scan จะเรียงเชิงตัวเลขเป็นความผิดพลาดที่พบบ่อย

## Point Get, Range Scan และ Filter

### Point Get

เมื่อรู้ RowKey เต็ม `get` สามารถ locate Region และอ่านแถวเป้าหมายได้:

```ruby
get 'linkshare', 'org.hbase.www', {COLUMN => ['link:title', 'statistics:share']}
```

นี่คือ access pattern ที่ HBase เด่น เพราะไม่ต้องไล่ทุก row

### Range Scan

```ruby
scan 'linkshare', {
  STARTROW => 'org.apache.',
  STOPROW => 'org.apache/'
}
```

แนวคิดสำคัญคือ scan เริ่มที่ key แรกซึ่งมากกว่าหรือเท่ากับ `STARTROW` และหยุดก่อน `STOPROW` โดยไม่จำเป็นต้องมี row ตรงกับ boundary ใน table ชื่อ option ใน HBase Shell ปัจจุบันมักใช้ `STOPROW`; สไลด์ใช้ `ENDROW` จึงต้องตรวจ `help 'scan'` ใน environment ก่อนรัน

การเลือก RowKey ที่ทำให้ข้อมูลซึ่งอ่านร่วมกันมี prefix เดียวกันช่วยให้ range scan มีขอบเขตสั้น แต่ถ้าเขียนทุก key ด้วย prefix เวลาเดียวกันตามลำดับ อาจทำให้ Region ท้ายสุดรับ writes ทั้งหมด เกิด hotspot

### Filter

สไลด์แนะนำ RowFilter, ValueFilter, ColumnRangeFilter, SingleColumnValueFilter และ RegexStringComparator Filters ช่วยตัดผลที่ไม่ตรงเงื่อนไขฝั่ง RegionServer ก่อนส่งกลับ client แต่ไม่ได้สร้าง secondary index อัตโนมัติ หาก filter ต้องตรวจข้อมูลจำนวนมาก ระบบยังอาจ scan rows/cells จำนวนมาก ดังนั้น “ส่งกลับน้อย” ไม่เท่ากับ “อ่านน้อย”

ตัวอย่างตามแนวคิดสไลด์ โดย syntax filter อาจต่างตาม version:

```ruby
show_filters
scan 'linkshare', {
  FILTER => "RowFilter(>, 'binary:org.hbase')"
}
```

ก่อนใช้ filter ให้ถามว่าสามารถ encode เงื่อนไขสำคัญใน RowKey เพื่อจำกัด range ก่อนได้หรือไม่ แล้วค่อยใช้ filter ภายในช่วงนั้น

## RowKey Hotspot: ความเร็วของ Range Scan แลกกับการกระจาย Write

Rows ที่อยู่ติดกันถูกจัดใน Region เดียวกันหรือใกล้กัน คุณสมบัตินี้ทำให้ range scan เร็ว แต่ถ้า RowKeys ใหม่เพิ่มแบบเรียงขึ้น เช่น timestamp อยู่ด้านหน้า writes ล่าสุดทั้งหมดจะมุ่งไป Region ปลายสุด RegionServer หนึ่งตัวรับภาระสูง ขณะที่ตัวอื่นว่าง

แนวทางแก้มี trade-off:

| วิธี | ช่วยอะไร | ต้นทุน |
|---|---|---|
| Salt/hash prefix | กระจาย writes หลาย Regions | การอ่านช่วงต้องยิงหลาย prefixes แล้วรวมผล |
| Reverse timestamp | อ่านค่าล่าสุดก่อนใน entity เดียว | ต้อง encode ให้ถูกและยังเสี่ยง hotspot หากไม่มี entity prefix |
| Composite key เช่น `device#date#event` | เก็บ events ของ device ใกล้กัน | Query ข้าม devices ต้องหลาย scans |
| Pre-split Regions | กระจายโหลดเริ่มต้นเมื่อรู้ key ranges | split ผิดทำให้ Regions ไม่สมดุล |

ไม่มี RowKey ที่ดีที่สุดสากล ต้องเริ่มจาก queries ที่สำคัญที่สุด, write distribution, cardinality และขนาด row แล้วทดสอบด้วยข้อมูลใกล้ production

## Delete, Drop และ Flush

```ruby
delete 'linkshare', 'org.hbase.www', 'link:title'
flush 'linkshare'
```

Delete สร้างเครื่องหมายลบตาม version semantics และ compaction จัดการข้อมูลเก่าในภายหลัง จึงไม่ควรตีความว่าทุก byte หายทันที ส่วน `flush` บังคับ MemStores ของ scope ที่ระบุให้สร้าง HFiles; ใช้เพื่อการทดลอง/ปฏิบัติการ ไม่ควรใช้แก้ performance แบบสุ่มเพราะเพิ่ม StoreFiles ได้

การลบ table ต้อง disable และ drop:

```ruby
disable 'linkshare'
drop 'linkshare'
```

นี่เป็น destructive operation ให้ตรวจ `list`, environment และชื่อ table ก่อนเสมอ สำหรับ Lab ควรใช้ชื่อเฉพาะของตนและเก็บคำสั่งสร้างข้อมูลใหม่ได้

## Guided Lab: Copy, Predict, Execute, Validate

### 1. สร้างและตรวจ schema

```ruby
create 'linkshare_lab', 'link', 'statistics'
describe 'linkshare_lab'
```

ทำนายก่อนรันว่า qualifiers ใดจะปรากฏ แม้ยังไม่ได้ประกาศ จากนั้น `put`:

```ruby
put 'linkshare_lab', 'org.apache.www', 'link:title', 'Apache'
put 'linkshare_lab', 'org.hbase.www', 'link:title', 'HBase'
incr 'linkshare_lab', 'org.hbase.www', 'statistics:share', 1
```

### 2. อ่านและตรวจผล

```ruby
get 'linkshare_lab', 'org.hbase.www'
scan 'linkshare_lab'
```

หลักฐานผ่านคือมีสอง RowKeys, `org.hbase.www` มี title และ counter เท่ากับ 1 และลำดับ scan ตรง byte order

### 3. Modify และ Diagnose

เพิ่ม `org.hive.www` แล้วทำนายตำแหน่ง ทดลอง scan ช่วง จากนั้นเขียน IDs `'1'`, `'2'`, `'10'` ใน table ทดลองและอธิบายเหตุผลของลำดับที่เห็น อย่าแก้ด้วย sort หลังอ่านโดยไม่ตอบว่าการออกแบบ RowKey ควรเปลี่ยนหรือไม่

### 4. Cleanup

```ruby
disable 'linkshare_lab'
drop 'linkshare_lab'
list
```

## Validation และ Troubleshooting

| อาการ | สาเหตุที่เป็นไปได้ | วิธีตรวจ/แก้ |
|---|---|---|
| เห็น version เดียว | Family ตั้ง `VERSIONS => 1` | `describe`, alter version policy แล้วเขียนใหม่ |
| Range scan ไม่ได้ rows ที่คาด | byte order/boundary ผิด | แสดง RowKeys จริงและตรวจ STOPROW exclusive |
| Write บาง Region สูงผิดปกติ | monotonic/hot prefix | Region metrics และ key distribution |
| Filter ช้าแม้คืนไม่กี่แถว | ไม่มี index และ scan ช่วงกว้าง | จำกัด STARTROW/STOPROW หรือ redesign key |
| Alter/drop ไม่ได้ | table state หรือ syntax ต่าง version | `is_enabled`, `help`, `describe` |

## Likely Exam Focus และ Model Answers

**Explain:** `get` กับ `scan` ต่างกันอย่างไร?  
**เฉลย:** `get` รู้ RowKey เต็มและอ่านแถวเป้าหมาย ส่วน `scan` เดินตามช่วง RowKey อาจกำหนด columns/filter เพิ่มได้ Cost จึงขึ้นกับช่วงที่ต้องอ่าน

**Apply:** ต้องการให้ string IDs 1–100 เรียงเชิงตัวเลข ควรทำอย่างไร?  
**เฉลย:** encode แบบ order-preserving หรือ zero-pad ให้กว้างเท่ากัน เช่น `001`–`100`

**Analyze:** RowKey เริ่มด้วย timestamp ปัจจุบันทุก record ทำไม write จึงช้าแม้มีหลาย RegionServers?  
**เฉลย:** keys ใหม่อยู่ช่วงปลายใกล้กันและไป Region เดียว เกิด hotspot ต้องกระจาย prefix หรือ redesign ตาม access pattern

**Evaluate:** ใช้ ValueFilter แทน secondary index ได้หรือไม่?  
**เฉลย:** Filter ลดข้อมูลที่ส่งกลับ แต่ยังอาจ scan จำนวนมาก จึงไม่เท่ากับ indexed lookup หาก query สำคัญต้องพิจารณา alternate table/index design

## Objective-to-Assessment Map และ Mastery Checklist

| Objective | หลักฐาน |
|---|---|
| สร้าง/อธิบาย schema | Guided Lab และ `describe` |
| Put/Get/Counter/Versions | คำสั่งพร้อม expected state |
| RowKey/order/hotspot | ทดลอง IDs และคำถาม Analyze |
| Get/Scan/Filter | ตาราง troubleshooting และ Evaluate |
| Operations ปลอดภัย | Cleanup และ state checks |

- [ ] เขียนพิกัด Cell ในคำสั่ง `put/get` ได้
- [ ] ทำนายลำดับ RowKeys แบบ string ได้
- [ ] ออกแบบ RowKey จาก access pattern พร้อม trade-off ได้
- [ ] อธิบายเหตุใด filter ไม่ใช่ index ได้
- [ ] ใช้ disable/drop/flush โดยอธิบายผลกระทบได้

## Source Coverage และ References

ครอบคลุมหน้า 9–16: Shell, create/list, alter/disable/enable, sorted RowKey/hotspot, put/incr/get, timerange/versions, scan boundaries, filters, delete/update/drop และ flush พร้อมแก้ smart quotes, `statistics: share`, `ENDROW` และคำอธิบายที่ขึ้นกับ version

- เอกสารหลัก หน้า 9–16
- [Apache HBase: Shell](https://hbase.apache.org/docs/shell/)
- [Apache HBase: Data Model](https://hbase.apache.org/docs/datamodel/)
- [Apache HBase: Schema Design](https://hbase.apache.org/docs/schema-design/)
