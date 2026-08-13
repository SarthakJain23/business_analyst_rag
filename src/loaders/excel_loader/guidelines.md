# Excel & CSV Loader Guidelines (`excel_loader.py`)

## Folder & File Context

The [`src/loaders/excel_loader/`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader) directory contains [`excel_loader.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader/excel_loader.py), which defines [`ExcelCSVLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader/excel_loader.py#L13-L56).

It parses tabular data files (`.csv`, `.xlsx`, `.xls`) using `pandas` and `tabulate`, converting rows and columns into clean Markdown tables so Gemini and ChromaDB vector search can accurately process financial tables, metrics, and structured reports.

---

## Detailed Code Explanation & Method Breakdown

### Class: [`ExcelCSVLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader/excel_loader.py#L13-L56)

- **Inheritance**: Inherits from [`BaseLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base/base.py#L8-L14).
- **Method**: [`load(file_path: Path, file_hash: str) -> List[Document]`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader/excel_loader.py#L16-L56):
  - **CSV Handling (`.csv`)** ([L21-L33](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader/excel_loader.py#L21-L33)):
    1. Reads file via `pd.read_csv(file_path)`.
    2. Drops fully blank rows using `df.dropna(how="all")`.
    3. Formats dataframe into a Markdown table string using `df.to_markdown(index=False)`.
    4. Attaches metadata: `page_or_section: "CSV Data"`, `row_count: len(df)`.
  - **Excel Handling (`.xlsx`, `.xls`)** ([L34-L49](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader/excel_loader.py#L34-L49)):
    1. Opens workbook with `pd.ExcelFile(file_path)`.
    2. Iterates over `excel_file.sheet_names`.
    3. Reads sheet data into DataFrame, drops blank rows, and formats content with header `# Sheet: {sheet_name}\n\n` + Markdown table.
    4. Creates a distinct `Document` per non-empty sheet with metadata: `page_or_section: f"Sheet: {sheet_name}"`, `row_count: len(df)`.
