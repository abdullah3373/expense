import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date

# Configure seaborn style
sns.set_theme(style="darkgrid")

# Title
st.title('Personal Finance App')
st.write('Track your expenses and manage your finances effectively.')

# Initialize session state
if 'expenses' not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=['Date', 'Category', 'Amount'])
if 'budgets' not in st.session_state:
    st.session_state.budgets = {category: 0 for category in ['Food', 'Transport', 'Entertainment', 'Rent', 'Utilities']}

# Sidebar for budget settings
st.sidebar.header('Budget Settings')
for category in st.session_state.budgets.keys():
    st.session_state.budgets[category] = st.sidebar.number_input(
        f'Monthly budget for {category} ($)',
        min_value=0,
        value=st.session_state.budgets[category],
        key=f'budget_{category}'
    )

# Main app section
col1, col2 = st.columns(2)
with col1:
    # Date input
    expense_date = st.date_input('Expense Date', value=date.today())
    
    # Category selection with images
    selected_category = st.selectbox('Select Category', ['Food', 'Transport', 'Entertainment', 'Rent', 'Utilities'])
    category_images = {
        'Food': 'https://images.search.yahoo.com/images/view;_ylt=AwrgMItm7OhnsNcqYE6JzbkF;_ylu=c2VjA3NyBHNsawNpbWcEb2lkAzdiNzgzYzY2ZTBmNGRjYzhiNWIwMDU0ZWYzYmQwYTM4BGdwb3MDMTAEaXQDYmluZw--?back=https%3A%2F%2Fimages.search.yahoo.com%2Fsearch%2Fimages%3Fp%3Dfood%2Bimage%26type%3DE210US91215G0%26fr%3Dmcafee%26fr2%3Dpiv-web%26tab%3Dorganic%26ri%3D10&w=1920&h=1200&imgurl=getwallpapers.com%2Fwallpaper%2Ffull%2F8%2Fb%2Fc%2F1183994-cool-healthy-food-wallpaper-1920x1200-for-samsung-galaxy.jpg&rurl=http%3A%2F%2Fgetwallpapers.com%2Fcollection%2Fhealthy-food-wallpaper&size=627KB&p=food+image&oid=7b783c66e0f4dcc8b5b0054ef3bd0a38&fr2=piv-web&fr=mcafee&tt=Healthy+Food+Wallpaper+%2865%2B+images%29&b=0&ni=21&no=10&ts=&tab=organic&sigr=7eJOnHjj0zvI&sigb=.tlomufXdNTm&sigi=bp7K7CC_C8DK&sigt=Yyje2boW_5kS&.crumb=nms72yzBoin&fr=mcafee&fr2=piv-web&type=E210US91215G0',
        'Transport': 'https://via.placeholder.com/300x200.png?text=Transport',
        'Entertainment': 'https://via.placeholder.com/300x200.png?text=Entertainment',
        'Rent': 'https://via.placeholder.com/300x200.png?text=Rent',
        'Utilities': 'https://via.placeholder.com/300x200.png?text=Utilities'
    }
    st.image(category_images[selected_category], caption=f'{selected_category} Expenses')

with col2:
    # Expense input
    expense_amount = st.number_input('Amount ($)', min_value=0)
    if st.button('Add Expense'):
        new_expense = pd.DataFrame([[expense_date, selected_category, expense_amount]],
                                 columns=['Date', 'Category', 'Amount'])
        st.session_state.expenses = pd.concat([st.session_state.expenses, new_expense], ignore_index=True)

# Display expenses
if not st.session_state.expenses.empty:
    st.subheader('Expense History')
    st.dataframe(st.session_state.expenses.sort_values('Date', ascending=False))

    # Download button
    csv = st.session_state.expenses.to_csv(index=False)
    st.download_button('Download Expenses as CSV', data=csv, file_name='expenses.csv')

# Visualizations
if not st.session_state.expenses.empty:
    # Convert to datetime
    expenses = st.session_state.expenses.copy()
    expenses['Date'] = pd.to_datetime(expenses['Date'])
    
    # Monthly Summary
    st.subheader('Monthly Summary')
    expenses['Month'] = expenses['Date'].dt.to_period('M')
    monthly_expenses = expenses.groupby(['Month', 'Category'])['Amount'].sum().unstack().fillna(0)
    st.write(monthly_expenses)
    
    # Visualization columns
    viz_col1, viz_col2 = st.columns(2)
    
    with viz_col1:
        # Time Series Plot
        st.subheader('Spending Over Time')
        daily_expenses = expenses.groupby('Date')['Amount'].sum().reset_index()
        plt.figure(figsize=(10, 4))
        sns.lineplot(data=daily_expenses, x='Date', y='Amount')
        st.pyplot(plt)
        
        # Budget vs Actual
        st.subheader('Budget vs Actual')
        budget_comparison = pd.DataFrame({
            'Category': list(st.session_state.budgets.keys()),
            'Spent': expenses.groupby('Category')['Amount'].sum().reindex(st.session_state.budgets.keys(), fill_value=0),
            'Budget': list(st.session_state.budgets.values())
        })
        budget_comparison['Remaining'] = budget_comparison['Budget'] - budget_comparison['Spent']
        
        plt.figure(figsize=(10, 6))
        sns.barplot(data=budget_comparison.melt(id_vars='Category', value_vars=['Spent', 'Budget']),
                    x='value', y='Category', hue='variable', orient='h')
        st.pyplot(plt)
    
    with viz_col2:
        # Category Distribution
        st.subheader('Spending by Category')
        category_expenses = expenses.groupby('Category')['Amount'].sum().reset_index()
        plt.figure(figsize=(10, 6))
        sns.barplot(data=category_expenses, x='Category', y='Amount')
        st.pyplot(plt)
        
        # Pie Chart
        st.subheader('Expense Distribution')
        fig, ax = plt.subplots()
        ax.pie(category_expenses['Amount'], 
               labels=category_expenses['Category'], 
               autopct='%1.1f%%',
               startangle=90)
        ax.axis('equal')
        st.pyplot(fig)

# Key Metrics
if not st.session_state.expenses.empty:
    total_spent = expenses['Amount'].sum()
    total_budget = sum(st.session_state.budgets.values())
    budget_remaining = total_budget - total_spent
    
    metric_col1, metric_col2, metric_col3 = st.columns(3)
    metric_col1.metric("Total Spent", f"${total_spent:,.2f}")
    metric_col2.metric("Total Budget", f"${total_budget:,.2f}")
    metric_col3.metric("Budget Remaining", f"${budget_remaining:,.2f}", 
                      delta_color="inverse" if budget_remaining < 0 else "normal")
else:
    st.write("No expenses recorded yet. Start adding expenses above!")
