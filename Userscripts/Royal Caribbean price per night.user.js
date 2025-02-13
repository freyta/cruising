// ==UserScript==
// @name         Royal Caribbean
// @namespace    http://freyta.net/
// @version      2025-02-13
// @description  Calculate and display price per night. Highlight any deals below $100pp
// @author       Freyta
// @match        https://www.royalcaribbean.com/*
// @icon         https://www.google.com/s2/favicons?sz=64&domain=royalcaribbean.com
// @grant        none
// ==/UserScript==


(function() {
    'use strict';

    const style = document.createElement('style');
    style.textContent = `
        @keyframes pulse {
            0% { background-color: lightred; }
            50% { background-color: #FFD5CC; } /* Lighter blue */
            100% { background-color: lightred; }
        }
        .pulse-background {
            animation: pulse 1.8s infinite;
        }
    `;

    document.head.appendChild(style);

    function updatePrices() {
        let rows = document.querySelectorAll('div[data-testid^="cruise-card-container"]');

        rows.forEach((row) => {
            const priceDiv = row.querySelector('div[data-testid^="cruise-price-label"]');
            let   priceText = priceDiv.textContent.trim().replace("$",""); // Strip the $ sign
                  priceText = parseFloat(priceText.replace(",","")); // Convert price to number

            const textReplace = row.querySelector('div[data-testid^="cruise-price-label"]'); // Target the correct container for price-per-night
            const daysDivs = row.querySelector('h3[data-testid^="cruise-duration-label"]').textContent.trim();
            const daysText = parseInt(daysDivs.split("-")[0].replace(/\D/g, '')); // Extract the number of days

            let SPECIAL_PRICE = 100;

            // Avoid adding price per night multiple times
            if (textReplace.querySelector('.price-per-night')) {
                return; // Skip if the price per night is already added
            }

            if (daysText > 0 && priceText > 0) {
                // Calculate price per night
                let price_per_night = (priceText / daysText).toFixed(2); // Generate the price per night, rounded to 2 digits

                // Create a new div element to display the price per night
                let pricePerNightText = document.createElement('div');
                pricePerNightText.className = 'price-per-night'; // Add a class to identify it
                pricePerNightText.textContent = `$${price_per_night} pp/n`; // The text we are adding
                pricePerNightText.style.fontWeight = 'bold'; // Style the text
                pricePerNightText.style.fontSize = 'small'; // Style the text


                if (price_per_night <= SPECIAL_PRICE) {
                    pricePerNightText.style.color = 'red'; // Highlight deals below $100
                    row.classList.add('pulse-background'); // Apply the class to the individual row
                } else {
                    pricePerNightText.style.color = 'black'; // Default colour
                    row.classList.add('price-per-night'); // Add our div
                }
                textReplace.appendChild(pricePerNightText); // Append to the correct container
            }
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