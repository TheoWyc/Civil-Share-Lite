document.addEventListener('DOMContentLoaded', () => {
    const button = document.getElementById('boutonAjouterNote');
    const buttonSave = document.getElementById('boutonSauvegarde');
    const buttonReload = document.getElementById('boutonRecharge');
    const buttonAddSave = document.getElementById('boutonAjouterSave');
    const buttonSupSave = document.getElementById('boutonSupprimerSave');

    button.addEventListener('click', (e) => {
        e.preventDefault();
        const couleur = document.getElementById('colorPicker').value;
        makeSquare(null, null, null, null, couleur, null);
    });

    buttonSave.addEventListener("click", () =>{
        save();
    });

    buttonReload.addEventListener("click", () =>{
        reload();
    });

    buttonAddSave.addEventListener("click", () =>{
        addSave();
    });

    buttonSupSave.addEventListener("click", () =>{
        deleteSave();
    });

    initSaves();

    reload();
});

function makeSquare(height, width, posX, posY, color, content) {
    const square = document.createElement('div');
    square.className = 'note-square';
    square.style.backgroundColor = color;

    // Crée une zone de texte éditable à l'intérieur du carré
    const textArea = document.createElement('div');

    textArea.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            document.execCommand('insertLineBreak');
            e.preventDefault();
        }
    }); 

    textArea.contentEditable = true;
    textArea.className = 'note-text-area'
    if (content === null)
        textArea.textContent = 'Cliquez pour écrire...';
    else
        textArea.textContent = content;

    // Efface le texte placeholder quand on clique
    textArea.addEventListener('focus', () => {
        if (textArea.textContent === 'Cliquez pour écrire...') {
            textArea.textContent = '';
        }
    });

    // Remet le placeholder si vide
    textArea.addEventListener('blur', () => {
        if (textArea.textContent.trim() === '') {
            textArea.textContent = 'Cliquez pour écrire...';
        }
    });

    if (height != null && width != null){
        square.style.height = height;
        square.style.width = width;
    }


    if (posX != null && posY != null){
        square.style.position = 'absolute';
        square.style.left = posX;
        square.style.top = posY;
    }

        
    square.appendChild(textArea);
    makeSquareDraggable(square);
    makeResizable(square);
    makeRightClickMenu(square);

    document.querySelector('.notes-conteneur').appendChild(square);
}

// Fonction pour rendre un carré déplaçable
function makeSquareDraggable(square) {
    let isDragging = false;
    let offsetX = 0;
    let offsetY = 0;
    
    square.addEventListener('mousedown', function(e) {
        // Empêche le drag/resize si on clique sur le texte éditable
        const rect = this.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Coin bas-droite 20x20 = REDIMENSIONNEMENT
        const resizeCorner = 20;
        if (x > rect.width - resizeCorner && y > rect.height - resizeCorner) {
            //startResize(e, this);
            return;
        }
        
        
        // Bordures SANS le coin = DÉPLACEMENT
        const gripZone = 20;
        const isTopBottom = (y < gripZone || y > rect.height - gripZone) && 
                        !(x > rect.width - resizeCorner && y > rect.height - resizeCorner);
        const isLeftRight = (x < gripZone || x > rect.width - gripZone) && 
                        !(x > rect.width - resizeCorner && y > rect.height - resizeCorner);
        
        if (isTopBottom || isLeftRight) {
            // Commence le drag
            isDragging = true;
            
            offsetX = e.clientX - rect.left;
            offsetY = e.clientY - rect.top;
            
            this.classList.add('dragging');
            this.style.position = 'absolute';
            this.style.left = rect.left + 'px';
            this.style.top = rect.top + 'px';
            this.style.margin = '0';
            
            e.preventDefault();
            return;
        }

        // Centre = ÉDITION (ne rien faire, laisser contentEditable)
        return;
    
    });
    
    // Événements de mouvement et fin (sur le document)
    document.addEventListener('mousemove', function(e) {
        if (isDragging) {
            const newX = e.clientX - offsetX;
            const newY = e.clientY - offsetY;
            
            // Limites de l'écran
            const maxX = window.innerWidth - square.offsetWidth;
            const maxY = window.innerHeight - square.offsetHeight;
            
            const finalX = Math.max(0, Math.min(newX, maxX));
            const finalY = Math.max(0, Math.min(newY, maxY));
            
            square.style.left = finalX + 'px';
            square.style.top = finalY + 'px';
        }
    });
    
    document.addEventListener('mouseup', function() {
        if (isDragging) {
            square.classList.remove('dragging');
            isDragging = false;
        }
    });
}

function makeResizable(square) {
        square.addEventListener('mousedown', function(e) {
        const rect = this.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        // Coin bas-droite 20x20 = REDIMENSIONNEMENT
        const resizeCorner = 20;
        if (x > rect.width - resizeCorner && y > rect.height - resizeCorner) {
            startResize(e, this);
            return;
        }
        
        // Bordures SANS le coin = DÉPLACEMENT
        const gripZone = 20;
        const isTopBottom = (y < gripZone || y > rect.height - gripZone) && 
                        !(x > rect.width - resizeCorner && y > rect.height - resizeCorner);
        const isLeftRight = (x < gripZone || x > rect.width - gripZone) && 
                        !(x > rect.width - resizeCorner && y > rect.height - resizeCorner);
        
        if (isTopBottom || isLeftRight) {
            return;
        }
        
        // Centre = ÉDITION
    });
}

function startResize(e, square) {
    let isResizing = true;
    square.classList.add('resizing');

    const startX = e.clientX;
    const startY = e.clientY;
    const startWidth = square.offsetWidth;
    const startHeight = square.offsetHeight;
    
    document.addEventListener('mousemove', function resize(e) {
        if (!isResizing) return;

        const deltaX = e.clientX - startX;
        const deltaY = e.clientY - startY;
        
        // Nouvelles dimensions (minimum 100x100)
        const newWidth = Math.max(100, startWidth + deltaX);
        const newHeight = Math.max(100, startHeight + deltaY);
        
        square.style.width = newWidth + 'px';
        square.style.height = newHeight + 'px';
    });
    
    document.addEventListener('mouseup', function stopResize() {
        isResizing = false;
        square.classList.remove('resizing');
        // Nettoyer les event listeners
    });
}

function makeRightClickMenu(square) {
    let activeNote = null;

    square.addEventListener('contextmenu', function(e) {
        e.preventDefault(); // Empêche le menu contextuel par défaut
        showContextMenu(e, this);
    });

    function showContextMenu(e, square) {
        const contextMenu = document.getElementById('contextMenu');
        activeNote = square;
        
        // Position du menu exactement où le clic droit a eu lieu
        contextMenu.style.left = e.clientX + 'px';
        contextMenu.style.top = e.clientY + 'px';
        contextMenu.style.display = 'block';
    }

    const contextMenu = document.getElementById('contextMenu');

    contextMenu.addEventListener('click', async (e) => {
        e.preventDefault();
        e.stopPropagation(); // <<< ajouté
        const action = e.target.dataset.action;
        if (action && activeNote) {
            await handleContextMenuAction(action, activeNote);
        } else {
            hideContextMenu();
        }
    });

    document.addEventListener('click', (e) => {
        const contextMenu = document.getElementById('contextMenu');
        if (!contextMenu.contains(e.target)) {
            contextMenu.style.display = 'none';
            activeNote = null;
        }
    });


    function hideContextMenu(square) {
        contextMenu.style.display = 'none';
        activeNote = null; // Réinitialiser la note active
    }

    async function handleContextMenuAction(action, square) {
        switch(action) {
            case 'duplicate':
                duplicateNote(square);
                break;
            case 'changeColor':
                changeNoteColor(square);
                break;
            case 'delete':
                deleteNote(square);
                break;
            case 'addFile':
                await addFile(square); // <<< await ici
                break;
        }
    }


    function duplicateNote(square) {
        const newSquare = square.cloneNode(true);
        newSquare.className = 'note-square';
        // Décaler légèrement la position
        const rect = square.getBoundingClientRect();
        newSquare.style.left = (rect.left + 20) + 'px';
        newSquare.style.top = (rect.top + 20) + 'px';
        
        makeSquareDraggable(newSquare);
        makeResizable(newSquare);
        makeRightClickMenu(newSquare)
        document.querySelector('.notes-conteneur').appendChild(newSquare);
    }

    function changeNoteColor(square) {
        const colorPicker = document.getElementById('colorPicker');
        square.style.backgroundColor = colorPicker.value;
    }

    function deleteNote(square) {
        if (confirm('Supprimer cette note ?')) {
            square.remove();
        }
    }

    async function addFile(square) {
        /*
        const input = document.createElement('input');
        input.type = 'file';
        input.style.display = 'none';
        document.body.appendChild(input);

        input.click();
        input.onchange = async (event) => {
            const file = event.target.files[0];
            if (!file) {
                return;
            }

            const fileUrl = await uploadFile(file)

            if (file.type)
        };

        document.body.removeChild(input);*/
    }



    async function uploadFile(file) {
        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch("http://192.168.137.1:8000/upload", {
            method: "POST",
            body: formData
        });

        const data = await res.json();
        return data.file_url; // URL renvoyée par le serveur
    }
}

async function save() {
    const menuSaves = document.getElementById('menuSaves');
    const save_name_selected = menuSaves.options[menuSaves.selectedIndex].value;

    await resetBado(save_name_selected);
    
    await listAndAddNotes();


    await clearSquares();
    await reload();
}

async function listAndAddNotes()
{
    const lst = Array.from(document.querySelectorAll('.note-square'));
    
    for (i in lst){
        square = lst[i];

        const height = window.getComputedStyle(square).height;
        const width = window.getComputedStyle(square).width;
        const posX = window.getComputedStyle(square).left;
        const posY = window.getComputedStyle(square).top;
        const color = rgbToHex(square.style.backgroundColor);
        const content = square.querySelector('.note-text-area').textContent;
        const save_name = menuSaves.options[menuSaves.selectedIndex].value;

        await addDataBaseNote(createNoteData(height, width, posX, posY, color, content, save_name));
    }
}

async function clearSquares(){
    document.querySelector('.notes-conteneur').innerHTML = '';
}

function rgbToHex(rgb) {
    if (rgb.startsWith('#')) return rgb;
    
    const result = rgb.match(/\d+/g);
    if (result) {
        const [r, g, b] = result.map(Number);
        return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)}`;
    }
    return rgb;
}

function createNoteData(height, width, posX, posY, color, content, save_name){
    return {
        content: content,
        posX: posX,
        posY: posY,
        width: width,
        height: height,
        color: color,
        save_name: save_name
    };
}

async function addDataBaseNote(noteData){
    try {
        const response = await fetch('http://192.168.137.1:8000/api/notes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(noteData)
        });

        await response.json();

    } catch (error) {
        console.error('Erreur:', error);
        return null;
    }
}

async function reload(){
    await clearSquares();

    const menuSavesTest = document.getElementById('menuSaves');

    const lstNotes = await getDataBaseNote();
    console.log(lstNotes['notes']);

    if (menuSavesTest.selectedIndex === -1){
        console.log("ok");
        return;
    }
    const save_name = menuSavesTest.options[menuSavesTest.selectedIndex].value;

    for (i in lstNotes['notes']) {
        /*console.log(lstNotes[1][1]);*/
        square = lstNotes['notes'][i];
        if (square != undefined)
            if (square.save_name === save_name)
                makeSquare(square.height, square.width, square.posX, square.posY, square.color, square.content);
    }
}

async function getDataBaseNote(){
    try {
        const response = await fetch('http://192.168.137.1:8000/api/notes', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        
        const res = await response.json();
        return res;
    } catch (error) {
        console.error('Erreur:', error);
        return null;
    }
}

async function resetBado(save_name) {
    try {
        const response = await fetch('http://192.168.137.1:8000/api/notes/reset/' + save_name, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
            },
        });
        
        await response.json();
    } catch (error) {
        console.error('Erreur:', error);
        return null;
    }
}

function addSave(){
    const menu = document.getElementById('menuSaves');
    const inputSave = document.getElementById('nomNewSave');
    const nomSave = inputSave.value;


    const newSave = document.createElement('option');
    newSave.textContent = nomSave;

    menu.appendChild(newSave);
    inputSave.value = "";
}

async function initSaves() {
    lstNotes = await getDataBaseNote();
    const menuSaves = document.getElementById('menuSaves');

    for (i in lstNotes['notes']) {
        square = lstNotes['notes'][i];

        let estDejaDansLaListe = false;
        for (j in menuSaves.options)
            if (menuSaves.options[j].value === square.save_name)
                estDejaDansLaListe = true;

        if (estDejaDansLaListe == false){
            const newOption = document.createElement('option');
            newOption.value = square.save_name;
            newOption.textContent = square.save_name;
            menuSaves.appendChild(newOption);
        }
    }
}

async function deleteSave(){
    const menuSaves = document.getElementById('menuSaves');
    const saveSupp = menuSaves.options[menuSaves.selectedIndex];

    await resetBado(saveSupp.value);

    menuSaves.remove(saveSupp);
}