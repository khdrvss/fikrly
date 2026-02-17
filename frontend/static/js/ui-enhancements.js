/**
 * Fikrly UI Enhancements
 * Toast notifications, skeleton loaders, and form validation
 */

// ============================================
// 1. TOAST NOTIFICATIONS
// ============================================
const Toast = {
  show(message, type = 'info', duration = 3000) {
    const colors = {
      success: 'bg-green-500',
      error: 'bg-red-500',
      warning: 'bg-yellow-500',
      info: 'bg-primary-600'
    };

    const icons = {
      success: `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
      </svg>`,
      error: `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
      </svg>`,
      warning: `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
      </svg>`,
      info: `<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
      </svg>`
    };

    const toast = document.createElement('div');
    toast.className = `toast fixed top-4 right-4 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg transform translate-x-full transition-transform duration-300 z-50 flex items-center space-x-3 max-w-md`;
    toast.innerHTML = `
      ${icons[type] || icons.info}
      <span class="flex-1">${message}</span>
      <button class="ml-2 hover:bg-white hover:bg-opacity-20 rounded p-1 transition-colors" onclick="this.parentElement.remove()">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    `;

    document.body.appendChild(toast);
    setTimeout(() => toast.classList.remove('translate-x-full'), 10);
    
    setTimeout(() => {
      // ============================================
      // 6. INFINITE SCROLL (DISABLED)
      // ============================================
      // Infinite scroll feature intentionally disabled to enforce strict pagination.
      // The class is replaced with a no-op stub to avoid runtime errors in pages
      // that might reference it. No client-side auto-loading will occur.
      class InfiniteScroll {
        constructor() {
          console.info('InfiniteScroll disabled');
        }
      }

      window.InfiniteScroll = InfiniteScroll;
      firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }

  isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  isValidPhone(phone) {
    // Supports formats: +998901234567, 998901234567, 901234567
    const cleaned = phone.replace(/\D/g, '');
    return /^(\+?998)?[0-9]{9}$/.test(cleaned);
  }

  reset() {
    const fields = this.form.querySelectorAll('input, textarea, select');
    fields.forEach(field => this.clearError(field));
  }
}

window.FormValidator = FormValidator;


// ============================================
// 4. PROGRESSIVE IMAGE LOADING
// ============================================
class LazyImage {
  static init() {
    // Progressive loading for images with data-src
    const images = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
      const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const img = entry.target;
            this.loadImage(img);
            observer.unobserve(img);
          }
        });
      }, {
        rootMargin: '50px 0px', // Start loading 50px before image enters viewport
        threshold: 0.01
      });
      
      images.forEach(img => imageObserver.observe(img));
    } else {
      // Fallback for older browsers
      images.forEach(img => this.loadImage(img));
    }
  }

  static loadImage(img) {
    const highResSrc = img.dataset.src;
    const placeholder = img.src;
    
    // Add blur effect to placeholder
    img.style.filter = 'blur(10px)';
    img.style.transition = 'filter 0.3s ease-in-out';
    
    // Create temp image to preload
    const tempImg = new Image();
    tempImg.onload = () => {
      img.src = highResSrc;
      img.removeAttribute('data-src');
      
      // Remove blur after loaded
      setTimeout(() => {
        img.style.filter = 'blur(0)';
      }, 50);
      
      // Add loaded class for additional styling
      img.classList.add('lazy-loaded');
    };
    
    tempImg.onerror = () => {
      // Fallback to placeholder on error
      img.style.filter = 'blur(0)';
      img.classList.add('lazy-error');
    };
    
    tempImg.src = highResSrc;
  }

  static convertImage(img, highResSrc, lowResSrc = null) {
    // Helper to convert existing img to lazy-loading
    if (lowResSrc) {
      img.src = lowResSrc;
    }
    img.dataset.src = highResSrc;
    img.classList.add('lazy-image');
    this.loadImage(img);
  }
}

window.LazyImage = LazyImage;


// ============================================
// 5. INTERACTIVE STAR RATING
// ============================================
class StarRating {
  constructor(container, options = {}) {
    this.container = typeof container === 'string' ? document.querySelector(container) : container;
    if (!this.container) return;
    
    this.options = {
      initialRating: 0,
      maxRating: 5,
      readonly: false,
      size: 'medium', // small, medium, large
      showCount: false,
      onChange: null,
      ...options
    };
    
    this.currentRating = this.options.initialRating;
    this.hoverRating = 0;
    this.init();
  }

  init() {
    this.container.classList.add('star-rating-container');
    this.render();
    
    if (!this.options.readonly) {
      this.attachEvents();
    }
  }

  render() {
    const sizes = {
      small: 'w-5 h-5',
      medium: 'w-8 h-8',
      large: 'w-10 h-10'
    };
    
    const sizeClass = sizes[this.options.size] || sizes.medium;
    let html = '<div class="flex items-center gap-1">';
    
    for (let i = 1; i <= this.options.maxRating; i++) {
      const filled = i <= (this.hoverRating || this.currentRating);
      const starClass = filled ? 'text-yellow-400' : 'text-gray-300';
      
      html += `
        <button type="button" 
                class="star-btn ${sizeClass} ${starClass} transition-all duration-150 transform hover:scale-110 ${this.options.readonly ? 'cursor-default' : 'cursor-pointer'}" 
                data-rating="${i}"
                ${this.options.readonly ? 'disabled' : ''}>
          <svg class="w-full h-full" fill="currentColor" viewBox="0 0 20 20">
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
          </svg>
        </button>
      `;
    }
    
    if (this.options.showCount) {
      html += `<span class="ml-2 text-sm text-gray-600">${this.currentRating}/${this.options.maxRating}</span>`;
    }
    
    html += '</div>';
    this.container.innerHTML = html;
  }

  attachEvents() {
    const stars = this.container.querySelectorAll('.star-btn');
    
    stars.forEach(star => {
      star.addEventListener('mouseenter', (e) => {
        this.hoverRating = parseInt(e.currentTarget.dataset.rating);
        this.updateStars();
      });
      
      star.addEventListener('click', (e) => {
        this.currentRating = parseInt(e.currentTarget.dataset.rating);
        this.hoverRating = 0;
        this.updateStars();
        
        if (this.options.onChange) {
          this.options.onChange(this.currentRating);
        }
        
        // Update hidden input if exists
        const hiddenInput = this.container.querySelector('input[type="hidden"]');
        if (hiddenInput) {
          hiddenInput.value = this.currentRating;
        }
        
        // Dispatch custom event
        this.container.dispatchEvent(new CustomEvent('ratingChange', { 
          detail: { rating: this.currentRating } 
        }));
      });
    });
    
    this.container.addEventListener('mouseleave', () => {
      this.hoverRating = 0;
      this.updateStars();
    });
  }

  updateStars() {
    const stars = this.container.querySelectorAll('.star-btn');
    const activeRating = this.hoverRating || this.currentRating;
    
    stars.forEach((star, index) => {
      if (index < activeRating) {
        star.classList.remove('text-gray-300');
        star.classList.add('text-yellow-400');
      } else {
        star.classList.remove('text-yellow-400');
        star.classList.add('text-gray-300');
      }
    });
  }

  setRating(rating) {
    this.currentRating = Math.max(0, Math.min(rating, this.options.maxRating));
    this.render();
  }

  getRating() {
    return this.currentRating;
  }
}

window.StarRating = StarRating;


// ============================================
// 6. INFINITE SCROLL
// ============================================
class InfiniteScroll {
  constructor(options = {}) {
    this.options = {
      container: null,
      loadMoreUrl: null,
      threshold: 300, // pixels from bottom to trigger load
      pageParam: 'page',
      onLoad: null,
      onError: null,
      skeletonType: 'card',
      skeletonCount: 3,
      ...options
    };
    
    this.container = typeof this.options.container === 'string' 
      ? document.querySelector(this.options.container) 
      : this.options.container;
    
    if (!this.container) {
      console.error('InfiniteScroll: Container not found');
      return;
    }
    
    this.page = 1;
    this.loading = false;
    this.hasMore = true;
    this.init();
  }

  init() {
    this.scrollHandler = this.checkScroll.bind(this);
    window.addEventListener('scroll', this.scrollHandler);
    
    // Check immediately in case content doesn't fill screen
    setTimeout(() => this.checkScroll(), 100);
  }

  checkScroll() {
    if (this.shouldLoadMore()) {
      this.loadMore();
    }
  }

  shouldLoadMore() {
    if (!this.hasMore || this.loading) return false;
    
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    
    return (scrollTop + windowHeight >= documentHeight - this.options.threshold);
  }

  async loadMore() {
    if (this.loading || !this.hasMore) return;
    
    this.loading = true;
    this.showLoader();
    
    try {
      // Get URL template from container if available
      const urlTemplate = this.container.dataset.urlTemplate;
      const currentNextPage = this.container.dataset.nextPage;
      
      let url;
      if (urlTemplate && currentNextPage) {
        // Use template-based URL (for business list with filters)
        // Use current path as base so query-only templates resolve to the current view
        const basePath = `${window.location.origin}${window.location.pathname}`;
        url = new URL(urlTemplate.replace('PAGE_NUM', currentNextPage), basePath);
      } else {
        // Use standard pagination
        url = new URL(this.options.loadMoreUrl, window.location.origin);
        url.searchParams.set(this.options.pageParam, this.page + 1);
      }
      
      const response = await fetch(url, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      });

      if (!response.ok) {
        // HTTP error statuses
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      // Ensure JSON content-type before parsing
      const contentType = response.headers.get('content-type') || '';
      if (!contentType.includes('application/json')) {
        throw new Error('Invalid response content-type');
      }

      const data = await response.json();
      
      this.hideLoader();
      
      // Handle business list format
      if (data.companies && data.companies.length > 0) {
        this.appendResults(data);
        this.page++;
        this.hasMore = data.has_next || false;
        
        // Update next page in container
        if (data.next_page) {
          this.container.dataset.nextPage = data.next_page;
        } else {
          this.container.removeAttribute('data-next-page');
        }
        
        if (this.options.onLoad) {
          this.options.onLoad(data);
        }
      } 
      // Handle generic format
      else if (data.results && data.results.length > 0) {
        this.appendResults(data);
        this.page++;
        this.hasMore = data.has_next || data.next || false;
        
        if (this.options.onLoad) {
          this.options.onLoad(data);
        }
      } 
      else {
        this.hasMore = false;
        this.showEndMessage();
      }
    } catch (error) {
      console.error('InfiniteScroll error:', error);
      this.hideLoader();

      let userMessage = 'Server bilan bog‘lanishda muammo yuz berdi.';
      if (error.message && error.message.includes('HTTP error')) {
        const status = parseInt(error.message.replace(/[^0-9]/g, ''), 10) || 0;
        if (status >= 500) {
          userMessage = 'Ichki server xatosi. Keyinroq urinib ko‘ring.';
        } else if (status === 404) {
          userMessage = 'Bu sahifada bizneslar topilmadi.';
        } else if (status === 400) {
          userMessage = 'So‘rov noto‘g‘ri yuborildi.';
        } else {
          userMessage = `Server javobi: ${status}`;
        }
      } else if (error.message && error.message.includes('Invalid response content-type')) {
        userMessage = 'Server noto‘g‘ri javob qaytardi.';
      }

      if (this.options.onError) {
        this.options.onError(error, userMessage);
      } else {
        Toast.error(userMessage);
      }
    } finally {
      this.loading = false;
    }
  }

  showLoader() {
    const loader = document.createElement('div');
    loader.id = 'infinite-scroll-loader';
    loader.className = 'infinite-scroll-loader py-8';
    
    // Add skeletons
    for (let i = 0; i < this.options.skeletonCount; i++) {
      loader.innerHTML += Skeleton[this.options.skeletonType]();
    }
    
    this.container.appendChild(loader);
  }

  hideLoader() {
    const loader = document.getElementById('infinite-scroll-loader');
    if (loader) {
      loader.remove();
    }
  }

  showEndMessage() {
    const existing = document.getElementById('infinite-scroll-end');
    if (existing) return;
    
    const endMsg = document.createElement('div');
    endMsg.id = 'infinite-scroll-end';
    endMsg.className = 'text-center py-8 text-gray-500';
    endMsg.innerHTML = `
      <svg class="w-12 h-12 mx-auto mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
      </svg>
      <p class="text-sm font-medium">Barcha ma'lumotlar ko'rsatildi</p>
    `;
    this.container.appendChild(endMsg);
  }

  appendResults(data) {
    // Handle business list format (companies array)
    if (data.companies) {
      data.companies.forEach(company => {
        const card = this.createBusinessCard(company);
        this.container.appendChild(card);
      });
      
      // Re-initialize lazy loading for new images
      LazyImage.init();
    }
    // If data has HTML property, use it
    else if (data.html) {
      const temp = document.createElement('div');
      temp.innerHTML = data.html;
      
      Array.from(temp.children).forEach(child => {
        this.container.appendChild(child);
      });
    } 
    // If data has results array with HTML
    else if (data.results) {
      data.results.forEach(item => {
        if (typeof item === 'string') {
          const temp = document.createElement('div');
          temp.innerHTML = item;
          this.container.appendChild(temp.firstElementChild);
        } else if (item.html) {
          const temp = document.createElement('div');
          temp.innerHTML = item.html;
          this.container.appendChild(temp.firstElementChild);
        }
      });
    }
  }

  createBusinessCard(company) {
    const card = document.createElement('div');
    card.className = 'group bg-white rounded-2xl border border-green-200 shadow-sm hover:shadow-xl transition-all duration-300 flex flex-col overflow-hidden relative';
    
    card.innerHTML = `
      <div class="relative h-48 overflow-hidden">
        <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 400'%3E%3Crect fill='%23f3f4f6' width='800' height='400'/%3E%3C/svg%3E"
             data-src="${company.image_url}"
             alt="${company.name}"
             class="lazy-image w-full h-full object-cover transform group-hover:scale-105 transition-transform duration-500">
        <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent opacity-60"></div>
        
        <div class="absolute bottom-4 left-4 right-4 flex items-end justify-between">
          <div class="bg-white p-1 rounded-lg shadow-lg overflow-hidden">
            <div class="w-10 h-10 rounded-md overflow-hidden relative">
              <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'%3E%3Crect fill='%23f3f4f6' width='40' height='40'/%3E%3C/svg%3E"
                   data-src="${company.logo_url}"
                   alt="${company.name} logo"
                   class="lazy-image w-full h-full object-cover absolute inset-0"
                   style="transform: scale(${company.logo_scale / 100});">
            </div>
          </div>
          <div class="flex items-center gap-1 bg-white/90 backdrop-blur-sm px-2 py-1 rounded-lg text-sm font-bold text-gray-900 shadow-sm">
            <svg class="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
            </svg>
            ${company.rating.toFixed(1)}
          </div>
        </div>
      </div>
      
      <div class="p-6 flex-1 flex flex-col">
        <div class="mb-4">
          <h3 class="text-xl font-bold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors line-clamp-2">${company.name}</h3>
          <div class="flex flex-wrap gap-2 text-sm text-gray-500">
            ${company.category ? `<span class="flex items-center gap-1.5"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"/></svg>${company.category}</span>` : ''}
            ${company.city ? `<span class="flex items-center gap-1.5"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/></svg>${company.city}</span>` : ''}
          </div>
        </div>
        
        <div class="mt-auto pt-4 border-t border-gray-100 flex items-center justify-between">
          <span class="text-sm text-gray-500">${company.review_count} ta sharh</span>
          <a href="${company.detail_url}" class="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-lg transition-colors">
            Ko'rish
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/></svg>
          </a>
        </div>
      </div>
    `;
    
    return card;
  }

  destroy() {
    window.removeEventListener('scroll', this.scrollHandler);
    this.hideLoader();
  }

  reset() {
    this.page = 1;
    this.hasMore = true;
    this.loading = false;
    this.hideLoader();
    document.getElementById('infinite-scroll-end')?.remove();
  }
}

window.InfiniteScroll = InfiniteScroll;


// ============================================
// 7. LOADING PROGRESS BAR
// ============================================
class LoadingBar {
  static instance = null;
  
  static init() {
    if (LoadingBar.instance) return LoadingBar.instance;
    
    // Create bar element
    const bar = document.createElement('div');
    bar.id = 'loading-progress-bar';
    bar.className = 'fixed top-0 left-0 right-0 h-1 bg-primary-600 transform origin-left scale-x-0 transition-transform duration-300 ease-out z-50';
    bar.style.boxShadow = '0 0 10px rgba(59, 130, 246, 0.5)';
    document.body.appendChild(bar);
    
    LoadingBar.instance = {
      bar: bar,
      progress: 0,
      timer: null,
      isComplete: false
    };
    
    return LoadingBar.instance;
  }
  
  static start() {
    const instance = LoadingBar.init();
    instance.progress = 0;
    instance.isComplete = false;
    instance.bar.style.transform = 'scaleX(0)';
    instance.bar.style.opacity = '1';
    
    // Animate to 30% quickly
    setTimeout(() => {
      instance.progress = 30;
      instance.bar.style.transform = 'scaleX(0.3)';
    }, 50);
    
    // Slowly progress to 90%
    instance.timer = setInterval(() => {
      if (instance.progress < 90 && !instance.isComplete) {
        instance.progress += Math.random() * 10;
        if (instance.progress > 90) instance.progress = 90;
        instance.bar.style.transform = `scaleX(${instance.progress / 100})`;
      }
    }, 500);
  }
  
  static complete() {
    const instance = LoadingBar.instance;
    if (!instance) return;
    
    instance.isComplete = true;
    clearInterval(instance.timer);
    
    // Complete to 100%
    instance.progress = 100;
    instance.bar.style.transform = 'scaleX(1)';
    
    // Fade out
    setTimeout(() => {
      instance.bar.style.opacity = '0';
      setTimeout(() => {
        instance.bar.style.transform = 'scaleX(0)';
        instance.progress = 0;
      }, 300);
    }, 200);
  }
  
  static set(percent) {
    const instance = LoadingBar.init();
    instance.progress = Math.min(Math.max(percent, 0), 100);
    instance.bar.style.transform = `scaleX(${instance.progress / 100})`;
  }
}

window.LoadingBar = LoadingBar;


// ============================================
// 8. CHARACTER COUNTER
// ============================================
class CharacterCounter {
  constructor(input, options = {}) {
    this.input = input;
    this.options = {
      maxLength: input.maxLength || input.getAttribute('maxlength') || 500,
      showRemaining: options.showRemaining !== false,
      warningThreshold: options.warningThreshold || 0.9,
      className: options.className || 'text-sm text-gray-500 mt-1',
      ...options
    };
    
    this.init();
  }
  
  init() {
    // Create counter element
    this.counter = document.createElement('div');
    this.counter.className = this.options.className;
    
    // Insert after input
    this.input.parentNode.insertBefore(this.counter, this.input.nextSibling);
    
    // Update on input
    this.input.addEventListener('input', () => this.update());
    
    // Initial update
    this.update();
  }
  
  update() {
    const current = this.input.value.length;
    const max = this.options.maxLength;
    const remaining = max - current;
    const percent = current / max;
    
    // Update text
    if (this.options.showRemaining) {
      this.counter.textContent = `${current}/${max}`;
    } else {
      this.counter.textContent = `${current} belgidan ${max}`;
    }
    
    // Update color based on threshold
    this.counter.classList.remove('text-gray-500', 'text-amber-600', 'text-red-600');
    
    if (percent >= 1) {
      this.counter.classList.add('text-red-600', 'font-medium');
    } else if (percent >= this.options.warningThreshold) {
      this.counter.classList.add('text-amber-600', 'font-medium');
    } else {
      this.counter.classList.add('text-gray-500');
      this.counter.classList.remove('font-medium');
    }
  }
  
  static init(selector = '[data-character-counter]') {
    document.querySelectorAll(selector).forEach(input => {
      if (!input._characterCounter) {
        input._characterCounter = new CharacterCounter(input, {
          maxLength: input.dataset.maxLength || input.maxLength,
          showRemaining: !input.dataset.hideRemaining
        });
      }
    });
  }
}

window.CharacterCounter = CharacterCounter;


// ============================================
// 9. SEARCH AUTOCOMPLETE
// ============================================
class SearchAutocomplete {
  constructor(input, options = {}) {
    this.input = input;
    this.options = {
      minChars: options.minChars || 2,
      debounceMs: options.debounceMs || 300,
      maxResults: options.maxResults || 8,
      searchUrl: options.searchUrl || '/api/search/',
      recentSearchesKey: options.recentSearchesKey || 'fikrly_recent_searches',
      maxRecentSearches: options.maxRecentSearches || 5,
      placeholder: options.placeholder || 'Qidiruv...',
      categories: options.categories || [],
      onSelect: options.onSelect || null,
      ...options
    };
    
    this.debounceTimer = null;
    this.isOpen = false;
    this.selectedIndex = -1;
    this.results = [];
    
    this.init();
  }
  
  init() {
    // Create dropdown container
    this.dropdown = document.createElement('div');
    this.dropdown.className = 'absolute top-full left-0 right-0 mt-2 bg-white rounded-lg shadow-xl border border-gray-200 max-h-96 overflow-y-auto hidden z-50';
    
    // Position relative to input's parent
    const wrapper = this.input.parentElement;
    if (wrapper.style.position !== 'relative' && wrapper.style.position !== 'absolute') {
      wrapper.style.position = 'relative';
    }
    wrapper.appendChild(this.dropdown);
    
    // Event listeners
    this.input.addEventListener('input', (e) => this.handleInput(e));
    this.input.addEventListener('focus', () => this.handleFocus());
    this.input.addEventListener('keydown', (e) => this.handleKeydown(e));
    
    // Close on outside click
    document.addEventListener('click', (e) => {
      if (!wrapper.contains(e.target)) {
        this.close();
      }
    });
  }
  
  handleInput(e) {
    const query = e.target.value.trim();
    
    clearTimeout(this.debounceTimer);
    
    if (query.length < this.options.minChars) {
      this.showRecentSearches();
      return;
    }
    
    this.debounceTimer = setTimeout(() => {
      this.search(query);
    }, this.options.debounceMs);
  }
  
  handleFocus() {
    const query = this.input.value.trim();
    if (query.length >= this.options.minChars) {
      this.search(query);
    } else {
      this.showRecentSearches();
    }
  }
  
  handleKeydown(e) {
    if (!this.isOpen) return;
    
    switch(e.key) {
      case 'ArrowDown':
        e.preventDefault();
        this.selectedIndex = Math.min(this.selectedIndex + 1, this.results.length - 1);
        this.updateSelection();
        break;
      case 'ArrowUp':
        e.preventDefault();
        this.selectedIndex = Math.max(this.selectedIndex - 1, -1);
        this.updateSelection();
        break;
      case 'Enter':
        e.preventDefault();
        if (this.selectedIndex >= 0) {
          this.selectResult(this.results[this.selectedIndex]);
        }
        break;
      case 'Escape':
        this.close();
        break;
    }
  }
  
  async search(query) {
    LoadingBar.start();
    
    try {
      // Mock search - replace with actual API call
      const results = await this.mockSearch(query);
      this.showResults(results, query);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      LoadingBar.complete();
    }
  }
  
  async mockSearch(query) {
    // TODO: Replace with actual fetch to your API
    // const response = await fetch(`${this.options.searchUrl}?q=${encodeURIComponent(query)}`);
    // const data = await response.json();
    // return data.results;
    
    // Mock data for now
    return [
      { type: 'company', name: `${query} kompaniyasi`, category: 'Restoran', icon: '🏢' },
      { type: 'category', name: `${query} kategoriyasi`, count: 15, icon: '📁' },
    ].filter(r => Math.random() > 0.3);
  }
  
  showRecentSearches() {
    const recent = this.getRecentSearches();
    
    if (recent.length === 0) {
      this.close();
      return;
    }
    
    this.results = recent.map(search => ({
      type: 'recent',
      name: search,
      icon: '🕒'
    }));
    
    this.renderDropdown('Oxirgi qidiruvlar');
  }
  
  showResults(results, query) {
    this.results = results;
    
    if (results.length === 0) {
      this.dropdown.innerHTML = `
        <div class="p-4 text-center text-gray-500">
          <svg class="w-12 h-12 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
          <p class="text-sm">Hech narsa topilmadi</p>
        </div>
      `;
      this.open();
      return;
    }
    
    this.renderDropdown(`Natijalar: "${query}"`);
  }
  
  renderDropdown(title) {
    this.dropdown.innerHTML = `
      ${title ? `<div class="px-4 py-2 text-xs font-medium text-gray-500 bg-gray-50 border-b">${title}</div>` : ''}
      <div class="py-2">
        ${this.results.map((result, index) => `
          <button type="button" 
                  class="w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center gap-3 transition-colors ${index === this.selectedIndex ? 'bg-primary-50' : ''}"
                  data-index="${index}">
            <span class="text-2xl">${result.icon || '🔍'}</span>
            <div class="flex-1 min-w-0">
              <div class="font-medium text-gray-900 truncate">${result.name}</div>
              ${result.category ? `<div class="text-xs text-gray-500">${result.category}</div>` : ''}
              ${result.count ? `<div class="text-xs text-gray-500">${result.count} ta kompaniya</div>` : ''}
            </div>
            ${result.type === 'recent' ? `
              <button type="button" class="p-1 hover:bg-gray-200 rounded" data-action="remove" onclick="event.stopPropagation();">
                <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            ` : ''}
          </button>
        `).join('')}
      </div>
    `;
    
    // Add click handlers
    this.dropdown.querySelectorAll('[data-index]').forEach(btn => {
      btn.addEventListener('click', () => {
        const index = parseInt(btn.dataset.index);
        this.selectResult(this.results[index]);
      });
    });
    
    // Add remove handlers for recent searches
    this.dropdown.querySelectorAll('[data-action="remove"]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const index = parseInt(btn.parentElement.dataset.index);
        this.removeRecentSearch(this.results[index].name);
        this.showRecentSearches();
      });
    });
    
    this.open();
  }
  
  updateSelection() {
    this.dropdown.querySelectorAll('[data-index]').forEach((btn, index) => {
      if (index === this.selectedIndex) {
        btn.classList.add('bg-primary-50');
        btn.scrollIntoView({ block: 'nearest' });
      } else {
        btn.classList.remove('bg-primary-50');
      }
    });
  }
  
  selectResult(result) {
    if (result.type === 'recent') {
      this.input.value = result.name;
    } else {
      this.input.value = result.name;
      this.saveRecentSearch(result.name);
    }
    
    this.close();
    
    if (this.options.onSelect) {
      this.options.onSelect(result);
    } else {
      // Submit form if exists
      const form = this.input.closest('form');
      if (form) {
        form.submit();
      }
    }
  }
  
  open() {
    this.dropdown.classList.remove('hidden');
    this.isOpen = true;
  }
  
  close() {
    this.dropdown.classList.add('hidden');
    this.isOpen = false;
    this.selectedIndex = -1;
  }
  
  getRecentSearches() {
    try {
      const recent = localStorage.getItem(this.options.recentSearchesKey);
      return recent ? JSON.parse(recent) : [];
    } catch {
      return [];
    }
  }
  
  saveRecentSearch(query) {
    try {
      const recent = this.getRecentSearches();
      const filtered = recent.filter(q => q !== query);
      filtered.unshift(query);
      const limited = filtered.slice(0, this.options.maxRecentSearches);
      localStorage.setItem(this.options.recentSearchesKey, JSON.stringify(limited));
    } catch (error) {
      console.error('Failed to save recent search:', error);
    }
  }
  
  removeRecentSearch(query) {
    try {
      const recent = this.getRecentSearches();
      const filtered = recent.filter(q => q !== query);
      localStorage.setItem(this.options.recentSearchesKey, JSON.stringify(filtered));
    } catch (error) {
      console.error('Failed to remove recent search:', error);
    }
  }
  
  static init(selector = '[data-search-autocomplete]') {
    document.querySelectorAll(selector).forEach(input => {
      if (!input._searchAutocomplete) {
        input._searchAutocomplete = new SearchAutocomplete(input, {
          searchUrl: input.dataset.searchUrl,
          minChars: input.dataset.minChars || 2
        });
      }
    });
  }
}

window.SearchAutocomplete = SearchAutocomplete;


// ============================================
// 10. MODAL SYSTEM
// ============================================
class Modal {
  static activeModals = [];
  static scrollbarWidth = 0;
  
  constructor(options = {}) {
    this.options = {
      title: options.title || '',
      content: options.content || '',
      size: options.size || 'medium', // small, medium, large, fullscreen
      showClose: options.showClose !== false,
      closeOnBackdrop: options.closeOnBackdrop !== false,
      closeOnEsc: options.closeOnEsc !== false,
      animation: options.animation || 'fade', // fade, slide, zoom
      buttons: options.buttons || [],
      onOpen: options.onOpen || null,
      onClose: options.onClose || null,
      className: options.className || '',
      ...options
    };
    
    this.isOpen = false;
    this.backdrop = null;
    this.modal = null;
    
    this.init();
  }
  
  init() {
    // Calculate scrollbar width once
    if (Modal.scrollbarWidth === 0) {
      const scrollDiv = document.createElement('div');
      scrollDiv.style.cssText = 'width: 100px; height: 100px; overflow: scroll; position: absolute; top: -9999px;';
      document.body.appendChild(scrollDiv);
      Modal.scrollbarWidth = scrollDiv.offsetWidth - scrollDiv.clientWidth;
      document.body.removeChild(scrollDiv);
    }
    
    this.createBackdrop();
    this.createModal();
    this.attachEvents();
  }
  
  createBackdrop() {
    this.backdrop = document.createElement('div');
    this.backdrop.className = 'modal-backdrop fixed inset-0 bg-black/50 backdrop-blur-sm z-40 opacity-0 transition-opacity duration-300';
    
    if (this.options.closeOnBackdrop) {
      this.backdrop.addEventListener('click', () => this.close());
    }
  }
  
  createModal() {
    const sizeClasses = {
      small: 'max-w-md',
      medium: 'max-w-lg',
      large: 'max-w-3xl',
      xlarge: 'max-w-5xl',
      fullscreen: 'max-w-full mx-4'
    };
    
    const animationClasses = {
      fade: 'opacity-0 scale-100',
      slide: 'opacity-0 translate-y-10',
      zoom: 'opacity-0 scale-95'
    };
    
    this.modal = document.createElement('div');
    this.modal.className = `modal-container fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none`;
    
    this.modal.innerHTML = `
      <div class="modal-content bg-white rounded-2xl shadow-2xl w-full ${sizeClasses[this.options.size]} transform transition-all duration-300 ${animationClasses[this.options.animation]} pointer-events-auto ${this.options.className}" role="dialog" aria-modal="true">
        ${this.options.title ? `
          <div class="modal-header flex items-center justify-between px-6 py-4 border-b border-gray-200">
            <h3 class="text-xl font-bold text-gray-900">${this.options.title}</h3>
            ${this.options.showClose ? `
              <button type="button" class="modal-close text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-lg hover:bg-gray-100" aria-label="Close">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            ` : ''}
          </div>
        ` : ''}
        
        <div class="modal-body px-6 py-6">
          ${this.options.content}
        </div>
        
        ${this.options.buttons && this.options.buttons.length > 0 ? `
          <div class="modal-footer flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-b-2xl">
            ${this.options.buttons.map(btn => `
              <button type="button" 
                      class="modal-btn px-6 py-2.5 rounded-lg font-medium transition-colors ${btn.className || (btn.primary ? 'bg-primary-600 hover:bg-primary-700 text-white' : 'bg-gray-200 hover:bg-gray-300 text-gray-700')}"
                      data-action="${btn.action || 'close'}">
                ${btn.text}
              </button>
            `).join('')}
          </div>
        ` : ''}
      </div>
    `;
    
    // Add click handlers for buttons
    this.modal.querySelectorAll('.modal-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const action = btn.dataset.action;
        const buttonConfig = this.options.buttons.find(b => b.action === action);
        
        if (buttonConfig && buttonConfig.onClick) {
          const result = buttonConfig.onClick();
          if (result !== false) {
            this.close();
          }
        } else if (action === 'close') {
          this.close();
        }
      });
    });
    
    // Close button
    const closeBtn = this.modal.querySelector('.modal-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => this.close());
    }
  }
  
  attachEvents() {
    if (this.options.closeOnEsc) {
      this.escHandler = (e) => {
        if (e.key === 'Escape' && Modal.activeModals[Modal.activeModals.length - 1] === this) {
          this.close();
        }
      };
      document.addEventListener('keydown', this.escHandler);
    }
  }
  
  open() {
    if (this.isOpen) return;
    
    // Lock body scroll
    if (Modal.activeModals.length === 0) {
      const scrollY = window.scrollY;
      document.body.style.position = 'fixed';
      document.body.style.top = `-${scrollY}px`;
      document.body.style.width = '100%';
      document.body.style.paddingRight = `${Modal.scrollbarWidth}px`;
    }
    
    // Add to DOM
    document.body.appendChild(this.backdrop);
    document.body.appendChild(this.modal);
    
    // Trigger animation
    requestAnimationFrame(() => {
      this.backdrop.classList.remove('opacity-0');
      this.backdrop.classList.add('opacity-100');
      
      const content = this.modal.querySelector('.modal-content');
      content.classList.remove('opacity-0', 'scale-95', 'scale-100', 'translate-y-10');
      content.classList.add('opacity-100', 'scale-100', 'translate-y-0');
    });
    
    this.isOpen = true;
    Modal.activeModals.push(this);
    
    // Focus first focusable element
    setTimeout(() => {
      const focusable = this.modal.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
      if (focusable) focusable.focus();
    }, 100);
    
    if (this.options.onOpen) {
      this.options.onOpen(this);
    }
  }
  
  close() {
    if (!this.isOpen) return;
    
    const content = this.modal.querySelector('.modal-content');
    const animationClasses = {
      fade: ['opacity-0', 'scale-100'],
      slide: ['opacity-0', 'translate-y-10'],
      zoom: ['opacity-0', 'scale-95']
    };
    
    this.backdrop.classList.remove('opacity-100');
    this.backdrop.classList.add('opacity-0');
    content.classList.remove('opacity-100', 'scale-100', 'translate-y-0');
    content.classList.add(...animationClasses[this.options.animation]);
    
    setTimeout(() => {
      this.backdrop.remove();
      this.modal.remove();
      
      // Remove from active modals
      const index = Modal.activeModals.indexOf(this);
      if (index > -1) {
        Modal.activeModals.splice(index, 1);
      }
      
      // Unlock body scroll if no more modals
      if (Modal.activeModals.length === 0) {
        const scrollY = document.body.style.top;
        document.body.style.position = '';
        document.body.style.top = '';
        document.body.style.width = '';
        document.body.style.paddingRight = '';
        window.scrollTo(0, parseInt(scrollY || '0') * -1);
      }
      
      if (this.escHandler) {
        document.removeEventListener('keydown', this.escHandler);
      }
      
      if (this.options.onClose) {
        this.options.onClose(this);
      }
    }, 300);
    
    this.isOpen = false;
  }
  
  // Static helper methods
  static alert(options) {
    if (typeof options === 'string') {
      options = { content: options };
    }
    
    return new Modal({
      title: options.title || 'Alert',
      content: `<p class="text-gray-700">${options.message || options.content}</p>`,
      size: 'small',
      buttons: [
        {
          text: options.buttonText || 'OK',
          primary: true,
          action: 'ok',
          onClick: options.onConfirm || null
        }
      ],
      ...options
    }).open();
  }
  
  static confirm(options) {
    if (typeof options === 'string') {
      options = { content: options };
    }
    
    return new Modal({
      title: options.title || 'Confirm',
      content: `<p class="text-gray-700">${options.message || options.content}</p>`,
      size: 'small',
      buttons: [
        {
          text: options.cancelText || 'Cancel',
          action: 'cancel',
          onClick: options.onCancel || null
        },
        {
          text: options.confirmText || 'Confirm',
          primary: true,
          className: options.danger ? 'bg-red-600 hover:bg-red-700 text-white' : '',
          action: 'confirm',
          onClick: options.onConfirm || null
        }
      ],
      ...options
    }).open();
  }
  
  static show(options) {
    return new Modal(options).open();
  }
}

window.Modal = Modal;


// ============================================
// 11. IMAGE LIGHTBOX
// ============================================
class ImageLightbox {
  constructor(images, startIndex = 0) {
    this.images = Array.isArray(images) ? images : [images];
    this.currentIndex = startIndex;
    this.modal = null;
    
    this.init();
  }
  
  init() {
    this.createLightbox();
    this.attachEvents();
    this.show();
  }
  
  createLightbox() {
    const image = this.images[this.currentIndex];
    const imageUrl = typeof image === 'string' ? image : image.url || image.src;
    const imageAlt = typeof image === 'string' ? '' : image.alt || '';
    
    this.modal = new Modal({
      title: '',
      content: `
        <div class="lightbox-container relative">
          <div class="lightbox-image-wrapper flex items-center justify-center min-h-[400px] max-h-[80vh]">
            <img src="${imageUrl}" 
                 alt="${imageAlt}" 
                 class="lightbox-image max-w-full max-h-[80vh] object-contain rounded-lg"
                 style="cursor: zoom-in;">
          </div>
          
          ${this.images.length > 1 ? `
            <div class="lightbox-controls flex items-center justify-between mt-4">
              <button type="button" class="lightbox-prev px-4 py-2 bg-gray-800 text-white rounded-lg hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed" ${this.currentIndex === 0 ? 'disabled' : ''}>
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
                </svg>
              </button>
              
              <span class="text-gray-600 font-medium">${this.currentIndex + 1} / ${this.images.length}</span>
              
              <button type="button" class="lightbox-next px-4 py-2 bg-gray-800 text-white rounded-lg hover:bg-gray-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed" ${this.currentIndex === this.images.length - 1 ? 'disabled' : ''}>
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
              </button>
            </div>
          ` : ''}
        </div>
      `,
      size: 'xlarge',
      className: 'lightbox-modal',
      showClose: true,
      closeOnBackdrop: true,
      animation: 'zoom'
    });
  }
  
  attachEvents() {
    const modalElement = this.modal.modal;
    
    // Navigation buttons
    const prevBtn = modalElement.querySelector('.lightbox-prev');
    const nextBtn = modalElement.querySelector('.lightbox-next');
    
    if (prevBtn) {
      prevBtn.addEventListener('click', () => this.prev());
    }
    
    if (nextBtn) {
      nextBtn.addEventListener('click', () => this.next());
    }
    
    // Keyboard navigation
    this.keyHandler = (e) => {
      if (e.key === 'ArrowLeft') this.prev();
      if (e.key === 'ArrowRight') this.next();
    };
    document.addEventListener('keydown', this.keyHandler);
    
    // Zoom on click
    const img = modalElement.querySelector('.lightbox-image');
    if (img) {
      img.addEventListener('click', () => {
        if (img.style.cursor === 'zoom-in') {
          img.style.transform = 'scale(1.5)';
          img.style.cursor = 'zoom-out';
        } else {
          img.style.transform = 'scale(1)';
          img.style.cursor = 'zoom-in';
        }
      });
    }
    
    // Cleanup on close
    const originalOnClose = this.modal.options.onClose;
    this.modal.options.onClose = () => {
      document.removeEventListener('keydown', this.keyHandler);
      if (originalOnClose) originalOnClose();
    };
  }
  
  show() {
    this.modal.open();
  }
  
  prev() {
    if (this.currentIndex > 0) {
      this.currentIndex--;
      this.update();
    }
  }
  
  next() {
    if (this.currentIndex < this.images.length - 1) {
      this.currentIndex++;
      this.update();
    }
  }
  
  update() {
    this.modal.close();
    setTimeout(() => {
      this.createLightbox();
      this.attachEvents();
      this.show();
    }, 100);
  }
  
  static init(selector = '[data-lightbox]') {
    document.querySelectorAll(selector).forEach(element => {
      element.style.cursor = 'pointer';
      
      element.addEventListener('click', (e) => {
        e.preventDefault();
        
        const group = element.dataset.lightboxGroup;
        
        if (group) {
          // Find all images in the same group
          const groupImages = Array.from(document.querySelectorAll(`[data-lightbox-group="${group}"]`));
          const images = groupImages.map(el => ({
            url: el.dataset.lightbox || el.src || el.href,
            alt: el.alt || el.title || ''
          }));
          const startIndex = groupImages.indexOf(element);
          
          new ImageLightbox(images, startIndex);
        } else {
          // Single image
          const imageUrl = element.dataset.lightbox || element.src || element.href;
          new ImageLightbox([{ url: imageUrl, alt: element.alt || '' }]);
        }
      });
    });
  }
}

window.ImageLightbox = ImageLightbox;


// ============================================
// 12. COPY TO CLIPBOARD UTILITY
// ============================================
class CopyToClipboard {
  static copy(text, successMessage = 'Nusxa olindi!') {
    if (navigator.clipboard && window.isSecureContext) {
      // Modern approach
      return navigator.clipboard.writeText(text)
        .then(() => {
          Toast.success(successMessage);
          return true;
        })
        .catch(err => {
          console.error('Copy failed:', err);
          Toast.error('Nusxa olib bo\'lmadi');
          return false;
        });
    } else {
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      
      try {
        const successful = document.execCommand('copy');
        document.body.removeChild(textArea);
        
        if (successful) {
          Toast.success(successMessage);
          return true;
        } else {
          Toast.error('Nusxa olib bo\'lmadi');
          return false;
        }
      } catch (err) {
        console.error('Copy failed:', err);
        document.body.removeChild(textArea);
        Toast.error('Nusxa olib bo\'lmadi');
        return false;
      }
    }
  }
  
  static init(selector = '[data-copy]') {
    document.querySelectorAll(selector).forEach(element => {
      element.style.cursor = 'pointer';
      
      element.addEventListener('click', (e) => {
        e.preventDefault();
        const text = element.dataset.copy || element.textContent || element.value;
        const message = element.dataset.copyMessage || 'Nusxa olindi!';
        CopyToClipboard.copy(text, message);
      });
    });
  }
}

window.CopyToClipboard = CopyToClipboard;


// ============================================
// 13. TOOLTIPS SYSTEM
// ============================================
class Tooltip {
  constructor(element, options = {}) {
    this.element = element;
    this.options = {
      content: options.content || element.dataset.tooltip || element.title || '',
      position: options.position || element.dataset.tooltipPosition || 'top',
      delay: options.delay || 200,
      className: options.className || '',
      ...options
    };
    
    this.tooltip = null;
    this.showTimeout = null;
    this.hideTimeout = null;
    
    // Clear title to avoid browser tooltip
    if (element.title) {
      element.dataset.originalTitle = element.title;
      element.removeAttribute('title');
    }
    
    this.init();
  }
  
  init() {
    this.element.addEventListener('mouseenter', () => this.show());
    this.element.addEventListener('mouseleave', () => this.hide());
    this.element.addEventListener('focus', () => this.show());
    this.element.addEventListener('blur', () => this.hide());
    
    // Touch support
    this.element.addEventListener('touchstart', (e) => {
      this.show();
      setTimeout(() => this.hide(), 2000);
    }, { passive: true });
  }
  
  show() {
    clearTimeout(this.hideTimeout);
    
    this.showTimeout = setTimeout(() => {
      if (!this.tooltip) {
        this.create();
      }
      
      this.position();
      
      requestAnimationFrame(() => {
        this.tooltip.classList.remove('opacity-0', 'scale-95');
        this.tooltip.classList.add('opacity-100', 'scale-100');
      });
    }, this.options.delay);
  }
  
  hide() {
    clearTimeout(this.showTimeout);
    
    if (this.tooltip) {
      this.tooltip.classList.remove('opacity-100', 'scale-100');
      this.tooltip.classList.add('opacity-0', 'scale-95');
      
      this.hideTimeout = setTimeout(() => {
        if (this.tooltip) {
          this.tooltip.remove();
          this.tooltip = null;
        }
      }, 200);
    }
  }
  
  create() {
    this.tooltip = document.createElement('div');
    this.tooltip.className = `tooltip fixed z-50 px-3 py-2 bg-gray-900 text-white text-sm rounded-lg shadow-lg pointer-events-none transform transition-all duration-200 opacity-0 scale-95 ${this.options.className}`;
    this.tooltip.textContent = this.options.content;
    
    // Arrow
    const arrow = document.createElement('div');
    arrow.className = 'tooltip-arrow absolute w-2 h-2 bg-gray-900 transform rotate-45';
    this.tooltip.appendChild(arrow);
    
    document.body.appendChild(this.tooltip);
  }
  
  position() {
    if (!this.tooltip) return;
    
    const rect = this.element.getBoundingClientRect();
    const tooltipRect = this.tooltip.getBoundingClientRect();
    const arrow = this.tooltip.querySelector('.tooltip-arrow');
    const offset = 8;
    
    let top, left;
    
    switch (this.options.position) {
      case 'top':
        top = rect.top - tooltipRect.height - offset;
        left = rect.left + (rect.width - tooltipRect.width) / 2;
        if (arrow) {
          arrow.style.bottom = '-4px';
          arrow.style.left = '50%';
          arrow.style.transform = 'translateX(-50%) rotate(45deg)';
        }
        break;
        
      case 'bottom':
        top = rect.bottom + offset;
        left = rect.left + (rect.width - tooltipRect.width) / 2;
        if (arrow) {
          arrow.style.top = '-4px';
          arrow.style.left = '50%';
          arrow.style.transform = 'translateX(-50%) rotate(45deg)';
        }
        break;
        
      case 'left':
        top = rect.top + (rect.height - tooltipRect.height) / 2;
        left = rect.left - tooltipRect.width - offset;
        if (arrow) {
          arrow.style.right = '-4px';
          arrow.style.top = '50%';
          arrow.style.transform = 'translateY(-50%) rotate(45deg)';
        }
        break;
        
      case 'right':
        top = rect.top + (rect.height - tooltipRect.height) / 2;
        left = rect.right + offset;
        if (arrow) {
          arrow.style.left = '-4px';
          arrow.style.top = '50%';
          arrow.style.transform = 'translateY(-50%) rotate(45deg)';
        }
        break;
    }
    
    // Keep tooltip in viewport
    const padding = 8;
    if (left < padding) left = padding;
    if (left + tooltipRect.width > window.innerWidth - padding) {
      left = window.innerWidth - tooltipRect.width - padding;
    }
    if (top < padding) top = padding;
    
    this.tooltip.style.top = `${top}px`;
    this.tooltip.style.left = `${left}px`;
  }
  
  static init(selector = '[data-tooltip]') {
    document.querySelectorAll(selector).forEach(element => {
      if (!element._tooltip) {
        element._tooltip = new Tooltip(element);
      }
    });
  }
}

window.Tooltip = Tooltip;


// ============================================
// 14. SCROLL TO TOP BUTTON
// ============================================
class ScrollToTop {
  static instance = null;
  
  static init(options = {}) {
    if (ScrollToTop.instance) return ScrollToTop.instance;
    
    const defaults = {
      showAfter: 300,
      scrollDuration: 600,
      position: 'bottom-right', // bottom-right, bottom-left
      className: '',
      ...options
    };
    
    // Create button
    const button = document.createElement('button');
    button.id = 'scroll-to-top';
    button.className = `fixed ${defaults.position === 'bottom-left' ? 'left-6' : 'right-6'} bottom-6 w-12 h-12 bg-primary-600 hover:bg-primary-700 text-white rounded-full shadow-lg hover:shadow-xl transform transition-all duration-300 opacity-0 scale-0 z-40 ${defaults.className}`;
    button.setAttribute('aria-label', 'Scroll to top');
    button.innerHTML = `
      <svg class="w-6 h-6 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"/>
      </svg>
    `;
    
    document.body.appendChild(button);
    
    // Show/hide on scroll
    let isVisible = false;
    const toggleButton = () => {
      const shouldShow = window.scrollY > defaults.showAfter;
      
      if (shouldShow && !isVisible) {
        button.classList.remove('opacity-0', 'scale-0');
        button.classList.add('opacity-100', 'scale-100');
        isVisible = true;
      } else if (!shouldShow && isVisible) {
        button.classList.remove('opacity-100', 'scale-100');
        button.classList.add('opacity-0', 'scale-0');
        isVisible = false;
      }
    };
    
    window.addEventListener('scroll', toggleButton, { passive: true });
    toggleButton(); // Initial check
    
    // Click to scroll
    button.addEventListener('click', () => {
      const start = window.scrollY;
      const startTime = performance.now();
      
      const scroll = (currentTime) => {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / defaults.scrollDuration, 1);
        
        // Easing function (ease-out)
        const easeOut = 1 - Math.pow(1 - progress, 3);
        
        window.scrollTo(0, start * (1 - easeOut));
        
        if (progress < 1) {
          requestAnimationFrame(scroll);
        }
      };
      
      requestAnimationFrame(scroll);
    });
    
    ScrollToTop.instance = { button, toggleButton };
    return ScrollToTop.instance;
  }
}

window.ScrollToTop = ScrollToTop;


// ============================================
// 15. FAVORITES/BOOKMARK SYSTEM
// ============================================
class Favorites {
  static STORAGE_KEY = 'fikrly_favorites';
  
  static getAll() {
    try {
      const favorites = localStorage.getItem(Favorites.STORAGE_KEY);
      return favorites ? JSON.parse(favorites) : [];
    } catch {
      return [];
    }
  }
  
  static isFavorite(companyId) {
    const favorites = Favorites.getAll();
    return favorites.includes(String(companyId));
  }
  
  static add(companyId, companyData = {}) {
    const favorites = Favorites.getAll();
    const id = String(companyId);
    
    if (!favorites.includes(id)) {
      favorites.push(id);
      localStorage.setItem(Favorites.STORAGE_KEY, JSON.stringify(favorites));
      
      // Store company metadata
      if (companyData.name) {
        const metadata = Favorites.getMetadata();
        metadata[id] = {
          name: companyData.name,
          slug: companyData.slug,
          rating: companyData.rating,
          category: companyData.category,
          addedAt: new Date().toISOString()
        };
        localStorage.setItem(Favorites.STORAGE_KEY + '_meta', JSON.stringify(metadata));
      }
      
      Favorites.updateUI(id, true);
      Toast.success('Sevimlilar ro\'yxatiga qo\'shildi!');
      return true;
    }
    return false;
  }
  
  static remove(companyId) {
    const favorites = Favorites.getAll();
    const id = String(companyId);
    const index = favorites.indexOf(id);
    
    if (index > -1) {
      favorites.splice(index, 1);
      localStorage.setItem(Favorites.STORAGE_KEY, JSON.stringify(favorites));
      
      // Remove metadata
      const metadata = Favorites.getMetadata();
      delete metadata[id];
      localStorage.setItem(Favorites.STORAGE_KEY + '_meta', JSON.stringify(metadata));
      
      Favorites.updateUI(id, false);
      Toast.info('Sevimlilardan o\'chirildi');
      return true;
    }
    return false;
  }
  
  static toggle(companyId, companyData = {}) {
    if (Favorites.isFavorite(companyId)) {
      return Favorites.remove(companyId);
    } else {
      return Favorites.add(companyId, companyData);
    }
  }
  
  static getMetadata() {
    try {
      const meta = localStorage.getItem(Favorites.STORAGE_KEY + '_meta');
      return meta ? JSON.parse(meta) : {};
    } catch {
      return {};
    }
  }
  
  static getCount() {
    return Favorites.getAll().length;
  }
  
  static clear() {
    localStorage.removeItem(Favorites.STORAGE_KEY);
    localStorage.removeItem(Favorites.STORAGE_KEY + '_meta');
    document.querySelectorAll('[data-favorite-btn]').forEach(btn => {
      Favorites.updateUI(btn.dataset.favoriteBtn, false);
    });
    Toast.success('Barcha sevimlilar o\'chirildi');
  }
  
  static updateUI(companyId, isFavorite) {
    document.querySelectorAll(`[data-favorite-btn="${companyId}"]`).forEach(btn => {
      const icon = btn.querySelector('.favorite-icon');
      const text = btn.querySelector('.favorite-text');
      
      if (isFavorite) {
        btn.classList.add('is-favorite');
        if (icon) {
          icon.setAttribute('fill', 'currentColor');
        }
        if (text) {
          text.textContent = text.dataset.activeText || 'Saqlangan';
        }
      } else {
        btn.classList.remove('is-favorite');
        if (icon) {
          icon.setAttribute('fill', 'none');
        }
        if (text) {
          text.textContent = text.dataset.inactiveText || 'Saqlash';
        }
      }
    });
    
    // Update count badges
    const count = Favorites.getCount();
    document.querySelectorAll('.favorites-count').forEach(badge => {
      badge.textContent = count;
      badge.style.display = count > 0 ? '' : 'none';
    });
  }
  
  static init(selector = '[data-favorite-btn]') {
    document.querySelectorAll(selector).forEach(btn => {
      const companyId = btn.dataset.favoriteBtn;
      const isFavorite = Favorites.isFavorite(companyId);
      
      // Set initial state
      Favorites.updateUI(companyId, isFavorite);
      
      // Add click handler
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        
        const companyData = {
          name: btn.dataset.companyName,
          slug: btn.dataset.companySlug,
          rating: btn.dataset.companyRating,
          category: btn.dataset.companyCategory
        };
        
        Favorites.toggle(companyId, companyData);
      });
    });
  }
}

window.Favorites = Favorites;


// ============================================
// 16. RECENT VIEWS HISTORY
// ============================================
class RecentViews {
  static STORAGE_KEY = 'fikrly_recent_views';
  static MAX_ITEMS = 20;
  
  static getAll() {
    try {
      const views = localStorage.getItem(RecentViews.STORAGE_KEY);
      return views ? JSON.parse(views) : [];
    } catch {
      return [];
    }
  }
  
  static add(companyData) {
    if (!companyData.id || !companyData.name) return;
    
    const views = RecentViews.getAll();
    const id = String(companyData.id);
    
    // Remove if already exists
    const filtered = views.filter(v => v.id !== id);
    
    // Add to beginning
    filtered.unshift({
      id: id,
      name: companyData.name,
      slug: companyData.slug,
      rating: companyData.rating,
      category: companyData.category,
      image: companyData.image,
      viewedAt: new Date().toISOString()
    });
    
    // Keep only MAX_ITEMS
    const limited = filtered.slice(0, RecentViews.MAX_ITEMS);
    
    localStorage.setItem(RecentViews.STORAGE_KEY, JSON.stringify(limited));
  }
  
  static clear() {
    localStorage.removeItem(RecentViews.STORAGE_KEY);
    Toast.success('Tarix tozalandi');
  }
  
  static render(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const views = RecentViews.getAll();
    
    if (views.length === 0) {
      container.innerHTML = `
        <div class="text-center py-8 text-gray-500">
          <svg class="w-16 h-16 mx-auto mb-3 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <p class="font-medium">Tarix bo'sh</p>
          <p class="text-sm mt-1">Siz hali hech qanday kompaniyaga kirmadingiz</p>
        </div>
      `;
      return;
    }
    
    container.innerHTML = views.map(view => `
      <a href="/company/${view.slug}/" class="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors group">
        ${view.image ? `
          <img src="${view.image}" alt="${view.name}" class="w-12 h-12 rounded-lg object-cover">
        ` : `
          <div class="w-12 h-12 rounded-lg bg-gray-200 flex items-center justify-center">
            <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
            </svg>
          </div>
        `}
        <div class="flex-1 min-w-0">
          <h4 class="font-medium text-gray-900 truncate group-hover:text-primary-600 transition-colors">${view.name}</h4>
          <div class="flex items-center gap-2 text-sm text-gray-500">
            ${view.rating ? `
              <span class="flex items-center gap-1">
                <svg class="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
                </svg>
                ${parseFloat(view.rating).toFixed(1)}
              </span>
            ` : ''}
            ${view.category ? `<span>• ${view.category}</span>` : ''}
          </div>
        </div>
      </a>
    `).join('');
  }
}

window.RecentViews = RecentViews;


// ============================================
// 17. BREADCRUMBS COMPONENT
// ============================================
class Breadcrumbs {
  static render(items, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = `
      <nav class="flex items-center space-x-2 text-sm" aria-label="Breadcrumb">
        ${items.map((item, index) => `
          <div class="flex items-center">
            ${index > 0 ? `
              <svg class="w-4 h-4 text-gray-400 mx-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
              </svg>
            ` : ''}
            ${item.url && index < items.length - 1 ? `
              <a href="${item.url}" class="text-gray-600 hover:text-primary-600 transition-colors">
                ${item.icon ? `<svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">${item.icon}</svg>` : ''}
                ${item.label}
              </a>
            ` : `
              <span class="text-gray-900 font-medium">
                ${item.icon ? `<svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">${item.icon}</svg>` : ''}
                ${item.label}
              </span>
            `}
          </div>
        `).join('')}
      </nav>
    `;
  }
  
  static init() {
    // Auto-detect from data attributes
    document.querySelectorAll('[data-breadcrumbs]').forEach(container => {
      try {
        const items = JSON.parse(container.dataset.breadcrumbs);
        Breadcrumbs.render(items, container.id);
      } catch (e) {
        console.error('Invalid breadcrumbs data:', e);
      }
    });
  }
}

window.Breadcrumbs = Breadcrumbs;


// ============================================
// 18. EMPTY STATES
// ============================================
class EmptyState {
  static render(container, options = {}) {
    const defaults = {
      icon: 'search',
      title: 'Hech narsa topilmadi',
      message: 'Qidiruv mezonlarini o\'zgartirib ko\'ring',
      actionText: null,
      actionUrl: null,
      suggestions: []
    };
    
    const config = { ...defaults, ...options };
    
    const icons = {
      search: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>',
      empty: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>',
      reviews: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"/>',
      favorites: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>',
      error: '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>'
    };
    
    const iconPath = icons[config.icon] || icons.empty;
    
    const html = `
      <div class="flex flex-col items-center justify-center py-12 px-4 text-center">
        <svg class="w-20 h-20 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          ${iconPath}
        </svg>
        <h3 class="text-xl font-semibold text-gray-900 mb-2">${config.title}</h3>
        <p class="text-gray-600 max-w-md mb-6">${config.message}</p>
        
        ${config.suggestions.length > 0 ? `
          <div class="bg-gray-50 rounded-lg p-4 max-w-md w-full mb-6">
            <h4 class="font-medium text-gray-900 mb-3 text-sm">Takliflar:</h4>
            <ul class="text-sm text-gray-600 space-y-2 text-left">
              ${config.suggestions.map(s => `<li class="flex items-start gap-2">
                <svg class="w-5 h-5 text-gray-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"/>
                </svg>
                ${s}
              </li>`).join('')}
            </ul>
          </div>
        ` : ''}
        
        ${config.actionText && config.actionUrl ? `
          <a href="${config.actionUrl}" class="px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors">
            ${config.actionText}
          </a>
        ` : ''}
      </div>
    `;
    
    if (typeof container === 'string') {
      const elem = document.getElementById(container);
      if (elem) elem.innerHTML = html;
    } else {
      container.innerHTML = html;
    }
  }
  
  static noResults(container, query = '') {
    EmptyState.render(container, {
      icon: 'search',
      title: 'Hech narsa topilmadi',
      message: query ? `"${query}" bo'yicha natija yo'q` : 'Qidiruv uchun kalit so\'z kiriting',
      suggestions: [
        'Imlo xatolarini tekshiring',
        'Boshqa kalit so\'zlarni sinab ko\'ring',
        'Umumiyroq qidiruv so\'zlarini ishlating'
      ]
    });
  }
  
  static noReviews(container) {
    EmptyState.render(container, {
      icon: 'reviews',
      title: 'Hali sharhlar yo\'q',
      message: 'Bu kompaniya haqida birinchi sharh yozuvchi bo\'ling!',
      actionText: 'Sharh yozish',
      actionUrl: '#write-review'
    });
  }
  
  static noFavorites(container) {
    EmptyState.render(container, {
      icon: 'favorites',
      title: 'Sevimlilar bo\'sh',
      message: 'Siz hali hech qanday kompaniyani saqlamadingiz',
      actionText: 'Kompaniyalarni ko\'rish',
      actionUrl: '/businesses/'
    });
  }
}

window.EmptyState = EmptyState;


// ============================================
// 19. REVIEW VOTING SYSTEM
// ============================================
class ReviewVoting {
  static init() {
    document.querySelectorAll('[data-review-vote]').forEach(container => {
      const reviewId = container.dataset.reviewVote;
      const helpfulBtn = container.querySelector('[data-vote="helpful"]');
      const notHelpfulBtn = container.querySelector('[data-vote="not_helpful"]');
      const countEl = container.querySelector('.helpful-count');
      
      if (helpfulBtn) {
        helpfulBtn.addEventListener('click', () => {
          ReviewVoting.vote(reviewId, 'helpful', helpfulBtn, notHelpfulBtn, countEl);
        });
      }
      
      if (notHelpfulBtn) {
        notHelpfulBtn.addEventListener('click', () => {
          ReviewVoting.vote(reviewId, 'not_helpful', notHelpfulBtn, helpfulBtn, countEl);
        });
      }
    });
  }
  
  static async vote(reviewId, voteType, clickedBtn, otherBtn, countEl) {
    // Check if already voted from localStorage
    const storageKey = `review_vote_${reviewId}`;
    const existingVote = localStorage.getItem(storageKey);
    
    if (existingVote === voteType) {
      Toast.info('Siz allaqachon ovoz berdingiz');
      return;
    }
    
    try {
      const response = await fetch(`/api/reviews/${reviewId}/vote/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': ReviewVoting.getCsrfToken()
        },
        body: JSON.stringify({ vote_type: voteType })
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Update UI
        clickedBtn.classList.add('voted');
        otherBtn.classList.remove('voted');
        
        if (countEl && data.helpful_count !== undefined) {
          countEl.textContent = data.helpful_count;
        }
        
        // Store vote
        localStorage.setItem(storageKey, voteType);
        
        Toast.success(voteType === 'helpful' ? 'Foydali deb belgilandi!' : 'Qayd etildi');
      } else {
        Toast.error(data.error || 'Xatolik yuz berdi');
      }
    } catch (error) {
      console.error('Vote error:', error);
      // Fallback: client-side only
      clickedBtn.classList.add('voted');
      otherBtn.classList.remove('voted');
      localStorage.setItem(storageKey, voteType);
      
      if (countEl) {
        const current = parseInt(countEl.textContent) || 0;
        countEl.textContent = voteType === 'helpful' ? current + 1 : current - 1;
      }
    }
  }
  
  static getCsrfToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === 'csrftoken') return value;
    }
    return '';
  }
  
  static restoreVotedState() {
    document.querySelectorAll('[data-review-vote]').forEach(container => {
      const reviewId = container.dataset.reviewVote;
      const vote = localStorage.getItem(`review_vote_${reviewId}`);
      
      if (vote) {
        const btn = container.querySelector(`[data-vote="${vote}"]`);
        if (btn) btn.classList.add('voted');
      }
    });
  }
}

window.ReviewVoting = ReviewVoting;


// ============================================
// 20. REVIEW FILTERS & SORTING
// ============================================
class ReviewFilters {
  constructor(options = {}) {
    this.container = options.container || document.getElementById('reviews-container');
    this.reviews = [];
    this.filters = {
      rating: 'all', // all, 5, 4, 3, 2, 1
      sort: 'newest' // newest, oldest, helpful, rating_high, rating_low
    };
    
    this.init();
  }
  
  init() {
    // Collect all reviews
    if (this.container) {
      this.reviews = Array.from(this.container.querySelectorAll('[data-review-item]')).map(el => ({
        element: el,
        rating: parseInt(el.dataset.reviewRating || 0),
        date: el.dataset.reviewDate || '',
        helpful: parseInt(el.dataset.reviewHelpful || 0),
        id: el.dataset.reviewId
      }));
    }
    
    // Set up filter controls
    this.initRatingFilter();
    this.initSortDropdown();
  }
  
  initRatingFilter() {
    document.querySelectorAll('[data-rating-filter]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const rating = btn.dataset.ratingFilter;
        this.setRatingFilter(rating);
        
        // Update active state
        document.querySelectorAll('[data-rating-filter]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      });
    });
  }
  
  initSortDropdown() {
    const sortSelect = document.getElementById('review-sort');
    if (sortSelect) {
      sortSelect.addEventListener('change', (e) => {
        this.setSortOrder(e.target.value);
      });
    }
  }
  
  setRatingFilter(rating) {
    this.filters.rating = rating;
    this.applyFilters();
  }
  
  setSortOrder(sort) {
    this.filters.sort = sort;
    this.applyFilters();
  }
  
  applyFilters() {
    let filtered = [...this.reviews];
    
    // Filter by rating
    if (this.filters.rating !== 'all') {
      const targetRating = parseInt(this.filters.rating);
      filtered = filtered.filter(r => r.rating === targetRating);
    }
    
    // Sort
    switch (this.filters.sort) {
      case 'oldest':
        filtered.sort((a, b) => a.date.localeCompare(b.date));
        break;
      case 'helpful':
        filtered.sort((a, b) => b.helpful - a.helpful);
        break;
      case 'rating_high':
        filtered.sort((a, b) => b.rating - a.rating);
        break;
      case 'rating_low':
        filtered.sort((a, b) => a.rating - b.rating);
        break;
      case 'newest':
      default:
        filtered.sort((a, b) => b.date.localeCompare(a.date));
        break;
    }
    
    // Ensure container has flex display for ordering
    if (this.container) {
      this.container.style.display = 'flex';
      this.container.style.flexDirection = 'column';
    }
    
    // Hide all reviews first
    this.reviews.forEach(r => r.element.style.display = 'none');
    
    // Hide empty state if it exists
    const emptyState = document.getElementById('reviews-empty-state');
    if (emptyState) {
      emptyState.style.display = 'none';
    }
    
    // Show filtered reviews in sorted order
    if (filtered.length > 0) {
      filtered.forEach((r, index) => {
        r.element.style.display = '';
        r.element.style.order = index;
      });
      
      // Update count
      this.updateCount(filtered.length, this.reviews.length);
    } else {
      // Show empty state
      this.showEmptyState();
    }
  }
  
  updateCount(shown, total) {
    const countEl = document.getElementById('reviews-count');
    if (countEl) {
      countEl.textContent = `${shown} ta sharh ko'rsatilmoqda (jami ${total} ta)`;
    }
  }
  
  showEmptyState() {
    const emptyState = document.getElementById('reviews-empty-state');
    if (emptyState) {
      emptyState.style.display = 'block';
    } else {
      // Create empty state
      const div = document.createElement('div');
      div.id = 'reviews-empty-state';
      div.className = 'col-span-full';
      EmptyState.render(div, {
        icon: 'reviews',
        title: 'Hech qanday sharh topilmadi',
        message: 'Ushbu filtrga mos keladigan sharhlar yo\'q',
        suggestions: ['Boshqa reytingni tanlang', 'Barcha sharhlarni ko\'rish uchun "Barchasi"ni bosing']
      });
      this.container.appendChild(div);
    }
    
    this.updateCount(0, this.reviews.length);
  }
}

window.ReviewFilters = ReviewFilters;


// ============================================
// AUTO-INITIALIZE
// ============================================
document.addEventListener('DOMContentLoaded', function() {
  // Initialize lazy loading for images
  LazyImage.init();
  
  // Auto-initialize star ratings
  document.querySelectorAll('[data-star-rating]').forEach(container => {
    const rating = parseFloat(container.dataset.starRating) || 0;
    const readonly = container.hasAttribute('data-readonly');
    const size = container.dataset.size || 'medium';
    const showCount = container.hasAttribute('data-show-count');
    
    new StarRating(container, {
      initialRating: rating,
      readonly: readonly,
      size: size,
      showCount: showCount,
      onChange: (rating) => {
        // Update hidden input if exists
        const input = container.querySelector('input[type="hidden"]') || 
                     container.parentElement.querySelector('input[name="rating"]');
        if (input) {
          input.value = rating;
        }
      }
    });
  });
  
  // Auto-initialize infinite scroll
  const infiniteContainer = document.querySelector('[data-infinite-scroll]');
  if (infiniteContainer) {
    const urlTemplate = infiniteContainer.dataset.urlTemplate;
    const nextPage = infiniteContainer.dataset.nextPage;
    
    if (urlTemplate && nextPage) {
      new InfiniteScroll({
        container: infiniteContainer,
        loadMoreUrl: urlTemplate.replace('PAGE_NUM', nextPage),
        threshold: 300
      });
    }
  }
  
  // Initialize character counters
  CharacterCounter.init();
  
  // Initialize search autocomplete
  SearchAutocomplete.init();
  
  // Initialize loading bar (creates singleton)
  LoadingBar.init();
  
  // Initialize tooltips
  Tooltip.init();
  
  // Initialize copy buttons
  CopyToClipboard.init();
  
  // Initialize image lightbox
  ImageLightbox.init();
  
  // Initialize scroll to top button
  ScrollToTop.init();
  
  // Add loading bar to all page navigations
  window.addEventListener('beforeunload', () => {
    LoadingBar.start();
  });
  
  // Add loading bar to fetch requests
  const originalFetch = window.fetch;
  window.fetch = function(...args) {
    LoadingBar.start();
    return originalFetch.apply(this, args)
      .then(response => {
        LoadingBar.complete();
        return response;
      })
      .catch(error => {
        LoadingBar.complete();
        throw error;
      });
  };
  
  // Convert Django messages to toasts
  const djangoMessages = document.querySelectorAll('.django-message, .messages .alert');
  djangoMessages.forEach(msg => {
    let type = 'info';
    if (msg.classList.contains('success') || msg.classList.contains('alert-success')) type = 'success';
    if (msg.classList.contains('error') || msg.classList.contains('alert-error') || msg.classList.contains('alert-danger')) type = 'error';
    if (msg.classList.contains('warning') || msg.classList.contains('alert-warning')) type = 'warning';
    
    const text = msg.textContent.trim();
    if (text) {
      Toast.show(text, type);
      msg.style.display = 'none';
    }
  });

  // Auto-initialize form validation on forms with data-validate attribute
  const validatableForms = document.querySelectorAll('form[data-validate]');
  validatableForms.forEach(form => {
    new FormValidator(form);
  });

  // Add loading states to forms
  document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
      const submitBtn = this.querySelector('button[type="submit"]');
      if (submitBtn && !submitBtn.disabled) {
        submitBtn.disabled = true;
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = `
          <svg class="animate-spin -ml-1 mr-2 h-4 w-4 inline-block" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span>Yuklanmoqda...</span>
        `;
        
        // Re-enable after 10 seconds as fallback
        setTimeout(() => {
          submitBtn.disabled = false;
          submitBtn.innerHTML = originalText;
        }, 10000);
      }
    });
  });
  
  // Initialize favorites system
  Favorites.init();
  
  // Initialize breadcrumbs
  Breadcrumbs.init();
  
  // Track recent view if on company page
  const companyData = document.querySelector('[data-company-data]');
  if (companyData) {
    try {
      const data = JSON.parse(companyData.dataset.companyData);
      RecentViews.add(data);
    } catch (e) {
      console.error('Failed to track recent view:', e);
    }
  }
  
  // Render recent views if container exists
  const recentViewsContainer = document.getElementById('recent-views-list');
  if (recentViewsContainer) {
    RecentViews.render('recent-views-list');
  }
  
  // Initialize review voting
  ReviewVoting.init();
  ReviewVoting.restoreVotedState();
  
  // Initialize review filters if on company detail page
  if (document.getElementById('reviews-container')) {
    window.reviewFilters = new ReviewFilters();
  }
});


// ============================================
// 21. SOCIAL SHARE COMPONENT
// ============================================
class SocialShare {
  constructor() {
    this.init();
  }
  
  init() {
    // Add share buttons to company pages
    const companyHeader = document.querySelector('[data-company-id]');
    if (companyHeader) {
      this.addShareButtons(companyHeader);
    }
    
    // Listen for share button clicks
    document.addEventListener('click', (e) => {
      const shareBtn = e.target.closest('[data-share-type]');
      if (shareBtn) {
        e.preventDefault();
        this.share(shareBtn.dataset.shareType);
      }
    });
  }
  
  addShareButtons(container) {
    const existingShare = container.querySelector('.social-share-buttons');
    if (existingShare) return;
    
    const shareContainer = document.createElement('div');
    shareContainer.className = 'social-share-buttons flex items-center gap-2 mt-4';
    shareContainer.setAttribute('role', 'group');
    shareContainer.setAttribute('aria-label', 'Ijtimoiy tarmoqlarda ulashish');
    
    shareContainer.innerHTML = `
      <span class="text-sm text-gray-600 font-medium">Ulashish:</span>
      <button data-share-type="telegram" 
              class="share-btn p-2 rounded-full bg-blue-500 hover:bg-blue-600 text-white transition-colors"
              aria-label="Telegram'da ulashish"
              title="Telegram'da ulashish">
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.562 8.161c-.18 1.897-.962 6.502-1.359 8.627-.168.9-.5 1.201-.82 1.23-.697.064-1.226-.461-1.901-.903-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.015-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.139-5.062 3.345-.479.329-.913.489-1.302.481-.428-.009-1.252-.242-1.865-.442-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.831-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635.099-.002.321.023.465.141.121.098.154.231.17.324.016.094.036.308.02.475z"/>
        </svg>
      </button>
      
      <button data-share-type="facebook" 
              class="share-btn p-2 rounded-full bg-blue-600 hover:bg-blue-700 text-white transition-colors"
              aria-label="Facebook'da ulashish"
              title="Facebook'da ulashish">
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
          <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
        </svg>
      </button>
      
      <button data-share-type="twitter" 
              class="share-btn p-2 rounded-full bg-sky-500 hover:bg-sky-600 text-white transition-colors"
              aria-label="Twitter'da ulashish"
              title="Twitter'da ulashish">
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
          <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
        </svg>
      </button>
      
      <button data-share-type="whatsapp" 
              class="share-btn p-2 rounded-full bg-green-500 hover:bg-green-600 text-white transition-colors"
              aria-label="WhatsApp'da ulashish"
              title="WhatsApp'da ulashish">
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
          <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
        </svg>
      </button>
      
      <button data-share-type="copy" 
              class="share-btn p-2 rounded-full bg-gray-500 hover:bg-gray-600 text-white transition-colors"
              aria-label="Havolani nusxalash"
              title="Havolani nusxalash">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
        </svg>
      </button>
      
      ${this.supportsNativeShare() ? `
        <button data-share-type="native" 
                class="share-btn p-2 rounded-full bg-purple-500 hover:bg-purple-600 text-white transition-colors"
                aria-label="Ulashish"
                title="Ulashish">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z"/>
          </svg>
        </button>
      ` : ''}
    `;
    
    container.appendChild(shareContainer);
  }
  
  share(type) {
    const url = window.location.href;
    const title = document.title;
    const description = document.querySelector('meta[name="description"]')?.content || '';
    
    const shareUrls = {
      telegram: `https://t.me/share/url?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`,
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
      twitter: `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`,
      whatsapp: `https://wa.me/?text=${encodeURIComponent(title + ' ' + url)}`,
    };
    
    switch(type) {
      case 'copy':
        this.copyToClipboard(url);
        break;
      case 'native':
        this.nativeShare(title, description, url);
        break;
      default:
        if (shareUrls[type]) {
          window.open(shareUrls[type], '_blank', 'width=600,height=400');
        }
    }
  }
  
  copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
      Toast.show('Havola nusxalandi!', 'success');
    }).catch(() => {
      Toast.show('Nusxalashda xatolik', 'error');
    });
  }
  
  async nativeShare(title, text, url) {
    try {
      await navigator.share({ title, text, url });
    } catch (err) {
      if (err.name !== 'AbortError') {
        Toast.show('Ulashishda xatolik', 'error');
      }
    }
  }
  
  supportsNativeShare() {
    return navigator.share !== undefined;
  }
}


// ============================================
// 22. ACCESSIBILITY ENHANCEMENTS
// ============================================
class AccessibilityManager {
  constructor() {
    this.init();
  }
  
  init() {
    this.addSkipLinks();
    this.enhanceKeyboardNavigation();
    this.addARIALiveRegions();
    this.improveFocusIndicators();
    this.addKeyboardShortcuts();
  }
  
  addSkipLinks() {
    if (document.querySelector('.skip-links')) return;
    
    const skipLinks = document.createElement('div');
    skipLinks.className = 'skip-links';
    skipLinks.innerHTML = `
      <a href="#main-content" class="skip-link">Asosiy tarkibga o'tish</a>
      <a href="#navigation" class="skip-link">Navigatsiyaga o'tish</a>
      <a href="#search" class="skip-link">Qidiruvga o'tish</a>
    `;
    
    // Add CSS for skip links
    const style = document.createElement('style');
    style.textContent = `
      .skip-link {
        position: absolute;
        top: -40px;
        left: 0;
        background: #000;
        color: #fff;
        padding: 8px;
        text-decoration: none;
        z-index: 100;
      }
      .skip-link:focus {
        top: 0;
      }
    `;
    
    document.head.appendChild(style);
    document.body.insertBefore(skipLinks, document.body.firstChild);
    
    // Add IDs to main elements if missing
    const mainContent = document.querySelector('main');
    if (mainContent && !mainContent.id) {
      mainContent.id = 'main-content';
    }
    
    const nav = document.querySelector('nav');
    if (nav && !nav.id) {
      nav.id = 'navigation';
    }
    
    const search = document.querySelector('input[type="search"], input[name="search"], input[name="q"]');
    if (search && !search.id) {
      search.id = 'search';
    }
  }
  
  enhanceKeyboardNavigation() {
    // Make modal closeable with Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        const modal = document.querySelector('.modal-overlay:not(.hidden)');
        if (modal) {
          modal.classList.add('hidden');
          document.body.classList.remove('modal-open');
        }
        
        const lightbox = document.querySelector('.image-lightbox-overlay');
        if (lightbox) {
          lightbox.remove();
        }
      }
    });
    
    // Trap focus in modals
    document.addEventListener('keydown', (e) => {
      if (e.key !== 'Tab') return;
      
      const modal = document.querySelector('.modal-overlay:not(.hidden) .modal-content');
      if (!modal) return;
      
      const focusableElements = modal.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      const firstFocusable = focusableElements[0];
      const lastFocusable = focusableElements[focusableElements.length - 1];
      
      if (e.shiftKey) {
        if (document.activeElement === firstFocusable) {
          e.preventDefault();
          lastFocusable.focus();
        }
      } else {
        if (document.activeElement === lastFocusable) {
          e.preventDefault();
          firstFocusable.focus();
        }
      }
    });
  }
  
  addARIALiveRegions() {
    // Add live region for dynamic content announcements
    if (document.querySelector('#aria-live-region')) return;
    
    const liveRegion = document.createElement('div');
    liveRegion.id = 'aria-live-region';
    liveRegion.setAttribute('role', 'status');
    liveRegion.setAttribute('aria-live', 'polite');
    liveRegion.setAttribute('aria-atomic', 'true');
    liveRegion.className = 'sr-only';
    
    const style = document.createElement('style');
    style.textContent = `
      .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border-width: 0;
      }
    `;
    document.head.appendChild(style);
    document.body.appendChild(liveRegion);
    
    // Announce toast messages to screen readers
    window.announceToScreenReader = (message) => {
      liveRegion.textContent = message;
      setTimeout(() => liveRegion.textContent = '', 1000);
    };
  }
  
  improveFocusIndicators() {
    const style = document.createElement('style');
    style.textContent = `
      *:focus-visible {
        outline: 2px solid #667eea;
        outline-offset: 2px;
        border-radius: 4px;
      }
      
      button:focus-visible,
      a:focus-visible {
        outline: 2px solid #667eea;
        outline-offset: 2px;
      }
      
      input:focus-visible,
      textarea:focus-visible,
      select:focus-visible {
        border-color: #667eea;
        ring: 2px;
        ring-color: #667eea;
      }
    `;
    document.head.appendChild(style);
  }
  
  addKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // Ctrl/Cmd + K for search
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="search"], input[name="search"], input[name="q"]');
        if (searchInput) {
          searchInput.focus();
          announceToScreenReader('Qidiruv oynasi ochildi');
        }
      }
      
      // Ctrl/Cmd + / for help
      if ((e.ctrlKey || e.metaKey) && e.key === '/') {
        e.preventDefault();
        this.showKeyboardShortcutsHelp();
      }
    });
  }
  
  showKeyboardShortcutsHelp() {
    const helpContent = `
      <div class="space-y-4">
        <h3 class="text-xl font-semibold mb-4">Klaviatura yorliqlari</h3>
        <div class="grid grid-cols-2 gap-3">
          <div class="flex justify-between items-center p-2 bg-gray-50 rounded">
            <span>Qidiruv</span>
            <kbd class="px-2 py-1 bg-white border rounded text-sm">Ctrl+K</kbd>
          </div>
          <div class="flex justify-between items-center p-2 bg-gray-50 rounded">
            <span>Yordam</span>
            <kbd class="px-2 py-1 bg-white border rounded text-sm">Ctrl+/</kbd>
          </div>
          <div class="flex justify-between items-center p-2 bg-gray-50 rounded">
            <span>Modalni yopish</span>
            <kbd class="px-2 py-1 bg-white border rounded text-sm">Esc</kbd>
          </div>
          <div class="flex justify-between items-center p-2 bg-gray-50 rounded">
            <span>Sahifa yuqoriga</span>
            <kbd class="px-2 py-1 bg-white border rounded text-sm">Home</kbd>
          </div>
        </div>
        <p class="text-sm text-gray-600 mt-4">
          Bu yorliqlar saytda navigatsiya qilishni osonlashtiradi.
        </p>
      </div>
    `;
    
    if (window.Modal) {
      Modal.show('Klaviatura yorliqlari', helpContent);
    }
  }
}


// ============================================
// 23. DARK MODE
// ============================================
class DarkMode {
  constructor() {
    this.darkModeEnabled = localStorage.getItem('darkMode') === 'enabled';
    this.init();
  }
  
  init() {
    // Apply saved preference
    if (this.darkModeEnabled) {
      document.documentElement.classList.add('dark');
    }
    
    // Create toggle button
    this.createToggleButton();
    
    // Listen for system preference changes
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    mediaQuery.addEventListener('change', (e) => {
      if (!localStorage.getItem('darkMode')) {
        this.setDarkMode(e.matches);
      }
    });
  }
  
  createToggleButton() {
    const existingBtn = document.querySelector('.dark-mode-toggle');
    if (existingBtn) return;
    
    const button = document.createElement('button');
    button.className = 'dark-mode-toggle fixed bottom-24 right-8 bg-gray-800 dark:bg-gray-200 text-white dark:text-gray-800 p-3 rounded-full shadow-lg hover:scale-110 transition-all duration-300 z-40';
    button.setAttribute('aria-label', 'Toggle dark mode');
    button.setAttribute('title', 'Dark Mode');
    
    button.innerHTML = `
      <svg class="w-6 h-6 dark-mode-icon-sun hidden dark:block" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd"/>
      </svg>
      <svg class="w-6 h-6 dark-mode-icon-moon block dark:hidden" fill="currentColor" viewBox="0 0 20 20">
        <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"/>
      </svg>
    `;
    
    button.addEventListener('click', () => this.toggle());
    document.body.appendChild(button);
  }
  
  toggle() {
    this.darkModeEnabled = !this.darkModeEnabled;
    this.setDarkMode(this.darkModeEnabled);
  }
  
  setDarkMode(enabled) {
    this.darkModeEnabled = enabled;
    
    if (enabled) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('darkMode', 'enabled');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('darkMode', 'disabled');
    }
    
    // Announce to screen readers
    if (window.announceToScreenReader) {
      announceToScreenReader(enabled ? 'Dark mode faollashtirildi' : 'Light mode faollashtirildi');
    }
  }
}


// ============================================
// 24. GAMIFICATION DISPLAY
// ============================================
class GamificationDisplay {
  constructor() {
    this.init();
  }
  
  init() {
    this.showLevelBadge();
    this.animateProgressBar();
    this.showAchievementNotifications();
  }
  
  showLevelBadge() {
    const levelContainer = document.querySelector('[data-user-level]');
    if (!levelContainer) return;
    
    const level = parseInt(levelContainer.dataset.userLevel);
    const xp = parseInt(levelContainer.dataset.userXp);
    const nextLevelXp = parseInt(levelContainer.dataset.nextLevelXp);
    
    if (!levelContainer.querySelector('.level-badge')) {
      const badge = document.createElement('div');
      badge.className = 'level-badge inline-flex items-center gap-2 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-4 py-2 rounded-full font-semibold shadow-lg';
      badge.innerHTML = `
        <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
        </svg>
        <span>Level ${level}</span>
      `;
      levelContainer.appendChild(badge);
    }
  }
  
  animateProgressBar() {
    const progressBars = document.querySelectorAll('[data-progress]');
    progressBars.forEach(bar => {
      const progress = parseFloat(bar.dataset.progress);
      const progressFill = bar.querySelector('.progress-fill');
      
      if (progressFill) {
        setTimeout(() => {
          progressFill.style.width = `${progress}%`;
        }, 100);
      }
    });
  }
  
  showAchievementNotifications() {
    const newBadges = document.querySelectorAll('[data-new-badge]');
    newBadges.forEach((badge, index) => {
      setTimeout(() => {
        this.showBadgeUnlocked(
          badge.dataset.badgeName,
          badge.dataset.badgeDescription,
          badge.dataset.badgeIcon
        );
      }, 1000 + (index * 2000));
    });
  }
  
  showBadgeUnlocked(name, description, icon) {
    const notification = document.createElement('div');
    notification.className = 'achievement-notification fixed top-20 right-8 bg-gradient-to-r from-yellow-400 to-orange-500 text-white p-6 rounded-xl shadow-2xl transform translate-x-full transition-all duration-500 z-50 max-w-sm';
    notification.innerHTML = `
      <div class="flex items-start gap-4">
        <div class="text-4xl">${icon || '🏆'}</div>
        <div class="flex-1">
          <div class="font-bold text-lg mb-1">Badge olindi!</div>
          <div class="font-semibold">${name}</div>
          <div class="text-sm opacity-90 mt-1">${description}</div>
        </div>
        <button onclick="this.parentElement.parentElement.remove()" class="text-white opacity-75 hover:opacity-100">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
      </div>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => notification.classList.remove('translate-x-full'), 100);
    setTimeout(() => {
      notification.classList.add('translate-x-full');
      setTimeout(() => notification.remove(), 500);
    }, 5000);
  }
}


// ============================================
// 25. IMAGE UPLOAD WITH PREVIEW
// ============================================
class ImageUploader {
  constructor(selector, options = {}) {
    this.container = document.querySelector(selector);
    if (!this.container) return;
    
    this.options = {
      maxFiles: options.maxFiles || 5,
      maxSize: options.maxSize || 5 * 1024 * 1024, // 5MB
      acceptedTypes: options.acceptedTypes || ['image/jpeg', 'image/png', 'image/webp'],
      uploadUrl: options.uploadUrl,
      onUpload: options.onUpload || null,
      ...options
    };
    
    this.files = [];
    this.init();
  }
  
  init() {
    this.createDropZone();
    this.attachEventListeners();
  }
  
  createDropZone() {
    this.container.innerHTML = `
      <div class="image-upload-dropzone border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center cursor-pointer hover:border-primary-500 transition-colors">
        <input type="file" class="hidden" id="fileInput" accept="image/*" multiple>
        <div class="upload-icon mb-4">
          <svg class="w-16 h-16 mx-auto text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"/>
          </svg>
        </div>
        <div class="upload-text">
          <p class="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">Rasmlarni yuklash</p>
          <p class="text-sm text-gray-500 dark:text-gray-400">Bosing yoki rasmlarni bu yerga torting</p>
          <p class="text-xs text-gray-400 dark:text-gray-500 mt-2">Maksimal ${this.options.maxFiles} ta rasm, har biri ${this.formatFileSize(this.options.maxSize)} gacha</p>
        </div>
      </div>
      <div class="image-preview-container mt-4 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4"></div>
    `;
  }
  
  attachEventListeners() {
    const dropZone = this.container.querySelector('.image-upload-dropzone');
    const fileInput = this.container.querySelector('#fileInput');
    
    // Click to upload
    dropZone.addEventListener('click', () => fileInput.click());
    
    // File input change
    fileInput.addEventListener('change', (e) => {
      this.handleFiles(Array.from(e.target.files));
      e.target.value = ''; // Reset input
    });
    
    // Drag and drop
    dropZone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropZone.classList.add('border-primary-500', 'bg-primary-50', 'dark:bg-primary-900/20');
    });
    
    dropZone.addEventListener('dragleave', () => {
      dropZone.classList.remove('border-primary-500', 'bg-primary-50', 'dark:bg-primary-900/20');
    });
    
    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('border-primary-500', 'bg-primary-50', 'dark:bg-primary-900/20');
      this.handleFiles(Array.from(e.dataTransfer.files));
    });
  }
  
  handleFiles(newFiles) {
    // Filter valid files
    const validFiles = newFiles.filter(file => {
      if (!this.options.acceptedTypes.includes(file.type)) {
        Toast.show(`${file.name} noto'g'ri format`, 'error');
        return false;
      }
      if (file.size > this.options.maxSize) {
        Toast.show(`${file.name} juda katta`, 'error');
        return false;
      }
      return true;
    });
    
    // Check max files
    if (this.files.length + validFiles.length > this.options.maxFiles) {
      Toast.show(`Maksimal ${this.options.maxFiles} ta rasm`, 'warning');
      validFiles.splice(this.options.maxFiles - this.files.length);
    }
    
    // Add files
    validFiles.forEach(file => {
      this.files.push(file);
      this.createPreview(file);
    });
    
    // Upload if URL provided
    if (this.options.uploadUrl && validFiles.length > 0) {
      this.uploadFiles(validFiles);
    }
  }
  
  createPreview(file) {
    const reader = new FileReader();
    const previewContainer = this.container.querySelector('.image-preview-container');
    const fileIndex = this.files.indexOf(file);
    
    const previewItem = document.createElement('div');
    previewItem.className = 'relative group';
    previewItem.dataset.fileIndex = fileIndex;
    
    reader.onload = (e) => {
      previewItem.innerHTML = `
        <div class="aspect-square rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-800">
          <img src="${e.target.result}" alt="Preview" class="w-full h-full object-cover">
        </div>
        <button class="remove-image absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white rounded-full p-2 opacity-0 group-hover:opacity-100 transition-opacity"
                data-file-index="${fileIndex}"
                aria-label="O'chirish">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
          </svg>
        </button>
        <div class="file-name text-xs text-gray-600 dark:text-gray-400 mt-1 truncate">${file.name}</div>
        <div class="file-size text-xs text-gray-400 dark:text-gray-500">${this.formatFileSize(file.size)}</div>
      `;
      
      // Remove button
      previewItem.querySelector('.remove-image').addEventListener('click', (e) => {
        e.stopPropagation();
        this.removeFile(fileIndex);
      });
    };
    
    reader.readAsDataURL(file);
    previewContainer.appendChild(previewItem);
  }
  
  removeFile(index) {
    this.files.splice(index, 1);
    const previewContainer = this.container.querySelector('.image-preview-container');
    const previewItem = previewContainer.querySelector(`[data-file-index="${index}"]`);
    if (previewItem) {
      previewItem.remove();
    }
    
    // Update indices
    const remainingPreviews = previewContainer.querySelectorAll('[data-file-index]');
    remainingPreviews.forEach((item, idx) => {
      item.dataset.fileIndex = idx;
      const removeBtn = item.querySelector('.remove-image');
      if (removeBtn) {
        removeBtn.dataset.fileIndex = idx;
      }
    });
  }
  
  async uploadFiles(files) {
    const formData = new FormData();
    files.forEach((file, idx) => {
      formData.append('images', file);
    });
    
    // Add CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (csrfToken) {
      formData.append('csrfmiddlewaretoken', csrfToken);
    }
    
    try {
      LoadingBar.start();
      const response = await fetch(this.options.uploadUrl, {
        method: 'POST',
        body: formData,
        headers: {
          'X-CSRFToken': csrfToken
        }
      });
      
      const data = await response.json();
      
      if (data.success) {
        Toast.show(data.message || 'Rasmlar yuklandi', 'success');
        if (this.options.onUpload) {
          this.options.onUpload(data);
        }
      } else {
        Toast.show(data.error || 'Yuklashda xatolik', 'error');
      }
    } catch (error) {
      Toast.show('Yuklashda xatolik', 'error');
      console.error('Upload error:', error);
    } finally {
      LoadingBar.complete();
    }
  }
  
  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  }
  
  getFiles() {
    return this.files;
  }
  
  clear() {
    this.files = [];
    const previewContainer = this.container.querySelector('.image-preview-container');
    if (previewContainer) {
      previewContainer.innerHTML = '';
    }
  }
}


// ============================================
// INITIALIZE ALL COMPONENTS
// ============================================
document.addEventListener('DOMContentLoaded', () => {
  // Initialize existing components
  if (document.querySelector('[data-skeleton]')) {
    window.skeletonLoader = new SkeletonLoader();
  }
  
  if (document.querySelector('form')) {
    window.formValidator = new FormValidator();
  }
  
  if (document.querySelectorAll('.star-rating').length) {
    window.starRating = new StarRating();
  }
  
  // Infinite scroll disabled: do not auto-initialize even if data attributes remain.
  
  if (document.querySelector('[data-lazy-src]')) {
    window.lazyImageLoader = new LazyImageLoader();
  }
  
  if (document.querySelector('.char-counter-input')) {
    window.characterCounter = new CharacterCounter();
  }
  
  if (document.querySelector('.search-autocomplete')) {
    window.searchAutocomplete = new SearchAutocomplete();
  }
  
  if (document.querySelectorAll('[data-lightbox]').length) {
    window.imageLightbox = new ImageLightbox();
  }
  
  if (document.querySelectorAll('[data-copy]').length) {
    window.copyToClipboard = new CopyToClipboard();
  }
  
  if (document.querySelectorAll('[data-tooltip]').length) {
    window.tooltip = new Tooltip();
  }
  
  if (document.querySelector('[data-company-id]')) {
    window.favorites = new Favorites();
    window.recentViews = new RecentViews();
  }
  
  if (document.querySelector('.breadcrumb')) {
    window.breadcrumbManager = new BreadcrumbManager();
  }
  
  if (document.querySelector('[data-review-filters]')) {
    window.reviewFilters = new ReviewFilters();
  }
  
  // Initialize new components
  window.socialShare = new SocialShare();
  window.a11yManager = new AccessibilityManager();
  
  // Initialize scroll to top
  window.scrollToTop = new ScrollToTop();
  
  // Initialize loading bar on page navigation
  window.loadingBar = new LoadingBar();
  window.addEventListener('beforeunload', () => {
    LoadingBar.start();
  });
  
  // Initialize dark mode
  window.darkMode = new DarkMode();
  
  // Initialize gamification display
  if (document.querySelector('[data-user-level]')) {
    window.gamification = new GamificationDisplay();
  }
});
