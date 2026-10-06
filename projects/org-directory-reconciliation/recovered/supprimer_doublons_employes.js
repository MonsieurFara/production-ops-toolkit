// Version publique adaptée ; voir docs/recovered-scripts.md.



const fs = require("fs");
const path = require("path");

const OPT = { url: process.env.ORG_API_URL, user: process.env.ORG_API_USER, password: process.env.ORG_API_PASSWORD };
for (let i = 2; i < process.argv.length; i++) {
    const a = process.argv[i];
    if (a === "--url") OPT.url = process.argv[++i];
    else if (a === "--user") OPT.user = process.argv[++i];
    else if (a === "--password") throw new Error("Utiliser ORG_API_PASSWORD, hors ligne de commande");
    else if (a === "--execute") OPT.execute = true;
}
if (!OPT.url || !OPT.user || !OPT.password) {
    console.log("Usage: node supprimer_doublons_employes.js --url <api> --user <login>  [--execute]");
    process.exit(1);
}
OPT.url = OPT.url.replace(/\/+$/, "");

const endpointPublicCheck = new URL(OPT.url);
if (endpointPublicCheck.username || endpointPublicCheck.password) throw new Error("Identifiants interdits dans l'URL");
if (endpointPublicCheck.protocol !== "https:" && !(endpointPublicCheck.protocol === "http:" && ["localhost", "127.0.0.1", "[::1]"].includes(endpointPublicCheck.hostname))) throw new Error("HTTPS requis hors localhost");

const DRY_RUN = !OPT.execute;

const normaliser = (s) => (s || "").toString().normalize("NFD")
    .replace(/[̀-ͯ]/g, "").toUpperCase().replace(/\s+/g, " ").trim();

const pause = (ms) => new Promise((r) => setTimeout(r, ms));
let TOKEN = null;

async function appel(methode, chemin, corps) {
    const entetes = { Accept: "application/json" };
    if (TOKEN) entetes.Authorization = `Bearer ${TOKEN}`;
    if (corps) entetes["Content-Type"] = "application/json";
    const reponse = await fetch(`${OPT.url}${chemin}`, {
        method: methode,
            signal: AbortSignal.timeout(10000), headers: entetes, body: corps ? JSON.stringify(corps) : undefined,
    });
    const texte = await reponse.text();
    let json = null;
    try { json = texte ? JSON.parse(texte) : null; } catch {  }
    return { ok: reponse.ok && (json === null || json.success !== false), status: reponse.status, data: json && json.data, message: (json && json.message) || texte.slice(0, 150) };
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

(async () => {
    console.log("=".repeat(70));
    console.log(`SUPPRESSION DES DOUBLONS  -  ${DRY_RUN ? "SIMULATION" : "EXECUTION REELLE"}`);
    console.log("=".repeat(70));
    console.log(`API : ${OPT.url}`);

    await connexion();
    const employes = (await appel("GET", "/api/employes")).data || [];
    console.log(`Employes en base : ${employes.length}\n`);

    const avecKeycloak = employes.filter((e) => e.keycloakUserId);
    const sansKeycloak = employes.filter((e) => !e.keycloakUserId);

    const doublons = [];
    const dejaRetenues = new Set();

    sansKeycloak.forEach((fiche) => {
        if (!fiche.matEmploye || !fiche.nomEmploye) return;
        if (dejaRetenues.has(fiche.id)) return;

        const memeIdentite = (ref) =>
            ref.matEmploye && String(ref.matEmploye).trim() === String(fiche.matEmploye).trim() &&
            normaliser(ref.nomEmploye) === normaliser(fiche.nomEmploye);


        const jumelleKeycloak = avecKeycloak.find(memeIdentite);
        if (jumelleKeycloak) { doublons.push({ fiche, jumelle: jumelleKeycloak }); return; }






        const jumelleParAffectation = avecKeycloak.find((ref) =>
            ref.matEmploye && String(ref.matEmploye).trim() === String(fiche.matEmploye).trim() &&
            ref.idUnite && fiche.idUnite && ref.idUnite === fiche.idUnite);
        if (jumelleParAffectation) { doublons.push({ fiche, jumelle: jumelleParAffectation }); return; }




        const memes = sansKeycloak.filter(memeIdentite);
        if (memes.length > 1) {
            const gardee = memes.find((e) => e.adresseEmail) || memes[0];
            memes.forEach((e) => {
                dejaRetenues.add(e.id);
                if (e.id !== gardee.id) doublons.push({ fiche: e, jumelle: gardee });
            });
        }
    });

    console.log(`Fiches sans lien Keycloak : ${sansKeycloak.length}`);
    console.log(`DOUBLONS identifies       : ${doublons.length}`);
    console.log(`Fiches conservees         : ${sansKeycloak.length - doublons.length} (vrais nouveaux employes)\n`);

    if (!doublons.length) { console.log("Rien a supprimer."); return; }

    doublons.forEach(({ fiche, jumelle }) => {
        console.log(`  ${(fiche.nomEmploye || "").padEnd(36).slice(0, 36)} mat=${fiche.matEmploye}`);
        console.log(`      conservee : ${jumelle.adresseEmail || "(sans email)"}`);
        console.log(`      supprimee : ${fiche.adresseEmail || "(sans email)"}`);
    });

    if (DRY_RUN) {
        console.log(`\n${"=".repeat(70)}`);
        console.log("SIMULATION - aucune suppression effectuee.");
        console.log("Relancer avec --execute pour supprimer.");
        return;
    }


    const horodatage = new Date().toISOString().slice(0, 16).replace(/[-:]/g, "").replace("T", "-");
    const sauvegarde = path.join(__dirname, `backup_doublons_supprimes_${horodatage}.json`);
    fs.writeFileSync(sauvegarde, JSON.stringify(doublons.map((d) => d.fiche), null, 2), "utf8");
    console.log(`\nSauvegarde des fiches supprimees : ${sauvegarde}`);

    let supprimees = 0, echecs = 0;
    for (const { fiche } of doublons) {
        const r = await appel("DELETE", `/api/employes/${fiche.id}`);
        if (r.ok) supprimees++;
        else { echecs++; console.log(`  ECHEC ${fiche.nomEmploye} (${r.status}) ${r.message}`); }
    }
    console.log(`\n${"=".repeat(70)}`);
    console.log(`Supprimees : ${supprimees}   Echecs : ${echecs}`);
    console.log(`Employes restants : ${((await appel("GET", "/api/employes")).data || []).length}`);
})().catch((e) => { console.error(`\nECHEC : ${e.message}`); process.exit(1); });
