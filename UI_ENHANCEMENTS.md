# UI Enhancements - Quick Reference

## 🎨 Features Implemented

### 1. **Toast Notifications**
Modern, non-intrusive notifications that auto-dismiss.

**Usage:**
```javascript
// Basic usage
Toast.success('Muvaffaqiyatli saqlandi!');
Toast.error('Xatolik yuz berdi!');
Toast.warning('Diqqat!');
Toast.info('Ma\'lumot');

// Custom duration (default: 3000ms)
Toast.show('Custom message', 'success', 5000);
```

**Django Messages Auto-Conversion:**
All Django messages (from `messages.success()`, etc.) are automatically converted to toasts!

```python
# In your view
messages.success(request, 'Review successfully saved!')
# This will appear as a toast notification automatically
```

---

### 2. **Skeleton Loaders**
Animated placeholder content while data loads.

**Usage:**
```javascript
// Show skeletons in a container
Skeleton.showInContainer('myContainerId', 'card', 3);  // 3 card skeletons
Skeleton.showInContainer('listContainer', 'list', 5);  // 5 list skeletons
Skeleton.showInContainer('textArea', 'text', 4);       // 4 text lines

// Hide skeletons
Skeleton.hide('myContainerId');

// Get HTML directly
const cardHtml = Skeleton.card();
const listHtml = Skeleton.list();
const textHtml = Skeleton.text(5);  // 5 lines
```

**Example Loading Pattern:**
```javascript
// Show skeleton while loading
Skeleton.showInContainer('results', 'card', 6);

// Fetch data
fetch('/api/companies')
  .then(res => res.json())
  .then(data => {
    document.getElementById('results').innerHTML = renderResults(data);
    Toast.success('Ma\'lumotlar yuklandi!');
  });
```

---

### 3. **Form Validation**
Real-time form validation with inline error messages.

**Enable on Forms:**
```html
<!-- Auto-initialize with data-validate attribute -->
<form data-validate method="post">
  <!-- Your form fields -->
</form>
```

**Field Attributes:**
```html
<input 
  type="email" 
  required 
  minlength="5"
  data-required-msg="Email kiriting"
  data-email-msg="To'g'ri email kiriting"
  data-minlength-msg="Kamida 5 ta belgi"
>
```

**Supported Validations:**
- `required` - Field must have a value
- `type="email"` - Must be valid email
- `type="tel"` - Must be valid phone (+998XXXXXXXXX)
- `minlength` - Minimum character length
- `maxlength` - Maximum character length
- `pattern` - Custom regex pattern

**Manual Validation:**
```javascript
// Initialize manually
const validator = new FormValidator('#myForm');

// Validate single field
validator.validateField(inputElement);

// Validate entire form
if (validator.validateForm()) {
  // Form is valid, submit
}

// Clear errors
validator.reset();
```

---

## 🚀 Quick Start

### 1. Forms Auto-Enhancement
All forms now have:
- ✅ Loading spinner on submit buttons
- ✅ Auto-disable on submit (prevents double-submit)
- ✅ Re-enables after 10 seconds as fallback

### 2. Django Messages
All Django messages automatically become toasts - no code changes needed!

### 3. Demo Page
Visit `/ui-demo/` to see all features in action and test them interactively.

---

## 📝 Examples

### Example 1: Search with Skeleton
```javascript
document.getElementById('searchBtn').addEventListener('click', async () => {
  // Show skeletons
  Skeleton.showInContainer('searchResults', 'card', 6);
  
  // Fetch results
  const results = await fetch('/search?q=' + query).then(r => r.json());
  
  // Display results
  document.getElementById('searchResults').innerHTML = results.html;
  
  Toast.success(`${results.count} ta natija topildi`);
});
```

### Example 2: Form Submission with Validation
```html
<form data-validate onsubmit="handleSubmit(event)">
  <div class="form-group">
    <input 
      type="text" 
      name="company_name"
      required
      minlength="3"
      data-required-msg="Kompaniya nomini kiriting"
      class="w-full px-4 py-3 border rounded-lg"
    >
  </div>
  <button type="submit">Saqlash</button>
</form>

<script>
function handleSubmit(e) {
  e.preventDefault();
  // Form is already validated by FormValidator
  
  fetch('/api/save', {
    method: 'POST',
    body: new FormData(e.target)
  })
  .then(res => res.json())
  .then(data => {
    Toast.success('Muvaffaqiyatli saqlandi!');
    e.target.reset();
  })
  .catch(err => {
    Toast.error('Xatolik yuz berdi');
  });
}
</script>
```

### Example 3: Dynamic Content Loading
```javascript
async function loadMoreReviews(page) {
  const container = document.getElementById('reviews');
  
  // Show loading skeletons
  for (let i = 0; i < 3; i++) {
    container.insertAdjacentHTML('beforeend', Skeleton.list());
  }
  
  // Load data
  const reviews = await fetch(`/reviews?page=${page}`).then(r => r.json());
  
  // Remove skeletons
  container.querySelectorAll('.animate-pulse').forEach(el => el.remove());
  
  // Add real content
  reviews.forEach(review => {
    container.insertAdjacentHTML('beforeend', renderReview(review));
  });
  
  if (reviews.length > 0) {
    Toast.info(`${reviews.length} ta yangi sharh yuklandi`);
  }
}
```

---

## 🎯 Best Practices

1. **Always show feedback** - Use toasts for user actions
2. **Use skeletons for > 500ms loads** - Better perceived performance
3. **Validate on blur, not on input** - Less annoying for users
4. **Custom error messages** - Use data attributes for localized messages
5. **Test with slow connection** - Use browser DevTools Network throttling

---

## 🔧 Configuration

All components are auto-initialized on `DOMContentLoaded`. No setup required!

**Customization:**
```javascript
// Change toast duration globally
Toast.show('Message', 'success', 10000); // 10 seconds

// Custom form validator options
new FormValidator(form, {
  validateOnBlur: true,
  validateOnInput: true,
  showSuccessState: false
});
```

---

## 📦 Files Added
- `/frontend/static/js/ui-enhancements.js` - Main component library
- `/frontend/templates/pages/ui_demo.html` - Interactive demo page

## 🔗 Integration
- ✅ Added to `base.html` - Available on all pages
- ✅ Forms enhanced automatically
- ✅ Django messages converted automatically
- ✅ All tests passing

---

**Questions?** Check the demo page at `/ui-demo/` or review the source code in `ui-enhancements.js`.
