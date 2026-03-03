from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied

User = get_user_model()

class MyOIDCBackend(OIDCAuthenticationBackend):
    def create_user(self, claims):
        user = super().create_user(claims)
        # Aquí sí asignas rol por dominio
        return self.update_user(user, claims, set_role=True)

    def update_user(self, user, claims, set_role=False):
        email = (claims.get("email") or claims.get("preferred_username") or claims.get("upn"))
        if not email:
            raise PermissionDenied("No se pudo obtener el email del proveedor OIDC")
        email = email.strip().lower()

        # siempre actualiza datos básicos
        user.external_id = claims.get("sub")
        user.email = email
        user.first_name = claims.get("given_name") or ""
        user.last_name = claims.get("family_name") or ""

        # ✅ Solo setea rol si es nuevo (set_role=True)
        if set_role:
            if email.endswith("@ucacue.edu.ec"):
                role_code = User.DOCENTE
            elif email.endswith("@est.ucacue.edu.ec") or email.endswith("@est.ucacue.edu"):
                role_code = User.ESTUDIANTE
            else:
                raise PermissionDenied("Dominio no autorizado")

            user.rol = role_code
            group, _ = Group.objects.get_or_create(name=role_code)
            user.groups.set([group])

        user.save()
        return user