function convertRelativeLinksToAbsolute() {
  // Select all elements that can have a link-like attribute
  const elements = document.querySelectorAll('a[href], link[href], img[src], script[src], form[action]');

  elements.forEach(el => {
    // The magic happens here. When you access properties like .href or .src,
    // the browser returns the fully resolved, absolute URL. We then take
    // that value and explicitly set the attribute with it.

    if (el.href) { // For <a> and <link> tags
      el.setAttribute('href', el.href);
    } else if (el.src) { // For <img> and <script> tags
      el.setAttribute('src', el.src);
    } else if (el.action) { // For <form> tags
      el.setAttribute('action', el.action);
    }
  });
}
convertRelativeLinksToAbsolute();