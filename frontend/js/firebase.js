import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import {
  getAuth,
  RecaptchaVerifier,
  signInWithPhoneNumber
} from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";
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


// ========================
// Phone Auth helpers
// ========================

window.initRecaptcha = () => {
  window.recaptchaVerifier = new RecaptchaVerifier(
    "recaptcha-container",
    { size: "invisible" },
    auth
  );
};

window.sendFirebaseOTP = async (phone) => {
  const confirmation = await signInWithPhoneNumber(
    auth,
    phone,
    window.recaptchaVerifier
  );
  window.confirmationResult = confirmation;
};

window.verifyFirebaseOTP = async (code) => {
  const result = await window.confirmationResult.confirm(code);
  return await result.user.getIdToken();
};
