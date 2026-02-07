function updateCharacterSheet(data) {
    document.getElementById("character-name").textContent = data.name;
    document.getElementById("result").textContent = data.character_sheet;

}