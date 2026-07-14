(function () {
  'use strict';

  function initThemeControl() {
    var root = document.documentElement;
    var button = document.querySelector('[data-theme-control]');
    var label = document.querySelector('[data-theme-label]');
    var modes = ['auto', 'light', 'dark'];
    if (!button || !label) {
      return;
    }

    function currentMode() {
      var value = root.getAttribute('data-color-mode');
      return modes.indexOf(value) === -1 ? 'auto' : value;
    }

    function applyMode(mode) {
      root.setAttribute('data-color-mode', mode);
      label.textContent = mode;
      try {
        if (mode === 'auto') {
          localStorage.removeItem('theme');
        } else {
          localStorage.setItem('theme', mode);
        }
      } catch (error) {
        root.setAttribute('data-theme-storage', 'unavailable');
      }
    }

    label.textContent = currentMode();
    button.addEventListener('click', function () {
      var index = modes.indexOf(currentMode());
      applyMode(modes[(index + 1) % modes.length]);
    });
  }

  function initImageFailureState() {
    document.querySelectorAll('.evidence-grid img').forEach(function (image) {
      function markFailed() {
        image.classList.add('image-failed');
        image.removeAttribute('src');
        image.setAttribute('aria-label', image.alt + '。图片加载失败，请阅读下方文字和来源。');
        // Browsers do not reliably paint alt text inside a broken <img>, so
        // sighted users need a visible note too. figcaption is a normal
        // (non-replaced) element and always renders.
        var figure = image.closest('figure');
        var caption = figure ? figure.querySelector('figcaption') : null;
        if (caption && !caption.querySelector('.image-failed-note')) {
          var note = document.createElement('span');
          note.className = 'image-failed-note';
          note.textContent = '图片加载失败，以下文字仍可参考：';
          caption.insertBefore(note, caption.firstChild);
        }
      }

      image.addEventListener('error', markFailed);
      // Evidence images load eagerly now (no `loading="lazy"`), so a fast
      // same-origin failure can resolve before this deferred script attaches
      // the listener above. Catch that already-missed event by checking the
      // settled state directly.
      if (image.complete && image.naturalWidth === 0 && image.getAttribute('src')) {
        markFailed();
      }
    });
  }

  initThemeControl();
  initImageFailureState();
})();
