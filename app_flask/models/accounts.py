from datetime import datetime

import pytz

from . import *
from .__mixins__ import UtilityMixin


class Accounts(db.Model, UtilityMixin):
    # PriKey
    account_id = db.Column(db.Integer, primary_key=True)

    email_address = db.Column(db.String(255), nullable=False)
    settings = db.Column(db.JSON, default={"theme": "dark"})
    auth_code = db.Column(db.String(512), nullable=True)
    auth_code_expiry = db.Column(db.DateTime, nullable=True)

    def update_auth_code(self, auth_code: str, auth_code_expiry: datetime):
        self.auth_code = auth_code
        self.auth_code_expiry = auth_code_expiry
        db.session.commit()

    def remove_auth_code(self):
        self.auth_code = None
        self.auth_code_expiry = None
        db.session.commit()

    @classmethod
    def get_account(cls, email_address: str):
        q = select(cls).where(cls.email_address == email_address)
        return db.session.execute(q).scalar_one_or_none()

    @classmethod
    def get_email_address(cls, account_id: int):
        q = select(cls.email_address).where(cls.account_id == account_id)
        return db.session.execute(q).scalar_one_or_none()

    @classmethod
    def process_auth_code(cls, account_id: int, auth_code: str):
        q = select(cls).where(
            cls.account_id == account_id,
            and_(cls.auth_code == auth_code),
        )
        r = db.session.execute(q).scalar_one_or_none()

        if not r:
            return None

        if isinstance(r.auth_code_expiry, datetime):
            if DatetimeDelta().datetime < pytz.UTC.localize(r.auth_code_expiry):
                return r

        return None
