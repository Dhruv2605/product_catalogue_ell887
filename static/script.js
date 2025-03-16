document.getElementById("productForm").addEventListener("submit", function(event) {
    event.preventDefault();

    const name = document.getElementById("name").value;
    const category = document.getElementById("category").value;
    const price = document.getElementById("price").value;
    const productID = Date.now().toString();  

    fetch("/add", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ 
            id: productID,       
            productID: productID, 
            name, 
            category, 
            price 
        })
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

        products.forEach((product, index) => {
            const li = document.createElement("li");
            li.textContent = `${index + 1}. ${product.name} - ${product.category} - ₹${product.price}`;
            li.classList.add("list-group-item"); 
            productList.appendChild(li);
        });
    })
    .catch(error => console.error("Error fetching products:", error));
}
function clearProducts() {
    fetch("/clear", { 
        method: "DELETE",
        credentials: "include"  
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Failed to clear products, possibly not logged in");
        }
        return response.json();
    })
    .then(data => {
        alert(data.message); 
        fetchProducts(); 
    })
    .catch(error => console.error("❌ Error clearing products:", error));
}



