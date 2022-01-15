function deleteNote(noteId) {
    fetch("/delete-note", {
        method: "POST",
        body: JSON.stringify({ noteId: noteId }),
    }).then((_res) => {
        window.location.href = "/";
    });
}


function guestChange(guestId, tableFrom, tableTo) {
    fetch("/guest-change", {
        method: "POST",
        body: JSON.stringify({ guestId: guestId, tableFrom: tableFrom, tableTo: tableTo }),
    }).then((_res) => {
        window.location.href = "/guest-list";
    });
}

function guestDelete(guestId, tableFrom) {
    fetch("/guest-delete", {
        method: "POST",
        body: JSON.stringify({ guestId: guestId, tableFrom: tableFrom }),
    }).then((_res) => {
        window.location.href = "/guest-list";
    });
}

function showMenu() {
    const mobileBtn = document.getElementById('mobile-cta')
    nav = document.querySelector('nav');
    movileBtnExit = document.getElementById('mobile-exit');

    mobileBtn.addEventListener('click', () => {
        nav.classList.add('menu-btn');
    })

    movileBtnExit.addEventListener('click', () => {
        nav.classList.remove('menu-btn');
    })
}

function closeMessage(flash) {
    $(flash).parent().remove()
}