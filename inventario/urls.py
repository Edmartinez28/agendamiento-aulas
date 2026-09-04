from django.urls import path
from .views import *

app_name = "inventario"
urlpatterns = [
    path("", inventariototal , name="inventariototal"),
    path("lab/<int:lab_id>/", inventario_por_laboratorio, name="inventario_por_laboratorio"),
    path("exportar/excel/", exportar_inventario_excel, name="exportar_inventario_excel"),
    path("item/nuevo/", nuevoinventario, name="nuevoinventario"),
    path("item/<int:item_id>/", actualizarinventario, name="actualizarinventario"),
]