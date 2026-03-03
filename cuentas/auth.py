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
        email = (
            claims.get("email")
            or claims.get("preferred_username")
            or claims.get("upn")
        )
        if not email:
            raise PermissionDenied("No se pudo obtener el email del proveedor OIDC")

        email = email.strip().lower()

        # ✅ Reglas por dominio
        if email.endswith("@ucacue.edu.ec"):
            role_code = User.DOCENTE
        elif email.endswith("@est.ucacue.edu.ec") or email.endswith("@est.ucacue.edu"):
            role_code = User.ESTUDIANTE
        else:
            raise PermissionDenied("Dominio no autorizado")

        # Campos básicos
        user.external_id = claims.get("sub")
        user.email = email
        # Si tu sistema usa username, puedes fijarlo también (opcional):
        # user.username = email  # o email.split("@")[0]
        user.first_name = claims.get("given_name") or ""
        user.last_name = claims.get("family_name") or ""

        # ✅ Asignación de rol + grupo
        user.rol = role_code
        group, _ = Group.objects.get_or_create(name=role_code)
        user.groups.set([group])

        user.save()
        return user