import pandas as pd
import sqlite3

conn = sqlite3.connect(r'C:\Users\Dreid\Desktop\Brain\Projects\P3Adaptive Project\sales_data.db')
cursor = conn.cursor()

sales_df = pd.read_sql_query("SELECT * FROM sales", conn)

# check date/time formats
sales_df['OrderDate'] = pd.to_datetime(sales_df['OrderDate'])
sales_df['FirstOrderDate'] = pd.to_datetime(sales_df['FirstOrderDate'])


def calculate_is_first_order(df):
    df['IsFirstOrder'] = df['OrderDate'] == df['FirstOrderDate']
    return df

def calculate_first_time_report(df, conn):
    #shift format
    df['MonthYear'] = df['OrderDate'].dt.strftime('%b %y')

    
    report_by_month = df[df['IsFirstOrder']].groupby('MonthYear', as_index=False).agg(
        FirstTimeReport=('CustomerKey', 'count')
    )

    report_by_month.to_sql('ReportByMonth', conn, if_exists='replace', index=False)

    print("The 'ReportByMonth' table with 'FirstTimeReport' has been created and updated.")
    return report_by_month


def calculate_has_order_within_90_days(df):
    df['HasOrderWithin90Days'] = 0

    # through each customer
    for customer_key in df['CustomerKey'].unique():
        customer_orders = df[df['CustomerKey'] == customer_key].sort_values(by='OrderDate')

        # through each customers orders
        for index, row in customer_orders.iterrows():
            if row['IsFirstOrder']:
                first_order_date = row['OrderDate']

                within_90_days = customer_orders[
                    (customer_orders['OrderDate'] > first_order_date) &
                    (customer_orders['OrderDate'] <= first_order_date + pd.Timedelta(days=90))
                ]

                if not within_90_days.empty:
                    df.at[index, 'HasOrderWithin90Days'] = 1
    return df


def find_next_order_after_first(df, month_year='2003-07'):
    first_orders_in_month = df[(df['IsFirstOrder'] == True) & (df['OrderDate'].dt.strftime('%Y-%m') == month_year)]
    
    for _, first_order_row in first_orders_in_month.iterrows():
        customer_key = first_order_row['CustomerKey']
        first_order_date = first_order_row['OrderDate']
        
  
        customer_orders = df[(df['CustomerKey'] == customer_key) & (df['OrderDate'] > first_order_date)]
        next_order = customer_orders.sort_values(by='OrderDate').iloc[0] if not customer_orders.empty else None
        
        if next_order is not None:
            next_order_date = next_order['OrderDate']
            days_between = (next_order_date - first_order_date).days
            print(f'{customer_key} : FirstOrder {first_order_date} : Next Order {next_order_date} : {days_between} days')
        






sales_df = calculate_is_first_order(sales_df)
report_by_month_df = calculate_first_time_report(sales_df, conn) 
sales_df = calculate_has_order_within_90_days(sales_df)


#debug function
#find_next_order_after_first(sales_df)




#back to db
sales_df.to_sql('sales', conn, if_exists='replace', index=False)

conn.close()

print("The 'IsFirstOrder' column has been calculated and updated in the database.")