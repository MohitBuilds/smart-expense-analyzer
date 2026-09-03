import streamlit as st
import mysql.connector
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from database import get_connection


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Smart Expense Analyzer",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM UI
# =========================================================

st.markdown("""
<style>

.stApp {
    background-color: #f5f7fb;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111827;
}

section[data-testid="stSidebar"] * {
    color: white;
}

/* Metric cards */
div[data-testid="metric-container"] {
    background-color: white;
    border: 1px solid #e5e7eb;
    padding: 18px;
    border-radius: 14px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.06);
}

/* Buttons */
.stButton > button,
.stDownloadButton > button {
    border-radius: 8px;
    font-weight: 600;
}

/* Tables */
div[data-testid="stDataFrame"] {
    border-radius: 10px;
}

/* Headers */
h1 {
    font-weight: 750;
}

h2, h3 {
    font-weight: 650;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# DATABASE CONNECTION
# =========================================================




# =========================================================
# GET EXPENSES
# =========================================================

def get_expenses():

    conn = get_connection()

    query = """
        SELECT
            id,
            expense_date,
            category,
            description,
            amount,
            payment_method
        FROM expenses
        ORDER BY expense_date DESC, id DESC
    """

    df = pd.read_sql(query, conn)

    conn.close()

    return df


# =========================================================
# ADD EXPENSE
# =========================================================

def add_expense(
    expense_date,
    category,
    description,
    amount,
    payment_method
):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO expenses
        (expense_date, category, description, amount, payment_method)
        VALUES (%s, %s, %s, %s, %s)
    """

    cursor.execute(
        query,
        (
            expense_date,
            category,
            description,
            amount,
            payment_method
        )
    )

    conn.commit()

    cursor.close()
    conn.close()


# =========================================================
# UPDATE EXPENSE
# =========================================================

def update_expense(
    expense_id,
    expense_date,
    category,
    description,
    amount,
    payment_method
):

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        UPDATE expenses
        SET
            expense_date = %s,
            category = %s,
            description = %s,
            amount = %s,
            payment_method = %s
        WHERE id = %s
    """

    cursor.execute(
        query,
        (
            expense_date,
            category,
            description,
            amount,
            payment_method,
            expense_id
        )
    )

    conn.commit()

    cursor.close()
    conn.close()


# =========================================================
# DELETE EXPENSE
# =========================================================

def delete_expense(expense_id):

    conn = get_connection()
    cursor = conn.cursor()

    query = "DELETE FROM expenses WHERE id = %s"

    cursor.execute(
        query,
        (expense_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()


# =========================================================
# PDF RECEIPT
# =========================================================

def generate_pdf_receipt(
    expense_id,
    expense_date,
    category,
    description,
    amount,
    payment_method
):

    buffer = BytesIO()

    pdf = canvas.Canvas(
        buffer,
        pagesize=A4
    )

    width, height = A4

    pdf.setFont(
        "Helvetica-Bold",
        20
    )

    pdf.drawCentredString(
        width / 2,
        height - 80,
        "EXPENSE RECEIPT"
    )

    pdf.setFont(
        "Helvetica",
        12
    )

    y = height - 140

    details = [
        f"Expense ID: {expense_id}",
        f"Date: {expense_date}",
        f"Category: {category}",
        f"Description: {description}",
        f"Amount: INR {amount}",
        f"Payment Method: {payment_method}"
    ]

    for detail in details:

        pdf.drawString(
            80,
            y,
            detail
        )

        y -= 30

    pdf.line(
        80,
        y,
        width - 80,
        y
    )

    pdf.setFont(
        "Helvetica-Bold",
        12
    )

    pdf.drawString(
        80,
        y - 35,
        "Smart Expense Analyzer"
    )

    pdf.setFont(
        "Helvetica",
        10
    )

    pdf.drawString(
        80,
        y - 55,
        "Thank you for using Smart Expense Analyzer."
    )

    pdf.save()

    buffer.seek(0)

    return buffer


# =========================================================
# CSV EXPORT
# =========================================================

def convert_to_csv(dataframe):

    return dataframe.to_csv(
        index=False
    ).encode("utf-8")


# =========================================================
# EXCEL EXPORT
# =========================================================

def convert_to_excel(dataframe):

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        dataframe.to_excel(
            writer,
            index=False,
            sheet_name="Expenses"
        )

    return output.getvalue()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("💰 Smart Expense")
st.sidebar.caption("Expense Management System")

st.sidebar.divider()

menu = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "➕ Add Expense",
        "📋 All Expenses",
        "✏️ Edit Expense",
        "🗑️ Delete Expense",
        "📄 PDF Receipt",
        "📅 Monthly Analysis",
        "📥 Export Data"
    ]
)

st.sidebar.divider()

st.sidebar.caption(
    "Built with Python + MySQL + Streamlit"
)


# =========================================================
# LOAD DATA
# =========================================================

try:

    df = get_expenses()

except Exception as e:

    st.error(
        "❌ Database connection failed."
    )

    st.code(str(e))

    st.stop()


# =========================================================
# DASHBOARD
# =========================================================

if menu == "📊 Dashboard":

    st.title("📊 Expense Dashboard")

    st.caption(
        "Track, analyze and manage your personal expenses."
    )

    if df.empty:

        st.info(
            "No expenses available. Add your first expense!"
        )

    else:

        total_expense = df["amount"].sum()
        average_expense = df["amount"].mean()
        highest_expense = df["amount"].max()
        total_transactions = len(df)

        # -------------------------
        # Metrics
        # -------------------------

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "💰 Total Expense",
            f"₹{total_expense:,.2f}"
        )

        col2.metric(
            "📊 Average Expense",
            f"₹{average_expense:,.2f}"
        )

        col3.metric(
            "🔥 Highest Expense",
            f"₹{highest_expense:,.2f}"
        )

        col4.metric(
            "🧾 Transactions",
            total_transactions
        )

        st.write("")

        # -------------------------
        # Category Analysis
        # -------------------------

        st.subheader(
            "📂 Spending by Category"
        )

        category_summary = (
            df.groupby("category")["amount"]
            .sum()
            .sort_values(ascending=False)
        )

        col1, col2 = st.columns(
            [1.5, 1]
        )

        with col1:

            st.bar_chart(
                category_summary
            )

        with col2:

            category_table = (
                category_summary
                .reset_index()
            )

            category_table.columns = [
                "Category",
                "Amount"
            ]

            st.dataframe(
                category_table,
                use_container_width=True,
                hide_index=True
            )

        st.divider()

        # -------------------------
        # Payment Analysis
        # -------------------------

        st.subheader(
            "💳 Spending by Payment Method"
        )

        payment_summary = (
            df.groupby("payment_method")["amount"]
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(
            payment_summary
        )

        st.divider()

        # -------------------------
        # Recent Expenses
        # -------------------------

        st.subheader(
            "🕒 Recent Expenses"
        )

        recent_df = df.head(8)

        st.dataframe(
            recent_df,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# ADD EXPENSE
# =========================================================

elif menu == "➕ Add Expense":

    st.title("➕ Add New Expense")

    st.caption(
        "Record a new transaction in your expense database."
    )

    with st.form(
        "add_expense_form"
    ):

        col1, col2 = st.columns(2)

        with col1:

            expense_date = st.date_input(
                "Expense Date"
            )

            category = st.selectbox(
                "Category",
                [
                    "Food",
                    "Travel",
                    "Shopping",
                    "Bills",
                    "Entertainment",
                    "Health",
                    "Education",
                    "Other"
                ]
            )

            amount = st.number_input(
                "Amount",
                min_value=0.0,
                step=10.0
            )

        with col2:

            description = st.text_input(
                "Description"
            )

            payment_method = st.selectbox(
                "Payment Method",
                [
                    "UPI",
                    "Cash",
                    "Credit Card",
                    "Debit Card",
                    "Bank Transfer"
                ]
            )

        submit = st.form_submit_button(
            "➕ Add Expense"
        )

        if submit:

            if amount <= 0:

                st.error(
                    "Amount must be greater than 0."
                )

            else:

                add_expense(
                    expense_date,
                    category,
                    description,
                    amount,
                    payment_method
                )

                st.success(
                    "Expense added successfully! ✅"
                )

                st.rerun()


# =========================================================
# ALL EXPENSES
# =========================================================

elif menu == "📋 All Expenses":

    st.title("📋 All Expenses")

    st.caption(
        "View and filter all recorded transactions."
    )

    if df.empty:

        st.info(
            "No expenses found."
        )

    else:

        col1, col2 = st.columns(2)

        with col1:

            categories = [
                "All"
            ] + sorted(
                df["category"]
                .dropna()
                .unique()
                .tolist()
            )

            selected_category = st.selectbox(
                "📂 Category",
                categories
            )

        with col2:

            payment_methods = [
                "All"
            ] + sorted(
                df["payment_method"]
                .dropna()
                .unique()
                .tolist()
            )

            selected_payment = st.selectbox(
                "💳 Payment Method",
                payment_methods
            )

        filtered_df = df.copy()

        if selected_category != "All":

            filtered_df = filtered_df[
                filtered_df["category"]
                == selected_category
            ]

        if selected_payment != "All":

            filtered_df = filtered_df[
                filtered_df["payment_method"]
                == selected_payment
            ]

        st.write(
            f"Showing **{len(filtered_df)}** expenses"
        )

        st.dataframe(
            filtered_df,
            use_container_width=True,
            hide_index=True
        )


# =========================================================
# EDIT EXPENSE
# =========================================================

elif menu == "✏️ Edit Expense":

    st.title("✏️ Edit Expense")

    if df.empty:

        st.info(
            "No expenses available."
        )

    else:

        expense_id = st.selectbox(
            "Select Expense ID",
            df["id"].tolist()
        )

        selected = df[
            df["id"] == expense_id
        ].iloc[0]

        categories = [
            "Food",
            "Travel",
            "Shopping",
            "Bills",
            "Entertainment",
            "Health",
            "Education",
            "Other"
        ]

        payment_options = [
            "UPI",
            "Cash",
            "Credit Card",
            "Debit Card",
            "Bank Transfer"
        ]

        with st.form(
            "edit_expense_form"
        ):

            col1, col2 = st.columns(2)

            with col1:

                expense_date = st.date_input(
                    "Expense Date",
                    value=pd.to_datetime(
                        selected["expense_date"]
                    ).date()
                )

                category = st.selectbox(
                    "Category",
                    categories,
                    index=(
                        categories.index(
                            selected["category"]
                        )
                        if selected["category"]
                        in categories
                        else 0
                    )
                )

                amount = st.number_input(
                    "Amount",
                    min_value=0.0,
                    value=float(
                        selected["amount"]
                    ),
                    step=10.0
                )

            with col2:

                description = st.text_input(
                    "Description",
                    value=(
                        selected["description"]
                        if pd.notna(
                            selected["description"]
                        )
                        else ""
                    )
                )

                payment_method = st.selectbox(
                    "Payment Method",
                    payment_options,
                    index=(
                        payment_options.index(
                            selected["payment_method"]
                        )
                        if selected["payment_method"]
                        in payment_options
                        else 0
                    )
                )

            update_button = st.form_submit_button(
                "💾 Update Expense"
            )

            if update_button:

                if amount <= 0:

                    st.error(
                        "Amount must be greater than 0."
                    )

                else:

                    update_expense(
                        expense_id,
                        expense_date,
                        category,
                        description,
                        amount,
                        payment_method
                    )

                    st.success(
                        "Expense updated successfully! ✅"
                    )

                    st.rerun()


# =========================================================
# DELETE EXPENSE
# =========================================================

elif menu == "🗑️ Delete Expense":

    st.title("🗑️ Delete Expense")

    if df.empty:

        st.info(
            "No expenses available."
        )

    else:

        expense_id = st.selectbox(
            "Select Expense ID",
            df["id"].tolist()
        )

        selected = df[
            df["id"] == expense_id
        ].iloc[0]

        st.warning(
            f"Expense #{expense_id} | "
            f"{selected['category']} | "
            f"₹{selected['amount']}"
        )

        confirm = st.checkbox(
            "I confirm that I want to delete this expense."
        )

        if st.button(
            "🗑️ Delete Expense",
            disabled=not confirm
        ):

            delete_expense(
                expense_id
            )

            st.success(
                "Expense deleted successfully! ✅"
            )

            st.rerun()


# =========================================================
# PDF RECEIPT
# =========================================================

elif menu == "📄 PDF Receipt":

    st.title("📄 Generate PDF Receipt")

    if df.empty:

        st.info(
            "No expenses available."
        )

    else:

        expense_id = st.selectbox(
            "Select Expense",
            df["id"].tolist()
        )

        selected = df[
            df["id"] == expense_id
        ].iloc[0]

        st.subheader(
            "🧾 Receipt Preview"
        )

        col1, col2 = st.columns(2)

        with col1:

            st.write(
                f"**Expense ID:** {selected['id']}"
            )

            st.write(
                f"**Date:** {selected['expense_date']}"
            )

            st.write(
                f"**Category:** {selected['category']}"
            )

        with col2:

            st.write(
                f"**Description:** {selected['description']}"
            )

            st.write(
                f"**Amount:** ₹{selected['amount']}"
            )

            st.write(
                f"**Payment:** {selected['payment_method']}"
            )

        pdf_file = generate_pdf_receipt(
            selected["id"],
            selected["expense_date"],
            selected["category"],
            selected["description"],
            selected["amount"],
            selected["payment_method"]
        )

        st.download_button(
            label="⬇️ Download PDF Receipt",
            data=pdf_file,
            file_name=f"expense_receipt_{expense_id}.pdf",
            mime="application/pdf"
        )


# =========================================================
# MONTHLY ANALYSIS
# =========================================================

elif menu == "📅 Monthly Analysis":

    st.title("📅 Monthly Expense Analysis")

    if df.empty:

        st.info(
            "No expenses available."
        )

    else:

        monthly_df = df.copy()

        monthly_df["expense_date"] = pd.to_datetime(
            monthly_df["expense_date"]
        )

        monthly_df["month"] = (
            monthly_df["expense_date"]
            .dt.to_period("M")
            .astype(str)
        )

        monthly_summary = (
            monthly_df
            .groupby("month")["amount"]
            .sum()
            .sort_index()
        )

        highest_month = (
            monthly_summary.idxmax()
        )

        highest_amount = (
            monthly_summary.max()
        )

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "📅 Months Tracked",
            len(monthly_summary)
        )

        col2.metric(
            "🔥 Highest Spending Month",
            highest_month
        )

        col3.metric(
            "💰 Highest Monthly Expense",
            f"₹{highest_amount:,.2f}"
        )

        st.divider()

        st.subheader(
            "📊 Monthly Spending"
        )

        st.bar_chart(
            monthly_summary
        )

        st.divider()

        st.subheader(
            "📋 Monthly Summary"
        )

        summary_table = (
            monthly_summary
            .reset_index()
        )

        summary_table.columns = [
            "Month",
            "Total Expense"
        ]

        st.dataframe(
            summary_table,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        selected_month = st.selectbox(
            "Select Month",
            monthly_summary.index.tolist()
        )

        selected_month_df = monthly_df[
            monthly_df["month"]
            == selected_month
        ].copy()

        selected_month_df = (
            selected_month_df
            .drop(columns=["month"])
        )

        st.subheader(
            f"🧾 Expenses in {selected_month}"
        )

        st.dataframe(
            selected_month_df,
            use_container_width=True,
            hide_index=True
        )

        st.success(
            f"Total spending in {selected_month}: "
            f"₹{monthly_summary[selected_month]:,.2f}"
        )


# =========================================================
# EXPORT DATA
# =========================================================

elif menu == "📥 Export Data":

    st.title("📥 Export Expense Data")

    st.caption(
        "Download your expense data in CSV or Excel format."
    )

    if df.empty:

        st.info(
            "No expense data available for export."
        )

    else:

        # -------------------------
        # Export Filters
        # -------------------------

        col1, col2 = st.columns(2)

        with col1:

            categories = [
                "All"
            ] + sorted(
                df["category"]
                .dropna()
                .unique()
                .tolist()
            )

            export_category = st.selectbox(
                "📂 Category",
                categories,
                key="export_category"
            )

        with col2:

            payment_methods = [
                "All"
            ] + sorted(
                df["payment_method"]
                .dropna()
                .unique()
                .tolist()
            )

            export_payment = st.selectbox(
                "💳 Payment Method",
                payment_methods,
                key="export_payment"
            )

        export_df = df.copy()

        if export_category != "All":

            export_df = export_df[
                export_df["category"]
                == export_category
            ]

        if export_payment != "All":

            export_df = export_df[
                export_df["payment_method"]
                == export_payment
            ]

        st.write(
            f"### {len(export_df)} expenses ready for export"
        )

        st.dataframe(
            export_df,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # -------------------------
        # CSV
        # -------------------------

        st.subheader(
            "📄 CSV Export"
        )

        csv_data = convert_to_csv(
            export_df
        )

        st.download_button(
            label="⬇️ Download CSV",
            data=csv_data,
            file_name="expenses.csv",
            mime="text/csv"
        )

        st.divider()

        # -------------------------
        # Excel
        # -------------------------

        st.subheader(
            "📊 Excel Export"
        )

        excel_data = convert_to_excel(
            export_df
        )

        st.download_button(
            label="⬇️ Download Excel",
            data=excel_data,
            file_name="expenses.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            )
        )

        st.success(
            "Your expense data is ready to download! ✅"
        )