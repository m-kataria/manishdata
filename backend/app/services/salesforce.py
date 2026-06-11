"""Salesforce client using simple_salesforce.

Auth via username + password + security token (the classic SOAP login flow that simple_salesforce
wraps). For production tenants you may want to switch to OAuth 2.0 JWT bearer flow; the public
surface here is stable across either choice.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class SalesforceError(RuntimeError):
    pass


class SalesforceClient:
    def __init__(
        self,
        username: str,
        password: str,
        security_token: str,
        domain: str = "login",
    ) -> None:
        self.username = username
        self.password = password
        self.security_token = security_token
        self.domain = domain
        self._sf = None

    def _credentials_present(self) -> bool:
        return all([self.username, self.password, self.security_token])

    def _connect(self):
        if self._sf is not None:
            return self._sf
        if not self._credentials_present():
            raise SalesforceError("Salesforce credentials not configured")

        from simple_salesforce import Salesforce

        self._sf = Salesforce(
            username=self.username,
            password=self.password,
            security_token=self.security_token,
            domain=self.domain,
        )
        return self._sf

    # --- public API ----------------------------------------------------------

    def ping(self) -> dict[str, Any]:
        if not self._credentials_present():
            return {
                "connected": False,
                "reason": "credentials_missing",
                "message": "Set SF_USERNAME, SF_PASSWORD, SF_SECURITY_TOKEN in .env",
            }
        try:
            sf = self._connect()
            user_info = sf.UserInfo if hasattr(sf, "UserInfo") else {}
        except Exception as e:
            return {"connected": False, "reason": "auth_failed", "message": str(e)}

        return {
            "connected": True,
            "username": self.username,
            "domain": self.domain,
            "instance": getattr(self._sf, "sf_instance", None),
            "userInfo": user_info,
        }

    def get_accounts(self, limit: int = 100) -> list[dict[str, Any]]:
        sf = self._connect()
        result = sf.query(
            f"SELECT Id, Name, Industry, BillingCity, Phone FROM Account LIMIT {int(limit)}"
        )
        return result.get("records", [])

    def get_opportunities(self, limit: int = 100) -> list[dict[str, Any]]:
        sf = self._connect()
        result = sf.query(
            f"SELECT Id, Name, AccountId, StageName, Amount, CloseDate FROM Opportunity "
            f"ORDER BY LastModifiedDate DESC LIMIT {int(limit)}"
        )
        return result.get("records", [])

    def get_contacts(self, limit: int = 100) -> list[dict[str, Any]]:
        sf = self._connect()
        result = sf.query(
            f"SELECT Id, FirstName, LastName, Email, Phone, AccountId FROM Contact "
            f"LIMIT {int(limit)}"
        )
        return result.get("records", [])

    def create_lead(self, payload: dict[str, Any]) -> dict[str, Any]:
        required = {"LastName", "Company"}
        missing = required - set(payload.keys())
        if missing:
            raise SalesforceError(f"Missing required Lead fields: {sorted(missing)}")

        sf = self._connect()
        return sf.Lead.create(payload)


def build_client_from_config(config) -> SalesforceClient:
    return SalesforceClient(
        username=config["SF_USERNAME"],
        password=config["SF_PASSWORD"],
        security_token=config["SF_SECURITY_TOKEN"],
        domain=config["SF_DOMAIN"],
    )
