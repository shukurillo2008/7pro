
// Robo Arena Main Script

document.addEventListener('DOMContentLoaded', () => {
    
    // --- Header Scroll Effect ---
    const header = document.getElementById('main-header');
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            header.style.padding = '0.5rem 0';
            header.style.background = 'rgba(10, 10, 12, 0.95)';
            header.style.boxShadow = '0 4px 20px rgba(0,0,0,0.4)';
        } else {
            header.style.padding = '1rem 0';
            header.style.background = 'rgba(10, 10, 12, 0.8)';
            header.style.boxShadow = 'none';
        }
    });

    // --- Intersection Observer for Fade In Animations ---
    const fadeElements = document.querySelectorAll('.fade-in-up');
    
    const observerOptions = {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px"
    };

    const observer = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animationPlayState = 'running';
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    fadeElements.forEach(el => {
        el.style.animationPlayState = 'paused'; // Pause initially
        observer.observe(el);
    });

    // --- Smooth Scroll for Anchor Links ---
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if(targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // --- Price Range Slider Logic ---
    const slider1 = document.getElementById("slider-1");
    const slider2 = document.getElementById("slider-2");
    const display1 = document.getElementById("range1");
    const display2 = document.getElementById("range2");
    const sliderTrack = document.querySelector(".slider-track");
    const minGap = 0;

    if (slider1 && slider2) {
        window.slideOne = function() {
            if (parseInt(slider2.value) - parseInt(slider1.value) <= minGap) {
                slider1.value = parseInt(slider2.value) - minGap;
            }
            display1.textContent = '$' + slider1.value;
            fillColor();
        }

        window.slideTwo = function() {
            if (parseInt(slider2.value) - parseInt(slider1.value) <= minGap) {
                slider2.value = parseInt(slider1.value) + minGap;
            }
            display2.textContent = '$' + slider2.value;
            fillColor();
        }

        function fillColor() {
            const percent1 = (slider1.value / slider1.max) * 100;
            const percent2 = (slider2.value / slider2.max) * 100;
            // Fallback colors if vars not readable (though they should be)
            const trackColor = '#2a2a2e'; 
            const accentColor = '#00f0ff';
            
            sliderTrack.style.background = `linear-gradient(to right, ${trackColor} ${percent1}%, ${accentColor} ${percent1}%, ${accentColor} ${percent2}%, ${trackColor} ${percent2}%)`;
        }

        // Initialize state
        slideOne();
        slideTwo();
    }
    // --- Product Carousel Logic ---
    window.moveCarousel = function(carouselId, direction) {
        const container = document.getElementById(carouselId);
        const slides = container.querySelectorAll('.carousel-slide');
        const dots = container.querySelectorAll('.dot');
        let activeIndex = 0;

        // Find current active index
        slides.forEach((slide, index) => {
            if (slide.classList.contains('active')) {
                activeIndex = index;
                slide.classList.remove('active');
            }
        });
        
        // Remove active dot
        if(dots.length > 0) dots[activeIndex].classList.remove('active');

        // Calculate new index
        let newIndex = activeIndex + direction;
        if (newIndex >= slides.length) newIndex = 0;
        if (newIndex < 0) newIndex = slides.length - 1;

        // Set new active state
        slides[newIndex].classList.add('active');
        if(dots.length > 0) dots[newIndex].classList.add('active');
    }
    // --- Product Detail Logic ---
    window.changeImage = function(src, thumbnail) {
        document.getElementById('main-product-img').src = src;
        document.getElementById('main-product-img').style.opacity = 0;
        setTimeout(() => {
            document.getElementById('main-product-img').style.opacity = 1;
        }, 50);
        
        // Update active class
        document.querySelectorAll('.thumbnail').forEach(t => t.classList.remove('active'));
        thumbnail.classList.add('active');
    }

    window.updateQty = function(change) {
        const input = document.getElementById('qty-input');
        let val = parseInt(input.value) + change;
        if(val < 1) val = 1;
        if(val > 10) val = 10;
        input.value = val;
    }

    window.switchTab = function(tabId) {
        // Buttons
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        event.target.classList.add('active');

        // Content
        document.querySelectorAll('.tab-content').forEach(content => content.classList.add('hidden'));
        document.getElementById(tabId).classList.remove('hidden');
    }
});
