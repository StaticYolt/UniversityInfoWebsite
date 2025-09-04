fetch("data.json")
    .then(res => res.json())
    .then(data => {
    const marquee = document.getElementById("marquee");
    data.filter(item => item.show).forEach(item => {
        const div = document.createElement("div");
        div.className = "item";
        div.innerHTML = `
        <strong>${item.title}</strong><br>
        ${item.description}<br>
        ${item.date ? `<em>${item.date}</em><br>` : ""}
        <a href="${item.link}" target="_blank">Learn More</a>
        `;
        marquee.appendChild(div);
    });
    });

const container = document.getElementById("vertical-marquee");
const content = document.getElementById("marquee");

content.innerHTML += content.innerHTML;
let scrollPos = 0;
let speed = .8;

function scrollMarquee() {
    scrollPos += speed;
    if (scrollPos >= content.scrollHeight) {
    console.log(container.style.height)
    scrollPos = -container.offsetHeight;
    }
    content.style.transform = `translateY(${-scrollPos}px)`;
    requestAnimationFrame(scrollMarquee);
}

scrollMarquee();