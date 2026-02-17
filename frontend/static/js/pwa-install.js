// PWA Installation and Management
(function() {
  'use strict';
  
  let deferredPrompt;
  
  // Register service worker
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/service-worker.js')
        .then(registration => {
          console.log('ServiceWorker registered:', registration.scope);
          
          // Check for updates every 24 hours
          setInterval(() => {
            registration.update();
          }, 24 * 60 * 60 * 1000);
        })
        .catch(error => {
          console.error('ServiceWorker registration failed:', error);
        });
    });
  }
  
  // Listen for install prompt
  window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent default mini-infobar
    e.preventDefault();
    deferredPrompt = e;
    
    // Show custom install button
    showInstallPromotion();
  });
  
  // Show install promotion banner
  function showInstallPromotion() {
    // Don't show if already installed or dismissed recently
    if (window.matchMedia('(display-mode: standalone)').matches) {
      return;
    }
    
    const dismissed = localStorage.getItem('pwa-install-dismissed');
    if (dismissed) {
      const dismissedDate = new Date(dismissed);
      const daysSince = (Date.now() - dismissedDate) / (1000 * 60 * 60 * 24);
      if (daysSince < 7) return; // Don't show for 7 days after dismissal
    }
    
    // Create install banner
    const banner = document.createElement('div');
    banner.id = 'pwa-install-banner';
    banner.className = 'fixed bottom-0 left-0 right-0 bg-primary-600 text-white p-4 shadow-lg z-50 transform transition-transform duration-300 translate-y-full';
    banner.innerHTML = `
      <div class="container mx-auto flex items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <svg class="w-10 h-10 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path d="M3 12v3c0 1.657 3.134 3 7 3s7-1.343 7-3v-3c0 1.657-3.134 3-7 3s-7-1.343-7-3z"/>
            <path d="M3 7v3c0 1.657 3.134 3 7 3s7-1.343 7-3V7c0 1.657-3.134 3-7 3S3 8.657 3 7z"/>
            <path d="M17 5c0 1.657-3.134 3-7 3S3 6.657 3 5s3.134-3 7-3 7 1.343 7 3z"/>
          </svg>
          <div>
            <div class="font-semibold">Fikrly ilovasini o'rnatish</div>
            <div class="text-sm opacity-90">Tezroq kirish va offline ishlash</div>
          </div>
        </div>
        <div class="flex items-center gap-2 flex-shrink-0">
          <button id="pwa-install-btn" class="bg-elevated text-primary-600 px-4 py-2 rounded-lg font-medium hover:bg-secondary transition-colors">
            O'rnatish
          </button>
          <button id="pwa-dismiss-btn" class="text-white opacity-75 hover:opacity-100 p-2">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      </div>
    `;
    
    document.body.appendChild(banner);
    
    // Animate in
    setTimeout(() => {
      banner.classList.remove('translate-y-full');
    }, 100);
    
    // Install button click
    document.getElementById('pwa-install-btn').addEventListener('click', async () => {
      if (!deferredPrompt) return;
      
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      
      if (outcome === 'accepted') {
        console.log('PWA installed');
        banner.remove();
      }
      
      deferredPrompt = null;
    });
    
    // Dismiss button click
    document.getElementById('pwa-dismiss-btn').addEventListener('click', () => {
      banner.classList.add('translate-y-full');
      setTimeout(() => banner.remove(), 300);
      localStorage.setItem('pwa-install-dismissed', new Date().toISOString());
    });
  }
  
  // Track installation
  window.addEventListener('appinstalled', () => {
    console.log('PWA was installed');
    deferredPrompt = null;
    
    // Remove install banner if visible
    const banner = document.getElementById('pwa-install-banner');
    if (banner) banner.remove();
    
    // Track installation event
    if (window.gtag) {
      gtag('event', 'pwa_install', {
        event_category: 'engagement'
      });
    }
  });
  
  // Request notification permission
  function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission().then(permission => {
        if (permission === 'granted') {
          subscribeUserToPush();
        }
      });
    }
  }
  
  // Subscribe to push notifications
  async function subscribeUserToPush() {
    try {
      const registration = await navigator.serviceWorker.ready;
      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(window.VAPID_PUBLIC_KEY || '')
      });
      
      // Send subscription to server
      await fetch('/api/push-subscribe/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(subscription)
      });
      
      console.log('Push subscription successful');
    } catch (error) {
      console.error('Push subscription failed:', error);
    }
  }
  
  // Helper to convert VAPID key
  function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }
  
  // Get CSRF token
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  
  // Show notification permission prompt after user engagement
  let engagementCount = 0;
  document.addEventListener('click', () => {
    engagementCount++;
    if (engagementCount === 3 && 'Notification' in window && Notification.permission === 'default') {
      setTimeout(requestNotificationPermission, 2000);
    }
  }, { once: true });
  
  // Detect if app is running in standalone mode
  if (window.matchMedia('(display-mode: standalone)').matches) {
    document.documentElement.classList.add('pwa-standalone');
  }
  
})();
