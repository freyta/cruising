// ==UserScript==
// @name         Ozcruising Mobile price per night
// @namespace    http://freyta.net/
// @version      2024-09-08
// @description  Calculate and display price per night. Highlight any deals below $100pp
// @author       Freyta
// @match        https://m.ozcruising.com.au/*
// @icon         https://static.ozcruising.com.au/assets/www-ozcruising-com-au/images/favicon/apple-touch-icon-76x76.png
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
        // Select all ".col-xs-6" elements inside the rows with price information
        let rows = document.querySelectorAll('.row .col-xs-6');

        rows.forEach((row) => {
            // Find all div elements that contain prices (those with the "$" sign)
            let priceDivs = row.querySelectorAll('div[style="min-height: 45px;"] div');
            let nightsDiv = row.querySelector('div[style="min-height: 130px;"] div:nth-child(1)');

            let price = 0, nights = 0;
            let price_split = "";
            let SPECIAL_PRICE = 100;

            // Extract the number of nights
            if (nightsDiv) {
                let nightsText = nightsDiv.textContent.trim();
                if (nightsText.includes("Nights")) {
                    nights = parseInt(nightsText.split(" Nights")[0]);  // Extract the number of nights as an integer
                }
            }

            // Loop through price divs and extract the twin price
            priceDivs.forEach((div) => {

                let parentDiv = row.closest('.row').parentElement;
                let text = div.textContent.trim();
                if (text.includes("Twin From")) {
                    let priceText = text.split("Twin From  $")[1]; // Extract the price
                    price_split = priceText.split(" ")[0].replace(",", ""); // Remove commas
                    price = parseFloat(price_split);  // Convert the price to a number

                    if (nights > 0 && price > 0) {
                        // Calculate price per night
                        let price_per_night = (price / nights).toFixed(2);

                        // Check if the price per night is already displayed
                        if (!div.querySelector('.price-per-night')) {
                            // Create a new text element to display the price per night
                            let pricePerNightText = document.createElement('div');
                            pricePerNightText.className = 'price-per-night'; // Add a class to identify it
                            pricePerNightText.textContent = `Price per night: $${price_per_night} pp`;
                            pricePerNightText.style.fontWeight = 'bold'; // Optional: Style the text
                            if (price_per_night <= SPECIAL_PRICE) {
                                pricePerNightText.style.color = 'red'; // Optional: Style the text
                                parentDiv.classList.add('pulse-background');
                            } else {
                                pricePerNightText.style.color = 'black'; // Optional: Style the text
                            }
                            // Insert the new text element below the existing price element
                            div.appendChild(pricePerNightText);
                        }
                    } else {
                        console.log("Price or nights data missing for this row.");
                    }
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
