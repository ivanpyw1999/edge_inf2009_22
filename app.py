from flask import Flask, render_template
from flask import request, jsonify

from extensions import db
from sqlalchemy import func

from models.db import Product
from models.db import AdvertisementTargeting

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:Password123!@localhost/inf2009'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)


@app.route("/")
def homepage():
    # Total advertisements shown (sum of counters)
    total_ads = db.session.query(func.sum(AdvertisementTargeting.counter)).scalar() or 0

    # Top 5 advertisements by counter
    top_ads_records = AdvertisementTargeting.query.order_by(AdvertisementTargeting.counter.desc()).limit(5).all()
    top_ads = []
    for ad in top_ads_records:
        product = Product.query.get(ad.product_id)
        if product:
            top_ads.append({'name': product.name, 'counter': ad.counter})

    # Most popular item (highest counter)
    most_pop_ad = AdvertisementTargeting.query.order_by(AdvertisementTargeting.counter.desc()).first()
    popular = None
    if most_pop_ad:
        product = Product.query.get(most_pop_ad.product_id)
        if product:
            popular = {'name': product.name, 'counter': most_pop_ad.counter}

    # Least popular item (lowest counter)
    least_pop_ad = AdvertisementTargeting.query.order_by(AdvertisementTargeting.counter.asc()).first()
    least = None
    if least_pop_ad:
        product = Product.query.get(least_pop_ad.product_id)
        if product:
            least = {'name': product.name, 'counter': least_pop_ad.counter}

    # List all products for testing
    products = Product.query.all()
    products_result = [
         {
            'id': product.id,
            'name': product.name,
            'category': product.category,
         }
         for product in products
    ]
    return render_template(
         "dashboard_statistics.html",
         products=products_result,
         total_ads=total_ads,
         top_ads=top_ads,
         popular=popular,
         least=least
    )


@app.route("/upload")
def upload_page():
	return render_template("dashboard_upload.html")

if __name__ == '__main__':
	app.run(host="0.0.0.0", port=5000, debug=True)