# Import library for Pandas
from io import StringIO
from string import whitespace
import pandas as pd
import re
import sqlite3

# Import library for Flask
from flask import Flask, jsonify
from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from

# --- create flask app ---
app = Flask(__name__)

# --- Define for Swagger ---
app.json_encoder = LazyJSONEncoder
swagger_template = dict(
info = {
    'title': LazyString(lambda: 'API Documentation for Data Processing and Modeling'),
    'version': LazyString(lambda: '1.0.0'),
    'description': LazyString(lambda: 'Dokumentasi API untuk Data Processing dan Modeling'),
    },
    host = LazyString(lambda: request.host)
)
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}
swagger = Swagger(app, template=swagger_template,
                  config=swagger_config)


# --- Define Regex for text Cleansing ---
def text_cleansing(text):
    text = re.sub(r"[^\x00-\x7F]+",'', text)
    text = re.sub(r"[^a-zA-Z0-9\s]+",'', text)
    text = re.sub('\n',' ', text) #remove every '\n'
    text = re.sub('rt',' ', text) # remove every retweet symbol
    text = re.sub('user',' ', text) #remove every username
    text = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))',' ',text) #remove url
    text = re.sub('  +',' ', text) #remove extra space  
    text = re.sub('[^0-9a-zA-Z]+', ' ', text)
    return text

# --- Endpoint for text input processing ---
@swag_from('docs/text-processing.yaml', methods=['GET'])   # --- End point for Swagger ---
@app.route('/text-processing', methods=['GET'])

# --- Define text Processing ---
def text_processing():
    add_text = request.args.get('add_text')
    #Json response for successful message
    if add_text:
        json_response = {
              'status_code': 200,
              'description': "Result from text cleansing, Successful response !!!",
              'data': text_cleansing(add_text),
          }

        response_data = jsonify(json_response)
        return response_data,200
    else:
      #Json response for error message
        json_response = {
              'status_code': 400,
              'description': "Text data is null",
          }

        response_data = jsonify(json_response) 
    return response_data,400

# --- Endpoint route for file processing ---  
@swag_from('docs/file-processing.yaml', methods=['POST'])
@app.route('/file-processing', methods=['POST'])
# --- Define file processing function ---  
def file_processing():
    if "file" in request.files:
      file = request.files['file']
      # Save temporary file in server
      file.save("cleansing_file.csv")
      df = pd.read_csv("cleansing_file.csv",header=None)
      text = df.values.tolist()
      clean_text = []

      for i in text:
        clean_text.append(text_cleansing(i[0]))
        
        
      # Json response for successful request
      json_response = {
              'status_code': 200,
              'description': "Result from file cleansing, Successful response !!!",
              'data': clean_text,
          }

      response_data = jsonify(json_response)
      return response_data,200
    
    else:
      #Json response for unsuccessful request
      json_response = {
              'status_code': 400,
              'description': "No file inputed",
          }
    return jsonify(json_response),400

def database_txt(kolom1, kolom2):
    conn = sqlite3.connect ("challenge.db")
    cursor = conn.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS result_cleansing (input, output)""")
    cursor.execute("""INSERT INTO result_cleansing (input, output) VALUES (?,?)""",(kolom1, kolom2))

    conn.commit()
    cursor.close()
    conn.close()
  

def databse_csv(data):
    conn = sqlite3.connect("challenge.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS result_cleansing (input, output)""")
    data.to_sql ('result_cleansing', conn, if_exists = 'append', index = False)


if __name__ == '__main__':
    # run app in debug mode on port 4000
    app.run(host='0.0.0.0',debug=True, port=4000)