from django.contrib import admin
from .models import *

# Register your models here.

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock')
    list_editable = ('precio', 'stock')
    search_fields = ('nombre',)
    list_filter = ('precio', 'stock')
    fields = ('nombre', 'precio', 'stock', 'foto')

admin.site.register(Producto, ProductoAdmin)
admin.site.register(ProductoCarrito)
admin.site.register(Carrito)
admin.site.register(Pedido)