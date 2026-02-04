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

function initPresence() {

  const userId =
    JSON.parse(localStorage.getItem("user_id"));

  if (!userId) return;


  const presenceRef =
    ref(rtdb, "presence/" + userId);

  const connectedRef =
    ref(rtdb, ".info/connected");


  onValue(connectedRef, (snap) => {

    if (!snap.val()) return;


    /* ---------- disconnect → offline ---------- */

    onDisconnect(presenceRef).set({
      online: false,
      updated_at: Date.now()
    });


    /* ---------- connected → online ---------- */

    set(presenceRef, {
      online: true,
      updated_at: Date.now()
    });

    console.log("presence connected");
  });
}


/* =========================
   Run
========================= */

initPresence();
