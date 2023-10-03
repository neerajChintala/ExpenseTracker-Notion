import requests
import datetime
import plotly.graph_objs as go
import networkx as nx
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import pandas as pd

NOTION_TOKEN = ""
DATABASE_ID = ""
headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


def get_pages(num_pages=None):
    """
    If num_pages is None, get all pages, otherwise just the defined number.
    """
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

    get_all = num_pages is None
    page_size = 100 if get_all else num_pages

    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=headers)

    data = response.json()

    results = data["results"]
    while data["has_more"] and get_all:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        results.extend(data["results"])

    return results


pages = get_pages()
expenses, names, categories, createdDates = [], [], [], []
for page in pages:
    props = page["properties"]
    # fetch respective properties and append them into the respective lists
    names.append(props['Name']['title'][0]['text']['content'])
    expenses.append(props['Amount']['number'])
    categories.append(props['Category']['rich_text'][0]['plain_text'])
    createdDates.append(datetime.datetime.strptime(props['Date']['date']['start'], "%Y-%m-%d"))
#Getting current month's Data
from datetime import datetime
curr_month = datetime.now().month
if curr_month <= 10:
    curr_month = '0'+str(curr_month)
# df to create the initial dataframe from JSON
df = pd.DataFrame.from_dict(
    {'Name': names, 'Categories': categories, 'Expenses': expenses, 'Created Date': createdDates})
df = df[df['Created Date'].dt.strftime('%Y-%m') == f'{datetime.now().year}-{str(curr_month)}']
# df2 is grouped data to give sum of expeneses per day, per category
df2 = df.groupby([df['Created Date'].dt.day, df.Categories])["Expenses"].sum().reset_index()

# Create a directed graph using networkx
G = nx.from_pandas_edgelist(df2, "Created Date", "Categories", edge_attr="Expenses", create_using=nx.DiGraph())

# Set up Sankey diagram using plotly.graph_objects
sankey_fig = go.Figure(go.Sankey(
    arrangement="snap",
    node=dict(
        pad=10,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=list(G.nodes())
    ),
    link=dict(
        source=[list(G.nodes()).index(u) for u, _ in G.edges()],
        target=[list(G.nodes()).index(v) for _, v in G.edges()],
        value=[d["Expenses"] for u, v, d in G.edges(data=True)]
    )
))

# Set layout title
sankey_fig.update_layout(
    hovermode = 'x',
    title="Expense Flow as Sankey Diagram",
    font=dict(size = 10, color = 'white'),
    plot_bgcolor='black',
    paper_bgcolor='black'
)

# Set up Pie chart
pie_fig = go.Figure(go.Pie(labels=df2["Categories"], values=df2["Expenses"]))

# Set up Bar graph
bar_fig = go.Figure(go.Bar(x=df2["Categories"], y=df2["Expenses"]))

mydate = datetime.now().strftime("%B")
# Save the figure to an HTML file
html_file = f"Monthly-Report-{mydate}.html"

with open(html_file, "w") as file:
    file.write("<html><head>")
    file.write("<link rel='stylesheet' href='https://codepen.io/chriddyp/pen/bWLwgP.css'>")
    file.write("</head><body>")

    # Add tabs
    file.write("<div class='tab'>")
    file.write("<button class='tablinks' onclick=\"openTab(event, 'Sankey')\">Sankey Diagram</button>")
    file.write("<button class='tablinks' onclick=\"openTab(event, 'Pie')\">Pie Chart</button>")
    file.write("<button class='tablinks' onclick=\"openTab(event, 'Bar')\">Bar Graph</button>")
    file.write("</div>")

    # Add tab content
    file.write("<div id='Sankey' class='tabcontent'>")
    file.write(sankey_fig.to_html(full_html=False, include_plotlyjs="cdn"))
    file.write("</div>")

    file.write("<div id='Pie' class='tabcontent'>")
    file.write(pie_fig.to_html(full_html=False, include_plotlyjs="cdn"))
    file.write("</div>")

    file.write("<div id='Bar' class='tabcontent'>")
    file.write(bar_fig.to_html(full_html=False, include_plotlyjs="cdn"))
    file.write("</div>")

    # Add JavaScript to switch tabs
    file.write("<script>")
    file.write("function openTab(evt, tabName) {")
    file.write("  var i, tabcontent, tablinks;")
    file.write("  tabcontent = document.getElementsByClassName('tabcontent');")
    file.write("  for (i = 0; i < tabcontent.length; i++) {")
    file.write("    tabcontent[i].style.display = 'none';")
    file.write("  }")
    file.write("  tablinks = document.getElementsByClassName('tablinks');")
    file.write("  for (i = 0; i < tablinks.length; i++) {")
    file.write("    tablinks[i].className = tablinks[i].className.replace(' active', '');")
    file.write("  }")
    file.write("  document.getElementById(tabName).style.display = 'block';")
    file.write("  evt.currentTarget.className += ' active';")
    file.write("}")
    file.write("</script>")

    file.write("</body></html>")
# Email configuration
email_from = "expenserepo90@gmail.com"
email_to = ["neerajchintala1@gmail.com", "vemparalakavya@gmail.com"]
email_subject = f"Monthly-Report for {mydate}"
print(email_subject)
email_body = "Please find the Bi-Monthly report of your expenses"

# Compose the email
msg = MIMEMultipart()
msg["From"] = email_from
msg["To"] = ", ".join(email_to)
msg["Subject"] = email_subject
msg.attach(MIMEText(email_body, "plain"))

# Attach the HTML file
with open(html_file, "rb") as file:
    attachment = MIMEApplication(file.read(), Name=html_file)
    attachment["Content-Disposition"] = f"attachment; filename={html_file}"
    msg.attach(attachment)

# Send the email
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_username = ""
smtp_password = ""

with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(email_from, email_to, msg.as_string())
    print("Email sent successfully!")

# Delete the HTML file after sending the email
import os
os.remove(html_file)
