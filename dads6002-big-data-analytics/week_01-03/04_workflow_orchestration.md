# บทที่ 4: Partitioner, Job Chaining และ Workflow Orchestration

> **จากเอกสาร:** dads6002_week01-03_hadoop.pdf หน้า 39–43  
> **Core:** data skew, การเชื่อม jobs เป็น DAG, Oozie fork/join และ Airflow workflows as code

> [← บทที่ 3](03_mapreduce_and_streaming.md) | [สารบัญ](README.md)

## Learning Objectives ประจำบท

1. วิเคราะห์ data skew และเลือก pre-aggregation, salting หรือ custom partitioning ได้
2. วาด DAG ที่มี sequential/parallel dependencies และตรวจ cycle ได้
3. อธิบาย Oozie fork/join และ Airflow task lifecycle ได้
4. แปล cron โดยคำนึงถึง timezone/data interval และออกแบบ retry ที่ idempotent ได้
5. เลือก Oozie หรือ Airflow จากข้อจำกัดจริง ไม่ใช่ความใหม่ของเครื่องมือได้

## Prerequisites และระดับความลึก

ควรอ่าน [บทที่ 3](03_mapreduce_and_streaming.md) เพื่อเข้าใจ Partitioner และ job output ก่อน หัวข้อ Core คือ skew, DAG และ orchestration; operator names และ cron syntax เป็น Reference

## 1. จาก MapReduce job เดี่ยวสู่งานข้อมูลจริง

**จากเอกสาร (หน้า 39–40)** Partitioner ควบคุมว่า key และ values จะถูกส่งไป reducer ใด ค่าเริ่มต้นคือ HashPartitioner ส่วนงานข้อมูลจริงมักมีหลาย jobs ที่ต้องรันตามลำดับหรือขนานกัน

MapReduce job หนึ่งชุดตอบโจทย์ transformation หนึ่งช่วงได้ดี แต่ pipeline จริงมักประกอบด้วยการรับข้อมูล ตรวจคุณภาพ แปลงข้อมูล สรุปผล และเผยแพร่ หากเริ่มทุกงานด้วย cron แยกกันโดยไม่บอก dependency งานปลายทางอาจเริ่มทั้งที่ input ยังไม่เสร็จ หรือทำงานต่อจาก upstream ที่ล้มเหลว **Workflow orchestration** จึงเป็นการนิยามว่า task ใดต้องรัน เมื่อใด ขึ้นกับ task ใด retry อย่างไร และสถานะใดถือว่าสำเร็จ

## 2. Partitioner และ Data Skew

Partitioner ทำงานหลัง Mapper โดยเลือก partition ของ intermediate key เงื่อนไขความถูกต้องคือ key เดียวกันต้องไป reducer เดียวกัน มิฉะนั้น reducer แต่ละตัวจะเห็นข้อมูลเพียงบางส่วนและผลรวมจะผิด HashPartitioner มักกระจาย “จำนวน keys” ได้ดีเมื่อ key distribution สมเหตุผล แต่ไม่ได้รับประกันว่าจำนวน values หรือปริมาณงานจะเท่ากัน

สมมติมี reducers 4 ตัว และ key UNKNOWN มี 8 ล้าน records ขณะที่ keys อื่นรวมกัน 2 ล้าน records แม้ hash จะส่ง keys อื่นกระจายดี reducer ที่รับ UNKNOWN ก็ยังหนักกว่ามาก ช่วงท้าย job จึงเหลือ reducer เดียวทำงาน ขณะที่อีกสามตัวว่าง อาการนี้เรียกว่า **data skew** การเพิ่ม reducers อย่างเดียวไม่แก้ เพราะ values ของ UNKNOWN ยังต้องอยู่ partition เดียว

แนวทางแก้ต้องรักษาความหมายของผลลัพธ์:

1. ทำ local aggregation หรือ Combiner เพื่อลดจำนวน values ก่อน shuffle
2. แก้ data quality หาก UNKNOWN เกิดจาก key ที่หายผิดปกติ
3. ทำ **salting** เช่นแบ่งเป็น UNKNOWN#0 ถึง UNKNOWN#9 ในรอบแรก แล้วรวม partial results อีกรอบ
4. ใช้ custom partitioner เมื่อรู้ distribution ล่วงหน้า
5. เปลี่ยน grain หากคำถามธุรกิจไม่จำเป็นต้องรวมทุก record ใน key เดียว

Salting แลก skew ที่ลดลงกับ job เพิ่มอีกขั้นและ logic ที่ซับซ้อนขึ้น จึงต้อง validate ว่าผลรวมหลัง unsalt เท่ากับ baseline

## 3. DAG: ภาษาในการอธิบาย dependency

**จากเอกสาร (หน้า 40–43)** workflow มีงานแบบ sequential และ parallel โดย Oozie ใช้ fork/join ส่วน Airflow นิยาม workflow เป็น Python DAG

**DAG (Directed Acyclic Graph)** คือกราฟมีทิศทางที่ไม่มีวงจร Node แทน task และ edge แทน dependency คำว่า acyclic สำคัญ เพราะถ้า A รอ B และ B รอ A จะไม่มีงานใดเริ่มได้

ตัวอย่าง pipeline คือ Ingest แล้วแยก Schema Check และ Volume Check ให้รันขนาน จากนั้น Aggregate ต้องรอทั้งสอง check ก่อนจึง Publish หาก Volume Check ล้ม Aggregate และ Publish ต้องไม่รัน การวาด DAG จึงทำให้ data contract มองเห็นได้ ไม่ใช่เพียงจัดลำดับ script

## 4. Apache Oozie

**จากเอกสาร (หน้า 40–41)** Oozie เป็น scheduler สำหรับงาน Hadoop รองรับ Hive, Pig, MapReduce และงานอื่น รวม jobs แบบลำดับและ fork/join โดย workflow เขียนเป็น XML

Oozie มี **action nodes** สำหรับลงมือทำงาน และ **control nodes** สำหรับควบคุมเส้นทาง เช่น start, end, decision, fork, join และ kill Fork เปิดหลาย branch พร้อมกัน ส่วน join รอ branch ที่เกี่ยวข้องก่อนเดินต่อ เอกสารทางการอธิบาย workflow เป็น DAG ของ action/control nodes ใน [Oozie Workflow Functional Specification](https://oozie.apache.org/docs/5.2.1/WorkflowFunctionalSpec.html)

ข้อดีคือเข้ากับ Hadoop ecosystem แบบดั้งเดิมและมี model ชัดสำหรับ job chaining ข้อจำกัดคือ XML อาจยาว การทดสอบและสร้าง workflow แบบ dynamic ไม่คล่องเท่า Python

## 5. Apache Airflow และ Workflows as Code

**จากเอกสาร (หน้า 41–43)** Airflow เป็น open-source platform สำหรับพัฒนา schedule และ monitor batch workflows DAG เขียนด้วย Python มี schedule, tasks, dependencies, callbacks และ parameters ตัวอย่างใช้ BashOperator กับ @task และกำหนด T2/T3 ให้เสร็จก่อน T4

Airflow เป็น **orchestrator ไม่ใช่ processing engine** Task อาจสั่ง SQL, Spark, shell, API หรือ container อีกที Scheduler ตรวจ DAG runs และ task instances ที่ dependency ครบ แล้วส่งงานให้ executor ตาม [Airflow Scheduler documentation](https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/scheduler.html) ดังนั้น Airflow ไม่ได้ทำ SQL หรือ Spark ให้เร็วขึ้นโดยตรง แต่ทำให้การประสานงาน ตรวจสถานะ retry และ backfill เป็นระบบ

### 5.1 อ่าน cron expression

0 0 * * * มีห้าช่อง: minute, hour, day-of-month, month, day-of-week จึงหมายถึงเวลา 00:00 ทุกวันตาม timezone ที่ DAG/environment กำหนด แต่ schedule เวลาเที่ยงคืนไม่ได้แปลว่า data พร้อมแล้ว ต้องพิจารณา upstream SLA และ data interval

### 5.2 กลไกการรัน

1. DAG file ถูก parse เพื่อสร้าง tasks/dependencies
2. Scheduler สร้าง DAG run ตาม timetable หรือ trigger
3. Scheduler ตรวจ task ที่ dependency ครบและ concurrency อนุญาต
4. Executor/worker รับ task ไปทำงาน
5. Task รายงาน success, failed, retry หรือ skipped
6. Downstream พร้อมเมื่อ trigger rule และ upstream states ตรงเงื่อนไข

Retry ช่วย transient failure แต่ task ต้อง **idempotent** คือรันซ้ำแล้วไม่สร้างยอดหรือ publish ซ้ำ วิธีที่ใช้ได้คือเขียน staging partition แล้ว replace, ใช้ deterministic key/upsert และบันทึก run identifier

## 6. Oozie หรือ Airflow?

| เกณฑ์ | Oozie | Airflow |
|---|---|---|
| นิยาม workflow | XML | Python |
| ความถนัดหลัก | Hadoop-native jobs | เชื่อมหลายแพลตฟอร์ม |
| Dynamic authoring | จำกัดกว่า | ยืดหยุ่น แต่เสี่ยง DAG code ซับซ้อน |
| เหมาะกับ | ระบบ Hadoop เดิม | Modern multi-system platform |

ไม่ควรย้ายเพียงเพราะเครื่องมือหนึ่งใหม่กว่า ต้องประเมิน test coverage, backfill, alerting, secrets, access control, operating skill และ migration risk

## 7. Guided Design Lab

ออกแบบ daily sales pipeline: ingest CSV → ตรวจ schema และยอดรวม → aggregate รายสาขา → publish dashboard

1. ให้ schema check กับ amount check รันขนาน
2. กำหนด Aggregate ให้รอทั้งสอง checks
3. retry 2 ครั้งเฉพาะ transient failures
4. publish แบบ idempotent โดยใช้ business_date เป็น partition/key
5. จงใจให้ amount check ล้ม; Aggregate/Publish ต้องไม่รัน
6. แก้ข้อมูลและ rerun แล้วตรวจว่าปลายทางไม่มีข้อมูลซ้ำ

**Validation:** source count = accepted + rejected, aggregate total = accepted total, partition date ตรง data interval และ rerun ให้ผลธุรกิจเดิม

## 8. Likely Exam Focus และคำถามทบทวน

- อธิบาย HashPartitioner และเหตุที่จำนวน keys สมดุลไม่ได้แปลว่า workload สมดุล
- วิเคราะห์ skew และเลือก salting/pre-aggregation/custom partitioner
- วาด sequential/parallel DAG และอธิบาย fork/join
- เปรียบเทียบ Oozie กับ Airflow ตามบริบท
- แปล cron พร้อมอธิบาย retry และ idempotency

**ถาม:** Airflow task success พิสูจน์ว่าข้อมูลถูกต้องหรือไม่?  
**ตอบ:** ไม่ พิสูจน์เพียงว่า process จบ ต้องมี quality assertions เช่น count, totals, uniqueness และ freshness

**ถาม:** retry publish แล้วข้อมูลซ้ำ แก้อย่างไร?  
**ตอบ:** ทำ side effect ให้ idempotent ด้วย upsert/replace partition หรือ transaction ที่ใช้ deterministic key

**Analyze:** มี reducers 20 ตัวแต่ UNKNOWN key มีข้อมูล 70% เหตุใด job ยังช้า?  
**เฉลย:** ความสมดุลของจำนวน keys ไม่เท่าความสมดุลของ values/work UNKNOWN ยังถูกส่งไป reducer เดียว วิธีแก้ต้องเปลี่ยน distribution เช่น pre-aggregate หรือ salt แล้วรวมรอบสอง พร้อม validate total หลัง unsalt

**Evaluate:** ควรย้าย Oozie workflow ที่เสถียรไป Airflow ทันทีหรือไม่?  
**แนวคำตอบ:** ไม่ตัดสินจากความใหม่ ต้องเทียบ integration, SLA, skills, test/backfill coverage, security, observability และ migration risk ถ้า workflow ยัง Hadoop-native และดูแลได้ Oozie อาจคุ้มกว่า; หากต้องเชื่อมหลาย platforms และทีมพร้อม Python Airflow อาจให้ประโยชน์มากกว่า

## 9. Validation, Failure Behavior และ Troubleshooting

| อาการ | สาเหตุที่เป็นไปได้ | หลักฐาน/ทางแก้ |
|---|---|---|
| DAG ไม่เริ่ม | schedule/timezone/start date | logical date และ scheduler log |
| downstream ไม่รัน | upstream state/trigger rule | task instance graph |
| retry แล้วข้อมูลซ้ำ | task ไม่ idempotent | business key และ target rows |
| workflow จบแต่ยอดผิด | ไม่มี data-quality gate | counts/totals/reconciliation |
| reducer ท้ายสุดค้าง | skew ไม่ใช่ scheduler | key distribution/task duration |

## 10. Mastery Checklist

- [ ] วาด DAG ที่มี parallel branches และ join ได้
- [ ] อธิบาย task lifecycle และจุดที่ retry เกิดได้
- [ ] แปล cron พร้อม timezone caveat
- [ ] ออกแบบ task ให้ rerun แล้วผลไม่ซ้ำ
- [ ] แยก orchestration ออกจาก processing
- [ ] วินิจฉัย data skew จาก distribution/task duration

## 11. Glossary และ Source Coverage

| คำ | ความหมาย |
|---|---|
| DAG | กราฟ dependency มีทิศทางและไม่มีวงจร |
| Fork/Join | เปิด branches ขนานและรอรวมก่อนเดินต่อ |
| Backfill | รัน workflow ย้อนสำหรับช่วงข้อมูลในอดีต |
| Idempotent | รันซ้ำแล้วผลธุรกิจสุดท้ายไม่เปลี่ยน/ไม่ซ้ำ |
| Trigger rule | เงื่อนไขสถานะ upstream ที่อนุญาต downstream |

ครอบคลุม PDF หน้า 39 เรื่อง Partitioner/skew/job chaining และหน้า 40–43 เรื่อง Oozie/Airflow/DAG/cron/operators ไม่มีหัวข้อจากหน้า 38 ที่ย้ายข้ามโดยไม่อ้างอิง; Combiner มีบ้านหลักในบทที่ 3

## 12. References

- เอกสารหลัก หน้า 39–43
- [Apache Oozie Workflow Functional Specification](https://oozie.apache.org/docs/5.2.1/WorkflowFunctionalSpec.html)
- [Apache Airflow DAGs](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html)
- [Apache Airflow Scheduler](https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/scheduler.html)
