// ==UserScript==
// @name         Cruisemart PPN Cruise page
// @namespace    http://freyta.net/
// @version      2024-10-12
// @description  Calculate and display price per night. Highlight any deals below $100pp
// @author       Freyta
// @match        https://*.cruisemart.com.au/swift/*
// @icon         https://www.cruisemart.com.au/Common/showimage.ashx/561142?Id=561142
// @grant        none
// ==/UserScript==

(function() {
    'use strict';

    const style = document.createElement('style');
    style.textContent = `
        @keyframes pulse {
            0% { background-color: lightred; }
            50% { background-color: #FFD5CC; }
            100% { background-color: lightred; }
        }
        .pulse-background {
            animation: pulse 1.8s infinite;
        }
    `;
    document.head.appendChild(style);

    function updatePrices() {
        let rows = document.querySelectorAll('div.card.cruise-item-card');

        rows.forEach((row) => {
            let nightsElement = row.querySelector('div.cruise-info-detail-item-inner.text-nowrap');
            let nights = 0;
            const SPECIAL_PRICE = 100;

            // Extract the number of nights
            if (nightsElement) {
                nights = parseInt(nightsElement.textContent.split(" Nights")[0]);
            } else {
                console.log('Nights element not found');
            }

            // Ensure we have a valid number of nights before processing prices
            if (nights > 0) {
                let priceRows = row.querySelectorAll('table.table.striped tr');

                priceRows.forEach((priceRow) => {
                    let priceElements = priceRow.querySelectorAll('.lowest-sailing-price');

                    priceElements.forEach((priceElement) => {
                        // Check if the price per night text has already been added
                        if (priceElement.dataset.perNightAdded) return;

                        if (priceElement) {
                            let priceText = priceElement.textContent;
                            let price = parseInt(priceText.replace(/[A$,\s]/g, ''));

                            if (!isNaN(price) && price > 0) {
                                let per_night = (price / nights).toFixed(2);
                                let textNode = document.createTextNode(` (${per_night} / night)`);

                                // Append the text node
                                priceElement.appendChild(textNode);

                                // Mark that the price per night text has been added
                                priceElement.dataset.perNightAdded = true;

                                // Change text color for special pricing
                                if (per_night <= SPECIAL_PRICE) {
                                    priceElement.style.color = 'red';
                                    priceElement.style.fontWeight = 'bold';
                                    // Add pulse animation for special price
                                    priceElement.parentElement.style.animation = 'pulse 2s infinite';
                                } else {
                                    priceElement.style.color = 'black';
                                }
                            } else {
                                console.log('Price value is invalid or not found');
                            }
                        }
                    });
                });
            } else {
                console.log('Nights value not found or is invalid.');
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
