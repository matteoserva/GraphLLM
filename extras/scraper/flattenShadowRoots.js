/**
         * Recursively flattens all shadow roots within a given element.
         * This function modifies the DOM in place.
         * @param {HTMLElement} element The root element to start flattening from.
         */
        function flattenShadow(element) {
            // First, recurse on the children. This is a depth-first traversal.
            // We convert childNodes to an array to prevent issues with a live NodeList while mutating the DOM.
            [...element.childNodes].forEach(child => {
                if (child.nodeType === Node.ELEMENT_NODE) {
                    flattenShadow(child);
                }
            });

            // After all children are processed, process the element itself.
            if (element.shadowRoot) {
                const host = element;
                const shadow = host.shadowRoot;
                const nodesToInsert = [];

                // Process each node in the shadow DOM
                [...shadow.childNodes].forEach(shadowNode => {
                    if (shadowNode.nodeName === 'SLOT') {
                        // This is a slot element, find the nodes assigned to it.
                        // The { flatten: true } option is important for nested slots.
                        const assignedNodes = shadowNode.assignedNodes({ flatten: true });

                        if (assignedNodes.length > 0) {
                            // If nodes are assigned, process and add them.
                            assignedNodes.forEach(node => {
                                // We must recursively flatten the slotted content as well,
                                // in case a custom element was passed into a slot.
                                if (node.nodeType === Node.ELEMENT_NODE) {
                                    flattenShadow(node);
                                }
                                nodesToInsert.push(node);
                            });
                        } else {
                            // If no nodes are assigned, use the slot's fallback content.
                            [...shadowNode.childNodes].forEach(fallbackNode => {
                                if (fallbackNode.nodeType === Node.ELEMENT_NODE) {
                                    flattenShadow(fallbackNode);
                                }
                                nodesToInsert.push(fallbackNode);
                            });
                        }
                    } else {
                        // This is a regular node in the shadow DOM.
                        // Recursively process it before adding.
                        if (shadowNode.nodeType === Node.ELEMENT_NODE) {
                           flattenShadow(shadowNode);
                        }
                        nodesToInsert.push(shadowNode);
                    }
                });

                // Replace the host element with the processed nodes from its shadow DOM.
                host.replaceWith(...nodesToInsert);
            }
        }

        /**
         * Main function to trigger the flattening.
         * It clones the target area so the original is preserved for comparison.
         * @param {HTMLElement} rootNode The element to flatten.
         */
        function flattenAllShadowRoots(rootNode) {
            console.log("Starting to flatten the DOM...");

            // Clone the node to keep the original for comparison
            const clone = rootNode

            // Run the flattening process on the clone
            flattenShadow(clone);

            // Display the result
            const flattenedContent = document.getElementById('flattened-content');
            flattenedContent.innerHTML = ''; // Clear previous results
            flattenedContent.appendChild(clone);
            document.getElementById('flattened-area').style.display = 'block';

            console.log("Flattening complete.");
        }

flattenAllShadowRoots(document.body)