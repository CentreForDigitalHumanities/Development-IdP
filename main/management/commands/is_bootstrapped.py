from django.contrib.auth.models import Group
from django.core.management import BaseCommand

from main.models import Affiliation, Entitlement


class Command(BaseCommand):
    help = "Returns if we have at least initial data loaded"

    def handle(self, *args, **options):
        is_bootstrapped = True
        if Entitlement.objects.count() == 0:
            is_bootstrapped = False
        elif Affiliation.objects.count() == 0:
            is_bootstrapped = False
        elif Group.objects.count() == 0:
            is_bootstrapped = False

        print(is_bootstrapped)
