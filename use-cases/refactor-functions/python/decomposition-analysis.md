# Function Decomposition Analysis — Sales Report Generator

## Selected function

`generate_sales_report` in `python/sales_report.py` — 267 lines, single monolithic function.

---

## Step 1: Identifying distinct responsibilities

The function performs these distinct tasks in sequence:

| # | Responsibility | Lines | Can extract? |
|---|---------------|-------|-------------|
| 1 | **Validate inputs** — check sales_data, report_type, output_format | 22-30 | Yes |
| 2 | **Filter by date range** — parse dates, filter list | 32-50 | Yes |
| 3 | **Apply additional filters** — key/value or list matching | 52-58 | Yes |
| 4 | **Handle empty results** — return empty report structure | 60-68 | Yes |
| 5 | **Calculate summary metrics** — total, avg, min, max | 70-74 | Yes |
| 6 | **Group data** — build grouped_data dict with totals/averages | 76-94 | Yes |
| 7 | **Build summary report structure** — assemble report_data dict | 96-117 | Yes |
| 8 | **Add grouping to report** — attach groups with percentages | 119-132 | Yes |
| 9 | **Build detailed transactions** — enrich with pre_tax/profit/margin | 134-149 | Yes |
| 10 | **Calculate forecast** — monthly aggregation, growth rates, projections | 151-209 | Yes |
| 11 | **Generate chart data** — time series + pie chart | 211-240 | Yes |
| 12 | **Format output** — json/html/excel/pdf dispatch | 242-250 | No (calls existing helpers) |

**Total: 12 responsibilities in one function.**

---

## Step 2: Decomposition plan

### Phase 1 — Extract pure helper functions (no side effects)

Extract these first since they transform data without touching the report structure:

1. `_validate_inputs(sales_data, report_type, output_format)` — raises on invalid
2. `_filter_by_date_range(sales_data, date_range)` → filtered list
3. `_apply_filters(sales_data, filters)` → filtered list
4. `_calculate_summary_metrics(sales_data)` → dict with total, avg, min, max
5. `_group_sales_data(sales_data, grouping)` → grouped dict
6. `_build_summary_section(total_sales, avg_sale, max_sale, min_sale, count)` → summary dict
7. `_build_grouping_section(grouped_data, grouping, total_sales)` → grouping dict
8. `_build_detailed_transactions(sales_data)` → list of enriched transactions
9. `_calculate_forecast(sales_data)` → forecast dict
10. `_build_chart_data(sales_data, grouping, grouped_data)` → charts dict
11. `_handle_empty_data(report_type, output_format)` — early return

### Phase 2 — Orchestrator becomes thin

After extraction, `generate_sales_report` calls helpers in sequence, passing data down. No helper modifies shared state — each returns a value.

---

## Step 3: Extracted helper functions

See `sales_report_refactored.py` for the full implementation. Key extractions:

### `_validate_inputs`
```python
def _validate_inputs(sales_data, report_type, output_format):
    if not sales_data or not isinstance(sales_data, list):
        raise ValueError("Sales data must be a non-empty list")
    if report_type not in ['summary', 'detailed', 'forecast']:
        raise ValueError("...")
    if output_format not in ['pdf', 'excel', 'html', 'json']:
        raise ValueError("...")
```
**Why:** Separates input validation from business logic. If validation rules change, only this function changes.

### `_filter_by_date_range`
```python
def _filter_by_date_range(sales_data, date_range):
    if not date_range:
        return sales_data
    if 'start' not in date_range or 'end' not in date_range:
        raise ValueError("Date range must include 'start' and 'end' dates")
    start = datetime.strptime(date_range['start'], '%Y-%m-%d')
    end = datetime.strptime(date_range['end'], '%Y-%m-%d')
    if start > end:
        raise ValueError("Start date cannot be after end date")
    return [s for s in sales_data if start <= datetime.strptime(s['date'], '%Y-%m-%d') <= end]
```
**Why:** The `date_range` parsing and validation logic was nested inside an `if` block. Extracting it makes the boundary between "validate then filter" explicit.

### `_calculate_summary_metrics`
```python
def _calculate_summary_metrics(sales_data):
    total = sum(s['amount'] for s in sales_data)
    avg = total / len(sales_data)
    max_sale = max(sales_data, key=lambda x: x['amount'])
    min_sale = min(sales_data, key=lambda x: x['amount'])
    return {'total': total, 'avg': avg, 'max': max_sale, 'min': min_sale}
```
**Why:** Pure data transformation. The most reusable function across the entire report system — any reporting feature would need these metrics.

### `_build_detailed_transactions`
```python
def _build_detailed_transactions(sales_data):
    transactions = []
    for sale in sales_data:
        t = dict(sale)
        if 'tax' in t and 'amount' in t:
            t['pre_tax'] = t['amount'] - t['tax']
        if 'cost' in t and 'amount' in t:
            t['profit'] = t['amount'] - t['cost']
            t['margin'] = (t['profit'] / t['amount']) * 100
        transactions.append(t)
    return transactions
```
**Why:** The enriched transaction logic was inline inside the `if report_type == 'detailed'` block. Extracting it makes the enrichment logic independently testable.

### `_calculate_forecast`
This was the largest extraction — 58 lines reduced to a single call. The logic for monthly aggregation, growth rate calculation, and 3-month projection is entirely self-contained.

---

## Step 4: Refactored orchestrator

After extraction, `generate_sales_report` becomes a thin composition of helpers:

```python
def generate_sales_report(sales_data, report_type='summary', date_range=None,
                          filters=None, grouping=None, include_charts=False,
                          output_format='pdf'):
    _validate_inputs(sales_data, report_type, output_format)
    sales_data = _filter_by_date_range(sales_data, date_range)
    sales_data = _apply_filters(sales_data, filters)

    if not sales_data:
        return _handle_empty_data(report_type, output_format)

    metrics = _calculate_summary_metrics(sales_data)
    grouped = _group_sales_data(sales_data, grouping) if grouping else {}

    report = _build_base_report(report_type, date_range, filters, metrics, sales_data)

    if grouping:
        report['grouping'] = _build_grouping_section(grouped, grouping, metrics['total'])

    if report_type == 'detailed':
        report['transactions'] = _build_detailed_transactions(sales_data)

    if report_type == 'forecast':
        report['forecast'] = _calculate_forecast(sales_data)

    if include_charts:
        report['charts'] = _build_chart_data(sales_data, grouping, grouped)

    return _format_output(report, include_charts, output_format)
```

**Key property:** The orchestrator is a sequence of data transformations. No function modifies shared state. Each function takes data in, returns data out. This is the core principle of functional decomposition.

---

## Step 5: Running tests

```bash
cd python
cp sales_report.py sales_report_original.py.bak  # backup
cp sales_report_refactored.py sales_report.py     # deploy refactored
python -m unittest test_sales_report -v
```

All 8 tests pass:
```
test_additional_filters ... ok
test_date_range_filtering ... ok
test_detailed_report ... ok
test_empty_data_after_filtering ... ok
test_forecast_report ... ok
test_grouped_data ... ok
test_include_charts ... ok
test_summary_report ... ok
```

---

## Reflection

### How did breaking down the function improve readability and maintainability?

The original `generate_sales_report` was 267 lines with 12 responsibilities. Reading it required holding the entire function in your head at once. After decomposition:

- **The orchestrator is 25 lines** — you can understand the entire pipeline in 30 seconds
- **Each helper is independently testable** — you can test `_calculate_forecast` without setting up filters, charts, and output formatting
- **Changes are isolated** — if the forecast algorithm changes, you edit `_calculate_forecast` without touching filtering, grouping, or charts

### What was the most challenging part of decomposing the function?

The **forecast** section was the hardest because it has internal state accumulation — building `monthly_sales`, then iterating sorted months to compute growth rates, then using those rates to project forward. I initially tried to extract it as three separate functions (`_aggregate_monthly`, `_compute_growth_rates`, `_generate_projection`), but the intermediate data (sorted months, growth rates) needed to flow through all three. The final version keeps it as one function since the three steps are tightly coupled.

The **report data assembly** (lines 96-117) was also tricky because it produces a dict that multiple subsequent sections (grouping, detailed, forecast, charts) all append to. Extracting independent builder functions that each return their own dict subsection, then merging in the orchestrator, was cleaner than having each helper mutate a shared `report_data` reference.

### Which extracted function would be most reusable in other contexts?

`_calculate_summary_metrics` is the most reusable — it computes total, average, min, max from any list of dicts with an `amount` key. This pattern appears in dashboards, invoices, expense reports, and analytics pipelines. The second most reusable is `_build_chart_data` — any reporting tool that needs time-series and pie chart data could use it.

### Most valuable insight

The **orchestrator pattern** — a thin function that calls named helpers in sequence — is far more maintainable than nested conditionals. Adding a new report type (e.g., `'comparison'` that compares two time periods) would require adding one helper function and one `if` branch in the orchestrator, with zero risk of breaking the existing report types.
