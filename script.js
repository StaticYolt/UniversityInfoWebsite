//create toggle whether you want event or resouce
//if there are dates for an event push it up

const container = document.getElementById("vertical-marquee");
const content = document.getElementById("marquee");
const searchContainer = document.getElementById("search-container");
const searchBox = document.getElementById("search-box");
const filterContainer = document.getElementById("filter-container");

let itemsData = [];

fetch("data.json")
  .then(res => res.json())
  .then(data => {
    itemsData = data.filter(item => item.show);
    renderItems(itemsData);

});
function renderItems(items) {
  content.innerHTML = "";
  items.forEach(item => {
    const div = document.createElement("div");
    div.className = "item";
    div.dataset.type = item.type; // save type for filtering
    div.innerHTML = `
      <strong>${item.title}</strong><br>
      ${item.description}<br>
      ${item.date ? `<em>${item.date}</em><br>` : ""}
      <a href="${item.link}" target="_blank">Learn More</a>
    `;
    content.appendChild(div);
  });
}
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
        filterContainer.style.display = "block";
    } else {
    // Resume auto-scroll
        container.scrollTop = 0;
        container.style.overflow = "hidden";
        searchContainer.style.display = "none";
        filterContainer.style.display = "none";
        scrollPos = 0;
        
        renderItems(itemsData);
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

filterContainer.addEventListener("click", e => {
  if (e.target.tagName === "BUTTON") {
    const type = e.target.dataset.type;
    document.querySelectorAll(".item").forEach(div => {
      div.style.display = div.dataset.type === type ? "block" : "none";
    });
  }
});