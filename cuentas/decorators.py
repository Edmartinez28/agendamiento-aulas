from django.core.exceptions import PermissionDenied

def rol_required(roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if request.user.rol not in roles:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator