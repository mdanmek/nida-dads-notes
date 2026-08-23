# DADS6002 Big Data Analytics: Hadoop (สัปดาห์ 01–03)

ชุด Master Notes ภาษาไทยจาก dads6002_week01-03_hadoop.pdf จำนวน 43 หน้า จัดเป็นบทเรียนสำหรับผู้เริ่มต้น โดยแยกตาม learning units เพื่อให้แต่ละหัวข้อมีคำอธิบาย กลไก ตัวอย่าง failure/trade-off และแบบฝึกหัดครบถ้วน

## ลำดับการเรียน

1. [บทที่ 1: Big Data Foundations, Workflow และ Data Lake](01_big_data_foundations.md) — หน้า 1–10
2. [บทที่ 2: Hadoop Architecture, HDFS และ YARN](02_hdfs_and_yarn.md) — หน้า 11–21
3. [บทที่ 3: MapReduce, Hadoop Streaming และการปรับประสิทธิภาพ](03_mapreduce_and_streaming.md) — หน้า 22–38
4. [บทที่ 4: Partitioner, Job Chaining และ Workflow Orchestration](04_workflow_orchestration.md) — หน้า 39–43

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

## References หลัก

- [Apache Hadoop Documentation](https://hadoop.apache.org/docs/current/)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/apache-airflow/stable/)
- [Apache Oozie Documentation](https://oozie.apache.org/docs/5.2.1/)
- [Google Research: The Google File System](https://research.google/pubs/the-google-file-system/)
- [Google Research: MapReduce](https://research.google/pubs/mapreduce-simplified-data-processing-on-large-clusters/)
