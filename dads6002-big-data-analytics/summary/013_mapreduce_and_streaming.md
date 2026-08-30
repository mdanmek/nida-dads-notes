# บทที่ 01.3: MapReduce, Hadoop Streaming และการปรับประสิทธิภาพ

> **จากเอกสาร:** dads6002_01_hadoop.pdf หน้า 22–38  
> **Core:** Map → partition/shuffle/sort → Reduce, Word Count, Shared Friendship, Python Streaming และ Combiner

> [← บทที่ 01.2](012_hdfs_and_yarn.md) | [สารบัญ](000_readme.md) | [บทที่ 01.4 →](014_workflow_orchestration.md)

## Learning Objectives ประจำบท

1. ติดตาม record ผ่าน InputFormat, Mapper, Partitioner, Shuffle/Sort และ Reducer ได้
2. ออกแบบ key/value สำหรับ Word Count และ Shared Friendship พร้อมตรวจความถูกต้องได้
3. เขียน รัน แก้ไข และ debug Hadoop Streaming mapper/reducer ด้วย Python ได้
4. อธิบาย retry/idempotency และเลือก Combiner อย่างไม่ทำให้คำตอบผิดได้
5. วินิจฉัย malformed output, unsorted local input และ output path conflict ได้

## Prerequisites และระดับความลึก

ต้องเข้าใจ HDFS blocks และ YARN จาก [บทที่ 01.2](012_hdfs_and_yarn.md) รวมถึง Python loop/dictionary เบื้องต้น หัวข้อ Core คือ data flow, key design และ Streaming code; syntax คำสั่งเป็น Reference

## MapReduce: จากแนวคิดสู่การไหลของข้อมูล

จากบทก่อน เรามีไฟล์ยอดขายอยู่ใน HDFS และมี YARN จัดสรรทรัพยากรให้ แต่สองสิ่งนี้ยังไม่บอกว่าจะคำนวณ “ยอดขายต่อสาขา” อย่างไรบนหลายเครื่อง ถ้าให้ทุกเครื่องอ่านทุก record งานจะซ้ำและสิ้นเปลือง ถ้าแบ่งไฟล์แล้วให้แต่ละเครื่องหาผลรวมของตัวเอง เราก็ยังต้องมีวิธีนำผลของสาขาเดียวกันกลับมารวมกัน MapReduce จึงเกิดจากปัญหาสองขั้นนี้: แปลงข้อมูลดิบเป็นหน่วยที่จัดกลุ่มได้ แล้วรวมค่าของกลุ่มเดียวกันให้เป็นคำตอบ

### MapReduce คืออะไร

**คำอธิบายพื้นฐาน:** MapReduce คือ **แบบจำลองและกรอบการประมวลผลข้อมูลแบบกระจาย** (distributed processing model/framework pattern) สำหรับแบ่งงานที่อ่านข้อมูลจำนวนมากออกไปทำบนหลายเครื่อง แล้วรวบรวมผลที่เกี่ยวข้องกันกลับมาสรุปอย่างเป็นระบบ ตัวมันไม่ใช่ฐานข้อมูล ไม่ใช่ระบบเก็บไฟล์ และไม่ใช่ฟังก์ชันเดียวที่ทำงานบนเครื่องเดียว; ใน Hadoop ข้อมูลมักอยู่ใน HDFS ส่วน YARN จัดทรัพยากร และ MapReduce กำหนดรูปแบบการประมวลผล

- **ปัญหาที่แก้:** เครื่องเดียวอ่านข้อมูลไม่ทันหรือเก็บข้อมูลทั้งหมดไม่ไหว และการแชร์ตัวแปรนับกลางระหว่างหลายเครื่องทำให้เกิดคอขวด
- **ขอบเขต:** หนึ่ง MapReduce **job** รับชุดข้อมูลเข้า แบ่งเป็น **tasks** บน workers หลายตัว และสร้างชุดไฟล์ผลลัพธ์ ไม่ได้ตอบ query แบบโต้ตอบทันที
- **input/output ทั่วไป:** input คือ records เช่น บรรทัด log; output คือ records สรุป เช่น `คำ → จำนวนครั้ง`
- **ผู้ลงมือ:** โค้ดของผู้ใช้กำหนด Map และ Reduce ส่วน framework แบ่งงาน ส่งข้อมูล จัดกลุ่ม key และ retry task ที่ล้ม

#### ตัวอย่างเล็กที่สุดแบบยังไม่ใช้ศัพท์เทคนิค

สมมติมีกระดาษสองแผ่น: `cat runs` และ `cat sleeps` ให้คนสองคนอ่านคนละแผ่นและเขียนบัตรคำ `cat:1`, `runs:1` หรือ `sleeps:1` จากนั้นเจ้าหน้าที่รวบบัตรชื่อเดียวกันไว้กองเดียว แล้วบวกเลขในแต่ละกอง ผลคือ `cat:2`, `runs:1`, `sleeps:1`

นี่คือเรื่องทั้งหมดในภาพกว้าง: **กระจายการอ่านและสร้างหลักฐานย่อย → รวมหลักฐานที่มีชื่อเดียวกัน → สรุปแต่ละกลุ่ม** อุปมานี้ช่วยอธิบายการไหลของข้อมูล แต่ในระบบจริงไม่มีเจ้าหน้าที่คนเดียว; framework กระจายทั้งการอ่าน การส่ง และการสรุปไปหลายเครื่อง

### ศัพท์พื้นฐานตามลำดับที่ต้องใช้

| คำ | ความหมายในบทนี้ | ตัวอย่างเดียวกัน |
|---|---|---|
| Record | หน่วยข้อมูลที่ส่งให้โปรแกรมประมวลผลหนึ่งครั้ง | หนึ่งบรรทัด `cat runs` |
| Key-value pair | คู่ “ป้ายกำกับ–ค่า” ที่ใช้บอกว่าข้อมูลใดควรรวมกัน | `(cat, 1)` |
| Map | แปลง record หนึ่งรายการเป็น intermediate pairs ศูนย์คู่หรือหลายคู่ | `cat runs` → `(cat,1),(runs,1)` |
| Intermediate result | ผลชั่วคราวหลัง Map ซึ่งยังไม่ใช่คำตอบสุดท้าย | บัตรคำทั้งหมด |
| Group by key | รวม values ของ key เดียวกัน | `cat → [1,1]` |
| Reduce | สรุป values หนึ่งกลุ่มเป็นผลลัพธ์ | `cat,[1,1]` → `cat,2` |

คำว่า **Map** ในที่นี้หมายถึง “แปลงข้อมูล” ไม่ใช่แผนที่ และ **Reduce** หมายถึง “สรุปข้อมูลในแต่ละ key” ไม่จำเป็นต้องลดจำนวน record เสมอไป เช่น reducer อาจ emit หลายผลลัพธ์ได้

### Functional model

**จากเอกสาร (หน้า 22–23)** Mapper และ Reducer ควรเป็น stateless functions ที่รับและส่งคู่ key-value:

```text
map(k1, v1)    -> list(k2, v2)
reduce(k2, [v2]) -> list(k3, v3)
```

#### ทำไมต้องมี Map และ Reduce แยกกัน

หากนับคำในไฟล์หนึ่งบนเครื่องเดียว โปรแกรมเพียงอ่านทุกบรรทัดแล้วเพิ่ม counter ก็พอ แต่เมื่อ input กระจายอยู่หลายร้อยเครื่อง การมี counter กลางหนึ่งตัวจะทำให้ทุกเครื่องต้องส่งข้อมูลไปแก้ state เดียวกัน เกิด network และ synchronization bottleneck MapReduce แก้ปัญหาด้วยการให้แต่ละ mapper ทำงานกับข้อมูลส่วนของตนโดยไม่แชร์ state แล้วใช้ key เป็นสัญญาว่า records ใดต้องมารวมกันภายหลัง

ใน Word Count mapper ยังไม่จำเป็นต้องรู้ว่าคำว่า `cat` ปรากฏรวมทั่วคลัสเตอร์กี่ครั้ง มันเพียง emit `(cat,1)` ส่วนระบบรับผิดชอบรวบรวมค่า `1` ของ key `cat` จาก mappers ทุกตัวไปยัง reducer เดียวกัน Reducer จึงคำนวณผลรวมได้โดยไม่ต้องอ่าน input ดิบทั้งหมด ความง่ายนี้มีราคา: intermediate data ต้องถูก sort และส่งผ่านเครือข่ายในช่วง shuffle ซึ่งมักเป็นระยะที่แพงที่สุด

#### การไหลของข้อมูลจริงและหน้าที่ของแต่ละองค์ประกอบ

เมื่อเข้าใจเรื่องบัตรคำแล้ว จึงค่อยแทนแต่ละช่วงด้วยชื่อทางการดังนี้

**1) InputFormat — กติกาว่าจะอ่าน input อย่างไร** Framework เรียก InputFormat ตอนเตรียม job เพื่อสร้าง **input splits** ซึ่งเป็นคำอธิบายช่วงข้อมูลเชิงตรรกะที่จะมอบให้ map task แต่ละตัว InputFormat ไม่ได้ประมวลผลคำและไม่ใช่ HDFS block; split อาจคร่อมหรือรวม blocks ได้ตามชนิดไฟล์ การบีบอัด และ configuration ถ้าแบ่งไม่เหมาะ งานอาจมี tasks น้อยเกินไปหรือเกิด imbalance

**2) RecordReader — ตัวแปลง bytes ให้เป็น records** ภายใน map task, RecordReader อ่าน split แล้วส่งคู่ input ให้ Mapper ทีละ record เช่น TextInputFormat มักให้ `(byte_offset, line_text)` มันจึงเป็นสะพานระหว่างไฟล์กับหน่วยข้อมูลที่โค้ดผู้ใช้เข้าใจ หากกำหนด record boundary ผิด เช่น ตัดข้อมูลหลายบรรทัดกลางรายการ Mapper จะได้รับข้อมูลไม่ครบ

**3) Mapper — ตัวสร้างคู่ผลลัพธ์ชั่วคราว** Framework เรียก Mapper สำหรับแต่ละ record; input คือ `(k1,v1)` และ output เป็นศูนย์คู่หรือหลายคู่ `(k2,v2)` Mapper ควรเก็บ state ให้น้อยและไม่ทำ side effect ภายนอก เพื่อให้ task รันซ้ำได้ ถ้า Mapper emit รูปแบบผิด งานช่วง shuffle/reduce อาจล้ม หรือแย่กว่านั้นคือได้ผลที่ดูถูกต้องแต่ข้อมูลหาย

**4) Partitioner — ตัวเลือก reducer ปลายทาง** หลัง Mapper, framework เรียก Partitioner กับ intermediate key เพื่อคืนหมายเลข partition เช่นแนวคิด `hash(key) mod R` โดย `R` คือจำนวน reducers หน้าที่ของมันคือ routing ไม่ใช่การรวมค่า เงื่อนไขสำคัญคือ key เดียวกันต้องไป reducer เดียวกัน; ถ้าฝ่าฝืน ผลรวมของ key จะถูกแยกและผิด

**5) Shuffle — การขนย้าย intermediate data** ระบบดึง partition ที่เกี่ยวข้องจาก map workers ไปยัง reducer ปลายทาง นี่เป็นกลไกของ framework ไม่ใช่ฟังก์ชันที่ผู้ใช้เรียกทีละ record และมักแพงเพราะใช้ network และ disk หาก Mapper สร้างข้อมูลชั่วคราวมาก ช่วงนี้จะกลายเป็นคอขวด

**6) Sort/Group — การจัด key และรวม values** ระบบเรียง intermediate keys และทำให้ values ของ key เดียวกันอยู่เป็นกลุ่มต่อเนื่อง เช่น `cat → [1,1]` ขั้นนี้เป็นเหตุให้ Streaming reducer แบบอ่านบรรทัดต่อบรรทัดสามารถรู้ได้ว่า key หนึ่งจบเมื่อใด

**7) Reducer — ตัวสรุปหนึ่ง key ต่อครั้ง** Framework เรียก Reducer ด้วย key และกลุ่ม values ที่จัดเตรียมแล้ว Reducer สร้างผลลัพธ์สุดท้าย `(k3,v3)` และ OutputFormat เขียนลงไฟล์ Reducer ไม่ต้องค้นหา values จาก mappers เอง; ถ้า logic ไม่ associative ตามที่คาดหรือมี side effect ที่ไม่ idempotent การ retry อาจทำให้ผิดหรือซ้ำ

สรุปลำดับอย่างเป็นทางการคือ `InputFormat → RecordReader → Mapper → Partitioner → Shuffle → Sort/Group → Reducer → OutputFormat` รายละเอียด API และ lifecycle ตรวจสอบได้จาก [Apache MapReduce Tutorial](https://hadoop.apache.org/docs/current/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html)

MapReduce สามารถ retry map task ได้เพราะ input อยู่ใน HDFS และ mapper ที่ดีไม่มี side effect ภายนอก หาก worker ล้ม task เดิมจึงไปรันบน worker อื่นได้ Reduce task ที่ล้มก็รันใหม่ได้จาก map outputs ที่ยังหาได้ หรืออาจบังคับให้ map บางส่วนสร้าง output ใหม่ อย่างไรก็ตาม ถ้า mapper เรียก API ที่ตัดเงินจริงหรือเขียนฐานข้อมูลโดยไม่มี idempotency การ retry อาจสร้างผลซ้ำ จึงต้องแยก pure transformation ออกจาก side effect

ให้ติดตามรายการ `สาขา=A, ยอด=100` ผ่านระบบ Mapper ไม่จำเป็นต้องรู้ยอดรวมทั้งหมด มันเพียงแปล record นี้เป็น `(A, 100)` เช่นเดียวกับ mapper อื่น ๆ เมื่อ Map phase จบ ระบบต้องรวบรวมคู่ที่มี key `A` จากทุกเครื่อง ขั้นนี้คือ shuffle และ sort/group จากนั้น Reducer ที่รับ key `A` จึงเห็นค่าทั้งหมด เช่น `[100, 80, 120]` และรวมเป็น 300 ได้ จุดแบ่งหน้าที่นี้ทำให้ map tasks ทำงานขนานโดยไม่ต้องสื่อสารกันตลอดเวลา ส่วนการสื่อสารหนักถูกจัดไว้ในช่วง shuffle อย่างชัดเจน

การแยกเช่นนี้มี trade-off MapReduce เหมาะกับงาน batch ที่แบ่งและรวมได้ แต่ shuffle ใช้ทั้ง network และ disk และแต่ละ job มี overhead จึงไม่เหมาะกับคำถามโต้ตอบที่ต้องตอบในเสี้ยววินาที ความเข้าใจนี้ช่วยให้เราไม่สรุปว่า “กระจายแล้วเร็วเสมอ” งานเล็กอาจช้ากว่าการคำนวณบนเครื่องเดียว และ key ที่กระจายไม่สมดุลอาจทำให้ reducer ตัวเดียวกลายเป็นคอขวด

#### Key design คือหัวใจของอัลกอริทึม

Key ไม่ใช่เพียงชื่อ column แต่เป็นการกำหนดว่า records ใดต้องพบกัน หากเลือก key ละเอียดเกินไป values ที่ควรรวมอาจแยกกัน หากหยาบเกินไป reducer เดียวอาจรับข้อมูลมหาศาลและเกิด skew ตัวอย่างเช่น `(date,branch)` ช่วยกระจายยอดขายรายสาขา แต่ key เพียง `date` อาจทำให้วันขายใหญ่ทั้งหมดไปรวม reducer เดียว การออกแบบ key จึงต้องคำนึงพร้อมกันทั้ง semantics ของคำตอบและ load distribution

### Worked Example: Word Count

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

### Worked Example: Shared Friendship

**จากเอกสาร (หน้า 28–32)** ให้ adjacency list ของ Allen, Betty, Chris, David และ Ellen แล้วหาเพื่อนร่วมกันของทุกคู่ Mapper สร้าง canonical pair เพื่อไม่ให้ `(Allen, Betty)` กับ `(Betty, Allen)` แยกกัน จากนั้น Reducer หาจุดตัดของ friend lists ตัวอย่างผลคือ Allen กับ Betty มี Chris และ David เป็นเพื่อนร่วมกัน

```text
key = tuple(sorted([person_a, person_b]))
mutual_friends = friends_of_a ∩ friends_of_b
```

เหตุที่ต้อง sort ชื่อใน pair คือ adjacency list มองความสัมพันธ์จากสองทิศ ถ้าไม่ canonicalize Mapper ของ Allen อาจ emit `(Allen,Betty)` แต่ Mapper ของ Betty emit `(Betty,Allen)` ทำให้ shuffle มองเป็นคนละ key และ Reducer ไม่ได้รับ friend lists สองฝั่งพร้อมกัน เมื่อใช้ canonical pair ทั้งคู่จะถูก group เป็น key เดียว แล้ว reducer จึงคำนวณ intersection ได้

สำหรับคู่ Allen/Betty สมมติ list จาก Allen คือ `{Betty, Chris, David}` และ list จาก Betty คือ `{Allen, Chris, David, Ellen}` จุดตัดคือ `{Chris, David}` ต้องตัดสมาชิกของ pair เองออกหากรูปแบบ input ทำให้หลุดเข้ามา Validation ที่ดีคือ output pair ต้องเรียงชื่อคงที่, mutual friends ต้องอยู่ใน lists ของทั้งสองฝั่ง และไม่ควรมี duplicate names

**คำอธิบายเพิ่มเติม:** ปัญหานี้เชื่อมกับ graph analytics และ recommendation แต่ “มีเพื่อนร่วมกัน” ไม่ควรถูกใช้เป็นเหตุผลเพียงอย่างเดียวในการแนะนำบุคคล เพราะอาจเปิดเผยความสัมพันธ์ที่ผู้ใช้ไม่ต้องการ เปิดช่อง stalking หรือสร้าง bias จึงต้องมี privacy controls, blocking rules และ evaluation มากกว่า click-through rate

## Hadoop Streaming ด้วย Python

**จากเอกสาร (หน้า 33–38)** Streaming ใช้โปรแกรมใดก็ได้ที่อ่าน `stdin` และเขียน `stdout`; Hadoop ส่ง input ให้ mapper และตีความบรรทัด output เป็น key-value ก่อน shuffle ไป reducer กลไก executable/stdin/stdout นี้ตรวจสอบเพิ่มเติมจาก [Apache Hadoop Streaming](https://hadoop.apache.org/docs/current/hadoop-streaming/HadoopStreaming.html)

> **คำอธิบายเพิ่มเติม/แก้ไข:** โค้ด Python ใน PDF มี capitalization, semicolon, indentation และ `__name__` ที่ไม่ถูกต้อง ตัวอย่างต่อไปนี้รักษาแนวคิดเดิม แต่แก้ให้รันได้จริง

### `mapper.py`

```python
#!/usr/bin/env python3
import re
import sys

for line in sys.stdin:
    for word in re.findall(r"[A-Za-z0-9']+", line.lower()):
        print(f"{word}\t1")
```

### `reducer.py`

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
hadoop jar /opt/hadoop/share/hadoop/tools/lib/hadoop-streaming-*.jar \
  -files mapper.py,reducer.py \
  -mapper mapper.py \
  -reducer reducer.py \
  -input /user/student/input \
  -output /user/student/output
```

ตรวจผลด้วย `hadoop fs -cat /user/student/output/part-*` และจำไว้ว่า output directory ต้องยังไม่มีอยู่ก่อนเริ่ม job

## Combiner และการลด network traffic

### Combiner

**จากเอกสาร (หน้า 37–38)** Combiner ทำ local aggregation หลัง mapper เพื่อลดข้อมูลที่ส่งผ่านเครือข่าย เช่น รวมจำนวนเที่ยวบินของ IAD/JFK/SFO ก่อน shuffle

**คำอธิบายเพิ่มเติม:** Hadoop ไม่รับประกันว่า Combiner จะรันกี่ครั้งหรือจะรันเลยหรือไม่ ตามข้อควรระวังใน [Apache MapReduce Tutorial](https://hadoop.apache.org/docs/current/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html) ดังนั้นคำตอบต้องถูกต้องแม้ไม่มี Combiner ฟังก์ชัน `sum`, `min`, `max` มักปลอดภัยเพราะ associative/commutative แต่ค่าเฉลี่ยห้ามเฉลี่ยค่าเฉลี่ยโดยตรง

ตัวอย่าง: กลุ่ม A มี `[10,20]` เฉลี่ย 15; กลุ่ม B มี `[100]` เฉลี่ย 100 การเฉลี่ย `15` กับ `100` ได้ 57.5 แต่คำตอบจริงคือ `(10+20+100)/3 = 43.33` ต้องส่ง `(sum,count)` แล้วรวมทั้งสองส่วน

## สะพานจากหนึ่ง job ไปสู่ workflow

MapReduce job หนึ่งงานมีขอบเขตชัด: อ่าน input สร้าง intermediate pairs และเขียน output แต่การใช้งานจริงไม่จบที่ยอดรวมหนึ่งตาราง หลังคำนวณยอดขาย เราอาจต้องตรวจคุณภาพ ผูกกับ master data คำนวณสต็อก แล้วเผยแพร่ dashboard แต่ละขั้นอาจเป็นคนละ job และบางขั้นรันขนานได้ เมื่อ job แรกช้า หรือล้ม งานถัดไปต้องไม่อ่าน output ที่ยังไม่สมบูรณ์

ข้อจำกัดนี้นำไปสู่สองแนวคิดในบทถัดไป แนวคิดแรกคือ Partitioner ซึ่งควบคุมการกระจาย key ภายใน job และช่วยให้เราอธิบายปัญหา data skew แนวคิดที่สองคือ workflow orchestration ซึ่งควบคุมความสัมพันธ์ระหว่างหลาย jobs จำสั้น ๆ ว่า Partitioner ตอบว่า “ข้อมูลกลุ่มนี้ไป reducer ใด” ส่วน orchestrator ตอบว่า “งานใดต้องรอหรือรันต่อจากงานใด” การแยกสองระดับนี้เป็นประเด็นที่มักใช้ทั้งในข้อสอบและการวินิจฉัยระบบจริง

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

## Guided Lab: Copy, Run, Break, Repair

### Input และคำสั่ง

บันทึก Mapper/Reducer ข้างต้น แล้วรัน:

```bash
printf 'The fast cat wears no hat.\nThe cat in the hat ran fast.\n' \
  | python3 mapper.py \
  | sort \
  | python3 reducer.py
```

ผลที่ตรวจสอบแล้วควรเป็น:

```text
cat     2
fast    2
hat     2
in      1
no      1
ran     1
the     3
wears   1
```

ก่อนดูผล ให้ทำนาย `the`, `cat` และจำนวน tokens รวม จากนั้นตรวจว่า sum ของ output counts = 13

### Deliberate failures

1. เอา `sort` ออก: key เดิมอาจแยกหลายช่วง ทำให้ reducer emit key ซ้ำ
2. เปลี่ยน mapper ให้พิมพ์ space แทน tab: reducer เกิด `ValueError`
3. เอา final flush ออก: key สุดท้ายหาย
4. ส่ง job ไป output directory เดิม: Hadoop ปฏิเสธเพื่อไม่ overwrite โดยไม่ตั้งใจ

หลังซ่อมต้อง rerun ได้ผลเดิมทุกครั้ง นี่คือหลักฐาน reproducibility ขั้นต่ำ

## Troubleshooting และ Validation

| อาการ | จุดตรวจ | วิธีแก้ |
|---|---|---|
| output key ซ้ำใน local test | input reducer ไม่ sorted | ใส่ `sort` ระหว่าง processes |
| `ValueError` ตอน split/int | mapper contract ผิด | inspect tab และ numeric value |
| คำสุดท้ายหาย | ไม่มี final flush | emit state หลัง loop |
| counts รวมไม่เท่า token count | tokenizer/reject/drop | เทียบ mapper line count และ sample output |
| reducers บางตัวช้ามาก | key skew | distribution, hot keys, pre-aggregation |

## Progressive Practice และ Model Answers

**Completion:** เติมเหตุผลว่า key เดียวกันต้องไป reducer เดียวกัน เพราะ ______  
**เฉลย:** reducer ต้องเห็น values ทั้งหมดของ key เพื่อคำนวณ aggregate ที่ครบ มิฉะนั้นจะได้ partial results หลายชุด

**Analyze:** ทำไม average ใช้เป็น Combiner โดยส่งเลขเฉลี่ยอย่างเดียวไม่ได้?  
**เฉลย:** partial groups มีขนาดไม่เท่ากัน ค่าเฉลี่ยของค่าเฉลี่ยให้น้ำหนักแต่ละกลุ่มเท่ากัน ตัวอย่าง `[10,20]` กับ `[100]` ให้ 57.5 แต่ค่าจริง 43.33 ต้องส่ง `(sum,count)` ซึ่งรวมต่อได้

**Transfer:** ต้องการยอดขายรายวัน-สาขา ควรใช้ key ใด?  
**แนวคำตอบ:** `(business_date, branch_id)` เพราะ records ที่ต้องรวมพบกัน หากใช้ date อย่างเดียวจะเสีย grain และเสี่ยง hot partition; หากใช้ transaction ID จะละเอียดเกินไปและไม่ aggregate ระดับที่ถาม

**Evaluate:** Mapper เขียนลงฐานข้อมูลโดยตรงแล้ว task ถูก retry มีความเสี่ยงอะไร?  
**เฉลย:** side effect อาจเกิดซ้ำ แม้ MapReduce มอง task attempt ใหม่ว่าถูกต้อง ต้องใช้ idempotent key/transactional sink หรือเขียน output ผ่าน commit protocol แทน

## Mastery Checklist

- [ ] trace record ผ่าน Map → partition → shuffle/sort → Reduce ได้
- [ ] reproduce Word Count และ validate total tokens ได้
- [ ] อธิบาย reducer state/final flush จาก trace table ได้
- [ ] ออกแบบ canonical key ของ Shared Friendship ได้
- [ ] repair malformed/unsorted Streaming pipeline ได้
- [ ] เลือก Combiner โดยพิสูจน์ correctness ได้

## Glossary และ Source Coverage

| คำ | ความหมาย |
|---|---|
| Input split | หน่วยเชิงตรรกะที่มอบให้ map task อ่าน |
| Shuffle | การโอน intermediate records ไป reducer ตาม partition |
| Sort/Group | การจัด key เพื่อให้ values ของ key เดียวอยู่รวมกัน |
| Combiner | local pre-aggregation ที่อาจรันศูนย์หรือหลายครั้ง |
| Final flush | การ emit state กลุ่มสุดท้ายหลัง input จบ |

ครอบคลุม PDF หน้า 22–28 MapReduce/Word Count, หน้า 29–32 Shared Friendship และหน้า 33–38 Jobs/Streaming/Combiner โค้ดต้นฉบับที่ syntax ผิดถูกแยกจากฉบับแก้ไขชัดเจน

## References

- เอกสารหลัก หน้า 22–38
- [Apache Hadoop: MapReduce Tutorial](https://hadoop.apache.org/docs/current/hadoop-mapreduce-client/hadoop-mapreduce-client-core/MapReduceTutorial.html)
- [Apache Hadoop: Hadoop Streaming](https://hadoop.apache.org/docs/current/hadoop-streaming/HadoopStreaming.html)
- [Google Research: MapReduce](https://research.google/pubs/mapreduce-simplified-data-processing-on-large-clusters/)
