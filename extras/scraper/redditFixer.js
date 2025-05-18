function removeNode(name) {
  document.querySelectorAll(name).forEach(el => {
              d = document.createElement("div");
              d.setAttribute("prevTag",el.tagName);
              d.innerHTML = el.innerHTML;
              el.replaceWith(d) });
  
}

function replaceNode(name,newTag = "div") {
  document.querySelectorAll(name).forEach(el => {
              d = document.createElement(newTag);
              d.setAttribute("prevTag",el.tagName);
              d.innerHTML = el.innerHTML;
              el.replaceWith(d) });
  
}

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
    document.querySelectorAll("shreddit-comment-tree-ad").forEach(el => {el.parentNode.removeChild(el) });
    
    document.querySelectorAll("shreddit-dynamic-ad-link").forEach(el => {el.parentNode.removeChild(el) });
}


var hostname = window.location.hostname;
var second_level = hostname.split(".").reverse()[1]

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function fix_reddit_new_post()
{
    document.querySelectorAll("faceplate-partial[loading=action]").forEach(el => {el.click()});
    document.querySelectorAll("shreddit-post button").forEach(el => {el.click()});
    window.onFetchCompleted = function() {
        removeAds()
        document.querySelectorAll("faceplate-partial#top-level-more-comments-partial").forEach(el => {el.parentNode.removeChild(el)});
        removeNode("shreddit-title")
        document.querySelectorAll("div[id='next-comment']").forEach(el => {el.parentNode.removeChild(el) });
        document.querySelectorAll("main > shreddit-post").forEach(el => {replaceWith(el,"div")});
        document.querySelectorAll("faceplate-loader").forEach(el => {el.parentNode.removeChild(el) });
        document.querySelectorAll("faceplate-partial").forEach(el => {el.parentNode.removeChild(el) });
        
        document.querySelectorAll("faceplate-batch").forEach(el => {el.parentNode.outerHTML = el.innerHTML});
        document.querySelectorAll("shreddit-comment-tree-stats").forEach(el => {el.parentNode.removeChild(el) });
        
        while(document.querySelectorAll("shreddit-comment-tree").length > 0)
        {
            replaceNode("shreddit-comment-tree")
            while(document.querySelectorAll("shreddit-comment").length > 0){         replaceNode("shreddit-comment") }
            //document.querySelectorAll("shreddit-comment").forEach(el => {replaceComment(el,"div")});
        }
        
        //document.querySelectorAll("faceplate-batch").forEach(el => {replaceWith(el,"div")});
        /*document.querySelectorAll("shreddit-comment").forEach(el => {replaceComment(el,"div")});
        document.querySelectorAll("shreddit-comment").forEach(el => {replaceComment(el,"div")});
        document.querySelectorAll("shreddit-comment").forEach(el => {replaceComment(el,"div")});
        
        
        document.querySelectorAll("shreddit-comment-tree").forEach(el => {d = document.createElement("div"); d.innerHTML = el.innerHTML; el.replaceWith(d) });
        document.querySelectorAll("shreddit-comment-tree").forEach(el => {d = document.createElement("div"); d.innerHTML = el.innerHTML; el.replaceWith(d) });*/
        removeAds()
        
    }
}


if (second_level == "reddit")
{
      var isOldPost = document.querySelectorAll("div[class='commentarea']").length > 0;
      var isNewPost = document.querySelectorAll("main > shreddit-post").length > 0;
      var isOldList = document.querySelectorAll("div[data-context=listing]").length > 0;
      var isNewList = document.querySelectorAll("main shreddit-feed").length > 0;
      console.log("old post", isOldPost, "new post", isNewPost, "old list", isOldList, "new list", isNewList);
      //old subreddit post
      //document.querySelectorAll("form.usertext > div").forEach(el => {p =el.parentNode; p.removeChild(el); p.parentNode.append(el)}); 

      // old subreddit post
      document.querySelectorAll("div[class='commentarea'] div[data-subreddit]").forEach(el => {p = el.parentNode; el.parentNode.removeChild(el); p.parentNode.parentNode.appendChild(el)});
      // replace links before removing nodes. So it works for the list of links too
      document.querySelectorAll("div[data-subreddit] a").forEach(el => {el.replaceWith("["+el.innerText+"]("+el.href+")");});
      //document.querySelectorAll("div[data-subreddit]").forEach(el => {el.replaceWith(el.innerText);});
      document.querySelectorAll("div.content").forEach(el => {el.innerText = el.innerText;});

    // new reddit

     // remove sidebars from new reddit
      document.querySelectorAll(".left-sidebar").forEach(el => {el.remove()});
      document.querySelectorAll(".right-sidebar").forEach(el => {el.remove()});
      
      // remove header with ads and stuff
      document.querySelectorAll(".masthead").forEach(el => {el.remove()});
      document.querySelectorAll("reddit-header-large").forEach(el => {el.remove()});

    //removeNode("shreddit-post")

    //
    
    // new reddit single post
    
    if (isNewPost)
    {
        
        fix_reddit_new_post()
        
        /**/
    }
    else
    {
        // new reddit list
        document.querySelectorAll("shreddit-post a div div").forEach(el => {el.textContent = el.textContent.substring(0,100)});

        //document.querySelectorAll("shreddit-post > a").forEach(el => {replaceWith(el,"div")});
        //replaceNode("shreddit-post > a","div")
        document.querySelectorAll("a[slot=full-post-link]").forEach(el => {el.remove()});
        document.querySelectorAll("div[slot=thumbnail]").forEach(el => {el.remove()});
        document.querySelectorAll("shreddit-post-flair").forEach(el => {el.remove()});
        document.querySelectorAll("shreddit-async-loader").forEach(el => {el.remove()}); //replaceNode("shreddit-async-loader")
        
        
        document.querySelectorAll("article a").forEach(el => {el.replaceWith("["+el.innerText+"]("+el.href+")");});
        document.querySelectorAll("shreddit-post").forEach(el => {replaceWith(el,"div")})
        //article = new window.a(document.cloneNode(true)).parse()
    }
    
}