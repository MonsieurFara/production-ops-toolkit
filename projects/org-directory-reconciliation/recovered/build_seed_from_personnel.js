// Version publique adaptée ; voir docs/recovered-scripts.md.



const fs = require("fs");
const path = require("path");


const CSV_DELIMITER = ";";
const CODE_AGENCE_LENGTH = 5;
const PLACEHOLDERS = ["(null)", "#n/a", "n/a", "null", "-"];

const inputPath = process.argv[2];
const outputPath = process.argv[3] || path.join(__dirname, "organigramme_seed.json");

if (!inputPath) {
    console.error("Usage: node build_seed_from_personnel.js <input.csv> [output.json]");
    process.exit(1);
}


function clean(value) {
    if (value === undefined || value === null) return null;
    const trimmed = String(value).trim();
    if (trimmed === "") return null;
    if (PLACEHOLDERS.includes(trimmed.toLowerCase())) return null;
    return trimmed;
}


function padCodeAgence(code) {
    const c = clean(code);
    if (c === null) return null;
    return c.padStart(CODE_AGENCE_LENGTH, "0");
}


function slug(label) {
    return String(label)
        .normalize("NFD").replace(/[̀-ͯ]/g, "")   
        .toUpperCase()
        .replace(/[^A-Z0-9]+/g, "-")
        .replace(/^-+|-+$/g, "")
        .slice(0, 40);
}


function parseCsv(content, delimiter) {
    const rows = [];
    let field = "";
    let row = [];
    let inQuotes = false;

    for (let i = 0; i < content.length; i++) {
        const ch = content[i];
        if (inQuotes) {
            if (ch === '"') {
                if (content[i + 1] === '"') { field += '"'; i++; }
                else inQuotes = false;
            } else field += ch;
            continue;
        }
        if (ch === '"') { inQuotes = true; continue; }
        if (ch === delimiter) { row.push(field); field = ""; continue; }
        if (ch === "\r") continue;
        if (ch === "\n") { row.push(field); rows.push(row); row = []; field = ""; continue; }
        field += ch;
    }
    if (field !== "" || row.length > 0) { row.push(field); rows.push(row); }
    return rows;
}


let raw = fs.readFileSync(inputPath, "utf8");
if (raw.charCodeAt(0) === 0xfeff) raw = raw.slice(1);   

const table = parseCsv(raw, CSV_DELIMITER).filter(r => r.some(c => c.trim() !== ""));
const headers = table[0].map(h => h.trim());
const records = table.slice(1).map(cells => {
    const obj = {};
    headers.forEach((h, i) => { obj[h] = cells[i] !== undefined ? cells[i] : ""; });
    return obj;
});

console.log("=".repeat(70));
console.log("Generation du seed organigramme");
console.log("=".repeat(70));
console.log(`Source           : ${inputPath}`);
console.log(`Lignes lues      : ${records.length}`);
console.log("");


const anomalies = { sansEmail: [], emailsDupliques: [], matriculesDupliques: [], reseauSansCode: [] };

let people = records.map((r, index) => {
    const noms = clean(r["per_noms"]) || "";
    const prenoms = clean(r["per_prenoms"]) || "";
    const emailRh = clean(r["cnt_email"]);
    const emailAd = clean(r["AD_Email"]);

    return {
        ligne: index + 2,                                  
        matricule: clean(r["emp_matricule"]),
        nomComplet: `${noms} ${prenoms}`.replace(/\s+/g, " ").trim(),
        sexe: clean(r["sexe"]),
        codeAgence: padCodeAgence(r["code_agence"]),
        agence: clean(r["agence"]),
        unite: clean(r["unite"]),
        email: emailRh || emailAd || null,
        emailSource: emailRh ? "RH" : (emailAd ? "AD" : null),
        username: clean(r["AD_Login AD"]),
        fonctionLibelle: clean(r["fonction_libele"]),
        fonctionAd: clean(r["AD_Fonction"]),
        societeAd: clean(r["AD_Société"]) || clean(r["AD_Societe"]),
    };
});


const dedoublonnees = [];
const occurrencesEmail = new Map();
people.forEach(p => {
    if (!p.email) return;
    const k = p.email.toLowerCase();
    occurrencesEmail.set(k, (occurrencesEmail.get(k) || 0) + 1);
});

const parPersonne = new Map();
people.forEach(p => {
    const cle = p.matricule ? `${slug(p.nomComplet)}|${p.matricule}` : `LIGNE-${p.ligne}`;
    if (!parPersonne.has(cle)) parPersonne.set(cle, []);
    parPersonne.get(cle).push(p);
});

const personnes = [];
parPersonne.forEach(groupe => {
    if (groupe.length === 1) { personnes.push(groupe[0]); return; }

    const preferee = groupe.find(p => p.email && occurrencesEmail.get(p.email.toLowerCase()) === 1)
        || groupe.find(p => p.email) || groupe[0];
    personnes.push(preferee);
    groupe.filter(p => p !== preferee).forEach(p =>
        dedoublonnees.push(`L${p.ligne} ${p.nomComplet} (mat ${p.matricule}) - ligne ecartee, email ${p.email || "absent"}`));
});
people = personnes;


people.forEach(p => { if (!p.email) anomalies.sansEmail.push(p); });

const byEmail = new Map();
people.filter(p => p.email).forEach(p => {
    const key = p.email.toLowerCase();
    if (!byEmail.has(key)) byEmail.set(key, []);
    byEmail.get(key).push(p);
});
byEmail.forEach((group, email) => { if (group.length > 1) anomalies.emailsDupliques.push({ email, group }); });

const byMatricule = new Map();
people.filter(p => p.matricule).forEach(p => {
    if (!byMatricule.has(p.matricule)) byMatricule.set(p.matricule, []);
    byMatricule.get(p.matricule).push(p);
});
byMatricule.forEach((group, mat) => { if (group.length > 1) anomalies.matriculesDupliques.push({ matricule: mat, group }); });


const unites = new Map();   

function upsertUnite({ code, libelle, parentCode, nature }) {
    if (!unites.has(code)) {
        unites.set(code, { code, libUnite: libelle, parentCode: parentCode || null, nature, nbEmployes: 0 });
    }
    const u = unites.get(code);

    if (!u.parentCode && parentCode) u.parentCode = parentCode;
    return u;
}

const RESEAU_PREFIX = "RESEAU";


const reseauCodes = new Map();
people.forEach(p => {
    if (p.agence && p.agence.toUpperCase().startsWith(RESEAU_PREFIX) && p.codeAgence && p.unite) {
        reseauCodes.set(p.unite.toUpperCase(), p.codeAgence);
    }
});

function codeDuReseau(uniteLabel) {
    return reseauCodes.get(uniteLabel.toUpperCase()) || `R-${slug(uniteLabel)}`;
}

people.forEach(p => {
    const estReseau = p.unite && p.unite.toUpperCase().startsWith(RESEAU_PREFIX);

    if (estReseau) {
        const reseauCode = codeDuReseau(p.unite);
        upsertUnite({ code: reseauCode, libelle: p.unite, parentCode: null, nature: "RESEAU" });



        const agenceEstLeReseau = p.agence && p.agence.toUpperCase().startsWith(RESEAU_PREFIX);
        if (agenceEstLeReseau || !p.codeAgence) {
            p.uniteCode = reseauCode;
        } else {
            upsertUnite({ code: p.codeAgence, libelle: p.agence, parentCode: reseauCode, nature: "AGENCE" });
            p.uniteCode = p.codeAgence;
        }
    } else {

        if (p.codeAgence) {
            upsertUnite({ code: p.codeAgence, libelle: p.agence, parentCode: null, nature: "AGENCE" });
        }
        if (p.unite) {
            const codeUnite = `U-${slug(p.unite)}`;
            upsertUnite({ code: codeUnite, libelle: p.unite, parentCode: p.codeAgence || null, nature: "UNITE" });
            p.uniteCode = codeUnite;
        } else {
            p.uniteCode = p.codeAgence;
        }
    }
});


const LIBELLE_SIEGE = "DIRECTION GENERALE";
const siege = [...unites.values()].find(
    u => u.nature === "AGENCE" && u.libUnite && u.libUnite.toUpperCase().trim() === LIBELLE_SIEGE);
if (siege) {
    siege.parentCode = null;   
    unites.forEach(u => {
        if (u.code !== siege.code && !u.parentCode) u.parentCode = siege.code;
    });
} else {
    console.log(`ATTENTION: unite "${LIBELLE_SIEGE}" introuvable, l'arbre gardera plusieurs racines.`);
}

people.forEach(p => { if (p.uniteCode && unites.has(p.uniteCode)) unites.get(p.uniteCode).nbEmployes++; });


const parentsMultiples = [];
const parentsVus = new Map();
people.forEach(p => {
    if (!p.uniteCode) return;
    const u = unites.get(p.uniteCode);
    if (!u || u.nature !== "UNITE") return;
    if (!parentsVus.has(u.code)) parentsVus.set(u.code, new Set());
    if (p.codeAgence) parentsVus.get(u.code).add(p.codeAgence);
});
parentsVus.forEach((parents, code) => {
    if (parents.size > 1) parentsMultiples.push({ code, libelle: unites.get(code).libUnite, parents: [...parents] });
});


const seed = {
    genereLe: new Date().toISOString(),
    source: path.basename(inputPath),
    regles: {
        codeAgence: `complete a ${CODE_AGENCE_LENGTH} chiffres par des zeros a gauche`,
        hierarchie: "unite RESEAU* => reseau parent de l'agence ; sinon agence parente de l'unite",
    },
    unites: [...unites.values()].sort((a, b) => a.code.localeCompare(b.code)),
    employes: people.map(p => ({
        matricule: p.matricule,
        nomEmploye: p.nomComplet,
        adresseEmail: p.email,
        username: p.username,
        uniteCode: p.uniteCode || null,
        fonctionLibelle: p.fonctionLibelle,
        sexe: p.sexe,
        societe: p.societeAd,
    })),
};

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, JSON.stringify(seed, null, 2), "utf8");


const dataJsPath = outputPath.replace(/\.json$/, "") + ".data.js";
fs.writeFileSync(dataJsPath, `var ORGANIGRAMME_SEED = ${JSON.stringify(seed, null, 2)};\n`, "utf8");


const parNature = {};
seed.unites.forEach(u => { parNature[u.nature] = (parNature[u.nature] || 0) + 1; });

console.log("--- UNITES CONSTRUITES ---");
Object.entries(parNature).forEach(([n, c]) => console.log(`  ${n.padEnd(8)} : ${c}`));
console.log(`  ${"TOTAL".padEnd(8)} : ${seed.unites.length}`);
console.log("");
console.log("--- RACINES (sans parent) ---");
seed.unites.filter(u => !u.parentCode).forEach(u =>
    console.log(`  [${u.code.padEnd(18)}] ${u.libUnite}  (${u.nbEmployes} employes directs)`));
console.log("");
console.log("--- EMPLOYES ---");
console.log(`  Lignes dans le fichier       : ${records.length}`);
console.log(`  Lignes en double ecartees    : ${dedoublonnees.length}`);
console.log(`  PERSONNES REELLES            : ${seed.employes.length}`);
console.log(`  Email issu du RH             : ${people.filter(p => p.emailSource === "RH").length}`);
console.log(`  Email recupere via AD        : ${people.filter(p => p.emailSource === "AD").length}`);
console.log(`  Sans email (index sparse)    : ${anomalies.sansEmail.length}`);
console.log(`  Rattaches a une unite        : ${seed.employes.filter(e => e.uniteCode).length}`);
console.log("");
console.log("--- ANOMALIES A ARBITRER ---");
console.log(`  Emails dupliques  : ${anomalies.emailsDupliques.length} (bloquant : index unique)`);
anomalies.emailsDupliques.forEach(d => {
    console.log(`    ${d.email}`);
    d.group.forEach(p => console.log(`      L${p.ligne} mat=${p.matricule} ${p.nomComplet} (${p.agence}/${p.unite})`));
});
console.log(`  Sans aucun email  : ${anomalies.sansEmail.length}`);
anomalies.sansEmail.forEach(p =>
    console.log(`    L${p.ligne} mat=${p.matricule} ${p.nomComplet} (${p.agence}/${p.unite})`));
console.log(`  Matricules dupliques : ${anomalies.matriculesDupliques.length}`);
console.log(`  Unites a parents multiples : ${parentsMultiples.length}`);
parentsMultiples.forEach(u => console.log(`    ${u.libelle} -> parents ${u.parents.join(", ")}`));
console.log("");
console.log(`Seed ecrit dans : ${outputPath}`);
console.log(`Module mongosh  : ${dataJsPath}`);
