from flask.views import MethodView
from flask.json import jsonify, dumps
from flask import request
from sqlalchemy import func

from app import app
from app.wordseer import wordseer
from app.models import *


from app.helpers.application_view import register_rest_view

class PropertiesMetaView(MethodView):
    """ Lists the property types that apply to a type of unit. """
    def get(self, **kwargs):
        params = dict(kwargs, **request.args)
        project = None
        if "project_id" in kwargs.keys():
            project = Project.query.get(kwargs["project_id"])
        if project is None:
            # TODO: real error response
            print("Project not found")

        properties = PropertyMetadata.query.\
            filter(PropertyMetadata.is_category == True)
        if "unit" in params.keys():
            if params["unit"][0] == "document":
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

    def post(self):
        pass

    def delete(self, id):
        pass

    def put(self, id):
        pass

class PropertiesView(MethodView):
    """ Lists all the property values of the sentences specified by the
    parameters. Depending on the view that is asked for, returns them as a
    list of property values (view=list) or as a hierarchy, where the list
    of property names is the top level and the values for a given property are
    under it. 
    """
    def get(self, **kwargs):
        params = dict(kwargs, **request.args)
        project = None
        if "project_id" in kwargs.keys():
            project = Project.query.get(kwargs["project_id"])
        if project is None:
            # TODO: real error response
            print("Project not found")

        view_type = params.get("view")[0]

        properties = db.session.query(
            PropertyMetadata.property_name.label("property_name"),
            PropertyMetadata.data_type.label("data_type"),
            PropertyMetadata.date_format.label("date_format")).\
        join(Property, Property.property_metadata_id == PropertyMetadata.id).\
        filter(Property.project_id == project.id).\
        filter(PropertyMetadata.is_category == True).\
        group_by(PropertyMetadata.property_name)

        results = []
        for property in properties:
            type = property.data_type
            if type == "date":
                type += "_" + property.date_format

            values = db.session.query(
                Property.value.label("value"),
                func.count(Property.unit_id.distinct()).label("unit_count")).\
            filter(Property.project_id == project.id).\
            filter(Property.name == property.property_name).\
            group_by(Property.value)

            if "query_id" in params:
                # Restrict to just the sentences that match the given query.
                values = values.join(
                PropertyOfSentence,
                    PropertyOfSentence.property_id == Property.id).\
                join(SentenceInQuery,
                    PropertyOfSentence.sentence_id ==
                    SentenceInQuery.sentence_id).\
                filter(SentenceInQuery.query_id == params["query_id"][0])

            metadata = {
                "propertyName": property.property_name,
                "displayName": property.property_name,
                "text": property.property_name,
                "type": type,
                "children": []
            }
            for value in values:
                property_value = {
                        "count": value.unit_count,
                        "document_count": value.unit_count,
                        "propertyName": property.property_name,
                        "displayName": property.property_name,
                        "text": value.value,
                        "value": value.value,
                        "leaf": True
                        }
                if view_type == "list":
                    results.append(property_value)
                elif view_type == "tree":
                    metadata["children"].append(property_value)
            if view_type == "tree":
                results.append(metadata)
        return jsonify(children = results)

    def post(self):
        pass

    def delete(self, id):
        pass

    def put(self, id):
        pass

register_rest_view(
    PropertiesMetaView,
    wordseer,
    'properties_meta_view',
    'meta_property',
    parents=["project", "document", "sentence"],
)

register_rest_view(
    PropertiesView,
    wordseer,
    'properties_view',
    'property',
    parents=["project", "document", "sentence"],
)
