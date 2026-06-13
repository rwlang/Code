// Animate bird cards in on scroll using IntersectionObserver
document.addEventListener('DOMContentLoaded', () => {
  const cards = document.querySelectorAll('.bird-card, .hotspot, .season');

  if (!('IntersectionObserver' in window)) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  cards.forEach(card => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(20px)';
    card.style.transition = 'opacity 0.5s ease, transform 0.5s ease, box-shadow 0.25s ease, border-left-color 0.25s ease';
    observer.observe(card);
  });
});
