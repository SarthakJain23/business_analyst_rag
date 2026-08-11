# Excel & CSV Loader Guidelines & Explanation (`excel_loader.py`)

## Overview

The [`excel_loader.py`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader/excel_loader.py) module provides the `ExcelCSVLoader` class, which handles parsing of tabular files (`.csv`, `.xlsx`, `.xls`). It converts structured data into Markdown formatted tables so LLMs and vector stores can accurately interpret row-column relationships and financial data points.

## Class Definition

`ExcelCSVLoader` inherits from [`BaseLoader`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base/base.py#L20) and implements the `load(file_path: Path, file_hash: str) -> List[RawDocument]` interface method.

---

## Detailed Code Flow & Guidelines

### 1. File Type Detection (`load` method)

- Extracts the lower-case file extension `ext = file_path.suffix.lower()` ([excel_loader.py:L14](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader/excel_loader.py#L14)).

### 2. Processing CSV Files (`.csv`)

- **Reading Data**: Reads the file using `pd.read_csv(file_path)` ([excel_loader.py:L18](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader/excel_loader.py#L18)).
- **Cleaning**: Drops entirely blank rows using `df.dropna(how="all")` ([excel_loader.py:L19](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader/excel_loader.py#L19)).
- **Markdown Conversion**: Formats dataframe as a Markdown table via `df.to_markdown(index=False)` ([excel_loader.py:L20](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader/excel_loader.py#L20)).
- **Metadata Construction**: Constructs metadata dictionary containing `source_file`, `file_name`, `file_type`, `file_hash`, `page_or_section: "CSV Data"`, and `row_count` ([excel_loader.py:L21-L28](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader/excel_loader.py#L21-L28)).
- **Output**: Wraps content and metadata inside a [`RawDocument`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base/base.py#L6) instance.

### 3. Processing Excel Workbooks (`.xlsx`, `.xls`)

- **Workbook Reading**: Opens the workbook using `pd.ExcelFile(file_path)` ([excel_loader.py:L32](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader/excel_loader.py#L32)).
- **Multi-Sheet Handling**: Loops through each sheet in `excel_file.sheet_names` ([excel_loader.py:L33](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader/excel_loader.py#L33)).
- **Per-Sheet Parsing**: Loads data with `pd.read_excel(excel_file, sheet_name=sheet_name)` and drops empty rows ([excel_loader.py:L34-L35](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader/excel_loader.py#L34-L35)).
- **Formatting**: Prefixes sheet header (`# Sheet: {sheet_name}\n\n`) followed by Markdown table syntax ([excel_loader.py:L37](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader/excel_loader.py#L37)).
- **Per-Sheet Metadata**: Creates a separate [`RawDocument`](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/base/base.py#L6) for each non-empty sheet with `page_or_section: f"Sheet: {sheet_name}"` ([excel_loader.py:L38-L46](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader/excel_loader.py#L38-L46)).

### 4. Logging & Error Handling

- Logs success message upon completion ([excel_loader.py:L48](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader/excel_loader.py#L48)).
- Logs errors and re-raises exceptions if parsing fails ([excel_loader.py:L49-L51](file:///Users/sarthakjain/Desktop/Personal/business_analyst_rag/src/loaders/excel_loader/excel_loader.py#L49-L51)).
