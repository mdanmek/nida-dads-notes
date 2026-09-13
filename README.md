# NIDA DADS Notes

คลังบันทึกการเรียน โค้ด แบบฝึกหัด และโครงงานของหลักสูตรปริญญาโท **Data Analytics and Data Science (DADS)** สถาบันบัณฑิตพัฒนบริหารศาสตร์ (NIDA)

Repository นี้จัดทำขึ้นเพื่อรวบรวมเนื้อหาแต่ละรายวิชาให้อ่านทบทวนได้จากที่เดียว โดยโน้ตในโฟลเดอร์ `summary/` เน้นการอธิบายแนวคิดตั้งแต่พื้นฐาน เชื่อมโยงกับตัวอย่างจาก Lecture และ Lab และใช้สำหรับเตรียมสอบ

## รายวิชา

| รหัสวิชา | รายวิชา | เนื้อหาที่มีในปัจจุบัน |
|---|---|---|
| [DADS5001](dads5001-data-tools/) | Data Tools and Programming | Pandas, Matplotlib, Seaborn และโครงงาน EDA |
| [DADS6001](dads6001-applied_statistics/) | Applied Modern Statistical Analytics | Statistical foundations, interval estimation, resampling และ hypothesis testing |
| [DADS6002](dads6002-big-data-analytics/) | Big Data Analytics | Hadoop, HDFS, YARN, MapReduce, Hive และ HBase |
| [DADS6003](dads6003-applied_ml/) | Applied Machine Learning | Linear regression, logistic regression, Naive Bayes, regularization และ model evaluation |

## เริ่มอ่านจากที่ไหน

- [DADS5001 — Study Notes](dads5001-data-tools/summary/)
- [DADS6001 — Study Notes Index](dads6001-applied_statistics/summary/00_readme.md)
- [DADS6002 — Study Notes Index](dads6002-big-data-analytics/summary/000_readme.md)
- [DADS6003 — Study Notes](dads6003-applied_ml/summary/)

## โครงสร้าง Repository

```text
nida-dads-notes/
├── dads5001-data-tools/
│   ├── lecture/
│   ├── lab/
│   ├── resource/
│   ├── summary/
│   └── project/
├── dads6001-applied_statistics/
│   ├── lecture/
│   ├── lab/
│   ├── read/
│   └── summary/
├── dads6002-big-data-analytics/
│   ├── lecture/
│   ├── lab/
│   └── summary/
└── dads6003-applied_ml/
    ├── lecture/
    ├── lab/
    ├── read/
    └── summary/
```

## ความหมายของแต่ละโฟลเดอร์

| โฟลเดอร์ | วัตถุประสงค์ |
|---|---|
| `lecture/` | เอกสารและสื่อประกอบการบรรยาย |
| `lab/` | Notebook, โค้ด และเอกสารปฏิบัติการ |
| `read/` | เอกสารอ่านเพิ่มเติมและกรณีศึกษา |
| `resource/` | Dataset หรือไฟล์ที่ใช้ประกอบการฝึก |
| `summary/` | Master study notes ภาษาไทยสำหรับทำความเข้าใจและเตรียมสอบ |
| `project/` | พื้นที่รวมโครงงานของรายวิชา แยกตามประเภทของโครงงาน |

บางรายวิชาอาจไม่มีทุกโฟลเดอร์ โดยขึ้นอยู่กับรูปแบบเนื้อหาและงานของรายวิชานั้น

## แนวทางการตั้งชื่อ

- ชื่อ repository และโฟลเดอร์หลักใช้ตัวพิมพ์เล็ก โดยคั่นคำด้วย `-`
- ชื่อไฟล์ โค้ด และตัวแปรใช้ `lower_case_with_underscore`
- ไฟล์โน้ตขึ้นต้นด้วยลำดับหัวข้อ เช่น `01_introduction.md`
- ไฟล์ที่เป็นสารบัญของรายวิชาใช้ชื่อ `00_readme.md` หรือชื่อเดิมที่กำหนดไว้ในรายวิชานั้น
- ชื่อไฟล์ควรสื่อความหมายและสอดคล้องกับลำดับเนื้อหาหรือโครงงาน

## แนวทางการใช้ Repository

1. เริ่มจากสารบัญหรือโฟลเดอร์ `summary/` ของรายวิชา
2. อ่าน Master Note เพื่อทำความเข้าใจภาพรวม แนวคิด ตัวอย่าง และประเด็นเตรียมสอบ
3. เปิดไฟล์ใน `lab/` เพื่อลองรันโค้ดและตรวจสอบผลลัพธ์ด้วยตนเอง
4. ใช้ `lecture/` และ `read/` เป็นแหล่งอ้างอิงเพิ่มเติม
5. ใช้ `project/` เพื่อติดตามการวางแผน การพัฒนา และการปรับปรุงโครงงานแต่ละประเภท

## หมายเหตุ

Repository นี้เป็นบันทึกเพื่อการศึกษา เนื้อหาใน Master Notes เป็นการเรียบเรียงเพื่อช่วยทำความเข้าใจ ไม่ใช่เอกสารทางการของรายวิชา โปรดตรวจสอบประกาศ เอกสาร และข้อกำหนดล่าสุดจากผู้สอนประกอบเสมอ
