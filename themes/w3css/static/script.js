
/*
 * Action input proxy
 */

function sendActionForm(target)
{
    let entries = []
    let vmarked = document.getElementById('action_mark').checked ? '1' : '0';
    let vread = document.getElementById('action_read').checked ? '1' : '0';

    var inputs = document.querySelectorAll("input[name='ids']:checked");
    for (let i = 0; i < inputs.length; i++) {
        entries.push(inputs[i].value);
    }

    let params = {
        action: "entry",
        read: vread,
        mark: vmarked,
        ids: entries.join(",")
    };
    post(params, target);
}

function post(params, path='', method='post')
{
    const form = document.createElement('form');
    form.method = method;
    form.action = path;

    for (const key in params) {
        if (params.hasOwnProperty(key)) {
            const hiddenField = document.createElement('input');
            hiddenField.type = 'hidden';
            hiddenField.name = key;
            hiddenField.value = params[key];
            form.appendChild(hiddenField);
        }
    }

    document.body.appendChild(form);
    form.submit();
}


/*
 * Read progress on feed
 */

function showProgressOnFeed()
{
    let tags = document.getElementsByClassName("pause-tag");
    for (let i = 0; i < tags.length; i++) {
        let id = tags[i].dataset.id;
        if (id) {
            let s = localStorage.getItem(id+"_progress");
            if (s !== null && s > 0) {
                tags[i].classList.remove('w3-hide');
            }
        }
    }
}


/*
 * Progress
 */

function restoreScrollProgress() {
    let el = document.getElementById('entry');
    if (el) {
        var identifier = el.getAttribute('data-id');
        var progress = localStorage.getItem(identifier + "_progress");
        if (progress) {
            window.scrollTo(0, progress);
            updateScrollProgressHeader(progress);
        }
    }
}

function saveScrollProgress() {
    let el = document.getElementById('entry');
    if (el) {
        var identifier = el.getAttribute('data-id');
        let progress = window.scrollY;
        localStorage.setItem(identifier + "_progress", progress);
        updateScrollProgressHeader(progress);
    }
}

function updateScrollProgressHeader(progress)
{
    let el = document.getElementsByClassName("header-progress");
    for (let i = 0; i < el.length; i++) {
        let limit = Math.max(
            document.body.scrollHeight,
            document.body.offsetHeight,
            document.documentElement.clientHeight,
            document.documentElement.scrollHeight,
            document.documentElement.offsetHeight
        ) - window.innerHeight;

        let p = parseInt((progress / limit) * 100)
        el[i].style.width = p+"%";
    }
}

function clearLocalStorage() {
    if (confirm("Are you sure?") == true) {
      localStorage.clear();
    }
}

/*
 * Color Scheme
 */

function initColorScheme() {
    let cs = localStorage.getItem("color-scheme");
    if (cs === null) {
        let prefersDarkScheme = window.matchMedia("(prefers-color-scheme: dark)");
        if (prefersDarkScheme.matches)
            cs = document.body.classList.contains("light-mode") ? "light" : "dark";
        else
            cs = document.body.classList.contains("dark-mode") ? "dark" : "light";
    }
    setColorScheme(cs)
}

function toggleColorScheme() {
    let currentTheme = localStorage.getItem("color-scheme");
    let newTheme = (currentTheme == "dark") ? 'light' : 'dark';
    setColorScheme(newTheme);
}

function setColorScheme(scheme) {
    if (scheme == "dark") {
        document.body.classList.add("dark-mode");
        localStorage.setItem("color-scheme", 'dark');
    } else {
        document.body.classList.remove("dark-mode");
        localStorage.setItem("color-scheme", 'light');
    }
}

/*
 * Font
 */

function initFont() {
    let f = localStorage.getItem("font");
    if (f === null) {
        f = 'sans-serif';
    }
    setFont(f)
}

function toggleFont() {
    let currentFont = localStorage.getItem("font");
    let newFont = (currentFont == "sans-serif") ? 'serif' : 'sans-serif';
    setFont(newFont);
}

function setFont(scheme) {
    if (scheme == "serif") {
        document.body.classList.add("w3-serif");
        localStorage.setItem("font", 'serif');
    } else {
        document.body.classList.remove("w3-serif");
        localStorage.setItem("font", 'sans-serif');
    }
}

/*
 * Initialize
 */

document.addEventListener("DOMContentLoaded", function(event) {
    initColorScheme();
    initFont();

    // try init entry page
    let el = document.getElementById('entry');
    if (el) {
        restoreScrollProgress();
        window.onscroll = function() {
            saveScrollProgress()
        };
    }

    // progress on feed
    showProgressOnFeed();

    // speed page changer
    let el2 = document.getElementsByClassName("pagination-dropdown");
    for (let i = 0; i < el2.length; i++) {
        el2[i].addEventListener("change", function(e) {
          window.location = "/page/"+e.currentTarget.value;
        });
        break;
    }
});
