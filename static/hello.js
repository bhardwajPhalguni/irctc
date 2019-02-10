<!DOCTYPE html>
<html lang="en" dir="ltr">
   <head>
	<meta charset="utf-8">
      <script type = "text/javascript" 
         src = "{{ url_for('static', filename = 'hello.js') }}" ></script>
   </head>
   
   <body>
	
	<form action = "/login" method = "POST">
  
	<p><h3>Enter full name</h3></p>
         
	<p><input type = 'text' name = 'nm'/></p>
		 
	E-mail : <p><input type = 'text' name = 'e-mail'/></p>
 
	<input type = "submit" value = "Submit" />