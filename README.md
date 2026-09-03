# Smart Expense Analyzer

A Python + MySQL expense tracking and analytics web application for managing and analyzing personal expenses.

## Features

- Add and manage daily expenses
- Store expense data using MySQL
- View expense records
- Analyze spending patterns
- Simple and user-friendly dashboard

## Tech Stack

- Python
- MySQL
- Streamlit
- SQL
- Pandas

## Project Structure

```text
smart-expense-analyzer/
│
├── app.py
├── database.py
├── expense_manager.py
├── requirements.txt
├── .gitignore
└── README.md
## Setup

1. Clone the repository:

```bash
git clone https://github.com/MohitBuilds/smart-expense-analyzer.git
cd smart-expense-analyzer

2.Install the required Python packages:
pip install -r requirements.txt

3.Create a .env file and add your MySQL database credentials.

4.Make sure MySQL is running and the required database is configured.

5.Run the application:
streamlit run app.py
