import pandas as pd
import sqlite3


data_sales = pd.read_excel(r'C:\Users\Dreid\Desktop\Brain\Projects\P3Adaptive Project\P3 Simulated Consulting Project.xlsx', sheet_name='Sales')
data_customer = pd.read_excel(r'C:\Users\Dreid\Desktop\Brain\Projects\P3Adaptive Project\P3 Simulated Consulting Project.xlsx', sheet_name='Customers')

conn = sqlite3.connect(r'C:\Users\Dreid\Desktop\Brain\Projects\P3Adaptive Project\sales_data.db')
cursor = conn.cursor()

db_within_90 = 'HasOrderWithin90Days'
db_first_order = 'FirstOrderDate'
db_table_sales = 'sales'


cursor.execute(f'PRAGMA table_info({db_table_sales})')
columns = cursor.fetchall()


data_sales['OrderDate'] = pd.to_datetime(data_sales['OrderDate'])

data_sales['MonthYear'] = data_sales['OrderDate'].dt.strftime('%b %y')

data_sales['Months'] = data_sales['OrderDate'].dt.to_period('M').dt.to_timestamp()

data = data_sales.sort_values(by=['CustomerKey', 'OrderDate'])


if any(db_first_order in col for col in columns):
    print(f"The column '{db_first_order}' already exists in the table '{db_table_sales}'.")
else:
    data_sales['FirstOrderDate'] = data_sales.groupby('CustomerKey')['OrderDate'].transform('min')

data_sales['IsFirstOrder'] = data_sales['OrderDate'] == data_sales['FirstOrderDate']
first_time_report = data_sales[data_sales['IsFirstOrder']].groupby('Months', as_index=False)['CustomerKey'].nunique()
first_time_report.rename(columns={'CustomerKey': 'FirstTimeReport'}, inplace=True)

# Merge 'FirstTimeReport' back into 'report_by_month'

if any(db_within_90 in col for col in columns):
    print(f"The column '{db_within_90}' already exists in the table '{db_table_sales}'.")
else:
    data_sales['HasOrderWithin90Days'] = data_sales.apply(
    lambda row: any(
        (data_sales['CustomerKey'] == row['CustomerKey']) & 
        (data_sales['OrderDate'] > row['FirstOrderDate']) & 
        (data_sales['OrderDate'] <= row['FirstOrderDate'] + pd.Timedelta(days=90))
    ) if row['IsFirstOrder'] else False,
    axis=1
)

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ReportByMonth'")
table_exists = cursor.fetchone()

if table_exists:
    print("The table 'ReportByMonth' already exists.")
else:
    report_by_month = data_sales.groupby('Months', as_index=False).agg(
        SumWithin90=('HasOrderWithin90Days', 'sum')
    )
    report_by_month = report_by_month.merge(first_time_report, on='Months', how='left')

    # Fill NaN values with 0 (in case there are months with no first orders)
    report_by_month['FirstTimeReport'].fillna(0, inplace=True)

    
    
    report_by_month['MonthYear'] = report_by_month['Months'].dt.strftime('%b %y')

    report_by_month['Percentage90'] = report_by_month.apply(
        lambda row: row['SumWithin90'] / row['FirstTimeReport'] if row['FirstTimeReport'] != 0 else 0,
        axis=1
    )
    report_by_month.to_sql('ReportByMonth', conn, if_exists='replace', index=False)
    print("The table 'ReportByMonth' has been created and populated.")


data_sales.to_sql('sales', conn, if_exists='replace', index=False)
conn.close()

data_sales.head()