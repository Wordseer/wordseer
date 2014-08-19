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

        if "sentence_id" in kwargs.keys():
            sentence = Sentence.query.get(params["sentence_id"])

            if not sentence:
                # TODO: handle
                print("Sentence not found")

            return jsonify(properties = dumps(sentence.properties))

        elif "document_id" in kwargs.keys():
            document = Document.query.get(kwargs["document_id"])

            if not document:
                # TODO: handle
                print("Document not found")

            return jsonify(result = document.properties)

        elif "project_id" in kwargs.keys():
            project = Project.query.get(kwargs["project_id"])

            if not project:
                # TODO: real error response
                print("Project not found")

            properties = []

            if "unit" in params.keys():

                if params["unit"] == "document":
                    for document in project.get_documents():
                        properties.extend(document.properties)

                elif params["unit"] == "sentence":
                    sentences = []

                    for document in project.get_documents():
                        sentences.extend(document.all_sentences)

                    for sentence in sentences:
                        properties.extend(sentence.properties)

            else:
                properties = project.get_documents()[0].properties

            result = []
            for prop in properties:
                result.append({
                    "propertyName": prop.name,
                    "nameToDisplay":  prop.name,
                    "valueIsDisplayed": prop.value,
                    "type": prop.data_type
                })

            return jsonify(result = result)

        elif "property_id" in kwargs.keys():
            pass

        else:
            return

    def post(self):
        pass

    def delete(self, id):
        pass

    def put(self, id):
        pass
        

register_rest_view(
    PropertiesView,
    wordseer,
    'properties_view',
    'property',
    parents=["project", "document", "sentence"],
)