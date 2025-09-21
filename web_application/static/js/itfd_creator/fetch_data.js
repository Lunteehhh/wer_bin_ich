export async function fetchPossibleMonsters(pack) {
    try {
        const response = await fetch(`/itfd-creator/packs/${pack}/selectable-monsters`, {
            method: 'GET',
            credentials: 'include'
        })
        .then(response => response.json());
        return await response["data"];
    } catch (error) {
        console.error("Fehler beim Laden der Benutzer:", error);
        return []; // leeres Array bei Fehler
    }
}

export async function fetchPossibleItems(pack) {
    try {
        const response = await fetch(`/itfd-creator/packs/${pack}/selectable-items`)
        .then(response => response.json());
        return await response["data"];
    } catch (error) {
        console.error("Fehler beim Laden der Benutzer:", error);
        return [];
    }
}

export async function fetchPossibleMapsNodes(pack, map) {
    try {
        const response = await fetch(`/itfd-creator/packs/${pack}/selectable-nodes`)
        .then(response => response.json());
        return await response["data"];
    } catch (error) {
        console.error("Fehler beim Laden der Benutzer:", error);
        return [];
    }
}

export async function fetchPossibleCommands(pack) {
    try {
        const response = await fetch(`/itfd-creator/packs/${pack}/selectable-commands`)
        .then(response => response.json());
        return await response["data"];
    } catch (error) {
        console.error("Fehler beim Laden der Benutzer:", error);
        return [];
    }
}

export async function fetchPossiblePermissions(pack) {
    try {
        const response = await fetch(`/itfd-creator/packs/${pack}/selectable-permissions`)
        .then(response => response.json());
        return await response["data"];
    } catch (error) {
        console.error("Fehler beim Laden der Benutzer:", error);
        return [];
    }
}
