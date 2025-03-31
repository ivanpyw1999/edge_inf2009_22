from flask import Flask, flash, redirect, render_template, url_for
from flask import request, jsonify
import json

from extensions import db
from sqlalchemy import func

from models.db import Product
from models.db import AdvertisementTargeting

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:Password123!@localhost:3306/inf2009'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://user:Password123!@192.168.122.230:3306/inf2009'

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
        product = db.session.get(Product, ad.product_id)
        if product:
            top_ads.append({'name': product.name, 'counter': ad.counter})

    # Most popular item (highest counter)
    most_pop_ad = AdvertisementTargeting.query.order_by(AdvertisementTargeting.counter.desc()).first()
    popular = None
    if most_pop_ad:
        product = db.session.get(Product, most_pop_ad.product_id)
        if product:
            popular = {'name': product.name, 'counter': most_pop_ad.counter}

    # Least popular item (lowest counter)
    least_pop_ad = AdvertisementTargeting.query.order_by(AdvertisementTargeting.counter.asc()).first()
    least = None
    if least_pop_ad:
        product = db.session.get(Product, least_pop_ad.product_id)
        if product:
            least = {'name': product.name, 'counter': least_pop_ad.counter}

    # New query: Sum engagement per category
    category_results = db.session.query(
        Product.category,
        func.sum(AdvertisementTargeting.counter).label('total')
    ).join(
        Product, Product.id == AdvertisementTargeting.product_id
    ).group_by(
        Product.category
    ).all()

    # Prepare lists for categories and their total engagement
    categories = [row.category for row in category_results]
    totals = [row.total for row in category_results]

    category_engagement_data = {
        'categories': categories,
        'totals': totals
    }

    return render_template(
        "dashboard_statistics.html",
        total_ads=total_ads,
        top_ads=top_ads,
        popular=popular,
        least=least,
        category_engagement_data=category_engagement_data
    )


@app.route('/upload', methods=['GET', 'POST'])
def upload_advertisement():
    error_message = None
    if request.method == 'POST':
        # Get product details from the form
        product_name = request.form.get('product-name')
        product_category = request.form.get('category')

        # Get advertisement targeting details from the form
        target_audience = request.form.get('target-audience')
        target_gender = request.form.get('gender')
        # Get the raw keywords string from the form
        raw_keywords = request.form.get('Keywords')

        # Optionally handle file upload if needed:
        image_file = request.files.get('file-upload')
        image_data = image_file.read() if image_file else None

        # Checks if fields are not empty
        if not (product_name and product_category and target_audience and target_gender and raw_keywords and image_file):
            error_message = "All fields are required. Please fill in all the fields before submitting."
            # Instead of flashing and redirecting, re-render the template with the error message.
            return render_template('dashboard_upload.html', error_message=error_message, form_data=request.form)

        # Convert the string into a list of keywords and then to a JSON string
        keywords_list = [kw.strip() for kw in raw_keywords.split(',')]
        json_keywords = json.dumps(keywords_list)

        # Create the product first
        new_product = Product(
            name=product_name,
            category=product_category,
            image=image_data
        )
        db.session.add(new_product)
        db.session.flush()  # Flush to assign new_product.id

        # Create an AdvertisementTargeting record linked to the product.
        new_targeting = AdvertisementTargeting(
            product_id=new_product.id,
            targeted_audience=target_audience,
            targeted_gender=target_gender,
            keyword=json_keywords
        )
        db.session.add(new_targeting)
        db.session.commit()

        return redirect(url_for('homepage'))

    return render_template('dashboard_upload.html')




@app.route('/update/<int:productID>', methods=['PUT'])
def update_API(productID):
    # Find the AdvertisementTargeting record associated with the given productID
    ad_target = AdvertisementTargeting.query.filter_by(product_id=productID).first()
    if not ad_target:
        return jsonify({"error": f"No advertisement targeting record found for productID {productID}"}), 404

    # Increment the counter by 1 and commit the change
    ad_target.counter += 1
    db.session.commit()

    # Return the updated counter value in a JSON response
    return jsonify({
        "message": "Counter incremented successfully",
        "productID": productID,
        "newCounter": ad_target.counter
    }), 200



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
