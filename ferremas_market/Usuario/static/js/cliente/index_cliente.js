document.addEventListener('DOMContentLoaded', function() {
    const cart = JSON.parse(localStorage.getItem('cart')) || [];

    const usuarioIdElement = document.getElementById('user-id');
    const usuarioId = usuarioIdElement ? usuarioIdElement.value : null;
    const cancelButton = document.getElementById('cancel-button');
    console.log("Usuario ID obtenido:", usuarioId);

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');

    function addToCart(productId, productName, productImage, productStock, productPrice) {
        const productIndex = cart.findIndex(item => item.id === productId);
        if (productIndex > -1) {
            if (cart[productIndex].quantity < cart[productIndex].stock) {
                cart[productIndex].quantity += 1;
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Stock limitado',
                    text: 'No puedes agregar más de este producto',
                    timer: 2000,
                    showConfirmButton: false
                });
                return;
            }
        } else {
            cart.push({ id: productId, name: productName, image: productImage, quantity: 1, stock: productStock, price: productPrice });
        }
        guardarCarrito();
        Swal.fire({
            icon: 'success',
            title: 'Producto agregado',
            text: `${productName} ha sido agregado al carrito`,
            timer: 1500,
            showConfirmButton: false
        });
        updateCartUI();
    }

    function guardarCarrito() {
        localStorage.setItem('cart', JSON.stringify(cart));
    }

    function updateCartUI() {
        const cartItemsContainer = document.getElementById('cart-items');
        const emptyMessage = document.getElementById('empty-message');
        const clearCartBtn = document.getElementById('clear-cart-btn');
        const totalAmountContainer = document.getElementById('total-amount');

        cartItemsContainer.innerHTML = '';
        let totalAmount = 0;
        cart.forEach(item => {
            const itemTotal = item.quantity * item.price;
            totalAmount += itemTotal;
            const productElement = document.createElement('li');
            productElement.classList.add('cart-item');
            productElement.innerHTML = `
                <img src="${item.image}" alt="${item.name}" class="cart-item-image">
                <span class="cart-item-name">${item.name}</span>
                <span class="cart-item-quantity">
                    <button class="decrease-quantity" data-id="${item.id}">-</button>
                    <span>${item.quantity}</span>
                    <button class="increase-quantity" data-id="${item.id}">+</button>
                </span>
                <span class="cart-item-price">${formatPrice(itemTotal)}</span>
                <button class="remove-item" data-id="${item.id}"><i class="fa fa-trash"></i></button>
            `;
            cartItemsContainer.appendChild(productElement);
        });

        totalAmountContainer.textContent = `Total: ${formatPrice(totalAmount)}`;

        if (cart.length === 0) {
            emptyMessage.style.display = 'block';
            clearCartBtn.style.display = 'none';
        } else {
            emptyMessage.style.display = 'none';
            clearCartBtn.style.display = 'block';
        }

        document.querySelectorAll('.decrease-quantity').forEach(button => {
            button.addEventListener('click', function() {
                const productId = this.getAttribute('data-id');
                decreaseQuantity(productId);
            });
        });

        document.querySelectorAll('.increase-quantity').forEach(button => {
            button.addEventListener('click', function() {
                const productId = this.getAttribute('data-id');
                increaseQuantity(productId);
            });
        });

        document.querySelectorAll('.remove-item').forEach(button => {
            button.addEventListener('click', function() {
                const productId = this.getAttribute('data-id');
                removeFromCart(productId);
            });
        });
    }

    function limpiarCarrito() {
        localStorage.removeItem('cart');
        cart.length = 0;
        updateCartUI();
    }

    function formatPrice(price) {
        return price.toLocaleString('es-CL', { style: 'currency', currency: 'CLP' });
    }

    function decreaseQuantity(productId) {
        const productIndex = cart.findIndex(item => item.id === productId);
        if (productIndex > -1) {
            if (cart[productIndex].quantity > 1) {
                cart[productIndex].quantity -= 1;
            } else {
                cart.splice(productIndex, 1);
            }
            guardarCarrito();
            updateCartUI();
        }
    }

    function increaseQuantity(productId) {
        const productIndex = cart.findIndex(item => item.id === productId);
        if (productIndex > -1) {
            if (cart[productIndex].quantity < cart[productIndex].stock) {
                cart[productIndex].quantity += 1;
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Stock limitado',
                    text: 'No puedes agregar más de este producto',
                    timer: 2000,
                    showConfirmButton: false
                });
                return;
            }
            guardarCarrito();
            updateCartUI();
        }
    }

    function removeFromCart(productId) {
        const productIndex = cart.findIndex(item => item.id === productId);
        if (productIndex > -1) {
            cart.splice(productIndex, 1);
            guardarCarrito();
            Swal.fire({
                icon: 'success',
                title: 'Producto eliminado',
                text: 'El producto ha sido eliminado del carrito',
                timer: 1500,
                showConfirmButton: false
            });
            updateCartUI();
        }
    }

    function clearCart() {
        cart.length = 0;
        guardarCarrito();
        updateCartUI();
        limpiarCarrito();
    }

    function actualizarStock(productData = null) {
        if (!usuarioId) {
            Swal.fire({
                icon: 'error',
                title: 'Inicia sesión',
                text: 'Debes iniciar sesión para comprar.',
                timer: 2000,
                showConfirmButton: false
            });
            return;
        }
    
        let productsToBuy = productData ? [productData] : cart;
    
        if (!productData && productsToBuy.length === 0) {
            Swal.fire({
                icon: 'error',
                title: 'Carrito vacío',
                text: 'No hay productos en el carrito para comprar.',
                timer: 2000,
                showConfirmButton: false
            });
            return;
        }
    
        console.log("Productos a comprar:", productsToBuy);
    
        const requestData = {
            usuario_id: usuarioId,
            items: productsToBuy
        };
    
        console.log("Enviando datos al servidor:", requestData);
    
        fetch('/Pedidos/api/update-stock/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log("Respuesta del servidor:", data);
            if (data.success) {
                window.location.href = data.redirect_url;
                limpiarCarrito();
            } else {
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: data.error || 'Hubo un problema al actualizar el stock',
                    timer: 2000,
                    showConfirmButton: false
                });
            }
        })
        .catch(error => {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Hubo un problema con la solicitud',
                timer: 2000,
                showConfirmButton: false
            });
            console.error('Error:', error);
        });
    }

    if (cancelButton) {
        cancelButton.addEventListener('click', function() {
            const token = new URLSearchParams(window.location.search).get('TBK_TOKEN');
            if (token) {
                fetch(`/Pedidos/api/anular-compra/?token_ws=${token}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            alert(data.message);
                            window.location.href = '/Usuario/';
                        } else {
                            alert('Error al anular la compra: ' + data.message);
                        }
                    })
                    .catch(error => console.error('Error:', error));
            } else {
                window.location.href = '/Usuario/';
            }
        });
    }

    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', function() {
            const isLoggedIn = this.getAttribute('data-logged-in') === 'True';
            if (!isLoggedIn) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Inicie sesión',
                    text: 'Por favor, inicie sesión para agregar productos al carrito.',
                    timer: 2000,
                    showConfirmButton: false
                });
                return;
            }
            const productId = this.getAttribute('data-id');
            const productName = this.getAttribute('data-name');
            const productImage = this.getAttribute('data-image');
            const productStock = parseInt(this.getAttribute('data-stock'));
            const productPrice = parseFloat(this.getAttribute('data-price'));
            addToCart(productId, productName, productImage, productStock, productPrice);
        });
    });

    document.querySelectorAll('.buy-now').forEach(button => {
        button.addEventListener('click', function() {
            const isLoggedIn = this.getAttribute('data-logged-in') === 'True';
            if (!isLoggedIn) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Inicie sesión',
                    text: 'Por favor, inicie sesión para comprar.',
                    timer: 2000,
                    showConfirmButton: false
                });
                return;
            }
            const productId = this.getAttribute('data-id');
            const productName = this.getAttribute('data-name');
            const productImage = this.getAttribute('data-image');
            const productStock = parseInt(this.getAttribute('data-stock'));
            const productPrice = parseFloat(this.getAttribute('data-price'));
            const productData = {
                id: productId,
                name: productName,
                image: productImage,
                quantity: 1,
                stock: productStock,
                price: productPrice
            };
            actualizarStock(productData);
        });
    });

    document.getElementById('clear-cart-btn').addEventListener('click', function() {
        clearCart();
    });

    document.getElementById('buy-btn').addEventListener('click', function() {
        if (cart.length === 0) {
            Swal.fire({
                icon: 'error',
                title: 'Carrito vacío',
                text: 'No hay productos en el carrito para comprar.',
                timer: 2000,
                showConfirmButton: false
            });
            return;
        }
        actualizarStock();
    });

    updateCartUI();

    document.getElementById("cart-icon").addEventListener("click", function() {
        document.getElementById("sidebar").style.width = "30%";
        document.getElementById("sidebar").style.maxWidth = "40%";
        document.getElementById("sidebar").style.overflow = "auto";
        updateCartUI();
    });

    document.getElementById("recibo-icon").addEventListener("click", function() {
        window.location.href = '/Usuario/cliente/historial-compras/';
    });

    document.getElementById("close-btn").addEventListener("click", function() {
        closeSidebar();
    });

    function closeSidebar() {
        document.getElementById("sidebar").style.width = "0";
    }

    window.addEventListener('click', function(event) {
        const sidebar = document.getElementById('sidebar');
        if (event.target !== sidebar && !sidebar.contains(event.target) && event.target !== document.getElementById('cart-icon')) {
            closeSidebar();
        }
    });
});