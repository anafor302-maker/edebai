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
    initMusicPlayer();
});

// Music Player
function initMusicPlayer() {
    const playBtn = document.getElementById('play-btn');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const progressBar = document.querySelector('.progress-bar');
    const progressFill = document.getElementById('progress-fill');
    const volumeSlider = document.getElementById('volume-slider');
    
    if (!playBtn) return;
    
    let isPlaying = false;
    let currentTime = 0;
    let duration = 225; // 3:45 in seconds
    let volume = 70;
    let animationId = null;
    
    // Play/Pause
    playBtn.addEventListener('click', function() {
        isPlaying = !isPlaying;
        
        if (isPlaying) {
            playBtn.textContent = '⏸';
            playBtn.classList.add('playing');
            startProgress();
        } else {
            playBtn.textContent = '▶';
            playBtn.classList.remove('playing');
            stopProgress();
        }
    });
    
    // Previous Track
    if (prevBtn) {
        prevBtn.addEventListener('click', function() {
            currentTime = 0;
            updateProgress();
        });
    }
    
    // Next Track
    if (nextBtn) {
        nextBtn.addEventListener('click', function() {
            currentTime = 0;
            updateProgress();
            // Could switch to next track here
        });
    }
    
    // Progress Bar Click
    if (progressBar) {
        progressBar.addEventListener('click', function(e) {
            const rect = progressBar.getBoundingClientRect();
            const percent = (e.clientX - rect.left) / rect.width;
            currentTime = percent * duration;
            updateProgress();
        });
    }
    
    // Volume Slider
    if (volumeSlider) {
        volumeSlider.addEventListener('input', function(e) {
            volume = e.target.value;
            // Here you would adjust actual audio volume
        });
    }
    
    function startProgress() {
        function animate() {
            if (isPlaying) {
                currentTime += 0.1;
                if (currentTime >= duration) {
                    currentTime = 0;
                    isPlaying = false;
                    playBtn.textContent = '▶';
                    playBtn.classList.remove('playing');
                    return;
                }
                updateProgress();
                animationId = requestAnimationFrame(animate);
            }
        }
        animate();
    }
    
    function stopProgress() {
        if (animationId) {
            cancelAnimationFrame(animationId);
        }
    }
    
    function updateProgress() {
        const percent = (currentTime / duration) * 100;
        if (progressFill) {
            progressFill.style.width = percent + '%';
        }
        
        // Update time display
        const currentTimeEl = document.getElementById('current-time');
        const durationEl = document.getElementById('duration');
        
        if (currentTimeEl) {
            currentTimeEl.textContent = formatTime(currentTime);
        }
        if (durationEl) {
            durationEl.textContent = formatTime(duration);
        }
    }
    
    function formatTime(seconds) {
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    }
    
    // Initialize
    updateProgress();
}

// Share Functions
function shareOnTwitter() {
    const url = encodeURIComponent(window.location.href);
    const text = encodeURIComponent(document.title);
    window.open(`https://twitter.com/intent/tweet?url=${url}&text=${text}`, '_blank', 'width=550,height=420');
}

function shareOnFacebook() {
    const url = encodeURIComponent(window.location.href);
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${url}`, '_blank', 'width=550,height=420');
}

function shareOnLinkedIn() {
    const url = encodeURIComponent(window.location.href);
    window.open(`https://www.linkedin.com/sharing/share-offsite/?url=${url}`, '_blank', 'width=550,height=420');
}

function copyLink() {
    const url = window.location.href;
    
    if (navigator.clipboard) {
        navigator.clipboard.writeText(url).then(function() {
            showMessage('Link kopyalandı!', 'success');
        }).catch(function() {
            fallbackCopyLink(url);
        });
    } else {
        fallbackCopyLink(url);
    }
}

function fallbackCopyLink(text) {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    textarea.select();
    
    try {
        document.execCommand('copy');
        showMessage('Link kopyalandı!', 'success');
    } catch (err) {
        showMessage('Link kopyalanamadı', 'error');
    }
    
    document.body.removeChild(textarea);
}

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

document.addEventListener("DOMContentLoaded", function () {
    const toggleBtn = document.getElementById("audio-toggle-btn");
    const player = document.getElementById("audio-player-wrapper");

    if (!toggleBtn || !player) return;

    toggleBtn.addEventListener("click", () => {
        player.classList.toggle("audio-player-hidden");
        player.classList.toggle("audio-player-visible");
    });
});