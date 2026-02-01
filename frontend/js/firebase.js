import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getAuth, signInAnonymously } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

const firebaseConfig = {
    apiKey: "AIzaSyDC0zepbZP9uOd8uHPLMr3-1nKjaelwtu4",
    authDomain: "about-nine-prototype-46a2c.firebaseapp.com",
    databaseURL: "https://about-nine-prototype-46a2c-default-rtdb.asia-southeast1.firebasedatabase.app",
    projectId: "about-nine-prototype-46a2c",
    storageBucket: "about-nine-prototype-46a2c.firebasestorage.app",
    messagingSenderId: "746184089802",
    appId: "1:746184089802:web:741d74b2cb1f5fe4231433"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const db = getFirestore(app);

signInAnonymously(auth);