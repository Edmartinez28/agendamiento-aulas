from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied

User = get_user_model()

class MyOIDCBackend(OIDCAuthenticationBackend):

    def create_user(self, claims):
        user = super().create_user(claims)
        return self.update_user(user, claims)

    def update_user(self, user, claims):

        email = claims.get("email")

        # 🔒 Validar dominio institucional
        if not email.endswith("@ucacue.edu.ec"):
            raise PermissionDenied("Dominio no autorizado")
        user.external_id = claims.get("sub")
        user.email = email
        user.first_name = claims.get("given_name", "")
        user.last_name = claims.get("family_name", "")

        # 👇 Mapeo seguro de roles
        erp_role = claims.get("role")

        ROLE_MAP = {
            "Administrador": "ADMIN",
            "Docente": "DOCENTE",
            "Estudiante": "ESTUDIANTE",
            "Tecnico": "TECNICO",
        }

        role_code = ROLE_MAP.get(erp_role)

        if role_code:
            user.rol = role_code

            group, _ = Group.objects.get_or_create(name=role_code)
            user.groups.set([group])

        user.save()
        return user