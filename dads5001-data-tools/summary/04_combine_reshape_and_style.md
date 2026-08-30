# Pandas Combine, Reshape และ Table Styling

> Source: `lab_04_pandas4.ipynb`  
> Scope: `merge`, `join`, `concat`, `pivot`, `pivot_table`, `melt` และ `Styler`

## 1. ภาพรวม: การรวมข้อมูลเปลี่ยนความหมายของแถว

การรวม DataFrame ไม่ใช่เพียงนำตารางมาวางติดกัน ผู้วิเคราะห์ต้องรู้ grain, key และ cardinality ของแต่ละฝั่ง เพราะ join key ที่ซ้ำสามารถคูณจำนวนแถวและยอดเงินได้ ตัวอย่างหลักของบทใช้ตาราง Pokémon และตาราง move: Pokémon หนึ่งตัวอาจมีหลาย move จึงเป็นความสัมพันธ์ one-to-many และผลหลัง merge มี grain เป็นหนึ่งแถวต่อคู่ Pokémon–move

## 2. Relational foundation

- **Key:** คอลัมน์ที่ใช้ระบุหรือจับคู่ record
- **Cardinality:** จำนวน record ที่ key เดียวเชื่อมได้ เช่น one-to-one, one-to-many
- **Matched row:** key พบในทั้งสองฝั่ง
- **Unmatched row:** key พบเพียงฝั่งเดียว
- **Output grain:** สิ่งที่หนึ่งแถวแทนหลังรวม

ก่อน merge ต้องถาม:

1. หนึ่งแถวของซ้ายและขวาแทนอะไร?
2. key ควร unique ฝั่งใด?
3. ต้องรักษาประชากรฝั่งไหน?
4. แถวที่ match ไม่ได้ควรหายหรือคงไว้?
5. หลังรวมคาดว่าแถวเพิ่ม ลด หรือเท่าเดิม?

## 3. `merge()` ด้วย key

```python
merged = pokemon.merge(
    moves,
    left_on='type2',
    right_on='type',
    how='left',
    validate='many_to_many',
    indicator=True
)
```

ชนิด join:

| `how` | ประชากรที่รักษา |
|---|---|
| `inner` | เฉพาะ key ที่พบทั้งสองฝั่ง |
| `left` | ทุกแถวซ้าย |
| `right` | ทุกแถวขวา |
| `outer` | key ทั้งสองฝั่ง |

`indicator=True` เพิ่ม `_merge` เพื่อแยก `both`, `left_only`, `right_only` ส่วน `validate` บังคับ cardinality ที่คาดไว้ เช่น `one_to_one`, `one_to_many`, `many_to_one` หากข้อมูลผิดสมมติฐานจะ error แทนการสร้างผลผิดเงียบ ๆ

### Row multiplication

ถ้า key `fire` มี Pokémon 2 แถวและ move 3 แถว inner join จะได้ 6 แถว เพราะทุกแถวซ้ายจับคู่ทุกแถวขวาใน key เดียวกัน นี่ไม่ใช่ duplicate จาก Pandas แต่เป็นผลตาม cardinality

## 4. Merge หลาย key

```python
enrollment.merge(
    grades,
    on=['student_id', 'course_id'],
    how='outer',
    validate='one_to_one',
    indicator=True
)
```

ใช้ composite key เมื่อคอลัมน์เดียวไม่ระบุ record ได้ เช่น student คนเดียวเรียนหลาย course ก่อน merge ควรตรวจ:

```python
assert not enrollment.duplicated(['student_id', 'course_id']).any()
```

## 5. `join()` ด้วย index

`DataFrame.join()` เป็น convenience method ที่เน้นจับคู่ index เหมาะเมื่อทั้งสองตารางสรุปไว้ที่ grain เดียวกันและตั้ง index เป็น key แล้ว

```python
result = pokemon_summary.join(move_summary, how='left')
```

ทำสิ่งใกล้เคียงกันด้วย `merge(left_index=True, right_index=True)` ได้ การเลือกไม่ใช่เรื่องผลลัพธ์อย่างเดียว แต่ต้องให้โค้ดสื่อว่ากำลังจับคู่ด้วยคอลัมน์หรือ index

`DataFrame.compare()` เปรียบเทียบได้เมื่อ row/column labels เหมือนกันทุกตำแหน่ง จึงควร sort และ align ก่อนใช้

## 6. Validation หลัง join

```python
before = len(pokemon)
result = pokemon.merge(dim_type, on='type1', how='left', validate='many_to_one', indicator=True)

assert len(result) == before
assert result['_merge'].eq('both').mean() >= 0.99
```

ถ้าเป็นการ join lookup many-to-one จำนวนแถวควรเท่าเดิม หากเพิ่มขึ้นแปลว่า key ฝั่ง lookup ไม่ unique ถ้าลดลงใน inner join แปลว่ามี unmatched keys

## 7. `concat()`: stacking ตาม axis

`concat` ไม่จับคู่ตามค่าของ key แบบ merge แต่เรียง object ต่อกันตามแกน

### ต่อแถว `axis=0`

```python
combined = pd.concat(
    [water, fire],
    axis=0,
    join='outer',
    ignore_index=True
)
```

- `join='outer'` เก็บ union ของคอลัมน์ คอลัมน์ที่ไม่มีในบางชุดเป็น NA
- `join='inner'` เก็บเฉพาะ intersection ของคอลัมน์
- `ignore_index=True` สร้าง row index ใหม่ แต่ไม่แก้ business key ซ้ำ

### ต่อคอลัมน์ `axis=1`

```python
wide = pd.concat([left, right], axis=1)
```

Pandas align ตาม index โดยอัตโนมัติ หากสองฝั่งมี index ต่างกันจะเกิด NA หากต้องการวางตามตำแหน่งต้อง reset index อย่างตั้งใจและยืนยันว่าลำดับแถวสอดคล้องจริง

## 8. Reshape: เปลี่ยนรูป ไม่ควรเปลี่ยนข้อเท็จจริง

Reshape เปลี่ยนการจัดวางข้อมูลระหว่าง long และ wide:

- **Long:** หนึ่ง observation ต่อแถว เหมาะกับ groupby, plotting และ tidy analysis
- **Wide:** category/time แยกเป็นหลายคอลัมน์ เหมาะกับรายงานและบาง model input

## 9. `pivot()` กับ `pivot_table()`

```python
wide = long_df.pivot(
    index='student',
    columns='subject',
    values='score'
)
```

`pivot()` ต้องมีค่าเดียวต่อ `(index, columns)` slot หากมีซ้ำจะเกิด `ValueError` ซึ่งเป็นสัญญาณว่า grain ไม่ตรงกับรูปที่ต้องการ—not a nuisance to suppress

เมื่อหนึ่ง slot มีหลาย record และมี business rule ให้สรุป ใช้ `pivot_table()`:

```python
wide = long_df.pivot_table(
    index='student',
    columns='subject',
    values='score',
    aggfunc='mean'
)
```

ความต่างสำคัญคือ `pivot_table` มี aggregation จึงอาจสูญเสียรายละเอียด ต้องประกาศ `aggfunc` และเหตุผลอย่างชัดเจน

## 10. Pivot table กับ GroupBy

สองวิธีอาจตอบคำถามเดียวกัน แต่ layout ต่างกัน:

```python
g = df.groupby(['team', 'season'])['points'].mean().reset_index()

p = df.pivot_table(
    index='team',
    columns='season',
    values='points',
    aggfunc='mean'
)
```

GroupBy แบบ long มักเหมาะกับการคำนวณต่อและ visual หลายประเภท ส่วน pivot แบบ wide เหมาะกับ matrix report อย่าเลือก pivot เพียงเพราะหน้าตาคล้าย Excel หากจะทำ time-series calculation ต่อ

## 11. `melt()`: wide กลับเป็น long

```python
long = wide.reset_index().melt(
    id_vars='student',
    var_name='subject',
    value_name='score'
)
```

`id_vars` คือคอลัมน์ที่คงไว้ ส่วนคอลัมน์อื่นถูกพับเป็นคู่ variable–value หลัง melt ต้องตรวจจำนวนแถวที่คาดว่าเพิ่มขึ้นและความหมายของ NA

## 12. Round-trip validation ของ reshape

หากไม่มี duplicate และไม่สูญเสียข้อมูล ควร pivot แล้ว melt กลับได้ใกล้เคียงเดิมหลังจัดเรียง:

```python
original = long_df.sort_values(['student', 'subject']).reset_index(drop=True)
roundtrip = (
    long_df.pivot(index='student', columns='subject', values='score')
    .reset_index()
    .melt(id_vars='student', var_name='subject', value_name='score')
    .dropna(subset=['score'])
    .sort_values(['student', 'subject'])
    .reset_index(drop=True)
)

pd.testing.assert_frame_equal(original, roundtrip)
```

## 13. Styling: แยกข้อมูลออกจากการนำเสนอ

```python
styled = (
    df.style
    .format('{:.2f}')
    .highlight_max(axis=0, props='color:white;background-color:darkblue;')
)
```

`styled` เป็น `Styler` ไม่ใช่ DataFrame จึงใช้วิเคราะห์ต่อแบบ DataFrame ไม่ได้ Styling ไม่เปลี่ยนค่าจริง เช่นการแสดง 2 ตำแหน่งไม่ได้ round ค่าในข้อมูล

Conditional styling มีสองระดับ:

- `.map(func)`: function รับทีละ cell และคืน CSS string
- `.apply(func, axis=...)`: function รับ Series/array ตาม axis และคืน style ที่จัดแนวได้

Built-in ที่ใช้บ่อย ได้แก่ `highlight_null`, `highlight_min`, `highlight_max`, `background_gradient` และ `bar` การใช้สีต้องคำนึงถึง contrast และไม่ใช้สีเป็นช่องทางเดียวในการสื่อสาร

## 14. End-to-end worked example

ตาราง order หนึ่งแถวต่อ order line และ customer หนึ่งแถวต่อลูกค้า:

```python
orders = pd.DataFrame({
    'order_id': ['O1', 'O1', 'O2'],
    'line_no': [1, 2, 1],
    'customer_id': ['C1', 'C1', 'C2'],
    'amount': [100, 50, 80]
})

customers = pd.DataFrame({
    'customer_id': ['C1', 'C2'],
    'segment': ['A', 'B']
})

enriched = orders.merge(
    customers,
    on='customer_id',
    how='left',
    validate='many_to_one',
    indicator=True
)
```

ตรวจ row count และ unmatched ก่อนสรุป:

```python
assert len(enriched) == len(orders)
assert enriched['_merge'].eq('both').all()

segment_summary = enriched.pivot_table(
    index='segment',
    values='amount',
    aggfunc='sum'
).reset_index()

assert segment_summary['amount'].sum() == orders['amount'].sum()
```

## 15. Failure modes และการวินิจฉัย

- จำนวนแถวเพิ่มหลัง lookup join → ตรวจ uniqueness ฝั่ง dimension และใช้ `validate='many_to_one'`
- inner join แล้วยอดหาย → ตรวจ unmatched key ด้วย outer/left join และ `indicator=True`
- concat แนวคอลัมน์เกิด NA → index ไม่ align
- pivot error duplicate entries → grain ต่อ slot ไม่ unique; กำหนด business aggregation ก่อน
- pivot_table ยอดไม่เท่าเดิม → ตรวจ NA keys, `aggfunc` และ margins/filter
- styled output ดูถูกแต่ค่าจริงผิด → validation ต้องทำกับ DataFrame ก่อน style

## 16. Likely Exam Focus

1. เลือก inner/left/right/outer ตาม population ที่ต้องรักษา
2. วิเคราะห์ cardinality และ row multiplication
3. แยก merge, join และ concat
4. แยก pivot กับ pivot_table และอธิบาย duplicate error
5. อธิบาย long/wide และ melt
6. แยก DataFrame ออกจาก Styler

## 17. แบบฝึกพร้อมเฉลย

### ข้อ 1

ต้องการเติมชื่อ vendor ลง fact purchase โดย vendor ID ใน dimension ควร unique ใช้อะไรตรวจ?

```python
fact.merge(
    dim_vendor,
    on='vendor_id',
    how='left',
    validate='many_to_one',
    indicator=True
)
```

### ข้อ 2

`pivot()` error ว่ามี duplicate entries ควรแก้อย่างไร?

**เฉลย:** ตรวจ grain และ record ที่ชน slot ก่อน หากเป็นข้อมูลซ้ำให้แก้ upstream; หากเป็นหลาย observation ที่ถูกต้อง ให้กำหนด aggregation ที่มีความหมายและใช้ `pivot_table()` ห้ามเลือก `mean` เพียงเพื่อให้ error หาย

### ข้อ 3

เหตุใด concat แนวคอลัมน์อาจได้ NA แม้ทั้งสองตารางไม่มี NA?

**เฉลย:** Pandas align ด้วย index หาก labels ไม่ตรงกันจึงสร้างช่องว่าง วิธีแก้ขึ้นกับความหมาย: join ด้วย key ที่ถูกต้อง หรือ reset index เมื่อพิสูจน์แล้วว่าลำดับแถวตรงกัน

## 18. Mini-project

รวม fact table กับ lookup อย่างน้อยหนึ่งชุดโดยประกาศ grain/cardinality ตรวจ unmatched และ row multiplication จากนั้นสร้าง summary แบบ long และ wide ทำ melt กลับ และ reconcile จำนวน record/ยอดรวม สุดท้ายตกแต่งตารางเพื่อสื่อสารโดยเก็บ DataFrame ต้นฉบับแยกจาก Styler

## 19. Mastery Checklist

- วาดความสัมพันธ์และคาดจำนวนแถวหลัง join ได้
- ใช้ `validate` และ `indicator` ตรวจ merge ได้
- เลือก merge/join/concat ตามกลไกที่ต้องการ
- แปลง long ↔ wide โดยอธิบาย aggregation และข้อมูลที่อาจสูญเสีย
- ตรวจผลด้วย row counts, uniqueness, unmatched analysis และ reconciliation
- แยก transformation ออกจาก presentation styling ได้

## References

- [Pandas merge, join and concatenate](https://pandas.pydata.org/docs/user_guide/merging.html)
- [Pandas reshaping](https://pandas.pydata.org/docs/user_guide/reshaping.html)
- [Pandas table visualization](https://pandas.pydata.org/docs/user_guide/style.html)

