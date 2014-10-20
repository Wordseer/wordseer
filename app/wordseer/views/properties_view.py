from flask.views import MethodView
from flask.json import jsonify, dumps
from flask import request

from app import app
from app.wordseer import wordseer
from app.models import *

from app.helpers.application_view import register_rest_view

class PropertiesView(MethodView):
    """ Lists the property types that apply to a type of unit. """
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
            properties = PropertyMetadata.query.\
                filter(PropertyMetadata.is_category == True)
            if "unit" in params.keys() and params["unit"][0] == "document":
                properties = properties.filter(
                    PropertyMetadata.unit_type == "document")

            result = []
            for prop in properties:
                result.append({
                    "nameToDisplay": prop.display_name,
                    "propertyName": prop.property_name,
                    "type": prop.data_type,
                    "valueIsDisplayed": prop.display,
                })
            return jsonify(results = result)


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

class PropertiesMetaView(MethodView):

    def get(self, **kwargs):

        params = dict(kwargs, **request.args)

        if "project_id" in kwargs.keys():
            project = Project.query.get(kwargs["project_id"])

            if not project:
                # TODO: real error response
                print("Project not found")

            # TODO: this sucks but PropertyMetadata is not being populated by
            # the preprocessor so this is the only alternative
            property_meta = { i.name: i.data_type for i in Property.query.all() }

            result = []

            for prop in property_meta.keys():
                ctype = property_meta[prop]
                if ctype == None:
                    ctype = "string"
                result.append({
                    "propertyName": prop,
                    "text":  prop,
                    "type": ctype
                })

            return jsonify(results = result)

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

register_rest_view(
    PropertiesMetaView,
    wordseer,
    'properties_meta_view',
    'meta_property',
    parents=["project", "document", "sentence"],
)
