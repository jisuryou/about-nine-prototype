import {
  rtdb,
  ref,
  set,
  onDisconnect,
  onValue
} from "/js/firebase.js";


/* =========================
   Presence Init
========================= */

let presenceInitialized = false;
let presenceRetryTimer = null;

function resolveUserId() {
  let userId = null;
  try {
    const raw = localStorage.getItem("user_id");
    if (raw) {
      try {
        userId = JSON.parse(raw);
      } catch {
        userId = raw;
      }
    }
  } catch {}
  return userId;
}

function initPresence() {
  if (presenceInitialized) return;
  const userId = resolveUserId();
  if (!userId) return;
  presenceInitialized = true;
  if (presenceRetryTimer) clearInterval(presenceRetryTimer);
  presenceRetryTimer = null;

  const presenceRef = ref(rtdb, "presence/" + userId);
  const connectedRef = ref(rtdb, ".info/connected");
  let heartbeatTimer = null;

  const setOnline = () =>
    set(presenceRef, { online: true, updated_at: Date.now() }).catch((e) => {
      console.error("presence setOnline failed:", e);
    });
  const setOffline = () =>
    set(presenceRef, { online: false, updated_at: Date.now() }).catch((e) => {
      console.error("presence setOffline failed:", e);
    });

  const startHeartbeat = () => {
    setOnline();
    if (heartbeatTimer) clearInterval(heartbeatTimer);
    heartbeatTimer = setInterval(() => {
      setOnline();
    }, 15000);
  };

  // Try to mark online immediately (queued if not connected yet)
  startHeartbeat();

  onValue(connectedRef, (snap) => {
    if (!snap.val()) return;

    onDisconnect(presenceRef).set({
      online: false,
      updated_at: Date.now()
    });

    startHeartbeat();

    console.log("presence connected");
  });

  // Mobile browsers may pause timers in background; re-assert on resume.
  document.addEventListener("visibilitychange", () => {
    try {
      if (document.hidden) {
        setOffline();
      } else {
        startHeartbeat();
      }
    } catch {}
  });

  window.addEventListener("focus", startHeartbeat);
  window.addEventListener("blur", () => {
    try {
      setOffline();
    } catch {}
  });

  window.addEventListener("pageshow", startHeartbeat);
  window.addEventListener("pagehide", () => {
    try {
      setOffline();
    } catch {}
  });

  window.addEventListener("beforeunload", () => {
    try {
      setOffline();
    } catch {}
  });
}


/* =========================
   Run
========================= */

initPresence();
if (!presenceInitialized) {
  presenceRetryTimer = setInterval(() => {
    if (!presenceInitialized) initPresence();
  }, 1000);
}
