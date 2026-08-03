from bson import ObjectId
from datetime import datetime


def dfsiteration(doc):

    stack = [(None, None, doc)]  # (parent_container, key_or_index, node) this is the last element 

    while stack:
        parent, key, node = stack.pop()

        if isinstance(node, dict):
            for k, v in node.items():
                stack.append((node, k, v))

        elif isinstance(node, list):
            for i, v in enumerate(node):
                stack.append((node, i, v))

        elif isinstance(node, (ObjectId, datetime)):  ## this is for the if the node is ObjectId tuype and dtaetime type
            parent[key] = str(node)

    return doc