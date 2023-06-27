"""File to transform a CSV of users into fixtures loadable by Django"""
import csv
import json
from typing import Dict

ENTITLEMENT_MAPPINGS = {
    "urn:mace:terena.org:tcs:personal-user-example": 1,
    "urn:x-surfnet:surf.nl:surfdrive-example:quota:50": 2,
    "urn:mace:surf.nl:value:edulicense": 3,
    "urn:mace:dir:entitlement:common-lib-terms-example": 4,
    "urn:mace:incommon.org:reg:education-example": 5,
}

AFFILIATION_MAPPINGS = {
    "student": 1,
    "staff": 2,
    "employee": 3,
    "faculty": 4,
    "member": 5,
}

GROUP_MAPPINGS = {
    'urn:collab:org:co-example.org': 1,
    'urn:collab:org:exchange-university.org': 2,
    'urn:collab:org:home-university.org': 3,
    'urn:collab:org:sunet-example.se': 4,
    'urn:collab:org:surf.nl': 5,
}


def _split_line(string: str):
    return string.split(', ')


def _mapper(data: str, mappings: Dict[str, int]):
    new_data = []
    splitted = _split_line(data)
    for item in splitted:
        result = mappings.get(item.strip(), None)
        if result:
            new_data.append(result)

    return new_data


with open('convertcsv.csv', mode='r') as f:
    csv_reader = csv.DictReader(f)

    user_id_num = 2
    email_id_num = 2

    user_fixtures = []
    email_fixtures = []

    datum: dict  # Makes the linter happy
    for datum in csv_reader:
        datum['is_staff'] = False
        datum['is_active'] = True
        datum['is_superuser'] = False
        datum['user_permissions'] = []
        datum['last_login'] = None
        datum['date_joined'] = "2023-05-02T08:27:53.470Z"

        datum['password'] = f"plain${datum['password']}"

        datum['_eduPersonEntitlement'] = _mapper(
            datum['eduPersonEntitlement'],
            ENTITLEMENT_MAPPINGS
        )
        del datum['eduPersonEntitlement']
        datum['_eduPersonAffiliation'] = _mapper(
            datum['eduPersonAffiliation'],
            AFFILIATION_MAPPINGS
        )
        del datum['eduPersonAffiliation']
        datum['_isMemberOf'] = _mapper(
            datum['isMemberOf'],
            GROUP_MAPPINGS
        )
        del datum['isMemberOf']

        # Not used in dev IdP
        del datum['eduPersonScopedAffiliation']

        for email in _split_line(datum['mail']):
            email_fixture_data = {
                'pk': email_id_num,
                'model': 'main.usermail',
                'fields': {
                    'email': email,
                    'user': user_id_num
                }
            }
            email_id_num += 1
            email_fixtures.append(email_fixture_data)

        del datum['mail']

        user_fixture_data = {
            'pk': user_id_num,
            'model': 'main.user',
            'fields': datum
        }
        user_fixtures.append(user_fixture_data)

        user_id_num += 1

    with open('surfconext-test-users.json', mode='w') as output_file:
        json.dump(user_fixtures + email_fixtures, output_file, indent=2)
