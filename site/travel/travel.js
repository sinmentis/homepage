(function () {
  'use strict';

  var routeMaps = {
    'route-a': {
      src: '/travel/assets/route-a.svg',
      alt: '路线 A：伊宁分别往返大西沟和唐布拉',
      caption: '路线 A 把长途拆开，但会两次回到伊宁。'
    },
    'route-b': {
      src: '/travel/assets/route-b.svg',
      alt: '路线 B：伊宁到大西沟，再横穿至唐布拉后返回伊宁',
      caption: '大西沟到唐布拉约 359 公里，会形成最累的横穿日。'
    },
    'route-c': {
      src: '/travel/assets/route-c.svg',
      alt: '路线 C：唐布拉为主线，大西沟为条件支线',
      caption: '大西沟只在秋色确认后增加，主线保持唐布拉深住。'
    }
  };

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

  function initRouteControls() {
    var controls = Array.from(document.querySelectorAll('[data-route-control]'));
    var map = document.querySelector('[data-route-map]');
    var caption = document.querySelector('[data-route-map-caption]');
    if (!controls.length || !map || !caption) {
      return;
    }

    function selectRoute(routeId, moveFocus) {
      var route = routeMaps[routeId];
      if (!route) {
        return;
      }
      controls.forEach(function (control) {
        var selected = control.getAttribute('data-route-control') === routeId;
        control.setAttribute('aria-pressed', selected ? 'true' : 'false');
        control.tabIndex = selected ? 0 : -1;
        if (selected && moveFocus) {
          control.focus();
        }
      });
      map.src = route.src;
      map.alt = route.alt;
      caption.textContent = route.caption;
    }

    controls.forEach(function (control, index) {
      control.addEventListener('click', function () {
        selectRoute(control.getAttribute('data-route-control'), false);
      });
      control.addEventListener('keydown', function (event) {
        var targetIndex = index;
        if (event.key === 'ArrowRight') {
          targetIndex = (index + 1) % controls.length;
        } else if (event.key === 'ArrowLeft') {
          targetIndex = (index - 1 + controls.length) % controls.length;
        } else if (event.key === 'Home') {
          targetIndex = 0;
        } else if (event.key === 'End') {
          targetIndex = controls.length - 1;
        } else {
          return;
        }
        event.preventDefault();
        selectRoute(controls[targetIndex].getAttribute('data-route-control'), true);
      });
    });

    selectRoute('route-a', false);
  }

  function initImageFailureState() {
    document.querySelectorAll('.evidence-grid img').forEach(function (image) {
      image.addEventListener('error', function () {
        image.classList.add('image-failed');
        image.removeAttribute('src');
        image.setAttribute('aria-label', image.alt + '。图片加载失败，请阅读下方文字和来源。');
      });
    });
  }

  initThemeControl();
  initRouteControls();
  initImageFailureState();
})();
