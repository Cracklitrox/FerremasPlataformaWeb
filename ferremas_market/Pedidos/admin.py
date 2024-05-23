from django.contrib import admin
from .models import *
from Usuario.models import Cliente

# Register your models here.

class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'precio', 'stock', 'get_categoria_nombre')
    list_editable = ('precio', 'stock')
    search_fields = ('nombre',)
    list_filter = ('precio', 'stock', 'categoria__nombre')
    fields = ('nombre', 'descripcion', 'precio', 'stock', 'categoria', 'foto')

    def get_categoria_nombre(self, obj):
        return obj.categoria.nombre if obj.categoria else 'No asignada'
    get_categoria_nombre.short_description = 'Categoría'

class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'activo')
    search_fields = ('nombre', 'activo')

class CompraAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha_compra', 'total')
    list_filter = ('fecha_compra', 'usuario')

class DetalleCompraAdmin(admin.ModelAdmin):
    list_display = ('compra', 'producto', 'cantidad', 'precio')
    list_filter = ('compra', 'producto')

admin.site.register(Categoria, CategoriaAdmin)
admin.site.register(Producto, ProductoAdmin)
admin.site.register(Pedido)
admin.site.register(Compra, CompraAdmin)
admin.site.register(DetalleCompra, DetalleCompraAdmin)