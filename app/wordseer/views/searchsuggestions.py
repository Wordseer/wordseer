"""????
"""

from flask import request
from sqlalchemy import _not
from sqlalchemy import func
from sqlalchemy.sql.expression import literal_column

from .. import wordseer
from ..models import PropertyMetadata
from ..models import WorkingSet
from ...uploader.models import Property
from app import db

def return_autosuggestions():
    query = request.args.get("query")
    timing = request.args.get("timing")
    user = request.args.get("user")

    suggestions = []

    search_text_filter = True
    value_filter = True

    if search_text:
        workingset_name_filter = WorkingSet.name.like("%" + query + "%")
        property_value_filter = Property.value.like("%" + query + "%")

    #TODO: Mystery clause
    #TODO: document_count
    sets = db.session.query(WorkingSet.id,
        Property.name.label("text"),
        literal_column("'phrase-set'").label("class")
        func.count(Property.unit_id.distinct()).label("unit_count")).\
            filter(Property.unit_name == "sentence").\
            filter(Property.value == WorkingSet.id).\
            filter(WorkingSet.username == user).\
            filter(Property.name == "phrase_set").\
            filter(workingset_name_filter).\
            group_by(WorkingSet.name).\
            all()

    suggestions.extend([set._asdict() for set in sets])

    #TODO: document_count, sentence_count
    metadata = db.session.query(PropertyMetadata.display_name,
        Property.name,
        Property.value,
        literal_column("'metadata'").label("class"),
        func.count(Property.unit_id.idstinct()).label("unit_count")).\
            filter(property_value_filter).\
            filter(Property.name == PropertyMetadata.property_name).\
            filter(PropertyMetadata.is_category == True).\
            filter(not_(Metadata.name.like("%_set"))).\
            group_by(Property.value).\
            limit(50).\
            all()

    for metadatum in metadata:
        property_name = metadata.name
        if metadatum.display_name:
            property_name = metadatum.display_name

        suggestion = metadatum._asdict()
        suggestion["text"] = {property_name.lower(): metadatum.value}
        suggestions.append(suggestion)


    sequences = []

