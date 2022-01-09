function deleteNote(noteId) {
  fetch("/delete-note", {
    method: "POST",
    body: JSON.stringify({ noteId: noteId }),
  }).then((_res) => {
    window.location.href = "/";
  });
}

function showMenu() {
  console.log('test')
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