//create toggle whether you want event or resouce
//if there are dates for an event push it up

const container = document.getElementById("vertical-marquee");
const content = document.getElementById("marquee");
const searchContainer = document.getElementById("search-container");
const searchBox = document.getElementById("search-box");
const filterContainer = document.getElementById("filter-container");

let itemsData = [];
let activeFilters = { event: true, resource: true, job: true };

// fetch("data.json")
//   .then(res => res.json())
//   .then(data => {
//     itemsData = data.filter(item => item.show);
//     updateFilterButtons();
//     renderItems(itemsData);

// });
function shuffleArray(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}

fetch("data.json")
  .then(res => res.json())
  .then(data => {
    // Filter + shuffle only "show: true"
    itemsData = shuffleArray(data.filter(item => item.show));
    updateFilterButtons();
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
    console.log(item.title)
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
        
        activeFilters = { event: true, resource: true, job: true };
        updateFilterButtons();
        renderItems(itemsData);
        searchBox.value = "";
    }
});

searchBox.addEventListener("input", () => {
  applyFilters();
});

filterContainer.addEventListener("click", e => {
  if (e.target.tagName === "BUTTON") {
    const type = e.target.dataset.type;
    activeFilters[type] = !activeFilters[type]; // toggle on/off
    updateFilterButtons();
    applyFilters();
  }
});

// Apply filters (type + search)
function applyFilters() {
  const query = searchBox.value.toLowerCase();
  document.querySelectorAll(".item").forEach(div => {
    const matchesType = activeFilters[div.dataset.type];
    const matchesSearch = div.innerText.toLowerCase().includes(query);
    div.style.display = matchesType && matchesSearch ? "block" : "none";
  });
}

// Update button styles to reflect active/inactive
function updateFilterButtons() {
  document.querySelectorAll("#filter-container button").forEach(btn => {
    const type = btn.dataset.type;
    if (activeFilters[type]) {
      btn.classList.add("active");
    } else {
      btn.classList.remove("active");
    }
  });
}