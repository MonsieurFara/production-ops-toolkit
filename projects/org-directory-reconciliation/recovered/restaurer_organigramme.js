// Version publique adaptée ; voir docs/recovered-scripts.md.



const fs = require("fs");

const OPT = { url: process.env.ORG_API_URL, user: process.env.ORG_API_USER, password: process.env.ORG_API_PASSWORD };
for (let i = 2; i < process.argv.length; i++) {
    const a = process.argv[i];
    if (a === "--url") OPT.url = process.argv[++i];
    else if (a === "--user") OPT.user = process.argv[++i];
    else if (a === "--password") throw new Error("Utiliser ORG_API_PASSWORD, hors ligne de commande");
    else if (a === "--backup") OPT.backup = process.argv[++i];
    else if (a === "--execute") OPT.execute = true;
    else if (a === "--supprimer-nouveaux") OPT.supprimerNouveaux = true;
}
if (!OPT.url || !OPT.user || !OPT.password || !OPT.backup) {
    console.log(`
Restauration de l'organigramme depuis une sauvegarde.

  node restaurer_organigramme.js --url <api> --user <login>  \\
                                 --backup <fichier.json> [--execute]

  --backup               Sauvegarde a restaurer (obligatoire)
  --execute              Restaure reellement. Sans cette option : simulation.
  --supprimer-nouveaux   Supprime aussi les employes crees depuis la sauvegarde
`);
    process.exit(1);
}
OPT.url = OPT.url.replace(/\/+$/, "");

const endpointPublicCheck = new URL(OPT.url);
if (endpointPublicCheck.username || endpointPublicCheck.password) throw new Error("Identifiants interdits dans l'URL");
if (endpointPublicCheck.protocol !== "https:" && !(endpointPublicCheck.protocol === "http:" && ["localhost", "127.0.0.1", "[::1]"].includes(endpointPublicCheck.hostname))) throw new Error("HTTPS requis hors localhost");

const DRY_RUN = !OPT.execute;

const pause = (ms) => new Promise((r) => setTimeout(r, ms));
let TOKEN = null;

async function appel(methode, chemin, corps) {
    const entetes = { Accept: "application/json" };
    if (TOKEN) entetes.Authorization = `Bearer ${TOKEN}`;
    if (corps) entetes["Content-Type"] = "application/json";
    try {
        const reponse = await fetch(`${OPT.url}${chemin}`, {
            method: methode,
            signal: AbortSignal.timeout(10000), headers: entetes, body: corps ? JSON.stringify(corps) : undefined,
        });
        const texte = await reponse.text();
        let json = null;
        try { json = texte ? JSON.parse(texte) : null; } catch {  }
        return {
            ok: reponse.ok && (json === null || json.success !== false),
            status: reponse.status,
            data: json && json.data !== undefined ? json.data : json,
            message: (json && json.message) || texte.slice(0, 150),
        };
    } catch (e) {
        return { ok: false, status: 0, data: null, message: e.message };
    }
}


async function connexion(tentatives = 4) {
    for (let essai = 1; essai <= tentatives; essai++) {
        const r = await appel("POST", "/api/auth/login", { username: OPT.user, password: OPT.password });
        const jeton = r.data && (r.data.access_token || r.data.accessToken || r.data.token);
        if (r.ok && jeton) { TOKEN = jeton; return; }
        if (essai === tentatives) throw new Error(`Authentification refusee : ${r.message}`);
        const attente = essai * 20;
        console.log(`  authentification refusee - nouvelle tentative dans ${attente}s...`);
        await pause(attente * 1000);
    }
}

const barre = (t) => { console.log(""); console.log("=".repeat(72)); console.log(t); console.log("=".repeat(72)); };

(async () => {
    barre(`RESTAURATION  -  ${DRY_RUN ? "SIMULATION (aucune ecriture)" : "EXECUTION REELLE"}`);

    if (!fs.existsSync(OPT.backup)) throw new Error(`Sauvegarde introuvable : ${OPT.backup}`);
    const sauvegarde = JSON.parse(fs.readFileSync(OPT.backup, "utf8"));
    console.log(`Sauvegarde : ${OPT.backup}`);
    console.log(`  prise le : ${sauvegarde.date}`);
    console.log(`  environnement : ${sauvegarde.api}`);
    console.log(`  contenu  : ${(sauvegarde.unites || []).length} unites, ${(sauvegarde.employes || []).length} employes`);

    if (sauvegarde.api && sauvegarde.api !== OPT.url) {
        console.log(`\n  ATTENTION : la sauvegarde provient de ${sauvegarde.api}`);
        console.log(`              et vous restaurez vers ${OPT.url}`);
    }

    await connexion();
    const idFiliale = sauvegarde.filiale && sauvegarde.filiale.id;
    if (!idFiliale) throw new Error("La sauvegarde ne contient pas de filiale.");

    const unitesActuelles = (await appel("GET", `/api/unites?idFiliale=${idFiliale}`)).data || [];
    const employesActuels = (await appel("GET", "/api/employes")).data || [];
    console.log(`Etat actuel : ${unitesActuelles.length} unites, ${employesActuels.length} employes`);

    const stats = { unitesRecreees: 0, unitesMajs: 0, employesRestaures: 0, employesSupprimes: 0, erreurs: 0 };
    const erreurs = [];






    barre("1/3  -  UNITES");
    const actuelleParCode = new Map();
    unitesActuelles.forEach((u) => { if (u.code) actuelleParCode.set(u.code, u); });

    const idParCode = new Map();          
    const ancienIdVersCode = new Map();   
    (sauvegarde.unites || []).forEach((u) => { if (u.code) ancienIdVersCode.set(u.id, u.code); });

    for (const ancienne of sauvegarde.unites || []) {
        if (!ancienne.code) continue;   
        const existante = actuelleParCode.get(ancienne.code);
        const corps = {
            idFiliale: ancienne.idFiliale,
            idTypeUnite: ancienne.idTypeUnite,
            idGrade: ancienne.idGrade,
            code: ancienne.code,
            libUnite: ancienne.libUnite,
        };
        if (existante) {
            idParCode.set(ancienne.code, existante.id);
            stats.unitesMajs++;
        } else if (DRY_RUN) {
            idParCode.set(ancienne.code, `SIMULE-${ancienne.code}`);
            stats.unitesRecreees++;
        } else {
            const r = await appel("POST", "/api/unites", corps);
            if (r.ok && r.data && r.data.id) { idParCode.set(ancienne.code, r.data.id); stats.unitesRecreees++; }
            else { stats.erreurs++; erreurs.push(`UNITE ${ancienne.code} (${r.status}) ${r.message}`); }
        }
    }
    console.log(`  recreees : ${stats.unitesRecreees}   deja presentes : ${stats.unitesMajs}`);




    barre("2/3  -  HIERARCHIE");
    let liens = 0;
    for (const ancienne of sauvegarde.unites || []) {
        if (!ancienne.code) continue;
        const id = idParCode.get(ancienne.code);
        if (!id || String(id).startsWith("SIMULE-")) { if (DRY_RUN) liens++; continue; }
        const codeParent = ancienne.superieurId ? ancienIdVersCode.get(ancienne.superieurId) : null;
        const idParent = codeParent ? idParCode.get(codeParent) : null;
        const courante = (await appel("GET", `/api/unites/${id}`)).data;
        if (!courante) continue;
        const r = await appel("PUT", `/api/unites/${id}`, { ...courante, superieurId: idParent || null });
        if (r.ok) liens++;
        else { stats.erreurs++; erreurs.push(`LIEN ${ancienne.code} (${r.status}) ${r.message}`); }
    }
    console.log(`  liens retablis : ${liens}`);







    barre("3/3  -  EMPLOYES");
    const actuelParId = new Map(employesActuels.map((e) => [e.id, e]));
    const idsSauvegardes = new Set((sauvegarde.employes || []).map((e) => e.id));

    for (const ancien of sauvegarde.employes || []) {
        const actuel = actuelParId.get(ancien.id);
        if (!actuel) continue;   

        const codeUnite = ancien.idUnite ? ancienIdVersCode.get(ancien.idUnite) : null;
        const idUnite = codeUnite ? idParCode.get(codeUnite) : null;

        const champs = {
            idUnite: idUnite && !String(idUnite).startsWith("SIMULE-") ? idUnite : null,
            idGrade: ancien.idGrade || null,
            idFonction: ancien.idFonction || null,
            matEmploye: ancien.matEmploye || null,
            niveau: ancien.niveau === undefined ? null : ancien.niveau,
            unitesSecondaires: ancien.unitesSecondaires || [],
        };
        if (DRY_RUN) { stats.employesRestaures++; continue; }
        const r = await appel("PUT", `/api/employes/${ancien.id}`, { ...actuel, ...champs });
        if (r.ok) stats.employesRestaures++;
        else { stats.erreurs++; erreurs.push(`EMPLOYE ${ancien.nomEmploye} (${r.status}) ${r.message}`); }
    }


    const nouveaux = employesActuels.filter((e) => !idsSauvegardes.has(e.id));
    console.log(`  affectations restaurees : ${stats.employesRestaures}`);
    console.log(`  employes crees depuis la sauvegarde : ${nouveaux.length}`);

    if (nouveaux.length && OPT.supprimerNouveaux) {
        for (const e of nouveaux) {
            if (DRY_RUN) { stats.employesSupprimes++; continue; }
            const r = await appel("DELETE", `/api/employes/${e.id}`);
            if (r.ok) stats.employesSupprimes++;
            else { stats.erreurs++; erreurs.push(`SUPPRESSION ${e.nomEmploye} (${r.status}) ${r.message}`); }
        }
        console.log(`  supprimes : ${stats.employesSupprimes}`);
    } else if (nouveaux.length) {
        console.log(`  conserves (ajouter --supprimer-nouveaux pour les retirer) :`);
        nouveaux.slice(0, 10).forEach((e) => console.log(`      ${e.nomEmploye} | ${e.adresseEmail || "(sans email)"}`));
        if (nouveaux.length > 10) console.log(`      ... et ${nouveaux.length - 10} autres`);
    }

    barre("RAPPORT");
    console.log(`Unites    : ${stats.unitesRecreees} recreees, ${stats.unitesMajs} deja presentes`);
    console.log(`Employes  : ${stats.employesRestaures} affectations restaurees, ${stats.employesSupprimes} supprimes`);
    console.log(`Erreurs   : ${stats.erreurs}`);
    if (erreurs.length) erreurs.slice(0, 20).forEach((e) => console.log(`  ${e}`));

    barre(DRY_RUN
        ? "SIMULATION TERMINEE - aucune donnee modifiee.\nRelancer avec --execute pour restaurer."
        : "RESTAURATION TERMINEE.");
})().catch((e) => { console.error(`\nECHEC : ${e.message}`); process.exit(1); });
