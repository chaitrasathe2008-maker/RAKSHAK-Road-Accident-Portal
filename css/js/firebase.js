// Firebase Import
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";


// Firebase Configuration

const firebaseConfig = {
  apiKey: "AIzaSyCzjAWb2du0Qsg16UBpqweZ_s-V-mYZtk4",
  authDomain: "rakshak-road-accident-portal.firebaseapp.com",
  projectId: "rakshak-road-accident-portal",
  storageBucket: "rakshak-road-accident-portal.firebasestorage.app",
  messagingSenderId: "720208220767",
  appId: "1:720208220767:web:3ea0cefa036e67bf6701ea"
};


// Initialize Firebase

const app = initializeApp(firebaseConfig);

const auth = getAuth(app);

export { auth };