(function () {
  'use strict';

  var root = document.documentElement;
  var themeOrder = ['auto', 'light', 'dark'];
  var reduceMotion = window.matchMedia
    && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function setTheme(mode, persist) {
    root.setAttribute('data-color-mode', mode);
    var label = document.querySelector('[data-theme-label]');
    if (label) label.textContent = mode;
    var control = document.querySelector('[data-theme-control]');
    if (control) {
      control.setAttribute(
        'aria-label',
        'Theme: ' + (mode === 'auto' ? 'system' : mode) + ' — activate to change'
      );
    }
    if (!persist) return;
    try {
      if (mode === 'auto') localStorage.removeItem('theme');
      else localStorage.setItem('theme', mode);
    } catch (error) {
      root.setAttribute('data-theme-storage', 'unavailable');
    }
  }

  function initThemeControl() {
    var control = document.querySelector('[data-theme-control]');
    if (!control) return;
    setTheme(root.getAttribute('data-color-mode') || 'auto', false);
    control.addEventListener('click', function () {
      var current = root.getAttribute('data-color-mode') || 'auto';
      setTheme(themeOrder[(themeOrder.indexOf(current) + 1) % themeOrder.length], true);
    });
  }

  function setLanguage(language, persist) {
    root.setAttribute('data-language', language);
    root.lang = language === 'zh' ? 'zh' : 'en';
    [].slice.call(document.querySelectorAll('[data-language-panel]')).forEach(function (panel) {
      var panelLanguage = panel.getAttribute('data-language-panel');
      panel.hidden = panelLanguage !== language;
    });
    [].slice.call(document.querySelectorAll('[data-language-control] [data-lang]')).forEach(function (button) {
      button.setAttribute(
        'aria-pressed',
        button.getAttribute('data-lang') === language ? 'true' : 'false'
      );
    });
    if (!persist) return;
    try {
      localStorage.setItem('resume-language', language);
    } catch (error) {
      root.setAttribute('data-language-storage', 'unavailable');
    }
  }

  function initLanguageControl() {
    var initialLanguage = root.getAttribute('data-language') === 'zh' ? 'zh' : 'en';
    setLanguage(initialLanguage, false);
    [].slice.call(document.querySelectorAll('[data-language-control] [data-lang]')).forEach(function (button) {
      button.addEventListener('click', function () {
        setLanguage(button.getAttribute('data-lang') === 'zh' ? 'zh' : 'en', true);
      });
    });
  }

  function setDisclosure(button, panel, open, immediate) {
    button.setAttribute('aria-expanded', open ? 'true' : 'false');
    button.textContent = open
      ? button.getAttribute('data-close-label')
      : button.getAttribute('data-open-label');
    if (open) {
      panel.hidden = false;
      panel.setAttribute('data-transition-state', 'opening');
      if (immediate || reduceMotion) {
        panel.setAttribute('data-open', 'true');
        panel.removeAttribute('data-transition-state');
        return;
      }
      requestAnimationFrame(function () {
        panel.setAttribute('data-open', 'true');
        panel.removeAttribute('data-transition-state');
      });
      return;
    }

    panel.removeAttribute('data-open');
    panel.setAttribute('data-transition-state', 'closing');
    if (immediate || reduceMotion) {
      panel.hidden = true;
      panel.removeAttribute('data-transition-state');
      return;
    }

    function finishClose(event) {
      if (event.target !== panel) return;
      panel.removeEventListener('transitionend', finishClose);
      if (panel.getAttribute('data-transition-state') === 'closing') {
        panel.hidden = true;
        panel.removeAttribute('data-transition-state');
      }
    }
    panel.addEventListener('transitionend', finishClose);
  }

  function initExperienceDisclosures() {
    var disclosures = [].slice.call(document.querySelectorAll('[data-disclosure]'));
    if (!disclosures.length) return;
    root.classList.add('has-disclosures');
    disclosures.forEach(function (disclosure) {
      var button = disclosure.querySelector('[data-disclosure-control]');
      var panel = disclosure.querySelector('[data-disclosure-panel]');
      if (!button || !panel) return;
      setDisclosure(button, panel, false, true);
      button.addEventListener('click', function () {
        setDisclosure(
          button,
          panel,
          button.getAttribute('aria-expanded') !== 'true',
          false
        );
      });
    });
  }

  function initPrintControls() {
    var printButtons = [].slice.call(document.querySelectorAll('[data-print]'));
    var disclosures = [].slice.call(document.querySelectorAll('[data-disclosure]'));
    var previousStates = [];

    printButtons.forEach(function (button) {
      button.addEventListener('click', function () {
        if (typeof window.print === 'function') window.print();
      });
    });

    window.addEventListener('beforeprint', function () {
      previousStates = disclosures.map(function (disclosure) {
        var button = disclosure.querySelector('[data-disclosure-control]');
        var panel = disclosure.querySelector('[data-disclosure-panel]');
        var open = button && button.getAttribute('aria-expanded') === 'true';
        if (button && panel) setDisclosure(button, panel, true, true);
        return { button: button, panel: panel, open: open };
      });
    });

    window.addEventListener('afterprint', function () {
      previousStates.forEach(function (state) {
        if (state.button && state.panel) {
          setDisclosure(state.button, state.panel, state.open, true);
        }
      });
    });
  }

  function initEmailCopy() {
    var links = [].slice.call(document.querySelectorAll('[data-email]'));
    var toast = document.querySelector('[data-toast]');
    var message = toast && toast.querySelector('[data-toast-message]');
    var timer;

    links.forEach(function (link) {
      link.addEventListener('click', function (event) {
        if (!navigator.clipboard || !navigator.clipboard.writeText) return;
        event.preventDefault();
        navigator.clipboard.writeText(link.getAttribute('data-email')).then(function () {
          if (!toast || !message) return;
          message.textContent = root.lang === 'zh' ? '邮箱已复制' : 'Email copied to clipboard';
          toast.classList.add('is-visible');
          clearTimeout(timer);
          timer = setTimeout(function () {
            toast.classList.remove('is-visible');
          }, 2200);
        }).catch(function () {
          window.location.href = link.getAttribute('href');
        });
      });
    });
  }

  function initFooterMetadata() {
    var year = document.getElementById('year');
    var updated = document.getElementById('updated');
    if (year) year.textContent = new Date().getFullYear();
    if (!updated) return;
    var date = new Date(document.lastModified);
    updated.textContent = Number.isNaN(date.getTime())
      ? String(new Date().getFullYear())
      : date.toLocaleDateString(root.lang === 'zh' ? 'zh-CN' : 'en-NZ', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        });
  }

  initThemeControl();
  initLanguageControl();
  initExperienceDisclosures();
  initPrintControls();
  initEmailCopy();
  initFooterMetadata();
})();
