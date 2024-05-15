from flask import Flask, render_template, request, jsonify
from main import main, business_list_to_table_rows

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    # Get keyword and quantity from the form
    keyword = request.json['keyword']
    quantity = int(request.json['quantity'])

    # Call the scraping function with the keyword and quantity
    scraped_data = list(main(keyword, quantity))

    # Converts the BusinessList to a list of lists for the HTML table
    rows = business_list_to_table_rows(scraped_data)

    return jsonify(rows)
if __name__ == "__main__":
    app.run(debug=True)