import { auth } from "./firebase.js";

import { createUserWithEmailAndPassword } 
from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";


const form = document.querySelector("form");


form.addEventListener("submit", function(e){

    e.preventDefault();

    let email = document.querySelector('input[type="email"]').value;

    let password = document.querySelectorAll('input[type="password"]')[0].value;

    let confirmPassword = document.querySelectorAll('input[type="password"]')[1].value;


    if(password !== confirmPassword){
        alert("Password does not match");
        return;
    }


    createUserWithEmailAndPassword(auth, email, password)

    .then(() => {

        alert("✅ Account Created Successfully!");

        window.location.href="login.html";

    })

    .catch((error)=>{

        alert(error.message);

    });

});