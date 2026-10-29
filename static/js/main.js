/**
 * NestKerala Master Client JavaScript
 * Interactive controls for filters, favorites, comparison, modals, and sharing
 */

document.addEventListener('DOMContentLoaded', () => {
  initMobileMenu();
  initFavoriteButtons();
  initCompareButtons();
  initShareButtons();
  initModals();
});

// 1. Mobile Menu Drawer
function initMobileMenu() {
  const menuBtn = document.getElementById('mobileMenuBtn');
  const drawer = document.getElementById('mobileDrawer');
  const overlay = document.getElementById('drawerOverlay');
  const closeBtn = document.getElementById('drawerCloseBtn');

  if (!menuBtn || !drawer || !overlay) return;

  const openDrawer = () => {
    drawer.classList.add('is-open');
    overlay.classList.add('is-open');
    document.body.style.overflow = 'hidden';
  };

  const closeDrawer = () => {
    drawer.classList.remove('is-open');
    overlay.classList.remove('is-open');
    document.body.style.overflow = '';
  };

  menuBtn.addEventListener('click', openDrawer);
  overlay.addEventListener('click', closeDrawer);
  if (closeBtn) closeBtn.addEventListener('click', closeDrawer);
}

// 2. AJAX Favorites Handler
function initFavoriteButtons() {
  document.querySelectorAll('.card-action-fav, .btn-fav-toggle').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const propId = btn.dataset.propId;
      if (!propId) return;

      try {
        const response = await fetch(`/favorite/toggle/${propId}`, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
          }
        });
        const data = await response.json();
        
        if (data.status === 'added') {
          btn.classList.add('is-active');
          showToast('Added to Saved Homes', 'success');
        } else {
          btn.classList.remove('is-active');
          showToast('Removed from Saved Homes', 'info');
        }

        // Update badge count if present
        const badge = document.getElementById('favCountBadge');
        if (badge) {
          let count = parseInt(badge.textContent) || 0;
          count = data.status === 'added' ? count + 1 : Math.max(0, count - 1);
          badge.textContent = count;
        }
      } catch (err) {
        console.error('Error toggling favorite:', err);
      }
    });
  });
}

// 3. Comparison Handler
function initCompareButtons() {
  document.querySelectorAll('.card-action-compare, .btn-compare-toggle').forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.preventDefault();
      e.stopPropagation();
      const propId = btn.dataset.propId;
      if (!propId) return;

      try {
        const response = await fetch(`/compare/toggle/${propId}`, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
          }
        });
        const data = await response.json();

        if (response.status === 400) {
          showToast(data.message, 'warning');
          return;
        }

        if (data.status === 'added') {
          btn.classList.add('is-active');
          showToast('Property added to comparison', 'success');
        } else {
          btn.classList.remove('is-active');
          showToast('Removed from comparison', 'info');
        }

        // Update badge
        const badge = document.getElementById('compareCountBadge');
        if (badge) badge.textContent = data.count;

        // Update sticky floating bar
        const stickyBar = document.getElementById('stickyCompareBar');
        const barCount = document.getElementById('compareBarCount');
        if (stickyBar && barCount) {
          barCount.textContent = data.count;
          if (data.count > 0) {
            stickyBar.classList.add('is-active');
          } else {
            stickyBar.classList.remove('is-active');
          }
        }
      } catch (err) {
        console.error('Error toggling compare:', err);
      }
    });
  });
}

// 4. Share Property Link (Clipboard)
function initShareButtons() {
  document.querySelectorAll('.btn-share-property').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const url = window.location.href;
      navigator.clipboard.writeText(url).then(() => {
        showToast('Property link copied to clipboard!', 'success');
      }).catch(() => {
        showToast('Could not copy link automatically.', 'warning');
      });
    });
  });
}

// 5. Modals Controls
function initModals() {
  // Triggers
  document.querySelectorAll('[data-open-modal]').forEach(trigger => {
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      const modalId = trigger.getAttribute('data-open-modal');
      const modal = document.getElementById(modalId);
      if (modal) {
        modal.classList.add('is-open');
        document.body.style.overflow = 'hidden';
      }
    });
  });

  // Closers
  document.querySelectorAll('.modal-close-btn, .modal-backdrop').forEach(closer => {
    closer.addEventListener('click', (e) => {
      if (e.target === closer || closer.classList.contains('modal-close-btn')) {
        const modal = closer.closest('.modal-backdrop');
        if (modal) {
          modal.classList.remove('is-open');
          document.body.style.overflow = '';
        }
      }
    });
  });
}

// 6. Toast Notification Dispenser
function showToast(message, type = 'info') {
  let toastContainer = document.getElementById('toastContainer');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'toastContainer';
    toastContainer.style.cssText = `
      position: fixed;
      bottom: 24px;
      right: 24px;
      z-index: 3000;
      display: flex;
      flex-direction: column;
      gap: 10px;
    `;
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement('div');
  const bg = type === 'success' ? '#0F4C3A' : (type === 'warning' ? '#D97706' : '#1E293B');
  toast.style.cssText = `
    background: ${bg};
    color: white;
    padding: 12px 20px;
    border-radius: 8px;
    font-size: 0.9rem;
    font-weight: 600;
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
    display: flex;
    align-items: center;
    gap: 10px;
    animation: toastSlide 0.25s ease-out;
  `;
  toast.innerHTML = `<span>${message}</span>`;
  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3200);
}
