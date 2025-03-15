document.getElementById("productForm").addEventListener("submit", function(event) {
    event.preventDefault();

    const name = document.getElementById("name").value;
    const category = document.getElementById("category").value;
    const price = document.getElementById("price").value;

    fetch("/add", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ id: Date.now().toString(), name, category, price })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        fetchProducts();
    })
    .catch(error => console.error("Error adding product:", error));
});

function fetchProducts() {
    fetch("/products")
    .then(response => response.json())
    .then(products => {
        const productList = document.getElementById("productList");
        productList.innerHTML = "";
        products.forEach(product => {
            const li = document.createElement("li");
            li.textContent = `${product.name} - ${product.category} - ₹${product.price}`;
            productList.appendChild(li);
        });
    })
    .catch(error => console.error("Error fetching products:", error));
}
