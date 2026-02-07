



function updateCharacterSheet(data) {
    document.getElementById("character-name").textContent = data.name;
    document.getElementById("class-name").textContent = data.class;
    document.getElementById("race-name").textContent = data.race;
    document.getElementById("backstory").textContent = data.backstory;
    document.getElementById("class-description").textContent = "a dude";
    document.getElementById("result").textContent = data.character_sheet;
}




