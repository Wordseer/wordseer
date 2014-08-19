from flask.views import MethodView
from flask.json import jsonify, dumps
from flask import request

from app import app, db
from app.wordseer import wordseer
from app.models import *

from app.helpers.application_view import register_rest_view

class DocumentsView(MethodView):

    def get(self, **kwargs):
        params = dict(kwargs, **request.args)
        keys = params.keys()

        if "project_id" in keys:
            project = Project.query.get(params["project_id"])
            documents = project.get_documents()

            results = list()

            for document in documents:
                document_dict = dict()

                for property in document.properties:
                    document_dict[property.name] = property.value

                document_dict["id"] = document.id

                results.append(document_dict)

            return jsonify(results = results)

    def post(self):
        pass

    def delete(self, id):
        pass

    def put(self, id):
        pass
        
register_rest_view(
    DocumentsView,
    wordseer,
    'documents_view',
    'document',
    parents=["project"],
)