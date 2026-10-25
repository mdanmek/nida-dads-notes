# Machine Learning with Spark: จากข้อมูลจำนวนมากสู่โมเดลที่นำไปทำนายได้

> บทนี้เรียบเรียงจาก lecture_07_machine_learning.pdf ทั้ง 51 หน้า เนื้อหาครอบคลุมพื้นฐาน Machine Learning, MLlib แบบ RDD, regression, classification, clustering, recommendation, model evaluation และ ML Pipeline แบบ DataFrame โดยอธิบาย API เก่าเพื่อให้อ่านสไลด์ได้ และใช้ DataFrame-based API เป็นแนวทางหลักสำหรับงานใหม่

## 1. Machine Learning กำลังเรียนรู้อะไรจากข้อมูล

Machine Learning คือกระบวนการค้นหารูปแบบหรือความสัมพันธ์จากข้อมูล แล้วเก็บสิ่งที่เรียนรู้ไว้ในรูปของ **model** ตัว model ไม่ใช่ข้อมูลดิบทั้งหมด แต่เป็นกฎ พารามิเตอร์ หรือโครงสร้างที่สรุปความสัมพันธ์และนำไปใช้กับข้อมูลใหม่ได้

สมมติโรงพยาบาลมีข้อมูลใบสั่งซื้อย้อนหลัง แต่ละรายการมีราคาต่อหน่วย ปริมาณ ระยะเวลาส่งมอบ ประเภทสินค้า และสถานะว่าส่งล่าช้าหรือไม่ หากต้องการทำนายว่าใบสั่งซื้อใหม่มีโอกาสล่าช้าหรือไม่ คอลัมน์ที่ใช้เป็นข้อมูลประกอบเรียกว่า **features** ส่วนคำตอบที่ต้องการทำนายเรียกว่า **label**

~~~mermaid
flowchart LR
    D["ข้อมูลย้อนหลัง"] --> F["Features และ Label"]
    F --> T["Learning Algorithm ฝึกโมเดล"]
    T --> M["Model ที่เรียนรู้รูปแบบ"]
    N["ข้อมูลใหม่ที่มี Features"] --> M
    M --> P["Prediction"]
~~~

Machine Learning ไม่ได้หมายความว่าโมเดลค้นพบเหตุและผลเสมอไป ส่วนใหญ่โมเดลเรียนรู้ความสัมพันธ์ที่ช่วยทำนาย หากข้อมูลมีอคติ ขาดตัวแปรสำคัญ หรือแตกต่างจากสภาพที่นำโมเดลไปใช้ ผลทำนายก็อาจผิดแม้คะแนนบนข้อมูลเก่าจะดูดี

## 2. Supervised และ Unsupervised Learning

การแบ่งประเภทขั้นแรกดูว่าข้อมูลฝึกมีคำตอบกำกับหรือไม่

**Supervised learning** ใช้ข้อมูลที่มี label เช่นยอดขายจริง ราคาจริง หรือสถานะล่าช้าจริง โมเดลเรียนรู้ความสัมพันธ์ระหว่าง independent variables หรือ features กับ dependent variable หรือ label จากนั้นใช้ทำนาย label ของข้อมูลใหม่

**Unsupervised learning** ใช้ข้อมูลที่ไม่มี label ให้ทำนาย ระบบค้นหาโครงสร้างที่ซ่อนอยู่ เช่นกลุ่มลูกค้าที่มีพฤติกรรมคล้ายกัน หรือรายการที่ผิดปกติจากข้อมูลส่วนใหญ่ ผลลัพธ์จึงไม่มี “คำตอบจริง” ให้เทียบโดยตรงเหมือน supervised learning และต้องอาศัยทั้งตัวชี้วัดกับความหมายทางธุรกิจในการตีความ

| ประเภทงาน | สิ่งที่ต้องการ | ตัวอย่าง |
|---|---|---|
| Classification | ทำนาย class label | ส่งตรงเวลา/ล่าช้า, ปกติ/ทุจริต |
| Regression | ทำนายค่าตัวเลขต่อเนื่อง | ราคาหรือระยะเวลาส่งมอบ |
| Clustering | แบ่งข้อมูลเป็นกลุ่มที่คล้ายกัน | แบ่งโรงพยาบาลตามรูปแบบการใช้ยา |
| Anomaly detection | หารายการที่แตกต่างผิดปกติ | ปริมาณสั่งซื้อสูงผิดจากประวัติ |
| Recommendation | ทำนายความชอบหรือความเกี่ยวข้อง | แนะนำสินค้าให้ผู้ใช้ |
| Dimension reduction | ลดจำนวนมิติโดยรักษาสาระสำคัญ | ย่อ features จำนวนมากเพื่อวิเคราะห์ |

Features อาจเป็น categorical เช่นประเภทสินค้า ระดับความเร่งด่วน และ numerical เช่นราคา ปริมาณ หรือจำนวนวัน Numerical feature ยังแบ่งเป็น discrete เช่นจำนวนครั้ง และ continuous เช่นน้ำหนักหรือเวลา

## 3. Training Data และ Test Data

หากฝึกโมเดลและประเมินด้วยข้อมูลชุดเดียวกัน โมเดลอาจจำรายละเอียดของข้อมูลฝึกจนดูเหมือนทำงานดี แต่ใช้กับข้อมูลใหม่ไม่ได้ ปัญหานี้เรียกว่า **overfitting**

จึงต้องแยกข้อมูลอย่างน้อยเป็นสองส่วน

- **Training data** ใช้เรียนรู้พารามิเตอร์ของโมเดล
- **Test data** เก็บไว้ประเมินโมเดลหลังฝึกเสร็จ

~~~mermaid
flowchart TD
    A["ข้อมูลที่มี Label"] --> B["แบ่งข้อมูล"]
    B --> C["Training Data"]
    B --> D["Test Data"]
    C --> E["fit โมเดล"]
    E --> F["โมเดลที่ฝึกแล้ว"]
    D --> G["ข้อมูลที่โมเดลยังไม่เห็น"]
    F --> G
    G --> H["Prediction เทียบ Label จริง"]
~~~

Test data ต้องไม่รั่วเข้าไปในขั้นตอนเลือก feature, scaling หรือปรับ hyperparameters มิฉะนั้นคะแนนจะมองโลกในแง่ดีเกินจริง ในงานที่ต้องปรับโมเดลควรมี validation set หรือใช้ cross-validation และเก็บ test set ไว้ตรวจครั้งสุดท้าย

ถ้าข้อมูลมีลำดับเวลา เช่นทำนายเดือนถัดไป การสุ่มแบ่งอาจทำให้ข้อมูลอนาคตไหลย้อนเข้า training ควรแบ่งตามเวลาให้โมเดลฝึกจากอดีตและทดสอบกับช่วงที่ใหม่กว่า

## 4. Machine Learning ใน Spark

Spark มี MLlib ซึ่งรวม algorithms, feature transformation, evaluation, pipelines และ utilities สำหรับงาน Machine Learning แบบกระจาย สไลด์แยกเป็นสอง API

1. **spark.mllib** ใช้ RDD และ data types เช่น Vector, LabeledPoint และ Rating
2. **spark.ml** ใช้ DataFrame และ Pipeline API

เอกสาร Apache Spark ปัจจุบันกำหนดให้ DataFrame-based API ใน spark.ml เป็น API หลัก ส่วน spark.mllib แบบ RDD อยู่ใน maintenance mode คือยังแก้ข้อผิดพลาดแต่ไม่เน้นเพิ่มความสามารถใหม่ ([MLlib Guide](https://spark.apache.org/docs/latest/ml-guide.html)).

บทนี้ยังอธิบาย spark.mllib เพราะเป็นเนื้อหาส่วนใหญ่ของสไลด์และช่วยให้เข้าใจ data representation แต่เมื่อเริ่มโครงการใหม่ควรใช้ spark.ml เป็นค่าเริ่มต้น เพราะเชื่อมกับ Spark SQL, Schema และ Pipeline ได้โดยตรง

## 5. จากหนึ่ง Observation ไปเป็น Vector

โมเดลจำนวนมากไม่ได้รับ columns แยกกัน แต่รับ features ของหนึ่ง observation รวมเป็น **vector** หากมี features n ตัว observation หนึ่งจึงเป็นจุดหนึ่งในปริภูมิ n มิติ

ตัวอย่างผู้ขายหนึ่งรายมี features สามตัว ได้แก่ราคาเฉลี่ย ระยะเวลาส่งมอบ และอัตราส่งล่าช้า

$$
mathbf{x} = [120.5, 7, 0.08]
$$

Vector มี index เริ่มจากศูนย์และเก็บค่าแบบ Double ใน MLlib มีสองรูปแบบหลัก

### Dense Vector

Dense vector เก็บทุกค่า เหมาะเมื่อ features ส่วนใหญ่ไม่เป็นศูนย์

~~~python
from pyspark.ml.linalg import Vectors

dense_vec = Vectors.dense([1.0, 2.0, 3.0])
~~~

### Sparse Vector

Sparse vector เก็บเฉพาะ index และค่าที่ไม่เป็นศูนย์ เหมาะกับ feature space ขนาดใหญ่ที่มีศูนย์จำนวนมาก เช่น text features ซึ่งเอกสารหนึ่งมีคำเพียงส่วนน้อยจากคลังคำทั้งหมด

~~~python
sparse_vec = Vectors.sparse(
    4,
    [1, 3],
    [1.0, 5.5],
)
~~~

Vector นี้มีขนาด 4 และเทียบเท่า [0.0, 1.0, 0.0, 5.5] การใช้ sparse vector ลดพื้นที่จัดเก็บและการคำนวณที่ไม่จำเป็น แต่ถ้าข้อมูลแทบไม่มีศูนย์ โครงสร้าง sparse อาจเพิ่ม overhead โดยไม่เกิดประโยชน์

## 6. LabeledPoint และ Rating ใน API แบบ RDD

**LabeledPoint** รวม label กับ feature vector ของหนึ่ง observation

~~~python
from pyspark.mllib.linalg import SparseVector
from pyspark.mllib.regression import LabeledPoint

positive = LabeledPoint(1.0, [1.0, 0.0, 3.0])
negative = LabeledPoint(
    0.0,
    SparseVector(3, [0, 2], [1.0, 3.0]),
)
~~~

สำหรับ regression label เป็นค่าตัวเลขที่ต้องการทำนาย สำหรับ binary classification นิยมแทน class ด้วย 0.0 และ 1.0 ส่วน multiclass ใช้ class index 0.0, 1.0, 2.0 ต่อกัน

**Rating** ใช้กับ recommendation แบบเก่า ประกอบด้วย user id, product id และ rating

~~~python
from pyspark.mllib.recommendation import Rating

rating = Rating(100, 10, 3.0)
~~~

ใน spark.ml ข้อมูลเหล่านี้อยู่ใน DataFrame โดยทั่วไปมีคอลัมน์ label, features หรือ user, item, rating จึงอ่านและเชื่อมกับขั้นตอนอื่นง่ายกว่า

## 7. Regression: ทำนายค่าตัวเลข

Linear regression สมมติว่าค่าที่ทำนายเป็นผลรวมเชิงเส้นของ features

$$
hat{y} = w_0 + mathbf{w}^{T}mathbf{x}
$$

$w_0$ คือ intercept ส่วน $w_j$ คือ coefficient ของ feature ที่ j โมเดลเรียนรู้ coefficients โดยลด loss ระหว่างค่าทำนายกับค่าจริง สำหรับ squared error:

$$
L_i = \frac{1}{2}(\mathbf{w}^{T}\mathbf{x}_i-y_i)^2
$$

และ objective โดยเฉลี่ยคือ

$$
J(\mathbf{w}) = \frac{1}{m}\sum_{i=1}^{m}L_i
$$

หาก coefficient ของ lead time เท่ากับ 2.5 ในโมเดลทำนายต้นทุน ความหมายคือเมื่อ feature อื่นคงที่ lead time เพิ่มหนึ่งหน่วยสัมพันธ์กับค่าทำนายที่เพิ่ม 2.5 หน่วย การตีความนี้ต้องอยู่ภายใต้สมมติฐานของโมเดลและไม่ได้ยืนยันเหตุและผล

### SGD เรียนรู้ coefficient อย่างไร

Stochastic Gradient Descent หรือ SGD ปรับ coefficients ซ้ำไปในทิศทางที่ทำให้ loss ลดลง เหมาะกับข้อมูลขนาดใหญ่เพราะใช้ข้อมูลบางส่วนในแต่ละรอบได้ แต่ผลขึ้นกับ learning rate, จำนวน iterations, feature scaling และความแปรปรวนของการอัปเดต

สไลด์ใช้ LinearRegressionWithSGD จาก spark.mllib ซึ่งเป็น API รุ่นเก่า งานใหม่ใช้ LinearRegression ใน pyspark.ml.regression ที่รับ DataFrame และรองรับ regularization ผ่านพารามิเตอร์

## 8. Overfitting และ Regularization

โมเดลที่ซับซ้อนมากเมื่อเทียบกับจำนวน observations หรือมี features ที่สัมพันธ์กันสูง อาจปรับตัวเข้ากับ noise ของ training data จน training error ต่ำ แต่ test error สูง Regularization เพิ่มบทลงโทษขนาด coefficients เข้าไปใน objective เพื่อควบคุมความซับซ้อน

### Ridge หรือ L2

$$
J(\mathbf{w}) =
\frac{1}{m}\sum_{i=1}^{m}L_i
+ \lambda\sum_{j=1}^{n}w_j^2
$$

L2 กด coefficients ให้เล็กลงและมักไม่ทำให้เป็นศูนย์พอดี เหมาะเมื่อหลาย features มีส่วนช่วยเล็กน้อยหรือมี multicollinearity

### Lasso หรือ L1

$$
J(\mathbf{w}) =
\frac{1}{m}\sum_{i=1}^{m}L_i
+ \lambda\sum_{j=1}^{n}|w_j|
$$

L1 สามารถทำให้ coefficients บางตัวเป็นศูนย์ จึงมีผลคล้าย feature selection แต่ถ้า features ที่สัมพันธ์กันสูง Lasso อาจเลือกบางตัวและตัดอีกตัวอย่างไม่เสถียร

### Elastic Net

Elastic Net ผสม L1 และ L2 โดยใช้ $alpha$ กำหนดสัดส่วน

$$
J(\mathbf{w}) =
\text{Loss}
+ \lambda[
\alpha\sum|w_j|
+ (1-\alpha)\frac{1}{2}\sum w_j^2
]
$$

- $lambda$ หรือ regParam ควบคุมความแรงของ regularization
- $alpha=0$ เป็น L2
- $alpha=1$ เป็น L1
- ค่าระหว่างกลางผสมทั้งสองแบบ

Regularization ไม่ได้แก้ overfitting ทุกกรณี หากข้อมูลรั่ว train/test ต่าง distribution หรือ feature ไม่มีคุณภาพ ต้องแก้กระบวนการข้อมูลและการประเมินร่วมด้วย

## 9. Regression ที่ไม่เป็นเส้นตรง

สไลด์กล่าวถึง Isotonic Regression, Decision Tree, Random Forest และ Gradient-Boosted Trees

**Isotonic regression** เหมาะเมื่อความสัมพันธ์ไม่จำเป็นต้องเป็นเส้นตรง แต่ต้องเป็น monotonic เช่นค่าทำนายไม่ลดลงเมื่อ feature เพิ่มขึ้น

**Decision Tree Regressor** แบ่งข้อมูลด้วยเงื่อนไขเป็นกิ่งและใช้ variance ช่วยเลือก split อ่านง่ายและจับ nonlinearity ได้ แต่ต้นไม้ลึกอาจ overfit

**Random Forest** สร้างต้นไม้หลายต้นจากข้อมูลและ features ที่สุ่มต่างกันแล้วเฉลี่ยผล เป็น bagging ที่ลดความแปรปรวนเมื่อเทียบกับต้นไม้เดียว

**Gradient-Boosted Trees** สร้างต้นไม้ต่อเนื่อง โดยต้นใหม่พยายามแก้ข้อผิดพลาดของ ensemble เดิม มักแม่นยำแต่ต้องปรับ parameters และใช้เวลาฝึกมากกว่า

## 10. Classification: ทำนายกลุ่ม

Classification ทำนาย label ที่เป็นกลุ่ม เช่น 0 = ส่งตรงเวลา และ 1 = ส่งล่าช้า Algorithms ในสไลด์ประกอบด้วย Logistic Regression, SVM, Naive Bayes, Decision Tree, Random Forest และ Gradient-Boosted Trees

Logistic regression ทำนาย probability ก่อนแปลงเป็น class ด้วย threshold จึงให้ข้อมูลมากกว่าคำตอบ 0/1 เพียงอย่างเดียว เช่น probability 0.51 กับ 0.99 ถูกจัดเป็น class 1 เหมือนกัน แต่ความมั่นใจต่างกัน

SVM พยายามหา decision boundary ที่มี margin แยก classes มากที่สุด Tree-based models สร้างเงื่อนไขแบ่งข้อมูล ส่วน Naive Bayes ใช้ความน่าจะเป็นภายใต้สมมติฐานแบบมีเงื่อนไข จึงมักใช้กับ text classification

สไลด์ยกตัวอย่าง SVMWithSGD แบบ RDD แล้วคำนวณ training error จุดที่ควรแก้เมื่อใช้จริงคือประเมินบน test data ไม่ใช่ training data เพราะ training error บอกได้เพียงว่าโมเดลเข้ากับข้อมูลที่เคยเห็นเพียงใด

## 11. Clustering และ K-Means

Clustering แบ่ง observations เป็นกลุ่มโดยไม่มี label กำกับ K-Means กำหนดจำนวนกลุ่ม K แล้วทำซ้ำสองขั้น

1. Assign แต่ละจุดให้ centroid ที่ใกล้ที่สุด
2. Update centroid เป็นค่าเฉลี่ยของจุดในกลุ่ม

~~~mermaid
flowchart LR
    A["กำหนด K และ centroid เริ่มต้น"] --> B["Assign จุดไป centroid ที่ใกล้สุด"]
    B --> C["คำนวณ centroid ใหม่"]
    C --> D{"ตำแหน่งคงที่หรือครบ iteration?"}
    D -- "ยัง" --> B
    D -- "ใช่" --> E["ได้ cluster"]
~~~

ตัวชี้วัดในสไลด์คือ Within Set Sum of Squared Errors หรือ WSSSE ซึ่งรวมระยะทางยกกำลังสองระหว่างแต่ละจุดกับ centroid ของกลุ่ม ค่ายิ่งต่ำหมายถึงจุดอยู่ใกล้ศูนย์กลางมากขึ้น แต่เมื่อ K เพิ่ม WSSSE มักลดลงเสมอ จึงไม่ควรเลือก K จากค่าต่ำสุดเพียงอย่างเดียว ต้องพิจารณา elbow, stability และความหมายของกลุ่มด้วย

K-Means เหมาะกับกลุ่มที่มีรูปร่างค่อนข้างกลมและใช้ระยะทางได้อย่างมีความหมาย จึงควร scale numerical features หากหน่วยต่างกันมาก และต้องระวัง outliers กับการกำหนด centroid เริ่มต้น

สไลด์ยังกล่าวถึง Gaussian Mixture สำหรับกลุ่มแบบ probabilistic, LDA สำหรับ topic modeling, Streaming K-Means และ Power Iteration Clustering สำหรับข้อมูลกราฟ

## 12. Recommendation และ User–Item Matrix

ระบบแนะนำพยายามคาดการณ์ความสนใจระหว่าง user กับ item ข้อมูลพื้นฐานมักเขียนเป็น matrix ที่แถวแทน users คอลัมน์แทน items และค่าภายในเป็น rating หรือสัญญาณพฤติกรรม

| User | Item A | Item B | Item C |
|---|---:|---:|---:|
| U1 | 5 | ? | 2 |
| U2 | 4 | 3 | ? |
| U3 | ? | 1 | 5 |

เครื่องหมาย ? คือคู่ user–item ที่ไม่เคยมี interaction ระบบต้องประมาณค่าที่หายแล้วจัดอันดับ items ที่คาดว่า user สนใจ

### Explicit และ Implicit Feedback

**Explicit feedback** คือความชอบที่ผู้ใช้ระบุโดยตรง เช่นคะแนน 1–5 ดาว ส่วน **implicit feedback** สังเกตจากพฤติกรรม เช่นคลิก ดู ซื้อ หรือเวลาที่ใช้ ข้อมูล implicit เก็บได้มากกว่าแต่ไม่ได้แปลว่าชอบเสมอไป การไม่คลิกอาจเกิดจากผู้ใช้ไม่เคยเห็น item นั้น

### Memory-based Collaborative Filtering

User-based collaborative filtering หาผู้ใช้ที่มีรูปแบบ rating คล้าย user เป้าหมาย แล้วใช้ rating ของเพื่อนบ้านช่วยทำนาย Item-based เปรียบเทียบความคล้ายระหว่าง items แล้วดูว่า user เคยชอบ items ใกล้เคียงหรือไม่

ความคล้ายวัดได้ด้วย Pearson correlation หรือ cosine similarity

$$
\cos(\mathbf{a},\mathbf{b}) =
\frac{\mathbf{a}\cdot\mathbf{b}}
{\|\mathbf{a}\|\|\mathbf{b}\|}
$$

Cosine วัดมุมระหว่าง vectors ไม่ได้พิจารณาขนาดโดยตรง ส่วน Pearson สนใจรูปแบบการเบี่ยงจากค่าเฉลี่ย การเลือกต้องสัมพันธ์กับความหมายของข้อมูลและการจัดการ missing values

## 13. Model-based Recommendation ด้วย ALS

ALS หรือ Alternating Least Squares แยก user–item matrix $R$ เป็น latent factor matrices สองชุด

$$
R \approx U P^T
$$

$U$ เก็บ factors ของ users และ $P$ เก็บ factors ของ items จำนวน latent factors คือ rank ซึ่งมีค่าน้อยกว่าจำนวน users และ items มาก

ALS ทำงานแบบสลับกัน

1. กำหนดค่าเริ่มต้นให้ item factors
2. ตรึง item factors แล้วแก้ user factors ด้วย regularized least squares
3. ตรึง user factors แล้วแก้ item factors
4. ทำซ้ำจนหยุดตามเกณฑ์

~~~mermaid
flowchart TD
    R["Observed user–item interactions"] --> P["กำหนด Item Factors"]
    P --> U["ตรึง P แล้วหา User Factors U"]
    U --> P2["ตรึง U แล้วปรับ Item Factors P"]
    P2 --> C{"ครบ iteration หรือยัง?"}
    C -- "ยัง" --> U
    C -- "ครบ" --> M["ใช้ U และ P ทำนายค่าที่หาย"]
~~~

พารามิเตอร์สำคัญคือ rank, maxIter, regParam และในกรณี implicit feedback มี implicitPrefs กับ alpha เอกสาร Spark ปัจจุบันอธิบายว่า implicit feedback ถูกมองเป็นความแรงของ observation และความมั่นใจ ไม่ใช่ rating ที่ผู้ใช้ให้โดยตรง ([Collaborative Filtering](https://spark.apache.org/docs/latest/ml-collaborative-filtering.html)).

### Cold Start

ผู้ใช้ใหม่หรือสินค้าใหม่ที่ไม่อยู่ใน training data ไม่มี latent factors ให้ ALS ทำนาย เรียกว่า cold-start problem ระบบจริงต้องมี fallback เช่นสินค้ายอดนิยมตามกลุ่ม, content-based recommendation หรือกฎธุรกิจ

### การประเมิน Recommendation

RMSE หรือ MSE วัดความคลาดเคลื่อนของ predicted rating ได้ แต่ระบบแนะนำมักสนใจการจัดอันดับ เช่น Precision@K, Recall@K หรือ ranking metrics เพราะเป้าหมายคือ items อันดับต้นที่ผู้ใช้เห็น ไม่ใช่เพียง rating error เฉลี่ย

## 14. Model Evaluation ต้องตรงกับชนิดปัญหา

### Regression

- **MSE** เฉลี่ย error ยกกำลังสอง จึงลงโทษ error ใหญ่แรง
- **RMSE** ถอดราก MSE ทำให้หน่วยกลับมาเหมือน label
- **MAE** เฉลี่ยค่าสัมบูรณ์ของ error ทนต่อ outlier มากกว่า MSE

$$
MSE = \frac{1}{n}\sum_{i=1}^{n}(y_i-\hat y_i)^2
$$

$$
RMSE = \sqrt{MSE}
$$

$$
MAE = \frac{1}{n}\sum_{i=1}^{n}|y_i-\hat y_i|
$$

### Binary Classification

ROC curve แสดง True Positive Rate เทียบ False Positive Rate เมื่อเปลี่ยน threshold และ AUC สรุปความสามารถในการจัดอันดับ positive เหนือ negative อย่างไรก็ตามเมื่อ positive class หายากมาก ควรดู precision, recall และ Precision–Recall curve เพิ่มเติม

### Multiclass Classification

Precision ตอบว่า prediction ของ class นั้นถูกเท่าใด Recall ตอบว่าตัวอย่างจริงของ class นั้นถูกค้นพบกี่ส่วน และ F1 ผสม precision กับ recall ต้องระบุด้วยว่าเฉลี่ยแบบ macro, weighted หรือ micro เพราะให้ความสำคัญกับ class imbalance ต่างกัน

สิ่งสำคัญคือ metric ต้องสะท้อนต้นทุนของข้อผิดพลาด เช่นระบบแจ้งเตือนยาขาดอาจให้ความสำคัญกับ recall เพื่อไม่พลาดเหตุการณ์ แม้ต้องยอมรับ false alarms เพิ่มขึ้น

## 15. ทำไม ML Pipeline จึงจำเป็น

งาน Machine Learning จริงไม่ได้มีเพียงการ fit algorithm แต่มีขั้นแปลงข้อมูลหลายขั้น เช่นแยกข้อความเป็นคำ แปลงคำเป็น vector ฝึกโมเดล และสร้าง prediction หากเขียนแต่ละขั้นแยกกัน อาจเผลอใช้ preprocessing คนละแบบระหว่าง training กับ test

Spark ML Pipeline เชื่อม stages ให้เป็น workflow เดียว โดยใช้ DataFrame เป็นข้อมูลที่ไหลผ่าน pipeline หนึ่ง DataFrame อาจมีคอลัมน์ text, words, features, label, probability และ prediction อยู่ร่วมกัน

องค์ประกอบหลักมีดังนี้

**Transformer** รับ DataFrame แล้วคืน DataFrame ใหม่ผ่าน transform() มักเพิ่มหรือเปลี่ยนคอลัมน์ เช่น Tokenizer แปลง text เป็น words โมเดลที่ฝึกแล้วก็เป็น Transformer เพราะรับ features แล้วเพิ่ม prediction

**Estimator** รับ DataFrame ผ่าน fit() แล้วผลิต Model ซึ่งเป็น Transformer เช่น LogisticRegression เป็น Estimator ส่วน LogisticRegressionModel เป็น Transformer

**Pipeline** เรียง Transformers และ Estimators เป็น stages ตัว Pipeline เองเป็น Estimator เมื่อ fit แล้วจะให้ PipelineModel ซึ่งเป็น Transformer

~~~mermaid
flowchart LR
    A["DataFrame: text + label"] --> T["Tokenizer transform"]
    T --> W["DataFrame: words"]
    W --> H["HashingTF transform"]
    H --> V["DataFrame: features"]
    V --> L["LogisticRegression fit"]
    L --> M["LogisticRegressionModel"]
~~~

ใน training ขั้น Transformer ใช้ transform ส่วน Estimator ใช้ fit เพื่อสร้าง model เมื่อได้ PipelineModel แล้ว test data จะผ่าน transformations ที่ฝึกหรือกำหนดไว้เหมือนกัน จึงลดความเสี่ยงของ training–serving skew ([ML Pipelines](https://spark.apache.org/docs/latest/ml-pipeline.html)).

## 16. ตัวอย่าง Text Classification Pipeline

~~~python
from pyspark.ml import Pipeline
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.feature import HashingTF, Tokenizer

training = spark.createDataFrame([
    (0, "a b c d e spark", 1.0),
    (1, "b d", 0.0),
    (2, "spark f g h", 1.0),
    (3, "hadoop mapreduce", 0.0),
], ["id", "text", "label"])

tokenizer = Tokenizer(
    inputCol="text",
    outputCol="words",
)

hashing_tf = HashingTF(
    inputCol="words",
    outputCol="features",
)

lr = LogisticRegression(
    maxIter=10,
    regParam=0.001,
)

pipeline = Pipeline(
    stages=[tokenizer, hashing_tf, lr]
)

pipeline_model = pipeline.fit(training)
~~~

ระหว่าง fit ข้อมูลเปลี่ยนรูปร่างดังนี้

| Stage | คอลัมน์ที่อ่าน | คอลัมน์ที่เพิ่ม |
|---|---|---|
| Tokenizer | text | words |
| HashingTF | words | features |
| LogisticRegression | features, label | สร้าง Model |

นำ PipelineModel ไปใช้กับข้อมูลใหม่

~~~python
test = spark.createDataFrame([
    (4, "spark i j k"),
    (5, "l m n"),
    (6, "spark hadoop spark"),
    (7, "apache hadoop"),
], ["id", "text"])

prediction = pipeline_model.transform(test)

prediction.select(
    "id",
    "text",
    "probability",
    "prediction",
).show(truncate=False)
~~~

เมื่อ transform test data จะผ่าน Tokenizer, HashingTF และ LogisticRegressionModel ตามลำดับ ไม่ได้ fit LogisticRegression ใหม่ และ test data ไม่ต้องมี label หากต้องการเพียงทำนาย

## 17. Parameters และการปรับโมเดล

Estimator และ Transformer มี Parameters ในรูปแบบเดียวกัน เช่น maxIter, regParam และ elasticNetParam กำหนดผ่าน constructor, setter หรือ ParamMap ได้

~~~python
lr = LogisticRegression(
    maxIter=10,
    regParam=0.01,
)

model_1 = lr.fit(training)

param_map = {
    lr.maxIter: 20,
    lr.regParam: 0.1,
}

model_2 = lr.fit(training, param_map)
~~~

ParamMap ที่ส่งเข้า fit จะ override ค่าที่กำหนดไว้เดิม การทดลอง parameters หลายชุดไม่ควรเลือกจาก test set ควรใช้ validation หรือ CrossValidator แล้วประเมิน test เพียงครั้งสุดท้าย

## 18. สิ่งที่ Spark ช่วยและสิ่งที่ Spark ไม่ได้แก้แทน

Spark ช่วยกระจายการแปลง features การฝึก algorithms ที่รองรับ และการประเมินข้อมูลขนาดใหญ่ Pipeline ช่วยจัดขั้นตอนให้ใช้ซ้ำและลดความไม่สอดคล้องระหว่าง training กับ prediction

แต่ Spark ไม่ได้ทำให้ข้อมูลมีคุณภาพ ไม่ได้เลือก metric ที่ตรงกับธุรกิจ ไม่ได้ป้องกัน data leakage อัตโนมัติ และไม่ได้รับประกันว่าโมเดลจะเป็นธรรม การทำ ML บนข้อมูลใหญ่ยังต้องตรวจ sampling bias, privacy, class imbalance, explainability และผลกระทบของ prediction

หากข้อมูลพอดีกับเครื่องเดียว การใช้ Spark อาจเพิ่ม overhead โดยไม่จำเป็น จุดแข็งเกิดเมื่อข้อมูลหรือ transformation ต้องกระจาย และ workflow เชื่อมกับ DataFrame หรือ data lake อยู่แล้ว

## 19. ความเข้าใจผิดที่ควรหลีกเลี่ยง

1. คะแนน training สูงไม่ได้แปลว่าใช้กับข้อมูลใหม่ได้ ต้องดู validation/test
2. Unsupervised learning ไม่ได้สร้างกลุ่มที่มีความหมายทางธุรกิจโดยอัตโนมัติ
3. WSSSE ต่ำลงเมื่อเพิ่ม K จึงใช้เลือก K แบบต่ำสุดตรง ๆ ไม่ได้
4. Sparse vector ไม่ได้แปลว่าข้อมูลมีน้อย แต่แปลว่ามิติส่วนใหญ่มีค่าเป็นศูนย์
5. Regularization ลดความซับซ้อน แต่ไม่แก้ data leakage หรือข้อมูลผิด
6. ALS ทำนายผู้ใช้หรือ item ใหม่ที่ไม่มีประวัติไม่ได้โดยตรง
7. PipelineModel ใช้ transform กับข้อมูลใหม่ ไม่ควร fit ใหม่ทุกครั้งที่ทำนาย
8. spark.mllib แบบ RDD ยังอ่านได้ตามสไลด์ แต่โครงการใหม่ควรเริ่มจาก spark.ml แบบ DataFrame

## 20. เชื่อมแนวคิดทั้งหมด

งาน Machine Learning with Spark เริ่มจาก DataFrame ที่มี observations และ columns จากนั้นแปลง columns ให้เป็น feature vector แยก training กับ test เลือก Estimator ให้ตรงกับชนิด label แล้ว fit เพื่อสร้าง Model เมื่อ Model transform ข้อมูลใหม่จะเพิ่ม prediction ส่วน Evaluator เปรียบ prediction กับ label จริงด้วย metric ที่ตรงกับโจทย์ Pipeline รวม preprocessing และ model ให้เดินทางเป็นชุดเดียว

เส้นทางทั้งหมดคือ

**Raw Data → DataFrame → Feature Transformation → Features/Label → Estimator.fit() → Model → Model.transform() → Prediction → Evaluation**

Regression, classification, clustering และ recommendation แตกต่างกันที่เป้าหมาย รูปแบบ label และวิธีประเมิน แต่ทุกงานต้องรักษาความหมายของข้อมูล ป้องกัน leakage และตรวจว่าสิ่งที่โมเดลเรียนรู้ยังใช้ได้กับข้อมูลใหม่

## 21. คำถามฝึกอธิบายพร้อมแนวคำตอบ

### 1. Supervised และ Unsupervised Learning ต่างกันอย่างไร

Supervised learning ใช้ข้อมูลที่มี label เพื่อเรียนรู้ความสัมพันธ์ระหว่าง features กับคำตอบ แล้วนำไปทำนายข้อมูลใหม่ เช่น classification และ regression ส่วน unsupervised learning ไม่มี label ให้ทำนาย จึงค้นหาโครงสร้าง เช่น clusters หรือ anomalies และต้องตีความผลร่วมกับความรู้ของงาน

### 2. เหตุใดต้องแบ่ง Training Data และ Test Data

Training data ใช้เรียนรู้พารามิเตอร์ ส่วน test data จำลองข้อมูลใหม่ที่โมเดลไม่เคยเห็น หากประเมินบนชุดฝึก โมเดลที่จำข้อมูลหรือ overfit อาจดูดีเกินจริง การแยก test จึงช่วยวัดความสามารถในการ generalize

### 3. Dense Vector และ Sparse Vector เหมาะกับข้อมูลแบบใด

Dense vector เก็บทุกตำแหน่ง เหมาะเมื่อค่าศูนย์มีไม่มาก Sparse vector เก็บเฉพาะ index และค่าที่ไม่เป็นศูนย์ เหมาะกับข้อมูลมิติสูงที่ส่วนใหญ่เป็นศูนย์ เช่น text features จึงลดพื้นที่และงานคำนวณที่ไม่จำเป็น

### 4. Ridge, Lasso และ Elastic Net ต่างกันอย่างไร

Ridge ใช้ L2 ลดขนาด coefficients แต่โดยทั่วไปไม่ทำให้เป็นศูนย์ Lasso ใช้ L1 และอาจทำให้บาง coefficients เป็นศูนย์ จึงมีผลคล้ายเลือก features ส่วน Elastic Net ผสม L1 กับ L2 โดยใช้ alpha กำหนดสัดส่วนและ lambda กำหนดความแรง

### 5. K-Means ทำงานอย่างไร และมีข้อจำกัดใด

K-Means กำหนด K centroids แล้วสลับระหว่าง assign จุดไป centroid ที่ใกล้ที่สุดกับคำนวณ centroid ใหม่จนหยุด เหมาะกับกลุ่มที่วัดด้วยระยะทางและมีรูปร่างค่อนข้างกลม ต้อง scale features และระวัง outliers, initialization และการเลือก K

### 6. ALS สร้างคำแนะนำอย่างไร

ALS แยก user–item matrix เป็น user factors กับ item factors ที่มีมิติต่ำ แล้วสลับตรึงชุดหนึ่งเพื่อหาอีกชุดด้วย regularized least squares ผลคูณของ factors ใช้ประมาณความสนใจที่หายไป แต่ user หรือ item ใหม่ไม่มี factors จึงต้องมีวิธีรับมือ cold start

### 7. Estimator และ Transformer ต่างกันอย่างไร

Estimator มี fit() รับ DataFrame แล้วสร้าง Model เช่น LogisticRegression ส่วน Transformer มี transform() รับ DataFrame แล้วคืน DataFrame ใหม่ เช่น Tokenizer หรือโมเดลที่ฝึกแล้วซึ่งเพิ่ม prediction

### 8. Pipeline ช่วยป้องกันปัญหาใด

Pipeline รวม preprocessing และ model เป็นลำดับเดียว ทำให้ training กับข้อมูลใหม่ผ่าน transformations ชุดเดียวกัน ลดความเสี่ยงที่ feature processing จะต่างกัน และทำให้บันทึกหรือใช้ workflow ซ้ำได้เป็นหน่วยเดียว

## สรุป

Machine Learning ใช้ข้อมูลเรียนรู้รูปแบบแล้วสร้าง model สำหรับทำนายหรือค้นหาโครงสร้าง Spark ทำให้งานนี้ทำกับ DataFrame และข้อมูลแบบกระจายได้ API แบบ RDD ใน spark.mllib ช่วยอธิบาย Vector, LabeledPoint และ Rating ตามสไลด์ ส่วน spark.ml เป็น API หลักสำหรับงานปัจจุบันและใช้แนวคิด Estimator, Transformer และ Pipeline

ความเข้าใจสำคัญไม่ได้อยู่ที่จำชื่อ algorithm ให้ได้มากที่สุด แต่อยู่ที่เลือกชนิดปัญหาให้ถูก สร้าง features กับ label อย่างมีความหมาย แยกข้อมูลโดยไม่รั่ว ใช้ metric ที่ตรงกับผลกระทบ และรักษากระบวนการตั้งแต่ preprocessing จนถึง prediction ให้สอดคล้องกัน

## แหล่งอ้างอิง

- เอกสารประกอบการสอน lecture_07_machine_learning.pdf หน้า 1–51
- [Apache Spark: MLlib Guide](https://spark.apache.org/docs/latest/ml-guide.html)
- [Apache Spark: ML Pipelines](https://spark.apache.org/docs/latest/ml-pipeline.html)
- [Apache Spark: Classification and Regression](https://spark.apache.org/docs/latest/ml-classification-regression.html)
- [Apache Spark: Collaborative Filtering](https://spark.apache.org/docs/latest/ml-collaborative-filtering.html)
