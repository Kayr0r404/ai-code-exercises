from datetime import datetime


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
        report['grouping'] = _build_grouping_section(grouped, grouping, metrics['total_sales'])

    if report_type == 'detailed':
        report['transactions'] = _build_detailed_transactions(sales_data)

    if report_type == 'forecast':
        report['forecast'] = _calculate_forecast(sales_data)

    if include_charts:
        report['charts'] = _build_chart_data(sales_data, grouping, grouped)

    return _format_output(report, include_charts, output_format)


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

def _validate_inputs(sales_data, report_type, output_format):
    if not sales_data or not isinstance(sales_data, list):
        raise ValueError("Sales data must be a non-empty list")

    if report_type not in ['summary', 'detailed', 'forecast']:
        raise ValueError("Report type must be 'summary', 'detailed', or 'forecast'")

    if output_format not in ['pdf', 'excel', 'html', 'json']:
        raise ValueError("Output format must be 'pdf', 'excel', 'html', or 'json'")


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def _filter_by_date_range(sales_data, date_range):
    if not date_range:
        return sales_data

    if 'start' not in date_range or 'end' not in date_range:
        raise ValueError("Date range must include 'start' and 'end' dates")

    start_date = datetime.strptime(date_range['start'], '%Y-%m-%d')
    end_date = datetime.strptime(date_range['end'], '%Y-%m-%d')

    if start_date > end_date:
        raise ValueError("Start date cannot be after end date")

    return [
        sale for sale in sales_data
        if start_date <= datetime.strptime(sale['date'], '%Y-%m-%d') <= end_date
    ]


def _apply_filters(sales_data, filters):
    if not filters:
        return sales_data

    result = list(sales_data)
    for key, value in filters.items():
        if isinstance(value, list):
            result = [sale for sale in result if sale.get(key) in value]
        else:
            result = [sale for sale in result if sale.get(key) == value]
    return result


# ---------------------------------------------------------------------------
# Metrics and grouping
# ---------------------------------------------------------------------------

def _calculate_summary_metrics(sales_data):
    total_sales = sum(sale['amount'] for sale in sales_data)
    avg_sale = total_sales / len(sales_data)
    max_sale = max(sales_data, key=lambda x: x['amount'])
    min_sale = min(sales_data, key=lambda x: x['amount'])
    return {
        'total_sales': total_sales,
        'average_sale': avg_sale,
        'max_sale': max_sale,
        'min_sale': min_sale
    }


def _group_sales_data(sales_data, grouping):
    grouped = {}
    for sale in sales_data:
        key = sale.get(grouping, 'Unknown')
        if key not in grouped:
            grouped[key] = {'count': 0, 'total': 0, 'items': []}
        grouped[key]['count'] += 1
        grouped[key]['total'] += sale['amount']
        grouped[key]['items'].append(sale)

    for key in grouped:
        grouped[key]['average'] = grouped[key]['total'] / grouped[key]['count']

    return grouped


# ---------------------------------------------------------------------------
# Report section builders
# ---------------------------------------------------------------------------

def _build_base_report(report_type, date_range, filters, metrics, sales_data):
    return {
        'report_type': report_type,
        'date_generated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'date_range': date_range,
        'filters': filters,
        'summary': {
            'total_sales': metrics['total_sales'],
            'transaction_count': len(sales_data),
            'average_sale': metrics['average_sale'],
            'max_sale': {
                'amount': metrics['max_sale']['amount'],
                'date': metrics['max_sale']['date'],
                'details': metrics['max_sale']
            },
            'min_sale': {
                'amount': metrics['min_sale']['amount'],
                'date': metrics['min_sale']['date'],
                'details': metrics['min_sale']
            }
        }
    }


def _build_grouping_section(grouped_data, grouping, total_sales):
    groups = {}
    for key, data in grouped_data.items():
        groups[key] = {
            'count': data['count'],
            'total': data['total'],
            'average': data['average'],
            'percentage': (data['total'] / total_sales) * 100
        }

    return {'by': grouping, 'groups': groups}


def _build_detailed_transactions(sales_data):
    transactions = []
    for sale in sales_data:
        transaction = dict(sale)
        if 'tax' in sale and 'amount' in sale:
            transaction['pre_tax'] = sale['amount'] - sale['tax']
        if 'cost' in sale and 'amount' in sale:
            transaction['profit'] = sale['amount'] - sale['cost']
            transaction['margin'] = (transaction['profit'] / sale['amount']) * 100
        transactions.append(transaction)
    return transactions


# ---------------------------------------------------------------------------
# Forecast calculations
# ---------------------------------------------------------------------------

def _calculate_forecast(sales_data):
    monthly_sales = _aggregate_monthly_sales(sales_data)
    sorted_months = sorted(monthly_sales.keys())
    growth_rates = _compute_growth_rates(monthly_sales, sorted_months)
    avg_growth_rate = sum(growth_rates) / len(growth_rates) if growth_rates else 0
    projected_sales = _project_next_months(monthly_sales, sorted_months, avg_growth_rate)

    growth_rate_map = {}
    for i in range(1, len(sorted_months)):
        growth_rate_map[sorted_months[i]] = growth_rates[i - 1]

    return {
        'monthly_sales': monthly_sales,
        'growth_rates': growth_rate_map,
        'average_growth_rate': avg_growth_rate,
        'projected_sales': projected_sales
    }


def _aggregate_monthly_sales(sales_data):
    monthly = {}
    for sale in sales_data:
        sale_date = datetime.strptime(sale['date'], '%Y-%m-%d')
        month_key = f"{sale_date.year}-{sale_date.month:02d}"
        monthly[month_key] = monthly.get(month_key, 0) + sale['amount']
    return monthly


def _compute_growth_rates(monthly_sales, sorted_months):
    rates = []
    for i in range(1, len(sorted_months)):
        prev = monthly_sales[sorted_months[i - 1]]
        curr = monthly_sales[sorted_months[i]]
        if prev > 0:
            rates.append(((curr - prev) / prev) * 100)
    return rates


def _project_next_months(monthly_sales, sorted_months, avg_growth_rate):
    forecast = {}
    if not sorted_months:
        return forecast

    last_month = sorted_months[-1]
    last_amount = monthly_sales[last_month]
    year, month = map(int, last_month.split('-'))

    for _ in range(3):
        month += 1
        if month > 12:
            month = 1
            year += 1
        forecast_month = f"{year}-{month:02d}"
        forecast_amount = last_amount * (1 + (avg_growth_rate / 100))
        forecast[forecast_month] = forecast_amount
        last_amount = forecast_amount

    return forecast


# ---------------------------------------------------------------------------
# Chart data builders
# ---------------------------------------------------------------------------

def _build_chart_data(sales_data, grouping, grouped_data):
    charts = {}
    charts['sales_over_time'] = _build_time_series_chart(sales_data)

    if grouping:
        charts['sales_by_' + grouping] = _build_pie_chart(grouped_data)

    return charts


def _build_time_series_chart(sales_data):
    date_sales = {}
    for sale in sales_data:
        date_sales[sale['date']] = date_sales.get(sale['date'], 0) + sale['amount']

    labels = sorted(date_sales.keys())
    data = [date_sales[d] for d in labels]
    return {'labels': labels, 'data': data}


def _build_pie_chart(grouped_data):
    labels = list(grouped_data.keys())
    data = [grouped_data[k]['total'] for k in labels]
    return {'labels': labels, 'data': data}


# ---------------------------------------------------------------------------
# Empty data handler
# ---------------------------------------------------------------------------

def _handle_empty_data(report_type, output_format):
    print("Warning: No data matches the specified criteria")
    if output_format == 'json':
        return {"message": "No data matches the specified criteria", "data": []}
    return _generate_empty_report(report_type, output_format)


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def _format_output(report_data, include_charts, output_format):
    if output_format == 'json':
        return report_data
    elif output_format == 'html':
        return _generate_html_report(report_data, include_charts)
    elif output_format == 'excel':
        return _generate_excel_report(report_data, include_charts)
    elif output_format == 'pdf':
        return _generate_pdf_report(report_data, include_charts)


# ---------------------------------------------------------------------------
# Stub helpers (external rendering — not implemented)
# ---------------------------------------------------------------------------

def _generate_empty_report(report_type, output_format):
    pass

def _generate_html_report(report_data, include_charts):
    pass

def _generate_excel_report(report_data, include_charts):
    pass

def _generate_pdf_report(report_data, include_charts):
    pass
