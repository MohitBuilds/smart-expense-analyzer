from database import get_connection


def add_expense(expense_date, category, description, amount, payment_method):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO expenses
        (expense_date, category, description, amount, payment_method)
        VALUES (%s, %s, %s, %s, %s)
    """

    values = (
        expense_date,
        category,
        description,
        amount,
        payment_method
    )

    cursor.execute(query, values)
    conn.commit()

    cursor.close()
    conn.close()

    print("Expense added successfully! ✅")


def get_expenses():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, expense_date, category, description, amount, payment_method
        FROM expenses
        ORDER BY expense_date DESC
    """)

    expenses = cursor.fetchall()

    cursor.close()
    conn.close()

    return expenses


def delete_expense(expense_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM expenses WHERE id = %s",
        (expense_id,)
    )

    conn.commit()

    cursor.close()
    conn.close()

    print("Expense deleted successfully! 🗑️")


def get_total_expense():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses")

    total = cursor.fetchone()[0]

    cursor.close()
    conn.close()

    return total


def get_category_summary():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, SUM(amount)
        FROM expenses
        GROUP BY category
        ORDER BY SUM(amount) DESC
    """)

    summary = cursor.fetchall()

    cursor.close()
    conn.close()

    return summary


if __name__ == "__main__":

    print("\n--- ALL EXPENSES ---")

    expenses = get_expenses()

    for expense in expenses:
        print(expense)

    print("\n--- TOTAL EXPENSE ---")

    total = get_total_expense()
    print(f"Total: ₹{total}")

    print("\n--- CATEGORY SUMMARY ---")

    summary = get_category_summary()

    for category, amount in summary:
        print(f"{category}: ₹{amount}")