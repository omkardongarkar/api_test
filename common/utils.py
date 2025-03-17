from bson import ObjectId

def serialize_mongo_document(doc):
    """ Recursively convert ObjectId fields to string in a MongoDB document """
    if isinstance(doc, list):
        return [serialize_mongo_document(d) for d in doc]
    elif isinstance(doc, dict):
        return {k: serialize_mongo_document(v) for k, v in doc.items()}
    elif isinstance(doc, ObjectId):
        return str(doc)
    return doc
