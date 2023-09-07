from flask import Flask, render_template_string

import warnings
# Filter out the specific warning message
warnings.filterwarnings("ignore", message="loaded more than 1 DLL from .libs")

import pandas as pd
import fredapi as fa
import wbdata


from dotenv import load_dotenv
import os


app = Flask(__name__)



# Load environment variables from .env
load_dotenv()

# Access the variables in your application
app.config['API_KEY'] = os.getenv('API_KEY')


fred = fa.Fred(app.config['API_KEY'])


@app.route('/', methods=['GET'])
def main():
    return render_template_string('''
    <!doctype html>    
    <html>
        <head>  
        <title>Economic Data API | Endpoints</title>          
        </head>
        <body>
            <h1>Endpoints:</h1>
            <ul>
                <li><a href="/api/median_price_houses_sold/median_household_income">/api/median_price_houses_sold/median_household_income</a></li>            
                <li><a href="/api/homeownership_rate_usa">/api/homeownership_rate_usa</a></li>            
                <li><a href="/api/employment_industry">/api/employment_industry</a></li>            
                <li><a href="/api/debt_balance">/api/debt_balance</a></li>            
                <li><a href="/api/income_inequality">/api/income_inequality</a></li>            
                <li><a href="/api/class_identification_gallup">/api/class_identification_gallup</a></li>            
                <li><a href="/api/global_manufacturing_2019">/api/global_manufacturing_2019</a></li>            
            </ul>
        </body>
    </html>
    ''')



@app.route('/api/median_price_houses_sold/median_household_income', methods=['GET'])
def get_price_houses():
    household_income      = fred.get_series('MEHOINUSA672N')
    household_income.name = "Real Median Household Income in the United States"
    price_houses          = fred.get_series('MSPUS')
    price_houses.name     = "Median Sales Price of Houses Sold for the United States"
    df = pd.merge(price_houses,household_income,left_index=True,right_index=True)   

    df.reset_index(inplace=True)      
    df['index'] = df['index'].astype(str)  
    return df.to_json(orient='records') 



@app.route('/api/homeownership_rate_usa', methods=['GET'])
def get_homeownership_rate():
    homeownership      = fred.get_series('RHORUSQ156N')
    homeownership.name = "Homeownership Rate in the United States"
    df = pd.DataFrame(data=homeownership) 

    df.reset_index(inplace=True)      
    df['index'] = df['index'].astype(str) 
    return df.to_json(orient='records')



@app.route('/api/employment_industry', methods=['GET'])
def get_employment_industry():
    
    # Define the indicator code for "Employment in industry (% of total employment) (modeled ILO estimate)"
    indicator = {'SL.IND.EMPL.ZS': 'employment_in_industry'}
    
    # Define a list of ISO country codes for the countries you are interested in
    countries = ["US","GB","JP","DE","CN","VN","IT","FR"]
    
    # Set the data date range 
    data_date = (pd.to_datetime('1991-01-01'), pd.to_datetime('2021-01-01'))
    
    data = wbdata.get_dataframe(indicator, country=countries,data_date=data_date)
    
    # Reset the index to include date as a column
    data.reset_index(inplace=True)

    # Pivot the DataFrame to have countries as columns and date as the index
    df = data.pivot(index='date', columns='country', values='employment_in_industry')  
    
    df.reset_index(inplace=True)      
  
    return df.to_json(orient='records')



@app.route('/api/debt_balance', methods=['GET'])
def get_debt_balance():
    
    csv_file = "csv_files/HHD_C_Report_2023Q2.csv"    
    df = pd.read_csv(csv_file, delimiter=" ",header=None, index_col=0)
    
    df.columns = ["Mortgage", "HE Revolving", "Auto Loan", "Credit Card", "Student Loan", "Other", "Total"]

    # Convert all columns to float
    df = df.apply(pd.to_numeric, errors='coerce')
    
    df.reset_index(inplace=True)       
    df[0] = df[0].astype(str) 
    return df.to_json(orient='records')



@app.route('/api/income_inequality', methods=['GET'])
def get_income_inequality():
    csv_file = "csv_files/income_inequality.csv"    
    df = pd.read_csv(csv_file, delimiter=",", index_col=0)  
    
    # Remove the "%" sign and convert to float
    df = df.apply(lambda x: x.str.replace('%', '').astype(float))
    
    df.reset_index(inplace=True)     
    
    return df.to_json(orient='records')



@app.route('/api/class_identification_gallup', methods=['GET'])
def get_class_identification():  
    csv_file = "csv_files/socialclass_identification_gallup.csv"    
    df = pd.read_csv(csv_file, delimiter=",", index_col=0)  

    # Convert all columns to float
    df = df.apply(pd.to_numeric, errors='coerce') 
    df.reset_index(inplace=True)   
    
    return df.to_json(orient='records')



@app.route('/api/global_manufacturing_2019', methods=['GET'])
def get_global_manufacturing():
    csv_file = "csv_files/global_manufacturing_output_2019.csv"
    df = pd.read_csv(csv_file, delimiter=",")  

    # Convert all columns to float
    df = df.apply(pd.to_numeric, errors='coerce')     
    
    return df.to_json(orient='records')



# Run the application if this file is executed
if __name__ == '__main__':
    app.run(debug=True)