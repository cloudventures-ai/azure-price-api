from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

DB = {
    "host": "db.kzwfztlddqunzljgbskx.supabase.co",
    "port": 5432,
    "dbname": "postgres",
    "user": "postgres",
    "password": "John1rob2!@#"
}

@app.route("/price")
def get_price():
    sku = request.args.get("sku")
    region = request.args.get("region")
    hours = float(request.args.get("hours", 1))

    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    cur.execute("""
        SELECT unit_price
        FROM azure_prices
        WHERE lower(sku_name) = lower(%s) AND lower(arm_region_name) = lower(%s)
        ORDER BY unit_price ASC
        LIMIT 1
    """, (sku, region))

    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return jsonify({ "error": "No match found." }), 404

    price_per_hour = row[0]
    total_price = round(price_per_hour * hours, 4)

    return jsonify({
        "price_per_hour": price_per_hour,
        "total_price": total_price
    })

@app.route("/regions")
def get_regions():
    try:
        conn = psycopg2.connect(**DB)
        cur = conn.cursor()

        cur.execute("""
            SELECT DISTINCT arm_region_name
            FROM azure_prices
            WHERE arm_region_name IS NOT NULL
            ORDER BY arm_region_name ASC
        """)

        rows = cur.fetchall()
        regions = [row[0] for row in rows]

        cur.close()
        conn.close()

        return jsonify(regions)

    except Exception as e:
        return jsonify({ "error": str(e) }), 500


