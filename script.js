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
const searchContainer = document.getElementById("search-container");
const searchBox = document.getElementById("search-box");

content.innerHTML += content.innerHTML;
let scrollPos = 0;
let speed = .8;
let paused = false;

function scrollMarquee() {
    if(!paused) {
        scrollPos += speed;
        if (scrollPos >= content.scrollHeight) {
            console.log(container.style.height);
            scrollPos = -container.offsetHeight;
        }
        content.style.transform = `translateY(${-scrollPos}px)`;
    }
    requestAnimationFrame(scrollMarquee);
}

scrollMarquee();

container.addEventListener("click", () => {
    paused = !paused;
    if (paused) {
        // Become scrollable
        container.style.overflowY = "auto";
        content.style.transform = ""; // reset transform
        searchContainer.style.display = "block";
    } else {
    // Resume auto-scroll
        container.scrollTop = 0;
        container.style.overflow = "hidden";
        searchContainer.style.display = "none";
        scrollPos = 0;
        
        document.querySelectorAll(".item").forEach(div => {
            div.style.display = "block";
        });
        searchBox.value = "";
    }
});

searchBox.addEventListener("input", () => {
    const query = searchBox.value.toLowerCase();
    document.querySelectorAll(".item").forEach(div => {
        const text = div.innerText.toLowerCase();
        div.style.display = text.includes(query) ? "block" : "none";
    });
});