// --- UTILS ---
function updateCartCount() {
    const badge = document.getElementById('cart-count');
    if (badge) {
        fetch('/api/cart').then(res => res.json()).then(data => {
            badge.innerText = data.items.length;
        });
    }
}

// ==========================================
// 1. STOREFRONT LOGIC (index.html)
// ==========================================
if (document.getElementById('product-grid')) {
    updateCartCount();

    fetch('/api/products')
        .then(res => res.json())
        .then(products => {
            const grid = document.getElementById('product-grid');
            grid.innerHTML = products.map(p => `
                <div class="product-card">
                    <img src="${p.image_url}" alt="${p.name}">
                    <h3>${p.name}</h3>
                    <p style="color: #888; font-size: 0.9rem; margin-bottom: 10px;">${p.description}</p>
                    <div class="price">KES ${p.price.toLocaleString()}</div>
                    <button class="btn" onclick="addToCart(${p.id})">Add to Cart</button>
                </div>
            `).join('');
        });

    async function addToCart(productId) {
        await fetch('/api/cart/add', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({product_id: productId})
        });
        updateCartCount();
        // Simple visual feedback
        const badge = document.getElementById('cart-count');
        badge.style.transform = "scale(1.5)";
        setTimeout(() => badge.style.transform = "scale(1)", 200);
    }
}

// ==========================================
// 2. CART & CHECKOUT LOGIC (cart.html)
// ==========================================
if (document.getElementById('cart-items')) {
    function loadCart() {
        fetch('/api/cart')
            .then(res => res.json())
            .then(data => {
                const container = document.getElementById('cart-items');
                
                if (data.items.length === 0) {
                    container.innerHTML = '<p style="text-align:center; color:#888; padding: 40px;">Your cart is empty.</p>';
                    document.getElementById('cart-total').innerText = "KES 0";
                    document.querySelector('.checkout-btn').style.display = 'none';
                    return;
                }

                document.querySelector('.checkout-btn').style.display = 'block';
                container.innerHTML = data.items.map(item => `
                    <div class="cart-item">
                        <img src="${item.image_url}" alt="${item.name}">
                        <div class="cart-item-info">
                            <h3>${item.name}</h3>
                            <p style="color:#888;">Qty: ${item.quantity} x KES ${item.price.toLocaleString()}</p>
                        </div>
                        <button class="remove-btn" onclick="removeFromCart(${item.id})">Remove</button>
                    </div>
                `).join('');

                document.getElementById('cart-total').innerText = `KES ${data.cart_total.toLocaleString()}`;
            });
    }

    async function removeFromCart(itemId) {
        await fetch(`/api/cart/${itemId}`, { method: 'DELETE' });
        loadCart(); 
    }

    loadCart(); 
}

// --- MODAL LOGIC ---
function openCheckout() {
    document.getElementById('checkout-modal').style.display = 'block';
}

function closeCheckout() {
    document.getElementById('checkout-modal').style.display = 'none';
    document.getElementById('payment-status').innerText = '';
}

async function processPayment() {
    const phone = document.getElementById('phone-input').value;
    const statusDiv = document.getElementById('payment-status');
    const btn = document.getElementById('pay-btn');

    if (!phone) {
        statusDiv.innerText = "Please enter a phone number.";
        statusDiv.style.color = "#ff5252";
        return;
    }

    btn.innerText = "Sending...";
    btn.disabled = true;

    try {
        const res = await fetch('/api/checkout', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({phone_number: phone})
        });

        const data = await res.json();

        if (res.ok) {
            statusDiv.innerText = "✅ " + data.message;
            statusDiv.style.color = "#4caf50";
            btn.innerText = "Check your phone";
        } else {
            statusDiv.innerText = "❌ " + data.detail;
            statusDiv.style.color = "#ff5252";
            btn.innerText = "Try Again";
            btn.disabled = false;
        }
    } catch (error) {
        statusDiv.innerText = "❌ Network error.";
        statusDiv.style.color = "#ff5252";
        btn.innerText = "Try Again";
        btn.disabled = false;
    }
}