from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    # קריאת הנתונים מקובץ CSV
    df = pd.read_csv('data/inventory.csv')
    # המרה לרשימת dictionaries
    inventory = df.to_dict('records')
    return render_template('index.html', inventory=inventory)

if __name__ == '__main__':
    app.run(debug=True) 