(function () {
  var root = document.documentElement;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- App-bar hairline on scroll ---- */
  var bar = document.getElementById('appbar');
  var onScroll = function () { bar.classList.toggle('is-stuck', window.scrollY > 4); };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* ---- Footer year + last-updated ---- */
  var y = document.getElementById('year'); if (y) y.textContent = new Date().getFullYear();
  var upd = document.getElementById('updated');
  if (upd) {
    try {
      upd.textContent = new Date(document.lastModified).toLocaleDateString('en-NZ',
        { year: 'numeric', month: 'short', day: 'numeric' });
    } catch (e) { upd.textContent = new Date().getFullYear(); }
  }

  /* ---- Theme toggle: system -> light -> dark ---- */
  var toggle = document.getElementById('themeToggle');
  var order = ['auto', 'light', 'dark'];
  function label(mode) {
    return 'Theme: ' + (mode === 'auto' ? 'system' : mode) + ' — click to change';
  }
  if (toggle) {
    toggle.setAttribute('aria-label', label(root.getAttribute('data-color-mode') || 'auto'));
    toggle.addEventListener('click', function () {
      var cur = root.getAttribute('data-color-mode') || 'auto';
      var next = order[(order.indexOf(cur) + 1) % order.length];
      root.setAttribute('data-color-mode', next);
      try {
        if (next === 'auto') localStorage.removeItem('theme');
        else localStorage.setItem('theme', next);
      } catch (e) {}
      toggle.setAttribute('aria-label', label(next));
    });
  }

  /* ---- Scroll reveal ---- */
  function showAll(els) { els.forEach(function (el) { el.classList.add('is-visible'); }); }
  var reveals = [].slice.call(document.querySelectorAll('.reveal'));
  var io = null;
  if (reduce || !('IntersectionObserver' in window)) {
    showAll(reveals);
  } else {
    io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('is-visible'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    reveals.forEach(function (el) { io.observe(el); });
  }

  /* ---- Count-up stats (animate on first reveal) ---- */
  function countUp(el) {
    if (el.getAttribute('data-counted') === '1') return;
    el.setAttribute('data-counted', '1');
    var target = parseFloat(el.getAttribute('data-count')) || 0;
    var suffix = el.getAttribute('data-suffix') || '';
    if (reduce) { el.textContent = target + suffix; return; }
    var dur = 1200, start = null;
    function step(ts) {
      if (!start) start = ts;
      var p = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(target * eased) + suffix;
      if (p < 1) requestAnimationFrame(step);
      else el.textContent = target + suffix;
    }
    requestAnimationFrame(step);
  }
  var counters = [].slice.call(document.querySelectorAll('[data-count]'));
  if (reduce || !('IntersectionObserver' in window)) {
    counters.forEach(countUp);
  } else {
    var cio = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { countUp(e.target); cio.unobserve(e.target); }
      });
    }, { threshold: 0.6 });
    counters.forEach(function (el) { cio.observe(el); });
  }

  /* ---- Expandable role details ---- */
  function setRoleExpanded(role, open) {
    if (!role) return;
    role.classList.toggle('is-collapsed', !open);
    var btn = role.querySelector('.rx-role__toggle');
    if (btn) btn.setAttribute('aria-expanded', open ? 'true' : 'false');
  }
  [].slice.call(document.querySelectorAll('.rx-role__toggle')).forEach(function (btn) {
    btn.addEventListener('click', function () {
      var role = btn.closest('.rx-role');
      setRoleExpanded(role, btn.getAttribute('aria-expanded') !== 'true');
    });
  });

  /* ---- Interactive career timeline (scrollspy + jump-to, per language) ---- */
  var timelineApis = [];
  function initTimeline(scope) {
    var timeline = scope.querySelector('.rx-timeline');
    if (!timeline) return null;
    var scroller = timeline.querySelector('.rx-timeline__scroll');
    var nodes = [].slice.call(timeline.querySelectorAll('.rx-timeline__node'));
    var roles = nodes.map(function (n) { return document.getElementById(n.getAttribute('data-target')); });
    var current = -1;

    function setActive(idx) {
      if (idx < 0 || idx === current) return;
      current = idx;
      nodes.forEach(function (n, i) {
        var on = i === idx;
        n.classList.toggle('is-active', on);
        if (on) n.setAttribute('aria-current', 'step'); else n.removeAttribute('aria-current');
      });
      roles.forEach(function (r, i) { if (r) r.classList.toggle('is-active', i === idx); });
      if (scroller && scroller.scrollWidth > scroller.clientWidth + 4) {
        var node = nodes[idx];
        scroller.scrollTo({
          left: node.offsetLeft - (scroller.clientWidth - node.offsetWidth) / 2,
          behavior: reduce ? 'auto' : 'smooth'
        });
      }
    }

    function update() {
      if (scope.offsetParent === null) return; /* hidden language — skip */
      var bar = document.getElementById('appbar');
      var line = (bar ? bar.offsetHeight : 56) + 96;
      var best = null, bestTop = -Infinity, below = null, belowTop = Infinity;
      roles.forEach(function (r) {
        if (!r) return;
        var top = r.getBoundingClientRect().top;
        if (top <= line) { if (top > bestTop) { bestTop = top; best = r; } }
        else { if (top < belowTop) { belowTop = top; below = r; } }
      });
      var idx = roles.indexOf(best || below);
      if (idx >= 0) setActive(idx);
    }

    nodes.forEach(function (n, i) {
      n.addEventListener('click', function () {
        var r = roles[i];
        if (!r) return;
        setRoleExpanded(r, true);
        setActive(i);
        try { r.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' }); }
        catch (e) { r.scrollIntoView(); }
        try { r.focus({ preventScroll: true }); } catch (e) {}
      });
    });

    /* Roving arrow-key navigation between milestones */
    timeline.addEventListener('keydown', function (e) {
      var i = nodes.indexOf(document.activeElement);
      if (i === -1) return;
      var to = -1;
      if (e.key === 'ArrowRight' || e.key === 'ArrowDown') to = Math.min(i + 1, nodes.length - 1);
      else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') to = Math.max(i - 1, 0);
      else if (e.key === 'Home') to = 0;
      else if (e.key === 'End') to = nodes.length - 1;
      if (to !== -1) { e.preventDefault(); nodes[to].focus(); }
    });

    return { update: update };
  }
  [].slice.call(document.querySelectorAll('.lang-en, .lang-zh')).forEach(function (scope) {
    var api = initTimeline(scope);
    if (api) timelineApis.push(api);
  });
  var rxTicking = false;
  function rxSpy() { rxTicking = false; timelineApis.forEach(function (a) { a.update(); }); }
  function rxScroll() { if (!rxTicking) { rxTicking = true; requestAnimationFrame(rxSpy); } }
  if (timelineApis.length) {
    window.addEventListener('scroll', rxScroll, { passive: true });
    window.addEventListener('resize', rxScroll, { passive: true });
    rxSpy();
  }

  /* ---- Language toggle (EN / 中文) ---- */
  var wrap = document.getElementById('wrap');
  var langButtons = [].slice.call(document.querySelectorAll('.segmented button'));
  function setLang(lang) {
    wrap.setAttribute('data-lang', lang);
    root.lang = (lang === 'zh' ? 'zh' : 'en');
    langButtons.forEach(function (b) {
      b.setAttribute('aria-pressed', b.getAttribute('data-lang') === lang ? 'true' : 'false');
    });
    /* guarantee revealed blocks in the now-visible language are shown */
    var active = wrap.querySelector(lang === 'zh' ? '.lang-zh' : '.lang-en');
    if (active) showAll([].slice.call(active.querySelectorAll('.reveal')));
    /* refresh the timeline's active milestone for the now-visible language */
    if (typeof rxSpy === 'function') rxSpy();
  }
  langButtons.forEach(function (b) {
    b.addEventListener('click', function () { setLang(b.getAttribute('data-lang')); });
  });

  /* ---- Print / Save as PDF ---- */
  [].slice.call(document.querySelectorAll('[data-print]')).forEach(function (btn) {
    btn.addEventListener('click', function () { window.print(); });
  });

  /* ---- Copy email + toast ---- */
  var toast = document.getElementById('toast');
  var toastMsg = document.getElementById('toastMsg');
  var toastTimer;
  function showToast(msg) {
    if (!toast) return;
    toastMsg.textContent = msg;
    toast.classList.add('is-shown');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toast.classList.remove('is-shown'); }, 2200);
  }
  var emailLink = document.getElementById('emailLink');
  if (emailLink && navigator.clipboard && navigator.clipboard.writeText) {
    emailLink.addEventListener('click', function (ev) {
      ev.preventDefault();
      navigator.clipboard.writeText(emailLink.getAttribute('data-email')).then(function () {
        showToast('Email copied to clipboard');
      }).catch(function () {
        window.location.href = emailLink.getAttribute('href');
      });
    });
  }
})();
