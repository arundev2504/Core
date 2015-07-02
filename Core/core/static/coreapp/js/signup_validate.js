function validateForm(){
    var pass = document.forms["signupForm"]["password"].value;
    var confPass = document.forms["signupForm"]["re_password"].value;		
        if(pass !== confPass){
	      	alert("Passwords not matching!!");
        	document.getElementById('re_password').value='';
        	return false;        		
        }
}	
