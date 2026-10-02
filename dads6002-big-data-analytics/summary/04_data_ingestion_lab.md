# ปฏิบัติการ Data Ingestion: Sqoop, Flume และ Kafka

**แก่นของบท:** ปฏิบัติการสามชุดที่พิสูจน์แนวคิดในไฟล์ Lecture ด้วยการรันจริง ได้แก่ ย้ายตาราง MySQL เข้า Hadoop ด้วย Sqoop, ส่ง log จำลองเข้า HDFS ผ่าน Flume สองชั้น และส่งข้อความผ่าน Kafka

**วิธีอ่าน:** อ่านไฟล์ `03_data_ingestion_lecture.md` ก่อน (หัวข้อ Sqoop, Flume, Avro, Kafka) ทุกคำสั่งในไฟล์นี้มีตารางอธิบายทีละส่วน และมี "ผลที่คาดว่าจะได้" ผลที่ระบุว่าคาดว่าจะได้เป็นผลจากการวิเคราะห์คำสั่ง ไม่ได้รันบน VM จริง ยกเว้นสคริปต์สร้าง log ในปฏิบัติการที่ 2 ที่ทดสอบการทำงานแล้ว ถ้าผลบนเครื่องของคุณต่างจากที่คาด ให้ดูตารางข้อผิดพลาดที่พบบ่อยในหัวข้อ 4

**สภาพแวดล้อม:** Cloudera QuickStart VM ที่มี MySQL, Hadoop, Hive, HBase, Sqoop และ Flume ติดตั้งแล้ว ผู้ใช้ cloudera โฟลเดอร์ทำงาน /home/cloudera รหัสผ่านฐานข้อมูล root คือ cloudera ซอฟต์แวร์รุ่น Sqoop 1.4.x, Flume 1.x และ Kafka 0.9.0.1

**ข้อควรระวังเรื่องเครื่องหมาย:** ข้อความที่คัดลอกมาจากเอกสารมักมีเครื่องหมายอัญประกาศแบบโค้ง (‘ ’) และขีดยาว (–) ปนมา ต้องพิมพ์เป็นเครื่องหมายตรง (' และ -) เท่านั้น ไม่เช่นนั้นคำสั่งรันไม่ได้ คำสั่งในไฟล์นี้ใช้เครื่องหมายตรงทั้งหมด

---

## สารบัญ

1. ปฏิบัติการที่ 1: Sqoop จาก MySQL ไป HDFS, Hive และ HBase
2. ปฏิบัติการที่ 2: Flume รับข้อมูล Product Impression
3. ปฏิบัติการที่ 3: Kafka Producer และ Consumer
4. ข้อผิดพลาดที่พบบ่อยในปฏิบัติการ
5. โจทย์ฝึกจากปฏิบัติการ
6. รายการตรวจตัวเองหลังจบปฏิบัติการ
7. References

---

## 1. ปฏิบัติการที่ 1: Sqoop จาก MySQL ไป HDFS, Hive และ HBase

**เป้าหมาย:** สร้างฐานข้อมูล MySQL สองชุด นำข้อมูลเข้าตาราง แล้วใช้ Sqoop ย้ายข้อมูลไปยัง HDFS, Hive และ HBase

**แนวคิดที่ใช้:** Sqoop แบ่งงานด้วยคอลัมน์แบ่งงาน ตารางที่ไม่มี primary key ต้องใช้ -m 1 (Lecture หัวข้อ 3.2 และ 3.3)

### 1.1 ขั้นที่ 1: สร้างฐานข้อมูลและตารางใน MySQL

```
mysql -uroot -pcloudera
```

คำสั่งนี้เปิด MySQL client โดย -u ตามด้วยชื่อผู้ใช้ (root) และ -p ตามด้วยรหัสผ่าน (cloudera) โดยไม่เว้นวรรคระหว่างตัวเลือกกับค่า

```sql
create database energydata;
use energydata;
create table avgprice_by_state (
  year INT NOT NULL,
  state VARCHAR(5) NOT NULL,
  sector VARCHAR(255),
  residential DECIMAL(10,2),
  industrial DECIMAL(10,2),
  transportation DECIMAL(10,2),
  other DECIMAL(10,2),
  total DECIMAL(10,2)
);
quit;
```

| บรรทัด | ความหมาย |
|---|---|
| create database energydata | สร้างฐานข้อมูลชื่อ energydata |
| use energydata | เลือกฐานข้อมูลนี้เป็นฐานที่ทำงานอยู่ |
| create table avgprice_by_state (...) | สร้างตารางเก็บราคาไฟฟ้าเฉลี่ยรายรัฐ รายปี รายภาคส่วน |
| year INT NOT NULL | ปีเป็นจำนวนเต็ม ห้ามว่าง |
| state VARCHAR(5) NOT NULL | รหัสรัฐ ข้อความยาวไม่เกิน 5 ตัวอักษร ห้ามว่าง |
| sector VARCHAR(255) | ภาคส่วน ข้อความยาวไม่เกิน 255 ตัวอักษร ว่างได้ |
| DECIMAL(10,2) | เลขทศนิยมที่มีตัวเลขรวมไม่เกิน 10 หลัก โดย 2 หลักอยู่หลังจุดทศนิยม ใช้กับราคาแต่ละภาคส่วน |
| quit | ออกจาก MySQL client |

ตารางนี้ **ไม่มี primary key** ซึ่งมีผลต่อขั้นที่ 4

### 1.2 ขั้นที่ 2: เตรียมไฟล์ข้อมูล CSV

ขั้นถัดไปต้องมีไฟล์ /home/cloudera/avgprice_kwh_state.csv ที่มีบรรทัดแรกเป็นหัวคอลัมน์ ถ้าคุณมีชุดข้อมูลราคาไฟฟ้าเฉลี่ยรายรัฐตามรูปแบบนี้อยู่แล้ว ให้วางไว้ที่ตำแหน่งนี้ ถ้าไม่มี สร้างไฟล์ตัวอย่างขนาดเล็กด้วยคำสั่งด้านล่าง ตัวเลขในไฟล์ตัวอย่างเป็นข้อมูลสมมติเพื่อฝึกเท่านั้น ไม่ใช่สถิติจริง

```
cd /home/cloudera
cat > avgprice_kwh_state.csv <<'EOF'
year,state,sector,residential,industrial,transportation,other,total
2013,AL,Total Electric Industry,11.87,6.15,0.00,9.47,9.58
2013,AK,Total Electric Industry,17.52,14.65,0.00,15.20,16.11
2013,AZ,Total Electric Industry,11.76,6.52,0.00,8.10,10.04
2014,AL,Total Electric Industry,12.40,6.38,0.00,9.88,9.91
2014,AK,Total Electric Industry,17.93,14.20,0.00,15.77,16.35
2014,AZ,Total Electric Industry,12.04,6.77,0.00,8.41,10.31
2015,AL,Total Electric Industry,12.15,6.04,0.00,9.52,9.62
2015,AZ,Total Electric Industry,12.38,6.44,0.00,8.29,10.25
EOF
wc -l avgprice_kwh_state.csv
```

| ส่วนของคำสั่ง | ความหมาย |
|---|---|
| cd /home/cloudera | ไปที่โฟลเดอร์ทำงาน |
| cat > ไฟล์ <<'EOF' ... EOF | เขียนข้อความระหว่างสองบรรทัด EOF ลงไฟล์ (เครื่องหมายคำพูดรอบ EOF ป้องกันเชลล์แปลความหมายอักขระพิเศษในข้อความ) |
| wc -l | นับจำนวนบรรทัดของไฟล์ |

**ผลที่คาดว่าจะได้:** wc -l พิมพ์ 9 (บรรทัดหัว 1 บรรทัด และข้อมูล 8 บรรทัด) ถ้ารันกับชุดข้อมูลจริง จำนวนบรรทัดจะต่างออกไป

### 1.3 ขั้นที่ 3: โหลดไฟล์ CSV เข้าตาราง

```
mysql -h localhost -uroot -pcloudera --local-infile=1
```

-h localhost คือเชื่อมต่อเครื่องนี้ ส่วน --local-infile=1 เปิดสิทธิ์ให้ client อ่านไฟล์ในเครื่องแล้วส่งเข้าเซิร์ฟเวอร์ ถ้าไม่ใส่ คำสั่ง load data local จะถูกปฏิเสธ

```sql
use energydata;
load data local infile '/home/cloudera/avgprice_kwh_state.csv'
  into table avgprice_by_state
  fields terminated by ','
  lines terminated by '\n'
  ignore 1 lines;
select * from avgprice_by_state limit 5;
quit;
```

| ส่วนของคำสั่ง | ความหมาย |
|---|---|
| load data local infile '...' | โหลดข้อมูลจากไฟล์ในเครื่อง client |
| into table avgprice_by_state | ใส่ลงตารางนี้ |
| fields terminated by ',' | คอลัมน์คั่นด้วยจุลภาค |
| lines terminated by '\n' | แถวคั่นด้วยอักขระขึ้นบรรทัดใหม่ |
| ignore 1 lines | ข้ามบรรทัดแรก เพราะเป็นหัวคอลัมน์ของไฟล์ CSV |
| select ... limit 5 | ขั้นตรวจสอบเสริม ดูห้าแถวแรกเพื่อยืนยันว่าโหลดสำเร็จ |

**ผลที่คาดว่าจะได้ (กับไฟล์ตัวอย่างข้างบน):** MySQL รายงานว่าโหลด 8 แถว (Records: 8) และ select แสดง 5 แถวแรก ได้แก่ ปี 2013 AL, 2013 AK, 2013 AZ, 2014 AL, 2014 AK โดยปกติลำดับตรงกับลำดับในไฟล์ แต่ MySQL ไม่รับประกันลำดับเมื่อไม่มี order by

### 1.4 ขั้นที่ 4: Sqoop import ไป HDFS

```
sqoop import \
  --connect jdbc:mysql://localhost:3306/energydata \
  --username root --password cloudera \
  --table avgprice_by_state \
  --target-dir /user/cloudera/energydata \
  -m 1
```

| ตัวเลือก | ความหมาย |
|---|---|
| --connect jdbc:mysql://localhost:3306/energydata | ต่อ MySQL ที่เครื่องนี้ พอร์ต 3306 ฐานข้อมูล energydata |
| --username root --password cloudera | ผู้ใช้และรหัสผ่าน ใช้ได้กับ VM เรียน แต่ไม่ปลอดภัยในงานจริง (Lecture หัวข้อ 3.7) |
| --table avgprice_by_state | ตารางที่จะดึง |
| --target-dir /user/cloudera/energydata | โฟลเดอร์ปลายทางใน HDFS ต้องยังไม่มีอยู่ |
| -m 1 | ใช้ map task เดียว ได้ไฟล์เดียว และจำเป็นเพราะตารางไม่มี primary key |

ตรวจสอบผล:

```
hadoop fs -ls /user/cloudera/energydata
hadoop fs -cat /user/cloudera/energydata/part-m-00000
```

**ผลที่คาดว่าจะได้ (จากการวิเคราะห์ ไม่ได้รันจริง):** โฟลเดอร์มีไฟล์ part-m-00000 และมักมีไฟล์ตัวบอกความสำเร็จของงาน (_SUCCESS) ด้วย เนื้อหาเป็นข้อความหนึ่งแถวต่อหนึ่งบรรทัด แต่ละบรรทัดมี 8 ค่าคั่นด้วยจุลภาค ตามลำดับคอลัมน์ year, state, sector, residential, industrial, transportation, other, total เช่นบรรทัดแรกของไฟล์ตัวอย่างคาดว่าเป็น

```
2013,AL,Total Electric Industry,11.87,6.15,0.00,9.47,9.58
```

ขณะรัน Sqoop พิมพ์ log ของงาน MapReduce ตอนท้ายมักมีบรรทัดสรุปจำนวนแถวที่ดึงมา (Retrieved 8 records) ให้เทียบกับ `select count(*)` ใน MySQL ซึ่งควรเท่ากัน

**การทดลองเสริม (ยืนยันกฎ primary key):** รันคำสั่งเดิมโดยเปลี่ยน --target-dir เป็น /user/cloudera/energydata2 และใส่ `-m 2` แทน `-m 1` คาดว่าล้มเหลวด้วยข้อความที่บอกว่าไม่พบ primary key และให้ระบุ --split-by หรือใช้ mapper เดียว ซึ่งตรงกับกฎใน Lecture หัวข้อ 3.3 (ข้อความจริงขึ้นกับรุ่น)

### 1.5 ขั้นที่ 5: Sqoop import ไป Hive

```
sqoop import \
  --connect jdbc:mysql://localhost:3306/energydata \
  --username root --password cloudera \
  --table avgprice_by_state \
  --hive-table avgprice --hive-import \
  -m 1
```

ต่างจากขั้นที่ 4 ตรงที่ไม่มี --target-dir แต่มี --hive-import (นำข้อมูลเข้า Hive) และ --hive-table avgprice (ตั้งชื่อตารางใน Hive เป็น avgprice) Sqoop สร้างตารางใน Hive ให้เองโดยแปลงชนิดข้อมูลจาก MySQL (Lecture หัวข้อ 3.5)

ตรวจสอบผล:

```
hive
```

```sql
select * from avgprice limit 10;
```

**ผลที่คาดว่าจะได้:** แถวข้อมูลเดียวกับตารางใน MySQL (กับไฟล์ตัวอย่างคือ 8 แถว) ถ้ารัน `describe avgprice;` คาดว่าเห็นคอลัมน์ชื่อเดียวกับตาราง MySQL ทั้งแปดคอลัมน์

### 1.6 ขั้นที่ 6: เตรียมตารางสำหรับ HBase ใน MySQL

```
mysql -uroot -pcloudera
```

```sql
create database country_db;
use country_db;
create table country_tbl (
  id int not null,
  country varchar(50),
  primary key (id)
);
insert into country_tbl values (1, 'USA');
insert into country_tbl values (2, 'CANADA');
insert into country_tbl values (3, 'JAPAN');
insert into country_tbl values (4, 'ENGLAND');
insert into country_tbl values (5, 'THAILAND');
select * from country_tbl;
quit;
```

ตารางนี้มี primary key คือ id ซึ่ง Sqoop ใช้เป็น row key ของ HBase เมื่อไม่ระบุเอง[[1]](https://sqoop.apache.org/docs/1.4.6/SqoopUserGuide.html) select ควรแสดงห้าแถว (id 1 ถึง 5)

### 1.7 ขั้นที่ 7: Sqoop import ไป HBase

```
sqoop import \
  --connect jdbc:mysql://localhost:3306/country_db \
  --username root --password cloudera \
  --table country_tbl \
  --hbase-table country \
  --column-family country-cf \
  --hbase-row-key id \
  --hbase-create-table \
  -m 1
```

| ตัวเลือก | ความหมาย |
|---|---|
| --hbase-table country | เขียนลงตาราง HBase ชื่อ country แทนการเขียนเป็นไฟล์ใน HDFS |
| --column-family country-cf | คอลัมน์ที่เหลือทั้งหมดใส่ใน column family ชื่อ country-cf |
| --hbase-row-key id | ใช้คอลัมน์ id เป็น row key |
| --hbase-create-table | สร้างตารางและ column family ให้ถ้ายังไม่มี ไม่เช่นนั้นงานล้มเหลว |

ตรวจสอบผล:

```
hbase shell
```

```
scan 'country'
```

**ผลที่คาดว่าจะได้ (จากการวิเคราะห์):** ห้าแถว row key เป็น 1 ถึง 5 แต่ละแถวมีเซลล์เดียวชื่อ country-cf:country ค่าเป็น USA, CANADA, JAPAN, ENGLAND, THAILAND ตามลำดับ รูปแบบบรรทัดผลลัพธ์ (timestamp ต่างกันตามเวลาที่รัน):

```
ROW        COLUMN+CELL
 1         column=country-cf:country, timestamp=..., value=USA
 2         column=country-cf:country, timestamp=..., value=CANADA
 ...
5 row(s) in ... seconds
```

ไม่มีคอลัมน์ id แยกต่างหาก เพราะค่าเริ่มต้นของ Sqoop ไม่เก็บคอลัมน์ที่ใช้เป็น row key ซ้ำในข้อมูลของแถว[[1]](https://sqoop.apache.org/docs/1.4.6/SqoopUserGuide.html) ออกจาก shell ด้วย `exit`

---
## 2. ปฏิบัติการที่ 2: Flume รับข้อมูล Product Impression

**เป้าหมาย:** จำลอง log การเข้าชมสินค้าของร้านค้าออนไลน์ แล้วใช้ Flume สองชั้น (client agent และ collector agent) ส่งเข้า HDFS

**โฟลว์ที่จะสร้าง:** ไฟล์ /tmp/impressions/impressions.log, client agent (spooldir source, file channel, Avro sink), collector agent (Avro source, file channel, HDFS sink) แล้วโฟลเดอร์ /user/cloudera/impressions ใน HDFS แผนภาพและตัวอย่างการเดินทางของ event อยู่ใน Lecture หัวข้อ 4.6

### 2.1 ขั้นที่ 1: สร้างโฟลเดอร์ที่จำเป็นด้วยสคริปต์

สร้างไฟล์ flume_setup.sh ใน /home/cloudera ด้วยโปรแกรมแก้ไขข้อความ เช่น nano ให้มีเนื้อหาดังนี้

```
#!/bin/bash
hadoop fs -mkdir -p /user/cloudera/impressions/
hadoop fs -chmod 777 /user/cloudera/impressions/
mkdir /tmp/impressions
chmod 777 /tmp/impressions
mkdir /tmp/flume
chmod 777 /tmp/flume
```

| บรรทัด | ความหมาย |
|---|---|
| #!/bin/bash | บอกว่าสคริปต์นี้รันด้วย bash |
| hadoop fs -mkdir -p /user/cloudera/impressions/ | สร้างโฟลเดอร์ปลายทางใน HDFS (-p สร้างโฟลเดอร์แม่ให้ด้วยถ้ายังไม่มี และไม่ error ถ้ามีอยู่แล้ว) |
| hadoop fs -chmod 777 ... | ให้ทุกคนอ่านเขียนได้ เพื่อให้ Flume เขียนได้ไม่ว่าจะรันเป็นผู้ใช้ใด |
| mkdir /tmp/impressions | โฟลเดอร์ในเครื่องที่โปรแกรมจำลองเขียน log และที่ spooldir source เฝ้าดู |
| mkdir /tmp/flume | โฟลเดอร์ที่ file channel ของ collector ใช้เก็บ checkpoint และข้อมูล |
| chmod 777 ... | เปิดสิทธิ์ให้เขียนได้ |

บางที่ใช้ chmod 1777 แทน 777 เลข 1 นำหน้าคือ sticky bit ที่ทำให้ผู้ใช้ลบได้เฉพาะไฟล์ของตนเองในโฟลเดอร์ที่ทุกคนเขียนได้ ทั้งสองแบบใช้ในปฏิบัติการนี้ได้

รันสคริปต์ด้วยสิทธิ์ผู้ดูแล:

```
sudo su -
cd /home/cloudera
sh flume_setup.sh
```

sudo su - สลับเป็นผู้ใช้ root ด้วย environment ของ root ส่วน cd ต้องกลับมาที่โฟลเดอร์ที่มีสคริปต์ ข้อควรระวัง: บนบางเครื่อง ผู้ใช้ root อาจไม่มีสิทธิ์สร้างโฟลเดอร์ใต้ /user/cloudera ใน HDFS ถ้าเห็นข้อความ Permission denied ให้ออกจาก root (พิมพ์ exit) แล้วรันสองบรรทัดแรกของสคริปต์ (hadoop fs -mkdir และ -chmod) ในฐานะผู้ใช้ cloudera ข้อนี้ยังไม่ได้ยืนยันบนเครื่องจริง

**ผลที่คาดว่าจะได้:** `hadoop fs -ls /user/cloudera` เห็นโฟลเดอร์ impressions และ `ls -ld /tmp/impressions /tmp/flume` เห็นสิทธิ์ drwxrwxrwx

### 2.2 ขั้นที่ 2: สร้าง log จำลอง

สร้างไฟล์ impression_tracker.py ใน /home/cloudera ด้วย nano แล้ววางเนื้อหาด้านล่าง สคริปต์นี้เขียนเป็นอักขระ ASCII ล้วน ใช้ได้ทั้ง Python 2 (รุ่นที่มากับ VM) และ Python 3

```python
#!/usr/bin/env python
# Generate simulated product-impression events: one JSON object per line.
# Works with Python 2 and Python 3.
from __future__ import print_function
import json
import random
import time

OUT_FILE = "/tmp/impressions/impressions.log"
NUM_EVENTS = 500
ACTIONS = ["view", "click", "add_cart", "remove_cart", "purchase"]

def make_ip():
    return ".".join(str(random.randint(1, 254)) for _ in range(4))

# 10 simulated customers: a 5-digit id and a fixed ip each
customers = [{"cid": str(random.randint(10000, 99999)), "ip": make_ip()}
             for _ in range(10)]
# 30 simulated products, sku format Tdddd-d
skus = ["T%d-%d" % (random.randint(1000, 9999), random.randint(1, 9))
        for _ in range(30)]

with open(OUT_FILE, "a") as f:
    for _ in range(NUM_EVENTS):
        c = random.choice(customers)
        event = {
            "sku": random.choice(skus),
            "timestamp": int(time.time() * 1000),
            "cid": c["cid"],
            "action": random.choice(ACTIONS),
            "ip": c["ip"],
        }
        line = json.dumps(event)
        print(line)
        f.write(line + "\n")
```

| ส่วนของโปรแกรม | ความหมาย |
|---|---|
| #!/usr/bin/env python | บรรทัดแรกบอกระบบว่าไฟล์นี้รันด้วย python จึงรันตรงๆ ด้วย ./ ได้หลัง chmod +x |
| from __future__ import print_function | ให้ print ทำงานแบบเดียวกันทั้ง Python 2 และ 3 |
| customers | ลูกค้าจำลอง 10 ราย แต่ละรายมี cid เลข 5 หลัก และ ip ประจำตัว |
| skus | รหัสสินค้าจำลอง 30 รายการ รูปแบบเช่น T9921-5 |
| random.choice(ACTIONS) | สุ่ม action จาก view, click, add_cart, remove_cart, purchase |
| time.time() * 1000 | เวลาปัจจุบันเป็นมิลลิวินาทีจาก epoch |
| open(OUT_FILE, "a") | เปิดไฟล์แบบต่อท้าย (append) |
| json.dumps(event) | แปลง dictionary เป็นข้อความ JSON หนึ่งบรรทัด |

โปรแกรมสร้าง event 500 ตัว เขียนทั้งลงหน้าจอและลงไฟล์ /tmp/impressions/impressions.log แล้วจบการทำงาน จากนั้นให้สิทธิ์รันและรัน

```
chmod +x impression_tracker.py
./impression_tracker.py
wc -l /tmp/impressions/impressions.log
```

**ผลที่ได้จากการทดสอบสคริปต์นี้ (กับพาธทดสอบ):** หน้าจอแสดง JSON 500 บรรทัด ตัวอย่างหนึ่งบรรทัด (ค่าต่างกันทุกครั้งเพราะสุ่ม)

```
{"sku": "T5415-1", "timestamp": 1790914444294, "cid": "53975", "action": "remove_cart", "ip": "143.5.46.178"}
```

`wc -l` รายงาน 500 สำหรับการรันครั้งแรก แต่ละบรรทัดยาว 101 ถึง 112 ตัวอักษร ข้อควรระวัง: โปรแกรมเปิดไฟล์แบบต่อท้าย ถ้ารันซ้ำโดยที่ไฟล์เดิมยังอยู่ จะได้ 1000 บรรทัด และต้องไม่รันขณะ Flume กำลังเฝ้าโฟลเดอร์นี้ เพราะ spooldir source จะหยุดเมื่อไฟล์ถูกแก้ไขหลังวางลงโฟลเดอร์ (Lecture หัวข้อ 4.3) ถ้าต้องการสร้างใหม่ ให้ลบไฟล์เดิมก่อน

### 2.3 ขั้นที่ 3: ไฟล์ตั้งค่า agent

สร้าง client.conf และ collector.conf ใน /home/cloudera ด้วย nano ให้มีเนื้อหาดังนี้

**client.conf (agent ชื่อ client)**

```
# define spooling directory source:
client.sources=r1
client.sources.r1.channels=ch1
client.sources.r1.type=spooldir
client.sources.r1.spoolDir=/tmp/impressions

# define a file channel:
client.channels=ch1
client.channels.ch1.type=FILE

# define an Avro sink:
client.sinks=k1
client.sinks.k1.type=avro
client.sinks.k1.hostname=localhost
client.sinks.k1.port=4141
client.sinks.k1.channel=ch1
```

| บรรทัด | ความหมาย |
|---|---|
| client.sources=r1 | agent ชื่อ client มี source หนึ่งตัวชื่อ r1 |
| client.sources.r1.channels=ch1 | source r1 เขียน event ลง channel ch1 (channels พหูพจน์) |
| client.sources.r1.type=spooldir | source ชนิด spooling directory |
| client.sources.r1.spoolDir=/tmp/impressions | โฟลเดอร์ที่เฝ้าดูไฟล์ใหม่ |
| client.channels.ch1.type=FILE | channel ชนิดเก็บลงไฟล์บนดิสก์ (ทนต่อการล่ม) ไม่ได้กำหนดโฟลเดอร์จึงใช้ค่าเริ่มต้นของ Flume |
| client.sinks.k1.type=avro | sink ชนิด Avro ส่งต่อให้ agent อื่นด้วย Avro RPC |
| client.sinks.k1.hostname=localhost และ port=4141 | ปลายทางคือ collector ที่เครื่องนี้ พอร์ต 4141 ในงานจริงเป็นชื่อเครื่องของ collector |
| client.sinks.k1.channel=ch1 | sink k1 อ่านจาก channel ch1 (channel เอกพจน์) |

**collector.conf (agent ชื่อ collector)**

```
# define an Avro source:
collector.sources=r1
collector.sources.r1.type=avro
collector.sources.r1.bind=0.0.0.0
collector.sources.r1.port=4141
collector.sources.r1.channels=ch1

# define a file channel using multiple disks for reliability
collector.channels=ch1
collector.channels.ch1.type=FILE
collector.channels.ch1.checkpointDir=/tmp/flume/checkpoint
collector.channels.ch1.dataDir=/tmp/flume/data

# define HDFS sinks to persist events as text
collector.sinks=k1
collector.sinks.k1.type=hdfs
collector.sinks.k1.channel=ch1

# HDFS sink configuration
collector.sinks.k1.hdfs.path=/user/cloudera/impressions
collector.sinks.k1.hdfs.filePrefix=impressions
collector.sinks.k1.hdfs.fileSuffix=.log
collector.sinks.k1.hdfs.fileType=DataStream
collector.sinks.k1.hdfs.writeFormat=text
collector.sinks.k1.hdfs.batchSize=1000
```

| บรรทัด | ความหมาย |
|---|---|
| collector.sources.r1.type=avro | รับ event ผ่าน Avro RPC |
| bind=0.0.0.0 และ port=4141 | ฟังที่ทุกการ์ดเครือข่ายของเครื่อง พอร์ต 4141 ต้องตรงกับ port ของ Avro sink ของ client |
| checkpointDir และ dataDir | ตำแหน่งบนดิสก์ที่ file channel เก็บจุดตรวจสอบและข้อมูล event ตรงกับโฟลเดอร์ /tmp/flume ที่สร้างในขั้นที่ 1 |
| hdfs.path | โฟลเดอร์ปลายทางใน HDFS |
| hdfs.filePrefix และ hdfs.fileSuffix | ส่วนหน้าและส่วนท้ายของชื่อไฟล์ผลลัพธ์ |
| hdfs.fileType=DataStream และ hdfs.writeFormat=text | เขียนเป็นไฟล์ข้อความธรรมดา (ค่าเริ่มต้นของ HDFS sink เป็น SequenceFile แบบไบนารี ซึ่ง cat แล้วอ่านไม่ออก) |
| hdfs.batchSize=1000 | จำนวน event ต่อหนึ่งชุดที่เขียนลง HDFS ต้องไม่เกินความจุธุรกรรมของ channel[[2]](https://flume.apache.org/releases/content/1.9.0/FlumeUserGuide.html) |

ไฟล์นี้ไม่ได้กำหนด hdfs.rollInterval, hdfs.rollSize และ hdfs.rollCount จึงใช้ค่าเริ่มต้น (30 วินาที, 1024 ไบต์, 10 event) ซึ่งมีผลต่อจำนวนไฟล์ในขั้นที่ 5

### 2.4 ขั้นที่ 4: รัน Flume

เปิดเทอร์มินัลที่ 1 สำหรับ collector

```
sudo su -
cd /home/cloudera
flume-ng agent --name collector --conf . --conf-file ./collector.conf -Dflume.root.logger=INFO,console
```

| ส่วนของคำสั่ง | ความหมาย |
|---|---|
| flume-ng agent | สตาร์ต Flume agent |
| --name collector | รัน agent ชื่อ collector ต้องตรงกับคำนำหน้าในไฟล์ (Lecture หัวข้อ 4.7) |
| --conf . | ใช้โฟลเดอร์ปัจจุบันเป็นโฟลเดอร์ config (สำหรับ flume-env.sh และ log4j) |
| --conf-file ./collector.conf | ไฟล์ตั้งค่าของ agent |
| -Dflume.root.logger=INFO,console | ตัวเลือกเสริมตามคู่มือ Flume แสดง log ระดับ INFO บนหน้าจอเพื่อเห็นว่า agent ทำงาน[[2]](https://flume.apache.org/releases/content/1.9.0/FlumeUserGuide.html) |

คำสั่งนี้ทำงานเบื้องหน้าและไม่คืนพรอมต์ ให้เปิดเทอร์มินัลนี้ทิ้งไว้ ไม่จำเป็นต้องสตาร์ตบริการ flume-ng-agent ที่ติดมากับเครื่อง เพราะเราสตาร์ต agent ของเราเองด้วยคำสั่งข้างบน

**ควรรัน collector ก่อน client** เพื่อให้ Avro source เปิดพอร์ต 4141 รอไว้ก่อนที่ Avro sink จะมาเชื่อม

เปิดเทอร์มินัลที่ 2 สำหรับ client

```
sudo su -
cd /home/cloudera
flume-ng agent --name client --conf . --conf-file ./client.conf -Dflume.root.logger=INFO,console
```

เทอร์มินัลนี้รัน agent ชื่อ client เพราะเป็นตัวที่อ่านโฟลเดอร์ /tmp/impressions แล้วส่งต่อ

**ผลที่คาดว่าจะได้:** log ของ collector แสดงว่า Avro source เริ่มทำงานและฟังที่พอร์ต 4141 และ log ของ client แสดงว่า Avro sink เชื่อมต่อได้ เมื่อ spooldir source อ่านไฟล์ครบ ไฟล์ /tmp/impressions/impressions.log ถูกเปลี่ยนชื่อเป็น impressions.log.COMPLETED (ข้อความ log จริงขึ้นกับรุ่น)

### 2.5 ขั้นที่ 5: ตรวจสอบผลใน HDFS

รอประมาณครึ่งนาทีให้ HDFS sink ปิดไฟล์ที่ยังเขียนอยู่ (Lecture หัวข้อ 4.8) แล้วเปิดเทอร์มินัลที่ 3

```
hadoop fs -ls /user/cloudera/impressions
hadoop fs -cat /user/cloudera/impressions/impressions.NNNN.log
hadoop fs -cat '/user/cloudera/impressions/*.log' | wc -l
ls /tmp/impressions
```

NNNN แทนตัวเลขในชื่อไฟล์จริงที่เห็นจากคำสั่ง -ls ให้แทนที่ด้วยชื่อจริง เครื่องหมายคำพูดรอบ */*.log ทำให้ hadoop เป็นผู้ขยาย wildcard ไม่ใช่เชลล์

**ผลที่คาดว่าจะได้ (จากการวิเคราะห์ ไม่ได้รันจริง):**

- `-ls` แสดงไฟล์จำนวนมาก (คาดว่าราว 50 ไฟล์ เพราะค่าเริ่มต้นปิดไฟล์ทุก 10 event และมี 500 event ดู Lecture หัวข้อ 4.8) ชื่อขึ้นต้น impressions. และลงท้าย .log ไฟล์ที่ยังเขียนอยู่มีนามสกุลชั่วคราว เช่น .tmp ต่อท้าย
- `-cat` ไฟล์เดียวแสดง JSON ประมาณ 10 บรรทัด หนึ่งบรรทัดต่อหนึ่ง event
- ผลรวมจำนวนบรรทัดทุกไฟล์ที่ปิดแล้วควรเป็น 500 (สำหรับการรัน generator หนึ่งครั้ง) ถ้าได้น้อยกว่า อาจเป็นเพราะไฟล์สุดท้ายยังไม่ถูกปิด ให้รอหรือกด Ctrl+C หยุด agent อย่างเรียบร้อยแล้วนับใหม่
- ในโฟลเดอร์ /tmp/impressions ไฟล์ impressions.log ถูกเปลี่ยนชื่อเป็น impressions.log.COMPLETED ซึ่งเป็นสัญญาณว่า spooldir source อ่านครบแล้ว

เมื่อตรวจเสร็จ กด Ctrl+C ที่เทอร์มินัลของ client และ collector เพื่อหยุด agent

**การทดลองเสริม: ดูความน่าเชื่อถือด้วยตา** ลบไฟล์ใน HDFS ออก ลบไฟล์ .COMPLETED เก่า แล้วสร้าง log ใหม่ด้วยชื่อไม่ซ้ำ จากนั้นรันเฉพาะ client โดยยังไม่รัน collector และดู log ของ client คาดว่าเชื่อมต่อ collector ไม่ได้ และ event ค้างใน file channel บนดิสก์ (โฟลเดอร์ข้อมูลของ file channel ที่ไม่ได้กำหนดเองมักอยู่ใต้โฮมของผู้ใช้ที่รัน agent ตรวจสอบตามรุ่นที่ใช้) จากนั้นสตาร์ต collector คาดว่า event ที่ค้างถูกส่งต่อจนครบ ซึ่งตรงกับหลักการใน Lecture หัวข้อ 4.5

---

## 3. ปฏิบัติการที่ 3: Kafka Producer และ Consumer

**เป้าหมาย:** ติดตั้ง Kafka รุ่น 0.9.0.1 รัน broker หนึ่งตัว ส่งข้อความด้วย console producer และอ่านด้วย console consumer

**แนวคิดที่ใช้:** topic, partition, offset, consumer group (Lecture หัวข้อ 6)

### 3.1 ขั้นที่ 1: ติดตั้ง

```
sudo su -
cd /home/cloudera
mkdir kafka
cd kafka
wget https://archive.apache.org/dist/kafka/0.9.0.1/kafka_2.10-0.9.0.1.tgz
tar xzf kafka_2.10-0.9.0.1.tgz
```

| บรรทัด | ความหมาย |
|---|---|
| mkdir kafka และ cd kafka | สร้างและเข้าโฟลเดอร์ติดตั้ง |
| wget URL | ดาวน์โหลดไฟล์บีบอัดจากคลังเก็บรุ่นเก่าของ Apache ถ้าลิงก์ใช้ไม่ได้ ให้หาไฟล์ชื่อเดียวกันในคลัง archive.apache.org/dist/kafka/ |
| tar xzf ... | x = แตกไฟล์, z = ไฟล์ถูกบีบอัดแบบ gzip, f = ระบุชื่อไฟล์ |

ชื่อไฟล์ kafka_2.10-0.9.0.1 อ่านว่า Kafka รุ่น 0.9.0.1 ที่คอมไพล์ด้วย Scala 2.10 ผลที่ได้คือโฟลเดอร์ /home/cloudera/kafka/kafka_2.10-0.9.0.1 ที่มีโฟลเดอร์ bin และ config (ลิงก์ดาวน์โหลดข้างบนยังไม่ได้ตรวจว่าใช้งานได้)

### 3.2 ขั้นที่ 2: สตาร์ต broker

เปิดเทอร์มินัลใหม่

```
sudo su -
cd /home/cloudera/kafka/kafka_2.10-0.9.0.1
bin/kafka-server-start.sh config/server.properties &
```

สคริปต์อ่านไฟล์ config/server.properties (รหัส broker พอร์ตที่ฟัง และที่อยู่ ZooKeeper) เครื่องหมาย & ให้งานทำงานเบื้องหลัง ข้อควรระวัง: broker ของ Kafka รุ่นนี้ต้องเชื่อม ZooKeeper (ค่าตั้งต้นในไฟล์ตัวอย่างชี้ไปที่ localhost:2181) ขั้นตอนในบทนี้ไม่ได้สตาร์ต ZooKeeper เพราะสมมติว่า ZooKeeper ทำงานอยู่แล้วบน VM ถ้า broker ขึ้นข้อความว่าเชื่อม ZooKeeper ไม่ได้ ให้สตาร์ต ZooKeeper ที่มากับ Kafka ก่อนด้วย `bin/zookeeper-server-start.sh config/zookeeper.properties &` (ตรวจสอบตามรุ่นที่ใช้)

### 3.3 ขั้นที่ 3 (ทางเลือก): สร้างและตรวจ topic

บทนี้ไม่ต้องสร้าง topic ล่วงหน้า เพราะ broker รุ่นนี้สร้าง topic ให้อัตโนมัติเมื่อมีการเขียนครั้งแรก (ขึ้นกับค่าตั้ง auto.create.topics.enable ตรวจสอบตามรุ่นที่ใช้) แต่ถ้าต้องการกำหนดจำนวน partition เอง หรือดูโครงสร้าง topic ใช้คำสั่งต่อไปนี้ (เทอร์มินัลใหม่ ในโฟลเดอร์ Kafka)

```
bin/kafka-topics.sh --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic test
bin/kafka-topics.sh --describe --zookeeper localhost:2181 --topic test
```

| ตัวเลือก | ความหมาย |
|---|---|
| --create | สร้าง topic |
| --replication-factor 1 | มีสำเนาข้อมูลชุดเดียว (broker มีตัวเดียว จึงตั้งได้สูงสุด 1) |
| --partitions 1 | topic มี partition เดียว |
| --describe | แสดงโครงสร้าง topic |

**ผลที่คาดว่าจะได้ (จากการวิเคราะห์):** คำสั่ง describe แสดงจำนวน partition (1) replication factor (1) และบรรทัดของ partition 0 ที่ระบุ leader และ replicas เป็นรหัส broker เดียวกัน ซึ่งเชื่อมกับ Lecture หัวข้อ 6.7 ว่า leader คือ broker ที่รับผิดชอบ partition นั้น

### 3.4 ขั้นที่ 4: รัน producer

เปิดเทอร์มินัลใหม่

```
sudo su -
cd /home/cloudera/kafka/kafka_2.10-0.9.0.1
bin/kafka-console-producer.sh --topic test --broker-list localhost:9092
```

| ตัวเลือก | ความหมาย |
|---|---|
| --topic test | เขียนไปที่ topic ชื่อ test |
| --broker-list localhost:9092 | ที่อยู่ broker ที่จะต่อ (พอร์ต 9092 เป็นพอร์ตมาตรฐาน) |

พิมพ์ข้อความสองบรรทัด กด Enter ท้ายแต่ละบรรทัด (ทุกบรรทัดคือหนึ่ง record)

```
This is a test.
Bye, Kafka.
```

แล้วกด Ctrl+D เพื่อจบการส่ง (Ctrl+D ปิด standard input ของโปรแกรม) ถ้าไม่ได้สร้าง topic ไว้ก่อน และ broker สร้างให้อัตโนมัติ producer อาจแสดงคำเตือนครั้งแรกเรื่องไม่พบ leader ของ topic ก่อนส่งสำเร็จ

### 3.5 ขั้นที่ 5: รัน consumer

เปิดเทอร์มินัลใหม่

```
sudo su -
cd /home/cloudera/kafka/kafka_2.10-0.9.0.1
bin/kafka-console-consumer.sh --topic test --zookeeper localhost:2181 --from-beginning
```

| ตัวเลือก | ความหมาย |
|---|---|
| --topic test | อ่านจาก topic ชื่อ test |
| --zookeeper localhost:2181 | consumer แบบเก่าของรุ่นนี้ค้นหาข้อมูลผ่าน ZooKeeper |
| --from-beginning | เริ่มอ่านจาก offset แรกสุดของ topic แทนที่จะอ่านเฉพาะข้อความใหม่ที่เข้ามาหลังจากเริ่มรัน |

**ผลที่คาดว่าจะได้:** consumer พิมพ์สองบรรทัดที่ส่งไว้ คือ This is a test. และ Bye, Kafka. แล้วรอข้อความใหม่ต่อ กด Ctrl+C เพื่อออก

**ข้อสังเกตเรื่องรุ่น:** Kafka รุ่นใหม่ปรับตัวเลือกของ console tool เป็น --bootstrap-server localhost:9092 ทั้งฝั่ง producer และ consumer และ consumer ไม่ใช้ --zookeeper แล้ว คำสั่งในปฏิบัติการนี้ใช้ได้กับรุ่น 0.9.0.1 (ตรวจสอบตามรุ่นที่ใช้)

### 3.6 การทดลองเสริม: เชื่อมกับ offset และ consumer group

1. **ผู้อ่านหลายคนอ่านอิสระ:** ขณะที่ consumer ตัวแรกเปิดค้าง ให้ส่งข้อความเพิ่มจาก producer คาดว่าเห็นข้อความใหม่ปรากฏทันที เปิด consumer ตัวที่สองด้วย --from-beginning คาดว่าเห็นข้อความครบทุกบรรทัด เพราะ console consumer แต่ละตัวที่ไม่ระบุกลุ่มได้ชื่อกลุ่มที่สร้างขึ้นเองต่างกัน ต่างกลุ่มจึงได้สำเนาทุก record (Lecture หัวข้อ 6.6)
2. **กลุ่มเดียวกัน partition เดียว:** เปิด consumer สองตัวพร้อมกันโดยระบุกลุ่มเดียวกัน (เพิ่ม `--group g1` ถ้ารุ่นนี้รองรับตัวเลือกนี้ ตรวจสอบตามรุ่นที่ใช้) กับ topic ที่มี partition เดียว แล้วส่งข้อความ คาดว่าข้อความไปที่ consumer เพียงตัวเดียว อีกตัวว่างงาน เพราะหนึ่ง partition มี consumer ได้ตัวเดียวต่อกลุ่ม ลองสร้าง topic ใหม่ที่มี 2 partition ด้วย --partitions 2 แล้วทำซ้ำ คาดว่าทั้งสองตัวได้งาน (การกระจายข้อความระหว่าง partition ขึ้นกับวิธีที่ producer รุ่นนี้เลือก partition ผลที่เห็นอาจไม่เท่ากัน)

---

## 4. ข้อผิดพลาดที่พบบ่อยในปฏิบัติการ

| อาการ | สาเหตุที่เป็นไปได้ | วิธีแก้ |
|---|---|---|
| คำสั่ง mysql หรือ sqoop รายงาน syntax error แปลกๆ | เครื่องหมายอัญประกาศโค้งหรือขีดยาวที่ติดมาจากการคัดลอก | พิมพ์เครื่องหมายตรง ' และ - ใหม่ |
| load data local ถูกปฏิเสธ | เปิด MySQL client โดยไม่ใส่ --local-infile=1 หรือเซิร์ฟเวอร์ปิดการใช้ local infile | ออกแล้วเข้าใหม่พร้อมตัวเลือกนี้ ถ้ายังไม่ได้ ตรวจค่า local_infile ของเซิร์ฟเวอร์ (ตรวจสอบตามรุ่นที่ใช้) |
| Sqoop ล้มเหลวแจ้งว่าตารางไม่มี primary key | ใช้ map task มากกว่า 1 กับตารางที่ไม่มี primary key | ใส่ -m 1 หรือ --split-by คอลัมน์ |
| Sqoop แจ้งว่า output directory มีอยู่แล้ว | โฟลเดอร์ --target-dir มีจากการรันครั้งก่อน | ลบด้วย hadoop fs -rm -r โฟลเดอร์นั้น หรือใส่ --delete-target-dir[[1]](https://sqoop.apache.org/docs/1.4.6/SqoopUserGuide.html) |
| Sqoop import เข้า HBase ล้มเหลว | ตารางหรือ column family ยังไม่มี หรือ HBase ยังไม่ทำงาน | ใส่ --hbase-create-table หรือสร้างตารางใน HBase ก่อน และตรวจว่า HBase ทำงาน |
| Hive ค้นค่า NULL ไม่ถูก | Sqoop เขียน NULL เป็นสตริง null แต่ Hive ใช้ \N | ใส่ --null-string และ --null-non-string[[1]](https://sqoop.apache.org/docs/1.4.6/SqoopUserGuide.html) |
| Flume แจ้งไม่พบการตั้งค่าของ agent | ค่า --name ไม่ตรงกับคำนำหน้าในไฟล์ (รวมถึงตัวพิมพ์ใหญ่เล็ก) หรือชี้ไฟล์ผิด | แก้ให้ตรง ตรวจ --conf-file |
| Avro sink ของ client ต่อ collector ไม่ติด | ยังไม่ได้รัน collector หรือพอร์ตไม่ตรง หรือพิมพ์คำนำหน้าผิด (เช่น clinet) | รัน collector ก่อน ตรวจ port 4141 ทั้งสองไฟล์ ตรวจว่าทุกบรรทัดของ client.conf ขึ้นต้นด้วย client. |
| Flume spooldir หยุดและแจ้งข้อผิดพลาดใน log | ไฟล์ถูกแก้ไขหลังวางในโฟลเดอร์ หรือชื่อไฟล์ซ้ำกับไฟล์ที่เคยประมวลผลแล้ว[[2]](https://flume.apache.org/releases/content/1.9.0/FlumeUserGuide.html) | ใช้ชื่อไฟล์ไม่ซ้ำ อย่าแก้ไขไฟล์หลังวาง ลบไฟล์ .COMPLETED เก่าก่อนรันซ้ำ |
| ไฟล์ใน HDFS มีนามสกุล .tmp หรือจำนวนบรรทัดไม่ครบ | HDFS sink ยังไม่ปิดไฟล์ | รอให้ครบเงื่อนไข roll หรือหยุด agent อย่างเรียบร้อย |
| ไฟล์ใน HDFS มีจำนวนมากและเล็ก | ค่า roll เริ่มต้น (30 วินาที, 1024 ไบต์, 10 event) | เป็นพฤติกรรมปกติ ถ้าต้องการไฟล์ใหญ่ขึ้น ตั้ง hdfs.rollCount, hdfs.rollSize, hdfs.rollInterval เอง |
| hadoop fs -cat แสดงอักขระอ่านไม่ออก | ไม่ได้ตั้ง fileType=DataStream และ writeFormat=text | แก้ collector.conf แล้วรันใหม่ |
| Permission denied ตอนเขียน HDFS | ผู้ใช้ที่รัน (เช่น root) ไม่มีสิทธิ์ในโฟลเดอร์ปลายทาง | รันเป็นผู้ใช้ที่มีสิทธิ์ หรือตั้ง chmod ของโฟลเดอร์ปลายทาง |
| Kafka broker สตาร์ตไม่ขึ้นหรือเชื่อม ZooKeeper ไม่ได้ | ZooKeeper ยังไม่ทำงาน | สตาร์ต ZooKeeper ก่อน (หัวข้อ 3.2) |
| Kafka console tool แจ้งว่า option ไม่รู้จัก | ใช้ตัวเลือกของรุ่นเก่ากับ Kafka รุ่นใหม่ หรือกลับกัน | ใช้ตัวเลือกให้ตรงรุ่น (หัวข้อ 3.5) |
| Consumer ไม่เห็นข้อความเก่าของ topic | ไม่ได้ใส่ --from-beginning | ใส่ตัวเลือกนี้ |

---

## 5. โจทย์ฝึกจากปฏิบัติการ

### โจทย์ L1 (ทำนายผล): Sqoop กับไฟล์ตัวอย่าง

ใช้ตาราง avgprice_by_state ที่โหลดไฟล์ตัวอย่าง 8 แถวในหัวข้อ 1.3 แล้ว (ก) คำสั่งในหัวข้อ 1.4 ได้ไฟล์ปลายทางกี่ไฟล์ ชื่ออะไร กี่บรรทัด (ข) ถ้าเปลี่ยนเป็น `-m 2` โดยไม่เพิ่มตัวเลือกอื่นเกิดอะไรขึ้น เพราะอะไร (ค) ถ้ารันคำสั่งในหัวข้อ 1.4 ซ้ำอีกครั้งทันที เกิดอะไรขึ้น

**แนวตอบ:** (ก) ไฟล์ข้อมูลหนึ่งไฟล์ part-m-00000 มี 8 บรรทัด (บวกไฟล์ _SUCCESS ที่ไม่มีข้อมูล) เพราะ -m 1 ใช้ task เดียว (ข) ล้มเหลว เพราะตารางไม่มี primary key และไม่ได้ระบุ --split-by ทำให้แบ่งงานเป็นสอง task ไม่ได้ (ค) ล้มเหลว เพราะ --target-dir /user/cloudera/energydata มีอยู่แล้วจากรอบแรก และ Sqoop ไม่เขียนทับ ต้องลบโฟลเดอร์หรือใส่ --delete-target-dir

**เกณฑ์คะแนน (6 คะแนน):** (ก) 2 (ข) 2 (ค) 2

### โจทย์ L2 (วินิจฉัย): ผ่านไป 2 นาทีแล้วไม่มีไฟล์ใน HDFS

ผู้เรียนรัน collector และ client ตามหัวข้อ 2.4 แล้ว ผ่านไป 2 นาที `hadoop fs -ls /user/cloudera/impressions` ไม่แสดงไฟล์ใดเลย และ /tmp/impressions ยังมี impressions.log ชื่อเดิม จงเรียงลำดับสิ่งที่ควรตรวจ พร้อมเหตุผล

**แนวตอบ:**

1. ดู log บนหน้าจอของ client ว่ามีข้อผิดพลาดเรื่องการตั้งค่าหรือไม่ ไฟล์ยังชื่อเดิมแสดงว่า spooldir source ยังไม่เริ่มอ่านหรือหยุดไปก่อน
2. ตรวจว่ารัน client ด้วย --name client (ไม่ใช่ collector) และ --conf-file ชี้ client.conf เพราะถ้าชื่อไม่ตรงคำนำหน้า agent ไม่พบการตั้งค่า
3. ตรวจ spoolDir ใน client.conf ว่าเป็น /tmp/impressions ตรงกับที่ generator เขียน
4. ตรวจว่าไฟล์ไม่ถูกแก้ไขหลังวาง (เช่นรัน generator ซ้ำขณะ Flume ทำงาน) หรือมี .COMPLETED ชื่อเดียวกันค้างจากรอบก่อน เพราะ spooldir จะหยุดเมื่อเจอกรณีนี้
5. ถ้า client ทำงานปกติแต่ไฟล์ยังไม่ถูกเปลี่ยนชื่อ ตรวจว่าใช้คำนำหน้า client. ครบทุกบรรทัด (เช่นไม่มี clinet) และดูว่า collector รันอยู่และพอร์ตตรงกัน
6. ถ้าไฟล์ถูกเปลี่ยนเป็น .COMPLETED แล้วแต่ HDFS ว่าง ตรวจ log ของ collector เรื่องสิทธิ์เขียน HDFS (Permission denied) และรอให้ครบเงื่อนไข roll

**เกณฑ์คะแนน (6 คะแนน):** ตรวจ log ก่อน (1) ตรวจชื่อ agent และไฟล์ (1) ตรวจ spoolDir (1) ตรวจเงื่อนไข spooldir หยุด (1) ตรวจพอร์ตและลำดับการรัน (1) ตรวจสิทธิ์ HDFS/การ roll (1)

### โจทย์ L3 (ทำนายผล): Kafka console

producer ส่งข้อความ A, B, C เข้า topic ที่มี partition เดียว แล้วจบ (ก) consumer ที่เริ่มทีหลังด้วย --from-beginning เห็นอะไร (ข) consumer ที่เริ่มทีหลังโดยไม่ใส่ --from-beginning เห็นอะไร (ค) ถ้า producer ส่ง D ต่อ ตอนนี้ consumer ทั้งสองแบบเห็นอะไร และ D ได้ offset เท่าไร

**แนวตอบ:** (ก) เห็น A, B, C ตามลำดับ เพราะอ่านตั้งแต่ offset 0 (ข) ไม่เห็นข้อความเก่า เพราะเริ่มอ่านเฉพาะข้อความที่เข้ามาหลังจากเริ่มรัน (ค) ทั้งสองเห็น D เมื่อมีการส่ง และ D ได้ offset 3 (A, B, C คือ offset 0, 1, 2)

**เกณฑ์คะแนน (4 คะแนน):** (ก) 1 (ข) 1 (ค) 2

---

## 6. รายการตรวจตัวเองหลังจบปฏิบัติการ

- อธิบายได้ว่าเหตุใดตาราง avgprice_by_state ต้องใช้ -m 1 และตาราง country_tbl ไม่ต้อง
- บอกได้ว่าไฟล์ part-m-00000 มีรูปแบบอย่างไร และต่างจากผลของ --hive-import และ --hbase-table อย่างไร
- วาดโฟลว์ client agent ไป collector agent ได้ และบอกได้ว่า event ถูกลบจาก channel ของ client เมื่อใด
- อธิบายได้ว่าเหตุใดต้องรัน collector ก่อน client และเหตุใดพอร์ตสองไฟล์ต้องตรงกัน
- บอกได้ว่าเหตุใดไฟล์ใน HDFS มีจำนวนมากและเล็ก
- ส่งและอ่านข้อความผ่าน console producer และ consumer ได้ และอธิบายผลของ --from-beginning

---

## 7. References

1. Apache Sqoop. Sqoop User Guide (v1.4.6). https://sqoop.apache.org/docs/1.4.6/SqoopUserGuide.html
2. Apache Flume. Flume 1.9.0 User Guide. https://flume.apache.org/releases/content/1.9.0/FlumeUserGuide.html
