/* ==========================================================================
   Theme toggle
   The <html data-theme> attribute is applied by a tiny inline script in each
   page's <head> (before first paint, so there is no light flash). This file
   only wires up the button and remembers the reader's choice.

   Loaded with `defer`, so the DOM is ready when it runs.
   ========================================================================== */
(function () {
  'use strict';

  var KEY = 'tml-theme';
  var root = document.documentElement;
  var btn = document.querySelector('.theme-toggle');
  var mq = window.matchMedia('(prefers-color-scheme: dark)');

  function stored() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }

  function syncLabel() {
    if (!btn) return;
    var label = root.getAttribute('data-theme') === 'dark'
      ? 'Switch to light theme'
      : 'Switch to dark theme';
    btn.setAttribute('aria-label', label);
    btn.setAttribute('title', label);
  }

  function set(theme, persist) {
    // cross-fade colours for a beat, then drop the helper class again
    var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!reduce) root.classList.add('theme-transitioning');

    root.setAttribute('data-theme', theme);
    if (persist) {
      try { localStorage.setItem(KEY, theme); } catch (e) {}
    }
    syncLabel();

    window.setTimeout(function () {
      root.classList.remove('theme-transitioning');
    }, 240);
  }

  syncLabel();

  if (btn) {
    btn.addEventListener('click', function () {
      set(root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark', true);
    });
  }

  // follow the OS only while the reader has not picked a side
  function onSystemChange() {
    if (!stored()) set(mq.matches ? 'dark' : 'light', false);
  }
  if (mq.addEventListener) mq.addEventListener('change', onSystemChange);
  else if (mq.addListener) mq.addListener(onSystemChange);
})();
