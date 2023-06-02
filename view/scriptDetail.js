const API_URI = "https://web-production-a66f.up.railway.app"
// const API_URI = "http://127.0.0.1:5000"

// function detail
function detail() {
    loadingskeletonFunction("judulDetail", "judul", true)
    loadinglistFunction("cara", "detail-cara-membuat", true)
    const urlParams = new URLSearchParams(window.location.search); 
    const id = urlParams.get('id');
    fetch(`${API_URI}/detail?id=${id}`, {
        method: "GET",
        credentials: "include",
    }).then(response => response.json())
    .then(data => {
        console.log(data, "INI DATA");
        // const doc = getElementById
        const cardJudul = document.getElementById("judulDetail");
        const kontenerfoto = document.getElementById("fotomakanan");
        const foto = document.createElement("img");
        foto.className = "rounded-t-lg object-cover w-full h-[500px]"
        kontenerfoto.appendChild(foto);
        foto.src = data.img;
        cardJudul.innerHTML = `
                    <a>
                        <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 ">${data.title}</h5>
                    </a> 
        `


        const listCaraMembuat = document.getElementById("detail-cara-membuat");
        const steps = data.steps.split("--");
        steps.forEach(step => {
            if (step === "") return;
            const div = document.createElement("div");
            div.className = "flex space-x-1"

            const span = document.createElement("span");
            span.className = "material-symbols-outlined";
            span.innerHTML = "fiber_manual_record";
            const garis = document.createElement("hr");
            garis.className = "w-full my-2 border-gray-300";
            const p = document.createElement("p");
            p.textContent = step;

            div.appendChild(span);
            div.appendChild(p);
            listCaraMembuat.appendChild(div);
            listCaraMembuat.appendChild(garis);
        })

        const listBahanElement = document.getElementById("list-bahan");
        const ingredients = data.ingredients.split("--");
        ingredients.forEach(ingredient => {
            if (ingredient === "") return;
            const li = document.createElement("li");
            li.className = "flex space-x-2";

            li.innerHTML = `
                <svg class="flex-shrink-0 w-4 h-4 text-blue-600 " fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>
                <span class="leading-tight">${ingredient}</span>
            `
            const garis = document.createElement("hr");
            garis.className = "w-full my-2 border-gray-300";
            listBahanElement.appendChild(li);
            listBahanElement.appendChild(garis);
        })
        loadinglistFunction("cara", "detail-cara-membuat", false)
    
    })
}
        
window.onload = function() {
    detail();
}

const loadingjudulElm = `
    <div role="status" class="max-w-sm animate-pulse">
        <div class="h-8 bg-gray-200 rounded-full dark:bg-gray-600 mb-4"></div>
        <span class="sr-only">Loading...</span>
    </div>
`

const loadinglistElm = `
    <div role="status" class="max-w-sm animate-pulse">
        <div class="h-5 bg-gray-200 rounded-full dark:bg-gray-600 mb-4"></div>
        <div class="h-5 bg-gray-200 rounded-full dark:bg-gray-600 mb-4"></div>
        <div class="h-5 bg-gray-200 rounded-full dark:bg-gray-600 mb-4"></div>
        <div class="h-5 bg-gray-200 rounded-full dark:bg-gray-600 mb-4"></div>
        <div class="h-5 bg-gray-200 rounded-full dark:bg-gray-600 mb-4"></div>
        <div class="h-5 bg-gray-200 rounded-full dark:bg-gray-600 mb-4"></div>
        <div class="h-5 bg-gray-200 rounded-full dark:bg-gray-600 mb-4"></div>
        <span class="sr-only">Loading...</span>
    </div>
`

loadingskeletonFunction = (idParentElm, idElm, isLoading) => {
    const parentElm = document.getElementById(idParentElm);
    const ulElm = document.getElementById(idElm);

    // create loadingjudulElm from string
    const parentloadingjudulElm = document.createElement('div');
    parentloadingjudulElm.className = "loading-judul-elm";
    parentloadingjudulElm.innerHTML = loadingjudulElm;
    

    if (isLoading) {
        // add class hidden
        ulElm.classList.add("hidden");
        parentElm.appendChild(parentloadingjudulElm);
    }

    if (!isLoading) {
        // remove class hidden
        ulElm.classList.remove("hidden");

        // remove loadingjudulElm
        const loadingjudulElmFromSelector = parentElm.getElementsByClassName("loading-judul-elm")

        for (let i = 0; i < loadingjudulElmFromSelector.length; i++) {
            const element = loadingjudulElmFromSelector[i];
            parentElm.removeChild(element);
        }

    }
    
}

loadinglistFunction = (idParentElm, idElm, isLoading) => {
    const parentElm = document.getElementById(idParentElm);
    const ulElm = document.getElementById(idElm);

    // create loadinglistElm from string
    const parentloadinglistElm = document.createElement('div');
    parentloadinglistElm.className = "loading-list-elm";
    parentloadinglistElm.innerHTML = loadinglistElm;
    

    if (isLoading) {
        // add class hidden
        ulElm.classList.add("hidden");
        parentElm.appendChild(parentloadinglistElm);
    }

    if (!isLoading) {
        // remove class hidden
        ulElm.classList.remove("hidden");

        // remove loadinglistElm
        const loadinglistElmFromSelector = parentElm.getElementsByClassName("loading-list-elm")

        for (let i = 0; i < loadinglistElmFromSelector.length; i++) {
            const element = loadinglistElmFromSelector[i];
            parentElm.removeChild(element);
        }

    }
    
}