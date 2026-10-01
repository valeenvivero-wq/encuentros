importScripts("https://www.gstatic.com/firebasejs/10.13.2/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.13.2/firebase-messaging-compat.js");

firebase.initializeApp({
  apiKey: "AIzaSyCZI-gW7tOPiz7jEFF1KTLejQcJM9jncGM",
  authDomain: "encuentros-e9cdb.firebaseapp.com",
  projectId: "encuentros-e9cdb",
  storageBucket: "encuentros-e9cdb.firebasestorage.app",
  messagingSenderId: "56539390412",
  appId: "1:56539390412:web:3e3a075d48811e07c67d69"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage(function(payload) {
  const notificationTitle = payload.notification?.title || "Encuentros";
  const notificationOptions = {
    body: payload.notification?.body || "Tenés una nueva actualización.",
    icon: "/favicon.png"
  };

  self.registration.showNotification(
    notificationTitle,
    notificationOptions
  );
});
