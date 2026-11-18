from bson import ObjectId


def serializar_documento(documento):
    if documento:
        for campo in ("_id", "usuario_id", "evento_id"):
            if campo in documento and isinstance(documento[campo], ObjectId):
                documento[campo] = str(documento[campo])
    return documento


def serializar_lista(documentos):
    return [serializar_documento(documento) for documento in documentos]
