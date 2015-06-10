from flask.views import MethodView
from flask.json import jsonify, dumps
from flask import request
from sqlalchemy import func

from app import app, db
from app.wordseer import wordseer
from app.models import *

from app.helpers.application_view import register_rest_view

class DocumentsView(MethodView):

    def get(self, **kwargs):
        params = dict(kwargs, **request.args)
        keys = params.keys()
        project = None
        query = None
        if "project_id" in keys:
            project = Project.query.get(params["project_id"])
            if "query_id" in keys:
                query = Query.query.get(params["query_id"])
        if project is None:
            abort(500)
        documents = project.get_documents()
        if query is not None:
            documents = db.session.query(
                Document.id.label('id'),
                func.count(Sentence.id.distinct()).label("matches")).\
                join(Sentence, Sentence.document_id == Document.id).\
                join(SentenceInQuery, Sentence.id == SentenceInQuery.sentence_id).\
            filter(SentenceInQuery.query_id == query.id).\
            group_by(Document.id)


        results = []
        for document_info in documents:
            document = Document.query.get(document_info.id)
            document_dict = {}
            for property in document.properties:
                document_dict[property.name] = property.value
            document_dict["id"] = document.id
            if query is not None:
                document_dict["matches"] = document_info.matches
            results.append(document_dict)
        return jsonify(results = results, total = len(results))

    def post(self):
        pass

    def delete(self, id):
        pass

    def put(self, id):
        pass
        
class SingleDocumentView(MethodView):

    def make_unit_metadata(self, unit):
        properties = []
        for property in unit.properties:
            metadata = property.property_metadata
            properties.append({
                    "property_name":property.name,
                    "value": property.value,
                    "name_is_displayed": metadata.display,
                    "value_is_displayed": metadata.display,
                    "is_category": metadata.is_category,
                    "name_to_display": metadata.display_name,
                })
        return properties

    def get_sets_for_sentence(self, sentence):
        sets = []
        properties = db.session.query(
            Property.name.label("property_name"),
            Property.value.label("value")).\
        join(PropertyOfSentence, PropertyOfSentence.property_id == Property.id).\
        filter(PropertyOfSentence.sentence_id == sentence.id).\
        filter(Property.name.contains("_set"))
        for property in properties:
            sets.append(property._asdict())
        return sets

    def make_sentence_info(self, sentence):
        info = {
            "sentence_id": sentence.id,
            "unit_name": "sentence",
            "document_id": sentence.document_id,
            "metadata": self.get_sets_for_sentence(sentence),
            "words": [{
                "word": word.surface,
                "word_id": word.id,
                "space_before": word.space_before}
                for word in sentence.word_in_sentence]
        }
        return info

    def add_unit_info(self, unit, info):
        if unit.name not in info["units"]:
            info["units"][unit.name] = {}
            info["children"][unit.name] = {}
        unit_info = {
            "unit_id": unit.id,
            "unit_name": unit.name,
            "parent_id": unit.parent_id,
            "metadata": self.make_unit_metadata(unit)
        }
        info["units"][unit.name][unit.id] = unit_info
        child_info = [
            {"id": child.id, "name": child.name} for child in unit.children]
        for child in unit.children:
            self.add_unit_info(child, info)
        for sentence in unit.sentences:
            print sentence.id
            child_info.append({"id": sentence.id, "name": "sentence"})
            info["units"]["sentence"][sentence.id] = self.make_sentence_info(
                sentence)
        info["children"][unit.name][unit.id] = child_info

    def get(self, **kwargs):
        params = dict(kwargs, **request.args)
        keys = params.keys()
        project = None
        document = None
        if "project_id" in keys:
            project = Project.query.get(params["project_id"])
            if "id" in keys:
                document = Document.query.get(params["id"][0])
        if project is None or document is None:
            return ""

        info = {
            "units": {"sentence": {}},
            "children": {"sentence": {}},
            "id": document.id,
            "has_text": True,
        }
        for property in document.properties:
            info[property.name] = property.value
        info["metadata"] = self.make_unit_metadata(document)
        self.add_unit_info(document, info)
        
        return jsonify(info)

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

register_rest_view(
    SingleDocumentView,
    wordseer,
    'single_document_view',
    'document_content',
    parents=["project"],
)