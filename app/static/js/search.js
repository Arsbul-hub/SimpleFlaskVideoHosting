
String.prototype.format = function() {
    let formatted = this;
    for (let i = 0; i < arguments.length; i++) {
      let regexp = new RegExp('\\{'+i+'\\}', 'gi');
      formatted = formatted.replace(regexp, arguments[i]);
    }
    return formatted;
  };
      function get_search_event(event) {
      
          if (event.code == "Enter") {
              req = document.getElementById("search-field").value;
              console.log(req);
              window.location.href = `/Поиск видео?category=string&request=${req}`;
              
          }
      }
  
  
  