document.addEventListener('DOMContentLoaded', function() {
    // Animate tech stack items on scroll
    const techItems = document.querySelectorAll('.tech-item');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate__animated', 'animate__fadeInUp');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    techItems.forEach(item => {
        observer.observe(item);
    });

    // Add pulse animation to blockchain blocks on hover
    const blocks = document.querySelectorAll('.block');
    blocks.forEach(block => {
        block.addEventListener('mouseenter', () => {
            block.classList.add('animate__pulse');
        });
        block.addEventListener('mouseleave', () => {
            block.classList.remove('animate__pulse');
        });
    });
});