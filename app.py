from flask import Flask, render_template, request, send_file, jsonify
import pandas as pd
import os
import processor
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        df = pd.read_excel(file)
        columns = df.columns.tolist()
        return jsonify({'columns': columns})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/process', methods=['POST'])
def process_file():
    if 'file' not in request.files or 'column' not in request.form:
        return jsonify({'error': 'Missing file or column'}), 400
    
    file = request.files['file']
    column = request.form['column']
    
    try:
        df = pd.read_excel(file)
        
        if column not in df.columns:
             return jsonify({'error': 'Column not found'}), 400
             
        processed_df = processor.process_dataframe(df, column)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            processed_df.to_excel(writer, index=False)
        output.seek(0)
        
        return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='processed_result.xlsx'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=9008)
