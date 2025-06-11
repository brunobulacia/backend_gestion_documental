from .models import BitacoraUsuario
from django.utils.timezone import now

class BitacoraMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated:
            ip = request.META.get('REMOTE_ADDR')
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            metodo = request.method
            path = request.path

            if metodo != 'GET':  
                accion = f"{metodo} en {path}"

                BitacoraUsuario.objects.create(
                    usuario=request.user,
                    ip=ip,
                    accion=accion,
                    metodo=metodo,
                    endpoint=path,
                    user_agent=user_agent,
                    fecha=now()
                )

        return response
