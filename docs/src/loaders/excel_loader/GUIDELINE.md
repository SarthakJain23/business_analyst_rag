# 📄 Guideline: `src/loaders/excel_loader/excel_loader.py` — Excel/CSV Loader

> **File**: [`excel_loader.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader/excel_loader.py)
> **Lines**: 57 | **Role**: Loads `.xlsx`, `.xls`, and `.csv` files into LangChain Documents
> **Module**: `src.loaders.excel_loader`

---

## 1. High-Level Overview

### Purpose
`ExcelCSVLoader` handles tabular data files — both Excel workbooks (multi-sheet) and CSV files. It converts each sheet/file into a **markdown table** representation using Pandas, making structured data readable by the LLM.

### Design Patterns Used
| Pattern | Usage |
|---------|-------|
| **Strategy** | Concrete implementation of `BaseLoader` for tabular files |
| **Adapter** | Adapts Pandas DataFrames to LangChain Document format via `df.to_markdown()` |

---

## 2. Dependencies & Imports

| Import | Purpose |
|--------|---------|
| `pandas` | DataFrame operations, CSV/Excel reading, markdown conversion |
| `langchain_core.documents.Document` | LangChain document data structure |
| `src.loaders.base.base.BaseLoader` | Abstract interface |
| `src.utils.logger` | Logging |

**Implicit dependency**: `openpyxl` (required by Pandas for `.xlsx` reading)

---

## 3. Low-Level Breakdown

### 3.1 `ExcelCSVLoader.load()` Method (Lines 16–56)

The method branches on file extension:

#### CSV Path (Lines 21–33)
```python
if ext == ".csv":
    df = pd.read_csv(file_path)
    df = df.dropna(how="all")
    markdown_table = df.to_markdown(index=False)
```
1. Reads entire CSV into a DataFrame
2. Drops rows where **all** values are NaN (empty rows)
3. Converts to markdown table format
4. Creates single `Document` with `page_or_section: "CSV Data"`
5. Includes `row_count` in metadata

#### Excel Path (Lines 34–49)
```python
else:
    excel_file = pd.ExcelFile(file_path)
    for sheet_name in excel_file.sheet_names:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
```
1. Opens Excel file once (`pd.ExcelFile`)
2. Iterates all sheet names
3. For each non-empty sheet:
   - Drops all-NaN rows
   - Adds a `# Sheet: {name}` header
   - Converts to markdown table
   - Creates a **separate `Document`** per sheet
   - Sets `page_or_section: f"Sheet: {sheet_name}"`

---

## 4. Data Flow

```
.csv file                     .xlsx/.xls file
    │                              │
    ▼                              ▼
pd.read_csv()               pd.ExcelFile()
    │                              │
    ▼                         ┌────┤────┐
df.dropna()                  │ Sheet 1  │ Sheet 2 ...
    │                         ▼         ▼
    ▼                    pd.read_excel() per sheet
df.to_markdown()              │
    │                         ▼
    ▼                    df.to_markdown()
Document(                     │
  "| col1 | col2 |..."       ▼
)                        Document per sheet
```

### Example Output
For a CSV file `revenue.csv`:
```markdown
|   Quarter |   Revenue |   Growth |
|-----------|-----------|----------|
|   Q1 2025 |    1500.0 |      5.2 |
|   Q2 2025 |    1620.0 |      8.0 |
```

---

## 5. Improvement Suggestions

| Area | Issue | Suggestion |
|------|-------|------------|
| **Large Files** | Entire file loaded into memory; very large CSVs may cause OOM | Add row-limit option or chunk-based reading with `pd.read_csv(chunksize=)` |
| **Data Types** | Datetime columns may not render well in markdown | Add type-specific formatting for dates, currencies, percentages |
| **Column Stats** | No summary statistics provided | Optionally append `df.describe().to_markdown()` as additional context |
| **Encoding** | CSV encoding defaults to system locale | Add `encoding` parameter (e.g., `utf-8`, `latin-1`) |
| **Empty Sheets** | Empty sheets are silently skipped | Log a warning for empty sheets |
| **Merged Cells** | Excel merged cells can produce unexpected results | Document this limitation or handle with `openpyxl` directly |
