// D&D Class Descriptions
// Fill in the 'displayText' field for each class with your custom description

const classDescriptions = {
    artificer: {
        name: "Artificer",
        displayText: "A master of magical invention. Artificers use tools and ingenuity to imbue mundane objects with arcane power, crafting magical devices, constructs, and enhancements through a blend of technology and magic.",
    },
    barbarian: {
        name: "Barbarian",
        displayText: "A fierce warrior of primitive background who can enter a battle rage. Barbarians draw on raw physical power, resilience, and primal instincts, shrugging off blows and striking with devastating force. Their rage fuels strength and toughness beyond normal limits.",
    },
    bard: {
        name: "Bard",
        displayText: "An inspiring magician whose power echoes the music of creation. Bards weave magic through words, music, and performance, bolstering allies and confounding foes. They are masters of knowledge, storytelling, and subtle magic.",
    },
    cleric: {
        name: "Cleric",
        displayText: "A priestly champion who wields divine magic in service of a higher power. Clerics channel the will of gods through prayer and faith, healing the wounded, smiting enemies, and shaping reality through divine miracles.",
    },
    druid: {
        name: "Druid",
        displayText: "A priest of the Old Faith, wielding the powers of nature and adopting animal forms. Druids draw strength from the natural world, commanding the elements, communing with beasts, and transforming into animals to protect the balance of nature.",
    },
    fighter: {
        name: "Fighter",
        displayText: "A master of martial combat, skilled with a wide variety of weapons and armor. Fighters rely on physical training, tactical skill, and sheer determination to overcome enemies in battle, adapting to many combat styles.",
    },
    monk: {
        name: "Monk",
        displayText: "A master of martial arts, harnessing inner power known as ki. Monks use disciplined training and spiritual focus to perform extraordinary feats, striking with speed and precision and moving with supernatural agility.",
    },
    paladin: {
        name: "Paladin",
        displayText: "A holy warrior bound by a sacred oath. Paladins combine martial prowess with divine magic, defending the innocent and smiting evil in the name of justice, honor, or devotion to a cause greater than themselves.",
    },
    ranger: {
        name: "Ranger",
        displayText: "A warrior who uses martial prowess and nature magic to combat threats on the edges of civilization. Rangers specialize in tracking, survival, and battling specific enemies, often fighting alongside animal companions or wielding nature-based spells.",
    },
    rogue: {
        name: "Rogue",
        displayText: "A scoundrel who uses stealth and trickery to overcome obstacles and enemies. Rogues rely on agility, cunning, and precise strikes, excelling at infiltration, deception, and exploiting weaknesses.",
    },
    sorcerer: {
        name: "Sorcerer",
        displayText: "A spellcaster who draws on inherent magic from a gift or bloodline. Sorcerers wield powerful magic through instinct and force of will, shaping spells in unique ways rather than relying on formal study.",
    },
    warlock: {
        name: "Warlock",
        displayText: "A wielder of magic derived from a pact with an otherworldly being. Warlocks gain supernatural abilities through bargains with powerful patrons, blending arcane magic with eldritch power.",
    },
    wizard: {
        name: "Wizard",
        displayText: "A scholarly magic-user capable of manipulating the structures of reality. Wizards learn spells through intense study, mastering a vast range of arcane magic and recording their knowledge in spellbooks.",
    }
};

// Helper function to get a class description by name
function getClassDescription(className) {
    const key = className.toLowerCase();
    return classDescriptions[key]?.displayText || "Description not found";
}

// Helper function to get all class names
function getAllClassNames() {
    return Object.values(classDescriptions).map(c => c.name);
}
