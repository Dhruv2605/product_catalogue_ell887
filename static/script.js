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
        body: JSON.stringify({ productID: Date.now().toString(), name, category, price })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        fetchProducts(); // Refresh the product list after adding
    })
    .catch(error => console.error("Error adding product:", error));
});

function fetchProducts() {
    fetch("/products")
    .then(response => response.json())
    .then(products => {
        const productList = document.getElementById("productList");
        productList.innerHTML = ""; // Clear existing list

        products.forEach((product, index) => {
            const li = document.createElement("li");
            li.textContent = `${index + 1}. ${product.name} - ${product.category} - ₹${product.price}`;
            li.classList.add("list-group-item"); // Add Bootstrap styling if needed
            productList.appendChild(li);
        });
    })
    .catch(error => console.error("Error fetching products:", error));
}
function clearProducts() {
    if (confirm("Are you sure you want to delete all products?")) {
        fetch("/clear", { method: "DELETE" })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            fetchProducts(); // Refresh the product list
        })
        .catch(error => console.error("Error clearing products:", error));
    }
}

