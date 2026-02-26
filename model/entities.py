import os

from pynamodb.attributes import (
    DiscriminatorAttribute,
    NumberAttribute,
    UnicodeAttribute,
)
from pynamodb.models import Model


class Entities(Model):
    class Meta:
        table_name = os.environ['ENTITIES_TABLE']
        region = os.environ['REGION']
        billing_mode = 'PAY_PER_REQUEST'

    cls = DiscriminatorAttribute()

    hashKey = UnicodeAttribute(hash_key=True)
    rangeKey = UnicodeAttribute(range_key=True)

    latestVersion = NumberAttribute(null=False)
    entryStatus = UnicodeAttribute(null=False)
    entryId = UnicodeAttribute(null=False)

    createDate = UnicodeAttribute(null=False)
    updateDate = UnicodeAttribute(null=False)
    createdBy = UnicodeAttribute(null=True)
    updatedBy = UnicodeAttribute(null=True)
