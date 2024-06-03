from flask import Flask, render_template, request, json
from main import main
from flask import stream_with_context

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
    scraped_data = main(keyword, quantity)

    # Stream the scraped data back to the client
    def generate():
        for listing in scraped_data:
            # Convert listing to JSON and encode as bytes
            yield (json.dumps([listing[key] for key in listing]) + '\n').encode('utf-8')
    
    return app.response_class(stream_with_context(generate()), mimetype='application/json')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)