const nativeFetch = window.fetch;
window.running_fetches = 0
function reduce_fetch_counter(){
  window.running_fetches = window.running_fetches - 1
  console.log('completed fetch call, now: '+ window.running_fetches);
  if(window.onFetchCompleted && window.running_fetches == 0 )
  {
     window.onFetchCompleted() 
  }
}

window.fetch = async function(...args) {
  
  window.running_fetches = window.running_fetches + 1
  console.log('detected fetch call, now: ' + window.running_fetches);
  el = await nativeFetch.apply(window, args);
  
  setTimeout(reduce_fetch_counter, 1000);
  
  return el;
}