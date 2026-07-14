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

  function initRouteTabs() {
    var root = document.documentElement;
    var routeIds = ['route-a', 'route-b', 'route-c'];
    var choices = Array.from(document.querySelectorAll('[data-route-choice]'));
    var tabs = Array.from(document.querySelectorAll('[data-route-tab]'));
    var panels = Array.from(document.querySelectorAll('[data-route-panel]'));
    var tabBar = document.querySelector('[data-route-tabs]');
    var backLink = document.querySelector('[data-route-back]');
    var comparisonTitle = document.querySelector('#comparison-title');

    if (
      choices.length !== routeIds.length ||
      tabs.length !== routeIds.length ||
      panels.length !== routeIds.length ||
      !tabBar ||
      !backLink ||
      !comparisonTitle
    ) {
      return;
    }

    function routeFromHash() {
      var value = window.location.hash.replace(/^#/, '');
      var fallbackRoute = value.replace(/-panel$/, '');
      if (routeIds.indexOf(value) !== -1) return value;
      if (routeIds.indexOf(fallbackRoute) !== -1) return fallbackRoute;
      return 'comparison';
    }

    function setTabState(routeId) {
      tabs.forEach(function (tab) {
        var active = tab.getAttribute('data-route-tab') === routeId;
        tab.setAttribute('aria-selected', String(active));
        tab.tabIndex = active ? 0 : -1;
      });
    }

    function activate(routeId, updateHash, focusTab) {
      var next = routeIds.indexOf(routeId) === -1 ? 'comparison' : routeId;
      root.setAttribute('data-active-route', next);
      setTabState(next);

      if (updateHash) {
        var hash = next === 'comparison' ? window.location.pathname + window.location.search : '#' + next;
        history.replaceState(null, '', hash);
      }

      if (focusTab && next !== 'comparison') {
        tabs[routeIds.indexOf(next)].focus();
      }
    }

    choices.forEach(function (choice) {
      choice.addEventListener('click', function (event) {
        event.preventDefault();
        activate(choice.getAttribute('data-route-choice'), true, true);
      });
    });

    tabs.forEach(function (tab, index) {
      tab.addEventListener('click', function () {
        activate(tab.getAttribute('data-route-tab'), true, false);
      });

      tab.addEventListener('keydown', function (event) {
        var nextIndex = index;
        if (event.key === 'ArrowLeft') nextIndex = (index - 1 + tabs.length) % tabs.length;
        if (event.key === 'ArrowRight') nextIndex = (index + 1) % tabs.length;
        if (event.key === 'Home') nextIndex = 0;
        if (event.key === 'End') nextIndex = tabs.length - 1;
        if (nextIndex === index && event.key !== 'Home' && event.key !== 'End') return;
        event.preventDefault();
        activate(tabs[nextIndex].getAttribute('data-route-tab'), true, true);
      });
    });

    backLink.addEventListener('click', function (event) {
      event.preventDefault();
      activate('comparison', true, false);
      comparisonTitle.focus();
    });

    window.addEventListener('hashchange', function () {
      activate(routeFromHash(), /-panel$/.test(window.location.hash), false);
    });

    root.setAttribute('data-route-enhanced', 'true');
    var initialRoute = routeFromHash();
    activate(initialRoute, /-panel$/.test(window.location.hash), false);
  }

  initThemeControl();
  initImageFailureState();
  initRouteTabs();
})();
