// Mobile Menu Toggle
function toggleMobileMenu() {
    const mobileNavLinks = document.getElementById('mobile-nav-links');
    const backdrop = document.getElementById('mobile-menu-backdrop');
    
    if (mobileNavLinks && backdrop) {
        mobileNavLinks.classList.toggle('active');
        backdrop.classList.toggle('active');
    }
}

function closeMobileMenu() {
    const mobileNavLinks = document.getElementById('mobile-nav-links');
    const backdrop = document.getElementById('mobile-menu-backdrop');
    
    if (mobileNavLinks && backdrop) {
        mobileNavLinks.classList.remove('active');
        backdrop.classList.remove('active');
    }
}

// Newsletter Form Handler
document.addEventListener('DOMContentLoaded', function() {
    const newsletterForm = document.querySelector('.newsletter-form');
    
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const emailInput = this.querySelector('input[type="email"]');
            const button = this.querySelector('button[type="submit"]');
            const successMsg = document.getElementById('newsletter-success');
            const errorMsg = document.getElementById('newsletter-error');
            
            if (!emailInput || !button) return;
            
            const email = emailInput.value.trim();
            const originalButtonText = button.textContent;
            
            // Disable button
            button.disabled = true;
            button.textContent = 'Gönderiliyor...';
            
            try {
                // Get CSRF token
                const csrftoken = getCookie('csrftoken');
                
                const response = await fetch('/ajax/bulten-abone/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrftoken
                    },
                    body: `email=${encodeURIComponent(email)}`
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Show success message
                    if (successMsg) {
                        successMsg.textContent = '✓ ' + data.message;
                        successMsg.classList.remove('hidden');
                        
                        // Hide after 4 seconds
                        setTimeout(() => {
                            successMsg.classList.add('hidden');
                        }, 4000);
                    }
                    
                    // Clear input
                    emailInput.value = '';
                } else {
                    // Show error message
                    showMessage(data.message, 'error');
                }
            } catch (error) {
                console.error('Newsletter error:', error);
                showMessage('Bir hata oluştu. Lütfen tekrar deneyin.', 'error');
            } finally {
                // Re-enable button
                button.disabled = false;
                button.textContent = originalButtonText;
            }
        });
    }
    
    // Contact Form Handler
    const contactForm = document.querySelector('.contact-form');
    
    if (contactForm) {
        contactForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const nameInput = this.querySelector('#contact-name');
            const emailInput = this.querySelector('#contact-email');
            const messageInput = this.querySelector('#contact-message');
            const button = this.querySelector('button[type="submit"]');
            const successMsg = document.getElementById('contact-success');
            
            if (!nameInput || !emailInput || !messageInput || !button) return;
            
            const name = nameInput.value.trim();
            const email = emailInput.value.trim();
            const message = messageInput.value.trim();
            const originalButtonText = button.textContent;
            
            // Disable button
            button.disabled = true;
            button.textContent = 'Gönderiliyor...';
            
            try {
                // Get CSRF token
                const csrftoken = getCookie('csrftoken');
                
                const response = await fetch('/ajax/iletisim-gonder/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrftoken
                    },
                    body: `name=${encodeURIComponent(name)}&email=${encodeURIComponent(email)}&message=${encodeURIComponent(message)}`
                });
                
                const data = await response.json();
                
                if (data.success) {
                    // Show success message
                    if (successMsg) {
                        successMsg.textContent = '✓ ' + data.message;
                        successMsg.classList.remove('hidden');
                        
                        // Hide after 5 seconds
                        setTimeout(() => {
                            successMsg.classList.add('hidden');
                        }, 5000);
                    }
                    
                    // Clear form
                    nameInput.value = '';
                    emailInput.value = '';
                    messageInput.value = '';
                } else {
                    showMessage(data.message, 'error');
                }
            } catch (error) {
                console.error('Contact form error:', error);
                showMessage('Bir hata oluştu. Lütfen tekrar deneyin.', 'error');
            } finally {
                // Re-enable button
                button.disabled = false;
                button.textContent = originalButtonText;
            }
        });
    }
});

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Helper function to show messages
function showMessage(message, type = 'success') {
    // Create message element if doesn't exist
    let messageEl = document.querySelector('.temp-message');
    
    if (!messageEl) {
        messageEl = document.createElement('div');
        messageEl.className = 'temp-message';
        document.body.appendChild(messageEl);
    }
    
    messageEl.className = `temp-message ${type === 'error' ? 'error-message' : 'success-message'}`;
    messageEl.textContent = type === 'error' ? '✗ ' + message : '✓ ' + message;
    messageEl.style.position = 'fixed';
    messageEl.style.top = '20px';
    messageEl.style.right = '20px';
    messageEl.style.zIndex = '9999';
    messageEl.style.display = 'block';
    
    // Hide after 4 seconds
    setTimeout(() => {
        messageEl.style.display = 'none';
    }, 4000);
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        const href = this.getAttribute('href');
        
        // Skip if it's just "#"
        if (href === '#') {
            return;
        }
        
        e.preventDefault();
        
        const target = document.querySelector(href);
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Cookie Consent
function acceptCookies() {
    // Set cookie for 1 year
    const date = new Date();
    date.setTime(date.getTime() + (365 * 24 * 60 * 60 * 1000));
    const expires = "expires=" + date.toUTCString();
    document.cookie = "cookie_consent=accepted;" + expires + ";path=/";
    
    // Hide banner
    const banner = document.getElementById('cookie-consent');
    if (banner) {
        banner.style.display = 'none';
    }
}

// Check if cookie consent already given
function checkCookieConsent() {
    const consent = document.cookie.split('; ').find(row => row.startsWith('cookie_consent='));
    if (!consent) {
        const banner = document.getElementById('cookie-consent');
        if (banner) {
            banner.style.display = 'block';
        }
    }
}

// Run on page load
document.addEventListener('DOMContentLoaded', function() {
    checkCookieConsent();
});

// Add fade-in animation to elements when they come into view
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('fade-in');
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observe elements
document.addEventListener('DOMContentLoaded', function() {
    const animatedElements = document.querySelectorAll('.blog-card, .category-card, .section-title');
    animatedElements.forEach(el => observer.observe(el));
});