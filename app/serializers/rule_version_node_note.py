from app.serializers.base import BaseSerializer


class RuleVersionNodeNoteSerializer(BaseSerializer):
    """
    rule version node note serializer
    """

    authorUserId = 0
    authorUserName = 0
    dateCreated = None
    notes = None

    def __init__(self, rule_version_node_note):
        self.authorUserId = rule_version_node_note.user.id
        self.authorUserName = rule_version_node_note.user.name
        self.dateCreated = rule_version_node_note.date_created
        self.notes = rule_version_node_note.notes
