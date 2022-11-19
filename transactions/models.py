from django.db import models

# SQLAlchemy version
#class Classification(db.Model):
#    __tablename__ = "classifications"
#    id = db.Column(db.Integer, primary_key=True)
#    name = db.Column(db.String(128))
#    classify_as = db.Column(db.String(128))
#    always_report = db.Column(db.Boolean)
#    regexes = relationship("Regex")
#    transactions = relationship("Transaction")
#
#    def __init__(self, name, classify_as=None, always_report=None):
#        self.name = name
#        self.classify_as = classify_as
#        self.always_report = always_report

class Classification(models.Model):
    name   = models.CharField(max_length=200)
    classify_as   = models.CharField(max_length=200)
    always_report = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.name}'

class ClassificationRegex(models.Model):
    regex   = models.CharField(max_length=200)
    classification = models.ForeignKey(Classification, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.regex}'

class Transaction(models.Model):
    description   = models.CharField(max_length=200)
    other_party   = models.CharField(max_length=200)
    reference     = models.CharField(max_length=200)
    particulars   = models.CharField(max_length=200)
    analysis_code = models.CharField(max_length=200)
    trans_date    = models.DateTimeField('Transaction Date')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    classifications = models.ManyToManyField(Classification)

    def __str__(self):
        return f'{self.amount} {self.other_party} {self.trans_date}'


# as described in sqlalchemy
#class Transaction(db.Model):
#    __tablename__ = "transactions"
#    id = db.Column(db.Integer, primary_key=True)
#    trans_date = db.Column(db.Date)
#    amount = db.Column(db.Numeric(precision=12, scale=2, asdecimal=False, decimal_return_scale=None))
##    other_party = db.Column(db.String(64))
##    description = db.Column(db.String(64))
##    reference = db.Column(db.String(64))
##    particulars = db.Column(db.String(64))
##    analysis_code = db.Column(db.String(64))
#
#    # Each transaction may have one classification
#    classification_id = db.Column(db.Integer, db.ForeignKey('classifications.id'))
#    classification = relationship('Classification', back_populates='transactions')
#
#    def __init__(self, trans_date, amount, other_party, description, reference, particulars, analysis_code):
#        self.trans_date = trans_date
#        self.amount = float(amount)
#        self.other_party = other_party
#        self.description = description
#        self.reference = reference
#        self.particulars = particulars
#        self.analysis_code = analysis_code
#
#    def __repr__(self):
#        return f'{self.amount} {self.other_party} {self.trans_date}'
#
