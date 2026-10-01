importScripts("https://www.gstatic.com/firebasejs/10.13.2/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.13.2/firebase-messaging-compat.js");

firebase.initializeApp({
  apiKey: "TU_API_KEY",
  authDomain: "TU_AUTH_DOMAIN",
  projectId: "encuentros-e9cdb",
  storageBucket: "TU_STORAGE_BUCKET",
  messagingSenderId: "56539390412",
  appId: "TU_APP_ID"
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
