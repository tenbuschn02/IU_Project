from website import create_app
from waitress import serve
import logging

app = create_app()

if __name__ == '__main__':
    # app.run(debug=False)
    # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
    serve(app)
