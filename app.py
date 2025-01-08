from flask import Flask, render_template, send_file
import pandas as pd
import io

app = Flask(__name__)

@app.route('/')
def index():
    # קריאת הנתונים מקובץ CSV
    df = pd.read_csv('data/inventory.csv')
    # המרה לרשימת dictionaries
    inventory = df.to_dict('records')
    return render_template('index.html', inventory=inventory)

@app.route('/download-excel')
def download_excel():
    # קריאת הנתונים
    df = pd.read_csv('data/inventory.csv')
    
    # יצירת קובץ אקסל בזיכרון
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Inventory')
    output.seek(0)
    
    # שליחת הקובץ
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='inventory.xlsx'
    )

if __name__ == '__main__':
    app.run(debug=True) 