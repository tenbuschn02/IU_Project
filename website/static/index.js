function deleteNote(noteId) {
    fetch("/delete-note", {
        method: "POST",
        body: JSON.stringify({ noteId: noteId }),
    }).then((_res) => {
        window.location.href = "/";
    });
}

function deleteFood(foodId) {
    fetch("/delete-food", {
        method: "POST",
        body: JSON.stringify({ foodId: foodId }),
    }).then((_res) => {
        window.location.href = "/foodcalc";
    });
}

function deleteCost(costId) {
    fetch("/delete-cost", {
        method: "POST",
        body: JSON.stringify({ costId: costId }),
    }).then((_res) => {
        window.location.href = "/finances";
    });
}

function deleteTable(tableId) {
    fetch("/delete-table", {
        method: "POST",
        body: JSON.stringify({ tableId: tableId }),
    }).then((_res) => {
        window.location.href = "/table-overview";
    });
}


function guestChange(guestId, new_status) {
    fetch("/guest-change", {
        method: "POST",
        body: JSON.stringify({ guestId: guestId, new_status: new_status }),
    }).then((_res) => {
        window.location.href = "/guest-list";
    });
}

function guestDelete(guestId, tableFrom) {
    fetch("/guest-delete", {
        method: "POST",
        body: JSON.stringify({ guestId: guestId }),
    }).then((_res) => {
        window.location.href = "/guest-list";
    });
}

function deleteAllGuests() {
    fetch("/delete-all", {
        method: "POST",
        body: JSON.stringify(),
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

function CurrencyFormatted(amount) {
	var i = parseFloat(amount);
	if(isNaN(i)) { i = 0.00; }
	var minus = '';
	if(i < 0) { minus = '-'; }
	i = Math.abs(i);
	i = parseInt((i + .005) * 100);
	i = i / 100;
	s = new String(i);
	if(s.indexOf('.') < 0) { s += '.00'; }
	if(s.indexOf('.') == (s.length - 2)) { s += '0'; }
	s = minus + s;
	return s;
}

function closeMessage(flash) {
    $(flash).parent().remove()
}

function getTemplate() {

    $form.submit();

}

