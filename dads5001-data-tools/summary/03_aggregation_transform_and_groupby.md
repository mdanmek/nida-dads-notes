# Pandas Aggregation, Transform และ GroupBy

> Source: `lab_03_pandas3.ipynb`  
> Scope: numeric/categorical aggregation, `agg`, `apply`, `transform`, Split–Apply–Combine และผลลัพธ์ของ GroupBy

## 1. ปัญหาหลักของบท

ข้อมูลระดับรายละเอียดตอบคำถามว่า “เกิดอะไรขึ้นในแต่ละ record” แต่ผู้วิเคราะห์มักต้องตอบคำถามระดับกลุ่ม เช่น HP เฉลี่ยต่อ Pokémon type หรือจำนวนสมาชิกในแต่ละรุ่น การสรุปข้อมูลจึงเปลี่ยน grain จากระดับรายละเอียดไปเป็นระดับกลุ่ม หากไม่รู้ว่า grain เปลี่ยนอย่างไร อาจนำยอดรวมไป join กลับแล้วนับซ้ำ

## 2. Aggregation คืออะไร

Aggregation รับค่าหลายค่าแล้วสรุปเป็นค่าน้อยลง เช่น mean, sum, min, max หรือ count

```python
pokemon[['hp', 'attack', 'defense']].mean()
```

DataFrame มีหลายคอลัมน์ การกำหนด `axis` จึงสำคัญ:

- `axis=0`: ยุบหลายแถว ได้หนึ่งผลต่อคอลัมน์
- `axis=1`: ยุบหลายคอลัมน์ ได้หนึ่งผลต่อแถว

```python
pokemon[['hp', 'attack', 'defense']].mean(axis=1)
```

Pandas ส่วนใหญ่ข้าม NA ใน aggregation โดยค่าเริ่มต้น ต้องระบุในคำอธิบายว่าค่าเฉลี่ยใช้จำนวน non-null ไม่ใช่จำนวนแถวทั้งหมด

```python
mean_hp = pokemon['hp'].mean()
above_average = pokemon.loc[pokemon['hp'].ge(mean_hp)]
```

## 3. Numeric กับ categorical aggregation

ข้อมูลตัวเลขตอบด้วย `mean`, `median`, `sum` ได้ ส่วนข้อมูลหมวดหมู่ต้องใช้คำถามคนละแบบ:

```python
s = pokemon['type2']
s.unique()                 # ค่าที่พบ
s.nunique(dropna=True)     # จำนวนค่าที่ต่างกัน
s.count()                  # จำนวน non-null
s.value_counts(dropna=False)  # ความถี่รวม NA
```

`count()` ไม่ใช่จำนวนแถวทั้งหมด เพราะข้าม NA ส่วน `size` นับจำนวนสมาชิกในกลุ่มรวม NA ความต่างนี้สำคัญเมื่อวัดจำนวนธุรกรรมกับจำนวนค่าที่กรอกสำเร็จ

## 4. `agg()` เพื่อสรุปหลายฟังก์ชัน

```python
pokemon[['hp', 'attack', 'defense']].agg(['mean', 'min', 'max'])
```

กำหนดคนละฟังก์ชันต่อคอลัมน์ได้:

```python
summary = pokemon.agg({
    'hp': ['mean', 'max'],
    'type1': ['nunique', 'count']
})
```

เมื่อฟังก์ชันหลายตัวหรือหลายระดับ ผลลัพธ์อาจมี MultiIndex ต้องตรวจ `result.index` และ `result.columns` ก่อน export หรือ join

Named aggregation ให้ชื่อคอลัมน์ผลลัพธ์ชัดเจนเมื่อใช้กับ groupby:

```python
type_summary = (
    pokemon.groupby('type1', dropna=False)
    .agg(
        pokemon_count=('name', 'size'),
        hp_mean=('hp', 'mean'),
        hp_max=('hp', 'max')
    )
    .reset_index()
)
```

## 5. `apply()` กับ `transform()` ต่างกันที่สัญญาผลลัพธ์

`transform()` ต้องส่งผลลัพธ์ที่จัดแนวกลับกับ input ได้ โดยทั่วไปจึงคงจำนวนแถวเดิม ส่วน `apply()` ยืดหยุ่นกว่าและอาจคืน scalar, Series หรือ DataFrame ทำให้ shape เปลี่ยนได้

```python
df = pokemon[['hp', 'attack', 'defense']].copy()

df.transform(lambda x: x + 10)
df.apply('mean')
```

ถ้า transform ด้วย aggregate function เช่น mean บนคอลัมน์ ระบบจะ broadcast ค่า mean กลับทุกแถว:

```python
hp_mean_per_row = pokemon['hp'].transform('mean')
assert len(hp_mean_per_row) == len(pokemon)
```

การเลือกใช้:

| ต้องการ | เครื่องมือ |
|---|---|
| สรุปหลายแถวเหลือหนึ่งค่าหรือหนึ่งแถวต่อกลุ่ม | `agg` |
| คำนวณแล้วคงแนว/จำนวนแถวเดิม | `transform` |
| logic ยืดหยุ่นที่ผลลัพธ์อาจเปลี่ยน shape | `apply` |
| operation ที่มี method vectorized อยู่แล้ว | ใช้ method นั้นก่อน |

อย่าใช้ `apply` เป็นค่าเริ่มต้น เพราะ vectorized operation มักชัดและเร็วกว่า

## 6. GroupBy mental model: Split–Apply–Combine

สมมติข้อมูล:

| name | type1 | hp |
|---|---|---:|
| A | fire | 40 |
| B | water | 60 |
| C | fire | 80 |

ระบบทำสามขั้น:

1. **Split:** แบ่งแถวตาม `type1` เป็น fire และ water
2. **Apply:** คำนวณ mean ในแต่ละกลุ่ม
3. **Combine:** รวมผลเป็นตาราง fire = 60, water = 60

```python
df.groupby('type1')['hp'].mean()
```

GroupBy object ยังไม่ใช่ DataFrame ผลลัพธ์ เป็นคำอธิบายว่าจะแบ่งกลุ่มอย่างไร การคำนวณจริงเกิดเมื่อเรียก `mean`, `agg`, `transform` หรือ operation อื่น

## 7. สำรวจ GroupBy object

```python
grouped = pokemon.groupby('type1', dropna=False)

grouped.ngroups
grouped.size()
grouped.first()
grouped.last()
```

วนดูแต่ละกลุ่มได้:

```python
for group_name, group_df in grouped:
    print(group_name, group_df.shape)
```

การ group หลายคอลัมน์สร้าง key แบบ tuple และผลลัพธ์มักมี MultiIndex:

```python
grouped = pokemon.groupby(['type1', 'type2'], dropna=False)
summary = grouped['hp'].mean().reset_index(name='hp_mean')
```

โดยค่าเริ่มต้น NA ใน grouping key ถูกตัดออก `dropna=False` เก็บกลุ่ม NA แต่ในบาง workflow การแทนด้วย label เช่น `'unknown'` ก่อน group ช่วยให้ตรวจและสื่อสารง่ายขึ้น ทั้งนี้ต้องไม่ทำให้ “ไม่มี type2” ถูกเข้าใจว่าเป็นข้อมูลเสีย

## 8. Aggregate, transform และ filter หลัง group

### Aggregate: เปลี่ยน grain

```python
type_stats = (
    pokemon.groupby('type1')
    .agg(
        n=('name', 'size'),
        hp_mean=('hp', 'mean')
    )
    .reset_index()
)
```

ผลคือหนึ่งแถวต่อ `type1`

### Transform: คง grain เดิม

```python
pokemon = pokemon.copy()
pokemon['type_hp_mean'] = (
    pokemon.groupby('type1')['hp'].transform('mean')
)
pokemon['hp_vs_type_mean'] = pokemon['hp'] - pokemon['type_hp_mean']
```

ผลยังหนึ่งแถวต่อ Pokémon แต่มีค่าเฉลี่ยของกลุ่มแนบกลับแต่ละ record

### Filter: เก็บหรือตัดทั้งกลุ่ม

```python
large_types = pokemon.groupby('type1').filter(lambda g: len(g) >= 20)
```

นี่ต่างจาก Boolean filter รายแถว เพราะเงื่อนไขถูกประเมินที่ระดับกลุ่ม

## 9. Trace table: คำนวณส่วนต่างจากค่าเฉลี่ยกลุ่ม

| record | type | hp | group mean | hp - mean |
|---|---|---:|---:|---:|
| A | fire | 40 | 60 | -20 |
| C | fire | 80 | 60 | 20 |
| B | water | 60 | 60 | 0 |

`groupby().transform('mean')` คืน `[60, 60, 60]` ที่จัดแนวกับ index เดิม จึงลบกับ `hp` แบบ element-wise ได้ หากใช้ `agg('mean')` จะได้ Series ที่ index เป็นชื่อกลุ่ม และลบตรง ๆ อาจเกิด alignment ไม่ตรงกัน

## 10. Validation ที่ต้องทำ

```python
assert type_stats['type1'].is_unique
assert type_stats['n'].sum() == len(pokemon.dropna(subset=['type1']))
assert pokemon['type_hp_mean'].shape[0] == pokemon.shape[0]
```

เมื่อ groupby หลาย key ให้ตรวจ uniqueness ของ composite key:

```python
assert not summary.duplicated(['type1', 'type2']).any()
```

ถ้าสรุปยอดเงิน ควร reconcile ยอดรวมก่อนและหลัง aggregation โดยคำนึงถึง NA key

## 11. Failure modes

- ใช้ `count` ทั้งที่ต้องการจำนวนแถว ทำให้ record ที่คอลัมน์เป้าหมายเป็น NA หาย
- ลืม `dropna=False` ทำให้ยอดรวมตามกลุ่มไม่เท่ายอดทั้งหมด
- reset index โดยไม่เข้าใจ ทำให้ MultiIndex กลายเป็นคอลัมน์เกินหรือหาย
- ใช้ `apply` แล้วคาดว่า shape จะเท่าเดิม
- join summary กลับด้วย key ไม่ unique ทำให้ row multiplication
- คำนวณ mean บนคอลัมน์ที่ถูกอ่านเป็น object แล้วได้ error หรือถูกตัดออก

## 12. Guided Lab

```python
sales = pd.DataFrame({
    'branch': ['A', 'A', 'B', 'B', None],
    'amount': [100, 200, 50, None, 25]
})
```

ทำนายก่อนรัน:

```python
sales.groupby('branch')['amount'].agg(['size', 'count', 'sum'])
sales.groupby('branch', dropna=False)['amount'].agg(['size', 'count', 'sum'])
```

ผลที่ต้องอธิบายได้: `size` นับแถว B สองแถว แต่ `count` นับ amount ที่ไม่ว่างเพียงหนึ่งแถว และคำสั่งแรกไม่มีกลุ่ม branch ที่ว่าง

สร้างสัดส่วนยอดขายต่อสาขา:

```python
sales['branch_total'] = (
    sales.groupby('branch', dropna=False)['amount'].transform('sum')
)
sales['share_in_branch'] = sales['amount'] / sales['branch_total']
```

ตรวจเฉพาะกลุ่มที่มีผลรวมไม่เป็นศูนย์:

```python
check = sales.groupby('branch', dropna=False)['share_in_branch'].sum()
assert check.dropna().round(10).eq(1).all()
```

## 13. Likely Exam Focus

1. อธิบาย grain ก่อน–หลัง aggregation
2. แยก `size`, `count`, `nunique`, `value_counts`
3. เปรียบเทียบ `agg`, `apply`, `transform`
4. อธิบาย Split–Apply–Combine ด้วยข้อมูลตัวอย่าง
5. อ่าน MultiIndex และ reset index
6. วิเคราะห์ผลของ NA ใน grouping key

## 14. แบบฝึกพร้อมเฉลย

### ข้อ 1

ต้องการให้ทุกแถวมีค่าเฉลี่ยเงินเดือนของแผนก ควรใช้อะไร?

```python
df['dept_salary_mean'] = df.groupby('dept')['salary'].transform('mean')
```

เพราะต้องคงหนึ่งผลต่อแถวเดิม

### ข้อ 2

ทำไมผลรวมรายกลุ่มต่ำกว่ายอดรวมทั้งตาราง?

**เฉลย:** ตรวจ NA ใน grouping key ก่อน เพราะ GroupBy ตัดกลุ่ม NA โดยค่าเริ่มต้น จากนั้นตรวจ filter และ dtype ของ measure

### ข้อ 3

ออกแบบ summary หนึ่งแถวต่อ type พร้อมจำนวน Pokémon, HP mean และ HP max

```python
df.groupby('type1', dropna=False).agg(
    pokemon_count=('name', 'size'),
    hp_mean=('hp', 'mean'),
    hp_max=('hp', 'max')
).reset_index()
```

## 15. Mini-project

ใช้ dataset ธุรกรรมหรือ Pokémon สร้าง summary อย่างน้อยสอง grain: หนึ่งแถวต่อกลุ่ม และหนึ่งแถวต่อ record ที่แนบ benchmark ของกลุ่ม อธิบาย key, NA policy, validation และกรณีที่ `count` กับ `size` ให้คำตอบต่างกัน

## 16. Mastery Checklist

- ระบุ grain ก่อนและหลังทุก aggregation ได้
- เลือก `agg`, `transform`, `apply`, `filter` ตาม shape ที่ต้องการ
- อธิบายและตรวจ NA group ได้
- สร้าง named aggregation ที่อ่านง่ายได้
- reconcile จำนวนแถวและยอดรวมได้

## References

- [Pandas GroupBy user guide](https://pandas.pydata.org/docs/user_guide/groupby.html)
- [Pandas aggregation](https://pandas.pydata.org/docs/reference/groupby.html)

