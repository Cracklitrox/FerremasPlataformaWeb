from django.contrib import admin
from .models import *

# Register your models here.

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock')
    list_editable = ('precio', 'stock')
    search_fields = ('nombre',)
    list_filter = ('precio', 'stock')
    fields = ('nombre', 'precio', 'stock', 'foto')

class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'activo')
    search_fields = ('nombre', 'activo')

admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(ProductoCarrito)
admin.site.register(Carrito)
admin.site.register(Pedido)