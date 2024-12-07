document.addEventListener('DOMContentLoaded', function() {

    // Function to calculate the total amount
    function calculateTotal() {
        let total = 0;
        document.querySelectorAll('.product-row').forEach(function(row) {
            let qty = parseFloat(row.querySelector('input[name$="-quantity"]').value || 0);
            let rate = parseFloat(row.querySelector('input[name$="-rate"]').value || 0);
            let amount = qty * rate;
            row.querySelector('.amount').innerText = amount.toFixed(2);
            total += amount;
        });

        document.getElementById('total-amount').innerText = total.toFixed(2);
    }

    // Function to bind row events for dynamic rows
    function bindRowEvents(row) {
        row.querySelector('.remove-product-row').addEventListener('click', function() {
            if (confirm("Are you sure you want to remove this product?")) {
                row.remove();
                calculateTotal();  // Recalculate total after removing the row
            }
        });
    }

    // Initial binding for existing rows
    document.querySelectorAll('.product-row').forEach(function(row) {
        bindRowEvents(row);
    });

    // Add logic for adding new product rows
    document.getElementById('add-product-row').addEventListener('click', function() {
        let productList = document.getElementById('product-list');
        let firstRow = productList.querySelector('.product-row');
        let newRow = firstRow.cloneNode(true);

        // Reset values in the new row
        newRow.querySelector('input[name$="-quantity"]').value = '';
        newRow.querySelector('input[name$="-rate"]').value = firstRow.querySelector('input[name$="-rate"]').value; // Keep the rate the same
        newRow.querySelector('.amount').innerText = '0.00';

        // Append the new row to the table
        productList.appendChild(newRow);

        // Re-bind the calculateTotal function to the new row's inputs
        bindRowEvents(newRow);
    });

    // Bind the calculateTotal function to the Calculate Total button
    document.getElementById('calculate-total').addEventListener('click', function() {
        calculateTotal();
        alert("Total amount has been calculated!");
    });

});
