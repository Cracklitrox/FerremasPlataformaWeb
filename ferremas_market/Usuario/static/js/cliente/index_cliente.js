document.getElementById("cart-icon").addEventListener("click", function() {
    document.getElementById("sidebar").style.width = "250px";
    document.getElementById("overlay").style.display = "block";
    checkCartItems();
});

document.getElementById("close-btn").addEventListener("click", function() {
    closeSidebar();
});

document.getElementById("overlay").addEventListener("click", function() {
    closeSidebar();
});

document.getElementById("buy-btn").addEventListener("click", function() {
    alert("Compra realizada");
    closeSidebar();
});

function closeSidebar() {
    document.getElementById("sidebar").style.width = "0";
    document.getElementById("overlay").style.display = "none";
}

function checkCartItems() {
    const cartItems = document.getElementById("cart-items");
    const emptyMessage = document.getElementById("empty-message");

    if (cartItems.children.length === 0) {
        emptyMessage.style.display = "block";
    } else {
        emptyMessage.style.display = "none";
    }
}

// Cierra el sidebar si se hace clic fuera del mismo
window.addEventListener('click', function(event) {
    const sidebar = document.getElementById('sidebar');
    if (event.target !== sidebar && !sidebar.contains(event.target) && event.target !== document.getElementById('cart-icon')) {
        closeSidebar();
    }
});