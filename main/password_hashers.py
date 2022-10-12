from django.contrib.auth.hashers import BasePasswordHasher
from django.utils.translation import gettext_lazy as _


class PlainPasswordHasher(BasePasswordHasher):
    "A hasher that doesn't actually hash"

    algorithm = "plain"
    iterations = 0

    def verify(self, password, encoded):
        return f"plain${password}" == encoded

    def encode(self, password, salt):
        return f"plain${password}"

    def safe_summary(self, encoded):
        try:
            hash = encoded.split('$')[1]
        except:
            hash = encoded

        return {
            _("algorithm"): self.algorithm,
            _("iterations"): self.iterations,
            _("salt"): "None!",
            _("hash"): hash,
        }
