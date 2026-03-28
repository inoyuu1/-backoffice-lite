import os
import pandas as pd
import streamlit as st
from datetime import date

st.set_page_config(page_title="BackOffice Lite", layout="centered")

DATA_DIR = "data"
INVOICE_FILE = os.path.join(DATA_DIR, "invoices.csv")
EXPENSE_FILE = os.path.join(DATA_DIR, "expenses.csv")

os.makedirs(DATA_DIR, exist_ok=True)

def init_csv():
    if not os.path.exists(INVOICE_FILE):
        pd.DataFrame(columns=["date", "client", "amount", "status"]).to_csv(INVOICE_FILE, index=False)
    if not os.path.exists(EXPENSE_FILE):
        pd.DataFrame(columns=["date", "item", "amount", "category"]).to_csv(EXPENSE_FILE, index=False)

def load_data():
    invoices = pd.read_csv(INVOICE_FILE)
    expenses = pd.read_csv(EXPENSE_FILE)
    return invoices, expenses

def save_invoice(new_row):
    invoices = pd.read_csv(INVOICE_FILE)
    invoices = pd.concat([invoices, pd.DataFrame([new_row])], ignore_index=True)
    invoices.to_csv(INVOICE_FILE, index=False)

def save_expense(new_row):
    expenses = pd.read_csv(EXPENSE_FILE)
    expenses = pd.concat([expenses, pd.DataFrame([new_row])], ignore_index=True)
    expenses.to_csv(EXPENSE_FILE, index=False)

init_csv()
invoices, expenses = load_data()

st.title("BackOffice Lite")
menu = st.sidebar.radio("メニュー", ["ダッシュボード", "請求管理", "経費管理"])

if menu == "ダッシュボード":
    st.subheader("月次サマリー")

    if not invoices.empty:
        invoices["date"] = pd.to_datetime(invoices["date"], errors="coerce")
        invoices["month"] = invoices["date"].dt.to_period("M").astype(str)
        monthly_sales = invoices.groupby("month")["amount"].sum().reset_index()
    else:
        monthly_sales = pd.DataFrame(columns=["month", "amount"])

    if not expenses.empty:
        expenses["date"] = pd.to_datetime(expenses["date"], errors="coerce")
        expenses["month"] = expenses["date"].dt.to_period("M").astype(str)
        monthly_expenses = expenses.groupby("month")["amount"].sum().reset_index()
    else:
        monthly_expenses = pd.DataFrame(columns=["month", "amount"])

    summary = pd.merge(
        monthly_sales.rename(columns={"amount": "sales"}),
        monthly_expenses.rename(columns={"amount": "expenses"}),
        on="month",
        how="outer"
    ).fillna(0)

    if not summary.empty:
        summary["profit"] = summary["sales"] - summary["expenses"]
        st.dataframe(summary, use_container_width=True)
        st.metric("累計売上", f"¥{int(summary['sales'].sum()):,}")
        st.metric("累計経費", f"¥{int(summary['expenses'].sum()):,}")
        st.metric("累計利益", f"¥{int(summary['profit'].sum()):,}")
    else:
        st.info("まだデータがありません。")

elif menu == "請求管理":
    st.subheader("請求登録")

    with st.form("invoice_form"):
        invoice_date = st.date_input("日付", value=date.today())
        client = st.text_input("取引先名")
        amount = st.number_input("金額", min_value=0, step=1000)
        status = st.selectbox("ステータス", ["未入金", "入金済"])
        submitted = st.form_submit_button("保存")

        if submitted:
            save_invoice({
                "date": invoice_date.strftime("%Y-%m-%d"),
                "client": client,
                "amount": amount,
                "status": status
            })
            st.success("請求情報を保存しました。")
            st.rerun()

    st.subheader("請求一覧")
    st.dataframe(invoices, use_container_width=True)

elif menu == "経費管理":
    st.subheader("経費登録")

    with st.form("expense_form"):
        expense_date = st.date_input("日付", value=date.today(), key="expense_date")
        item = st.text_input("内容")
        amount = st.number_input("金額", min_value=0, step=100, key="expense_amount")
        category = st.selectbox("カテゴリ", ["交通費", "消耗品費", "通信費", "会議費", "その他"])
        submitted = st.form_submit_button("保存")

        if submitted:
            save_expense({
                "date": expense_date.strftime("%Y-%m-%d"),
                "item": item,
                "amount": amount,
                "category": category
            })
            st.success("経費情報を保存しました。")
            st.rerun()

    st.subheader("経費一覧")
    st.dataframe(expenses, use_container_width=True)