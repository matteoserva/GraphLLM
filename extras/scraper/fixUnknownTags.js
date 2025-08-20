/**
 * Recursively traverses a DOM tree and replaces non-standard HTML elements with a <div>.
 * A "non-standard" element is identified if its constructor is the generic HTMLElement.
 *
 * @param {Node} rootNode The DOM node to start the traversal from. Defaults to document.body.
 */
function replaceNonStandardTags(rootNode = document.body) {

  // We define the recursive function inside the main function
  // to keep it self-contained.
  function traverse(currentNode) {
    // 1. We must first iterate over a static copy of the children.
    // If we iterate over the live NodeList and replace a child,
    // the list will change, causing us to skip elements.
    const children = Array.from(currentNode.children);
    for (const child of children) {
      traverse(child); // Recurse deeper into the tree
    }

    // 2. After handling the children, process the current node itself.
    // The most reliable way to check for a non-standard element is to see
    // if its constructor is the base HTMLElement. Standard elements like <p>
    // have specific constructors like HTMLParagraphElement.
    // We also make sure it's an element node (nodeType 1).
    if (customElements.get(currentNode.tagName.toLowerCase() ) ) {

      console.log(`Found non-standard tag: <${currentNode.tagName.toLowerCase()}>. Replacing with <div>.`);

      // 3. Create the new <div> element
      const newDiv = document.createElement('div');

      // 4. Copy all attributes from the old element to the new one
      for (const attr of currentNode.attributes) {
        newDiv.setAttribute(attr.name, attr.value);
      }

      // 5. Move all child nodes from the old element to the new one.
      // Using a while loop with appendChild is an efficient way to move all nodes.
      while (currentNode.firstChild) {
        newDiv.appendChild(currentNode.firstChild);
      }

      // 6. Replace the old element with the new div in the DOM tree.
      // We need to check if the parentNode exists (it might be the root).
      if (currentNode.parentNode) {
        currentNode.parentNode.replaceChild(newDiv, currentNode);
      }
    }
  }

  // Start the traversal from the root node
  traverse(rootNode);
}

replaceNonStandardTags();
