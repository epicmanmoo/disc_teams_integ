setInterval(function(){
    let url = "https://graph.microsoft.com/v1.0/me/presence";

	let XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;
	let xhr = new XMLHttpRequest();
	xhr.open("GET", url);
	
	var fs = require('fs');
	fs.readFile('ACCESS_TOKEN.txt', 'utf8', function(err, data){
		let access_token = data;

		let auth = "Bearer " + access_token;
	
		xhr.setRequestHeader("Authorization", auth);
	
	
		xhr.onreadystatechange = function () {
			if (xhr.readyState === 4) {
				fs.writeFile('REQUEST_OUTPUT.txt', xhr.status + '\n' + xhr.responseText, function (err) {
					if (err) throw err;
					console.log('Updated.');
				});
			}
		};
	
		xhr.send();
		
	});

}, 5000);
