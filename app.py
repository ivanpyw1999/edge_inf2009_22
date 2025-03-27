from flask import Flask, render_template
from flask import request, jsonify

from extensions import db

from models.db import Product
from models.db import AdvertisementTargeting

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:Password123!@localhost/inf2009'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)




@app.route("/")
def homepage():
    products = Product.query.all()
    result = [
        {
            'id': product.id,
            'name': product.name,
            'category': product.category,
            # Not returning image binary data in this example.
        }
        for product in products
    ]
    return render_template("dashboard_statistics.html", products=result)


@app.route("/upload")
def upload_page():
	return render_template("dashboard_upload.html")

if __name__ == '__main__':
	app.run(host="0.0.0.0", port=5000, debug=True)