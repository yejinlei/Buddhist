// 全站移动端导航 + 触控增强
(function () {
  'use strict';

  // 只在移动端尺寸生效
  if (window.matchMedia('(min-width: 768px)').matches) return;

  // ---- 1. 给所有子页面 nav 添加统一的 class 和汉堡按钮 ----
  document.querySelectorAll('nav.site-nav, nav.bg-ink').forEach(function (nav) {
    if (!nav.classList.contains('site-nav')) nav.classList.add('site-nav');

    // 给品牌链接加 class
    var brandA = nav.querySelector('a.text-xl, a[href*="index.html"]');
    if (brandA) brandA.classList.add('nav-brand');

    // 给分隔符加 class
    nav.querySelectorAll('span').forEach(function (s) {
      if (s.textContent.trim() === '|') s.classList.add('nav-sep');
    });

    // 给右侧链接组加 class
    nav.querySelectorAll('div.ml-auto, div.flex.gap-4').forEach(function (d) {
      if (!d.classList.contains('nav-links')) d.classList.add('nav-links');
    });

    // 如果还没有汉堡按钮就添加
    if (!nav.querySelector('.mobile-menu-btn')) {
      var btn = document.createElement('button');
      btn.className = 'mobile-menu-btn ml-auto text-paper text-xl bg-transparent border-0 cursor-pointer';
      btn.style.cssText = 'color:#F5F0E1;font-size:22px;min-width:44px;min-height:44px;display:none;align-items:center;justify-content:center;';
      btn.innerHTML = '<i class="fa fa-bars"></i>';
      btn.setAttribute('aria-label', '打开菜单');
      nav.appendChild(btn);
    }
  });

  // ---- 2. 创建抽屉面板 ----
  if (!document.getElementById('mobileNavPanel')) {
    var mask = document.createElement('div');
    mask.id = 'mobileNavMask';
    document.body.appendChild(mask);

    var panel = document.createElement('div');
    panel.id = 'mobileNavPanel';
    panel.innerHTML = '<button id="mobileNavClose" aria-label="关闭菜单"><i class="fa fa-times"></i></button><div class="mobileNavLinks"></div>';
    document.body.appendChild(panel);

    // 收集所有导航链接
    var links = [];
    document.querySelectorAll('nav.site-nav a, header nav a').forEach(function (a) {
      var href = a.getAttribute('href') || '';
      var text = a.textContent.trim();
      if (!text || text === '佛学本体论') return;
      // 去重
      if (links.some(function (l) { return l.href === href && l.text === text; })) return;
      var isActive = a.classList.contains('nav-active') ||
                     a.getAttribute('style') && a.getAttribute('style').indexOf('nav-active') >= 0 ||
                     a.getAttribute('style') && a.getAttribute('style').indexOf('rgba(184,134,11,0.25)') >= 0;
      links.push({ href: href, text: text, active: isActive });
    });

    // 顶部"返回首页"
    var homeLink = { href: '../index.html', text: '🏠 返回首页', active: false };
    if (location.pathname.endsWith('/index.html') || location.pathname.endsWith('/Buddhist/') || location.pathname === '/') {
      homeLink = { href: 'index.html', text: '🏠 首页', active: true };
    }

    var html = '';
    var all = [homeLink].concat(links.filter(function (l) {
      return l.text.indexOf('首页') < 0;
    }));
    all.forEach(function (l) {
      html += '<a href="' + l.href + '"' + (l.active ? ' class="nav-active"' : '') + '>' + l.text + '</a>';
    });
    panel.querySelector('.mobileNavLinks').innerHTML = html;

    // 开关逻辑
    function openMenu() {
      panel.classList.add('open');
      mask.classList.add('open');
      document.body.style.overflow = 'hidden';
    }
    function closeMenu() {
      panel.classList.remove('open');
      mask.classList.remove('open');
      document.body.style.overflow = '';
    }
    document.querySelectorAll('.mobile-menu-btn').forEach(function (b) {
      b.addEventListener('click', openMenu);
    });
    document.getElementById('mobileNavClose').addEventListener('click', closeMenu);
    mask.addEventListener('click', closeMenu);
  }

  // ---- 3. 触控增强：快速点击，消除 300ms 延迟 ----
  document.addEventListener('touchend', function (e) {
    var t = e.target.closest('a, button');
    if (!t) return;
    if (t.tagName === 'A') {
      var href = t.getAttribute('href');
      if (href && !href.startsWith('#') && !href.startsWith('javascript:') && t.target !== '_blank') {
        // 让浏览器默认处理链接跳转
      }
    }
  }, { passive: true });

  // ---- 4. 固定在底部的"返回顶部"按钮（仅读经页和长列表页）----
  if (document.querySelector('.sutra-content, .dict-list, .cat-sutra-list, #search-results')) {
    var backTop = document.createElement('button');
    backTop.id = 'mobileBackTop';
    backTop.innerHTML = '<i class="fa fa-arrow-up"></i>';
    backTop.setAttribute('aria-label', '返回顶部');
    backTop.style.cssText = 'position:fixed;right:14px;bottom:78px;width:44px;height:44px;border-radius:50%;background:rgba(62,39,35,.85);color:#F5F0E1;border:0;font-size:18px;z-index:90;box-shadow:0 4px 12px rgba(0,0,0,.2);display:none;align-items:center;justify-content:center;cursor:pointer;';
    document.body.appendChild(backTop);
    backTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    window.addEventListener('scroll', function () {
      backTop.style.display = window.scrollY > 400 ? 'flex' : 'none';
    }, { passive: true });
  }

  // ---- 5. 读经页：手机端默认中字号 ----
  if (document.querySelector('.sutra-content') && !localStorage.getItem('sutra-font-size')) {
    document.documentElement.classList.remove('fs-small','fs-large','fs-xlarge');
    document.documentElement.classList.add('fs-medium');
    var style = document.getElementById('fsStyle') || document.createElement('style');
    style.id = 'fsStyle';
    style.textContent = '.sutra-content{font-size:17px !important;line-height:2 !important;}';
    if (!style.parentNode) document.head.appendChild(style);
  }
})();
