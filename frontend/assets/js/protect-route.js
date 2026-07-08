// protect-route.js
import { auth, onAuthStateChanged, signOut } from './firebase-auth.js';

// Protect the route: if not logged in, redirect to login page (/)
onAuthStateChanged(auth, (user) => {
    if (!user) {
        window.location.href = 'index.html';
    }
});

// Setup logout button if it exists
document.addEventListener('DOMContentLoaded', () => {
    const logoutBtns = document.querySelectorAll('.logout-btn');
    logoutBtns.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            try {
                await signOut(auth);
                // The onAuthStateChanged listener will handle the redirect
            } catch (error) {
                console.error('Error signing out:', error);
            }
        });
    });
});
