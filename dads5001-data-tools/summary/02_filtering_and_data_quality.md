# Pandas Filtering and Data Quality

> Source: `lab_02_pandas2.ipynb`  
> Scope: conditional selection/change, string and datetime filtering, missing values และ duplicate records

## 1. ภาพรวม

การวิเคราะห์ที่ดีเริ่มจากการกำหนดประชากรที่ต้องการอย่างชัดเจน แล้วตรวจว่าข้อมูลในประชากรนั้นครบ ถูกชนิด และไม่ซ้ำ การกรองจึงไม่ใช่เพียง syntax แต่เป็นการแปลงนิยามทางธุรกิจให้เป็น Boolean mask ที่ตรวจสอบได้

## 2. Boolean mask คืออะไร

Boolean mask คือ Series ที่มี `True`/`False` หนึ่งค่าต่อหนึ่งแถว `True` หมายถึงแถวนั้นผ่านเงื่อนไข

```python
mask = pokemon['type1'].eq('grass')
grass = pokemon.loc[mask].copy()
```

ใช้ `.copy()` เมื่อจะปรับ subset ต่อ เพื่อให้เจตนาชัดและลดปัญหา chained assignment

```python
grass = pokemon[pokemon['type1'] == 'grass']
grass = pokemon.query("type1 == 'grass'")
```

ทั้งสองแบบให้แนวคิดเดียวกัน `query()` อ่านคล้ายประโยค แต่เมื่อชื่อคอลัมน์มีช่องว่างต้องครอบด้วย backticks และตัวแปรภายนอกต้องนำหน้าด้วย `@`

```python
selected_type = 'grass'
pokemon.query('type1 == @selected_type')
```

## 3. หลายเงื่อนไขและ precedence

```python
mask = (
    pokemon['type1'].isin(['grass', 'fire'])
    & pokemon['hp'].ge(60)
    & pokemon['weight_kg'].notna()
)
result = pokemon.loc[mask]
```

ใน Pandas ใช้ `&`, `|`, `~` แทน `and`, `or`, `not` และต้องใส่วงเล็บรอบแต่ละเงื่อนไข เพราะ operator precedence อาจทำให้ expression ถูกตีความผิด

การตรวจ population:

```python
assert len(result) == mask.sum()
assert result['type1'].isin(['grass', 'fire']).all()
```

## 4. String filtering และ regular expression

```python
pokemon.loc[pokemon['name'].str.startswith('Char', na=False)]
pokemon.loc[pokemon['abilities'].str.contains('blaze', case=False, na=False)]
pokemon.loc[pokemon['name'].str.contains(r'^char|bug\Z', case=False, na=False)]
```

`na=False` กำหนดให้ missing string ไม่ผ่านเงื่อนไข มิฉะนั้น mask อาจมี `NA` Regex `^` หมายถึงต้นข้อความและ `\Z` หมายถึงท้ายข้อความ ต้องแยกให้ออกจาก literal substring

ถ้าค้นหาข้อความที่ผู้ใช้ป้อนและไม่ต้องการ regex ให้ใช้ `regex=False` เพื่อป้องกันอักขระพิเศษถูกตีความเป็น pattern

## 5. Datetime filtering

ข้อความวันที่ต้องแปลงก่อนจึงใช้ `.dt` ได้

```python
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df['year'] = df['date'].dt.year

mask = df['date'].between('2010-01-01', '2022-12-31')
period = df.loc[mask]
```

`errors='coerce'` เปลี่ยนค่าที่ parse ไม่ได้เป็น `NaT` จึงต้องนับค่าที่เสียหลัง conversion

```python
invalid_count = df['date'].isna().sum()
```

การคำนวณอายุด้วยปีปัจจุบันลบปีเกิดเป็น approximation เพราะยังไม่ดูว่าในปีนี้ผ่านวันเกิดหรือยัง งานจริงควรเปรียบเทียบเดือนและวันด้วย

## 6. Conditional assignment

```python
out = pokemon.copy()
out.loc[out['type1'].eq('dark'), 'type1'] = 'black'
```

เมื่อแก้หลายคอลัมน์ ค่าด้านขวาต้องมี shape ที่สอดคล้องกับพื้นที่ด้านซ้าย

```python
mask = out['type1'].eq('black')
out.loc[mask, ['type1', 'type3']] = ['dark', 'shadow']
```

หลังแก้ควรตรวจทั้งจำนวนแถวที่เปลี่ยนและค่าใหม่ ไม่ใช่ดูด้วยสายตาเพียงไม่กี่แถว

## 7. Column filtering

Boolean mask ใช้กับคอลัมน์ได้เมื่อความยาวเท่าจำนวนคอลัมน์:

```python
mask = ~pokemon.columns.str.contains('against_')
selected = pokemon.loc[:, mask]
```

`filter()` กรองตาม label ไม่ได้กรองค่าภายใน cell:

```python
pokemon.filter(items=['name', 'hp'])
pokemon.filter(like='against_')
pokemon.filter(regex=r'(^name\Z|fairy)')
```

เลือกตาม dtype:

```python
numeric = pokemon.select_dtypes(include='number')
text = pokemon.select_dtypes(include=['object', 'string'])
```

## 8. Missing data workflow

Missing value อาจหมายถึง “ไม่ทราบ”, “ไม่เกี่ยวข้อง”, “ยังไม่เกิด” หรือ “ระบบเสีย” ซึ่งมีความหมายต่างกัน ต้องเข้าใจสาเหตุก่อนเลือก drop หรือ fill

### 8.1 Detect และ count

```python
pokemon.isna().sum()
pokemon.notna().sum()
pokemon.isna().sum(axis=1)
```

`df.isna()` ให้ DataFrame Boolean ไม่สามารถนำไปเลือกแถวตรง ๆ ได้ ต้องยุบตามแถวก่อน:

```python
rows_with_na = pokemon.loc[pokemon.isna().any(axis=1)]
complete_rows = pokemon.loc[pokemon.notna().all(axis=1)]
```

### 8.2 Drop

```python
clean = pokemon.dropna(subset=['height_m', 'weight_kg'])
strict = pokemon.dropna(how='any')
```

การ drop อาจเปลี่ยนประชากรและสร้าง selection bias ต้องรายงานจำนวนและสัดส่วนที่หายไป

### 8.3 Fill

```python
filled = pokemon.copy()
filled['type2'] = filled['type2'].fillna('none')
filled['height_m'] = filled['height_m'].fillna(filled['height_m'].median())
```

Median ทนต่อ outlier กว่า mean แต่ไม่ใช่คำตอบสากล การเติมค่าทำให้ distribution และความไม่แน่นอนเปลี่ยน ควรเพิ่ม flag หากการที่ค่า missing มีความหมาย

```python
filled['height_missing'] = filled['height_m'].isna()
```

## 9. Duplicate data

Duplicate ต้องนิยามผ่าน grain และ key ไม่ใช่ดูว่าทั้งแถวเหมือนกันอย่างเดียว

```python
pokemon.duplicated().sum()
pokemon.duplicated(subset=['pokedex_number'], keep=False)
```

ความหมาย `keep`:

| ค่า | ผล |
|---|---|
| `'first'` | ตัวแรกไม่ถือว่าซ้ำ ตัวถัดไปเป็นซ้ำ |
| `'last'` | ตัวสุดท้ายไม่ถือว่าซ้ำ ตัวก่อนหน้าเป็นซ้ำ |
| `False` | ทำเครื่องหมายทุกสมาชิกในกลุ่มซ้ำ |

```python
deduped = pokemon.drop_duplicates(
    subset=['pokedex_number'],
    keep='first'
)
```

อย่า deduplicate ก่อนกำหนดกฎเลือก record เช่น latest timestamp, data source priority หรือ completeness score มิฉะนั้นอาจทิ้ง record ที่ถูกต้องกว่า

## 10. Type conversion failure: บทเรียนจาก `capture_rate`

คอลัมน์ที่ดูเหมือนตัวเลขอาจถูกอ่านเป็น `object` เพราะมีข้อความปน จึงเปรียบเทียบ `> 90` ไม่ได้อย่างปลอดภัย

```python
capture_rate_num = pd.to_numeric(
    pokemon['capture_rate'],
    errors='coerce'
)

bad_values = pokemon.loc[
    capture_rate_num.isna() & pokemon['capture_rate'].notna(),
    'capture_rate'
].unique()
```

ลำดับที่ถูกคือแปลง → ตรวจค่าที่แปลงไม่ได้ → ตัดสินใจแก้ → จึงกรอง ไม่ควรใช้ `errors='coerce'` แล้วเงียบ เพราะอาจซ่อนปัญหาข้อมูล

## 11. Guided Lab: quality pipeline

```python
orders = pd.DataFrame({
    'order_id': ['A1', 'A1', 'A2', 'A3'],
    'order_date': ['2026-01-01', '2026-01-01', 'bad', '2026-02-01'],
    'amount': ['100', '100', 'unknown', '250']
})

orders['order_date'] = pd.to_datetime(orders['order_date'], errors='coerce')
orders['amount_num'] = pd.to_numeric(orders['amount'], errors='coerce')
```

ตรวจ:

```python
assert orders['order_date'].isna().sum() == 1
assert orders['amount_num'].isna().sum() == 1
assert orders.duplicated('order_id', keep=False).sum() == 2
```

ก่อนลบ A1 ซ้ำ ต้องยืนยันว่าเป็น duplicate จริง ไม่ใช่สอง order lines ที่ใช้ order_id เดียวกัน หาก grain คือหนึ่งแถวต่อรายการสินค้า key ต้องรวม line number ด้วย

## 12. Likely Exam Focus

- สร้างและอธิบาย Boolean mask แบบหลายเงื่อนไข
- แยก `filter()` ตาม label ออกจากการกรองค่าด้วย mask
- ใช้ `.str`, regex และ `.dt` อย่างปลอดภัย
- เปรียบเทียบ drop กับ imputation และผลต่อ bias
- อธิบาย `duplicated(..., keep=...)`
- debug คอลัมน์ตัวเลขที่ถูกอ่านเป็น `object`

## 13. แบบฝึกพร้อมเฉลย

### ข้อ 1

เลือกแถวที่ `hp >= 80` และ `type2` ไม่ว่าง

```python
df.loc[df['hp'].ge(80) & df['type2'].notna()]
```

### ข้อ 2

ทำไม `df['a'] > 1 & df['b'] < 5` จึงผิด?

**เฉลย:** ต้องใส่วงเล็บแต่ละ comparison เพราะ precedence: `(df['a'] > 1) & (df['b'] < 5)`

### ข้อ 3

จะพิสูจน์ได้อย่างไรว่าการลบ duplicate ไม่ทำยอดรวมผิด?

**เฉลย:** กำหนด grain/key และกฎเลือก record ก่อน จากนั้นเปรียบเทียบจำนวน key, จำนวนแถว และยอดรวมก่อน–หลัง พร้อมตรวจกลุ่มซ้ำเป็นตัวอย่าง หากยอดซ้ำเป็นธุรกรรมจริงห้ามลบ

## 14. Mastery Checklist

- แปลงนิยามประชากรเป็น Boolean mask และตรวจกลับได้
- แยกปัญหา missing, invalid dtype และ duplicate ได้
- เลือก drop/fill โดยอธิบายผลต่อประชากรและ bias
- ตรวจข้อมูลที่สูญเสียจาก conversion ได้
- กำหนด duplicate ด้วย grain/key ไม่ใช่ด้วยหน้าตา record

## References

- [Pandas Boolean indexing](https://pandas.pydata.org/docs/user_guide/indexing.html#boolean-indexing)
- [Pandas working with missing data](https://pandas.pydata.org/docs/user_guide/missing_data.html)
- [Pandas text data](https://pandas.pydata.org/docs/user_guide/text.html)
