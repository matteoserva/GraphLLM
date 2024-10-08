function removeNode(name) {document.querySelectorAll(name).forEach(el => {d = document.createElement("div"); d.setAttribute("prevTag",el.tagName); d.innerHTML = el.innerHTML; el.replaceWith(d) });}
function replaceWith(node, newTag)
{
d = document.createElement("div");
d.setAttribute("prevTag",node.tagName);
node.querySelectorAll("a").forEach(el => {el.replaceWith("["+el.innerText+"]("+el.href+")");});
d.innerText = node.innerText
node.replaceWith(d)

}

function replaceComment(node, newTag)
{
m = document.querySelector("div[prevTag='SHREDDIT-POST']")

node.querySelectorAll("a").forEach(el => {el.replaceWith("["+el.innerText+"]("+el.href+")");});

d = document.createElement("div");
d.setAttribute("prevTag",node.tagName);
d.innerText = node.innerText
//d.innerText = d.innerText.replace(/(\r\n|\r|\n)(\r\n|\r|\n\s){1,}(\r\n|\r|\n)/g, '\n\n');

node.parentNode.removeChild(node)
m.appendChild(d)


}

function removeAds()
{
document.querySelectorAll("shreddit-async-loader").forEach(el => {el.parentNode.removeChild(el) });
document.querySelectorAll("shreddit-comments-page-ad").forEach(el => {el.parentNode.removeChild(el) });
document.querySelectorAll("shreddit-comments-tree-ad").forEach(el => {el.parentNode.removeChild(el) });
document.querySelectorAll("shreddit-dynamic-ad-link").forEach(el => {el.parentNode.removeChild(el) });
}

  //old subreddit post
  //document.querySelectorAll("form.usertext > div").forEach(el => {p =el.parentNode; p.removeChild(el); p.parentNode.append(el)}); 

  // old subreddit post
  document.querySelectorAll("div[class='commentarea'] div[data-subreddit]").forEach(el => {p = el.parentNode; el.parentNode.removeChild(el); p.parentNode.parentNode.appendChild(el)});
  // replace links before removing nodes. So it works for the list of links too
  document.querySelectorAll("div[data-subreddit] a").forEach(el => {el.replaceWith("["+el.innerText+"]("+el.href+")");});
  document.querySelectorAll("div[data-subreddit]").forEach(el => {el.replaceWith(el.innerText)});

// new reddit



//removeNode("shreddit-post")

removeAds()
document.querySelectorAll("faceplate-partial#top-level-more-comments-partial").forEach(el => {el.parentNode.removeChild(el)});
// new reddit single post
removeNode("shreddit-title")
document.querySelectorAll("div[id='next-comment']").forEach(el => {el.parentNode.removeChild(el) });
document.querySelectorAll("main > shreddit-post").forEach(el => {replaceWith(el,"div")});
document.querySelectorAll("shreddit-comment").forEach(el => {replaceComment(el,"div")});
document.querySelectorAll("shreddit-comment").forEach(el => {replaceComment(el,"div")});
document.querySelectorAll("shreddit-comment").forEach(el => {replaceComment(el,"div")});
document.querySelectorAll("shreddit-comment").forEach(el => {replaceComment(el,"div")});
document.querySelectorAll("shreddit-comment-tree").forEach(el => {d = document.createElement("div"); d.innerHTML = el.innerHTML; el.replaceWith(d) });
document.querySelectorAll("shreddit-comment-tree").forEach(el => {d = document.createElement("div"); d.innerHTML = el.innerHTML; el.replaceWith(d) });
document.querySelectorAll("shreddit-comment-tree").forEach(el => {d = document.createElement("div"); d.innerHTML = el.innerHTML; el.replaceWith(d) });

// new reddit list
document.querySelectorAll("shreddit-post a div div").forEach(el => {el.textContent = el.textContent.substring(0,100)});

removeAds()
