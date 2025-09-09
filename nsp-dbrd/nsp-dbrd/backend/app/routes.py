from flask import Blueprint, jsonify
from .database import get_connection

routes = Blueprint('routes', __name__)

@routes.route('/api/top-states', methods=['GET'])
def top_states():
    conn = get_connection('nsp_fresh')
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cur = conn.cursor()
        query = """
            SELECT state_name, COUNT(*) as applications
            FROM data_applicant_registration_details
            GROUP BY state_name
            ORDER BY applications DESC
            LIMIT 8
        """
        cur.execute(query)
        results = cur.fetchall()
        data = [{"state": row[0], "applications": row[1]} for row in results]
        return jsonify(data)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@routes.route('/api/gender-distribution', methods=['GET'])
def gender_distribution():
    conn = get_connection('nsp_fresh')
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cur = conn.cursor()
        query = """
            SELECT gender, COUNT(*) as count
            FROM data_applicant_registration_details
            GROUP BY gender
        """
        cur.execute(query)
        results = cur.fetchall()
        total = sum(row[1] for row in results)
        data = [{"gender": row[0], "count": row[1], "percentage": round(row[1] / total * 100, 1)} for row in results]
        return jsonify(data)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@routes.route('/api/categories', methods=['GET'])
def categories():
    conn = get_connection('nsp_fresh')
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cur = conn.cursor()
        query = """
            SELECT category_name, COUNT(*) as applications
            FROM data_applicant_registration_details
            GROUP BY category_name
        """
        cur.execute(query)
        results = cur.fetchall()
        data = [{"category": row[0], "applications": row[1]} for row in results]
        return jsonify(data)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@routes.route('/api/funding-breakdown', methods=['GET'])
def funding_breakdown():
    conn = get_connection('nsp_fresh')
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cur = conn.cursor()
        query = """
            SELECT SUM(pay_amt_state_shr) as state_share, SUM(pay_amt_centre_shr) as centre_share
            FROM data_applicant_payments_calculation
        """
        cur.execute(query)
        result = cur.fetchone()
        data = {
            "state_share": int(result[0]),
            "centre_share": int(result[1]),
            "total": int(result[0]) + int(result[1])
        }
        return jsonify(data)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

@routes.route('/api/income-distribution', methods=['GET'])
def income_distribution():
    conn = get_connection('nsp_fresh')
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    try:
        cur = conn.cursor()
        query = """
            SELECT annual_family_income
            FROM data_applicant_registration_details
            WHERE annual_family_income IS NOT NULL
        """
        cur.execute(query)
        results = cur.fetchall()
        income_data = [row[0] for row in results]
        mean_income = np.mean(income_data)
        median_income = np.median(income_data)
        counts, bins = np.histogram(income_data, bins=20)
        
        data = {
            "stats": {
                "mean": int(mean_income),
                "median": int(median_income)
            },
            "histogram": {
                "bins": bins.tolist(),
                "counts": counts.tolist()
            }
        }
        return jsonify(data)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()