document.querySelectorAll(".left-sidebar").forEach(el => {el.remove()});
document.querySelectorAll(".right-sidebar").forEach(el => {el.remove()});
document.querySelectorAll("div#reddit-chat").forEach(el => {el.parentNode.remove()});
document.querySelectorAll("div[bundlename=reddit_cookie_banner]").forEach(el => {el.remove()});


// posts list
document.querySelectorAll("div.community-highlight-carousel").forEach(el => {el.remove()});
document.querySelectorAll("div[bundlename=shreddit_sort_dropdown]").forEach(el => {el.remove()});

// comments list
document.querySelectorAll("div[bundlename=comment_body_header]").forEach(el => {el.remove()});
document.querySelectorAll("a[slot=more-comments-permalink]").forEach(el => {el.remove()});

//old comments

document.querySelectorAll('div.content form.usertext').forEach(article => {
let parent = article.parentElement;
while (article.firstChild) {
                    parent.appendChild(article.firstChild);
                }
article.remove();
})

document.querySelectorAll("ul.flat-list.buttons").forEach(el => {el.remove()});


// comments
/*document.querySelectorAll("div[slot=text-body]").forEach(el => {el.innerText = "POST_START:\n\n" + el.innerText.trim() + "\n\nPOST_END\n\n"});
document.querySelectorAll("div[slot=commentMeta]").forEach(el => {el.innerText = "META_START:\n\n" + el.innerText.trim() + "\n\nMETA_END\n\n"});
document.querySelectorAll("div[slot=comment]").forEach(el => {el.innerText = "COMMENT_START:\n\n" + el.innerText.trim() + "\n\nCOMMENT_END\n\n"});
*/

/*
const main = document.querySelector('main');
const articles = main.querySelectorAll('article');
articles.forEach(article => {
    while (article.firstChild) {
                    main.appendChild(article.firstChild);
                }
    let parent = article.parentElement;
                article.remove(); // Remove the empty article

                // Traverse up the tree and remove empty parent divs
                while (parent && parent !== main && parent.childElementCount === 0) {
                    const grandparent = parent.parentElement;
                    parent.remove();
                    parent = grandparent;
                }
})*/

/*let textContent = document.querySelector("main").innerText
document.querySelector("main").innerText = textContent
*/