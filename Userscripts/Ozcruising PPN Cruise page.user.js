// ==UserScript==
// @name         Ozcruising PPN Cruise page
// @namespace    http://freyta.net/
// @version      2024-09-08
// @description  Calculate and display price per night. Highlight any deals below $100pp
// @author       Freyta
// @match        https://*.ozcruising.com.au/cruise/*
// @match        https://*.cruises.com.au/cruise/*
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
        // Select the table rows inside the tbody
        let rows = document.querySelectorAll('table tbody tr');

        // Select the div that contains the information about the number of nights
        let nights_div = document.querySelector('div .media-body');

        // Find the element that contains the "Nights" text (with the hourglass icon)
        let nightsElement = Array.from(nights_div.querySelectorAll('i.font-blue-soft.fa-hourglass.fa')).find(el => el.nextSibling.textContent.includes('Nights'));
        let nights = 0;
        let SPECIAL_PRICE = 100;

        // If the nightsElement is found, extract the text and use a regex to capture the number of nights
        if (nightsElement) {
            let nightsText = nightsElement.nextSibling.textContent.trim(); // Get the text content after the hourglass icon
            nights = parseInt(nightsText.match(/\d+/)[0]); // Use regex to match the first number in the text
        } else {
            console.log('Nights element not found');
        }

        // Ensure we found the nights value before continuing
        if (nights > 0) {
            // Loop through each row and extract the price from the third column (Price (pp))
            rows.forEach((row) => {
                // Get the third 'td' element which contains the price (pp)
                let priceCell = row.querySelectorAll('td')[2]; // The price (pp) is in the third column (index 2)

                if (priceCell) {
                    // Extract and clean the price (remove the $ sign and commas if necessary)
                    let priceText = priceCell.textContent.trim();
                    let price = priceText.replace('$', '').replace(',', '');

                    // Validate if the extracted price is a valid number
                    if (!isNaN(price) && price !== "") {
                        // Calculate the price per night
                        let price_per_night = (parseFloat(price) / nights).toFixed(2);

                        // Check for NaN in the price_per_night calculation
                        if (!isNaN(price_per_night)) {
                            // Create a new div to display the price per night
                            let pricePerNightText = document.createElement('div');
                            pricePerNightText.className = 'price-per-night'; // Add a class to identify it
                            pricePerNightText.textContent = `$${price_per_night} pp`;

                            // Change the text color if price per night is lower than or equal to SPECIAL_PRICE
                            if (price_per_night <= SPECIAL_PRICE) {
                                pricePerNightText.style.color = 'red'; // Special price
                                pricePerNightText.style.fontWeight = 'bold'; // Style the text
                                // Add pulse animation for special price
                                priceCell.parentElement.style.animation = 'pulse 2s infinite';
                            } else {
                                pricePerNightText.style.color = 'black'; // Regular price
                            }

                            // Insert the new text element below the existing price element
                            priceCell.appendChild(pricePerNightText);
                        } else {
                            console.log('Price per night calculation resulted in NaN');
                        }
                    } else {
                        console.log('Price value is invalid or not found');
                    }
                }
            });
        } else {
            console.log('Nights value not found or is invalid.');
        }

        // CSS for the pulse animation
        let styleSheet = document.createElement("style");
        styleSheet.type = "text/css";
        styleSheet.innerText = `
    @keyframes pulse {
        0% { background-color: rgba(173, 216, 230, 1); }
        50% { background-color: rgba(173, 216, 230, 0.5); }
        100% { background-color: rgba(173, 216, 230, 1); }
    }
`;
        document.head.appendChild(styleSheet);

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
