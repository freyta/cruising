// ==UserScript==
// @name         Princess Cruises add room number to booking page
// @namespace    http://freyta.net/
// @version      1.2
// @description  Add missing text to cabin figures using their IDs, remove "cabin-text-" prefix, make the text color black, and adjust its vertical position.
// @author       Freyta
// @match        https://www.princess.com/cruise-search/stateroom-location/
                 https://www.princess.com/cruise-search/stateroom-location/
// @icon         https://www.google.com/s2/favicons?sz=64&domain=princess.com
// @grant        none
// ==/UserScript==

(function () {
    'use strict';

    // Find all elements with the class 'cabin-figure'
    const observer = new MutationObserver(() => {
        document.querySelectorAll('.cabin-figure').forEach(cabinFigure => {
            // Find the <text> element inside the cabin-figure
            const textElement = cabinFigure.querySelector('text');

            if (textElement) {
                // Check if the <text> field is empty
                if (!textElement.textContent.trim()) {
                    // Get the 'id' attribute of the <text> element
                    const textId = textElement.id;

                    if (textId && textId.startsWith('cabin-text-')) {
                        // Remove the "cabin-text-" prefix
                        const newText = textId.replace('cabin-text-', '');

                        // Set the new text content
                        textElement.textContent = newText;

                        // Update the text color to black for readability
                        textElement.setAttribute('fill', 'black');

                        // Adjust the vertical position of the text by modifying the 'x' value
                        const currentX = parseFloat(textElement.getAttribute('x')) || 0; // Default to 0 if 'x' is not set
                        textElement.setAttribute('x', currentX - 5); // Move text higher by 5 units
                    }
                }
            }
        });
    });

    // Start observing the body for changes
    observer.observe(document.body, { childList: true, subtree: true });

})();
