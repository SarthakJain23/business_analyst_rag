# Code Explanation: `excel_loader.py`

## Overview
The [`excel_loader.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader.py) module provides the `ExcelCSVLoader` class, which handles parsing of tabular files (`.csv`, `.xlsx`, `.xls`). It converts structured data into Markdown formatted tables so LLMs and vector stores can accurately interpret row-column relationships and financial data points.

## Class Definition
`ExcelCSVLoader` inherits from [`BaseLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base.py#L23) and implements the `load(file_path: Path, file_hash: str) -> List[RawDocument]` interface method.

---

## Detailed Code Flow

### 1. File Type Detection (`load` method)
- Extracts the lower-case file extension `ext = file_path.suffix.lower()` ([excel_loader.py:L17](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader.py#L17)).

### 2. Processing CSV Files (`.csv`)
- **Reading Data**: Reads the file using `pd.read_csv(file_path)` ([excel_loader.py:L21](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader.py#L21)).
- **Cleaning**: Drops entirely blank rows using `df.dropna(how="all")` ([excel_loader.py:L22](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader.py#L22)).
- **Markdown Conversion**: Formats dataframe as a Markdown table via `df.to_markdown(index=False)` ([excel_loader.py:L23](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader.py#L23)).
- **Metadata Construction**: Constructs metadata dictionary containing `source_file`, `file_name`, `file_type`, `file_hash`, `page_or_section: "CSV Data"`, and `row_count` ([excel_loader.py:L24-L31](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader.py#L24-L31)).
- **Output**: Wraps content and metadata inside a [`RawDocument`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base.py#L8) instance.

### 3. Processing Excel Workbooks (`.xlsx`, `.xls`)
- **Workbook Reading**: Opens the workbook using `pd.ExcelFile(file_path)` ([excel_loader.py:L35](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader.py#L35)).
- **Multi-Sheet Handling**: Loops through each sheet in `excel_file.sheet_names` ([excel_loader.py:L36](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader.py#L36)).
- **Per-Sheet Parsing**: Loads data with `pd.read_excel(excel_file, sheet_name=sheet_name)` and drops empty rows ([excel_loader.py:L37-L38](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader.py#L37-L38)).
- **Formatting**: Prefixes sheet header (`# Sheet: {sheet_name}\n\n`) followed by Markdown table syntax ([excel_loader.py:L40](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader.py#L40)).
- **Per-Sheet Metadata**: Creates a separate [`RawDocument`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base.py#L8) for each non-empty sheet with `page_or_section: f"Sheet: {sheet_name}"` ([excel_loader.py:L41-L49](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader.py#L41-L49)).

### 4. Logging & Error Handling
- Logs success message upon completion ([excel_loader.py:L51](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader.py#L51)).
- Logs errors and re-raises exceptions if parsing fails ([excel_loader.py:L52-L54](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader.py#L52-L54)).
