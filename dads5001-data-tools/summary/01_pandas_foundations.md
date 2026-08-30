# Pandas Foundations: จากข้อมูลดิบสู่ DataFrame ที่ตรวจสอบได้

> Source: `dads5001_01_pandas.pdf`, `lab_01_pandas1.ipynb`  
> Scope: แนวคิด Pandas, Series/DataFrame, dtype, การอ่านและสำรวจข้อมูล, indexing, การแก้ไข, sorting และ export

## 1. เป้าหมายการเรียนรู้

หลังจบบทนี้ ผู้เรียนควรสามารถอธิบายได้ว่า Pandas แก้ปัญหาอะไร สร้างและตรวจสอบ `Series`/`DataFrame` เลือกข้อมูลด้วย label และตำแหน่ง แก้ไขข้อมูลโดยไม่ทำลาย grain โดยไม่ตั้งใจ และ export ผลลัพธ์โดยตรวจสอบความถูกต้องก่อนส่งต่อ

## 2. ทำไมต้องมี Pandas

ข้อมูลวิเคราะห์มักไม่ได้มีเพียงตัวเลขเรียงต่อกัน แต่มีทั้งชื่อคอลัมน์ ชนิดข้อมูล ค่าว่าง และดัชนีที่บอกว่าแต่ละแถวหมายถึงอะไร Python `list` เก็บข้อมูลได้แต่ไม่รู้ความหมายของแต่ละคอลัมน์ ส่วน NumPy เหมาะกับการคำนวณ array ที่มีชนิดข้อมูลค่อนข้างสม่ำเสมอ Pandas จึงเพิ่มโครงสร้างแบบตารางและ label บน NumPy เพื่อให้การเลือก กรอง รวม และตรวจสอบข้อมูลใกล้เคียงกับงานวิเคราะห์จริง

Pandas เป็นไลบรารี ไม่ใช่ฐานข้อมูล และไม่ใช่ spreadsheet ที่แก้ทีละเซลล์ด้วยสายตา จุดแข็งคือการแปลงข้อมูลด้วยโค้ดที่ทำซ้ำได้ แต่โดยทั่วไปข้อมูลต้องอยู่ในหน่วยความจำ จึงยังมีข้อจำกัดจาก RAM

## 3. Mental model: ตารางหนึ่งใบมีสามชั้น

ให้นึกถึงตารางพนักงานที่หนึ่งแถวแทนพนักงานหนึ่งคน ชั้นแรกคือ **values** เช่นชื่อและเงินเดือน ชั้นที่สองคือ **column labels** เช่น `name`, `salary` และชั้นที่สามคือ **row index** ที่ใช้ระบุแถว Pandas แยกสามชั้นนี้ออกจากกัน จึงเลือกข้อมูลได้ทั้งตามชื่อและตำแหน่ง

คำศัพท์สำคัญ:

- `Series`: ข้อมูลหนึ่งมิติ มี values และ index
- `DataFrame`: ตารางสองมิติ แต่ละคอลัมน์เป็น Series ที่ใช้ index ร่วมกัน
- `shape`: `(จำนวนแถว, จำนวนคอลัมน์)`
- `dtype`: ชนิดข้อมูลของ Series หนึ่งคอลัมน์
- `axis=0`: เดินตามแนวแถวหรือคำนวณแยกตามคอลัมน์
- `axis=1`: เดินตามแนวคอลัมน์หรือคำนวณแยกตามแถว

## 4. Notebook และ rich display

`print()` แสดงข้อความธรรมดา ส่วน `display()` ขอให้ Notebook render object ตามชนิดของมัน จึงเห็น DataFrame เป็นตาราง และยังแสดง `Markdown`, `HTML`, `Image` หรือ `YouTubeVideo` ได้ ตัวอย่างใน Lab ต้องการสอนว่า Notebook เป็นเอกสารที่ผสมคำอธิบาย โค้ด และผลลัพธ์—not merely a Python script

```python
from IPython.display import display

display(df.head())
```

`clear_output()` ล้าง output ของ cell ในหน้าจอ แต่ไม่ได้ลบตัวแปรออกจาก memory และไม่ได้ย้อนผลข้างเคียงของโค้ด

## 5. การสร้าง Series และ dtype

```python
import pandas as pd

scores = pd.Series([10, 20.5, 30.6, 100])
```

Pandas หา dtype ที่รองรับค่าทั้งหมดร่วมกัน จำนวนเต็มจึงถูกยกระดับเป็น floating point เมื่ออยู่ร่วมกับทศนิยม การบังคับ `dtype='int32'` ทั้งที่มี `20.5` เป็นการสูญเสียข้อมูลและใน Pandas รุ่นใหม่อาจเกิด error

```python
scores = pd.Series([10, 20.5, 30.6], dtype='float64')
names = pd.Series(['Mary', 'John'], dtype='string')
```

`object` อาจเก็บ string หรือค่าหลายชนิดปนกัน จึงไม่รับประกันว่าเป็นข้อความทั้งหมด ขณะที่ `string` เป็น dtype เชิงความหมายและรองรับ missing value แบบ `pd.NA` ชัดกว่า

### Missing value กับ dtype

ใน NumPy backend เดิม คอลัมน์ integer ที่มี `None` มักถูกแปลงเป็น float เพื่อใช้ `NaN` ส่วน nullable dtype เช่น `Int64` และ PyArrow-backed dtype รองรับ `pd.NA` โดยไม่ต้องเปลี่ยน integer เป็น float

```python
ids = pd.Series([10, 20, None], dtype='Int64')
assert ids.isna().sum() == 1
```

ข้อควรจำคือ dtype ไม่ใช่เพียงรายละเอียดทางเทคนิค แต่กำหนดว่าคำนวณ เปรียบเทียบ และจัดการค่าว่างได้หรือไม่

## 6. การสร้าง DataFrame และ grain

```python
employees = pd.DataFrame({
    'name': ['Mary', 'John', 'George'],
    'salary': [50000.0, 35000.0, 25333.33]
})
```

ก่อนวิเคราะห์ต้องบอกให้ได้ว่า “หนึ่งแถวแทนอะไร” ซึ่งเรียกว่า **grain** ในตัวอย่างนี้หนึ่งแถวคือพนักงานหนึ่งคน หาก `name` ซ้ำอาจเป็นคนชื่อซ้ำ ไม่ได้พิสูจน์ว่าแถวซ้ำ จึงควรมีรหัสพนักงานเป็น key

ตั้ง index แบบกำหนดเองได้ แต่ index ไม่จำเป็นต้องเป็น primary key:

```python
employees = employees.set_index('name')
employees = employees.reset_index()
```

`reset_index(drop=True)` ทิ้ง index เดิม ส่วน `reset_index()` เก็บ index เดิมเป็นคอลัมน์ ต้องเลือกให้สอดคล้องกับความหมายของข้อมูล

## 7. อ่านและสำรวจข้อมูลก่อนวิเคราะห์

```python
pokemon = pd.read_csv('pokemon.csv')
```

ขั้นตรวจข้อมูลที่ควรทำทันที:

```python
pokemon.shape
pokemon.head()
pokemon.tail()
pokemon.sample(5, random_state=42)
pokemon.info()
pokemon.describe(include='all')
```

`head()` และ `tail()` เห็นเพียงตัวอย่าง ไม่พิสูจน์ว่าข้อมูลทั้งชุดสะอาด `info()` ช่วยดูจำนวน non-null และ dtype ส่วน `describe()` สรุป distribution ตามชนิดข้อมูล การตรวจที่ดีจึงต้องใช้หลายมุมร่วมกัน

```python
assert pokemon.columns.is_unique
assert len(pokemon) > 0
```

## 8. การเลือกข้อมูล: label กับ position

Pandas มีสองระบบหลัก:

| เครื่องมือ | อ้างอิงด้วย | เหมาะกับ |
|---|---|---|
| `loc` | label | โค้ดที่สื่อความหมายและทนต่อการเปลี่ยนลำดับ |
| `iloc` | integer position | เลือกตามตำแหน่งจริง |
| `at` | label เดียว | อ่าน/เขียนหนึ่งเซลล์ |
| `iat` | position เดียว | อ่าน/เขียนหนึ่งเซลล์ |

```python
pokemon.loc[3, 'name']
pokemon.iloc[3, 0]
pokemon.at[3, 'name']
pokemon.iat[3, 0]
```

ความต่างที่ออกสอบบ่อยคือ slicing: `iloc[2:5]` ไม่รวมตำแหน่ง 5 แต่ `loc['A':'C']` รวม label ปลายทาง `C` หาก index เรียงและมี label ดังกล่าว

```python
pokemon.loc[:, ['name', 'hp', 'attack']]
pokemon.iloc[0:10, 0:3]
```

`df.column` ใช้ได้เฉพาะชื่อที่เป็น Python identifier และอาจชนกับ method ของ DataFrame จึงควรใช้ `df['column']` เป็นรูปแบบมาตรฐาน

## 9. การเปลี่ยนข้อมูลและ vectorization

```python
pokemon = pokemon.rename(columns={'sp_attack': 'special_attack'})
pokemon['avg_attack_defense'] = (
    pokemon['attack'] + pokemon['defense']
) / 2
```

สมการนี้ทำงานแบบ element-wise และ scalar `2` ถูก broadcast ไปทุกแถว จึงเร็วและอ่านง่ายกว่าการ loop ทีละ record ที่สำคัญต้องตรวจผลลัพธ์ ไม่ใช่เชื่อเพียงเพราะโค้ดรันผ่าน

```python
expected = (pokemon['attack'] + pokemon['defense']) / 2
pd.testing.assert_series_equal(
    pokemon['avg_attack_defense'],
    expected,
    check_names=False
)
```

การเพิ่มแถวผ่าน `df.loc[new_label]` ทำได้ แต่เสี่ยงชน index และ dtype เปลี่ยน ใน pipeline จริงนิยมสร้าง DataFrame ใหม่แล้ว `pd.concat()` มากกว่า

```python
pokemon = pokemon.drop(columns=['unused_column'])
pokemon = pokemon.drop(index=[0, 1, 2]).reset_index(drop=True)
```

ระวัง `inplace=True`: ไม่ได้ทำให้เร็วกว่าเสมอ และทำให้ chain/ทดสอบยาก การ assign ผลลัพธ์กลับตัวแปรมักชัดเจนกว่า

## 10. Sorting

`sort_index()` เรียงตาม label ส่วน `sort_values()` เรียงตามค่า

```python
ranked = pokemon.sort_values(
    ['hp', 'attack'],
    ascending=[False, False],
    na_position='last'
)
```

คำสั่งนี้เรียง `hp` ก่อน และใช้ `attack` เป็นตัวตัดสินเมื่อ `hp` เท่ากัน การ sort ไม่รับประกันว่า index จะกลับเป็น 0 ถึง N−1 จึงค่อย `reset_index(drop=True)` เมื่อจำเป็น

## 11. Export และ round-trip validation

```python
ranked.to_csv('pokemon_ranked.csv', index=False)
check = pd.read_csv('pokemon_ranked.csv')

assert check.shape == ranked.shape
assert check.columns.tolist() == ranked.columns.tolist()
```

Pandas export ได้หลายรูปแบบ เช่น CSV, Excel, JSON, HTML และ LaTeX แต่แต่ละ format เก็บ dtype/index ไม่เท่ากัน `Styler` ใช้ตกแต่งการแสดงผลและไม่ใช่ DataFrame จึงไม่ควรใช้แทนข้อมูลต้นฉบับ

## 12. Guided Lab: สร้างตารางที่ตรวจสอบได้

```python
sales = pd.DataFrame({
    'invoice_id': ['A01', 'A02', 'A03'],
    'qty': [2, 3, 1],
    'unit_price': [100.0, 80.0, None]
})

sales['amount'] = sales['qty'] * sales['unit_price']
display(sales)
```

ให้ทำนายก่อนรันว่า `amount` ของ A03 เป็นอะไร จากนั้นตรวจ:

```python
assert sales['invoice_id'].is_unique
assert sales['amount'].isna().sum() == 1
assert sales.loc[sales['invoice_id'] == 'A02', 'amount'].iloc[0] == 240
```

ทดลองผิดโดยเขียน `sales.iloc[:, 'qty']` จะเกิด error เพราะ `iloc` ต้องรับตำแหน่งจำนวนเต็ม วิธีแก้คือ `sales.loc[:, 'qty']` หรือ `sales.iloc[:, 1]`

## 13. Common misconceptions

- Index คือ key เสมอ — ไม่จริง index อาจซ้ำได้
- `object` หมายถึง string — ไม่เสมอ อาจเป็นข้อมูลปนชนิด
- `head()` ดูแล้วข้อมูลถูก — เห็นเพียงไม่กี่แถว
- `axis=0` หมายถึงเลือกแถวเสมอ — ความหมายขึ้นกับ operation; สำหรับ aggregation คือยุบแถวและให้ผลต่อคอลัมน์
- การรันไม่ error แปลว่าถูก — ต้องตรวจ shape, dtype, grain และค่าที่คาดหมาย

## 14. Likely Exam Focus

1. เปรียบเทียบ Series กับ DataFrame และอธิบายบทบาทของ index
2. อ่านผล `shape`, `info()` และ `describe()`
3. แยก `loc`/`iloc` และ inclusive/exclusive slicing
4. อธิบาย vectorization และ broadcasting
5. วิเคราะห์ผลของ dtype และ missing value
6. เลือก `sort_index()` หรือ `sort_values()` ตามสถานการณ์

## 15. แบบฝึกและเฉลย

### ข้อ 1

ถ้า `df.shape == (100, 5)` หมายถึงอะไร?

**เฉลย:** มี 100 แถวและ 5 คอลัมน์ โดยยังสรุปไม่ได้ว่า grain ถูกต้องหรือ key ไม่ซ้ำ

### ข้อ 2

เหตุใด `df.loc[2:5]` อาจได้ 4 แถว แต่ `df.iloc[2:5]` ได้ 3 แถว?

**เฉลย:** `loc` slice ตาม label และรวมปลายทาง ส่วน `iloc` ตามกฎ Python slicing ไม่รวมตำแหน่งปลายทาง

### ข้อ 3

เขียนคำสั่งเลือก 10 แถวแรกและเฉพาะ `name`, `hp`

```python
df.loc[df.index[:10], ['name', 'hp']]
# หรือเมื่อ index เป็นลำดับปกติ
df.iloc[:10][['name', 'hp']]
```

รูปแบบที่ชัดกว่าและหลีกเลี่ยง chained indexing คือ:

```python
df.loc[df.index[:10], ['name', 'hp']]
```

### ข้อ 4

ทำไมควร export ด้วย `index=False` ในหลายกรณี?

**เฉลย:** ป้องกัน index ภายในถูกบันทึกเป็นคอลัมน์เกินมา แต่หาก index มีความหมายทางธุรกิจต้องเก็บเป็นคอลัมน์อย่างตั้งใจก่อน

## 16. Mini-project

เลือก CSV หนึ่งชุด กำหนด grain และ candidate key จากนั้นอ่านข้อมูล ตรวจ shape/dtype/missing/duplicates สร้างอย่างน้อยหนึ่ง derived column จัดเรียงผลลัพธ์ และ export พร้อม round-trip validation รายงานข้อจำกัดว่ามีสิ่งใดที่ยังพิสูจน์ไม่ได้จากข้อมูล

## 17. Mastery Checklist

- อธิบาย Series, DataFrame, index, dtype และ grain ได้
- เลือกข้อมูลด้วย `loc`/`iloc` ได้โดยไม่สับสน
- ตรวจข้อมูลก่อนและหลัง transformation ด้วย assertion ที่เหมาะสม
- อธิบายผลของ missing value ต่อ dtype และ calculation ได้
- export แล้วอ่านกลับมาตรวจสอบได้

## References

- [Pandas User Guide](https://pandas.pydata.org/docs/user_guide/index.html)
- [Pandas indexing](https://pandas.pydata.org/docs/user_guide/indexing.html)
- [Pandas missing data](https://pandas.pydata.org/docs/user_guide/missing_data.html)

