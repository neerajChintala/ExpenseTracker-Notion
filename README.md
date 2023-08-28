# Monthly Expense Report Generator

This script fetches expense data from a Notion database, creates visualizations including a Sankey diagram, a Pie chart, and a Bar graph, and sends out a monthly expense report via email.

## Requirements

- Python 3.x
- Required Python packages: `requests`, `plotly`, `networkx`, `smtplib`, `pandas`

## Setup

1. Clone this repository to your local machine.
2. Install the required Python packages by running: `pip install requests plotly networkx pandas`
3. Obtain a Notion integration token and the database ID where your expense data is stored. Update the `NOTION_TOKEN` and `DATABASE_ID` variables in the code with your values.
4. Provide your email credentials. Update the `smtp_username` and `smtp_password` variables with your Gmail credentials.
5. Customize recipient email addresses and subject in the `email_to` and `email_subject` variables.
6. Run the script: `python expense_report.py`

## Functionality

1. The script fetches expense data from the specified Notion database.
2. It processes the data to create a Sankey diagram, Pie chart, and Bar graph visualizing monthly expenses.
3. The visualizations are embedded in an HTML page with tabs for easy navigation.
4. The HTML page is saved as a file, attached to an email, and sent to specified recipients.
5. The locally created HTML file is then deleted.

## Important Notes

- Make sure you have the necessary permissions to access the Notion database and use Gmail for sending emails.
- The script uses Gmail's SMTP server for sending emails. If you're using a different email provider, adjust the SMTP server settings accordingly.
- Use this script responsibly and ensure that your credentials and personal data are stored securely.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
