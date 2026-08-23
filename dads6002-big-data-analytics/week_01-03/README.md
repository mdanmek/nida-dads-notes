# DADS6002 Big Data Analytics: Hadoop (สัปดาห์ 01–03)

ชุด Master Notes ภาษาไทยจาก dads6002_week01-03_hadoop.pdf จำนวน 43 หน้า จัดเป็นบทเรียนสำหรับผู้เริ่มต้น โดยแยกตาม learning units เพื่อให้แต่ละหัวข้อมีคำอธิบาย กลไก ตัวอย่าง failure/trade-off และแบบฝึกหัดครบถ้วน

## ลำดับการเรียน

1. [บทที่ 1: Big Data Foundations, Workflow และ Data Lake](01_big_data_foundations.md) — หน้า 1–10
2. [บทที่ 2: Hadoop Architecture, HDFS และ YARN](02_hdfs_and_yarn.md) — หน้า 11–21
3. [บทที่ 3: MapReduce, Hadoop Streaming และการปรับประสิทธิภาพ](03_mapreduce_and_streaming.md) — หน้า 22–38
4. [บทที่ 4: Partitioner, Job Chaining และ Workflow Orchestration](04_workflow_orchestration.md) — หน้า 39–43

| บท | ผลลัพธ์หลังเรียน |
|---|---|
| 1 | แปลง 5Vs/SLA เป็น workflow, Lambda และ Data Lake design |
| 2 | trace HDFS/YARN mechanisms และวิเคราะห์ failure/storage overhead |
| 3 | รันและ debug MapReduce Streaming พร้อมออกแบบ key/Combiner |
| 4 | แก้ skew และออกแบบ DAG/retry/idempotency |

ฉบับ [hadoop.md](hadoop.md) เป็น Master Note แบบไฟล์เดียวที่เก็บไว้เพื่อรักษาลิงก์เดิม ส่วนชุด 4 บทด้านบนเป็นลำดับอ่านที่แนะนำ

## Cumulative Learning Objectives

- เชื่อม 5Vs กับข้อกำหนด storage, latency, quality และ value
- ออกแบบ workflow และเลือก batch/speed layer ตาม SLA
- ติดตาม HDFS write/read/failure recovery
- อธิบาย YARN application lifecycle
- ติดตาม record ผ่าน Map, partition, shuffle, sort และ reduce
- เขียนและ debug Hadoop Streaming ด้วย Python
- วิเคราะห์ Combiner, Partitioner, skew และ network cost
- ออกแบบ DAG ที่ retry/backfill/rerun อย่าง idempotent

## Prerequisite และ Dependency Map

บทที่ 1 เป็นฐานเรื่อง workflow/latency → บทที่ 2 เพิ่ม storage/resource mechanisms → บทที่ 3 ใช้ HDFS/YARN เพื่ออธิบาย distributed computation → บทที่ 4 นำ jobs หลายชุดมา orchestration ดังนั้นควรอ่านตามลำดับ 1 → 2 → 3 → 4 หากต้องทบทวนเฉพาะสอบ ให้เริ่มจาก objectives/mastery checklist ของบท แล้วกลับไป worked examples ที่ยังอธิบายไม่ได้

## แผนขอบเขตและระดับความลึก

| ระดับ | หัวข้อ |
|---|---|
| Core | HDFS, YARN, MapReduce flow, Streaming code, Combiner/Partitioner, workflow DAG |
| Supporting | Data types, 5Vs, Data Product, Lambda Architecture, Data Lake, ecosystem |
| Reference | CLI commands, ecosystem tool names, cron/operator syntax |

## Source Coverage Audit

| หน้า PDF | เนื้อหา | บท |
|---:|---|---|
| 1–4 | Data types, 5Vs, Data Product, Data Science Pipeline | 1 |
| 5–10 | Big Data Workflow, Lambda Architecture, Data Lake | 1 |
| 11–16 | Hadoop ecosystem, requirements, architecture | 2 |
| 17–21 | HDFS, YARN, blocks, access และ CLI | 2 |
| 22–28 | MapReduce model และ Word Count | 3 |
| 29–32 | Shared Friendship | 3 |
| 33–38 | Jobs, Streaming, Python และ Combiners | 3 |
| 39 | Partitioner, skew และ Job Chaining | 4 |
| 40–43 | Oozie, Airflow, DAG, cron และ operators | 4 |

ตรวจ text layer และภาพครบหน้า 1–43 แล้ว ไม่มีส่วนที่อ่านไม่ได้จนต้องคาดเดา โค้ด Python ในเอกสารมี syntax/formatting ที่รันไม่ได้บางจุด จึงรักษาแนวคิดเดิมและให้ฉบับแก้ไขในบทที่ 3

## Integrated Capstone: Reliable Pharmacy Sales Pipeline

### สถานการณ์

ร้านยา 100 สาขาส่งยอดขายและ cancellation events ต้องมี dashboard ภายใน 5 นาที รายงานปิดวันต้องตรง Finance และต้อง rerun วันที่ผิดได้โดยไม่ซ้ำ

### งานที่ต้องส่ง

1. วิเคราะห์ 5Vs และกำหนด SLA/data-quality requirements (บท 1)
2. ออกแบบ raw/validated/curated zones และ HDFS blocks/replication สำหรับไฟล์รายวัน (บท 1–2)
3. trace ไฟล์หนึ่งผ่าน HDFS write/read และ YARN application (บท 2)
4. ออกแบบ MapReduce key เป็น `(business_date, branch_id)` พร้อม Streaming pseudocode และ validation totals (บท 3)
5. วิเคราะห์ hot key เช่น `branch_id=UNKNOWN` และเสนอ pre-aggregation/salting (บท 4)
6. วาด DAG ingest → validations ขนาน → aggregate → reconcile → publish พร้อม retry/backfill/idempotency (บท 4)
7. จำลอง DataNode failure, malformed mapper output และ publish retry แล้วอธิบาย detection/recovery

### Rubric 20 คะแนน

| ด้าน | คะแนน | หลักฐาน |
|---|---:|---|
| Architecture/เหตุผล | 5 | component ตรง SLA และมี trade-off |
| Correctness/validation | 5 | counts, totals, key grain, reconciliation |
| Reliability | 4 | replication, retry, idempotency, recovery |
| Execution/diagnosis | 4 | runnable local test และ failure evidence |
| Communication | 2 | diagram, assumptions และข้อจำกัดชัดเจน |

## Cumulative Exam Blueprint

| Objective | Recall/Explain | Apply/Analyze | Evaluate/Create | หลักฐาน |
|---|---|---|---|---|
| Workflow/Lambda/Lake | นิยาม layers/5Vs | วิเคราะห์ late data | เลือก architecture | บท 1 Lab/Transfer |
| HDFS/YARN | อธิบาย components | คำนวณ/trace failure | เลือก replication/EC | บท 2 Paper Lab |
| MapReduce/Streaming | อธิบาย stages | run/debug/key design | ประเมิน Combiner/idempotency | บท 3 Lab |
| Skew/Orchestration | อธิบาย DAG/cron | diagnose skew/retry | เลือก Oozie/Airflow | บท 4 Design Lab |
| Integration | เชื่อม terminology | trace end-to-end | สร้าง reliable pipeline | Capstone |

## Final Revision Checklist

- [ ] วาด HDFS write/read และ YARN lifecycle จากความจำ
- [ ] คำนวณ blocks/replication โดยไม่สับสน logical capacity กับ payload
- [ ] trace Word Count และ Shared Friendship ทุก intermediate stage
- [ ] รัน local Streaming และซ่อม 3 planted failures ได้
- [ ] อธิบาย average-of-averages และ skew ด้วย counterexample
- [ ] วาด DAG ที่มี fork/join, retry, validation gate และ idempotent publish
- [ ] ตอบ scenario โดยระบุ assumptions, trade-offs, validation และ failure recovery

## Suite Integrity Audit

- แต่ละ source topic มี primary home ตามตาราง Coverage และใช้ cross-link เมื่อเชื่อมบท
- Chapter objectives เป็นคนละชุดและรวมกันเท่ากับ cumulative objectives
- คำศัพท์ block/split/container/task/DAG ใช้ความหมายสม่ำเสมอ
- Assessments ครอบคลุม Core objectives ทั้ง Explain, Apply, Analyze และ Evaluate/Create
- Capstone เชื่อม source-to-storage-to-compute-to-orchestration และมี failure/validation evidence
- ไม่พบส่วนอ่านไม่ได้หรือ ambiguity ที่ต้องคาดเดา; ความคลาดเคลื่อนของโค้ดต้นฉบับถูกระบุในบท 3

## References หลัก

- [Apache Hadoop Documentation](https://hadoop.apache.org/docs/current/)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/apache-airflow/stable/)
- [Apache Oozie Documentation](https://oozie.apache.org/docs/5.2.1/)
- [Google Research: The Google File System](https://research.google/pubs/the-google-file-system/)
- [Google Research: MapReduce](https://research.google/pubs/mapreduce-simplified-data-processing-on-large-clusters/)
