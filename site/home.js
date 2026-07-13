(function () {
  'use strict';

  var root = document.documentElement;
  var reduceMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var toastTimer;

  function initThemeControl() {
    var control = document.querySelector('[data-theme-control]');
    var label = document.querySelector('[data-theme-label]');
    var order = ['auto', 'light', 'dark'];

    if (!control || !label) return;

    function currentMode() {
      var mode = root.getAttribute('data-color-mode');
      return order.indexOf(mode) === -1 ? 'auto' : mode;
    }

    function render(mode) {
      label.textContent = mode;
      control.setAttribute('aria-label', 'Theme: ' + mode + '. Activate to change.');
    }

    render(currentMode());

    control.addEventListener('click', function () {
      var mode = currentMode();
      var next = order[(order.indexOf(mode) + 1) % order.length];
      root.setAttribute('data-color-mode', next);

      try {
        if (next === 'auto') {
          localStorage.removeItem('theme');
        } else {
          localStorage.setItem('theme', next);
        }
      } catch (error) {
        root.setAttribute('data-theme-storage', 'unavailable');
      }

      render(next);
    });
  }

  function initEntrySequence() {
    if (reduceMotion) {
      root.classList.add('entry-complete');
      return;
    }

    root.classList.add('entry-running');
    window.setTimeout(function () {
      root.classList.remove('entry-running');
      root.classList.add('entry-complete');
    }, 1400);
  }

  function initScrollScenes() {
    var reveals = Array.prototype.slice.call(
      document.querySelectorAll('[data-reveal]')
    );
    var route = document.querySelector('[data-route]');

    if (!reduceMotion && 'IntersectionObserver' in window && reveals.length) {
      root.classList.add('has-reveal');

      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        });
      }, {
        threshold: 0.16,
        rootMargin: '0px 0px -10% 0px'
      });

      reveals.forEach(function (element) {
        observer.observe(element);
      });
    }

    if (route) {
      if (reduceMotion || !('IntersectionObserver' in window)) {
        route.classList.add('is-visible');
      } else {
        var routeObserver = new IntersectionObserver(function (entries) {
          entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            entry.target.classList.add('is-visible');
            routeObserver.unobserve(entry.target);
          });
        }, { threshold: 0.4 });
        routeObserver.observe(route);
      }
    }

    if (reduceMotion || !window.requestAnimationFrame) return;

    var framePending = false;

    function updateProgress() {
      var scrollable = document.documentElement.scrollHeight - window.innerHeight;
      var progress = scrollable > 0 ? window.scrollY / scrollable : 0;
      var clamped = Math.max(0, Math.min(1, progress));
      root.style.setProperty('--page-progress', (clamped * 100) + '%');
      root.style.setProperty('--grid-offset', (-clamped * 120) + 'px');
      framePending = false;
    }

    function requestProgressUpdate() {
      if (framePending) return;
      framePending = true;
      window.requestAnimationFrame(updateProgress);
    }

    updateProgress();
    window.addEventListener('scroll', requestProgressUpdate, { passive: true });
    window.addEventListener('resize', requestProgressUpdate);
  }

  function showToast(message) {
    var toast = document.querySelector('[data-toast]');
    var toastMessage = document.querySelector('[data-toast-message]');

    if (!toast || !toastMessage) return;

    toastMessage.textContent = message;
    toast.classList.add('is-visible');
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(function () {
      toast.classList.remove('is-visible');
    }, 2200);
  }

  function initEmailCopy() {
    var emailLink = document.querySelector('[data-email]');
    if (!emailLink) return;

    emailLink.addEventListener('click', function (event) {
      if (!navigator.clipboard || !navigator.clipboard.writeText) return;

      event.preventDefault();
      navigator.clipboard.writeText(emailLink.getAttribute('data-email'))
        .then(function () {
          showToast('Email copied to clipboard');
        })
        .catch(function () {
          window.location.assign(emailLink.getAttribute('href'));
        });
    });
  }

  function initFooterMetadata() {
    var year = document.getElementById('year');
    var updated = document.getElementById('updated');

    if (year) {
      year.textContent = String(new Date().getFullYear());
    }

    if (updated) {
      var modified = new Date(document.lastModified);
      if (Number.isNaN(modified.getTime())) {
        updated.textContent = 'unknown';
      } else {
        updated.textContent = modified.toLocaleDateString('en-NZ', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        });
      }
    }
  }

  initThemeControl();
  initEntrySequence();
  initScrollScenes();
  initEmailCopy();
  initFooterMetadata();
})();
