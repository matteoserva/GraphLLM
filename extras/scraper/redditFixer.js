  //old subreddit post
  //document.querySelectorAll("form.usertext > div").forEach(el => {p =el.parentNode; p.removeChild(el); p.parentNode.append(el)}); 
  document.querySelectorAll("div[class='commentarea'] div[data-subreddit]").forEach(el => {p = el.parentNode; el.parentNode.removeChild(el); p.parentNode.parentNode.appendChild(el)});
  // replace links before removing nodes. So it works for the list of links too
  document.querySelectorAll("div[data-subreddit] a").forEach(el => {el.replaceWith("["+el.innerText+"]("+el.href+")");});
  document.querySelectorAll("div[data-subreddit]").forEach(el => {el.replaceWith(el.innerText)});

// new reddit
function removeNode(name) {document.querySelectorAll(name).forEach(el => {d = document.createElement("div"); d.setAttribute("prevTag",el.tagName); d.innerHTML = el.innerHTML; el.replaceWith(d) });}
removeNode("shreddit-title")
//removeNode("shreddit-post")
document.querySelectorAll("shreddit-async-loader").forEach(el => {el.parentNode.removeChild(el) });
document.querySelectorAll("main > shreddit-post").forEach(el => {el.replaceWith(el.innerText)});
document.querySelectorAll("shreddit-comment").forEach(el => {el.replaceWith(el.innerText)});
document.querySelectorAll("shreddit-comment").forEach(el => {el.replaceWith(el.innerText)});
document.querySelectorAll("shreddit-comment").forEach(el => {el.replaceWith(el.innerText)});
document.querySelectorAll("shreddit-comment").forEach(el => {el.replaceWith(el.innerText)});
document.querySelectorAll("shreddit-comment-tree").forEach(el => {d = document.createElement("div"); d.innerHTML = el.innerHTML; el.replaceWith(d) });
document.querySelectorAll("shreddit-comment-tree").forEach(el => {d = document.createElement("div"); d.innerHTML = el.innerHTML; el.replaceWith(d) });
document.querySelectorAll("shreddit-comment-tree").forEach(el => {d = document.createElement("div"); d.innerHTML = el.innerHTML; el.replaceWith(d) });