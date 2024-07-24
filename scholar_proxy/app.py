from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flasgger import Swagger
from flasgger.utils import swag_from
from scholarly import ProxyGenerator, scholarly


def configure_proxy():
    proxy_gen = ProxyGenerator()
    proxy_gen.Luminati(usr='your_username', passwd='your_password', proxy_port=22225)
    scholarly.use_proxy(proxy_gen)


class ScholarSearch(Resource):
    @swag_from('swagger.yaml', methods=['GET'])
    def get(self):
        # api_key = request.headers.get('api_key')
        # if api_key != 'your_secure_api_key':  # Replace with your actual API key validation logic
        #     return {'message': 'Invalid API key'}, 401

        query = request.args.get('query')
        sources = request.args.getlist('sources')
        source_query = ' OR '.join([f'"{source}"' for source in sources])
        full_query = f'{query} source:{source_query}' if sources else query

        search_query = scholarly.search_pubs(full_query)
        results = []
        for i in range(10):  # Limiting to 10 results for demonstration
            try:
                results.append(next(search_query))
            except StopIteration:
                break

        return jsonify(results)


if __name__ == '__main__':
    configure_proxy()

    app = Flask(__name__)
    api = Api(app)
    swagger = Swagger(app, template_file='swagger.yaml')
    api.add_resource(ScholarSearch, '/scholar')
    app.run(debug=True, port=8000)
