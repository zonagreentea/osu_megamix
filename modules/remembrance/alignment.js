
function alignMemorial() {
    const left = document.querySelector('.remembrance-poem-left');
    const right = document.querySelector('.remembrance-poem-right');
    const heading = document.querySelector('main h1');
    const main = document.querySelector('main');

    if (!left || !right || !heading || !main) return;

    if (window.innerWidth <= 800) {
        main.style.removeProperty('--memorial-offset');
        return;
    }

    main.style.setProperty('--memorial-offset', '0px');

    const poemTop = Math.min(
        left.getBoundingClientRect().top,
        right.getBoundingClientRect().top
    );

    const headingRect = heading.getBoundingClientRect();
    const headingMiddle = headingRect.top + headingRect.height / 2;

    main.style.setProperty(
        '--memorial-offset',
        `${poemTop - headingMiddle + 160}px`
    );
}

window.addEventListener('load', alignMemorial);
window.addEventListener('resize', alignMemorial);
