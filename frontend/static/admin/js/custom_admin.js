// Custom admin interactions: sidebar toggles, collapsibles, micro-interactions
document.addEventListener('DOMContentLoaded', function(){
  // Toggle collapsible system info in admin dashboard
  document.querySelectorAll('.system-collapsible .toggle').forEach(function(toggle){
    toggle.addEventListener('click', function(e){
      const wrapper = e.currentTarget.closest('.system-collapsible');
      wrapper.classList.toggle('open');
    });
  });

  // Make table rows clickable when data-href present
  document.querySelectorAll('table.activity-table tbody tr[data-href]').forEach(function(row){
    row.addEventListener('click', function(){
      const href = row.getAttribute('data-href');
      if(href) window.location.href = href;
    });
  });

  // Simple keyboard shortcut: press 'c' to focus quick-actions add button (if present)
  document.addEventListener('keydown', function(e){
    if(document.activeElement.tagName === 'INPUT' || document.activeElement.tagName === 'TEXTAREA') return;
    if(e.key === 'c' || e.key === 'C'){
      const btn = document.querySelector('.quick-actions a');
      if(btn) { btn.focus(); btn.classList.add('fade-in'); setTimeout(()=>btn.classList.remove('fade-in'),500); }
    }
  });

});

// Show a small banner when viewing filtered pending reviews
document.addEventListener('DOMContentLoaded', function(){
  try{
    const path = window.location.pathname || '';
    const qs = window.location.search || '';
    // Detect admin review changelist path (frontend app)
    if(/\/admin\/frontend\/review\//.test(path) && /is_approved__exact=0/.test(qs)){
      const container = document.getElementById('admin-filter-banner-container');
      if(container){
        const banner = document.createElement('div');
        banner.className = 'admin-filter-banner';
        banner.textContent = 'Currently viewing: Pending Reviews';
        banner.style.padding = '10px 14px';
        banner.style.borderRadius = '8px';
        banner.style.background = 'var(--red-soft, rgba(255,107,107,0.12))';
        banner.style.color = 'var(--red, #FF6B6B)';
        banner.style.margin = '16px 0';
        container.appendChild(banner);
      }
    }
  }catch(e){/* no-op */}
});
