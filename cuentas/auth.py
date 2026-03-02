from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied

User = get_user_model()

class MyOIDCBackend(OIDCAuthenticationBackend):
    def create_user(self, claims):
        print("Claims:",claims)
        user = super().create_user(claims)
        return self.update_user(user, claims)

    def update_user(self, user, claims):
        print("Claims:",claims)
        email = (
            claims.get("email")
            or claims.get("preferred_username")
            or claims.get("upn")
        )

        if not email or not email.lower().endswith("@ucacue.edu.ec"):
            raise PermissionDenied("Dominio no autorizado")

        user.external_id = claims.get("sub")
        user.email = email
        user.first_name = claims.get("given_name", "") or ""
        user.last_name = claims.get("family_name", "") or ""

        ROLE_MAP = {
            "Administrador": "ADMIN",
            "Docente": "DOCENTE",
            "Estudiante": "ESTUDIANTE",
            "Tecnico": "TECNICO",
        }

        # Azure suele enviar roles como lista en "roles"
        roles = claims.get("roles") or []
        erp_role = None
        if isinstance(roles, list) and roles:
            erp_role = roles[0]
        else:
            erp_role = claims.get("role")

        role_code = ROLE_MAP.get(erp_role)
        if role_code:
            user.rol = role_code
            group, _ = Group.objects.get_or_create(name=role_code)
            user.groups.set([group])

        user.save()
        return user