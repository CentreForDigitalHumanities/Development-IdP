from typing import Dict

from djangosaml2idp.models import ServiceProvider
from djangosaml2idp.processors import BaseProcessor, NameIdBuilder


class CNameIdBuilder(NameIdBuilder):
    @classmethod
    def get_nameid_transient(cls, **kwargs) -> str:
        """ This would return EPPN, now just hacked to return a persistnant.
        It's not spec, but it works
        """
        raise cls.get_nameid_persistent(**kwargs)


class SamlProcessor(BaseProcessor):
    def create_identity(self, user, sp_attribute_mapping: Dict[str, str]) -> Dict[str, str]:
        """ Generate an identity dictionary of the user based on the
            given mapping of desired user attributes by the SP
        """
        results = {}
        for user_attr, out_attr in sp_attribute_mapping.items():
            if hasattr(user, user_attr):
                attr = getattr(user, user_attr)
                results[out_attr] = attr() if callable(attr) else attr
        return results
