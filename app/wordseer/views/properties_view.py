from flask.views import MethodView
from flask.json import jsonify, dumps
from flask import request

from app import app
from app.wordseer import wordseer
from app.models import *

from app.helpers.application_view import register_rest_view

class PropertiesView(MethodView):

    def get(self, **kwargs):

        params = dict(kwargs, **request.args)
        keys = params.keys()

        if "sentence_id" in keys:
            sentence = Sentence.query.get(kwargs["sentence_id"])

            if not sentence:
                # TODO: handle
                print("Sentence not found")

            return jsonify(properties = dumps(sentence.properties))

        elif "document_id" in keys:
            document = Document.query.get(kwargs["document_id"])

            if not document:
                # TODO: handle
                print("Document not found")

            return jsonify(result = document.properties)

        elif "project_id" in keys:
            project = Project.query.get(kwargs["project_id"])

            if not project:
                # TODO: real error response
                print("Project not found")

            properties = []

            if params["unit"] == "document":
                for document in project.get_documents():
                    properties.extend(document.properties)

            elif params["unit"] == "sentence":
                sentences = []

                for document in project.get_documents():
                    sentences.extend(document.all_sentences)

                for sentence in sentences:
                    properties.extend(sentence.properties)

            result = []
            for prop in properties:
                result.append({
                    "propertyName": prop.name,
                    "nameToDisplay":  prop.name,
                    "valueIsDisplayed": prop.value,
                    "type": prop.data_type
                })

            return jsonify(result = result)

        if "property_id" in keys:
            pass

    def post(self):
        pass

    def delete(self, property_id):
        pass

    def put(self, property_id):
        pass
        

register_rest_view(
    PropertiesView,
    wordseer,
    'properties_view',
    'property',
    parents=["project", "document", "sentence"],
)