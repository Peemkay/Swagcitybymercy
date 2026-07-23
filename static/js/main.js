(function () {
    "use strict";

    /* -----------------------------------------------------------------
       Helpers
    ----------------------------------------------------------------- */
    function getCookie(name) {
        const match = document.cookie.match(new RegExp('(^| )' + name + '=([^;]+)'));
        return match ? decodeURIComponent(match[2]) : null;
    }
    const CSRF_TOKEN = getCookie('csrftoken');

    function formatNaira(value) {
        const n = Math.round(parseFloat(value) || 0);
        return '₦' + n.toLocaleString('en-NG');
    }

    function fetchJSON(url, options) {
        options = options || {};
        options.headers = Object.assign({
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': CSRF_TOKEN,
        }, options.headers || {});
        return fetch(url, options).then(function (res) {
            return res.json().then(function (data) { return { ok: res.ok, data: data }; });
        });
    }

    /* -----------------------------------------------------------------
       Theme (dark mode) toggle
    ----------------------------------------------------------------- */
    const THEME_KEY = 'scm-theme';
    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        document.querySelectorAll('.theme-toggle i').forEach(function (icon) {
            icon.className = theme === 'dark' ? 'bi bi-sun' : 'bi bi-moon-stars';
        });
    }
    function initTheme() {
        const saved = localStorage.getItem(THEME_KEY);
        if (saved) applyTheme(saved);
        document.querySelectorAll('.theme-toggle').forEach(function (btn) {
            btn.addEventListener('click', function () {
                const current = document.documentElement.getAttribute('data-theme') ||
                    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
                const next = current === 'dark' ? 'light' : 'dark';
                applyTheme(next);
                localStorage.setItem(THEME_KEY, next);
            });
        });
    }

    /* -----------------------------------------------------------------
       Sticky header shrink-on-scroll + back-to-top
    ----------------------------------------------------------------- */
    function initScrollEffects() {
        const header = document.querySelector('.site-header');
        const backToTop = document.querySelector('.back-to-top');
        function onScroll() {
            const y = window.scrollY || window.pageYOffset;
            if (header) header.classList.toggle('is-scrolled', y > 12);
            if (backToTop) backToTop.classList.toggle('is-visible', y > 420);
        }
        document.addEventListener('scroll', onScroll, { passive: true });
        onScroll();
        if (backToTop) {
            backToTop.addEventListener('click', function () {
                window.scrollTo({ top: 0, behavior: 'smooth' });
            });
        }
    }

    /* -----------------------------------------------------------------
       Reveal-on-scroll
    ----------------------------------------------------------------- */
    function initReveal() {
        const targets = document.querySelectorAll('.reveal');
        if (!targets.length) return;
        if (!('IntersectionObserver' in window)) {
            targets.forEach(function (el) { el.classList.add('is-visible'); });
            return;
        }
        const io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    io.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
        targets.forEach(function (el, i) {
            el.style.transitionDelay = Math.min(i % 8, 8) * 60 + 'ms';
            io.observe(el);
        });
    }

    /* -----------------------------------------------------------------
       3D tilt + glare for product cards
    ----------------------------------------------------------------- */
    function initTilt() {
        const cards = document.querySelectorAll('.tilt-card');
        const supportsHover = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
        if (!supportsHover) return;
        cards.forEach(function (card) {
            const inner = card.querySelector('.product-card');
            function reset() {
                card.style.setProperty('--tilt-x', '0deg');
                card.style.setProperty('--tilt-y', '0deg');
                card.style.setProperty('--tilt-scale', '1');
            }
            card.addEventListener('mousemove', function (e) {
                const rect = card.getBoundingClientRect();
                const px = (e.clientX - rect.left) / rect.width;
                const py = (e.clientY - rect.top) / rect.height;
                const rotY = (px - 0.5) * 10;
                const rotX = (0.5 - py) * 10;
                card.style.setProperty('--tilt-x', rotX.toFixed(2) + 'deg');
                card.style.setProperty('--tilt-y', rotY.toFixed(2) + 'deg');
                card.style.setProperty('--tilt-scale', '1.015');
                card.style.setProperty('--gx', (px * 100).toFixed(1) + '%');
                card.style.setProperty('--gy', (py * 100).toFixed(1) + '%');
            });
            card.addEventListener('mouseleave', reset);
            if (inner) { /* keep reference to avoid unused warnings in some linters */ }
        });
    }

    /* -----------------------------------------------------------------
       Lazy image skeleton fade-in
    ----------------------------------------------------------------- */
    function initImageFade() {
        document.querySelectorAll('.img-wrap img, .product-gallery img').forEach(function (img) {
            const wrap = img.closest('.img-wrap');
            function markLoaded() {
                img.classList.add('is-loaded');
                if (wrap) wrap.classList.remove('skeleton');
            }
            if (img.complete && img.naturalWidth > 0) markLoaded();
            else img.addEventListener('load', markLoaded);
        });
    }

    /* -----------------------------------------------------------------
       Toast notifications
    ----------------------------------------------------------------- */
    function getToastStack() {
        let stack = document.querySelector('.scm-toast-stack');
        if (!stack) {
            stack = document.createElement('div');
            stack.className = 'scm-toast-stack';
            document.body.appendChild(stack);
        }
        return stack;
    }
    function showToast(message, type) {
        type = type || 'info';
        const stack = getToastStack();
        const toast = document.createElement('div');
        toast.className = 'scm-toast ' + type;
        toast.innerHTML = '<span class="msg"></span><button class="close" aria-label="Dismiss">&times;</button>';
        toast.querySelector('.msg').textContent = message;
        stack.appendChild(toast);
        requestAnimationFrame(function () { toast.classList.add('is-visible'); });
        function dismiss() {
            toast.classList.remove('is-visible');
            setTimeout(function () { toast.remove(); }, 400);
        }
        toast.querySelector('.close').addEventListener('click', dismiss);
        setTimeout(dismiss, 4500);
    }
    window.scmToast = showToast;

    function initDjangoMessagesAsToasts() {
        const container = document.querySelector('.scm-django-messages');
        if (!container) return;
        container.querySelectorAll('[data-message]').forEach(function (el) {
            showToast(el.dataset.message, el.dataset.tag || 'info');
        });
        container.remove();
    }

    /* -----------------------------------------------------------------
       Cart badge bump helper
    ----------------------------------------------------------------- */
    function updateCartBadge(count) {
        document.querySelectorAll('.cart-badge, .mb-badge').forEach(function (badge) {
            badge.textContent = count;
            badge.style.display = count > 0 ? '' : 'none';
            badge.classList.remove('bump');
            void badge.offsetWidth;
            badge.classList.add('bump');
        });
    }

    /* -----------------------------------------------------------------
       AJAX add-to-cart (progressive enhancement)
    ----------------------------------------------------------------- */
    function initAjaxCart() {
        document.querySelectorAll('.ajax-cart-form').forEach(function (form) {
            form.addEventListener('submit', function (e) {
                if (!form.action) return;
                e.preventDefault();
                const btn = form.querySelector('[type="submit"]');
                const originalText = btn ? btn.innerHTML : null;
                if (btn) { btn.disabled = true; btn.innerHTML = 'Adding&hellip;'; }

                fetchJSON(form.action, { method: 'POST', body: new FormData(form) })
                    .then(function (result) {
                        if (result.data.success) {
                            showToast(result.data.message, 'success');
                            updateCartBadge(result.data.cart_count);
                        } else {
                            showToast(result.data.message || 'Something went wrong.', 'error');
                        }
                    })
                    .catch(function () {
                        form.submit();
                    })
                    .finally(function () {
                        if (btn) { btn.disabled = false; btn.innerHTML = originalText; }
                    });
            });
        });
    }

    /* -----------------------------------------------------------------
       Cart page: AJAX quantity update / remove
    ----------------------------------------------------------------- */
    function initCartPage() {
        document.querySelectorAll('.cart-update-form').forEach(function (form) {
            form.addEventListener('submit', function (e) {
                e.preventDefault();
                fetchJSON(form.action, { method: 'POST', body: new FormData(form) }).then(function (result) {
                    if (!result.data.success) return;
                    const line = form.closest('.cart-line');
                    if (result.data.removed) {
                        if (line) { line.classList.add('removing'); setTimeout(function () { line.remove(); }, 300); }
                    } else {
                        const lineTotalEl = line ? line.querySelector('.js-line-total') : null;
                        if (lineTotalEl) lineTotalEl.textContent = formatNaira(result.data.line_total);
                    }
                    const subtotalEl = document.querySelector('.js-cart-subtotal');
                    if (subtotalEl) subtotalEl.textContent = formatNaira(result.data.cart_subtotal);
                    updateCartBadge(result.data.cart_count);
                    showToast('Bag updated.', 'success');
                });
            });
        });
        document.querySelectorAll('.cart-remove-form').forEach(function (form) {
            form.addEventListener('submit', function (e) {
                e.preventDefault();
                const line = form.closest('.cart-line');
                fetchJSON(form.action, { method: 'POST', body: new FormData(form) }).then(function (result) {
                    if (!result.data.success) return;
                    if (line) { line.classList.add('removing'); setTimeout(function () { line.remove(); }, 300); }
                    const subtotalEl = document.querySelector('.js-cart-subtotal');
                    if (subtotalEl) subtotalEl.textContent = formatNaira(result.data.cart_subtotal);
                    updateCartBadge(result.data.cart_count);
                    showToast('Item removed from your bag.', 'info');
                });
            });
        });
    }

    /* -----------------------------------------------------------------
       Quantity steppers
    ----------------------------------------------------------------- */
    function initQtySteppers() {
        document.querySelectorAll('.qty-stepper').forEach(function (stepper) {
            const input = stepper.querySelector('input[type="number"]');
            if (!input) return;
            stepper.querySelectorAll('button[data-step]').forEach(function (btn) {
                btn.addEventListener('click', function () {
                    const step = parseInt(btn.dataset.step, 10);
                    const min = parseInt(input.min || '1', 10);
                    const max = input.max ? parseInt(input.max, 10) : Infinity;
                    let value = (parseInt(input.value, 10) || min) + step;
                    value = Math.max(min, Math.min(max, value));
                    input.value = value;
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                });
            });
        });
    }

    /* -----------------------------------------------------------------
       Wishlist (localStorage)
    ----------------------------------------------------------------- */
    const WISHLIST_KEY = 'scm-wishlist';
    function getWishlist() {
        try { return JSON.parse(localStorage.getItem(WISHLIST_KEY)) || []; }
        catch (e) { return []; }
    }
    function setWishlist(list) { localStorage.setItem(WISHLIST_KEY, JSON.stringify(list)); }

    function refreshWishlistUI() {
        const list = getWishlist();
        document.querySelectorAll('.wishlist-btn[data-slug]').forEach(function (btn) {
            btn.classList.toggle('active', list.indexOf(btn.dataset.slug) !== -1);
        });
        document.querySelectorAll('.wishlist-count').forEach(function (el) {
            el.textContent = list.length;
            el.style.display = list.length > 0 ? '' : 'none';
        });
    }

    function initWishlist() {
        document.addEventListener('click', function (e) {
            const btn = e.target.closest('.wishlist-btn[data-slug]');
            if (!btn) return;
            e.preventDefault();
            const slug = btn.dataset.slug;
            let list = getWishlist();
            if (list.indexOf(slug) === -1) {
                list.push(slug);
                showToast('Added to your favorites.', 'success');
            } else {
                list = list.filter(function (s) { return s !== slug; });
                showToast('Removed from your favorites.', 'info');
            }
            setWishlist(list);
            btn.classList.add('pulse');
            setTimeout(function () { btn.classList.remove('pulse'); }, 400);
            refreshWishlistUI();
            applyWishlistFilter();
        });
        refreshWishlistUI();
    }

    function applyWishlistFilter() {
        const toggle = document.getElementById('favoritesOnlyToggle');
        if (!toggle) return;
        const list = getWishlist();
        const onlyFavorites = toggle.checked;
        document.querySelectorAll('.tilt-card[data-slug]').forEach(function (card) {
            const show = !onlyFavorites || list.indexOf(card.dataset.slug) !== -1;
            card.classList.toggle('d-none', !show);
        });
    }
    function initFavoritesFilter() {
        const toggle = document.getElementById('favoritesOnlyToggle');
        if (!toggle) return;
        toggle.addEventListener('change', applyWishlistFilter);
        applyWishlistFilter();
    }

    /* -----------------------------------------------------------------
       Recently viewed (localStorage)
    ----------------------------------------------------------------- */
    const RECENT_KEY = 'scm-recently-viewed';
    function trackRecentlyViewed() {
        const dataEl = document.getElementById('currentProductData');
        if (!dataEl) return;
        let product;
        try { product = JSON.parse(dataEl.textContent); } catch (e) { return; }
        let list = [];
        try { list = JSON.parse(localStorage.getItem(RECENT_KEY)) || []; } catch (e) { list = []; }
        list = list.filter(function (p) { return p.slug !== product.slug; });
        list.unshift(product);
        list = list.slice(0, 8);
        localStorage.setItem(RECENT_KEY, JSON.stringify(list));
    }
    function renderRecentlyViewed() {
        const strip = document.getElementById('recentlyViewedStrip');
        if (!strip) return;
        let list = [];
        try { list = JSON.parse(localStorage.getItem(RECENT_KEY)) || []; } catch (e) { list = []; }
        const currentSlug = document.body.dataset.productSlug;
        list = list.filter(function (p) { return p.slug !== currentSlug; });
        if (!list.length) return;
        const track = strip.querySelector('.rv-track');
        track.innerHTML = list.map(function (p) {
            return '<a class="rv-item" href="' + p.url + '">' +
                '<div class="rv-img"><img src="' + p.image + '" alt="' + p.name + '" loading="lazy"></div>' +
                '<div class="rv-name">' + p.name + '</div>' +
                '<div class="rv-price">' + formatNaira(p.price) + '</div>' +
                '</a>';
        }).join('');
        strip.classList.add('has-items');
    }

    /* -----------------------------------------------------------------
       Product gallery lightbox
    ----------------------------------------------------------------- */
    function initLightbox() {
        const gallery = document.querySelector('.product-gallery');
        if (!gallery) return;
        const mainImg = gallery.querySelector('#mainImage');
        const thumbs = Array.prototype.slice.call(gallery.querySelectorAll('.thumb-swap'));
        const images = thumbs.length ? thumbs.map(function (t) { return t.dataset.full; }) : (mainImg ? [mainImg.src] : []);
        if (!images.length) return;

        let lb = document.querySelector('.scm-lightbox');
        if (!lb) {
            lb = document.createElement('div');
            lb.className = 'scm-lightbox';
            lb.innerHTML = '<button class="lb-close" aria-label="Close"><i class="bi bi-x-lg"></i></button>' +
                '<button class="lb-prev" aria-label="Previous"><i class="bi bi-chevron-left"></i></button>' +
                '<img alt="Product photo">' +
                '<button class="lb-next" aria-label="Next"><i class="bi bi-chevron-right"></i></button>';
            document.body.appendChild(lb);
        }
        const lbImg = lb.querySelector('img');
        let index = 0;

        function open(i) {
            index = i;
            lbImg.src = images[index];
            lb.classList.add('is-open');
        }
        function close() { lb.classList.remove('is-open'); }
        function nav(delta) { index = (index + delta + images.length) % images.length; lbImg.src = images[index]; }

        if (mainImg) mainImg.addEventListener('click', function () {
            const currentSrc = mainImg.src;
            const found = images.indexOf(currentSrc);
            open(found !== -1 ? found : 0);
        });
        thumbs.forEach(function (thumb, i) {
            thumb.addEventListener('click', function () {
                if (mainImg) { mainImg.src = thumb.dataset.full; mainImg.classList.add('is-loaded'); }
                thumbs.forEach(function (t) { t.classList.remove('active-thumb'); });
                thumb.classList.add('active-thumb');
            });
        });
        lb.querySelector('.lb-close').addEventListener('click', close);
        lb.querySelector('.lb-prev').addEventListener('click', function () { nav(-1); });
        lb.querySelector('.lb-next').addEventListener('click', function () { nav(1); });
        lb.addEventListener('click', function (e) { if (e.target === lb) close(); });
        document.addEventListener('keydown', function (e) {
            if (!lb.classList.contains('is-open')) return;
            if (e.key === 'Escape') close();
            if (e.key === 'ArrowLeft') nav(-1);
            if (e.key === 'ArrowRight') nav(1);
        });
    }

    /* -----------------------------------------------------------------
       Sticky "add to bag" bar on mobile PDP
    ----------------------------------------------------------------- */
    function initStickyAddBar() {
        const bar = document.getElementById('stickyAddBar');
        const trigger = document.getElementById('addToCartBtn');
        if (!bar || !trigger || !('IntersectionObserver' in window)) return;
        const io = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                bar.classList.toggle('is-visible', !entry.isIntersecting && window.innerWidth < 992);
            });
        }, { threshold: 0 });
        io.observe(trigger);
        const barBtn = bar.querySelector('button, a.btn-scm');
        if (barBtn) {
            barBtn.addEventListener('click', function (e) {
                e.preventDefault();
                trigger.scrollIntoView({ behavior: 'smooth', block: 'center' });
            });
        }
    }

    /* -----------------------------------------------------------------
       Shop page: sort / grid-list toggle / debounced search
    ----------------------------------------------------------------- */
    function initShopControls() {
        const sortSelect = document.getElementById('sortSelect');
        if (sortSelect) {
            sortSelect.addEventListener('change', function () {
                const url = new URL(window.location.href);
                url.searchParams.set('sort', sortSelect.value);
                url.searchParams.delete('page');
                window.location.href = url.toString();
            });
        }

        const inStockToggle = document.getElementById('inStockToggle');
        if (inStockToggle) {
            inStockToggle.addEventListener('change', function () {
                const url = new URL(window.location.href);
                if (inStockToggle.checked) url.searchParams.set('in_stock', '1');
                else url.searchParams.delete('in_stock');
                url.searchParams.delete('page');
                window.location.href = url.toString();
            });
        }

        const grid = document.querySelector('.shop-grid');
        const gridBtn = document.getElementById('gridViewBtn');
        const listBtn = document.getElementById('listViewBtn');
        if (grid && gridBtn && listBtn) {
            const savedView = localStorage.getItem('scm-shop-view');
            if (savedView === 'list') { grid.classList.add('list-view'); listBtn.classList.add('active'); gridBtn.classList.remove('active'); }
            gridBtn.addEventListener('click', function () {
                grid.classList.remove('list-view');
                gridBtn.classList.add('active'); listBtn.classList.remove('active');
                localStorage.setItem('scm-shop-view', 'grid');
            });
            listBtn.addEventListener('click', function () {
                grid.classList.add('list-view');
                listBtn.classList.add('active'); gridBtn.classList.remove('active');
                localStorage.setItem('scm-shop-view', 'list');
            });
        }

        const searchInput = document.getElementById('shopSearchInput');
        if (searchInput) {
            let timer = null;
            searchInput.addEventListener('input', function () {
                clearTimeout(timer);
                timer = setTimeout(function () { searchInput.form.submit(); }, 600);
            });
        }
    }

    /* -----------------------------------------------------------------
       Copy to clipboard
    ----------------------------------------------------------------- */
    function initCopyButtons() {
        document.querySelectorAll('.copy-btn[data-copy]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                const text = btn.dataset.copy;
                const done = function () {
                    const original = btn.textContent;
                    btn.textContent = 'Copied!';
                    btn.classList.add('copied');
                    showToast('Copied to clipboard.', 'success');
                    setTimeout(function () { btn.textContent = original; btn.classList.remove('copied'); }, 1800);
                };
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(text).then(done).catch(done);
                } else {
                    const ta = document.createElement('textarea');
                    ta.value = text; document.body.appendChild(ta); ta.select();
                    try { document.execCommand('copy'); } catch (e) { /* no-op */ }
                    ta.remove();
                    done();
                }
            });
        });
    }

    /* -----------------------------------------------------------------
       Newsletter AJAX submit
    ----------------------------------------------------------------- */
    function initNewsletterForm() {
        document.querySelectorAll('.newsletter-form').forEach(function (form) {
            form.addEventListener('submit', function (e) {
                e.preventDefault();
                fetchJSON(form.action, { method: 'POST', body: new FormData(form) }).then(function (result) {
                    showToast(result.data.message, result.data.success ? 'success' : 'error');
                    if (result.data.success) form.reset();
                });
            });
        });
    }

    /* -----------------------------------------------------------------
       Init
    ----------------------------------------------------------------- */
    document.addEventListener('DOMContentLoaded', function () {
        initTheme();
        initScrollEffects();
        initReveal();
        initTilt();
        initImageFade();
        initDjangoMessagesAsToasts();
        initAjaxCart();
        initCartPage();
        initQtySteppers();
        initWishlist();
        initFavoritesFilter();
        trackRecentlyViewed();
        renderRecentlyViewed();
        initLightbox();
        initStickyAddBar();
        initShopControls();
        initCopyButtons();
        initNewsletterForm();
    });
})();
