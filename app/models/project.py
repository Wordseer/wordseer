class Project(db.Model, Base):
    """A WordSeer project for a collection of documents.
    """

    # Attributes
    name = db.Column(db.String)
    path = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    # Relationships
    documents = db.relationship("Document", secondary="documents_in_projects",
            backref="projects")
