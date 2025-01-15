# Import packages
from dash import Dash, html, dash_table, dcc
import pandas as pd
import psycopg2
import plotly.express as px
import os
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Load environment variables
load_dotenv()
DATABASE_STRING = os.getenv('DATABASE_STRING')

# Connect to the database
conn = psycopg2.connect(DATABASE_STRING)
cur = conn.cursor()

# Fetch existing data
cur.execute("SELECT * FROM sales_monthly")
db_data = cur.fetchall()
db_data = [(row[0], row[2]) for row in db_data]
df_existing = pd.DataFrame(db_data, columns=['year_month', 'sales'])

# Fetch predictions data
cur.execute("SELECT * FROM predictions")
pred_data = cur.fetchall()
pred_data = [(row[1], row[2]) for row in pred_data]
print(pred_data)
df_predictions = pd.DataFrame(pred_data, columns=['year_month', 'sales'])

# Combine existing data and predictions
df_existing['type'] = 'Actual'
df_predictions['type'] = 'Prediction'
df_combined = pd.concat([df_existing, df_predictions])

# Initialize the app
app = Dash()

# App layout
app.layout = html.Div([
    html.H1(children='Monthly Sales Data and Predictions'),
    dash_table.DataTable(data=df_combined.to_dict('records'), page_size=12),
    dcc.Graph(figure=px.line(df_combined, x='year_month', y='sales', color='type', title='Sales Data and Predictions')),
    html.Button('Send Email', id='send-email-button', n_clicks=0),
    html.Div(id='email-status')
])

@app.callback(
    Output('email-status', 'children'),
    Input('send-email-button', 'n_clicks')
)

def send_email(n_clicks):
    if n_clicks > 0:
        try:
            # Create the email content
            msg = MIMEMultipart()
            msg['From'] = EMAIL_USER
            msg['To'] = EMAIL_RECEIVER
            msg['Subject'] = 'Monthly Sales Data and Predictions'
            body = 'Please find the attached monthly sales data and predictions.'
            msg.attach(MIMEText(body, 'plain'))

            # Send the email
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            text = msg.as_string()
            server.sendmail(EMAIL_USER, EMAIL_RECEIVER, text)
            server.quit()

            return 'Email sent successfully!'
        except Exception as e:
            return f'Failed to send email: {str(e)}'
    return ''


# Run the app
if __name__ == '__main__':
    app.run(debug=True)