from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def homepage():
	return render_template("dashboard_statistics.html")

@app.route("/upload")
def upload_page():
	return render_template("dashboard_upload.html")

if __name__ == '__main__':
	app.run(debug=True)