from flask import Flask, request, jsonify, Response, send_file
import psycopg2
from psycopg2.extras import DictCursor
import logging
import pandas as pd
import io
import numpy as np
from scipy import stats

#----------------- Logging -----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------- DB Config -----------------
DB_CONFIGS = {
    'main': {
        'host': '10.192.145.144',
        'port': 5432,
        'user': 'nspquery',
        'password': 'nic123',
        'dbname': 'otrapi_db'
    },
    'nsp_fresh': {
        'host': '10.192.145.137',
        'port': 5432,
        'user': 'nspquery',
        'password': 'nic123',
        'dbname': 'nsp_fresh_2425'
    },
    'nsp_renewal': {
        'host': '10.192.145.139',
        'port': 5432,
        'user': 'nspquery',
        'password': 'nic123',
        'dbname': 'nsp_renewal_2425'
    }
}

# ----------------- DB Helpers -----------------
def get_connection(db_key: str):
    try:
        config = DB_CONFIGS[db_key]
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            user=config['user'],
            password=config['password'],
            dbname=config['dbname'],
            cursor_factory=DictCursor
        )
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to {db_key}: {e}")
        return None

app = Flask(__name__)

@app.route('/api/top-states', methods=['GET'])
def top_states():
    conn = get_connection('nsp_fresh')
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cur = conn.cursor()
        query = """
            SELECT r.application_id,
                r.permanent_address,
                d.district_name,
                s.state_name, 
                r.gender, 
                cat.category_name, 
                r.category_id,
                pay.pay_amt_state_shr,
                pay.pay_amt_centre_shr,
                r.annual_family_income,
                r.marital_status,
                marr.marital_status_name, 
                r.fresh_renewal,
                q.c_institution_id,
                dis.district_name as institute_district,                  
                sch.scheme_id, 
                mst.scheme_name
            FROM data_applicant_registration_details r 
            join mst_districts d 
            on d.district_id = r.permanent_district_id
            join mst_states s on s.state_id = d.state_id 
            join mst_category cat on cat.category_id = r.category_id
            join mst_marital_status marr on marr.marital_id = r.marital_status
            join data_applicant_qualifications q on q.application_id = r.application_id
            join data_applicant_applied_schemes sch on sch.application_id = r.application_id 
            join mst_schemes mst on mst.scheme_id = sch.scheme_id 
            join mst_institution inst on inst.institution_id = q.c_institution_id
            join mst_districts dis on dis.district_id= inst.district_id
            join data_applicant_payments_calculation pay on pay.application_id = r.application_id
            limit 1000
        """
        cur.execute(query)
        results = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        df = pd.DataFrame(results, columns=colnames)
        
        numeric_cols = ["pay_amt_state_shr", "pay_amt_centre_shr", "annual_family_income"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        
        df = df.dropna(subset=["pay_amt_state_shr", "pay_amt_centre_shr"], how="all")
        df['payment_amt_share'] = df[['pay_amt_state_shr', 'pay_amt_centre_shr']].sum(axis=1)
        
        state_counts = df['state_name'].value_counts().head(8)
        data = [{"state": k, "applications": int(v)} for k, v in state_counts.items()]
        
        return jsonify(data)
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/gender-distribution', methods=['GET'])
def gender_distribution():
    conn = get_connection('nsp_fresh')
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cur = conn.cursor()
        query = """
            SELECT r.application_id,
                r.permanent_address,
                d.district_name,
                s.state_name, 
                r.gender, 
                cat.category_name, 
                r.category_id,
                pay.pay_amt_state_shr,
                pay.pay_amt_centre_shr,
                r.annual_family_income,
                r.marital_status,
                marr.marital_status_name, 
                r.fresh_renewal,
                q.c_institution_id,
                dis.district_name as institute_district,                  
                sch.scheme_id, 
                mst.scheme_name
            FROM data_applicant_registration_details r 
            join mst_districts d 
            on d.district_id = r.permanent_district_id
            join mst_states s on s.state_id = d.state_id 
            join mst_category cat on cat.category_id = r.category_id
            join mst_marital_status marr on marr.marital_id = r.marital_status
            join data_applicant_qualifications q on q.application_id = r.application_id
            join data_applicant_applied_schemes sch on sch.application_id = r.application_id 
            join mst_schemes mst on mst.scheme_id = sch.scheme_id 
            join mst_institution inst on inst.institution_id = q.c_institution_id
            join mst_districts dis on dis.district_id= inst.district_id
            join data_applicant_payments_calculation pay on pay.application_id = r.application_id
            limit 1000
        """
        cur.execute(query)
        results = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        df = pd.DataFrame(results, columns=colnames)
        
        numeric_cols = ["pay_amt_state_shr", "pay_amt_centre_shr", "annual_family_income"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        
        df = df.dropna(subset=["pay_amt_state_shr", "pay_amt_centre_shr"], how="all")
        df['payment_amt_share'] = df[['pay_amt_state_shr', 'pay_amt_centre_shr']].sum(axis=1)
        
        gender_counts = df['gender'].value_counts()
        total = gender_counts.sum()
        data = [{"gender": k, "count": int(v), "percentage": round(v / total * 100, 1)} for k, v in gender_counts.items()]
        
        return jsonify(data)
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/categories', methods=['GET'])
def categories():
    conn = get_connection('nsp_fresh')
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cur = conn.cursor()
        query = """
            SELECT r.application_id,
                r.permanent_address,
                d.district_name,
                s.state_name, 
                r.gender, 
                cat.category_name, 
                r.category_id,
                pay.pay_amt_state_shr,
                pay.pay_amt_centre_shr,
                r.annual_family_income,
                r.marital_status,
                marr.marital_status_name, 
                r.fresh_renewal,
                q.c_institution_id,
                dis.district_name as institute_district,                  
                sch.scheme_id, 
                mst.scheme_name
            FROM data_applicant_registration_details r 
            join mst_districts d 
            on d.district_id = r.permanent_district_id
            join mst_states s on s.state_id = d.state_id 
            join mst_category cat on cat.category_id = r.category_id
            join mst_marital_status marr on marr.marital_id = r.marital_status
            join data_applicant_qualifications q on q.application_id = r.application_id
            join data_applicant_applied_schemes sch on sch.application_id = r.application_id 
            join mst_schemes mst on mst.scheme_id = sch.scheme_id 
            join mst_institution inst on inst.institution_id = q.c_institution_id
            join mst_districts dis on dis.district_id= inst.district_id
            join data_applicant_payments_calculation pay on pay.application_id = r.application_id
            limit 1000
        """
        cur.execute(query)
        results = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        df = pd.DataFrame(results, columns=colnames)
        
        numeric_cols = ["pay_amt_state_shr", "pay_amt_centre_shr", "annual_family_income"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        
        df = df.dropna(subset=["pay_amt_state_shr", "pay_amt_centre_shr"], how="all")
        df['payment_amt_share'] = df[['pay_amt_state_shr', 'pay_amt_centre_shr']].sum(axis=1)
        
        category_counts = df['category_name'].value_counts()
        data = [{"category": k, "applications": int(v)} for k, v in category_counts.items()]
        
        return jsonify(data)
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/funding-breakdown', methods=['GET'])
def funding_breakdown():
    conn = get_connection('nsp_fresh')
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cur = conn.cursor()
        query = """
            SELECT r.application_id,
                r.permanent_address,
                d.district_name,
                s.state_name, 
                r.gender, 
                cat.category_name, 
                r.category_id,
                pay.pay_amt_state_shr,
                pay.pay_amt_centre_shr,
                r.annual_family_income,
                r.marital_status,
                marr.marital_status_name, 
                r.fresh_renewal,
                q.c_institution_id,
                dis.district_name as institute_district,                  
                sch.scheme_id, 
                mst.scheme_name
            FROM data_applicant_registration_details r 
            join mst_districts d 
            on d.district_id = r.permanent_district_id
            join mst_states s on s.state_id = d.state_id 
            join mst_category cat on cat.category_id = r.category_id
            join mst_marital_status marr on marr.marital_id = r.marital_status
            join data_applicant_qualifications q on q.application_id = r.application_id
            join data_applicant_applied_schemes sch on sch.application_id = r.application_id 
            join mst_schemes mst on mst.scheme_id = sch.scheme_id 
            join mst_institution inst on inst.institution_id = q.c_institution_id
            join mst_districts dis on dis.district_id= inst.district_id
            join data_applicant_payments_calculation pay on pay.application_id = r.application_id
            limit 1000
        """
        cur.execute(query)
        results = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        df = pd.DataFrame(results, columns=colnames)
        
        numeric_cols = ["pay_amt_state_shr", "pay_amt_centre_shr", "annual_family_income"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        
        df = df.dropna(subset=["pay_amt_state_shr", "pay_amt_centre_shr"], how="all")
        df['payment_amt_share'] = df[['pay_amt_state_shr', 'pay_amt_centre_shr']].sum(axis=1)
        
        funding_data = df[['pay_amt_state_shr', 'pay_amt_centre_shr']].sum()
        data = {
            "state_share": int(funding_data['pay_amt_state_shr']),
            "centre_share": int(funding_data['pay_amt_centre_shr']),
            "total": int(funding_data.sum())
        }
        
        return jsonify(data)
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/income-distribution', methods=['GET'])
def income_distribution():
    conn = get_connection('nsp_fresh')
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cur = conn.cursor()
        query = """
            SELECT r.application_id,
                r.permanent_address,
                d.district_name,
                s.state_name, 
                r.gender, 
                cat.category_name, 
                r.category_id,
                pay.pay_amt_state_shr,
                pay.pay_amt_centre_shr,
                r.annual_family_income,
                r.marital_status,
                marr.marital_status_name, 
                r.fresh_renewal,
                q.c_institution_id,
                dis.district_name as institute_district,                  
                sch.scheme_id, 
                mst.scheme_name
            FROM data_applicant_registration_details r 
            join mst_districts d 
            on d.district_id = r.permanent_district_id
            join mst_states s on s.state_id = d.state_id 
            join mst_category cat on cat.category_id = r.category_id
            join mst_marital_status marr on marr.marital_id = r.marital_status
            join data_applicant_qualifications q on q.application_id = r.application_id
            join data_applicant_applied_schemes sch on sch.application_id = r.application_id 
            join mst_schemes mst on mst.scheme_id = sch.scheme_id 
            join mst_institution inst on inst.institution_id = q.c_institution_id
            join mst_districts dis on dis.district_id= inst.district_id
            join data_applicant_payments_calculation pay on pay.application_id = r.application_id
            limit 1000
        """
        cur.execute(query)
        results = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        df = pd.DataFrame(results, columns=colnames)
        
        numeric_cols = ["pay_amt_state_shr", "pay_amt_centre_shr", "annual_family_income"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        
        df = df.dropna(subset=["pay_amt_state_shr", "pay_amt_centre_shr"], how="all")
        df['payment_amt_share'] = df[['pay_amt_state_shr', 'pay_amt_centre_shr']].sum(axis=1)
        
        income_data = df['annual_family_income'].dropna()
        mean_income = income_data.mean()
        median_income = income_data.median()
        
        counts, bins = np.histogram(income_data, bins=20)
        
        density = stats.gaussian_kde(income_data)
        xs = np.linspace(income_data.min(), income_data.max(), 200)
        ys = density(xs)
        
        data = {
            "stats": {
                "mean": int(mean_income),
                "median": int(median_income)
            },
            "histogram": {
                "bins": bins.tolist(),
                "counts": counts.tolist()
            },
            "kde": {
                "x": xs.tolist(),
                "y": ys.tolist()
            }
        }
        
        return jsonify(data)
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/top-districts-payments', methods=['GET'])
def top_districts_payments():
    conn = get_connection('nsp_fresh')
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cur = conn.cursor()
        query = """
            SELECT r.application_id,
                r.permanent_address,
                d.district_name,
                s.state_name, 
                r.gender, 
                cat.category_name, 
                r.category_id,
                pay.pay_amt_state_shr,
                pay.pay_amt_centre_shr,
                r.annual_family_income,
                r.marital_status,
                marr.marital_status_name, 
                r.fresh_renewal,
                q.c_institution_id,
                dis.district_name as institute_district,                  
                sch.scheme_id, 
                mst.scheme_name
            FROM data_applicant_registration_details r 
            join mst_districts d 
            on d.district_id = r.permanent_district_id
            join mst_states s on s.state_id = d.state_id 
            join mst_category cat on cat.category_id = r.category_id
            join mst_marital_status marr on marr.marital_id = r.marital_status
            join data_applicant_qualifications q on q.application_id = r.application_id
            join data_applicant_applied_schemes sch on sch.application_id = r.application_id 
            join mst_schemes mst on mst.scheme_id = sch.scheme_id 
            join mst_institution inst on inst.institution_id = q.c_institution_id
            join mst_districts dis on dis.district_id= inst.district_id
            join data_applicant_payments_calculation pay on pay.application_id = r.application_id
            limit 1000
        """
        cur.execute(query)
        results = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        df = pd.DataFrame(results, columns=colnames)
        
        numeric_cols = ["pay_amt_state_shr", "pay_amt_centre_shr", "annual_family_income"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        
        df = df.dropna(subset=["pay_amt_state_shr", "pay_amt_centre_shr"], how="all")
        df['payment_amt_share'] = df[['pay_amt_state_shr', 'pay_amt_centre_shr']].sum(axis=1)
        
        district_payments = df.groupby('institute_district')['payment_amt_share'].sum().sort_values(ascending=False).head(8)
        total = district_payments.sum()
        data = [{"district": k, "payment": int(v), "percentage": round(v / total * 100, 1)} for k, v in district_payments.items()]
        
        return jsonify(data)
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/top-schemes-payments', methods=['GET'])
def top_schemes_payments():
    conn = get_connection('nsp_fresh')
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cur = conn.cursor()
        query = """
            SELECT r.application_id,
                r.permanent_address,
                d.district_name,
                s.state_name, 
                r.gender, 
                cat.category_name, 
                r.category_id,
                pay.pay_amt_state_shr,
                pay.pay_amt_centre_shr,
                r.annual_family_income,
                r.marital_status,
                marr.marital_status_name, 
                r.fresh_renewal,
                q.c_institution_id,
                dis.district_name as institute_district,                  
                sch.scheme_id, 
                mst.scheme_name
            FROM data_applicant_registration_details r 
            join mst_districts d 
            on d.district_id = r.permanent_district_id
            join mst_states s on s.state_id = d.state_id 
            join mst_category cat on cat.category_id = r.category_id
            join mst_marital_status marr on marr.marital_id = r.marital_status
            join data_applicant_qualifications q on q.application_id = r.application_id
            join data_applicant_applied_schemes sch on sch.application_id = r.application_id 
            join mst_schemes mst on mst.scheme_id = sch.scheme_id 
            join mst_institution inst on inst.institution_id = q.c_institution_id
            join mst_districts dis on dis.district_id= inst.district_id
            join data_applicant_payments_calculation pay on pay.application_id = r.application_id
            limit 1000
        """
        cur.execute(query)
        results = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        df = pd.DataFrame(results, columns=colnames)
        
        numeric_cols = ["pay_amt_state_shr", "pay_amt_centre_shr", "annual_family_income"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        
        df = df.dropna(subset=["pay_amt_state_shr", "pay_amt_centre_shr"], how="all")
        df['payment_amt_share'] = df[['pay_amt_state_shr', 'pay_amt_centre_shr']].sum(axis=1)
        
        scheme_payments = df.groupby('scheme_name')['payment_amt_share'].sum().sort_values(ascending=False).head(8)
        total = scheme_payments.sum()
        data = [{"scheme": k, "payment": int(v), "percentage": round(v / total * 100, 1)} for k, v in scheme_payments.items()]
        
        return jsonify(data)
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/category-payments', methods=['GET'])
def category_payments():
    conn = get_connection('nsp_fresh')
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cur = conn.cursor()
        query = """
            SELECT r.application_id,
                r.permanent_address,
                d.district_name,
                s.state_name, 
                r.gender, 
                cat.category_name, 
                r.category_id,
                pay.pay_amt_state_shr,
                pay.pay_amt_centre_shr,
                r.annual_family_income,
                r.marital_status,
                marr.marital_status_name, 
                r.fresh_renewal,
                q.c_institution_id,
                dis.district_name as institute_district,                  
                sch.scheme_id, 
                mst.scheme_name
            FROM data_applicant_registration_details r 
            join mst_districts d 
            on d.district_id = r.permanent_district_id
            join mst_states s on s.state_id = d.state_id 
            join mst_category cat on cat.category_id = r.category_id
            join mst_marital_status marr on marr.marital_id = r.marital_status
            join data_applicant_qualifications q on q.application_id = r.application_id
            join data_applicant_applied_schemes sch on sch.application_id = r.application_id 
            join mst_schemes mst on mst.scheme_id = sch.scheme_id 
            join mst_institution inst on inst.institution_id = q.c_institution_id
            join mst_districts dis on dis.district_id= inst.district_id
            join data_applicant_payments_calculation pay on pay.application_id = r.application_id
            limit 1000
        """
        cur.execute(query)
        results = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        df = pd.DataFrame(results, columns=colnames)
        
        numeric_cols = ["pay_amt_state_shr", "pay_amt_centre_shr", "annual_family_income"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        
        df = df.dropna(subset=["pay_amt_state_shr", "pay_amt_centre_shr"], how="all")
        df['payment_amt_share'] = df[['pay_amt_state_shr', 'pay_amt_centre_shr']].sum(axis=1)
        
        category_payments = df.groupby('category_name')['payment_amt_share'].sum().sort_values(ascending=False)
        data = [{"category": k, "payment": int(v)} for k, v in category_payments.items()]
        
        return jsonify(data)
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/gender-payments', methods=['GET'])
def gender_payments():
    conn = get_connection('nsp_fresh')
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cur = conn.cursor()
        query = """
            SELECT r.application_id,
                r.permanent_address,
                d.district_name,
                s.state_name, 
                r.gender, 
                cat.category_name, 
                r.category_id,
                pay.pay_amt_state_shr,
                pay.pay_amt_centre_shr,
                r.annual_family_income,
                r.marital_status,
                marr.marital_status_name, 
                r.fresh_renewal,
                q.c_institution_id,
                dis.district_name as institute_district,                  
                sch.scheme_id, 
                mst.scheme_name
            FROM data_applicant_registration_details r 
            join mst_districts d 
            on d.district_id = r.permanent_district_id
            join mst_states s on s.state_id = d.state_id 
            join mst_category cat on cat.category_id = r.category_id
            join mst_marital_status marr on marr.marital_id = r.marital_status
            join data_applicant_qualifications q on q.application_id = r.application_id
            join data_applicant_applied_schemes sch on sch.application_id = r.application_id 
            join mst_schemes mst on mst.scheme_id = sch.scheme_id 
            join mst_institution inst on inst.institution_id = q.c_institution_id
            join mst_districts dis on dis.district_id= inst.district_id
            join data_applicant_payments_calculation pay on pay.application_id = r.application_id
            limit 1000
        """
        cur.execute(query)
        results = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        df = pd.DataFrame(results, columns=colnames)
        
        numeric_cols = ["pay_amt_state_shr", "pay_amt_centre_shr", "annual_family_income"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        
        df = df.dropna(subset=["pay_amt_state_shr", "pay_amt_centre_shr"], how="all")
        df['payment_amt_share'] = df[['pay_amt_state_shr', 'pay_amt_centre_shr']].sum(axis=1)
        
        gender_payments = df.groupby('gender')['payment_amt_share'].sum().sort_values(ascending=False)
        data = [{"gender": k, "payment": int(v)} for k, v in gender_payments.items()]
        
        return jsonify(data)
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/top-schemes-applications', methods=['GET'])
def top_schemes_applications():
    conn = get_connection('nsp_fresh')
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cur = conn.cursor()
        query = """
            SELECT r.application_id,
                r.permanent_address,
                d.district_name,
                s.state_name, 
                r.gender, 
                cat.category_name, 
                r.category_id,
                pay.pay_amt_state_shr,
                pay.pay_amt_centre_shr,
                r.annual_family_income,
                r.marital_status,
                marr.marital_status_name, 
                r.fresh_renewal,
                q.c_institution_id,
                dis.district_name as institute_district,                  
                sch.scheme_id, 
                mst.scheme_name
            FROM data_applicant_registration_details r 
            join mst_districts d 
            on d.district_id = r.permanent_district_id
            join mst_states s on s.state_id = d.state_id 
            join mst_category cat on cat.category_id = r.category_id
            join mst_marital_status marr on marr.marital_id = r.marital_status
            join data_applicant_qualifications q on q.application_id = r.application_id
            join data_applicant_applied_schemes sch on sch.application_id = r.application_id 
            join mst_schemes mst on mst.scheme_id = sch.scheme_id 
            join mst_institution inst on inst.institution_id = q.c_institution_id
            join mst_districts dis on dis.district_id= inst.district_id
            join data_applicant_payments_calculation pay on pay.application_id = r.application_id
            limit 1000
        """
        cur.execute(query)
        results = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        df = pd.DataFrame(results, columns=colnames)
        
        numeric_cols = ["pay_amt_state_shr", "pay_amt_centre_shr", "annual_family_income"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        
        df = df.dropna(subset=["pay_amt_state_shr", "pay_amt_centre_shr"], how="all")
        df['payment_amt_share'] = df[['pay_amt_state_shr', 'pay_amt_centre_shr']].sum(axis=1)
        
        scheme_counts = df['scheme_name'].value_counts().head(8)
        data = [{"scheme": k, "applications": int(v)} for k, v in scheme_counts.items()]
        
        return jsonify(data)
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@app.route('/api/summary', methods=['GET'])
def summary():
    conn = get_connection('nsp_fresh')
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cur = conn.cursor()
        query = """
            SELECT r.application_id,
                r.permanent_address,
                d.district_name,
                s.state_name, 
                r.gender, 
                cat.category_name, 
                r.category_id,
                pay.pay_amt_state_shr,
                pay.pay_amt_centre_shr,
                r.annual_family_income,
                r.marital_status,
                marr.marital_status_name, 
                r.fresh_renewal,
                q.c_institution_id,
                dis.district_name as institute_district,                  
                sch.scheme_id, 
                mst.scheme_name
            FROM data_applicant_registration_details r 
            join mst_districts d 
            on d.district_id = r.permanent_district_id
            join mst_states s on s.state_id = d.state_id 
            join mst_category cat on cat.category_id = r.category_id
            join mst_marital_status marr on marr.marital_id = r.marital_status
            join data_applicant_qualifications q on q.application_id = r.application_id
            join data_applicant_applied_schemes sch on sch.application_id = r.application_id 
            join mst_schemes mst on mst.scheme_id = sch.scheme_id 
            join mst_institution inst on inst.institution_id = q.c_institution_id
            join mst_districts dis on dis.district_id= inst.district_id
            join data_applicant_payments_calculation pay on pay.application_id = r.application_id
            limit 1000
        """
        cur.execute(query)
        results = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        df = pd.DataFrame(results, columns=colnames)
        
        numeric_cols = ["pay_amt_state_shr", "pay_amt_centre_shr", "annual_family_income"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        
        df = df.dropna(subset=["pay_amt_state_shr", "pay_amt_centre_shr"], how="all")
        df['payment_amt_share'] = df[['pay_amt_state_shr', 'pay_amt_centre_shr']].sum(axis=1)
        
        total_applications = len(df)
        total_funding = df['payment_amt_share'].sum()
        avg_payment = df['payment_amt_share'].mean()
        
        data = {
            "total_applications": int(total_applications),
            "total_funding": int(total_funding),
            "avg_payment": int(avg_payment)
        }
        
        return jsonify(data)
    
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    app.run(debug=True)