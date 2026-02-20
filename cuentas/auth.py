from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

class MyOIDCBackend(OIDCAuthenticationBackend):

    def create_user(self, claims):
        user = super().create_user(claims)
        return self.update_user(user, claims)

    def update_user(self, user, claims):

        user.email = claims.get("email")
        user.first_name = claims.get("given_name")
        user.last_name = claims.get("family_name")

        role = claims.get("role")  # 👈 debe venir del ERP
        user.rol = role
        user.save()

        user.groups.clear()

        if role:
            group, _ = Group.objects.get_or_create(name=role)
            user.groups.add(group)

        return user
