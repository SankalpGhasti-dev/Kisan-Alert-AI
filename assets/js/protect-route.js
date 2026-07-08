// protect-route.js
import { auth, onAuthStateChanged, signOut, DEMO_MODE } from './firebase-auth.js';

if (DEMO_MODE) {
    if (localStorage.getItem("demoMode") !== "true") {
        window.location.href = 'index.html';
    }
} else {
    // Protect the route: if not logged in, redirect to login page (/)
    onAuthStateChanged(auth, (user) => {
        if (!user) {
            window.location.href = 'index.html';
        }
    });
}

// Setup logout button if it exists
document.addEventListener('DOMContentLoaded', () => {
    const logoutBtns = document.querySelectorAll('.logout-btn');
    logoutBtns.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            if (DEMO_MODE) {
                localStorage.clear();
                window.location.href = 'index.html';
            } else {
                try {
                    await signOut(auth);
                    // The onAuthStateChanged listener will handle the redirect
                } catch (error) {
                    console.error('Error signing out:', error);
                }
            }
        });
    });
});
