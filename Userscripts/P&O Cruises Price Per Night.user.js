// ==UserScript==
// @name         P&O Cruises Price Per Night
// @namespace    http://freyta.net/
// @version      2025-01-06
// @description  Display the price per night on the P&O Cruises search page
// @author       Freyta
// @match        https://www.pocruises.com.au/cruises/search*
// @match        https://www.pocruises.com.au/homeports/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=pocruises.com.au
// @grant        none
// ==/UserScript==


(function() {
    'use strict';

    const style = document.createElement('style');

    document.head.appendChild(style);

    function updatePrices() {
        let rows = document.querySelectorAll('div[class="col-12 ng-star-inserted"]');

        rows.forEach((row) => {
            // Select all price elements in the row
            const priceDivs = row.querySelectorAll('h4[class="mb-0"]');

            priceDivs.forEach((priceDiv) => {
                const priceText = parseFloat(priceDiv.textContent.trim().replace("A$", "").replace(",", ""));
                const daysDiv = row.querySelector('div[class="d-lg-flex mt-1 mt-md-3"] div[class="me-5"] + div h4[class="color-white"]');
                if (!daysDiv) return; // Skip if daysDiv is not found
                const daysText = parseInt(daysDiv.textContent.trim().split("Nights")[0].replace(/\D/g, ''));

                let SPECIAL_PRICE = 100;

                // Avoid adding price per night multiple times
                if (priceDiv.querySelector('.price-per-night')) {
                    return; // Skip if the price per night is already added
                }

                if (daysText > 0 && priceText > 0) {
                    // Calculate price per night
                    let price_per_night = (priceText / daysText).toFixed(2);

                    // Create a new div element to display the price per night
                    let pricePerNightText = document.createElement('div');
                    pricePerNightText.className = 'price-per-night'; // Add a class to identify it
                    pricePerNightText.textContent = `Price per night: $${price_per_night} pp`;
                    pricePerNightText.style.fontWeight = 'bold'; // Optional: Style the text
                    pricePerNightText.style.fontSize = 'small'; // Optional: Style the text

                    if (price_per_night <= SPECIAL_PRICE) {
                        pricePerNightText.style.color = 'red'; // Highlight deals below $110
                        row.classList.add('pulse-background'); // Apply the class to the individual row
                    } else {
                        pricePerNightText.style.color = 'black'; // Default color
                    }
                    priceDiv.appendChild(pricePerNightText); // Append to the correct container
                }
            });
        });
    }


    // Create a MutationObserver to watch for changes in the DOM
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                updatePrices();
            }
        });
    });

    // Observe the body for changes
    observer.observe(document.body, { childList: true, subtree: true });

    // Initial run to handle content already loaded
    updatePrices();
})();