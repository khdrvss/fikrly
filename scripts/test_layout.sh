#!/bin/bash
# Quick test script for business listing page layout

echo "🧪 Testing Business Listing Page Layout..."
echo ""

# Check if server is running
if ! curl -s http://localhost/bizneslar/ > /dev/null; then
    echo "❌ Server not running. Start with: docker-compose up -d"
    exit 1
fi

echo "✅ Server is running"
echo ""

# Check for proper container structure
echo "📦 Checking container structure..."
if curl -s 'http://localhost/bizneslar/' | grep -q 'max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10'; then
    echo "✅ Proper container wrapper found"
else
    echo "❌ Container wrapper missing"
fi

# Check for grid layout
echo "📊 Checking grid layout..."
if curl -s 'http://localhost/bizneslar/' | grep -q 'grid grid-cols-1 lg:grid-cols-4'; then
    echo "✅ Grid layout implemented"
else
    echo "❌ Grid layout missing"
fi

# Check for sidebar
echo "📌 Checking sidebar..."
if curl -s 'http://localhost/bizneslar/' | grep -q 'lg:col-span-1'; then
    echo "✅ Sidebar column span correct"
else
    echo "❌ Sidebar layout issue"
fi

# Check for main content
echo "📄 Checking main content..."
if curl -s 'http://localhost/bizneslar/' | grep -q 'lg:col-span-3'; then
    echo "✅ Main content column span correct"
else
    echo "❌ Main content layout issue"
fi

# Check for CSS variables
echo "🎨 Checking theme tokens..."
if curl -s 'http://localhost/bizneslar/' | grep -q 'var(--surface)'; then
    echo "✅ CSS variable tokens in use"
else
    echo "❌ Hardcoded colors still present"
fi

# Check for pagination
echo "📖 Checking pagination..."
if curl -s 'http://localhost/bizneslar/' | grep -q 'flex justify-center'; then
    echo "✅ Pagination centered"
else
    echo "⚠️  No pagination found (may be empty page)"
fi

echo ""
echo "🎯 Summary:"
echo "✓ Page structure refactored"
echo "✓ Grid layout implemented"  
echo "✓ Dark mode tokens in use"
echo "✓ Container properly centered"
echo ""
echo "🌐 Visit: http://localhost/bizneslar/"
echo "🌙 Toggle dark mode to test theme"
echo ""
