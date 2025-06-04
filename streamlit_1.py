import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import mysql.connector

# --- Connect once ---
connection = mysql.connector.connect(
    host="gateway01.ap-southeast-1.prod.aws.tidbcloud.com",
    port=4000,
    user="2LwupNhEckogWnm.root",
    password="oHH2C3xTDDLFymia",
    database="project2_Top_Final_stock"
)

# --- Sidebar Navigation ---
choice = st.sidebar.selectbox('Navigation', ['Home', 'Visualization'])

if choice == 'Home':
    st.title('Welcome to Streamlit!')

elif choice == 'Visualization':

    # -------------------------------- 1. Volatility Analysis --------------------------------
    st.title("1. Volatility Analysis")

    query = "SELECT * FROM project2_Top_Final_stock.volatility_top"
    df = pd.read_sql(query, connection)

    st.subheader("Top 10 Most Volatile Stocks")
    st.dataframe(df)

    st.subheader("Volatility Bar Chart")
    plt.figure(figsize=(10, 6))
    sns.barplot(x='ticker', y='volatility', data=df, palette='viridis')
    plt.title('Top 10 Most Volatile Stocks')
    plt.ylabel('Volatility (Standard Deviation of Daily Returns)')
    plt.xlabel('Stock')
    plt.xticks(rotation=45)
    st.pyplot(plt)

    # -------------------------------- 2. Cumulative Returns --------------------------------
    st.title("2. Cumulative Return Over Time")

    # Load data from TiDB
    query = "SELECT * FROM cumm_top5"
    df = pd.read_sql(query, connection)

    # Fix data types
    df['date'] = pd.to_datetime(df['date'])
    df['cumulative_return'] = pd.to_numeric(df['cumulative_return'], errors='coerce')

    # Show data
    st.subheader("Cumulative Return for Top 5 Performing Stocks")
    st.dataframe(df)

    # Plot
    import matplotlib.pyplot as plt
    import seaborn as sns

    st.subheader("Cumulative Return Line Chart")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=df, x='date', y='cumulative_return', hue='Ticker', ax=ax)
    ax.set_title('Cumulative Return Over Time (Top 5 Performing Stocks)')
    ax.set_ylabel('Cumulative Return')
    ax.set_xlabel('Date')
    ax.legend(title='Ticker')
    fig.tight_layout()

    st.pyplot(fig)


    # -------------------------------- 3. Sector-wise Performance -----------------------------
    st.title("3. Sector-wise Performance")

    query = "SELECT * FROM project2_Top_Final_stock.sector_performance"
    df = pd.read_sql(query, connection)
    df['avg_yearly_return'] = pd.to_numeric(df['avg_yearly_return'], errors='coerce')
    df = df.sort_values(by='avg_yearly_return', ascending=False)

    st.subheader("Average Yearly Return by Sector")
    st.dataframe(df)

    st.subheader("Sector-wise Average Yearly Return Bar Chart")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(df['sector'], df['avg_yearly_return'], color='steelblue')
    ax.set_xlabel('Sector')
    ax.set_ylabel('Average Yearly Return (%)')
    ax.set_title('Sector-wise Average Yearly Return')
    plt.xticks(rotation=45)
    ax.grid(axis='y', linestyle='--', alpha=0.6)
    fig.tight_layout()
    st.pyplot(fig)

    # -------------------------------- 4. Stock Price Correlation -----------------------------
    st.title("4. Stock Price Correlation")

    query = "SELECT * FROM project2_Top_Final_stock.stock_price_correlation"
    df = pd.read_sql(query, connection)

    # Handle duplicates using pivot_table to create a clean correlation matrix
    corr_matrix = df.pivot_table(index='ticker', columns='ticker2', values='correlation', aggfunc='mean')

    
    st.subheader("Stock Price Correlation Matrix")
    st.dataframe(corr_matrix)

    st.subheader("Stock Price Correlation Heatmap")
    fig, ax = plt.subplots(figsize=(20, 16))
    sns.heatmap(corr_matrix, annot=False, cmap='coolwarm', linewidths=0.5, cbar=True, square=True)
    ax.set_title('Stock Price Correlation Heatmap', fontsize=20)
    plt.xticks(rotation=90)
    plt.yticks(rotation=0)
    st.pyplot(fig)

    # ------------------------- 5. Top 5 Gainers and Losers (Month-wise) ------------------------
    st.title("5. Top 5 Gainers and Losers (Month-wise)")

    query = "SELECT * FROM project2_Top_Final_stock.monthly_gainers_losers"
    df = pd.read_sql(query, connection)
    df.columns = df.columns.str.strip()

    st.dataframe(df)

    months = df['month_year'].unique()
    selected_month = st.selectbox("Select Month:", sorted(months))

    month_df = df[df['month_year'] == selected_month]
    top_gainers = month_df.nlargest(5, 'daily_return')
    top_losers = month_df.nsmallest(5, 'daily_return')

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"Top 5 Gainers - {selected_month}")
        fig1, ax1 = plt.subplots()
        sns.barplot(x='daily_return', y='ticker', data=top_gainers, palette='Greens', ax=ax1)
        ax1.set_xlabel("Monthly Return (%)")
        st.pyplot(fig1)

    with col2:
        st.subheader(f"Top 5 Losers - {selected_month}")
        fig2, ax2 = plt.subplots()
        sns.barplot(x='daily_return', y='ticker', data=top_losers, palette='Reds', ax=ax2)
        ax2.set_xlabel("Monthly Return (%)")
        st.pyplot(fig2)

# --- Close connection ---
connection.close()
