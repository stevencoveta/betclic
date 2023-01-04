import pandas as pd 
import numpy as np
import streamlit as st 
from google.cloud import bigquery
from google.oauth2 import service_account
import matplotlib.pyplot as plt
import altair as alt
from pretty_numbers import *

credentials = service_account.Credentials.from_service_account_file(
        "keyfile.json", scopes=["https://www.googleapis.com/auth/cloud-platform"]
                  )
client = bigquery.Client(credentials=credentials, project=credentials.project_id,)

total_bettors = """
Select count(*) as count_bettors
 from(
SELECT t.CUSTOMER_ID as customers_id , sum(cast(replace(BET_AMOUNT,",",".") as float64)) as total_bet_amount
FROM `bclic-371311.data.daily_transaction` t
LEFT JOIN `bclic-371311.data.customers` c ON t.CUSTOMER_ID = c.CUSTOMER_ID
LEFT JOIN `bclic-371311.data.ref_country` r ON c.CUSTOMER_COUNTRY_CODE = r.CUSTOMER_COUNTRY_CODE
group by t.CUSTOMER_ID
having total_bet_amount > 0
 )
"""

total_customers = """
SELECT count(distinct t.CUSTOMER_ID ) as customers
FROM `bclic-371311.data.daily_transaction` t
LEFT JOIN `bclic-371311.data.customers` c ON t.CUSTOMER_ID = c.CUSTOMER_ID
LEFT JOIN `bclic-371311.data.ref_country` r ON c.CUSTOMER_COUNTRY_CODE = r.CUSTOMER_COUNTRY_CODE

"""

total_deposits = """
SELECT sum(cast(replace(t.DEPOSIT_AMOUNT,",",".") as float64)) total_deposits
FROM `bclic-371311.data.daily_transaction` t
LEFT JOIN `bclic-371311.data.customers` c ON t.CUSTOMER_ID = c.CUSTOMER_ID
LEFT JOIN `bclic-371311.data.ref_country` r ON c.CUSTOMER_COUNTRY_CODE = r.CUSTOMER_COUNTRY_CODE

"""

avg_deposits = """
SELECT sum(cast(replace(t.DEPOSIT_AMOUNT,",",".") as float64)) / count(distinct t.CUSTOMER_ID) as avg_deposit
FROM `bclic-371311.data.daily_transaction` t
LEFT JOIN `bclic-371311.data.customers` c ON t.CUSTOMER_ID = c.CUSTOMER_ID
LEFT JOIN `bclic-371311.data.ref_country` r ON c.CUSTOMER_COUNTRY_CODE = r.CUSTOMER_COUNTRY_CODE

"""

sum_total_bets = """
SELECT sum(cast(replace(t.BET_AMOUNT,",",".") as float64)) sum_total_bets
FROM `bclic-371311.data.daily_transaction` t
LEFT JOIN `bclic-371311.data.customers` c ON t.CUSTOMER_ID = c.CUSTOMER_ID
LEFT JOIN `bclic-371311.data.ref_country` r ON c.CUSTOMER_COUNTRY_CODE = r.CUSTOMER_COUNTRY_CODE

"""

average_stake = """
SELECT sum(cast(replace(t.BET_AMOUNT,",",".") as float64)) / count(distinct t.CUSTOMER_ID) as avg_stake
FROM `bclic-371311.data.daily_transaction` t
LEFT JOIN `bclic-371311.data.customers` c ON t.CUSTOMER_ID = c.CUSTOMER_ID
LEFT JOIN `bclic-371311.data.ref_country` r ON c.CUSTOMER_COUNTRY_CODE = r.CUSTOMER_COUNTRY_CODE

"""

profits_win_loss = """
SELECT sum(cast(replace(t.BET_AMOUNT,",",".") as float64)) / count(distinct t.CUSTOMER_ID) as avg_stake
FROM `bclic-371311.data.daily_transaction` t
LEFT JOIN `bclic-371311.data.customers` c ON t.CUSTOMER_ID = c.CUSTOMER_ID
LEFT JOIN `bclic-371311.data.ref_country` r ON c.CUSTOMER_COUNTRY_CODE = r.CUSTOMER_COUNTRY_CODE

"""

profit_win_loss = """
select sum(cast(replace(BET_AMOUNT,",",".") as float64)) - sum(cast(replace(WIN_AMOUNT,",",".") as float64)) as profit_loss
FROM `bclic-371311.data.daily_transaction` 
"""

AVG_profit_user = """
select (sum(cast(replace(BET_AMOUNT,",",".") as float64)) - sum(cast(replace(WIN_AMOUNT,",",".") as float64))) / count(distinct CUSTOMER_ID) as profit_loss
FROM `bclic-371311.data.daily_transaction` 
"""

@st.cache(allow_output_mutation=True)
def get_queries(query):
    return client.query(query).to_dataframe()


customer = get_queries(total_customers)
customers = prettify(customer.values[0][0])

bettor = get_queries(total_bettors)
bettors = prettify(bettor.values[0][0])

pct = round( (((1 - (bettor.count_bettors[0])/(customer.customers[0]))) * 100),2)
print(bettor , customer)

total_deposits = get_queries(total_deposits)
total_deposits = prettify(total_deposits.values[0][0])
avg_deposits = get_queries(avg_deposits)
sum_total_bets = get_queries(sum_total_bets)
sum_total_bets = prettify(sum_total_bets.values[0][0])
average_stake = get_queries(average_stake)
total_profit = get_queries(profit_win_loss)
total_profit = prettify(total_profit.values[0][0])

avg_profit_user = get_queries(AVG_profit_user)



st.sidebar.image("betclic.jpg",width=250)
st.sidebar.title("Welcome to Betclic KPI's")
st.title("Business Summary")

col1,col2= st.sidebar.columns(2)
col3,col4= st.sidebar.columns(2)
col5,col6= st.sidebar.columns(2)
col7,col8= st.sidebar.columns(2)

col1.metric(label="Customers", value=str(customers))
col2.metric(label="Bettors", value=str(bettors), delta=f"+{pct}%")
col3.metric(label="Total Deposits", value= f"${total_deposits}")
col4.metric(label="Average Deposits", value= f"${str(round(avg_deposits,2).values[0][0])}")
col5.metric(label="Total Stake", value= f"${sum_total_bets}")
col6.metric(label="Average Stake", value= f"${str(round(average_stake,2).values[0][0])}")
col7.metric(label="Profit Win/Loss", value= f"${total_profit}")
col8.metric(label="Average profits user", value= f"${str(round(avg_profit_user,2).values[0][0])}")


h_amount_vs_segment = """
SELECT c.CUSTOMER_SEGMENTATION as customer_segmentation ,sum(cast(replace(BET_AMOUNT,",",".") as float64)) bet_amount
FROM `bclic-371311.data.daily_transaction` t
LEFT JOIN `bclic-371311.data.customers` c ON t.CUSTOMER_ID = c.CUSTOMER_ID
LEFT JOIN `bclic-371311.data.ref_country` r ON c.CUSTOMER_COUNTRY_CODE = r.CUSTOMER_COUNTRY_CODE
group by c.CUSTOMER_SEGMENTATION
order by CUSTOMER_SEGMENTATION
"""

hist_amount_vs_segment = get_queries(h_amount_vs_segment)
hist_amount_vs_segment = hist_amount_vs_segment.set_index("customer_segmentation")
hist_amount_vs_segment = hist_amount_vs_segment["bet_amount"] / sum(hist_amount_vs_segment["bet_amount"])
hist_amount_vs_segment = hist_amount_vs_segment.reset_index()

bar_chart = alt.Chart(hist_amount_vs_segment).mark_bar().encode(
        y='customer_segmentation:O',
        x="bet_amount").properties(
    width=400,
    height=250
)
 
 
st.subheader("Customer Segments")

col1,col2, col3= st.columns(3)

col1.caption("Betting volume vs segment")
col1.altair_chart(bar_chart, use_container_width=True)

h_profit_vs_segment = """
SELECT c.CUSTOMER_SEGMENTATION as customer_segmentation ,(sum(cast(replace(BET_AMOUNT,",",".") as float64)) - sum(cast(replace(WIN_AMOUNT,",",".") as float64))) as profit_loss
FROM `bclic-371311.data.daily_transaction` t
LEFT JOIN `bclic-371311.data.customers` c ON t.CUSTOMER_ID = c.CUSTOMER_ID
LEFT JOIN `bclic-371311.data.ref_country` r ON c.CUSTOMER_COUNTRY_CODE = r.CUSTOMER_COUNTRY_CODE
group by c.CUSTOMER_SEGMENTATION
order by CUSTOMER_SEGMENTATION
"""

hist_profit_vs_segment = get_queries(h_profit_vs_segment)
hist_profit_vs_segment = hist_profit_vs_segment.set_index("customer_segmentation")
hist_profit_vs_segment = hist_profit_vs_segment["profit_loss"] / sum(hist_profit_vs_segment["profit_loss"])
hist_profit_vs_segment = hist_profit_vs_segment.reset_index()


bar_chart_1 = alt.Chart(hist_profit_vs_segment).mark_bar().encode(
        y='customer_segmentation',
        x="profit_loss").properties(
    width=400,
    height=250
)

col2.caption("Profit loss % vs segment")
col2.altair_chart(bar_chart_1, use_container_width=True)

new_pnl = pd.DataFrame()
new_pnl["customer_segmentation"] = hist_profit_vs_segment["customer_segmentation"]
new_pnl["ratio"] = (hist_profit_vs_segment["profit_loss"] / hist_amount_vs_segment["bet_amount"]) -1

bar_chart_2 = alt.Chart(new_pnl).mark_bar().encode(
        y='customer_segmentation',
        x="ratio",color=alt.value('red')).properties(
    width=400,
    height=250
)

col3.caption("Profit_loss vs bet amount")
col3.altair_chart(bar_chart_2, use_container_width=True)


age_betting_amount = """
SELECT c.CUSTOMER_AGE as CUSTOMER_AGE ,sum(cast(replace(BET_AMOUNT,",",".") as float64)) bet_amount 
FROM `bclic-371311.data.daily_transaction` t
LEFT JOIN `bclic-371311.data.customers` c ON t.CUSTOMER_ID = c.CUSTOMER_ID
LEFT JOIN `bclic-371311.data.ref_country` r ON c.CUSTOMER_COUNTRY_CODE = r.CUSTOMER_COUNTRY_CODE
group by c.CUSTOMER_AGE
order by CUSTOMER_AGE
"""

hist_age_betting_amount = get_queries(age_betting_amount)
bar_chart_3 = alt.Chart(hist_age_betting_amount).mark_bar().encode(
        y='bet_amount',
        x="CUSTOMER_AGE").properties(
    width=400,
    height=250
)


age_profit_loss = """
SELECT c.CUSTOMER_AGE as CUSTOMER_AGE ,(sum(cast(replace(BET_AMOUNT,",",".") as float64)) - sum(cast(replace(WIN_AMOUNT,",",".") as float64))) as profit_loss
FROM `bclic-371311.data.daily_transaction` t
LEFT JOIN `bclic-371311.data.customers` c ON t.CUSTOMER_ID = c.CUSTOMER_ID
LEFT JOIN `bclic-371311.data.ref_country` r ON c.CUSTOMER_COUNTRY_CODE = r.CUSTOMER_COUNTRY_CODE
group by c.CUSTOMER_AGE
order by CUSTOMER_AGE
"""

hist_age_profit_loss = get_queries(age_profit_loss)
bar_chart_4 = alt.Chart(hist_age_profit_loss).mark_bar().encode(
        y='profit_loss',
        x="CUSTOMER_AGE").properties(
    width=400,
    height=250
)

st.subheader("KPI's by age group")
st.caption("Volume and profit loss per age group")
col1,col2= st.columns(2)

col1.altair_chart(bar_chart_3, use_container_width=True)
col2.altair_chart(bar_chart_4, use_container_width=True)


country_vs_customers = """
SELECT r.CUSTOMER_COUNTRY_LABEL, count(distinct t.CUSTOMER_ID) as customers
FROM `bclic-371311.data.daily_transaction` t
LEFT JOIN `bclic-371311.data.customers` c ON t.CUSTOMER_ID = c.CUSTOMER_ID
LEFT JOIN `bclic-371311.data.ref_country` r ON c.CUSTOMER_COUNTRY_CODE = r.CUSTOMER_COUNTRY_CODE
GROUP BY 1;
"""

hist_country_vs_customers = get_queries(country_vs_customers)

bar_chart_5 = alt.Chart(hist_country_vs_customers).mark_bar().encode(
        y='customers',
        x="CUSTOMER_COUNTRY_LABEL").properties(
    width=400,
    height=250
)

country_vs_customers = """
SELECT r.CUSTOMER_COUNTRY_LABEL,c.CUSTOMER_SEGMENTATION, (sum(cast(replace(BET_AMOUNT,",",".") as float64)) - sum(cast(replace(WIN_AMOUNT,",",".") as float64))) as profit_loss
FROM `bclic-371311.data.daily_transaction` t
LEFT JOIN `bclic-371311.data.customers` c ON t.CUSTOMER_ID = c.CUSTOMER_ID
LEFT JOIN `bclic-371311.data.ref_country` r ON c.CUSTOMER_COUNTRY_CODE = r.CUSTOMER_COUNTRY_CODE
GROUP BY 2,1
order by c.CUSTOMER_SEGMENTATION

"""

age_country_vs_customers = """
SELECT r.CUSTOMER_COUNTRY_LABEL,c.CUSTOMER_SEGMENTATION,c.CUSTOMER_AGE, (sum(cast(replace(BET_AMOUNT,",",".") as float64)) - sum(cast(replace(WIN_AMOUNT,",",".") as float64))) as profit_loss
FROM `bclic-371311.data.daily_transaction` t
LEFT JOIN `bclic-371311.data.customers` c ON t.CUSTOMER_ID = c.CUSTOMER_ID
LEFT JOIN `bclic-371311.data.ref_country` r ON c.CUSTOMER_COUNTRY_CODE = r.CUSTOMER_COUNTRY_CODE
GROUP BY 2,3,1
Order by profit_loss desc

"""

hist_country_vs_customers = get_queries(country_vs_customers)

hist_age_country_vs_customers = get_queries(age_country_vs_customers)
hist_age_country_vs_customers["percentage"] = abs(hist_age_country_vs_customers.profit_loss) / sum(abs(hist_age_country_vs_customers.profit_loss))
hist_age_country_vs_customers["percentage_cumsum"] = hist_age_country_vs_customers.percentage.cumsum()
top4_df = hist_age_country_vs_customers.head(4)
country = [top4_df.CUSTOMER_COUNTRY_LABEL[i].split(".")[1] for i in range(len(top4_df))]
top4_df["country"] = country
top_4_names = top4_df.CUSTOMER_SEGMENTATION +"-"+ top4_df.country +"-:"+ top4_df.CUSTOMER_AGE

bar_chart_5 = alt.Chart(
    hist_country_vs_customers
).transform_fold(
    ['Average Annual Return', 'Sharpe Ratio'],
    ['type', 'value'],
).mark_bar().encode(
    column='profit_loss:N',
    color='CUSTOMER_COUNTRY_LABEL:N',
    x='profit_loss:N',
    y='CUSTOMER_COUNTRY_LABEL:Q',
).properties(
    width=00
)

labels = top_4_names[0], top_4_names[1], top_4_names[2], top_4_names[3],'Other Segments'
sizes = [round(top4_df.percentage[0] * 100,2), round(top4_df.percentage[1] * 100,2),round(top4_df.percentage[2] * 100,2),round(top4_df.percentage[3] * 100,2),round((1 - top4_df.percentage.sum()) * 100,2)]
explode = (0.1, 0.1, 0.1, 0.1, 0)  

fig1, ax1 = plt.subplots()
ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
        shadow=True, startangle=90)
ax1.axis('equal')  

st.subheader("Most profitable segment by total profit")
st.caption("Grouping by segmentation, age and country output is profit_loss %")
st.pyplot(fig1)
