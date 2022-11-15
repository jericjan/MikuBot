function makeUL(array) {
    // Create the list element:
    var list = document.createElement('ul');

    for (var i = 0; i < array.length; i++) {
        // Create the list item:
        var item = document.createElement('li');

        // Set its contents:
        text = document.createElement("a")
        text.innerHTML = array[i]
        item.appendChild(text);

        closeButton = document.createElement("button")
        closeButton.innerHTML = "X"
        closeButton.onclick = function(){
          var textStuff = this.previousElementSibling.innerHTML
          doDelete = confirm(`Do you want to delete "${textStuff}?"`)
          if (doDelete == true){
            var xmlHttp = new XMLHttpRequest();
            var query = encodeURI(textStuff)
            xmlHttp.open( "GET", "/delete?query="+query, false ); // false for synchronous request
            xmlHttp.send();
            var errors = parseInt(xmlHttp.responseText)
            alert(`Done! ${errors} errors`)
            if (errors == 0){
            this.parentElement.remove()
              }
          }

        }
        item.appendChild(closeButton);

        // Add it to the list:
        list.appendChild(item);
    }

    // Finally, return the constructed list:
    return list;
}

document.querySelector("#all").onclick = function(){
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.open( "GET", "/all", false ); // false for synchronous request
  xmlHttp.send();
  json_list = JSON.parse(xmlHttp.responseText)['results'];
  var divList = document.getElementById("list");  
  divList.innerHTML = "";
  divList.appendChild(makeUL(json_list));
};
  
document.querySelector("#search").onclick = function(){
  var xmlHttp = new XMLHttpRequest();
  var query = encodeURI(document.querySelector("input").value)
  xmlHttp.open( "GET", "/search?query="+query, false ); // false for synchronous request
  xmlHttp.send();
  json_list = JSON.parse(xmlHttp.responseText)['results'];
  var divList = document.getElementById("list");  
  divList.innerHTML = "";
  divList.appendChild(makeUL(json_list));
};