# บทที่ 3: MapReduce, Hadoop Streaming และการปรับประสิทธิภาพ

> **จากเอกสาร:** dads6002_week01-03_hadoop.pdf หน้า 22–38  
> **Core:** Map → partition/shuffle/sort → Reduce, Word Count, Shared Friendship, Python Streaming และ Combiner

## 10. MapReduce: จากแนวคิดสู่การไหลของข้อมูล

### 10.1 Functional model

**จากเอกสาร (หน้า 22–23)** Mapper และ Reducer ควรเป็น stateless functions ที่รับและส่งคู่ key-value:

```text
map(k1, v1)    -> list(k2, v2)
reduce(k2, [v2]) -> list(k3, v3)
```

#### ทำไมต้องมี Map และ Reduce แยกกัน

หากนับคำในไฟล์หนึ่งบนเครื่องเดียว โปรแกรมเพียงอ่านทุกบรรทัดแล้วเพิ่ม counter ก็พอ แต่เมื่อ input กระจายอยู่หลายร้อยเครื่อง การมี counter กลางหนึ่งตัวจะทำให้ทุกเครื่องต้องส่งข้อมูลไปแก้ state เดียวกัน เกิด network และ synchronization bottleneck MapReduce แก้ปัญหาด้วยการให้แต่ละ mapper ทำงานกับข้อมูลส่วนของตนโดยไม่แชร์ state แล้วใช้ key เป็นสัญญาว่า records ใดต้องมารวมกันภายหลัง

ใน Word Count mapper ยังไม่จำเป็นต้องรู้ว่าคำว่า `cat` ปรากฏรวมทั่วคลัสเตอร์กี่ครั้ง มันเพียง emit `(cat,1)` ส่วนระบบรับผิดชอบรวบรวมค่า `1` ของ key `cat` จาก mappers ทุกตัวไปยัง reducer เดียวกัน Reducer จึงคำนวณผลรวมได้โดยไม่ต้องอ่าน input ดิบทั้งหมด ความง่ายนี้มีราคา: intermediate data ต้องถูก sort และส่งผ่านเครือข่ายในช่วง shuffle ซึ่งมักเป็นระยะที่แพงที่สุด

#### การไหลของข้อมูลจริง

1. InputFormat แบ่ง input เป็น splits และ RecordReader สร้าง records
2. Mapper แปลงแต่ละ record เป็น intermediate pairs
3. Partitioner เลือกว่า key ใดไป reducer ตัวใด
4. Shuffle โอนข้อมูลข้าม node และ Sort จัด key/group values
5. Reducer สรุปผลของแต่ละ key และเขียน output

Input split เป็นมุมมองเชิงตรรกะสำหรับงานอ่าน ส่วน HDFS block เป็นหน่วยจัดเก็บ ทั้งสองมักมีขนาดใกล้กันเพื่อ locality แต่ไม่ใช่สิ่งเดียวกันเสมอ จำนวน splits ขึ้นกับ InputFormat, compression และ configuration RecordReader แปลง bytes ให้เป็น records เช่น `(byte_offset, line_text)` ก่อนเรียก mapper

หลัง mapper, Partitioner ใช้ key เลือก reducer โดยทั่วไปแนวคิดคล้าย `hash(key) mod number_of_reducers` เงื่อนไขสำคัญคือ key เดียวกันต้องไป partition เดียวกัน จากนั้น mapper output ของแต่ละ partition ถูก sort ในเครื่องต้นทางและ shuffle ไปยัง reducer ปลายทาง Reducer จึงเห็น `key` พร้อม iterable ของ values ที่ถูก group แล้ว ไม่ได้เห็นข้อมูลแยกตาม mapper

MapReduce สามารถ retry map task ได้เพราะ input อยู่ใน HDFS และ mapper ที่ดีไม่มี side effect ภายนอก หาก worker ล้ม task เดิมจึงไปรันบน worker อื่นได้ Reduce task ที่ล้มก็รันใหม่ได้จาก map outputs ที่ยังหาได้ หรืออาจบังคับให้ map บางส่วนสร้าง output ใหม่ อย่างไรก็ตาม ถ้า mapper เรียก API ที่ตัดเงินจริงหรือเขียนฐานข้อมูลโดยไม่มี idempotency การ retry อาจสร้างผลซ้ำ จึงต้องแยก pure transformation ออกจาก side effect

#### Key design คือหัวใจของอัลกอริทึม

Key ไม่ใช่เพียงชื่อ column แต่เป็นการกำหนดว่า records ใดต้องพบกัน หากเลือก key ละเอียดเกินไป values ที่ควรรวมอาจแยกกัน หากหยาบเกินไป reducer เดียวอาจรับข้อมูลมหาศาลและเกิด skew ตัวอย่างเช่น `(date,branch)` ช่วยกระจายยอดขายรายสาขา แต่ key เพียง `date` อาจทำให้วันขายใหญ่ทั้งหมดไปรวม reducer เดียว การออกแบบ key จึงต้องคำนึงพร้อมกันทั้ง semantics ของคำตอบและ load distribution

### 10.2 Worked Example: Word Count

**จากเอกสาร (หน้า 24–27)** ใช้ข้อความสองส่วน:

```text
The fast cat wears no hat.
The cat in the hat ran fast.
```

Mapper ทำ normalization แล้ว emit `(word, 1)` เช่น `(cat,1)`; shuffle/sort รวมเป็น `cat -> [1,1]`; reducer บวกค่าเป็น `cat -> 2`

| ระยะ | ตัวอย่างผล |
|---|---|
| Map | `(the,1) (fast,1) (cat,1) ...` |
| Shuffle/Sort | `cat:[1,1]`, `fast:[1,1]`, `the:[1,1,1]` |
| Reduce | `cat:2`, `fast:2`, `the:3` |

ข้อควรระวัง: ต้องกำหนด policy ของตัวพิมพ์ใหญ่ เครื่องหมายวรรคตอน Unicode และ tokenization ก่อน ไม่เช่นนั้น `The`, `the`, `hat.` และ `hat` อาจถูกนับเป็นคนละคำ

#### Trace แบบไม่ข้ามขั้น

กำหนดให้ normalize เป็นตัวพิมพ์เล็กและตัดจุดท้ายคำ Mapper 1 จึง emit `the, fast, cat, wears, no, hat` อย่างละค่า 1 ส่วน Mapper 2 emit `the, cat, in, the, hat, ran, fast` อย่างละค่า 1 Partitioner ตรวจ key เช่น `cat` จากทั้งสอง mapper แล้วส่งไป reducer เดียวกัน Shuffle ทำหน้าที่เคลื่อน intermediate records ส่วน sort/group ทำให้ reducer เห็น `cat -> [1,1]` ต่อเนื่องกัน

Reducer ไม่ต้องรู้ว่าเลข 1 ตัวแรกมาจาก block ใด เพียงบวก iterable เป็น 2 Validation ทำได้สองทาง: นับ token ทั้งหมดจาก input ได้ 13 และรวม counts ทุก key จาก output ต้องได้ 13; จากนั้นสุ่มตรวจ `the=3`, `cat=2`, `in=1` ด้วยมือ หากผลรวมไม่เท่ากัน ให้ตรวจ tokenizer, malformed output หรือ records ที่ถูก reject

### 10.3 Worked Example: Shared Friendship

**จากเอกสาร (หน้า 28–32)** ให้ adjacency list ของ Allen, Betty, Chris, David และ Ellen แล้วหาเพื่อนร่วมกันของทุกคู่ Mapper สร้าง canonical pair เพื่อไม่ให้ `(Allen, Betty)` กับ `(Betty, Allen)` แยกกัน จากนั้น Reducer หาจุดตัดของ friend lists ตัวอย่างผลคือ Allen กับ Betty มี Chris และ David เป็นเพื่อนร่วมกัน

```text
key = tuple(sorted([person_a, person_b]))
mutual_friends = friends_of_a ∩ friends_of_b
```

เหตุที่ต้อง sort ชื่อใน pair คือ adjacency list มองความสัมพันธ์จากสองทิศ ถ้าไม่ canonicalize Mapper ของ Allen อาจ emit `(Allen,Betty)` แต่ Mapper ของ Betty emit `(Betty,Allen)` ทำให้ shuffle มองเป็นคนละ key และ Reducer ไม่ได้รับ friend lists สองฝั่งพร้อมกัน เมื่อใช้ canonical pair ทั้งคู่จะถูก group เป็น key เดียว แล้ว reducer จึงคำนวณ intersection ได้

สำหรับคู่ Allen/Betty สมมติ list จาก Allen คือ `{Betty, Chris, David}` และ list จาก Betty คือ `{Allen, Chris, David, Ellen}` จุดตัดคือ `{Chris, David}` ต้องตัดสมาชิกของ pair เองออกหากรูปแบบ input ทำให้หลุดเข้ามา Validation ที่ดีคือ output pair ต้องเรียงชื่อคงที่, mutual friends ต้องอยู่ใน lists ของทั้งสองฝั่ง และไม่ควรมี duplicate names

**คำอธิบายเพิ่มเติม:** ปัญหานี้เชื่อมกับ graph analytics และ recommendation แต่ “มีเพื่อนร่วมกัน” ไม่ควรถูกใช้เป็นเหตุผลเพียงอย่างเดียวในการแนะนำบุคคล เพราะอาจเปิดเผยความสัมพันธ์ที่ผู้ใช้ไม่ต้องการ เปิดช่อง stalking หรือสร้าง bias จึงต้องมี privacy controls, blocking rules และ evaluation มากกว่า click-through rate

## 11. Hadoop Streaming ด้วย Python

**จากเอกสาร (หน้า 33–38)** Streaming ใช้โปรแกรมใดก็ได้ที่อ่าน `stdin` และเขียน `stdout`; Hadoop ส่ง input ให้ mapper และตีความบรรทัด output เป็น key-value ก่อน shuffle ไป reducer

> **คำอธิบายเพิ่มเติม/แก้ไข:** โค้ด Python ใน PDF มี capitalization, semicolon, indentation และ `__name__` ที่ไม่ถูกต้อง ตัวอย่างต่อไปนี้รักษาแนวคิดเดิม แต่แก้ให้รันได้จริง

### 11.1 `mapper.py`

```python
#!/usr/bin/env python3
import re
import sys

for line in sys.stdin:
    for word in re.findall(r"[A-Za-z0-9']+", line.lower()):
        print(f"{word}\t1")
```

### 11.2 `reducer.py`

```python
#!/usr/bin/env python3
import sys

current_word = None
current_count = 0

for line in sys.stdin:
    word, count_text = line.rstrip("\n").split("\t", 1)
    count = int(count_text)

    if word == current_word:
        current_count += count
    else:
        if current_word is not None:
            print(f"{current_word}\t{current_count}")
        current_word = word
        current_count = count

if current_word is not None:
    print(f"{current_word}\t{current_count}")
```

Reducer ใช้ state เพียงสองตัว `current_word` และ `current_count` เพราะ input ถูก sort แล้ว เมื่อ key เดิมเข้ามาจะสะสม count แต่เมื่อ key เปลี่ยนต้อง emit กลุ่มก่อนหน้า แล้ว reset state ให้ key ใหม่ เงื่อนไข `current_word is not None` ป้องกันการพิมพ์ค่าหลอกก่อนอ่าน record แรก ส่วน final block หลัง loop จำเป็นเพราะ EOF ไม่ทำให้ branch `else` ทำงาน หากตัดออก key สุดท้ายจะหาย

บรรทัด `split("\t", 1)` กำหนด data contract ว่า mapper output ต้องมี tab คั่น key/value และ value ต้องแปลงเป็น integer ได้ ใน production ควรตัดสินใจชัดว่าจะ fail fast เมื่อ malformed หรือส่งไป reject stream; การข้ามเงียบ ๆ ทำให้ยอดรวมดูสมเหตุผลแต่ไม่ครบ

Reducer นี้พึ่งพา input ที่ sort ตาม key แล้ว ซึ่ง Hadoop shuffle รับประกันให้ แต่การทดสอบ local ต้องใส่ `sort` เอง:

```bash
printf 'The fast cat wears no hat.\nThe cat in the hat ran fast.\n' \
  | python3 mapper.py \
  | sort \
  | python3 reducer.py
```

ตัวอย่างส่งงานจริง (path ของ JAR แตกต่างตาม installation):

```bash
hadoop jar "$HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar" \
  -files mapper.py,reducer.py \
  -mapper mapper.py \
  -reducer reducer.py \
  -input /user/student/input \
  -output /user/student/output
```

ตรวจผลด้วย `hadoop fs -cat /user/student/output/part-*` และจำไว้ว่า output directory ต้องยังไม่มีอยู่ก่อนเริ่ม job

## 12. Combiner, Partitioner, Data Skew และ Job Chaining

### 12.1 Combiner

**จากเอกสาร (หน้า 37–38)** Combiner ทำ local aggregation หลัง mapper เพื่อลดข้อมูลที่ส่งผ่านเครือข่าย เช่น รวมจำนวนเที่ยวบินของ IAD/JFK/SFO ก่อน shuffle

**คำอธิบายเพิ่มเติม:** Hadoop ไม่รับประกันว่า Combiner จะรันกี่ครั้งหรือจะรันเลยหรือไม่ ดังนั้นคำตอบต้องถูกต้องแม้ไม่มี Combiner ฟังก์ชัน `sum`, `min`, `max` มักปลอดภัยเพราะ associative/commutative แต่ค่าเฉลี่ยห้ามเฉลี่ยค่าเฉลี่ยโดยตรง

ตัวอย่าง: กลุ่ม A มี `[10,20]` เฉลี่ย 15; กลุ่ม B มี `[100]` เฉลี่ย 100 การเฉลี่ย `15` กับ `100` ได้ 57.5 แต่คำตอบจริงคือ `(10+20+100)/3 = 43.33` ต้องส่ง `(sum,count)` แล้วรวมทั้งสองส่วน

## Trace Table: Reducer ทำไมต้องมี final flush

| Input | current_word ก่อน | การตัดสินใจ | Output ทันที | State หลัง |
|---|---|---|---|---|
| cat + 1 | None | เริ่ม key แรก | - | cat,1 |
| cat + 1 | cat | key เดิม | - | cat,2 |
| dog + 1 | cat | key เปลี่ยน | cat + 2 | dog,1 |
| EOF | dog | ไม่มีบรรทัดถัดไปกระตุ้น else | dog + 1 | จบ |

หากลบ final flush หลัง loop คำสุดท้ายจะหาย เพราะ reducer emit key ก่อนหน้าเมื่อพบ key ใหม่เท่านั้น แต่ EOF ไม่ใช่ key ใหม่ นี่เป็น pattern สำคัญของ streaming aggregation

## Modification Experiments

1. ตัด line.lower() ออกแล้วทำนายว่า The กับ the จะรวมกันหรือไม่
2. ตัด sort ออกจาก local pipeline แล้วสังเกตว่า key เดิมอาจปรากฏหลายกลุ่ม
3. เปลี่ยน mapper ให้ emit (word, len(word)) แล้ว reducer หาผลรวมความยาว อธิบายว่าคำตอบหมายถึงอะไร
4. ลองใช้ average เป็น Combiner แล้วสร้าง counterexample เพื่อพิสูจน์ว่า average-of-averages ผิด

## Mastery Check ประจำบท

ผู้เรียนควรติดตามหนึ่ง record ผ่านทุก stage ได้, ออกแบบ key ให้ถูกทั้ง semantics และ load distribution, อธิบาย retry/idempotency, เขียน Streaming mapper/reducer ที่รันจริง และวินิจฉัย malformed output, unsorted input, output path ซ้ำ และ data skew ได้

## References

- เอกสารหลัก หน้า 22–38
- [Apache Hadoop: MapReduce Tutorial](https://hadoop.apache.org/docs/current/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html)
- [Apache Hadoop: Hadoop Streaming](https://hadoop.apache.org/docs/current/hadoop-streaming/HadoopStreaming.html)
- [Google Research: MapReduce](https://research.google/pubs/mapreduce-simplified-data-processing-on-large-clusters/)
