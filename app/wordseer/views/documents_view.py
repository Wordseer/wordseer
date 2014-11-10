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
            filter(SentenceInQuery.query_id == query.id)

        results = []
        for document_info in documents:
            document = Document.query.get(document_info.id)
            document_dict = {}
            for property in document.properties:
                document_dict[property.name] = property.value
            document_dict["id"] = document.id
            document_dict["matches"] = document_info.matches
            results.append(document_dict)
        return jsonify(results = results, total = len(results))

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