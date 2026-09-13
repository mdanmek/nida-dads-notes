# บทที่ 03.2: HBase Architecture, Read/Write Path และ Storage

> **จากเอกสาร:** [dads6002_03_hbase.pdf](../lecture/dads6002_03_hbase.pdf) หน้า 3–6  
> **ขอบเขต:** Region, HMaster, RegionServer, WAL, MemStore, HFile, BlockCache, ZooKeeper, META และ Compaction

> [← บทที่ 03.1: HBase Data Model](031_hbase_foundations_and_data_model.md) | [สารบัญ](000_readme.md) | [บทที่ 03.3: Shell และ RowKey Design →](033_hbase_shell_and_rowkey_design.md)

## Learning Objectives และ Prerequisites

บทก่อนอธิบายว่าหนึ่งค่าถูกระบุด้วย RowKey, column และ timestamp บทนี้ตอบคำถามต่อว่า เมื่อ table ใหญ่เกินเครื่องเดียว ระบบรู้ได้อย่างไรว่า row อยู่เครื่องใด การเขียนที่ยังอยู่ใน memory จะไม่หายเมื่อ process ล้มได้อย่างไร และเหตุใดการมี HFiles มากขึ้นทำให้ read path แพงขึ้น

ควรอ่านบท 03.1 และเข้าใจ HDFS block/replication จาก [บท 01.2](012_hdfs_and_yarn.md) ก่อน เมื่อจบบทนี้ควรทำได้ดังนี้:

1. ติดตาม client จาก RowKey ไปยัง RegionServer ที่รับผิดชอบ
2. อธิบาย write path ผ่าน WAL, MemStore, flush และ HFile
3. อธิบาย read path ผ่าน BlockCache, MemStore และ HFiles
4. วิเคราะห์ RegionServer failure และ recovery
5. แยก flush, minor compaction และ major compaction ได้

## ภาพรวมแบบไม่ใช้ศัพท์เทคนิค

สมมติตารางอุปกรณ์มีแฟ้มเรียงตามรหัสตั้งแต่ `DEV-0001` ถึง `DEV-9999` เมื่อแฟ้มมากเกินเจ้าหน้าที่คนเดียว จึงแบ่งช่วงอักษรให้หลายโต๊ะดูแล โต๊ะ A ดูแล `DEV-0001` ถึงก่อน `DEV-3000` โต๊ะ B ดูแลช่วงถัดไป และมีสารบัญกลางบอกว่าแต่ละช่วงอยู่โต๊ะใด

เมื่อมีข้อมูลใหม่ เจ้าหน้าที่ไม่รีบเปิดแฟ้มบนชั้นแล้วเขียนทุกครั้ง เพราะการเขียนชิ้นเล็กลงชั้นเก็บถาวรจะช้า เขาจดเหตุการณ์ลงสมุดกู้คืนก่อน แล้วรวบรวมข้อมูลใหม่ไว้ในถาดที่เรียงตามรหัส เมื่อถาดเต็มจึงยกข้อมูลทั้งชุดไปสร้างแฟ้มถาวรใหม่ ส่วนข้อมูลที่ถูกเปิดบ่อยจะมีสำเนาในโต๊ะทำงานเพื่ออ่านเร็วขึ้น

ในระบบจริง ช่วง RowKey คือ Region, โต๊ะที่ดูแลคือ RegionServer, สารบัญตำแหน่ง Region คือ `hbase:meta`, สมุดกู้คืนคือ WAL, ถาดใน memory คือ MemStore, แฟ้มถาวรคือ HFile และสำเนาข้อมูลที่อ่านบ่อยคือ BlockCache อุปมานี้หยุดตรงที่ระบบจริงมี concurrency, checksums, indexes และ HDFS replication ซึ่งซับซ้อนกว่าการทำงานของเจ้าหน้าที่

## Region และการกระจาย Table

HBase แบ่ง table ตามช่วง RowKey เป็น **Regions** แต่ละ Region มี start key และ end key และถูกเปิดให้ RegionServer หนึ่งตัวรับบริการในเวลาหนึ่ง เมื่อ Region โตถึงเกณฑ์ ระบบสามารถ split ออกเป็นสองช่วง ทำให้ table ขยายข้าม RegionServers ได้

คำว่า Region ไม่เหมือน HDFS block Region เป็นช่วงเชิงตรรกะของ rows ใน HBase และภายในมี Store แยกตาม Column Family ส่วน HFile เป็นไฟล์จริงบน HDFS HDFS ยังคงรับผิดชอบ durability ของ bytes แต่ HBase รับผิดชอบความหมายของ rows, columns, versions และการส่งคำขอไป Region ที่ถูกต้อง

## องค์ประกอบและขอบเขตความรับผิดชอบ

### HMaster

HMaster จัดการงานควบคุมระดับคลัสเตอร์ เช่น assign/reassign Regions, load balancing และ schema/admin operations แต่ client ไม่จำเป็นต้องส่งทุก `get` หรือ `put` ผ่าน HMaster หลังรู้ตำแหน่ง Region แล้ว client ติดต่อ RegionServer โดยตรง หาก HMaster หยุดชั่วคราว existing Regions อาจยังให้บริการได้บางส่วน แต่ admin operations, reassignment และ recovery จะได้รับผล จึงต้องมี high availability ตามการติดตั้งจริง

### RegionServer

RegionServer รับ read/write ของ Regions ที่ตนเปิดอยู่ มันดูแล WAL, MemStores, BlockCache และ Stores/HFiles ของ Regions เหล่านั้น สไลด์กล่าวว่า RegionServer รันบน HDFS DataNode ซึ่งเป็น deployment ที่มัก colocate เพื่อ locality แต่ควรแยกว่า RegionServer กับ DataNode เป็นคนละ service ไม่ใช่องค์ประกอบเดียวกัน

### ZooKeeper และ `hbase:meta`

สไลด์อธิบาย flow รุ่นดั้งเดิมว่า ZooKeeper ช่วยบอกตำแหน่ง META และ META บอกว่า RowKey อยู่ Region ใด แก่นที่ควรจำคือ client ต้องมี **bootstrap location** แล้วค้น mapping จาก key range ไป RegionServer ก่อน caching ตำแหน่งไว้ คำขอครั้งถัดไปจึงไม่ต้องค้นใหม่ทุกครั้ง เมื่อ Region ย้ายหรือ split แล้ว cache เก่า Client จะ refresh location

ใน HBase รุ่นต่างกัน bootstrap mechanism และบทบาท ZooKeeper อาจต่างกัน จึงไม่ควรจำขั้น RPC แบบตายตัวข้าม version แต่ `hbase:meta` ยังคงเป็น catalog สำคัญของ Region locations ดู architecture ปัจจุบันได้จาก [Apache HBase Architecture](https://hbase.apache.org/docs/architecture/)

## Write Path: จาก `put` ไปสู่ HFile

สมมติ application เขียน `DEV-0098, reading:temperature, 37.2` กระบวนการเชิงแนวคิดเป็นดังนี้:

1. Client แปลง RowKey และค่าต่าง ๆ เป็น bytes แล้วหา Region ที่ครอบคลุม `DEV-0098`
2. Client ส่ง `put` ไปยัง RegionServer ที่ดูแล Region นั้น
3. RegionServer บันทึกการเปลี่ยนแปลงลง **Write-Ahead Log (WAL)** เพื่อให้มีหลักฐาน durable ก่อนข้อมูลใน memory สูญหาย
4. RegionServer เพิ่ม Cell ลง **MemStore** ของ Column Family ที่เกี่ยวข้อง MemStore เก็บข้อมูลเรียงตาม key
5. เมื่อเงื่อนไข flush ถึงเกณฑ์ MemStore ถูกเขียนเป็น HFile ใหม่บน HDFS
6. หลังข้อมูลใน HFile ปลอดภัย ส่วน WAL ที่ไม่จำเป็นต่อ recovery แล้วจึงถูกจัดการตาม lifecycle

WAL กับ MemStore จึงแก้คนละปัญหา WAL แก้ durability เมื่อ RegionServer ล้ม ส่วน MemStore รวม random writes ให้กลายเป็น sequential sorted file write ถ้าบันทึกเฉพาะ MemStore การดับของ process อาจทำให้ค่าที่ตอบรับแล้วหาย แต่ถ้าเขียน HFile ใหม่ทุก Cell ระบบจะสร้าง small files และ I/O มากเกินไป

### Failure และ recovery

ถ้า RegionServer ล้มก่อน MemStore flush, HMaster/cluster coordination ตรวจพบ server failure, Regions ถูก assign ไปยัง RegionServers อื่น และ WAL ที่เกี่ยวข้องถูก replay เพื่อสร้าง updates ที่ยังไม่อยู่ใน HFiles ใหม่ การ recovery จึงอาศัยทั้ง HFiles ที่ durable อยู่แล้วและ WAL ของข้อมูลใหม่ ไม่ใช่อาศัย MemStore ซึ่งหายไปพร้อม process

การที่ `put` คืน success ยังไม่เท่ากับมี HFile ใหม่ทันที สิ่งที่ต้องพิสูจน์คือ WAL durability และ acknowledgement semantics ตาม configuration นอกจากนี้ HDFS replication ป้องกัน disk/node failure แต่ไม่แทน backup เมื่อผู้ใช้ลบข้อมูลผิด

## Read Path: ระบบค้นค่าจากที่ใด

สมมติ client ขอค่าล่าสุดของ `DEV-0098` หลังหา RegionServer แล้ว ระบบต้องพิจารณาข้อมูลหลายชั้นเพราะค่าล่าสุดอาจเพิ่งเขียนและยังไม่ flush:

1. ตรวจข้อมูลที่เพิ่งเขียนใน MemStore
2. ตรวจ BlockCache สำหรับ HFile blocks ที่เคยอ่านและยังอยู่ใน memory
3. อ่าน StoreFiles/HFiles ที่เกี่ยวข้องจาก storage โดยใช้ indexes, Bloom filters และ metadata ช่วยลดไฟล์/blocks ที่ต้องเปิด
4. รวม candidates ตาม key, timestamp และ delete markers เพื่อคืน version ที่ตรง request

สไลด์ย่อว่า “ค้น BlockCache และ MemStore ก่อน แล้ว binary search HFiles” ซึ่งใช้สร้างภาพรวมได้ แต่ read path จริงไม่ใช่ binary search ทุกไฟล์แบบตรงไปตรงมา และอาจต้องตรวจ HFiles หลายชุด ยิ่งมี HFiles ทับซ้อนกันมาก read amplification ยิ่งสูง นี่คือเหตุผลที่ต้องมี compaction

## Flush และ Compaction ต่างกันอย่างไร

**Flush** เปลี่ยน MemStore หนึ่งชุดเป็น HFile ใหม่ ทำให้ข้อมูลออกจาก memory ไป storage แต่ไม่ได้รวม HFiles เดิม ดังนั้น flush ถี่เกินไปสร้างไฟล์เล็กจำนวนมาก

**Minor compaction** เลือก HFiles บางชุดใน Store มารวมเป็นไฟล์ใหม่ที่ใหญ่ขึ้น เพื่อลดจำนวนไฟล์ที่ read path ต้องตรวจ ส่วน **Major compaction** พยายาม rewrite HFiles ทั้งหมดของ Store ที่เกี่ยวข้อง เพื่อรวม versions/delete markers ตาม policy และลดไฟล์ แต่ใช้ I/O สูง

ข้อความในสไลด์ที่ว่า major compaction รวม HFiles “ของ table” เป็น HFile เดียวควรตีความในขอบเขต Store/Region ไม่ใช่ทั้งตารางข้ามทุก Regions และ Column Families เพราะ table ขนาดใหญ่ยังคงกระจายเป็นหลาย Regions [Apache HBase Architecture](https://hbase.apache.org/docs/architecture/) อธิบายโครง RegionServer, Regions และ Stores ไว้แยกกัน

| Operation | Input | Output | จุดประสงค์หลัก | ความเสี่ยง |
|---|---|---|---|---|
| Flush | MemStore | HFile ใหม่ | ทำข้อมูลใน memory ให้ durable เป็นไฟล์ | ไฟล์เล็กเพิ่ม |
| Minor compaction | HFiles บางชุด | HFile ที่รวมแล้ว | ลด read amplification | I/O background |
| Major compaction | HFiles ของ Store ตาม scope | ชุดไฟล์ rewrite | รวมข้อมูลและจัดการ obsolete cells | I/O สูงและกระทบ workload |

## BlockCache: เร็วขึ้นแต่ไม่ใช่แหล่งข้อมูลถาวร

BlockCache เก็บ blocks ที่อ่านบ่อยใน memory เมื่อ cache hit ระบบลดการอ่าน storage แต่ถ้า cache เต็ม blocks ที่ใช้น้อยจะถูก evict การ restart RegionServer ทำให้ cache อุ่นใหม่ จึงอาจเห็น latency สูงชั่วคราว Cache ช่วย performance ไม่ใช่ durability และข้อมูลที่ไม่อยู่ใน cache ยังต้องอ่านได้จาก HFiles

## Worked Trace: Cell หนึ่งรายการตลอดวงจร

| เหตุการณ์ | WAL | MemStore | HFile | สิ่งที่ Client อ่านได้ |
|---|---|---|---|---|
| ก่อน `put` | ไม่มี update | ไม่มี | ค่าเดิม 36.8 | 36.8 |
| หลัง `put` สำเร็จ | มี 37.2 | มี 37.2 | ยังเป็น 36.8 | 37.2 จาก merged read |
| หลัง flush | WAL entry เลิกจำเป็นตาม lifecycle | ถูก clear ชุดนั้น | มี 37.2 ในไฟล์ใหม่ | 37.2 |
| หลัง compaction | ตาม lifecycle | - | HFiles ถูก merge/rewrite | 37.2 |

Validation สำคัญคือ read-after-write ได้ค่าที่คาด, timestamp ถูกต้อง, RegionServer restart แล้วยังอ่านค่าได้ และจำนวน HFiles/latency หลัง compaction เปลี่ยนตามสมมติฐานโดยไม่ทำ row count หรือ versions ที่ต้องเก็บหาย

## Troubleshooting และ Decision Practice

| อาการ | สมมติฐาน | หลักฐานที่ตรวจ |
|---|---|---|
| Write latency สูง | WAL/HDFS ช้า, Region hotspot | WAL sync latency, Region request rate |
| Read ช้าหลัง restart | BlockCache เย็น | cache hit ratio และ disk reads |
| Read ช้าลงเรื่อย ๆ | HFiles มาก/read amplification | StoreFile count, compaction queue |
| RegionServer ล้มแล้วบาง row ชั่วคราวเข้าไม่ได้ | Region recovery/reassignment | server log, Region state, WAL replay |
| MemStore สูง | flush pressure หรือ hot Region | MemStore size และ flush metrics |

## Likely Exam Focus และ Model Answers

**Explain:** เพราะเหตุใดต้องเขียน WAL ก่อน MemStore?  
**เฉลย:** MemStore อยู่ใน memory และหายเมื่อ process ล้ม WAL เป็นหลักฐาน durable สำหรับ replay ขณะที่ MemStore ช่วยรวม writes ให้เขียน HFile แบบ sorted batch

**Trace:** หลัง `put` สำเร็จแต่ยังไม่ flush ค่าใหม่อ่านได้หรือไม่?  
**เฉลย:** ได้ Read path รวมข้อมูลจาก MemStore กับ storage จึงไม่ต้องรอ HFile ใหม่

**Analyze:** RegionServer ล้มก่อน flush แล้วข้อมูลกู้จาก BlockCache ได้หรือไม่?  
**เฉลย:** ไม่ BlockCache เป็น read cache ไม่ใช่ recovery log ต้องใช้ WAL replay ร่วมกับ HFiles

**Evaluate:** ควรสั่ง major compaction ระหว่าง peak time เพื่อให้ read เร็วทันทีหรือไม่?  
**เฉลย:** ไม่ควรสรุปเช่นนั้น Major compaction ใช้ I/O สูง ต้องดู StoreFile count, SLA และ maintenance window ประโยชน์ระยะหลังอาจแลกกับ latency ระหว่างทำงาน

## Objective-to-Assessment Map และ Mastery Checklist

| Objective | หลักฐาน |
|---|---|
| ค้น RegionServer | Client → META/cache → RegionServer narrative |
| Write path | Trace table และ WAL/MemStore question |
| Read path | กรณีค่าใหม่ยังไม่ flush |
| Failure recovery | RegionServer failure และ WAL replay |
| Flush/compaction | ตารางเปรียบเทียบและ Evaluate question |

- [ ] วาด write path และอธิบายเหตุผลของแต่ละขั้นได้
- [ ] วาด read path โดยไม่สับสน cache กับ durable storage ได้
- [ ] แยก Region จาก HDFS block ได้
- [ ] อธิบาย RegionServer failure/recovery ได้
- [ ] แยก flush, minor และ major compaction ได้

## Source Coverage และ References

ครอบคลุมหน้า 3–6: Regions/HFiles, HMaster, RegionServer, WAL, BlockCache, MemStore, HFiles, read path, compaction, ZooKeeper และ META โดยชี้แจงส่วนที่สไลด์ย่อเกินไปเกี่ยวกับ deployment, lookup และ compaction scope

- เอกสารหลัก หน้า 3–6
- [Apache HBase: Architecture](https://hbase.apache.org/docs/architecture/)
- [Apache HBase: Data Model](https://hbase.apache.org/docs/datamodel/)

