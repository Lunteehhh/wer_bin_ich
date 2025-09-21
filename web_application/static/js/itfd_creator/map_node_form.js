import {
    fetchPossibleMonsters, fetchPossibleItems, fetchPossibleMapsNodes,
    fetchPossibleCommands, fetchPossiblePermissions
} from "./fetch_data.js";

// appData
const appData = window.appData;
const dataInsert = appData.insertData;
const packName = appData.packName;
const mapName = appData.mapName;
const nodeName = appData.name
const nodeId = appData.nodeId

// data
const possibleNodes = await fetchPossibleMapsNodes(packName, mapName);
const possiblePerms = await fetchPossiblePermissions(packName);
const possibleItems = await fetchPossibleItems(packName);
const possibleMonsters = await fetchPossibleMonsters(packName);
const possibleCommands = await fetchPossibleCommands(packName);


console.log("mapName:", mapName);
console.log("Monsters:", possibleMonsters);
console.log("Nodes:", possibleNodes);
console.log("Perms:", possiblePerms);
console.log("Commands:", possibleCommands);
console.log("items:", possibleItems);

// Global Vars
let globalCategory;
let errorCount = 0;

// Connection/Entrances Name
let titlesConnections = [];
let titlesEntrances = [];

// Error Message
const pError = document.getElementById('error-message');

// Valid Functions
let invalidInputMatches = {};
function validTitlesV1() {
    function _validTitlesV1(array, num, setMatches) {
        for (let i = num + 1; i < array.length; i++) {
            console.log(`${i}: ${array[num].value} === ${array[i].value}`);
            if (array[num].value === array[i].value) {
                setMatches.add(array[num]);
                setMatches.add(array[i]);
            }
        }
        return setMatches;
    }
    function setValid(elem) {
        elem.classList.add("valid");
        elem.classList.remove("invalid");
    }
    function setInvalid(elem) {
        elem.classList.add("invalid");
        elem.classList.remove("valid");
    }
    console.log("VALID")

    let allTitles = titlesConnections;
    let invalidTitles = new Set;
    let validTitles;

    if (globalCategory === 1) {
        allTitles = allTitles.concat(titlesEntrances);
    }
    console.log("allTitles:", allTitles);
    validTitles = new Set(allTitles);

    for (let i = 0; i < allTitles.length; i++) {
        invalidTitles = _validTitlesV1(allTitles, i, invalidTitles);
    }

    console.log(invalidTitles);
    validTitles = validTitles.difference(invalidTitles);

    validTitles.forEach((elem) => {
        setValid(elem);
    })

    invalidTitles.forEach((elem) => {
        setInvalid(elem);
    })

    errorCount = invalidTitles.size;
}

// Options Functions
console.log("Load OPTIONS");
function permOptions() {
    let options = [];

    for (let key in possiblePerms) {
        const newOption = document.createElement("option");

        newOption.value = key;
        newOption.text = possiblePerms[key];

        options.push(newOption);
    }
    return options;
}
function mapOptions() {
    const mapNames = possibleNodes;
    let options = [];

    for (let key in mapNames) {
        const newOption = document.createElement("option");

        newOption.value = key;
        newOption.text = mapNames[key];

        options.push(newOption);
    }
    return options;
}
function nodesOptions(map_id) {
    const nodeDict = possibleNodes[map_id][1];
    let options = [];
    console.log(nodeDict);

    nodeDict.forEach((_nodeId, _nodeName) => {
        const newOption = document.createElement("option");

        newOption.value = _nodeId;
        newOption.text = _nodeName;

        options.push(newOption);
    })
    return options;
}
function itemsOptions() {
    let options = [];
    const noneOption = document.createElement("option");
    noneOption.value = "none";
    noneOption.text = "---";
    options.push(noneOption);

    console.log(possibleItems);
    possibleItems.forEach((_itemData, _) => {
        const newOption = document.createElement("option");

        newOption.value = _itemData[0];
        newOption.text = `${_itemData[0]}: ${_itemData[1]}`;

        options.push(newOption);
    })
    return options;
}
function monstersOptions() {
    let options = [];
    const noneOption = document.createElement("option");
    noneOption.value = "none";
    noneOption.text = "---";
    options.push(noneOption);

    possibleMonsters.forEach((_monsterData, _) => {
        const newOption = document.createElement("option");

        newOption.value = _monsterData[0];
        newOption.text = `${_monsterData[0]}: ${_monsterData[1]}`;

        options.push(newOption);
    })
    return options;
}
function commandsOptions() {
    let options = [];

    for (let commandId in possibleCommands) {
        const newOption = document.createElement("option");

        newOption.value = commandId;
        newOption.text = possibleCommands[commandId];

        options.push(newOption);
    }
    return options;
}

// Connections
console.log("Load Connections");
const connContainer = document.getElementById('conn-container');
const addConnBtn = document.getElementById('add-conn-btn');
/* Global Vars */
let connectionsIds = [];
let countConn = 1;
/* Functions */
function addConnection() {
    console.log("add connection");

    const newDivConn = document.createElement('div');
    const newDeleteBtn = document.createElement('button');

    const newLabelNode = document.createElement("label");
    const newSelectNode = document.createElement('select');

    const newLabelTitle = document.createElement("label");
    const newInputTitle = document.createElement('input');

    const newLabelPerm = document.createElement('label');
    const newSelectPerm = document.createElement('select');

    const optionsNode = nodesOptions(mapName);
    const optionsPerm = permOptions();

    const removeId  = countConn;

    // Div
    newDivConn.id = "connections-div-" + countConn;
    newDivConn.classList.add("none-value")
    connContainer.insertBefore(newDivConn, addConnBtn);
    newDivConn.appendChild(newLabelNode);
    newDivConn.appendChild(newLabelTitle);
    newDivConn.appendChild(newLabelPerm);
    newDivConn.appendChild(newDeleteBtn);

    // Node
    newLabelNode.textContent = "Node:";
    newLabelNode.appendChild(newSelectNode);
    newSelectNode.id = "connections-node-" + countConn;
    console.log(`CREATE CONN: ${newSelectNode.id}`);
    optionsNode.forEach((option) => {
        newSelectNode.add(option);
    });

    // Title
    newLabelTitle.textContent = "Title:";
    newLabelTitle.appendChild(newInputTitle);

    newInputTitle.id = "connections-title-" + countConn;
    newInputTitle.type = "text";
    newInputTitle.classList.add("none-value");

    titlesConnections.push(newInputTitle);
    newInputTitle.addEventListener("input", () => {
        console.log("Input " + newInputTitle.value);
        if (newInputTitle.value === "") {
            newInputTitle.classList.add("none-value");
        } else {
            newInputTitle.classList.remove("none-value");
        }
        validTitlesV1();
    })

    // Perm
    newLabelPerm.textContent = "Permission:";
    newLabelPerm.appendChild(newSelectPerm);
    newSelectPerm.id = "connections-perm-" + countConn;

    optionsPerm.forEach(option => {
        newSelectPerm.add(option);
    });


    // Delete Button
    newDeleteBtn.id = "delete-btn-" + countConn;
    newDeleteBtn.textContent = "delete";
    newDeleteBtn.addEventListener('click', () => {
        console.log('Delete conn ', countConn - 1);
        newDivConn.remove();
        connectionsIds.splice(connectionsIds.indexOf(removeId), 1);
    })

    connectionsIds.push(countConn++);

    return [newSelectNode, newInputTitle, newSelectPerm];
}
addConnBtn.addEventListener('click', () => {
    addConnection();
})

/* Sentenced First
 * HTML Elements */
console.log("Load Sentences Fist");
const sentencesFirstContainer = document.getElementById('sentences-first-container');
const addSentencesFirstBtn = document.getElementById('add-sentence-first-btn');
/* global vars */
let sentencesFirstNums = [];
let countSentencesFirst = 0;
/* Functions */
function addSentenceFirst() {
    const divSentenceFirst = document.createElement("div")
    const labelSentence = document.createElement("label");
    const inputSentence = document.createElement("input");
    const btnRemoveSentence = document.createElement("button");
    const removeId = countSentencesFirst;

    // Div
    sentencesFirstContainer.insertBefore(divSentenceFirst, addSentencesFirstBtn);
    divSentenceFirst.appendChild(labelSentence);
    divSentenceFirst.appendChild(btnRemoveSentence);

    // Input
    labelSentence.textContent = "Sentence:";
    labelSentence.appendChild(inputSentence);

    inputSentence.id = "sentences-first-" + countSentencesFirst;
    inputSentence.type = "text";
    inputSentence.classList.add("none-value");

    inputSentence.addEventListener("input", () => {
        if (inputSentence.value === "") {
            inputSentence.classList.add("none-value");
        } else {
            inputSentence.classList.remove("none-value");
        }
    })

    // Button
    btnRemoveSentence.textContent = "remove";
    btnRemoveSentence.addEventListener('click', () => {
        divSentenceFirst.remove();
        sentencesFirstNums.splice(sentencesFirstNums.indexOf(removeId), 1);
    })

    sentencesFirstNums.push(countSentencesFirst++);
    return inputSentence;
}
addSentencesFirstBtn.addEventListener('click', () => {
    addSentenceFirst();
})

/* Sentence Last
 * HTML Elements */
console.log("Load Sentences Last");
const sentencesLastContainer = document.getElementById('sentences-last-container');
const addSentencesLastBtn = document.getElementById('add-sentence-last-btn');
/* Global vars */
let sentencesLastNums = [];
let countSentencesLast = 0;
/* Functions */
function addSentenceLast() {
    const divSentenceLast = document.createElement("div");
    const labelSentence = document.createElement("label");
    const inputSentence = document.createElement("input");
    const btnRemoveSentence = document.createElement("button");
    const removeId = countSentencesLast;

    // Div
    sentencesLastContainer.insertBefore(divSentenceLast, addSentencesLastBtn);
    divSentenceLast.appendChild(labelSentence);
    divSentenceLast.appendChild(inputSentence);
    divSentenceLast.appendChild(btnRemoveSentence);

    // Input
    labelSentence.textContent = "Sentence:";
    labelSentence.appendChild(inputSentence);

    inputSentence.id = "sentences-last-" + countSentencesLast;
    inputSentence.type = "text";
    inputSentence.classList.add("none-value");

    inputSentence.addEventListener("input", () => {
        if (inputSentence.value === "") {
            inputSentence.classList.add("none-value");
        } else {
            inputSentence.classList.remove("none-value");
        }
    })

    // Button
    btnRemoveSentence.textContent = "remove";
    btnRemoveSentence.addEventListener('click', () => {
        divSentenceLast.remove();
        console.log("remove", removeId);
        sentencesLastNums.splice(sentencesLastNums.indexOf(removeId), 1);
    })

    sentencesLastNums.push(countSentencesLast++);
    return inputSentence;
}
addSentencesLastBtn.addEventListener('click', () => {
    addSentenceLast();
})

/* Items
 * HTML Elements */
console.log("Load Items");
const itemContainer = document.getElementById('item-container');
const addItemBtn = document.getElementById('add-item-btn');
/* Global Vars */
let itemNums = [];
let countItems = 0;
/* Functions */
function addItem() {
    const divItem = document.createElement("div");
    const labelItem = document.createElement("label");
    const selectItem = document.createElement("select");
    const buttonRemove = document.createElement("button");
    const optionsItems = itemsOptions();
    const removeId = countItems;

    // Div
    itemContainer.insertBefore(divItem, addItemBtn);
    divItem.appendChild(labelItem);
    divItem.appendChild(buttonRemove);

    // Select
    selectItem.id = "select-item-" + countItems;
    labelItem.textContent = "Item:";
    labelItem.appendChild(selectItem);
    optionsItems.forEach(option => {
        selectItem.add(option);
    })

    // button
    buttonRemove.textContent = "Remove";
    buttonRemove.addEventListener('click', () => {
        divItem.remove();
        itemNums.splice(itemNums.indexOf(removeId))
    })

    itemNums.push(countItems++);
    return selectItem;
}
addItemBtn.addEventListener('click', () => {
    addItem();
})

/* Monster
 * HTML Elements */
console.log("Load Monsters");
const monsterContainer = document.getElementById('monsters-container');
const addMonsterBtn = document.getElementById('add-monster-btn');
/* Global Vars */
let monsterNums = [];
let countMonsters = 0;

function addMonster() {
    const divMonster = document.createElement("div");
    const labelMonster = document.createElement("label");
    const selectMonster = document.createElement("select");
    const buttonRemove = document.createElement("button");
    const optionsMonsters = monstersOptions();
    const removeId = countMonsters;

    // Div
    monsterContainer.insertBefore(divMonster, addMonsterBtn);
    divMonster.appendChild(labelMonster);
    divMonster.appendChild(buttonRemove);

    // Select
    labelMonster.textContent = "Monster:";
    labelMonster.appendChild(selectMonster);
    selectMonster.id = "select-monster-" + countMonsters;
    optionsMonsters.forEach(option => {
        selectMonster.add(option);
    })

    // button
    buttonRemove.textContent = "Remove";
    buttonRemove.addEventListener('click', () => {
        divMonster.remove();
        monsterNums.splice(monsterNums.indexOf(removeId))
    })

    monsterNums.push(countMonsters++);
    return selectMonster;
}
addMonsterBtn.addEventListener('click', () => {
    addMonster();
})

/* Commands
 * HTML Elements */
console.log("Load Commands");
const commandsContainer = document.getElementById('commands-container');
const addCommandBtn = document.getElementById('add-command-btn');
/* Global Vars */
let commandsNums = [];
let countCommands = 0;

function addCommand() {
    const divCommand = document.createElement("div");
    const labelCommand = document.createElement("label");
    const selectCommand = document.createElement("select");
    const buttonRemove = document.createElement("button");
    const optionsCommands = commandsOptions();
    const removeId = countCommands;

    // Div
    commandsContainer.insertBefore(divCommand, addCommandBtn);
    divCommand.appendChild(labelCommand);
    divCommand.appendChild(buttonRemove);

    // Label
    labelCommand.textContent = "Command:";
    labelCommand.appendChild(selectCommand);

    // Select
    console.log("hi")
    selectCommand.id = "select-command-" + countCommands;
    optionsCommands.forEach(option => {
        selectCommand.add(option);
    })

    // button
    buttonRemove.textContent = "Remove";
    buttonRemove.addEventListener('click', () => {
        divCommand.remove();
        commandsNums.splice(commandsNums.indexOf(removeId))
    })

    commandsNums.push(countCommands++);
    return selectCommand;
}
addCommandBtn.addEventListener('click', () => {
    addCommand();
})

/* Entrances
 * HTML Elements */
console.log("Load Entrances");
const divEntranceContainer = document.getElementById('entrances-container');
const addEntranceBtn = document.getElementById('add-entrance-btn');
/* Global Vars */
let entranceNums = [];
let countEntrances = 1;
function addEntrance(){
    // HTML-Objects
    const divEntrance = document.createElement('div');

    const labelMap = document.createElement("label");
    const selectMap = document.createElement("select");

    const labelNode = document.createElement("label");
    const selectNode = document.createElement("select");

    const labelTitle = document.createElement("label");
    const inputTitle = document.createElement("input");

    const labelPerm = document.createElement("label");
    const selectPerm = document.createElement("select");

    const buttonRemove = document.createElement("button");

    // Options
    const optionsMap = mapOptions();
    let optionsNode = [];
    const optionsPerm = permOptions();

    // Remove
    const removeId = countEntrances;

    // div
    divEntrance.id = "add-entrance-" + countEntrances;
    divEntranceContainer.insertBefore(divEntrance, addEntranceBtn);
    divEntrance.appendChild(labelMap);
    divEntrance.appendChild(labelNode);
    divEntrance.appendChild(labelTitle);
    divEntrance.appendChild(labelPerm);
    divEntrance.appendChild(buttonRemove);

    // Map
    labelMap.textContent = "Map:"
    labelMap.appendChild(selectMap);
    selectMap.id = "entrance-map-" + countEntrances;
    optionsMap.forEach((option) => {
        selectMap.add(option);
    });

    selectMap.addEventListener("change", () => {
        selectNode.innerHTML = "";
        optionsNode = nodesOptions(selectMap.value);

        optionsNode.forEach((option) => {
            selectNode.add(option);
        })
    })

    // Node
    labelNode.textContent = "Node:"
    labelNode.appendChild(selectNode);
    selectNode.id = "entrance-node-" + countEntrances;
    optionsNode = nodesOptions(selectMap.value);
    optionsNode.forEach(option => {
        selectNode.add(option);
    })

    // Title
    labelTitle.textContent = "Title:"
    labelTitle.appendChild(inputTitle);
    inputTitle.id = "entrance-title-" + countEntrances;
    inputTitle.type = "text";
    inputTitle.classList.add("none-value");
    titlesConnections.push(inputTitle);
    inputTitle.addEventListener("input", () => {
        if (inputTitle.value === "") {
            inputTitle.classList.add("none-value");
        } else {
            inputTitle.classList.remove("none-value");
            validTitlesV1();
        }
    })

    // Perm
    labelPerm.textContent = "Perm:"
    labelPerm.appendChild(selectPerm);
    selectPerm.id = "entrance-perm-" + countEntrances;
    optionsPerm.forEach((option) => {
        selectPerm.add(option);
    })

    // Remove
    buttonRemove.textContent = "remove";
    buttonRemove.addEventListener("click", () => {
        divEntrance.remove();
        entranceNums.splice(entranceNums.indexOf(removeId), 1);
    })

    entranceNums.push(countEntrances++);
    return [selectMap, selectNode, inputTitle, selectPerm];
}
addEntranceBtn.addEventListener('click', () => {
    addEntrance();
})


// Additional Data
const selectCategory = document.getElementById("category");

selectCategory.addEventListener("change", () => {
    const category = selectCategory.value;

    if (category === "1") {
        divEntranceContainer.style.display = "block";
        console.log("selected");
    } else {
        divEntranceContainer.style.display = "none";
        console.log("Changed");
    }
})

// Commit
const form = document.getElementById("node-form");
form.addEventListener("submit", (event) => {
    event.preventDefault();

    if (errorCount) {
        console.log("[ERROR] - Connections/Entrances name is used to often");
        return;
    }

    // Name
    const inputName = document.getElementById("name");
    const name = inputName.value.trim();
    if (name.length === 0) {
        console.log("[ERROR] - name is to short");
        return;
    }

    // category
    const selectCategory = document.getElementById("category");
    const category = selectCategory.value;

    // Connections
    let connections = [];
    connectionsIds.forEach((connId) => {
        const selectNode = document.getElementById("connections-node-" + connId);
        const inputTitle = document.getElementById("connections-title-" + connId);
        const selectPerm = document.getElementById("connections-perm-" + connId);

        if (inputTitle.value !== "") {
            connections.push([
                selectNode.value,
                inputTitle.value,
                selectPerm.value
            ]);
        }
    });

    // Sentences First
    let firstSentence = [];
    sentencesFirstNums.forEach((num) => {
        const inputSentence = document.getElementById("sentences-first-" + num);

        if (inputSentence.value !== "") {
            firstSentence.push(inputSentence.value);
        } else {
            console.log("[warning] - SKIP first-sentence because its empty.");
        }

    });

    // Sentences Last
    let lastSentence = [];
    sentencesLastNums.forEach((num) => {
        const inputSentence = document.getElementById("sentences-last-" + num);

        if (inputSentence.value !== "") {
            lastSentence.push(inputSentence.value);
        } else {
            console.log("[warning] - SKIP last-sentence because its empty.");
        }
    });

    // Items
    let items = [];
    itemNums.forEach(num => {
        const selectItem = document.getElementById("select-item-" + num);

        items.push(selectItem.value);
    });

    // Monsters
    let monsters = [];
    monsterNums.forEach(num => {
        const selectMonster = document.getElementById("select-monster-" + num);

        monsters.push(selectMonster.value);
    });

    // Commands
    let commands = [];
    commandsNums.forEach(num => {
        const selectCommand = document.getElementById("select-command-" + num);

        if (selectCommand.value !== "0") {
            commands.push(selectCommand.value);
        }
        console.log(selectCommand.value);
    });

    // Entrances
    let additionalData = [];
    if (category === "1") {
        entranceNums.forEach(num => {
            const selectMap = document.getElementById("entrance-map-" + num);
            const selectNode = document.getElementById("entrance-node-" + num);
            const inputTitle = document.getElementById("entrance-title-" + num);
            const selectPerm = document.getElementById("entrance-perm-" + num);



            if (inputTitle.value.length > 0) {
                additionalData.push([
                    selectMap.value,
                    selectNode.value,
                    inputTitle.value,
                    selectPerm.value
                ]);
            }
        });
    }
    const json = JSON.stringify({
        "name": name,
        "category": category,
        "connections": connections,
        "sentences_first": firstSentence,
        "sentences_last": lastSentence,
        "monsters": monsters,
        "items": items,
        "commands": commands,
        "additional_data": additionalData
    });
    console.log(json);

    // API-URL abhängig vom Modus
    const url = nodeId !== null
        ? `/itfd-creator/packs/${packName}/maps/${mapName}/edit-node/${nodeId}`
        : `/itfd-creator/packs/${packName}/maps/${mapName}/add-node`;

    fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: json,
        credentials: "include"
    })
    .then(response => response.json())  // 🔑 JSON vom Backend erwarten
    .then(data => {
        if (data.redirect_url) {
            window.location.href = data.redirect_url;
        } else {
            console.log("Antwort:", data);
        }
    })
    .catch(error => {
        console.error("Fehler:", error);
    });
})

/*insert Data (ONLY IF EDIT) */
if (dataInsert) {
    // Name
    document.addEventListener("DOMContentLoaded", () => {})
    const inputName = document.getElementById("name");
    inputName.value = dataInsert["name"];

    // Category
    globalCategory = dataInsert["category"];
    selectCategory.value = globalCategory;

    // Connections
    const connValues = dataInsert["connections"]
    connValues.forEach(([node, title, perm]) => {
        const [_nodeElem, _titleElem, _permElem] = addConnection();

        _nodeElem.value = node;
        _titleElem.value = title;
        _permElem.value = perm;

        _titleElem.classList.remove("none-value");
    })

    // Sentences First
    const sentencesFirst = dataInsert["sentences_first"];
    sentencesFirst.forEach((sentence) => {
        const _inputSentence = addSentenceFirst()
        _inputSentence.value = sentence;
        _inputSentence.classList.remove("none-value");
    })

    // Sentences Last
    const sentencesLast = dataInsert["sentences_last"];
    sentencesLast.forEach((sentence) => {
        const _inputSentence = addSentenceLast()
        _inputSentence.value = sentence;
        _inputSentence.classList.remove("none-value");
    })

    // Items
    const items = dataInsert["items"];
    items.forEach((item) => {
        const _selectItem = addItem()
        _selectItem.value = item;
    })

    // Monsters
    const monsters = dataInsert["monsters"];
    monsters.forEach((monster) => {
        const _selectMonster = addMonster()
        _selectMonster.value = monster;
    })

    // Items
    const commands = dataInsert["commands"];
    commands.forEach((command) => {
        const _selectCommand = addCommand()
        _selectCommand.value = command;
    })

    console.log("GLOBAL CATEGORY: " + globalCategory);
    if (globalCategory === "1") {
        console.log("GLOBAL CATEGORY: " + globalCategory);
        const entranceValues = dataInsert["additional_data"]
        divEntranceContainer.style.display = "block";

        entranceValues.forEach(([map, node, title, perm]) => {
            const [
                _mapElem,
                _nodeElem,
                _titleElem,
                _permElem
            ] = addEntrance();

            _mapElem.value = map;
            _nodeElem.value = node;
            _titleElem.value = title;
            _permElem.value = perm;

            _titleElem.classList.remove("none-value");
        })
    }
}
