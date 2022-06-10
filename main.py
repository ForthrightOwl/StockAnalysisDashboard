from app import app
from layout import app_layout

app.layout = app_layout
app.run_server(debug=True)