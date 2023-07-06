// const API_URI = "https://web-production-a66f.up.railway.app"
const API_URI = "http://127.0.0.1:5000"

const BahanBumbu = "Bumbu";
const BahanSayur = "Sayur";
const BahanTambahan = "Tambahan";

let bahanPanganTambahan;
let defaultListElementTambahan = {
    [BahanBumbu]: [],
    [BahanSayur]: [],
    [BahanTambahan]: []
};;

let checkedListElement = {
    [BahanBumbu]: [],
    [BahanSayur]: [],
    [BahanTambahan]: []
};

let daftarBahan = {
    [BahanBumbu]: [],
    [BahanSayur]: [],
    [BahanTambahan]: []
}

let itemsClicked = {}

const loadingElm = `
    <div class=" flex items-center justify-center w-48 h-[360px] text-sm font-medium border rounded-lg bg-gray-300 border-white-600 text-yellow-500 shadow">
        <div role="status">
            <svg aria-hidden="true" class="w-8 h-8 mr-2 animate-spin text-gray-600 fill-[#FF8903]" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/><path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/></svg>
            <span class="sr-only">Loading...</span>
        </div>
    </div>
`

const loadingbutton = `
    <div class="animate-pulse">
        <div class="cursor-not-allowed w-full font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 bg-red-400 text-red-300 hover:text-white  ">LOADING...</div>
    </div>

`

const loadingbuttonFunction = (idParentElm, idULElm, isLoading) => {
    // loadingFunction("data-daftarbahanbumbu", "myFormBumbu", true);

    const parentElm = document.getElementById(idParentElm);
    const ulElm = document.getElementById(idULElm);

    // create loadingElm from string
    const parentLoadingElm = document.createElement('div');
    parentLoadingElm.className = "loading-elm";
    parentLoadingElm.innerHTML = loadingbutton;
    

    if (isLoading) {
        // add class hidden
        ulElm.classList.add("hidden");
        parentElm.appendChild(parentLoadingElm);
    }

    if (!isLoading) {
        // remove class hidden
        ulElm.classList.remove("hidden");

        // remove loadingElm
        const loadingElmFromSelector = parentElm.getElementsByClassName("loading-elm")

        for (let i = 0; i < loadingElmFromSelector.length; i++) {
            const element = loadingElmFromSelector[i];
            parentElm.removeChild(element);
        }

    }
    
}
const loadingFunction = (idParentElm, idULElm, isLoading) => {

    const parentElm = document.getElementById(idParentElm);
    const ulElm = document.getElementById(idULElm);

    // create loadingElm from string
    // const parentLoadingElm = document.createElement('div');
    // parentLoadingElm.className = "loading-elm";
    // parentLoadingElm.innerHTML = loadingElm;
    

    if (isLoading) {
        // add class hidden
        // ulElm.classList.add("hidden");
        // parentElm.appendChild(parentLoadingElm);
    }

    if (!isLoading) {
        // remove class hidden
        ulElm.classList.remove("hidden");

        // remove loadingElm
        const loadingElmFromSelector = parentElm.getElementsByClassName("loading-elm")

        for (let i = 0; i < loadingElmFromSelector.length; i++) {
            const element = loadingElmFromSelector[i];
            parentElm.removeChild(element);
        }

    }
    
}



function choosen(message) {
    // membuat variabel untuk menampung array
    var kumpulan_bahan = [];
    // membuat variabel untuk menampung nilai
    for (var i = 0; i < 5; i++) {
        kumpulan_bahan[i] = document.getElementById("bahan" + i).value;
    }
    
    alert(message);
}    

function getDaftarBahanBumbu() {
    loadingFunction("data-daftarbahanbumbu", "myFormBumbu", true);
    fetch(`${API_URI}/daftarbahanbumbu`)
    .then(response => response.json())
    .then(data => {
        daftarBahan[BahanBumbu] = data;
        const ulElm = document.getElementById("myFormBumbu");
        data.slice(0, 8).forEach(item => {
            const liElm = document.createElement('li');
            liElm.className   = "w-full rounded-t-lg border-transparent";
            liElm.innerHTML = `
                <div class="flex items-center pl-3 rounded-lg hover:bg-slate-200">
                    <input name="bahan" id="${item.id}-bumbu-checkbox" type="checkbox" value="${item.nama_pangan}" class="w-4 h-4 text-[#C1002D] rounded focus:ring-transparent ring-offset-transparent focus:ring-offset-transparent focus:ring-1 bg-gray-100 border-gray-500"/>
                    <label for="${item.id}-bumbu-checkbox" class="w-full py-3 ml-2 text-sm font-medium text-gray-700">${capitalizeFirstLetter(item.nama_pangan)}</label>
                </div>
            `

            ulElm.appendChild(liElm);
            defaultListElementTambahan[BahanBumbu].push(liElm);
            loadingFunction("data-daftarbahanbumbu", "myFormBumbu", false);
        })
    });
    // load on page load
}

function getDaftarBahanSayur() {
    loadingFunction("data-daftarbahansayur", "myFormSayur", true);
    fetch(`${API_URI}/daftarbahansayur`)
    .then(response => response.json())
    .then(data => {
        daftarBahan[BahanSayur] = data;
        const ulElm = document.getElementById("myFormSayur");
        data.slice(0, 8).forEach(item => {
            const liElm = document.createElement('li');
            liElm.className = "w-full rounded-t-lg border-transparent";
            liElm.innerHTML = `
                <div class="flex items-center pl-3 rounded-lg hover:bg-slate-200">
                    <input name="bahan" id="${item.id}-sayur-checkbox" type="checkbox" value="${item.nama_pangan}"class="w-4 h-4 text-[#C1002D] rounded focus:ring-transparent ring-offset-transparent focus:ring-offset-transparent focus:ring-1 bg-gray-100 border-gray-500"/>
                    <label for="${item.id}-sayur-checkbox" class="w-full py-3 ml-2 text-sm font-medium text-gray-700">${capitalizeFirstLetter(item.nama_pangan)}</label>
                </div>
            `

            ulElm.appendChild(liElm);
            defaultListElementTambahan[BahanSayur].push(liElm);
            loadingFunction("data-daftarbahansayur", "myFormSayur", false);
        })
    });
    // load on page load
}

function getDaftarBahanTambahan() {
    loadingFunction("data-daftarbahantambahan", "myFormTambahan", true);
    fetch(`${API_URI}/daftarbahantambahan`)
    .then(response => response.json())
    .then(data => {
        daftarBahan[BahanTambahan] = data;
        const ulElm = document.getElementById("myFormTambahan");
        data.slice(0, 8).forEach(item => {
            const liElm = document.createElement('li');
            liElm.className = "w-full rounded-t-lg border-transparent";
            liElm.innerHTML = `
                <div class="flex items-center pl-3 rounded-lg hover:bg-slate-200">
                    <input name="bahan" id="${item.id}-tambahan-checkbox" type="checkbox" value="${item.nama_pangan}" class="w-4 h-4 text-[#C1002D] rounded focus:ring-transparent ring-offset-transparent focus:ring-offset-transparent focus:ring-1 bg-gray-100 border-gray-500"/>
                    <label for="${item.id}-tambahan-checkbox" class="w-full py-3 ml-2 text-sm font-medium text-gray-700">${capitalizeFirstLetter(item.nama_pangan)}</label>
                </div>
            `

            ulElm.appendChild(liElm);
            defaultListElementTambahan[BahanTambahan].push(liElm);
            loadingFunction("data-daftarbahantambahan", "myFormTambahan", false);
        })
    });
    // load on page load
}

// function kapital huruf pertama
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
    // return string
}

window.onload = function() {
    initSession();
    getDaftarBahanBumbu();
    getDaftarBahanSayur();
    getDaftarBahanTambahan();
    searchHelper();
    checkboxListener();
    dropdownFunction();
}

function searchHelper(){


    const search = document.getElementById("search-dropdown");
    search.addEventListener("input", function(e) {
        const dropdownMainButton = document.getElementById("dropdown-button");
        const elementBahan = {
            [BahanBumbu]: "myFormBumbu",
            [BahanSayur]: "myFormSayur",
            [BahanTambahan]: "myFormTambahan"
        }

        const selectedDropdown = dropdownMainButton.textContent.replace(/\n/g, '');
        
        const searchValue = e.target.value; 
        const result = window.matchSorter(daftarBahan[selectedDropdown], searchValue, {
            keys: ["nama_pangan"],
            threshold: window.matchSorter.rankings.WORD_STARTS_WITH
        })

        const idElm = elementBahan[selectedDropdown];

        const ulElm = document.getElementById(idElm);
        for (let i = 0; i < ulElm.children.length; i++) {
            const child = ulElm.children[i];
            const checkbox = child.querySelector("input[type=checkbox]");
            if (checkbox.checked) {
                checkedListElement[selectedDropdown].push(child);
                child.addEventListener("change", function(e) {
                    if (!e.target.checked) {
                        checkedListElement[selectedDropdown] = checkedListElement[selectedDropdown].filter(item => {
                            return item.textContent.replace(/\n/g, '').replace(/\s+/g, ' ').trim().toLowerCase() !== e.target.value.replace(/\n/g, '').replace(/\s+/g, ' ').trim().toLowerCase()
                        });
                        const searchElm = document.getElementById("search-dropdown");
                        if (searchElm.value === ""){
                            let isContainInResult = false;
                            result.slice(0, 8).forEach(item => {
                                if (item.nama_pangan === e.target.value.replace(/\n/g, '').replace(/\s+/g, ' ').trim().toLowerCase()){
                                    isContainInResult = true;
                                }
                            })
                            if (isContainInResult) {
                                return
                            }
                        }
                        

                        const ulElmNew = document.getElementById(idElm);
                        // remove from ulElmNew
                        let newChildList = []
                        for (let i = 0; i < ulElmNew.children.length; i++) {
                            const childNew = ulElmNew.children[i];
                            let InDefaultList = defaultListElementTambahan[selectedDropdown].filter(item => item.textContent.replace(/\n/g, '').replace(/\s+/g, ' ').trim().toLowerCase() === childNew.textContent.replace(/\n/g, '').replace(/\s+/g, ' ').trim().toLowerCase());
                            if (childNew !== child || InDefaultList.length > 0) {

                                const labelElm = childNew.querySelector("label");
                                labelElm.textContent = capitalizeFirstLetter(labelElm.textContent);

                                newChildList.push(childNew);
                            }
                        }

                        ulElmNew.innerHTML = "";
                        newChildList.forEach(item => {
                            ulElmNew.appendChild(item);
                        })
                    }
                })
            }
        }

        ulElm.innerHTML = "";

        checkedListElement[selectedDropdown].forEach(item => {
            ulElm.appendChild(item);
        })

        result.slice(0, 8).forEach(item => {
            let isItemChecked = false;
            checkedListElement[selectedDropdown].forEach(itemChecked => {
                if (itemChecked.textContent.replace(/\n/g, '').replace(/\s+/g, ' ').trim().toLowerCase() === item.nama_pangan.replace(/\n/g, '').replace(/\s+/g, ' ').trim().toLowerCase()) {
                    isItemChecked = true;
                    // console.log(itemChecked.textContent.replace(/\n/g, '').replace(/\s+/g, ' ').trim().toLowerCase(), item.nama_pangan.replace(/\n/g, '').replace(/\s+/g, ' ').trim().toLowerCase())
                }
            })
            if (isItemChecked) {
                return
            }
            const liElm = document.createElement('li');
            liElm.className = "w-full rounded-t-lg border-transparent";
            liElm.innerHTML = `
                <div class="flex items-center pl-3 rounded-lg hover:bg-slate-200">
                    <input name="bahan" id="${item.id}-checkbox" type="checkbox" value="${item.nama_pangan}" class="w-4 h-4 text-[#C1002D] rounded focus:ring-transparent ring-offset-transparent focus:ring-offset-transparent focus:ring-1 bg-gray-100 border-gray-500"/>
                    <label for="${item.id}-checkbox" class="w-full py-3 ml-2 text-sm font-medium text-gray-700">${capitalizeFirstLetter(item.nama_pangan)}</label>
                </div>
            `

            ulElm.appendChild(liElm);
        })

        if (searchValue === "") {
            // filter default list if already checked based on variable checkedListElement
            ulElm.innerHTML = " ";
            checkedListElement[selectedDropdown].forEach(item => {
                ulElm.appendChild(item);
            })
            defaultListElementTambahan[selectedDropdown].forEach(item => {
                let isItemChecked = false;
                checkedListElement[selectedDropdown].forEach(itemChecked => {
                    if (itemChecked.textContent.replace(/\n/g, '').replace(/\s+/g, ' ').trim().toLowerCase() === item.textContent.replace(/\n/g, '').replace(/\s+/g, ' ').trim().toLowerCase()) {
                        isItemChecked = true;
                    }
                })
                if (isItemChecked) {
                    return
                }
                ulElm.appendChild(item);
            })
            
        }
    });
}

function checkboxListener(){
    var checkboxes = document.querySelectorAll("input[type=checkbox]");
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                // append to list with jquery
                
            } 
        });
    })
    
};

function submit() { 
    loadingbuttonFunction("submit", "submitbtn", true);
    const form = document.getElementById("myFormUtama");
    form.href= 'result';
    const checkboxesbu = form.querySelectorAll("input[type=checkbox][name=bahan]:checked");
    const totalbahan = [];
    for (let i = 0; i < checkboxesbu.length; i++) {
        totalbahan.push(checkboxesbu[i].value);
        checkboxesbu[i].checked = false;
    }
    const formbumbu = document.getElementById("myFormBumbu");
    const checkboxesbumbu = formbumbu.querySelectorAll("input[type=checkbox][name=bahan]:checked");
    for (let i = 0; i < checkboxesbumbu.length; i++) {
        totalbahan.push(checkboxesbumbu[i].value);
        checkboxesbumbu[i].checked = false;
    }
    const formsayur = document.getElementById("myFormSayur");
    const checkboxesbusayur = formsayur.querySelectorAll("input[type=checkbox][name=bahan]:checked");
    for (let i = 0; i < checkboxesbusayur.length; i++) {
        totalbahan.push(checkboxesbusayur[i].value);
        checkboxesbusayur[i].checked = false;
    }
    const formtambahan = document.getElementById("myFormTambahan");
    const checkboxesbtambahan = formtambahan.querySelectorAll("input[type=checkbox][name=bahan]:checked");
    for (let i = 0; i < checkboxesbtambahan.length; i++) {
        totalbahan.push(checkboxesbtambahan[i].value);
        checkboxesbtambahan[i].checked = false;
    } 
    
    const total_input = totalbahan.join(" ");
    fetch(`${API_URI}/submit`, {
        method: "POST",
        credentials: "include",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            bahan: total_input,
        }),
        
    }).then(response => response.json())
    .then(data => {
        const containerresult = document.getElementById('result');
        containerresult.className = "w-full bg-white border border-gray-200 rounded-lg p-10 mt-8 shadow"; 
        const container = document.getElementById('res-container'); 
        const containerjudulres = document.getElementById('resjudul-container'); 
        containerjudulres.innerHTML = "";
        container.innerHTML = " ";
        // console.log(data); 
        let counter = 0;
        const elementjudul = document.createElement('h1');
        elementjudul.className = "text-4xl text-gray-700 font-extrabold text-center p-4"; 
        elementjudul.textContent = "Hasil Rekomendasi";
        const garisjudul = document.createElement('hr');
        garisjudul.className = "p-4"; 
        containerjudulres.appendChild(elementjudul);
        containerjudulres.appendChild(garisjudul);
        
        data.forEach(item => { 
            counter++;
            const cards = document.createElement('div');
            cards.className = "w-80 h-max p-6 my-2 bg-gray-100 border border-gray-200 rounded-lg mt-8 shadow"; 
            const card = document.createElement('div');
            card.className = "space-y-7"; 
            const elementnomer = document.createElement('h5');
            elementnomer.className = "text-gray-500 font-bold text-xs"; 
            elementnomer.textContent = 'Resep ' + counter;
            const elementjudul = document.createElement('h5');
            elementjudul.className = "mb-2 text-2xl font-bold tracking-tight text-gray-700"; 
            elementjudul.textContent = item.judul_resep;
            const containerlistbahan = document.createElement('div');
            containerlistbahan.className = "no-scrollbar list-decimal space-y-2 pb-4 overflow-y-scroll w-full h-[16rem] mb-3 font-normal text-gray-600 "; 
            item.bahan.split("--").forEach(bahan => {
                if (bahan == "") {
                    return;
                }
                var containerisilist = document.createElement('div');
                containerisilist.className = "flex space-x-1 pr-8"; 
                var lingkaran = document.createElement('span');
                lingkaran.className = "material-symbols-outlined "; 
                lingkaran.textContent = "fiber_manual_record";
                var isilist = document.createElement('div');
                isilist.textContent = bahan;

                // append the child to the parent
                containerisilist.appendChild(lingkaran);
                containerisilist.appendChild(isilist);
                // append the child to the parent
                containerlistbahan.appendChild(containerisilist);  
            });
            containerlistbahan.style.listStyleType = "circle";
            const garisatas = document.createElement('hr');
            const garis = document.createElement('hr');
            const containerpanah = document.createElement('div');
            containerpanah.className = "flex justify-end "; 
            const elementpanah = document.createElement('a');
            elementpanah.className = "cursor-pointer inline-flex items-center px-3 py-2 text-sm font-medium text-center text-white rounded-lg focus:ring-4 focus:outline-none bg-[#C1002D] hover:bg-red-800 focus:ring-red-900"; 
            const moreinfo = document.createElement('div');
            moreinfo.className = "flex justify-center items-center px-2 hover:underline decoration-1 "; 
            moreinfo.textContent = "Detail";
            const panah = document.createElement('span');
            panah.className = "material-symbols-outlined";
            panah.textContent = "arrow_forward_ios";

            elementpanah.id = item.id;
            let judul = item.jud
            elementpanah.onclick = function(e) {
                e.preventDefault();
                const isAlreadyClicked = itemsClicked[elementpanah.id];
                if (!isAlreadyClicked) {
                    fetch(`${API_URI}/success`, {
                        method: "POST",
                        credentials: "include",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            id: elementpanah.id,
                        }),
                        
                    })
                }
                
                // disable a button
                // const submitbtn = document.getElementById(elementpanah.id);
                // submitbtn.onclick = function(e) {
                //     e.preventDefault();
                // }
                // submitbtn.classList.remove("bg-[#C1002D]");
                // submitbtn.classList.add("bg-gray-600");
                // // text pudar
                // submitbtn.classList.remove("text-white");
                // submitbtn.classList.add("text-gray-400");
                // submitbtn.classList.remove("hover:bg-red-800");
                // submitbtn.classList.remove("focus:ring-red-900");
                // submitbtn.classList.remove("focus:ring-4");
                // submitbtn.classList.remove("focus:outline-none");
                // submitbtn.classList.remove("cursor-pointer");
                // submitbtn.classList.add("cursor-not-allowed");
                // submitbtn.childNodes[0].classList.remove("hover:underline");

                itemsClicked[elementpanah.id] = true;
                window.open(`./detail.html?id=${elementpanah.id}`, "_blank");
                
            }

            // masukan elementnomer ke dalam card
            card.appendChild(elementnomer);
            // masukan elementjudul ke dalam card
            card.appendChild(elementjudul);
            card.appendChild(garisatas);
            // masukan containerlistbahan ke dalam card
            card.appendChild(containerlistbahan);
            // masukan garis ke dalam card
            card.appendChild(garis);
            // masukan moreinfo ke dalam elementpanah
            elementpanah.appendChild(moreinfo);
            elementpanah.appendChild(panah);
            // masukan elementpanah ke dalam containerpanah
            containerpanah.appendChild(elementpanah);
            // masukan containerpanah ke dalam card
            card.appendChild(containerpanah);
            // masukan card ke dalam cards
            cards.appendChild(card);
            // masukan card ke dalam container
            container.appendChild(cards);
            // masukan container ke dalam containerresult
            containerresult.appendChild(container);
        });
        loadingbuttonFunction("submit", "submitbtn", false);
    });
    
}

const list = document.getElementsByTagName("ol");

const svgSstring = `
<svg aria-hidden="true" class="w-4 h-4 ml-1" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>
`
const dropdownFunction = () => {
    const dropdownList = document.getElementById("dropdown");
    const dropdownUl = document.getElementById("dropdown-ul");
    const dropdownMainButton = document.getElementById("dropdown-button");

    dropdownMainButton.innerHTML = `${BahanBumbu}${svgSstring}`
    const bahan = Array( BahanSayur, BahanTambahan)
    bahan.forEach(item => {
        const LiElm = document.createElement('li');
        const Button = document.createElement('button');
        Button.className = "inline-flex w-full px-4 py-2 hover:bg-red-800 hover:text-white";
        Button.textContent = item;
        LiElm.appendChild(Button);
        dropdownUl.appendChild(LiElm);
    }) 
    dropdownList.querySelectorAll("button").forEach(item => {
        // add event listener
        item.addEventListener("click", function(e) {
            const dropdownMainButton = document.getElementById("dropdown-button");
            const currentText = dropdownMainButton.textContent;
            dropdownMainButton.innerHTML = `${item.textContent}${svgSstring}`;
            item.textContent = currentText;
        });
    });
}

const initSession = () => {
    fetch(`${API_URI}/session`, {
        method: "GET",
        credentials: "include",
    })
}