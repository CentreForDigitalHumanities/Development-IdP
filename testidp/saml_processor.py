from typing import Dict

from djangosaml2idp.models import ServiceProvider
from djangosaml2idp.processors import BaseProcessor, NameIdBuilder


class CNameIdBuilder(NameIdBuilder):
    @classmethod
    def get_nameid_transient(cls, *args, **kwargs) -> str:
        """ This would return EPPN, now just hacked to return a persistnant.
        It's not spec, but it works
        """
        return cls.get_nameid_persistent(*args, **kwargs)


class SamlProcessor(BaseProcessor):

    def get_user_id(self, user, name_id_format: str, service_provider: ServiceProvider, idp_config) -> str:
        """ Get identifier for a user.
        """
        user_field_str = service_provider.nameid_field
        user_field = getattr(user, user_field_str)

        if callable(user_field):
            user_id = str(user_field())
        else:
            user_id = str(user_field)

        # returns in a real name_id format
        return CNameIdBuilder.get_nameid(user_id, name_id_format, sp=service_provider, user=user)

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
